"""
Модуль управления ресурсами
Обеспечивает правильный доступ к файлам ресурсов в dev-режиме и после сборки PyInstaller
"""

import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Получает абсолютный путь к ресурсу
    Работает как в режиме разработки, так и после сборки PyInstaller
    
    Args:
        relative_path: Относительный путь к ресурсу
        
    Returns:
        Абсолютный путь к ресурсу
    """
    try:
        # PyInstaller создает временную папку и сохраняет путь в _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # В режиме разработки используем текущую директорию
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_app_data_path() -> str:
    """
    Получает путь к папке данных приложения
    
    Returns:
        Путь к папке данных приложения
    """
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
    """
    Создает папку данных приложения если она не существует
    
    Returns:
        Путь к папке данных приложения
    """
    app_data_path = get_app_data_path()
    os.makedirs(app_data_path, exist_ok=True)
    return app_data_path


def get_settings_file_path() -> str:
    """
    Получает полный путь к файлу настроек
    
    Returns:
        Путь к файлу настроек
    """
    app_data_path = ensure_app_data_dir()
    return os.path.join(app_data_path, 'settings.json')


def get_log_file_path() -> str:
    """
    Получает полный путь к файлу логов
    
    Returns:
        Путь к файлу логов
    """
    app_data_path = ensure_app_data_dir()
    return os.path.join(app_data_path, 'app.log')


def resource_exists(relative_path: str) -> bool:
    """
    Проверяет существование ресурса
    
    Args:
        relative_path: Относительный путь к ресурсу
        
    Returns:
        True если ресурс существует, False в противном случае
    """
    return os.path.exists(resource_path(relative_path))


def get_template_path(template_name: str) -> str:
    """
    Получает путь к шаблону
    
    Args:
        template_name: Имя файла шаблона
        
    Returns:
        Путь к файлу шаблона
    """
    return resource_path(f"resources/templates/{template_name}")


def get_icon_path(icon_name: str) -> str:
    """
    Получает путь к иконке
    
    Args:
        icon_name: Имя файла иконки
        
    Returns:
        Путь к файлу иконки
    """
    return resource_path(f"resources/icons/{icon_name}")