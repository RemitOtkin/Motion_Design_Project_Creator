"""
Основное окно приложения Project Creator
Содержит главный интерфейс и логику взаимодействия с пользователем
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QLineEdit, QCheckBox, QTextEdit,
                            QProgressBar, QStatusBar, QMessageBox, QFileDialog,
                            QApplication, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QIcon

from config.settings import SettingsManager
from config.translations import Translations
from ui.components.animated_button import AnimatedButton
from ui.components.settings_dialog import SettingsDialog
from ui.styles.stylesheet import StyleSheet
from core.project_creator import ProjectCreatorWorker
from utils.platform_utils import open_folder


class ProjectCreatorApp(QMainWindow):
    """Главное окно приложения Project Creator"""

    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        
        # Инициализация настроек
        self.settings_manager = SettingsManager()
        
        # Настройка языка
        self.current_lang = self.settings_manager.get('language', 'ru')
        self.t = Translations.get(self.current_lang)
        
        # Настройка окна
        self.setWindowTitle("🎬 Project Creator v0.2")
        self.resize(1280, 960)
        self.setWindowIcon(self._create_icon())
        
        # Инициализация UI
        self._init_ui()
        self._apply_styles()
        
        # Центрируем окно
        self._center_window()
        
        # Восстанавливаем геометрию окна если сохранена
        saved_geometry = self.settings_manager.get('window_geometry')
        if saved_geometry is not None:
            try:
                self.restoreGeometry(saved_geometry)
            except Exception as e:
                print(f"Предупреждение: Не удалось восстановить геометрию окна: {e}")
    
    def _create_icon(self) -> QIcon:
        """
        Создает иконку для приложения
        
        Returns:
            QIcon с иконкой приложения
        """
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(79, 172, 254))
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.white, 2))
        painter.setFont(QFont("Montserrat", 16, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "PC")
        painter.end()
        
        return QIcon(pixmap)
    
    def _center_window(self) -> None:
        """Центрирует окно на экране"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def _init_ui(self) -> None:
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Создаем компоненты интерфейса
        self._create_header(layout)
        self._create_main_form(layout)
        self._create_progress_bar(layout)
        self._create_buttons(layout)
        self._create_status_bar()
    
    def _create_header(self, layout: QVBoxLayout) -> None:
        """
        Создает заголовок приложения
        
        Args:
            layout: Макет для размещения заголовка
        """
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 20)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Основной заголовок
        self.title = QLabel(self.t['window_title'])
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        # Подзаголовок
        self.subtitle = QLabel(self.t['subtitle'])
        self.subtitle.setObjectName("subtitle") 
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)
        layout.addWidget(header_widget)
    
    def _create_main_form(self, layout: QVBoxLayout) -> None:
        """
        Создает основную форму приложения
        
        Args:
            layout: Макет для размещения формы
        """
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Группа настроек проекта
        self._create_project_settings_group(form_layout)
        
        # Группа инструментов разработки
        self._create_tools_group(form_layout)
        
        # Группа предварительного просмотра
        self._create_preview_group(form_layout)
        
        layout.addWidget(form_widget)
    
    def _create_project_settings_group(self, layout: QVBoxLayout) -> None:
        """
        Создает группу настроек проекта
        
        Args:
            layout: Макет для размещения группы
        """
        self.name_group = QGroupBox(self.t['project_settings'])
        name_layout = QVBoxLayout(self.name_group)
        name_layout.setContentsMargins(15, 25, 15, 15)
        
        # Поле ввода названия проекта
        self.name_label = QLabel(self.t['project_name_label'])
        self.name_label.setObjectName("form_label")
        
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText(self.t['project_name_placeholder'])
        self.project_name.textChanged.connect(self._validate_form)
        
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.project_name)
        
        # Поле выбора пути к проектам
        self._create_path_input(name_layout)
        
        layout.addWidget(self.name_group)
    
    def _create_path_input(self, layout: QVBoxLayout) -> None:
        """
        Создает поле ввода пути к проектам
        
        Args:
            layout: Макет для размещения поля ввода
        """
        path_widget = QWidget()
        path_layout = QVBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 10, 0, 0)
        
        # Метка поля пути
        self.path_label = QLabel(self.t['project_folder_label'])
        self.path_label.setObjectName("form_label")
        path_layout.addWidget(self.path_label)
        
        # Поле ввода и кнопка обзора
        path_input_layout = QHBoxLayout()
        
        self.project_path = QLineEdit()
        self.project_path.setText(self.settings_manager.get_default_path())
        self.project_path.setPlaceholderText(self.t['project_folder_placeholder'])
        self.project_path.textChanged.connect(self._validate_form)
        
        self.browse_btn = AnimatedButton(self.t['browse'])
        self.browse_btn.setObjectName("browse_button")
        self.browse_btn.clicked.connect(self._browse_folder)
        
        path_input_layout.addWidget(self.project_path)
        path_input_layout.addWidget(self.browse_btn)
        path_layout.addLayout(path_input_layout)
        
        layout.addWidget(path_widget)
    
    def _create_tools_group(self, layout: QVBoxLayout) -> None:
        """
        Создает группу выбора инструментов разработки
        
        Args:
            layout: Макет для размещения группы
        """
        self.tools_group = QGroupBox(self.t['dev_tools'])
        tools_layout = QVBoxLayout(self.tools_group)
        tools_layout.setContentsMargins(15, 25, 15, 15)
        
        # Функция для создания контейнера с иконкой и чекбоксом
        def create_tool_container(display_name, icon_filename, fallback_emoji):
            container = QHBoxLayout()
            
            # Иконка
            icon_label = QLabel()
            icon_path = os.path.join("resources", "icons", icon_filename)
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                scaled_pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                icon_label.setText(fallback_emoji)
                icon_label.setStyleSheet("font-size: 18px;")
            
            # Чекбокс
            checkbox = QCheckBox(display_name)
            checkbox.setObjectName("tool_checkbox")
            checkbox.stateChanged.connect(self._update_preview)
            
            container.addWidget(checkbox)
            container.addWidget(icon_label)
           # container.addStretch()
            
            return container, checkbox
        
        # Первая строка
        row1_layout = QHBoxLayout()
        
        # After Effects
        ae_container, self.ae_checkbox = create_tool_container("After Effects", "after_effects.png", "🎬")
        ae_widget = QWidget()
        ae_widget.setLayout(ae_container)
        row1_layout.addWidget(ae_widget)
        
        # Cinema 4D
        c4d_container, self.c4d_checkbox = create_tool_container("Cinema 4D", "cinema4d.png", "🎭")
        c4d_widget = QWidget()
        c4d_widget.setLayout(c4d_container)
        row1_layout.addWidget(c4d_widget)
        
        # Premiere Pro
        pr_container, self.pr_checkbox = create_tool_container("Premiere Pro", "premiere_pro.png", "🎞️")
        pr_widget = QWidget()
        pr_widget.setLayout(pr_container)
        row1_layout.addWidget(pr_widget)
        
        row1_layout.addStretch()
        
        # Вторая строка
        row2_layout = QHBoxLayout()
        
        # Houdini
        houdini_container, self.houdini_checkbox = create_tool_container("Houdini", "houdini.png", "🌪️")
        houdini_widget = QWidget()
        houdini_widget.setLayout(houdini_container)
        row2_layout.addWidget(houdini_widget)
        
        # Blender
        blender_container, self.blender_checkbox = create_tool_container("Blender", "blender.png", "🍊")
        blender_widget = QWidget()
        blender_widget.setLayout(blender_container)
        row2_layout.addWidget(blender_widget)
        
        row2_layout.addStretch()
        
        # Добавляем строки в основной layout
        tools_layout.addLayout(row1_layout)
        tools_layout.addLayout(row2_layout)
        
        layout.addWidget(self.tools_group)
    
    def _create_preview_group(self, layout: QVBoxLayout) -> None:
        """
        Создает группу предварительного просмотра структуры
        
        Args:
            layout: Макет для размещения группы
        """
        self.preview_group = QGroupBox(self.t['project_structure'])
        preview_layout = QVBoxLayout(self.preview_group)
        preview_layout.setContentsMargins(15, 25, 15, 15)
        
        self.structure_text = QTextEdit()
        self.structure_text.setReadOnly(True)
        self.structure_text.setMaximumHeight(250)
        
        preview_layout.addWidget(self.structure_text)
        layout.addWidget(self.preview_group)
        
        # Обновляем предварительный просмотр
        self._update_preview()
    
    def _create_progress_bar(self, layout: QVBoxLayout) -> None:
        """
        Создает прогресс-бар
        
        Args:
            layout: Макет для размещения прогресс-бара
        """
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
    
    def _create_buttons(self, layout: QVBoxLayout) -> None:
        """
        Создает кнопки управления
        
        Args:
            layout: Макет для размещения кнопок
        """
        button_layout = QHBoxLayout()
        
        # Основная кнопка создания проекта
        self.create_btn = AnimatedButton(self.t['create_project'])
        self.create_btn.setObjectName("create_button")
        self.create_btn.clicked.connect(self._create_project)
        self.create_btn.setEnabled(False)
        
        # Кнопка сброса формы
        self.reset_btn = AnimatedButton(self.t['reset'])
        self.reset_btn.setObjectName("secondary_button")
        self.reset_btn.clicked.connect(self._reset_form)
        
        # Кнопка настроек
        self.settings_btn = AnimatedButton(self.t['settings'])
        self.settings_btn.setObjectName("secondary_button")
        self.settings_btn.clicked.connect(self._show_settings)
        
        # Кнопка открытия папки проектов
        self.open_folder_btn = AnimatedButton(self.t['open_folder'])
        self.open_folder_btn.setObjectName("secondary_button")
        self.open_folder_btn.clicked.connect(self._open_projects_folder)
        
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.settings_btn)
        button_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(button_layout)
    
    def _create_status_bar(self) -> None:
        """Создает строку состояния"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.t['ready'])
    
    def _apply_styles(self) -> None:
        """Применяет стили к интерфейсу"""
        self.setStyleSheet(StyleSheet.get_main_stylesheet())
    
    def _browse_folder(self) -> None:
        """Открывает диалог выбора папки для проектов"""
        folder = QFileDialog.getExistingDirectory(
            self, self.t['browse'], 
            self.project_path.text()
        )
        if folder:
            self.project_path.setText(folder)
    
    def _validate_form(self) -> None:
        """Проверяет корректность заполнения формы"""
        name = self.project_name.text().strip()
        path = self.project_path.text().strip()
        
        # Проверяем минимальную длину имени и существование пути
        valid = len(name) >= 3 and os.path.exists(path)
        self.create_btn.setEnabled(valid)
        
        # Обновляем статус
        if valid:
            self.status_bar.showMessage(self.t['ready_to_create'])
        else:
            self.status_bar.showMessage(self.t['fill_fields'])
    
    def _update_preview(self) -> None:
        """Обновляет предварительный просмотр структуры проекта"""
        structure = f"""📁 [{self.t['project_name_label'].replace(':', '')}]/
