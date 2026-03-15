"""QTableView wrapper for displaying kernel log entries."""
from __future__ import annotations
from PyQt6.QtWidgets import QTableView, QAbstractItemView, QHeaderView
from PyQt6.QtCore import Qt, QModelIndex, pyqtSignal

from models.log_table_model import LogTableModel, LogFilterProxyModel, COL_MSG
from models.log_entry import LogEntry


class LogTableView(QTableView):
    entry_selected = pyqtSignal(object)  # LogEntry

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_model = LogTableModel(self)
        self._proxy = LogFilterProxyModel(self)
        self._proxy.setSourceModel(self._source_model)
        self.setModel(self._proxy)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # default column widths
        self.setColumnWidth(0, 140)   # Timestamp
        self.setColumnWidth(1, 60)    # Level
        self.setColumnWidth(2, 70)    # Facility
        self.setColumnWidth(3, 80)    # Source

        self.selectionModel().currentRowChanged.connect(self._on_row_changed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def source_model(self) -> LogTableModel:
        return self._source_model

    @property
    def proxy_model(self) -> LogFilterProxyModel:
        return self._proxy

    def scroll_to_bottom(self):
        self.scrollToBottom()

    def scroll_to_entry(self, entry: LogEntry):
        """Scroll to and select the row matching the given entry."""
        for row in range(self._source_model.rowCount()):
            if self._source_model.entry_at(row) is entry:
                source_idx = self._source_model.index(row, 0)
                proxy_idx = self._proxy.mapFromSource(source_idx)
                if proxy_idx.isValid():
                    self.scrollTo(proxy_idx)
                    self.selectRow(proxy_idx.row())
                break

    def visible_entry_count(self) -> int:
        return self._proxy.rowCount()

    # ------------------------------------------------------------------
    def _on_row_changed(self, current: QModelIndex, _prev: QModelIndex):
        src_idx = self._proxy.mapToSource(current)
        entry = self._source_model.entry_at(src_idx.row())
        if entry:
            self.entry_selected.emit(entry)
