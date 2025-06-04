"""
Диалог управления структурой папок проекта
Позволяет пользователю настраивать структуру папок
"""

import json
import os
from typing import List, Dict, Any
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTreeWidget, QTreeWidgetItem,
                            QLineEdit, QMessageBox, QInputDialog, QGroupBox,
                            QComboBox, QTextEdit, QSplitter, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from config.translations import Translations
from utils.resource_manager import get_settings_file_path


class FolderStructureDialog(QDialog):
    """Диалог настройки структуры папок"""
    
    structure_changed = pyqtSignal(dict)  # Сигнал об изменении структуры
    
    def __init__(self, parent=None, current_lang: str = 'ru'):
        """
        Инициализация диалога структуры папок
        
        Args:
            parent: Родительский виджет
            current_lang: Текущий язык интерфейса
        """
        super().__init__(parent)
        
        self.current_lang = current_lang
        self.t = Translations.get(current_lang)
        
        # Структуры папок
        self.default_structure = self._get_default_structure()
        self.custom_structures = self._load_custom_structures()
        self.current_structure = self.default_structure.copy()
        
        self._init_ui()
        self._load_structure_to_tree()
    
    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("📁 Настройка структуры папок")
        self.setFixedSize(800, 600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        self._create_header(main_layout)
        
        # Основная область с разделителем
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - управление структурами
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Правая панель - дерево папок
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Устанавливаем пропорции
        splitter.setSizes([250, 550])
        main_layout.addWidget(splitter)
        
        # Кнопки управления
        self._create_buttons(main_layout)
        
        self._apply_styles()
    
    def _create_header(self, layout: QVBoxLayout) -> None:
        """Создает заголовок диалога"""
        header_label = QLabel("Настройка структуры папок проекта")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        description = QLabel(
            "Настройте структуру папок для ваших проектов.\n"
            "Вы можете использовать готовые шаблоны или создать свои."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        layout.addWidget(header_label)
        layout.addWidget(description)
    
    def _create_left_panel(self) -> QGroupBox:
        """Создает левую панель управления"""
        panel = QGroupBox("🎛️ Управление")
        layout = QVBoxLayout(panel)
        
        # Выбор шаблона структуры
        template_group = QGroupBox("📋 Шаблоны")
        template_layout = QVBoxLayout(template_group)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("🏭 Стандартная структура", "default")
        
        # Добавляем пользовательские структуры
        for name in self.custom_structures.keys():
            self.template_combo.addItem(f"👤 {name}", name)
        
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        template_layout.addWidget(self.template_combo)
        
        # Кнопки управления шаблонами
        template_buttons = QHBoxLayout()
        
        self.save_template_btn = QPushButton("💾 Сохранить")
        self.save_template_btn.clicked.connect(self._save_custom_structure)
        
        self.delete_template_btn = QPushButton("🗑️ Удалить")
        self.delete_template_btn.clicked.connect(self._delete_custom_structure)
        
        template_buttons.addWidget(self.save_template_btn)
        template_buttons.addWidget(self.delete_template_btn)
        template_layout.addLayout(template_buttons)
        
        layout.addWidget(template_group)
        
        # Управление папками
        folder_group = QGroupBox("📁 Папки")
        folder_layout = QVBoxLayout(folder_group)
        
        self.add_folder_btn = QPushButton("➕ Добавить папку")
        self.add_folder_btn.clicked.connect(self._add_folder)
        
        self.add_subfolder_btn = QPushButton("📂 Добавить подпапку")
        self.add_subfolder_btn.clicked.connect(self._add_subfolder)
        
        self.edit_folder_btn = QPushButton("✏️ Редактировать")
        self.edit_folder_btn.clicked.connect(self._edit_folder)
        
        self.delete_folder_btn = QPushButton("🗑️ Удалить папку")
        self.delete_folder_btn.clicked.connect(self._delete_folder)
        
        folder_layout.addWidget(self.add_folder_btn)
        folder_layout.addWidget(self.add_subfolder_btn)
        folder_layout.addWidget(self.edit_folder_btn)
        folder_layout.addWidget(self.delete_folder_btn)
        
        layout.addWidget(folder_group)
        
        # Предварительный просмотр
        preview_group = QGroupBox("👁️ Превью")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setFont(QFont("Consolas", 9))
        
        preview_layout.addWidget(self.preview_text)
        layout.addWidget(preview_group)
        
        layout.addStretch()
        return panel
    
    def _create_right_panel(self) -> QGroupBox:
        """Создает правую панель с деревом папок"""
        panel = QGroupBox("🌳 Структура папок")
        layout = QVBoxLayout(panel)
        
        # Дерево папок
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["Папка", "Комментарий"])
        self.folder_tree.setColumnWidth(0, 200)
        self.folder_tree.itemChanged.connect(self._on_item_changed)
        self.folder_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Настройка контекстного меню
        self.folder_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_tree.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.folder_tree)
        
        # Информация
        info_label = QLabel(
            "💡 Совет: Щелкните правой кнопкой для контекстного меню.\n"
            "Дважды щелкните для редактирования названия или комментария."
        )
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        return panel
    
    def _create_buttons(self, layout: QVBoxLayout) -> None:
        """Создает кнопки управления диалогом"""
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("🔄 Сбросить")
        self.reset_btn.clicked.connect(self._reset_to_default)
        
        self.apply_btn = QPushButton("✅ Применить")
        self.apply_btn.clicked.connect(self._apply_changes)
        
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """Возвращает стандартную структуру папок"""
        return {
            "01_IN": {
                "comment": "Входящие материалы",
                "children": {
                    "FOOTAGES": {"comment": "Исходные видеофайлы"},
                    "SFX": {"comment": "Звуковые эффекты и музыка"},
                    "FONTS": {"comment": "Шрифты для проекта"},
                    "ASSETS": {"comment": "Графические материалы, текстуры"}
                }
            },
            "02_PROCESS": {
                "comment": "Рабочие файлы",
                "children": {}  # Заполняется динамически в зависимости от выбранных инструментов
            },
            "03_RENDER": {
                "comment": "Промежуточный рендер",
                "children": {}
            },
            "04_OUT": {
                "comment": "Итоговые материалы",
                "children": {
                    "01_PREVIEW": {"comment": "Превью для заказчика"},
                    "02_STILLSHOTS": {"comment": "Стоп-кадры"},
                    "03_ANIMATIC": {"comment": "Аниматик проекта"},
                    "04_MASTER": {"comment": "Финальные файлы для публикации"}
                }
            }
        }
    
    def _load_custom_structures(self) -> Dict[str, Dict]:
        """Загружает пользовательские структуры"""
        try:
            structures_file = os.path.join(os.path.dirname(get_settings_file_path()), 'folder_structures.json')
            if os.path.exists(structures_file):
                with open(structures_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки пользовательских структур: {e}")
        
        return {}
    
    def _save_custom_structures(self) -> None:
        """Сохраняет пользовательские структуры"""
        try:
            structures_file = os.path.join(os.path.dirname(get_settings_file_path()), 'folder_structures.json')
            os.makedirs(os.path.dirname(structures_file), exist_ok=True)
            
            with open(structures_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_structures, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения пользовательских структур: {e}")
    
    def _load_structure_to_tree(self) -> None:
        """Загружает структуру в дерево"""
        self.folder_tree.clear()
        self._add_items_to_tree(self.current_structure, self.folder_tree.invisibleRootItem())
        self.folder_tree.expandAll()
        self._update_preview()
    
    def _add_items_to_tree(self, structure: Dict, parent_item: QTreeWidgetItem) -> None:
        """Рекурсивно добавляет элементы в дерево"""
        for folder_name, folder_data in structure.items():
            item = QTreeWidgetItem(parent_item)
            item.setText(0, folder_name)
            item.setText(1, folder_data.get("comment", ""))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            
            # Добавляем подпапки
            if "children" in folder_data and folder_data["children"]:
                self._add_items_to_tree(folder_data["children"], item)
    
    def _update_preview(self) -> None:
        """Обновляет предварительный просмотр структуры"""
        preview = self._generate_structure_preview(self.current_structure)
        self.preview_text.setPlainText(preview)
    
    def _generate_structure_preview(self, structure: Dict, prefix: str = "📁 [Проект]/\n") -> str:
        """Генерирует текстовое представление структуры"""
        result = prefix
        
        def add_folder(folder_dict, level=0):
            nonlocal result
            indent = "│   " * level
            
            for i, (name, data) in enumerate(folder_dict.items()):
                is_last = i == len(folder_dict) - 1
                connector = "└── " if is_last else "├── "
                
                comment = data.get("comment", "")
                comment_text = f"  # {comment}" if comment else ""
                
                result += f"{indent}{connector}📁 {name}/{comment_text}\n"
                
                if "children" in data and data["children"]:
                    next_indent = "    " if is_last else "│   "
                    add_folder(data["children"], level + 1)
        
        add_folder(structure)
        return result
    
    def _on_template_changed(self) -> None:
        """Обработчик изменения шаблона"""
        current_data = self.template_combo.currentData()
        
        if current_data == "default":
            self.current_structure = self._get_default_structure()
        elif current_data in self.custom_structures:
            self.current_structure = self.custom_structures[current_data].copy()
        
        self._load_structure_to_tree()
    
    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """Обработчик изменения элемента дерева"""
        self._update_structure_from_tree()
        self._update_preview()
    
    def _on_selection_changed(self) -> None:
        """Обработчик изменения выбора в дереве"""
        selected = self.folder_tree.currentItem()
        
        # Активируем/деактивируем кнопки в зависимости от выбора
        has_selection = selected is not None
        self.add_subfolder_btn.setEnabled(has_selection)
        self.edit_folder_btn.setEnabled(has_selection)
        self.delete_folder_btn.setEnabled(has_selection and selected.parent() is not None)
    
    def _show_context_menu(self, position) -> None:
        """Показывает контекстное меню"""
        item = self.folder_tree.itemAt(position)
        
        menu = QMenu(self)
        
        add_folder_action = menu.addAction("➕ Добавить папку")
        add_folder_action.triggered.connect(self._add_folder)
        
        if item:
            add_subfolder_action = menu.addAction("📂 Добавить подпапку")
            add_subfolder_action.triggered.connect(self._add_subfolder)
            
            menu.addSeparator()
            
            edit_action = menu.addAction("✏️ Редактировать")
            edit_action.triggered.connect(self._edit_folder)
            
            if item.parent():  # Не позволяем удалять корневые папки
                delete_action = menu.addAction("🗑️ Удалить")
                delete_action.triggered.connect(self._delete_folder)
        
        menu.exec_(self.folder_tree.mapToGlobal(position))
    
    def _add_folder(self) -> None:
        """Добавляет новую папку"""
        name, ok = QInputDialog.getText(self, "Новая папка", "Введите название папки:")
        if ok and name.strip():
            name = name.strip()
            comment, ok = QInputDialog.getText(self, "Комментарий", "Введите комментарий (необязательно):")
            if ok:
                item = QTreeWidgetItem(self.folder_tree.invisibleRootItem())
                item.setText(0, name)
                item.setText(1, comment.strip())
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                
                self._update_structure_from_tree()
                self._update_preview()
    
    def _add_subfolder(self) -> None:
        """Добавляет подпапку к выбранной папке"""
        current = self.folder_tree.currentItem()
        if not current:
            return
        
        name, ok = QInputDialog.getText(self, "Новая подпапка", "Введите название подпапки:")
        if ok and name.strip():
            name = name.strip()
            comment, ok = QInputDialog.getText(self, "Комментарий", "Введите комментарий (необязательно):")
            if ok:
                item = QTreeWidgetItem(current)
                item.setText(0, name)
                item.setText(1, comment.strip())
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                
                current.setExpanded(True)
                self._update_structure_from_tree()
                self._update_preview()
    
    def _edit_folder(self) -> None:
        """Редактирует выбранную папку"""
        current = self.folder_tree.currentItem()
        if current:
            # Позволяем редактировать прямо в дереве
            self.folder_tree.editItem(current, 0)
    
    def _delete_folder(self) -> None:
        """Удаляет выбранную папку"""
        current = self.folder_tree.currentItem()
        if not current or not current.parent():
            return
        
        reply = QMessageBox.question(
            self, "Удаление папки",
            f"Удалить папку '{current.text(0)}' и все её подпапки?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            parent = current.parent()
            parent.removeChild(current)
            self._update_structure_from_tree()
            self._update_preview()
    
    def _update_structure_from_tree(self) -> None:
        """Обновляет структуру данных из дерева"""
        self.current_structure = self._tree_to_structure(self.folder_tree.invisibleRootItem())
    
    def _tree_to_structure(self, parent_item: QTreeWidgetItem) -> Dict:
        """Преобразует дерево в структуру данных"""
        structure = {}
        
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            folder_name = child.text(0)
            comment = child.text(1)
            
            folder_data = {"comment": comment}
            
            if child.childCount() > 0:
                folder_data["children"] = self._tree_to_structure(child)
            else:
                folder_data["children"] = {}
            
            structure[folder_name] = folder_data
        
        return structure
    
    def _save_custom_structure(self) -> None:
        """Сохраняет текущую структуру как пользовательскую"""
        name, ok = QInputDialog.getText(self, "Сохранить структуру", "Введите название структуры:")
        if ok and name.strip():
            name = name.strip()
            self.custom_structures[name] = self.current_structure.copy()
            self._save_custom_structures()
            
            # Обновляем комбобокс
            self.template_combo.addItem(f"👤 {name}", name)
            self.template_combo.setCurrentText(f"👤 {name}")
            
            QMessageBox.information(self, "Сохранено", f"Структура '{name}' сохранена!")
    
    def _delete_custom_structure(self) -> None:
        """Удаляет пользовательскую структуру"""
        current_data = self.template_combo.currentData()
        if current_data != "default" and current_data in self.custom_structures:
            reply = QMessageBox.question(
                self, "Удаление структуры",
                f"Удалить структуру '{current_data}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                del self.custom_structures[current_data]
                self._save_custom_structures()
                
                # Обновляем комбобокс
                for i in range(self.template_combo.count()):
                    if self.template_combo.itemData(i) == current_data:
                        self.template_combo.removeItem(i)
                        break
                
                self.template_combo.setCurrentIndex(0)  # Переключаемся на стандартную
                QMessageBox.information(self, "Удалено", f"Структура '{current_data}' удалена!")
    
    def _reset_to_default(self) -> None:
        """Сбрасывает к стандартной структуре"""
        self.current_structure = self._get_default_structure()
        self._load_structure_to_tree()
        self.template_combo.setCurrentIndex(0)
    
    def _apply_changes(self) -> None:
        """Применяет изменения и закрывает диалог"""
        self.structure_changed.emit(self.current_structure)
        self.accept()
    
    def get_current_structure(self) -> Dict[str, Any]:
        """Возвращает текущую структуру"""
        return self.current_structure
    
    def _apply_styles(self) -> None:
        """Применяет стили к диалогу"""
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                background: white;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                padding: 9px 17px;
            }
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background: #fafafa;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                background: #f8f9fa;
                font-family: "Consolas", monospace;
            }
        """)