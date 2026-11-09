"""Settings: default projects folder and language."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout)

from ..i18n import LANGUAGES, Translator
from . import theme


class SettingsDialog(QDialog):
    def __init__(self, parent, tr: Translator, default_path: str, language: str):
        super().__init__(parent)
        self.tr_ = tr
        self.setWindowTitle(tr("settings_title"))
        self.setModal(True)
        self.setMinimumWidth(520)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 26, 28, 24)
        lay.setSpacing(8)

        title = QLabel(tr("settings_title"))
        title.setObjectName("appTitle")
        lay.addWidget(title)
        lay.addSpacing(14)

        folder_label = QLabel(tr("default_folder"))
        folder_label.setObjectName("fieldLabel")
        lay.addWidget(folder_label)
        row = QHBoxLayout()
        row.setSpacing(8)
        self.path = QLineEdit(default_path)
        self.path.setObjectName("pathEdit")
        folder_label.setBuddy(self.path)
        browse = QPushButton(tr("browse"))
        browse.clicked.connect(self._browse)
        row.addWidget(self.path, 1)
        row.addWidget(browse)
        lay.addLayout(row)
        self.error = QLabel()
        self.error.setObjectName("error")
        self.error.hide()
        lay.addWidget(self.error)
        lay.addSpacing(12)

        lang_label = QLabel(tr("language"))
        lang_label.setObjectName("fieldLabel")
        lay.addWidget(lang_label)
        self.lang = QComboBox()
        for key, name in LANGUAGES.items():
            self.lang.addItem(name, key)
        self.lang.setCurrentIndex(max(0, self.lang.findData(language)))
        lang_label.setBuddy(self.lang)
        lay.addWidget(self.lang)

        lay.addSpacing(22)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton(tr("cancel"))
        cancel.clicked.connect(self.reject)
        save = QPushButton(tr("save"))
        save.setObjectName("smallPrimary")
        save.setStyleSheet("min-height: 44px; padding: 0 20px; font-size: 14px; border-radius: 10px;")
        save.setDefault(True)
        save.clicked.connect(self._accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        lay.addLayout(buttons)

    def showEvent(self, e):
        super().showEvent(e)
        theme.dark_title_bar(self)

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.tr_("choose_folder"), self.path.text())
        if folder:
            self.path.setText(str(Path(folder)))

    def _accept(self) -> None:
        if not Path(self.path.text().strip()).is_dir():
            self.error.setText(self.tr_("err_path_missing"))
            self.error.show()
            return
        self.accept()

    def values(self) -> tuple[str, str]:
        return str(Path(self.path.text().strip())), self.lang.currentData()
