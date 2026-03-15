"""Left-side filter panel: level checkboxes + facility multi-select."""
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox,
    QListWidget, QListWidgetItem, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt

from models.log_entry import LEVEL_NAMES, FACILITY_NAMES

DISPLAY_FACILITIES = {
    0: "kern", 1: "user", 3: "daemon", 4: "auth",
    5: "syslog", 6: "lpr", 7: "news", 9: "cron",
}


class FilterPanel(QWidget):
    levels_changed = pyqtSignal(set)
    facilities_changed = pyqtSignal(set)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setFixedWidth(160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # --- Level group -----------------------------------------------
        level_group = QGroupBox("Log Levels")
        level_layout = QVBoxLayout(level_group)
        level_layout.setContentsMargins(4, 4, 4, 4)
        self._level_checks: dict[int, QCheckBox] = {}
        for lvl in range(8):
            cb = QCheckBox(LEVEL_NAMES[lvl])
            cb.setChecked(True)
            cb.stateChanged.connect(self._emit_levels)
            level_layout.addWidget(cb)
            self._level_checks[lvl] = cb
        layout.addWidget(level_group)

        # --- Facility group --------------------------------------------
        fac_group = QGroupBox("Facilities")
        fac_layout = QVBoxLayout(fac_group)
        fac_layout.setContentsMargins(4, 4, 4, 4)
        self._facility_list = QListWidget()
        self._facility_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection
        )
        for fid, fname in DISPLAY_FACILITIES.items():
            item = QListWidgetItem(fname)
            item.setData(Qt.ItemDataRole.UserRole, fid)
            self._facility_list.addItem(item)
            item.setSelected(True)
        self._facility_list.itemSelectionChanged.connect(self._emit_facilities)
        fac_layout.addWidget(self._facility_list)
        layout.addWidget(fac_group)
        layout.addStretch()

    # ------------------------------------------------------------------
    def _emit_levels(self):
        allowed = {lvl for lvl, cb in self._level_checks.items() if cb.isChecked()}
        self.levels_changed.emit(allowed)

    def _emit_facilities(self):
        allowed = set()
        for item in self._facility_list.selectedItems():
            allowed.add(item.data(Qt.ItemDataRole.UserRole))
        # If none selected → show all (avoid empty set blocking everything)
        if not allowed:
            allowed = set(DISPLAY_FACILITIES.keys())
        self.facilities_changed.emit(allowed)

    def get_allowed_levels(self) -> set[int]:
        return {lvl for lvl, cb in self._level_checks.items() if cb.isChecked()}

    def get_allowed_facilities(self) -> set[int]:
        selected = {
            item.data(Qt.ItemDataRole.UserRole)
            for item in self._facility_list.selectedItems()
        }
        return selected if selected else set(DISPLAY_FACILITIES.keys())
