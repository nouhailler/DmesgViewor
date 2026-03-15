"""Application toolbar."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QToolBar, QLabel, QLineEdit, QCheckBox, QComboBox,
    QWidget, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QIcon


class AppToolBar(QToolBar):
    refresh_requested = pyqtSignal()
    follow_start_requested = pyqtSignal()
    follow_pause_requested = pyqtSignal()
    export_requested = pyqtSignal()
    clear_buffer_requested = pyqtSignal()
    search_changed = pyqtSignal(str, bool, bool)   # pattern, regex, case
    log_level_set = pyqtSignal(int)
    source_changed = pyqtSignal(str)               # "dmesg" or "journalctl"

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self._build()

    def _build(self):
        # --- Source selector -------------------------------------------
        self.addWidget(QLabel("Source: "))
        self._source_combo = QComboBox()
        self._source_combo.addItem("dmesg buffer", "dmesg")
        self._source_combo.addItem("journalctl kernel", "journalctl")
        self._source_combo.currentIndexChanged.connect(self._on_source_changed)
        self.addWidget(self._source_combo)

        self.addSeparator()

        # --- Core actions ----------------------------------------------
        self._act_refresh = QAction("⟳ Refresh", self)
        self._act_refresh.setToolTip("Reload kernel logs (dmesg --json --decode)")
        self._act_refresh.triggered.connect(self.refresh_requested)
        self.addAction(self._act_refresh)

        self._act_follow = QAction("▶ Follow", self)
        self._act_follow.setToolTip("Start live log streaming")
        self._act_follow.triggered.connect(self.follow_start_requested)
        self.addAction(self._act_follow)

        self._act_pause = QAction("⏸ Pause", self)
        self._act_pause.setToolTip("Pause live log streaming")
        self._act_pause.setEnabled(False)
        self._act_pause.triggered.connect(self.follow_pause_requested)
        self.addAction(self._act_pause)

        self._act_export = QAction("⬇ Export", self)
        self._act_export.setToolTip("Export visible logs")
        self._act_export.triggered.connect(self.export_requested)
        self.addAction(self._act_export)

        self._act_clear = QAction("🗑 Clear Buffer", self)
        self._act_clear.setToolTip("Clear kernel ring buffer (dmesg -C)")
        self._act_clear.triggered.connect(self.clear_buffer_requested)
        self.addAction(self._act_clear)

        self.addSeparator()

        # --- Console log level -----------------------------------------
        self.addWidget(QLabel("Console level: "))
        self._level_combo = QComboBox()
        # Labels show the kernel index (0-7) and the name.
        # dmesg -n expects 1-8 (kernel_level = index + 1), handled in backend.
        level_names = ["0 emerg", "1 alert", "2 crit", "3 err",
                       "4 warn", "5 notice", "6 info", "7 debug"]
        for name in level_names:
            self._level_combo.addItem(name)
        self._level_combo.setCurrentIndex(7)   # default: debug (show all)
        self._level_combo.currentIndexChanged.connect(
            lambda idx: self.log_level_set.emit(idx)
        )
        self.addWidget(self._level_combo)

        self.addSeparator()

        # --- Search bar ------------------------------------------------
        self.addWidget(QLabel("Search: "))
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Filter messages…")
        self._search_box.setMinimumWidth(200)
        self._search_box.textChanged.connect(self._emit_search)
        self.addWidget(self._search_box)

        self._regex_cb = QCheckBox("Regex")
        self._regex_cb.stateChanged.connect(self._emit_search)
        self.addWidget(self._regex_cb)

        self._case_cb = QCheckBox("Case")
        self._case_cb.stateChanged.connect(self._emit_search)
        self.addWidget(self._case_cb)

    # ------------------------------------------------------------------
    def set_follow_active(self, active: bool):
        self._act_follow.setEnabled(not active)
        self._act_pause.setEnabled(active)

    def _emit_search(self):
        self.search_changed.emit(
            self._search_box.text(),
            self._regex_cb.isChecked(),
            self._case_cb.isChecked(),
        )

    def _on_source_changed(self, idx: int):
        source = self._source_combo.itemData(idx)
        self.source_changed.emit(source)
