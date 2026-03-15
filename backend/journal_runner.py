"""Run journalctl for kernel logs and stream output."""
from __future__ import annotations
import shutil
import subprocess
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from backend.json_parser import parse_journal_json_line
from models.log_entry import LogEntry


def _check_journalctl() -> bool:
    return shutil.which("journalctl") is not None


def run_journal_once(
    since: str = "",
    until: str = "",
    sudo_password: Optional[str] = None,
) -> tuple[list[LogEntry], Optional[str]]:
    """Run journalctl -k --output=json and return (entries, error)."""
    if not _check_journalctl():
        return [], "journalctl not found."

    cmd = ["journalctl", "-k", "-o", "json", "--no-pager"]
    if since:
        cmd += ["--since", since]
    if until:
        cmd += ["--until", until]

    stdin_data = None
    if sudo_password:
        cmd = ["sudo", "-S"] + cmd
        stdin_data = sudo_password + "\n"

    try:
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            low = err.lower()
            if "permission" in low or "non permise" in low:
                return [], "PERMISSION_DENIED"
            if sudo_password and ("incorrect" in low or "sorry" in low):
                return [], "WRONG_PASSWORD"
            return [], err or "journalctl failed."

        entries = []
        for line in result.stdout.splitlines():
            entry = parse_journal_json_line(line)
            if entry:
                entries.append(entry)
        return entries, None

    except subprocess.TimeoutExpired:
        return [], "journalctl timed out."
    except Exception as exc:
        return [], str(exc)


class JournalFollowWorker(QObject):
    """
    Streams journalctl -kf -o json using subprocess.Popen in a QThread.
    Using subprocess instead of QProcess avoids QSocketNotifier thread issues.
    """
    new_entries = pyqtSignal(list)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, sudo_password: Optional[str] = None):
        super().__init__()
        self._sudo_password = sudo_password
        self._process: Optional[subprocess.Popen] = None
        self._running = False

    def start(self):
        """Called in the QThread via thread.started signal."""
        self._running = True
        base_cmd = ["journalctl", "-kf", "-o", "json"]

        if self._sudo_password:
            cmd = ["sudo", "-S"] + base_cmd
        else:
            cmd = base_cmd

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            if self._sudo_password and self._process.stdin:
                self._process.stdin.write(self._sudo_password + "\n")
                self._process.stdin.flush()
                self._process.stdin.close()

            for line in self._process.stdout:
                if not self._running:
                    break
                entry = parse_journal_json_line(line)
                if entry:
                    self.new_entries.emit([entry])

        except Exception as exc:
            if self._running:
                self.error.emit(str(exc))
        finally:
            self._running = False
            self.finished.emit()

    def stop(self):
        """Stop the follow loop. Safe to call from the main thread."""
        self._running = False
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass
