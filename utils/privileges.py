"""Permission helpers and sudo password dialog."""
from __future__ import annotations
import subprocess
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class SudoPasswordDialog(QDialog):
    """Modal dialog asking for the sudo password."""

    def __init__(self, parent=None, message: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Authentification requise")
        self.setMinimumWidth(420)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Icon + explanation
        info = QLabel(
            "<b>DMESGVIEWOR nécessite des droits élevés</b><br><br>"
            "L'accès aux journaux du noyau (<code>dmesg</code>) est restreint "
            "sur ce système.<br>"
            "Veuillez entrer votre mot de passe <b>sudo</b> pour continuer."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        if message:
            extra = QLabel(f"<i>{message}</i>")
            extra.setStyleSheet("color: #c0392b;")
            extra.setWordWrap(True)
            layout.addWidget(extra)

        # Password field
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel("Mot de passe :"))
        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pwd_edit.setPlaceholderText("sudo password…")
        self._pwd_edit.returnPressed.connect(self._accept)
        pwd_layout.addWidget(self._pwd_edit)
        layout.addLayout(pwd_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_ok = QPushButton("Valider")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._accept)
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)

        # Hint about permanent fix
        hint = QLabel(
            "<small>Conseil : pour éviter cette demande à chaque lancement, "
            "ajoutez votre utilisateur au groupe <code>adm</code> :<br>"
            "<code>sudo usermod -aG adm $USER</code> (puis reconnectez-vous)</small>"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #555;")
        layout.addWidget(hint)

    def _accept(self):
        if self._pwd_edit.text():
            self.accept()

    def password(self) -> str:
        return self._pwd_edit.text()


def ask_sudo_password(parent=None, error_message: str = "") -> Optional[str]:
    """Show the sudo password dialog. Returns the password or None if cancelled."""
    dlg = SudoPasswordDialog(parent, message=error_message)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        return dlg.password()
    return None


def verify_sudo_password(password: str) -> bool:
    """Check if the given password is a valid sudo password."""
    try:
        result = subprocess.run(
            ["sudo", "-S", "-v"],
            input=password + "\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False
