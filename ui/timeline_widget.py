"""Timeline tab: bar/line chart of log frequency over time using PyQtGraph."""
from __future__ import annotations
import math
from collections import defaultdict
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False

from models.log_entry import LogEntry
from utils.time_utils import dmesg_ts_to_epoch


class TimelineWidget(QWidget):
    """Shows log frequency over time with error/warn/info breakdown."""

    time_window_selected = pyqtSignal(float, float)   # (start_epoch, end_epoch)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        if not HAS_PYQTGRAPH:
            layout.addWidget(QLabel(
                "pyqtgraph is not installed.\n"
                "Install it with: pip install pyqtgraph\n"
                "Then restart the application."
            ))
            self._plot = None
            return

        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self._plot_widget = pg.PlotWidget(title="Kernel Log Timeline")
        self._plot_widget.setLabel("left", "Log count / minute")
        self._plot_widget.setLabel("bottom", "Time (epoch seconds)")
        self._plot_widget.addLegend()
        self._plot_widget.setMouseEnabled(x=True, y=False)
        self._plot_widget.showGrid(x=True, y=True)

        # Three bar graph items (stacked via separate curves)
        self._bar_errors   = pg.BarGraphItem(x=[], height=[], width=50, brush="r",   name="errors")
        self._bar_warnings = pg.BarGraphItem(x=[], height=[], width=50, brush="#ff8c00", name="warnings")
        self._bar_info     = pg.BarGraphItem(x=[], height=[], width=50, brush="b",   name="info/other")

        self._plot_widget.addItem(self._bar_errors)
        self._plot_widget.addItem(self._bar_warnings)
        self._plot_widget.addItem(self._bar_info)

        # Region selector for clicking → filter table
        self._region = pg.LinearRegionItem(movable=True)
        self._region.setZValue(10)
        self._region.sigRegionChangeFinished.connect(self._on_region_changed)
        self._plot_widget.addItem(self._region)
        self._region.hide()

        layout.addWidget(self._plot_widget)

        btn_row = QHBoxLayout()
        btn_select = QPushButton("Apply time window to table")
        btn_select.clicked.connect(self._apply_region)
        btn_clear = QPushButton("Clear selection")
        btn_clear.clicked.connect(self._clear_region)
        btn_row.addWidget(btn_select)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._entries: list[LogEntry] = []

    # ------------------------------------------------------------------
    def update_entries(self, entries: list[LogEntry], source: str = "dmesg"):
        """Recompute histogram and redraw."""
        if not HAS_PYQTGRAPH or self._plot_widget is None:
            return
        self._entries = entries
        self._source = source

        if not entries:
            self._bar_errors.setOpts(x=[], height=[])
            self._bar_warnings.setOpts(x=[], height=[])
            self._bar_info.setOpts(x=[], height=[])
            return

        # bucket by minute
        buckets_err: dict[int, int] = defaultdict(int)
        buckets_warn: dict[int, int] = defaultdict(int)
        buckets_info: dict[int, int] = defaultdict(int)

        for e in entries:
            epoch = e.timestamp if source == "journalctl" else dmesg_ts_to_epoch(e.timestamp)
            minute = int(epoch // 60) * 60
            lvl = e.level
            if lvl <= 3:
                buckets_err[minute] += 1
            elif lvl == 4:
                buckets_warn[minute] += 1
            else:
                buckets_info[minute] += 1

        all_minutes = sorted(
            set(buckets_err) | set(buckets_warn) | set(buckets_info)
        )
        if not all_minutes:
            return

        xs = all_minutes
        err_h   = [buckets_err.get(m, 0)   for m in xs]
        warn_h  = [buckets_warn.get(m, 0)  for m in xs]
        info_h  = [buckets_info.get(m, 0)  for m in xs]

        self._bar_errors.setOpts(x=xs, height=err_h, width=50)
        self._bar_warnings.setOpts(x=xs, height=warn_h, width=50)
        self._bar_info.setOpts(x=xs, height=info_h, width=50)
        self._plot_widget.autoRange()

    # ------------------------------------------------------------------
    def _on_region_changed(self):
        self._region.show()

    def _apply_region(self):
        if not HAS_PYQTGRAPH:
            return
        start, end = self._region.getRegion()
        self._region.show()
        self.time_window_selected.emit(start, end)

    def _clear_region(self):
        self._region.hide()
        self.time_window_selected.emit(0.0, 0.0)
