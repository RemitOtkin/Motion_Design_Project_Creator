"""
Модуль управления настройками приложения
Обрабатывает загрузку, сохранение и валидацию настроек
"""

import json
import os
from typing import Dict, Any


class SettingsManager:
    """Класс для управления настройками приложения"""
    
    DEFAULT_SETTINGS = {
        'default_path': os.path.expanduser('~/Work'),  # Исправлен путь
        'language': 'ru',
        'window_geometry': None,
        'last_project_path': None
    }
    
    def __init__(self, settings_file: str = "project_creator_settings.json"):
        """
        Инициализация менеджера настроек
        
        Args:
            settings_file: Путь к файлу настроек
        """
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Загружает настройки из файла
        
        Returns:
            Словарь с настройками
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                    # Объединяем с дефолтными настройками
                    settings = self.DEFAULT_SETTINGS.copy()
                    settings.update(loaded_settings)
                    
                    # Конвертируем base64 строку обратно в QByteArray если нужно
                    if 'window_geometry' in settings and settings['window_geometry'] is not None:
                        try:
                            if isinstance(settings['window_geometry'], str):
                                import base64
                                from PyQt5.QtCore import QByteArray
                                geometry_bytes = base64.b64decode(settings['window_geometry'].encode('utf-8'))
                                settings['window_geometry'] = QByteArray(geometry_bytes)
                        except Exception as e:
                            print(f"Предупреждение: Не удалось загрузить геометрию окна: {e}")
                            settings['window_geometry'] = None
                    
                    return settings
            else:
                return self.DEFAULT_SETTINGS.copy()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки настроек: {e}")
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> bool:
        """
        Сохраняет настройки в файл
        
        Returns:
            True если сохранение успешно, False в противном случае
        """
        try:
            # Создаем копию настроек для сохранения
            settings_to_save = self.settings.copy()
            
            # Конвертируем QByteArray в base64 строку если присутствует
            if 'window_geometry' in settings_to_save and settings_to_save['window_geometry'] is not None:
                try:
                    # Если это QByteArray, конвертируем в base64
                    geometry = settings_to_save['window_geometry']
                    if hasattr(geometry, 'toBase64'):
                        settings_to_save['window_geometry'] = geometry.toBase64().data().decode('utf-8')
                    elif isinstance(geometry, bytes):
                        import base64
                        settings_to_save['window_geometry'] = base64.b64encode(geometry).decode('utf-8')
                except Exception as e:
                    print(f"Предупреждение: Не удалось сохранить геометрию окна: {e}")
                    settings_to_save['window_geometry'] = None
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def get(self, key: str, default=None):
        """
        Получает значение настройки
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки или default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Устанавливает значение настройки
        
        Args:
            key: Ключ настройки
            value: Значение настройки
        """
        self.settings[key] = value
    
    def update(self, new_settings: Dict[str, Any]) -> None:
        """
        Обновляет несколько настроек одновременно
        
        Args:
            new_settings: Словарь с новыми настройками
        """
        self.settings.update(new_settings)
    
    def reset_to_defaults(self) -> None:
        """Сбрасывает настройки к значениям по умолчанию"""
        self.settings = self.DEFAULT_SETTINGS.copy()
    
    def validate_path(self, path: str) -> bool:
        """
        Проверяет, существует ли указанный путь
        
        Args:
            path: Путь для проверки
            
        Returns:
            True если путь существует, False в противном случае
        """
        return os.path.exists(path) and os.path.isdir(path)
    
    def get_default_path(self) -> str:
        """
        Возвращает валидный путь для проектов
        
        Returns:
            Путь к папке для проектов
        """
        default_path = self.get('default_path')
        if self.validate_path(default_path):
            return default_path
        
        # Если сохраненный путь не существует, используем домашнюю папку
        home_work = os.path.expanduser('~/Work')
        if self.validate_path(home_work):
            return home_work
        
        # В крайнем случае используем домашнюю папку
        return os.path.expanduser('~')