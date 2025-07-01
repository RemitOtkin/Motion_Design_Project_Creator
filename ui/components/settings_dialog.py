"""
Диалоговое окно настроек приложения
Позволяет пользователю изменять настройки языка и путей
"""

from typing import Dict, Any
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QFileDialog, QWidget)
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
        
        self.setFixedSize(750, 500)  
        self.setStyleSheet(StyleSheet.get_dialog_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Увеличили отступы
        layout.setContentsMargins(30, 30, 30, 30)  # Увеличили отступы
        
        self._create_path_section(layout)
        
        self._create_language_buttons_section(layout)
        
          
    def _create_path_section(self, layout: QVBoxLayout) -> None:
    
        # Создаем контейнер для секции
        path_widget = QWidget()
        path_widget.setObjectName("path_section")
        path_layout = QVBoxLayout(path_widget)
        path_layout.setSpacing(12)
        path_layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок секции
        path_label = QLabel(self.t['default_folder'])
        path_layout.addWidget(path_label)
        
        # Поле ввода пути и кнопка обзора
        path_input_layout = QHBoxLayout()
        path_input_layout.setSpacing(12)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(self.t['project_folder_placeholder'])
        
        self.browse_btn = QPushButton(self.t['browse'])
        self.browse_btn.setObjectName("browse_btn")
        self.browse_btn.clicked.connect(self._browse_folder)
        # Ограничиваем ширину кнопки обзора
        self.browse_btn.setMaximumWidth(120)
        
        path_input_layout.addWidget(self.path_edit, 1)  # Растягиваем поле ввода
        path_input_layout.addWidget(self.browse_btn, 0)  # Фиксированная ширина кнопки
        
        path_layout.addLayout(path_input_layout)
        layout.addWidget(path_widget)
    
    def _create_language_buttons_section(self, layout: QVBoxLayout) -> None:
    
        lang_buttons_widget = QWidget()
        lang_buttons_widget.setObjectName("language_buttons_section")
        main_layout = QVBoxLayout(lang_buttons_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Горизонтальный layout для языка и кнопок
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(20)
        
        # Левая часть - выбор языка
        language_layout = QVBoxLayout()
        language_layout.setSpacing(8)
        
        lang_label = QLabel(self.t['language'])
        language_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.addItem("English", "en")
        language_layout.addWidget(self.lang_combo)
        
        # Правая часть - кнопки
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Добавляем небольшой отступ сверху для выравнивания с комбобоксом
        buttons_layout.addSpacing(26)  # Примерно высота label
        
        buttons_horizontal = QHBoxLayout()
        buttons_horizontal.setSpacing(12)
        
        self.save_btn = QPushButton(self.t['save'])
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton(self.t['cancel'])
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_horizontal.addWidget(self.save_btn)
        buttons_horizontal.addWidget(self.cancel_btn)
        buttons_layout.addLayout(buttons_horizontal)
        
        # Добавляем части в горизонтальный layout
        horizontal_layout.addLayout(language_layout)
        horizontal_layout.addStretch()  # Растягиваем пространство между языком и кнопками
        horizontal_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(horizontal_layout)
        layout.addWidget(lang_buttons_widget)
    
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