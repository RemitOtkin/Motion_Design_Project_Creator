"""
Модуль управления ресурсами
Обеспечивает правильный доступ к файлам ресурсов в dev-режиме и после сборки PyInstaller
"""

import sys
import os


def resource_path(relative_path: str) -> str:
  
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # В режиме разработки используем текущую директорию
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_app_data_path() -> str:
  
    if sys.platform == 'win32':
        # Windows: используем APPDATA
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'ProjectCreator')
    elif sys.platform == 'darwin':
        # macOS: используем ~/Library/Application Support
        return os.path.expanduser('~/Library/Application Support/ProjectCreator')
    else:
        # Linux: используем ~/.config
        return os.path.expanduser('~/.config/ProjectCreator')


def ensure_app_data_dir() -> str:
 
    app_data_path = get_app_data_path()
    os.makedirs(app_data_path, exist_ok=True)
    return app_data_path


def get_settings_file_path() -> str:
  
    app_data_path = ensure_app_data_dir()
    return os.path.join(app_data_path, 'settings.json')


def get_log_file_path() -> str:
 
    app_data_path = ensure_app_data_dir()
    return os.path.join(app_data_path, 'app.log')


def resource_exists(relative_path: str) -> bool:
   
    return os.path.exists(resource_path(relative_path))


def get_template_path(template_name: str) -> str:
  
    return resource_path(f"resources/templates/{template_name}")


def get_icon_path(icon_name: str) -> str:

    return resource_path(f"resources/icons/{icon_name}")