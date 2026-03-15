"""Main application window."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStatusBar, QTabWidget, QSplitter, QLabel
)
from PyQt6.QtCore import Qt

from ui.toolbar import AppToolBar
from ui.filter_panel import FilterPanel
from ui.log_table import LogTableView
from ui.timeline_widget import TimelineWidget
from ui.issues_panel import IssuesPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMESGVIEWOR — Kernel Log Viewer")
        self.resize(1280, 800)

        # --- Toolbar ---------------------------------------------------
        self.toolbar = AppToolBar(self)
        self.addToolBar(self.toolbar)

        # --- Central widget -------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Horizontal splitter: filter panel | tab area
        h_split = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(h_split)

        # Left: filter panel
        self.filter_panel = FilterPanel()
        h_split.addWidget(self.filter_panel)

        # Right: tabs
        self.tabs = QTabWidget()
        h_split.addWidget(self.tabs)
        h_split.setStretchFactor(0, 0)
        h_split.setStretchFactor(1, 1)

        # Tab 1: Logs
        self.log_table = LogTableView()
        self.tabs.addTab(self.log_table, "Logs")

        # Tab 2: Timeline
        self.timeline = TimelineWidget()
        self.tabs.addTab(self.timeline, "Timeline")

        # Tab 3: Detected Issues
        self.issues_panel = IssuesPanel()
        self.tabs.addTab(self.issues_panel, "Detected Issues")

        # --- Status bar -----------------------------------------------
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._lbl_count   = QLabel("Logs: 0")
        self._lbl_follow  = QLabel("Follow: OFF")
        self._lbl_perm    = QLabel("Permissions: OK")
        self._lbl_source  = QLabel("Source: dmesg")

        self._status_bar.addWidget(self._lbl_count)
        self._status_bar.addWidget(QLabel(" | "))
        self._status_bar.addWidget(self._lbl_follow)
        self._status_bar.addWidget(QLabel(" | "))
        self._status_bar.addWidget(self._lbl_perm)
        self._status_bar.addWidget(QLabel(" | "))
        self._status_bar.addWidget(self._lbl_source)

    # ------------------------------------------------------------------
    # Status bar helpers
    # ------------------------------------------------------------------
    def set_log_count(self, total: int, visible: int):
        self._lbl_count.setText(f"Logs: {visible}/{total}")

    def set_follow_status(self, active: bool):
        self._lbl_follow.setText(f"Follow: {'ON' if active else 'OFF'}")

    def set_permission_status(self, ok: bool):
        self._lbl_perm.setText(f"Permissions: {'OK' if ok else 'RESTRICTED'}")

    def set_source_label(self, source: str):
        self._lbl_source.setText(f"Source: {source}")
