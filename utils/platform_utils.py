"""
Модуль утилит для работы с различными платформами
Содержит функции для выполнения системно-зависимых операций
"""

import sys
import os
import subprocess
from typing import Optional


def open_folder(path: str) -> bool:
    """
    Открывает папку в файловом менеджере операционной системы
    
    Args:
        path: Путь к папке для открытия
        
    Returns:
        True если операция выполнена успешно, False в противном случае
    """
    if not os.path.exists(path):
        return False
    
    try:
        if sys.platform == 'win32':
            # Windows: используем explorer
            os.startfile(path)
        elif sys.platform == 'darwin':
            # macOS: используем open
            subprocess.run(['open', path], check=True)
        else:
            # Linux: используем xdg-open
            subprocess.run(['xdg-open', path], check=True)
        return True
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Ошибка при открытии папки {path}: {e}")
        return False


def get_default_projects_path() -> str:
    """
    Получает путь по умолчанию для папки проектов
    
    Returns:
        Путь к папке проектов по умолчанию
    """
    if sys.platform == 'win32':
        # Windows: используем Documents/Work
        documents = os.path.join(os.path.expanduser('~'), 'Documents')
        return os.path.join(documents, 'Work')
    elif sys.platform == 'darwin':
        # macOS: используем ~/Work
        return os.path.expanduser('~/Work')
    else:
        # Linux: используем ~/Work
        return os.path.expanduser('~/Work')


def get_system_info() -> dict:
    """
    Получает информацию о системе
    
    Returns:
        Словарь с информацией о системе
    """
    return {
        'platform': sys.platform,
        'python_version': sys.version,
        'executable': sys.executable,
        'is_frozen': getattr(sys, 'frozen', False)
    }


def is_admin_user() -> bool:
    """
    Проверяет, запущено ли приложение с правами администратора
    
    Returns:
        True если пользователь имеет права администратора
    """
    try:
        if sys.platform == 'win32':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def create_desktop_shortcut(app_path: str, shortcut_name: str) -> bool:
    """
    Создает ярлык на рабочем столе (только для Windows)
    
    Args:
        app_path: Путь к исполняемому файлу
        shortcut_name: Имя ярлыка
        
    Returns:
        True если ярлык создан успешно
    """
    if sys.platform != 'win32':
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{shortcut_name}.lnk")
        target = app_path
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(app_path)
        shortcut.save()
        
        return True
    except ImportError:
        print("Для создания ярлыков требуется установить pywin32 и winshell")
        return False
    except Exception as e:
        print(f"Ошибка при создании ярлыка: {e}")
        return False


def get_free_disk_space(path: str) -> Optional[int]:
    """
    Получает количество свободного места на диске
    
    Args:
        path: Путь для проверки
        
    Returns:
        Количество свободных байт или None при ошибке
    """
    try:
        if sys.platform == 'win32':
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                ctypes.pointer(free_bytes),
                None,
                None
            )
            return free_bytes.value
        else:
            statvfs = os.statvfs(path)
            return statvfs.f_frsize * statvfs.f_available
    except Exception as e:
        print(f"Ошибка при получении информации о диске: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """
    Форматирует размер файла в человекочитаемый вид
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        Отформатированная строка с размером
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def is_valid_filename(filename: str) -> bool:
    """
    Проверяет корректность имени файла для текущей ОС
    
    Args:
        filename: Имя файла для проверки
        
    Returns:
        True если имя корректно
    """
    if not filename or filename.strip() != filename:
        return False
    
    # Запрещенные символы для Windows (более строгие)
    forbidden_chars = '<>:"/\\|?*'
    if any(char in filename for char in forbidden_chars):
        return False
    
    # Запрещенные имена для Windows
    forbidden_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    if filename.upper() in forbidden_names:
        return False
    
    # Проверяем длину
    if len(filename) > 255:
        return False
    
    return True