"""Detected Issues panel: automatic critical pattern detection."""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHeaderView, QFileDialog, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from models.log_entry import LogEntry
from utils.time_utils import format_dmesg_ts
from utils.exporter import export_issues_json

# ---------------------------------------------------------------------------
# Detection rules
# ---------------------------------------------------------------------------
@dataclass
class DetectionRule:
    pattern: re.Pattern
    category: str
    severity: str   # "critical" | "error" | "warning"


_RULES: list[DetectionRule] = [
    DetectionRule(re.compile(r"kernel panic", re.I), "Kernel Panic", "critical"),
    DetectionRule(re.compile(r"segfault", re.I), "Segfault", "error"),
    DetectionRule(re.compile(r"\bBUG:", re.I), "Kernel BUG", "critical"),
    DetectionRule(re.compile(r"\bOops:", re.I), "Kernel Oops", "critical"),
    DetectionRule(re.compile(r"Call Trace:", re.I), "Call Trace", "error"),
    DetectionRule(re.compile(r"I/O error", re.I), "I/O Error", "error"),
    DetectionRule(re.compile(r"EXT4-fs error", re.I), "EXT4 FS Error", "error"),
    DetectionRule(re.compile(r"Out of memory", re.I), "OOM", "critical"),
    DetectionRule(re.compile(r"hardware error", re.I), "Hardware Error", "critical"),
    DetectionRule(re.compile(r"watchdog.*timeout|watchdog.*reset", re.I), "Watchdog Timeout", "critical"),
    DetectionRule(re.compile(r"PCIe.*error|pcie.*error", re.I), "PCIe Error", "error"),
    DetectionRule(re.compile(r"USB disconnect", re.I), "USB Disconnect", "warning"),
    DetectionRule(re.compile(r"ACPI.*error", re.I), "ACPI Error", "error"),
    DetectionRule(re.compile(r"MCE.*error|Machine Check", re.I), "MCE Error", "critical"),
    DetectionRule(re.compile(r"EDAC.*error", re.I), "EDAC Error", "error"),
    DetectionRule(re.compile(r"NMI", re.I), "NMI", "critical"),
    DetectionRule(re.compile(r"soft lockup", re.I), "Soft Lockup", "critical"),
    DetectionRule(re.compile(r"hung_task", re.I), "Hung Task", "error"),
]

SEVERITY_COLORS = {
    "critical": QColor("#ff4444"),
    "error":    QColor("#ff8800"),
    "warning":  QColor("#ffcc00"),
}

COLUMNS = ["Timestamp", "Category", "Severity", "Message"]


@dataclass
class Issue:
    entry: LogEntry
    category: str
    severity: str


def detect_issues(entries: list[LogEntry]) -> list[Issue]:
    issues = []
    for entry in entries:
        for rule in _RULES:
            if rule.pattern.search(entry.message):
                issues.append(Issue(entry=entry, category=rule.category, severity=rule.severity))
                break  # one issue per entry
    return issues


class IssuesPanel(QWidget):
    entry_focus_requested = pyqtSignal(object)   # LogEntry

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        hdr = QHBoxLayout()
        self._count_label = QLabel("No issues detected.")
        hdr.addWidget(self._count_label)
        hdr.addStretch()
        btn_export = QPushButton("Export issues (JSON)")
        btn_export.clicked.connect(self._export)
        hdr.addWidget(btn_export)
        layout.addLayout(hdr)

        self._table = QTableWidget(0, len(COLUMNS))
        self._table.setHorizontalHeaderLabels(COLUMNS)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

        self._issues: list[Issue] = []

    # ------------------------------------------------------------------
    def update_issues(self, issues: list[Issue]):
        self._issues = issues
        self._table.setRowCount(0)
        count = len(issues)
        self._count_label.setText(
            f"{count} issue{'s' if count != 1 else ''} detected."
            if count else "No issues detected."
        )
        for issue in issues:
            row = self._table.rowCount()
            self._table.insertRow(row)

            ts_str = format_dmesg_ts(issue.entry.timestamp, issue.entry.source)
            items = [
                QTableWidgetItem(ts_str),
                QTableWidgetItem(issue.category),
                QTableWidgetItem(issue.severity),
                QTableWidgetItem(issue.entry.message),
            ]
            color = SEVERITY_COLORS.get(issue.severity, QColor("white"))
            for col, item in enumerate(items):
                item.setBackground(color)
                self._table.setItem(row, col, item)

        self._table.resizeColumnsToContents()

    # ------------------------------------------------------------------
    def _on_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self._issues):
            self.entry_focus_requested.emit(self._issues[row].entry)

    def _export(self):
        if not self._issues:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Issues", "issues.json", "JSON (*.json)"
        )
        if path:
            data = [
                {
                    "timestamp": format_dmesg_ts(i.entry.timestamp, i.entry.source),
                    "category": i.category,
                    "severity": i.severity,
                    "message": i.entry.message,
                    "source": i.entry.source,
                }
                for i in self._issues
            ]
            export_issues_json(data, path)
