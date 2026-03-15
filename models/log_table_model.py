"""QAbstractTableModel for kernel log entries."""
from __future__ import annotations
import re
from typing import Optional

from PyQt6.QtCore import (
    QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel,
    pyqtSignal
)
from PyQt6.QtGui import QColor, QFont

from models.log_entry import LogEntry, LEVEL_NAMES

# --- colour palette --------------------------------------------------------
LEVEL_COLORS = {
    0: (QColor("#ff0000"), QColor("white")),   # emerg   bg red / white text
    1: (QColor("#ff0000"), QColor("white")),   # alert   bg red / white text
    2: (QColor("#8b0000"), QColor("white")),   # crit    dark red bg
    3: (QColor("white"),   QColor("red")),     # err     red text
    4: (QColor("white"),   QColor("#ff8c00")), # warn    orange text
    5: (QColor("white"),   QColor("#00008b")), # notice  blue text
    6: (QColor("white"),   QColor("black")),   # info    black text
    7: (QColor("white"),   QColor("#808080")), # debug   gray text
}

COLUMNS = ["Timestamp", "Level", "Facility", "Source", "Message"]
COL_TS, COL_LEVEL, COL_FACILITY, COL_SOURCE, COL_MSG = range(5)

MAX_ENTRIES = 50_000


class LogTableModel(QAbstractTableModel):
    """Stores up to MAX_ENTRIES log entries and exposes them to a QTableView."""

    rowCountChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries: list[LogEntry] = []

    # ------------------------------------------------------------------
    # QAbstractTableModel interface
    # ------------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._entries)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return COLUMNS[section]
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        entry = self._entries[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == COL_TS:
                return f"{entry.timestamp:.6f}"
            if col == COL_LEVEL:
                return entry.level_name
            if col == COL_FACILITY:
                return entry.facility_name
            if col == COL_SOURCE:
                return entry.source
            if col == COL_MSG:
                return entry.message

        if role == Qt.ItemDataRole.BackgroundRole:
            bg, _ = LEVEL_COLORS.get(entry.level, (QColor("white"), QColor("black")))
            return bg

        if role == Qt.ItemDataRole.ForegroundRole:
            _, fg = LEVEL_COLORS.get(entry.level, (QColor("white"), QColor("black")))
            return fg

        if role == Qt.ItemDataRole.UserRole:
            return entry

        return None

    # ------------------------------------------------------------------
    # Data management
    # ------------------------------------------------------------------
    def set_entries(self, entries: list[LogEntry]):
        self.beginResetModel()
        self._entries = entries[-MAX_ENTRIES:]
        self.endResetModel()
        self.rowCountChanged.emit(len(self._entries))

    def append_entries(self, new_entries: list[LogEntry]):
        if not new_entries:
            return
        overflow = len(self._entries) + len(new_entries) - MAX_ENTRIES
        if overflow > 0:
            self.beginRemoveRows(QModelIndex(), 0, overflow - 1)
            self._entries = self._entries[overflow:]
            self.endRemoveRows()

        first = len(self._entries)
        last = first + len(new_entries) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        self._entries.extend(new_entries)
        self.endInsertRows()
        self.rowCountChanged.emit(len(self._entries))

    def entry_at(self, row: int) -> Optional[LogEntry]:
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None

    def all_entries(self) -> list[LogEntry]:
        return list(self._entries)

    def clear(self):
        self.beginResetModel()
        self._entries = []
        self.endResetModel()
        self.rowCountChanged.emit(0)


# ---------------------------------------------------------------------------
# Proxy model: level + facility + search filtering
# ---------------------------------------------------------------------------
class LogFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._allowed_levels: set[int] = set(range(8))
        self._allowed_facilities: set[int] = set(range(24))
        self._search_pattern: str = ""
        self._search_regex: bool = False
        self._search_case: bool = False
        self._compiled: Optional[re.Pattern] = None

        self.setSortRole(Qt.ItemDataRole.UserRole)

    # ------------------------------------------------------------------
    # Filter setters
    # ------------------------------------------------------------------
    def set_allowed_levels(self, levels: set[int]):
        self._allowed_levels = levels
        self.invalidateFilter()

    def set_allowed_facilities(self, facilities: set[int]):
        self._allowed_facilities = facilities
        self.invalidateFilter()

    def set_search(self, pattern: str, use_regex: bool, case_sensitive: bool):
        self._search_pattern = pattern
        self._search_regex = use_regex
        self._search_case = case_sensitive
        self._compiled = None
        if pattern:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                p = pattern if use_regex else re.escape(pattern)
                self._compiled = re.compile(p, flags)
            except re.error:
                self._compiled = None
        self.invalidateFilter()

    # ------------------------------------------------------------------
    # QSortFilterProxyModel override
    # ------------------------------------------------------------------
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        source_model: LogTableModel = self.sourceModel()
        entry = source_model.entry_at(source_row)
        if entry is None:
            return False

        if entry.level not in self._allowed_levels:
            return False
        if entry.facility not in self._allowed_facilities:
            return False

        if self._compiled:
            if not self._compiled.search(entry.message):
                return False

        return True
