"""Run dmesg command and stream its output."""
from __future__ import annotations
import subprocess
import shutil
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from backend.json_parser import parse_dmesg_json, parse_dmesg_json_line
from models.log_entry import LogEntry


def _check_dmesg() -> bool:
    return shutil.which("dmesg") is not None


def _is_permission_error(stderr: str) -> bool:
    low = stderr.lower()
    return (
        "operation not permitted" in low
        or "permission denied" in low
        or "non permise" in low
        or "not permitted" in low
    )


def _is_wrong_password(stderr: str) -> bool:
    low = stderr.lower()
    return "incorrect password" in low or "sorry" in low or "mot de passe" in low


def _build_cmd(base_cmd: list[str], sudo_password: Optional[str]) -> tuple[list[str], Optional[str]]:
    """Return (command, stdin_input). Prepend sudo -S when password given."""
    if sudo_password:
        return ["sudo", "-S"] + base_cmd, sudo_password + "\n"
    return base_cmd, None


def run_dmesg_once(sudo_password: Optional[str] = None) -> tuple[list[LogEntry], Optional[str]]:
    """Run `dmesg --json` and return (entries, error_message)."""
    if not _check_dmesg():
        return [], "dmesg command not found. Install util-linux."
    cmd, stdin_data = _build_cmd(["dmesg", "--json"], sudo_password)
    try:
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            if _is_permission_error(err):
                return [], "PERMISSION_DENIED"
            if sudo_password and _is_wrong_password(err):
                return [], "WRONG_PASSWORD"
            return [], err or "dmesg returned non-zero exit code."
        entries = parse_dmesg_json(result.stdout)
        return entries, None
    except subprocess.TimeoutExpired:
        return [], "dmesg timed out."
    except Exception as exc:
        return [], str(exc)


def clear_kernel_buffer(sudo_password: Optional[str] = None) -> Optional[str]:
    """Run `dmesg -C`. Returns error string or None on success."""
    cmd, stdin_data = _build_cmd(["dmesg", "-C"], sudo_password)
    try:
        result = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            err = result.stderr.strip()
            if _is_permission_error(err):
                return "PERMISSION_DENIED"
            if sudo_password and _is_wrong_password(err):
                return "WRONG_PASSWORD"
            return err or "Failed to clear kernel buffer."
        return None
    except Exception as exc:
        return str(exc)


def set_console_log_level(level: int, sudo_password: Optional[str] = None) -> Optional[str]:
    """Run `dmesg -n <level>`. Returns error or None on success.

    The combo box uses indices 0-7 (emerg→debug) but dmesg -n expects 1-8,
    so we add 1 to convert.
    """
    kernel_level = level + 1   # 0-7  →  1-8
    cmd, stdin_data = _build_cmd(["dmesg", "-n", str(kernel_level)], sudo_password)
    try:
        result = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            err = result.stderr.strip()
            if _is_permission_error(err):
                return "PERMISSION_DENIED"
            if sudo_password and _is_wrong_password(err):
                return "WRONG_PASSWORD"
            return err or f"Failed to set log level {level}."
        return None
    except Exception as exc:
        return str(exc)


class DmesgFollowWorker(QObject):
    """
    Streams `dmesg -w --json` using subprocess.Popen (line-by-line) in a QThread.
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
        base_cmd = ["dmesg", "-w", "--json"]
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
            # Feed sudo password on stdin
            if self._sudo_password and self._process.stdin:
                self._process.stdin.write(self._sudo_password + "\n")
                self._process.stdin.flush()
                self._process.stdin.close()

            for line in self._process.stdout:
                if not self._running:
                    break
                entry = parse_dmesg_json_line(line)
                if entry:
                    self.new_entries.emit([entry])

            # Check for permission error in stderr after process ends
            if self._process.returncode not in (None, 0, -15):
                stderr = self._process.stderr.read()
                if _is_permission_error(stderr):
                    self.error.emit("PERMISSION_DENIED")
                elif stderr.strip():
                    self.error.emit(stderr.strip())
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
