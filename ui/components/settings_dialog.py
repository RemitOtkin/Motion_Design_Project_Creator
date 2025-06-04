"""
Диалоговое окно настроек приложения
Позволяет пользователю изменять настройки языка и путей
"""

from typing import Dict, Any
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt

from config.translations import Translations
from config.settings import SettingsManager
from ui.styles.stylesheet import StyleSheet


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    def __init__(self, parent=None, settings_manager: SettingsManager = None, current_lang: str = 'ru'):
        """
        Инициализация диалога настроек
        
        Args:
            parent: Родительский виджет
            settings_manager: Менеджер настроек
            current_lang: Текущий язык интерфейса
        """
        super().__init__(parent)
        
        self.settings_manager = settings_manager or SettingsManager()
        self.current_lang = current_lang
        self.t = Translations.get(current_lang)
        
        self._init_ui()
        self._load_current_settings()
    
    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle(self.t['settings_title'])
        self.setFixedSize(500, 300)
        self.setStyleSheet(StyleSheet.get_dialog_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Настройка пути по умолчанию
        self._create_path_section(layout)
        
        # Настройка языка
        self._create_language_section(layout)
        
        # Растягиваем пространство
        layout.addStretch()
        
        # Кнопки управления
        self._create_buttons(layout)
    
    def _create_path_section(self, layout: QVBoxLayout) -> None:
        """
        Создает секцию настройки пути по умолчанию
        
        Args:
            layout: Макет для размещения секции
        """
        path_layout = QVBoxLayout()
        
        # Заголовок секции
        path_label = QLabel(self.t['default_folder'])
        path_layout.addWidget(path_label)
        
        # Поле ввода пути и кнопка обзора
        path_input_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(self.t['project_folder_placeholder'])
        
        self.browse_btn = QPushButton(self.t['browse'])
        self.browse_btn.setObjectName("browse_btn")
        self.browse_btn.clicked.connect(self._browse_folder)
        
        path_input_layout.addWidget(self.path_edit)
        path_input_layout.addWidget(self.browse_btn)
        path_layout.addLayout(path_input_layout)
        
        layout.addLayout(path_layout)
    
    def _create_language_section(self, layout: QVBoxLayout) -> None:
        """
        Создает секцию выбора языка
        
        Args:
            layout: Макет для размещения секции
        """
        lang_layout = QVBoxLayout()
        
        # Заголовок секции
        lang_label = QLabel(self.t['language'])
        lang_layout.addWidget(lang_label)
        
        # Выпадающий список языков
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.addItem("English", "en")
        
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
    
    def _create_buttons(self, layout: QVBoxLayout) -> None:
        """
        Создает кнопки управления диалогом
        
        Args:
            layout: Макет для размещения кнопок
        """
        button_layout = QHBoxLayout()
        
        # Кнопка сохранения
        self.save_btn = QPushButton(self.t['save'])
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.accept)
        
        # Кнопка отмены
        self.cancel_btn = QPushButton(self.t['cancel'])
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _browse_folder(self) -> None:
        """Открывает диалог выбора папки"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            self.t['default_folder'],
            self.path_edit.text()
        )
        if folder:
            self.path_edit.setText(folder)
    
    def _load_current_settings(self) -> None:
        """Загружает текущие настройки в форму"""
        # Загружаем путь по умолчанию
        default_path = self.settings_manager.get('default_path', '')
        self.path_edit.setText(default_path)
        
        # Устанавливаем текущий язык
        current_index = 0 if self.current_lang == 'ru' else 1
        self.lang_combo.setCurrentIndex(current_index)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Получает настройки из формы
        
        Returns:
            Словарь с новыми настройками
        """
        return {
            'default_path': self.path_edit.text().strip(),
            'language': self.lang_combo.currentData()
        }
    
    def validate_settings(self) -> bool:
        """
        Проверяет корректность введенных настроек
        
        Returns:
            True если настройки корректны
        """
        path = self.path_edit.text().strip()
        if path and not self.settings_manager.validate_path(path):
            return False
        return True