├── 📁 01_IN/
│   ├── 📁 FOOTAGES/     {self.t['structure_comments']['footages']}
│   ├── 📁 SFX/          {self.t['structure_comments']['sfx']}  
│   ├── 📁 FONTS/        {self.t['structure_comments']['fonts']}
│   └── 📁 ASSETS/       {self.t['structure_comments']['assets']}
├── 📁 02_PROCESS/"""
        
        # Добавляем папки для выбранных инструментов
        if self.ae_checkbox.isChecked():
            structure += f"\n│   ├── 📁 AE/            {self.t['structure_comments']['ae']}"
        if self.c4d_checkbox.isChecked():
            structure += f"\n│   ├── 📁 C4D/           {self.t['structure_comments']['c4d']}"
        if hasattr(self, 'pr_checkbox') and self.pr_checkbox.isChecked():
            structure += f"\n│   ├── 📁 PR/            {self.t['structure_comments'].get('pr', '# Premiere Pro проекты')}"
        if hasattr(self, 'houdini_checkbox') and self.houdini_checkbox.isChecked():
            structure += f"\n│   ├── 📁 HOUDINI/       {self.t['structure_comments'].get('houdini', '# Houdini проекты')}"
        if hasattr(self, 'blender_checkbox') and self.blender_checkbox.isChecked():
            structure += f"\n│   ├── 📁 BLENDER/       {self.t['structure_comments'].get('blender', '# Blender проекты')}"
            
        structure += f"""
