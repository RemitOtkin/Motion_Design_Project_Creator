"""
Модуль переводов для Project Creator
Содержит все текстовые ресурсы для русского и английского языков
"""


class Translations:
    """Класс для хранения переводов интерфейса"""
    
    RU = {
        'window_title': 'Remit Otkin Project Creator',
        'subtitle': 'Персональный инструмент <br> для создания структуры медиа-проектов',
        'project_settings': '📁 Настройки проекта',
        'project_name_label': 'Название проекта:',
        'project_name_placeholder': 'Введите название проекта...',
        'project_folder_label': 'Папка для проектов:',
        'project_folder_placeholder': 'Выберите папку для проектов...',
        'browse': '📂 Обзор',
        'dev_tools': '🛠️ Инструменты разработки',
        'project_structure': '📂 Структура проекта',
        'create_project': '🗃️ Создать проект',
        'reset': '🔄 Сбросить',
        'settings': '⚙️ Настройки',
        'open_folder': '📂 Открыть папку',
        'ready': 'Готов к созданию проектов',
        'ready_to_create': 'Готов к созданию проекта',
        'fill_fields': 'Заполните все поля корректно',
        'select_tool_warning': 'Выберите хотя бы один инструмент разработки!',
        'creating': '⏳ Создание...',
        'success': 'Успех!',
        'project_created': 'Проект \'{}\' успешно создан!',
        'path': 'Путь',
        'folders_created': 'Создано папок',
        'files_created': 'Создано файлов',
        'tools': 'Инструменты',
        'project_ready': 'Проект готов к работе!',
        'ok': '✅ OK',
        'error': 'Ошибка',
        'project_exists': 'Проект \'{}\' уже существует!',
        'creation_error': 'Ошибка при создании проекта',
        'project_created_success': 'Проект \'{}\' создан успешно',
        'settings_title': '⚙️ Настройки',
        'default_folder': 'Папка по умолчанию:',
        'language': 'Язык:',
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'folder_not_exists': 'Папка не существует!',
        'warning': 'Предупреждение',
        'structure_comments': {
            'footages': '# исходные видео',
            'sfx': '# звуковые эффекты',
            'fonts': '# шрифты',
            'assets': '# ресурсы',
            'ae': '# After Effects проекты',
            'c4d': '# Cinema 4D проекты',
            'pr': '# Premiere Pro проекты',        
            'houdini': '# Houdini проекты',         
            'blender': '# Blender проекты',         
            'render': '# рендер файлы',
            'preview': '# превью',
            'stillshots': '# кадры',
            'animatic': '# аниматик',
            'master': '# финальные файлы'
        }
    }
    
    EN = {
        'window_title': 'Remit Otkin Project Creator',
        'subtitle': 'Personal tool <br> for creating media project structures',
        'project_settings': '📁 Project Settings',
        'project_name_label': 'Project name:',
        'project_name_placeholder': 'Enter project name...',
        'project_folder_label': 'Projects folder:',
        'project_folder_placeholder': 'Select projects folder...',
        'browse': '📂 Browse',
        'dev_tools': '🛠️ Development Tools',
        'project_structure': '📦 Project Structure',
        'create_project': '🗃️ Create Project',
        'reset': '🔄 Reset',
        'settings': '⚙️ Settings',
        'open_folder': '📂 Open Folder',
        'ready': 'Ready to create projects',
        'ready_to_create': 'Ready to create project',
        'fill_fields': 'Fill all fields correctly',
        'select_tool_warning': 'Select at least one development tool!',
        'creating': '⏳ Creating...',
        'success': 'Success!',
        'project_created': 'Project \'{}\' created successfully!',
        'path': 'Path',
        'folders_created': 'Folders created',
        'files_created': 'Files created',
        'tools': 'Tools',
        'project_ready': 'Project is ready to work!',
        'ok': '✅ OK',
        'error': 'Error',
        'project_exists': 'Project \'{}\' already exists!',
        'creation_error': 'Error creating project',
        'project_created_success': 'Project \'{}\' created successfully',
        'settings_title': '⚙️ Settings',
        'default_folder': 'Default folder:',
        'language': 'Language:',
        'save': 'Save',
        'cancel': 'Cancel',
        'folder_not_exists': 'Folder does not exist!',
        'warning': 'Warning',
        'structure_comments': {
            'footages': '# source videos',
            'sfx': '# sound effects',
            'fonts': '# fonts',
            'assets': '# resources',
            'ae': '# After Effects projects',
            'c4d': '# Cinema 4D projects',
            'pr': '# Premiere Pro projects',        
            'houdini': '# Houdini projects',         
            'blender': '# Blender projects',         
            'render': '# render files',
            'preview': '# preview',
            'stillshots': '# frames',
            'animatic': '# animatic',
            'master': '# final files'
        }
    }

    @classmethod
    def get(cls, lang='ru'):
        """Получить словарь переводов для указанного языка"""
        return cls.RU if lang == 'ru' else cls.EN