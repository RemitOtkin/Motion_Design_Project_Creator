"""
Менеджер структуры папок проекта
Управляет созданием папок на основе пользовательских настроек
"""

import os
import json
from typing import Dict, List, Any
from utils.resource_manager import get_settings_file_path


class FolderStructureManager:
    """Класс для управления структурой папок проекта"""
    
    def __init__(self):
        """Инициализация менеджера структуры папок"""
        self.current_structure = self._load_current_structure()
        self.tool_folders = {
            'ae': 'AE',
            'c4d': 'C4D',
            'pr': 'PR',
            'houdini': 'HOUDINI',
            'blender': 'BLENDER'
        }
    
    def _load_current_structure(self) -> Dict[str, Any]:
        """Загружает текущую структуру папок"""
        try:
            structure_file = os.path.join(os.path.dirname(get_settings_file_path()), 'current_structure.json')
            if os.path.exists(structure_file):
                with open(structure_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки структуры: {e}")
        
        # Возвращаем стандартную структуру
        return self._get_default_structure()
    
    def _save_current_structure(self) -> None:
        """Сохраняет текущую структуру папок"""
        try:
            structure_file = os.path.join(os.path.dirname(get_settings_file_path()), 'current_structure.json')
            os.makedirs(os.path.dirname(structure_file), exist_ok=True)
            
            with open(structure_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_structure, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения структуры: {e}")
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """Возвращает стандартную структуру папок"""
        return {
            "01_IN": {
                "comment": "Входящие материалы",
                "children": {
                    "FOOTAGES": {"comment": "Исходные видеофайлы", "children": {}},
                    "SFX": {"comment": "Звуковые эффекты и музыка", "children": {}},
                    "FONTS": {"comment": "Шрифты для проекта", "children": {}},
                    "ASSETS": {"comment": "Графические материалы, текстуры", "children": {}}
                }
            },
            "02_PROCESS": {
                "comment": "Рабочие файлы",
                "children": {}
            },
            "03_RENDER": {
                "comment": "Промежуточный рендер",
                "children": {}
            },
            "04_OUT": {
                "comment": "Итоговые материалы",
                "children": {
                    "01_PREVIEW": {"comment": "Превью для заказчика", "children": {}},
                    "02_STILLSHOTS": {"comment": "Стоп-кадры", "children": {}},
                    "03_ANIMATIC": {"comment": "Аниматик проекта", "children": {}},
                    "04_MASTER": {"comment": "Финальные файлы для публикации", "children": {}}
                }
            }
        }
    
    def update_structure(self, new_structure: Dict[str, Any]) -> None:
        """
        Обновляет текущую структуру папок
        
        Args:
            new_structure: Новая структура папок
        """
        self.current_structure = new_structure
        self._save_current_structure()
    
    def get_folder_list(self, selected_tools: List[str]) -> List[str]:
        """
        Получает список папок для создания с учетом выбранных инструментов
        
        Args:
            selected_tools: Список выбранных инструментов
            
        Returns:
            Список путей папок для создания
        """
        # Создаем копию структуры для модификации
        structure = self.current_structure.copy()
        
        # Добавляем папки для инструментов в 02_PROCESS
        if "02_PROCESS" in structure:
            process_children = structure["02_PROCESS"].get("children", {})
            
            for tool in selected_tools:
                if tool in self.tool_folders:
                    folder_name = self.tool_folders[tool]
                    process_children[folder_name] = {
                        "comment": f"Проекты {tool.upper()}",
                        "children": {}
                    }
            
            structure["02_PROCESS"]["children"] = process_children
        
        # Преобразуем структуру в список путей
        return self._structure_to_paths(structure)
    
    def _structure_to_paths(self, structure: Dict[str, Any], prefix: str = "") -> List[str]:
        """
        Преобразует структуру в список путей для создания
        
        Args:
            structure: Структура папок
            prefix: Префикс пути
            
        Returns:
            Список путей папок
        """
        paths = []
        
        for folder_name, folder_data in structure.items():
            current_path = os.path.join(prefix, folder_name) if prefix else folder_name
            paths.append(current_path)
            
            # Рекурсивно добавляем подпапки
            if "children" in folder_data and folder_data["children"]:
                child_paths = self._structure_to_paths(folder_data["children"], current_path)
                paths.extend(child_paths)
        
        return paths
    
    def get_structure_preview(self, selected_tools: List[str] = None) -> str:
        """
        Генерирует текстовое представление структуры
        
        Args:
            selected_tools: Список выбранных инструментов для включения их папок
            
        Returns:
            Текстовое представление структуры
        """
        if selected_tools is None:
            selected_tools = []
        
        # Получаем структуру с инструментами
        structure = self.current_structure.copy()
        
        # Добавляем папки инструментов
        if "02_PROCESS" in structure and selected_tools:
            process_children = structure["02_PROCESS"].get("children", {})
            
            for tool in selected_tools:
                if tool in self.tool_folders:
                    folder_name = self.tool_folders[tool]
                    process_children[folder_name] = {
                        "comment": f"Проекты {tool.upper()}",
                        "children": {}
                    }
            
            structure["02_PROCESS"]["children"] = process_children
        
        return self._generate_tree_view(structure)
    
    def _generate_tree_view(self, structure: Dict[str, Any], prefix: str = "📁 [Проект]/\n", level: int = 0) -> str:
        """
        Генерирует древовидное представление структуры
        
        Args:
            structure: Структура папок
            prefix: Начальный префикс
            level: Уровень вложенности
            
        Returns:
            Строковое представление дерева
        """
        if level == 0:
            result = prefix
        else:
            result = ""
        
        items = list(structure.items())
        
        for i, (folder_name, folder_data) in enumerate(items):
            is_last = i == len(items) - 1
            
            # Создаем отступ
            if level > 0:
                indent = "│   " * (level - 1)
                if level == 1:
                    indent = ""
                connector = "└── " if is_last else "├── "
                line_prefix = f"{indent}{connector}"
            else:
                line_prefix = "├── " if not is_last else "└── "
            
            # Добавляем комментарий если есть
            comment = folder_data.get("comment", "")
            comment_text = f"  # {comment}" if comment else ""
            
            result += f"{line_prefix}📁 {folder_name}/{comment_text}\n"
            
            # Рекурсивно добавляем подпапки
            if "children" in folder_data and folder_data["children"]:
                child_result = self._generate_tree_view(folder_data["children"], "", level + 1)
                
                # Корректируем отступы для дочерних элементов
                if level > 0:
                    base_indent = "│   " * level if not is_last else "    " * level
                else:
                    base_indent = "│   " if not is_last else "    "
                
                # Добавляем базовый отступ к каждой строке дочерних элементов
                child_lines = child_result.split('\n')
                for line in child_lines:
                    if line.strip():
                        result += f"{base_indent}{line}\n"
        
        return result
    
    def get_current_structure(self) -> Dict[str, Any]:
        """
        Возвращает текущую структуру папок
        
        Returns:
            Словарь с текущей структурой
        """
        return self.current_structure.copy()
    
    def reset_to_default(self) -> None:
        """Сбрасывает структуру к стандартной"""
        self.current_structure = self._get_default_structure()
        self._save_current_structure()
    
    def get_tool_folder_mapping(self) -> Dict[str, str]:
        """
        Возвращает соответствие инструментов и папок
        
        Returns:
            Словарь соответствия tool_code -> folder_name
        """
        return self.tool_folders.copy()
    
    def add_tool_folder_mapping(self, tool_code: str, folder_name: str) -> None:
        """
        Добавляет новое соответствие инструмента и папки
        
        Args:
            tool_code: Код инструмента
            folder_name: Название папки
        """
        self.tool_folders[tool_code] = folder_name
    
    def validate_structure(self, structure: Dict[str, Any]) -> List[str]:
        """
        Валидирует структуру папок
        
        Args:
            structure: Структура для валидации
            
        Returns:
            Список ошибок валидации (пустой если ошибок нет)
        """
        errors = []
        
        def validate_folder(folder_dict, path=""):
            for folder_name, folder_data in folder_dict.items():
                current_path = f"{path}/{folder_name}" if path else folder_name
                
                # Проверяем имя папки
                if not folder_name or not folder_name.strip():
                    errors.append(f"Пустое имя папки в пути: {path}")
                    continue
                
                # Проверяем недопустимые символы
                invalid_chars = '<>:"/\\|?*'
                if any(char in folder_name for char in invalid_chars):
                    errors.append(f"Недопустимые символы в имени папки: {current_path}")
                
                # Проверяем длину имени
                if len(folder_name) > 255:
                    errors.append(f"Слишком длинное имя папки: {current_path}")
                
                # Проверяем структуру данных
                if not isinstance(folder_data, dict):
                    errors.append(f"Неверная структура данных для папки: {current_path}")
                    continue
                
                # Рекурсивно проверяем подпапки
                if "children" in folder_data and folder_data["children"]:
                    validate_folder(folder_data["children"], current_path)
        
        try:
            validate_folder(structure)
        except Exception as e:
            errors.append(f"Ошибка валидации: {str(e)}")
        
        return errors