├── 📁 03_RENDER/        {self.t['structure_comments']['render']}
└── 📁 04_OUT/
    ├── 📁 01_PREVIEW/   {self.t['structure_comments']['preview']}
    ├── 📁 02_STILLSHOTS/ {self.t['structure_comments']['stillshots']}  
    ├── 📁 03_ANIMATIC/  {self.t['structure_comments']['animatic']}
    └── 📁 04_MASTER/    {self.t['structure_comments']['master']}"""
        
        self.structure_text.setPlainText(structure)
    
    def _create_project(self) -> None:
        """Запускает процесс создания проекта"""
        project_name = self.project_name.text().strip()
        base_path = self.project_path.text().strip()
        
        # Собираем список выбранных инструментов
        tools = []
        if self.ae_checkbox.isChecked():
            tools.append('ae')
        if self.c4d_checkbox.isChecked():
            tools.append('c4d')
        if self.pr_checkbox.isChecked():
            tools.append('pr')
        if self.houdini_checkbox.isChecked():
            tools.append('houdini')
        if self.blender_checkbox.isChecked():
            tools.append('blender')
        
        # Проверяем, что выбран хотя бы один инструмент
        if not tools:
            QMessageBox.warning(self, self.t['warning'], 
                              self.t['select_tool_warning'])
            return
        
        project_data = {
            'name': project_name,
            'tools': tools
        }
        
        # Блокируем интерфейс и показываем прогресс
        self._set_ui_creating_state(True)
        
        # Запускаем рабочий поток
        self.worker = ProjectCreatorWorker(project_data, base_path, self.current_lang)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self._on_project_created)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()
    
    def _set_ui_creating_state(self, creating: bool) -> None:
        """
        Устанавливает состояние интерфейса во время создания проекта
        
        Args:
            creating: True если идет создание, False если завершено
        """
        self.create_btn.setEnabled(not creating)
        self.create_btn.setText(self.t['creating'] if creating else self.t['create_project'])
        self.progress_bar.setVisible(creating)
        if creating:
            self.progress_bar.setValue(0)
    
    def _on_project_created(self, result: dict) -> None:
        """
        Обработчик успешного создания проекта
        
        Args:
            result: Результат создания проекта
        """
        self._set_ui_creating_state(False)
        
        # Показываем сообщение об успехе
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(self.t['success'])
        msg.setText(self.t['project_created'].format(result['name']))
        
        # Добавляем детальную информацию
        details = f"""📁 {self.t['path']}: {result['path']}
                      📂 {self.t['folders_created']}: {result['folders_created']}
                      📄 {self.t['files_created']}: {result['files_created']}
                      🛠️ {self.t['tools']}: {', '.join(result['tools'])}
                      🎉 {self.t['project_ready']}"""
        
        msg.setDetailedText(details)
        msg.addButton(self.t['open_folder'], QMessageBox.ActionRole)
        msg.addButton(self.t['ok'], QMessageBox.AcceptRole)
        
        reply = msg.exec_()
        if reply == 0:  # Открыть папку
            open_folder(result['path'])
        
        # Сбрасываем форму и обновляем статус
        self._reset_form()
        self.status_bar.showMessage(self.t['project_created_success'].format(result['name']))
        
        # Сохраняем последний использованный путь
        self.settings_manager.set('last_project_path', result['path'])
    
    def _on_error(self, error_message: str) -> None:
        """
        Обработчик ошибки создания проекта
        
        Args:
            error_message: Сообщение об ошибке
        """
        self._set_ui_creating_state(False)
        
        QMessageBox.critical(self, self.t['error'], f"❌ {error_message}")
        self.status_bar.showMessage(self.t['creation_error'])
    
    def _reset_form(self) -> None:
        """Сбрасывает форму к начальному состоянию"""
        self.project_name.clear()
        self.ae_checkbox.setChecked(False)
        self.c4d_checkbox.setChecked(False)
        if hasattr(self, 'pr_checkbox'):
            self.pr_checkbox.setChecked(False)
        if hasattr(self, 'houdini_checkbox'):
            self.houdini_checkbox.setChecked(False)
        if hasattr(self, 'blender_checkbox'):
            self.blender_checkbox.setChecked(False)
        self._update_preview()
        self._validate_form()
    
    def _show_settings(self) -> None:
        """Показывает диалог настроек"""
        dialog = SettingsDialog(self, self.settings_manager, self.current_lang)
        if dialog.exec_() == SettingsDialog.Accepted:
            # Получаем новые настройки
            new_settings = dialog.get_settings()
            self.settings_manager.update(new_settings)
            self.settings_manager.save_settings()
            
            # Обновляем путь к проектам
            self.project_path.setText(new_settings.get('default_path', ''))
            
            # Если язык изменился, обновляем интерфейс
            new_lang = new_settings.get('language', self.current_lang)
            if new_lang != self.current_lang:
                self.current_lang = new_lang
                self.t = Translations.get(new_lang)
                self._update_ui_texts()
    
    def _update_ui_texts(self) -> None:
        """Обновляет тексты интерфейса при смене языка"""
        self.title.setText(self.t['window_title'])
        self.subtitle.setText(self.t['subtitle'])
        self.name_group.setTitle(self.t['project_settings'])
        self.name_label.setText(self.t['project_name_label'])
        self.project_name.setPlaceholderText(self.t['project_name_placeholder'])
        self.path_label.setText(self.t['project_folder_label'])
        self.project_path.setPlaceholderText(self.t['project_folder_placeholder'])
        self.browse_btn.setText(self.t['browse'])
        self.tools_group.setTitle(self.t['dev_tools'])
        self.preview_group.setTitle(self.t['project_structure'])
        self.create_btn.setText(self.t['create_project'])
        self.reset_btn.setText(self.t['reset'])
        self.settings_btn.setText(self.t['settings'])
        self.open_folder_btn.setText(self.t['open_folder'])
        self.status_bar.showMessage(self.t['ready'])
        self._update_preview()
    
    def _open_projects_folder(self) -> None:
        """Открывает папку с проектами"""
        path = self.project_path.text()
        if os.path.exists(path):
            open_folder(path)
        else:
            QMessageBox.warning(self, self.t['warning'], self.t['folder_not_exists'])
    
    def closeEvent(self, event) -> None:
        """
        Обработчик закрытия приложения
        
        Args:
            event: Событие закрытия
        """
        try:
            # Сохраняем геометрию окна
            self.settings_manager.set('window_geometry', self.saveGeometry())
            self.settings_manager.save_settings()
        except Exception as e:
            print(f"Предупреждение: Не удалось сохранить настройки при закрытии: {e}")
        
        event.accept()