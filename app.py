"""Application entry point: creates QApplication and MainWindow."""
from __future__ import annotations
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from controllers.main_controller import MainController


def run():
    app = QApplication(sys.argv)
    app.setApplicationName("DMESGVIEWOR")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("dmesgviewor")

    window = MainWindow()
    controller = MainController(window)   # noqa: F841 – keeps controller alive
    window.show()

    sys.exit(app.exec())
