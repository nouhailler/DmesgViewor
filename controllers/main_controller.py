"""Main controller: wires UI signals to backend actions."""
from __future__ import annotations
from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from ui.main_window import MainWindow
from ui.issues_panel import detect_issues
from backend.dmesg_runner import (
    DmesgFollowWorker, run_dmesg_once,
    clear_kernel_buffer, set_console_log_level
)
from backend.journal_runner import JournalFollowWorker, run_journal_once
from models.log_entry import LogEntry
from utils.privileges import ask_sudo_password
from utils.exporter import export_txt, export_json, export_csv, export_html
from utils.time_utils import dmesg_ts_to_epoch


class _LoadWorker(QObject):
    """Background worker for the initial one-shot dmesg/journalctl load."""
    done = pyqtSignal(list, str)   # (entries, error or "")

    def __init__(self, source: str, sudo_password: Optional[str]):
        super().__init__()
        self._source = source
        self._sudo_password = sudo_password

    def run(self):
        if self._source == "journalctl":
            entries, err = run_journal_once(sudo_password=self._sudo_password)
        else:
            entries, err = run_dmesg_once(sudo_password=self._sudo_password)
        self.done.emit(entries, err or "")


class MainController(QObject):
    def __init__(self, window: MainWindow):
        super().__init__()
        self._win = window
        self._source = "dmesg"
        self._sudo_password: Optional[str] = None   # cached for the session
        self._follow_active = False
        self._follow_worker: Optional[QObject] = None
        self._follow_thread: Optional[QThread] = None
        self._load_thread: Optional[QThread] = None
        self._all_entries: list[LogEntry] = []

        self._connect_signals()
        self._do_refresh()

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------
    def _connect_signals(self):
        tb = self._win.toolbar
        tb.refresh_requested.connect(self._do_refresh)
        tb.follow_start_requested.connect(self._start_follow)
        tb.follow_pause_requested.connect(self._stop_follow)
        tb.export_requested.connect(self._do_export)
        tb.clear_buffer_requested.connect(self._do_clear_buffer)
        tb.search_changed.connect(self._on_search_changed)
        tb.log_level_set.connect(self._set_log_level)
        tb.source_changed.connect(self._on_source_changed)

        fp = self._win.filter_panel
        fp.levels_changed.connect(self._win.log_table.proxy_model.set_allowed_levels)
        fp.facilities_changed.connect(self._win.log_table.proxy_model.set_allowed_facilities)

        self._win.log_table.source_model.rowCountChanged.connect(self._update_status)
        self._win.issues_panel.entry_focus_requested.connect(self._focus_entry)
        self._win.timeline.time_window_selected.connect(self._on_time_window)

    # ------------------------------------------------------------------
    # Sudo password management
    # ------------------------------------------------------------------
    def _request_sudo_password(self, error_hint: str = "") -> bool:
        """Ask the user for their sudo password. Returns True if provided."""
        pwd = ask_sudo_password(self._win, error_message=error_hint)
        if pwd is None:
            return False
        self._sudo_password = pwd
        return True

    def _handle_permission_error(self, context: str = "") -> bool:
        """
        Called when PERMISSION_DENIED is returned from a backend call.
        Shows password dialog. Returns True if the user provided a password
        (caller should retry), False if cancelled.
        """
        hint = ""
        if context:
            hint = f"Contexte : {context}"
        return self._request_sudo_password(error_hint=hint)

    def _handle_wrong_password(self) -> bool:
        """Called when sudo reports a wrong password. Asks again."""
        return self._request_sudo_password(
            error_hint="Mot de passe incorrect. Veuillez réessayer."
        )

    # ------------------------------------------------------------------
    # Refresh (one-shot load)
    # ------------------------------------------------------------------
    @pyqtSlot()
    def _do_refresh(self):
        if self._load_thread and self._load_thread.isRunning():
            return
        self._start_load_thread()

    def _start_load_thread(self):
        self._load_thread = QThread()
        self._load_worker = _LoadWorker(self._source, self._sudo_password)
        self._load_worker.moveToThread(self._load_thread)
        self._load_thread.started.connect(self._load_worker.run)
        self._load_worker.done.connect(self._on_load_done)
        self._load_worker.done.connect(self._load_thread.quit)
        self._load_thread.start()

    @pyqtSlot(list, str)
    def _on_load_done(self, entries: list[LogEntry], error: str):
        if error == "PERMISSION_DENIED":
            self._win.set_permission_status(False)
            if self._handle_permission_error("lecture des journaux dmesg"):
                # Retry immediately with the new password
                self._start_load_thread()
            return

        if error == "WRONG_PASSWORD":
            self._sudo_password = None
            if self._handle_wrong_password():
                self._start_load_thread()
            return

        if error:
            QMessageBox.warning(self._win, "Erreur de chargement", error)
            return

        self._win.set_permission_status(True)
        self._all_entries = entries
        self._win.log_table.source_model.set_entries(entries)
        self._win.timeline.update_entries(entries, self._source)
        self._win.issues_panel.update_issues(detect_issues(entries))
        self._update_status()

    # ------------------------------------------------------------------
    # Follow mode
    # ------------------------------------------------------------------
    @pyqtSlot()
    def _start_follow(self):
        if self._follow_active:
            return
        self._follow_thread = QThread()
        if self._source == "journalctl":
            self._follow_worker = JournalFollowWorker(sudo_password=self._sudo_password)
        else:
            self._follow_worker = DmesgFollowWorker(sudo_password=self._sudo_password)

        self._follow_worker.moveToThread(self._follow_thread)
        self._follow_thread.started.connect(self._follow_worker.start)
        self._follow_worker.new_entries.connect(self._on_new_entries)
        self._follow_worker.error.connect(self._on_follow_error)
        self._follow_worker.finished.connect(self._follow_thread.quit)
        self._follow_thread.start()

        self._follow_active = True
        self._win.toolbar.set_follow_active(True)
        self._win.set_follow_status(True)

    @pyqtSlot()
    def _stop_follow(self):
        if not self._follow_active:
            return
        if self._follow_worker:
            self._follow_worker.stop()
        if self._follow_thread:
            self._follow_thread.quit()
            self._follow_thread.wait(3000)
        self._follow_active = False
        self._win.toolbar.set_follow_active(False)
        self._win.set_follow_status(False)

    @pyqtSlot(list)
    def _on_new_entries(self, entries: list[LogEntry]):
        self._all_entries.extend(entries)
        if len(self._all_entries) > 50_000:
            self._all_entries = self._all_entries[-50_000:]
        self._win.log_table.source_model.append_entries(entries)
        self._win.timeline.update_entries(self._all_entries, self._source)
        new_issues = detect_issues(entries)
        if new_issues:
            self._win.issues_panel.update_issues(detect_issues(self._all_entries))
        self._win.log_table.scroll_to_bottom()

    @pyqtSlot(str)
    def _on_follow_error(self, msg: str):
        self._stop_follow()
        if "PERMISSION" in msg.upper():
            self._win.set_permission_status(False)
            if self._handle_permission_error("mode follow dmesg -w"):
                self._start_follow()
        else:
            QMessageBox.warning(self._win, "Erreur Follow", msg)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    @pyqtSlot()
    def _do_export(self):
        proxy = self._win.log_table.proxy_model
        source_model = self._win.log_table.source_model
        visible = [
            source_model.entry_at(proxy.mapToSource(proxy.index(r, 0)).row())
            for r in range(proxy.rowCount())
        ]
        visible = [e for e in visible if e is not None]

        path, _ = QFileDialog.getSaveFileName(
            self._win, "Exporter les logs", "dmesg_export",
            "Text (*.txt);;JSON (*.json);;CSV (*.csv);;HTML (*.html)",
        )
        if not path:
            return
        try:
            if path.endswith(".json"):
                export_json(visible, path)
            elif path.endswith(".csv"):
                export_csv(visible, path)
            elif path.endswith(".html"):
                export_html(visible, path)
            else:
                export_txt(visible, path)
            QMessageBox.information(
                self._win, "Export",
                f"{len(visible)} entrées exportées vers :\n{path}"
            )
        except Exception as exc:
            QMessageBox.critical(self._win, "Erreur d'export", str(exc))

    # ------------------------------------------------------------------
    # Clear buffer
    # ------------------------------------------------------------------
    @pyqtSlot()
    def _do_clear_buffer(self):
        reply = QMessageBox.question(
            self._win, "Confirmer l'effacement",
            "Cette action va vider le tampon de noyau (dmesg -C).\n"
            "Elle est irréversible.\n\nContinuer ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._try_clear_buffer()

    def _try_clear_buffer(self):
        err = clear_kernel_buffer(sudo_password=self._sudo_password)
        if err == "PERMISSION_DENIED":
            if self._handle_permission_error("effacement du tampon dmesg -C"):
                self._try_clear_buffer()
        elif err == "WRONG_PASSWORD":
            self._sudo_password = None
            if self._handle_wrong_password():
                self._try_clear_buffer()
        elif err:
            QMessageBox.warning(self._win, "Erreur", err)
        else:
            self._win.log_table.source_model.clear()
            self._all_entries = []
            self._win.issues_panel.update_issues([])
            self._win.timeline.update_entries([], self._source)

    # ------------------------------------------------------------------
    # Console log level
    # ------------------------------------------------------------------
    @pyqtSlot(int)
    def _set_log_level(self, level: int):
        err = set_console_log_level(level, sudo_password=self._sudo_password)
        if err == "PERMISSION_DENIED":
            if self._handle_permission_error("changement du niveau de log console"):
                self._set_log_level(level)
        elif err == "WRONG_PASSWORD":
            self._sudo_password = None
            if self._handle_wrong_password():
                self._set_log_level(level)
        elif err:
            QMessageBox.warning(self._win, "Erreur niveau log", err)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    @pyqtSlot(str, bool, bool)
    def _on_search_changed(self, pattern: str, regex: bool, case: bool):
        self._win.log_table.proxy_model.set_search(pattern, regex, case)
        self._update_status()

    # ------------------------------------------------------------------
    # Source switch
    # ------------------------------------------------------------------
    @pyqtSlot(str)
    def _on_source_changed(self, source: str):
        if self._follow_active:
            self._stop_follow()
        self._source = source
        self._win.set_source_label(source)
        self._do_refresh()

    # ------------------------------------------------------------------
    # Timeline time window
    # ------------------------------------------------------------------
    @pyqtSlot(float, float)
    def _on_time_window(self, start: float, end: float):
        if start == 0.0 and end == 0.0:
            self._win.log_table.source_model.set_entries(self._all_entries)
            return

        def to_epoch(e: LogEntry) -> float:
            return e.timestamp if self._source == "journalctl" else dmesg_ts_to_epoch(e.timestamp)

        filtered = [e for e in self._all_entries if start <= to_epoch(e) <= end]
        self._win.log_table.source_model.set_entries(filtered)
        self._win.tabs.setCurrentIndex(0)

    # ------------------------------------------------------------------
    # Focus on entry
    # ------------------------------------------------------------------
    @pyqtSlot(object)
    def _focus_entry(self, entry: LogEntry):
        self._win.tabs.setCurrentIndex(0)
        self._win.log_table.scroll_to_entry(entry)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _update_status(self, *_):
        total = self._win.log_table.source_model.rowCount()
        visible = self._win.log_table.visible_entry_count()
        self._win.set_log_count(total, visible)
