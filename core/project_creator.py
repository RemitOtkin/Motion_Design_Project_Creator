"""
Основная логика создания проектов
Содержит классы для создания структуры папок и файлов проекта
"""

import os
import time
import shutil
import glob
from typing import List, Dict, Any
from PyQt5.QtCore import QThread, pyqtSignal

from config.translations import Translations
from utils.resource_manager import resource_path
from core.folder_structure_manager import FolderStructureManager


class ProjectCreatorWorker(QThread):
    """Рабочий поток для создания проекта в фоновом режиме"""
    
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, project_data: Dict[str, Any], base_path: str, lang: str = 'ru'):
        """
        Инициализация рабочего потока
        
        Args:
            project_data: Данные проекта (имя, инструменты)
            base_path: Базовый путь для создания проекта
            lang: Язык интерфейса
        """
        super().__init__()
        self.project_data = project_data
        self.base_path = base_path
        self.lang = lang
        self.t = Translations.get(lang)
        
        # Путь к папке с шаблонами
        self.templates_dir = resource_path("resources/templates")
        
        # Инициализируем менеджер структуры папок
        try:
            self.folder_structure_manager = FolderStructureManager()
        except Exception as e:
            print(f"⚠️ Ошибка инициализации FolderStructureManager: {e}")
            self.folder_structure_manager = None
        
        # Fallback структура папок
        self.base_folders = [
            "01_IN/FOOTAGES",
            "01_IN/SFX", 
            "01_IN/FONTS",
            "01_IN/ASSETS",
            "02_PROCESS",
            "03_RENDER",
            "04_OUT/01_PREVIEW",
            "04_OUT/02_STILLSHOTS", 
            "04_OUT/03_ANIMATIC",
            "04_OUT/04_MASTER"
        ]
    
    def run(self) -> None:
        """Основной метод выполнения создания проекта"""
        try:
            project_name = self.project_data['name']
            project_path = os.path.join(self.base_path, project_name)
            
            # Проверяем, существует ли уже проект
            if os.path.exists(project_path):
                self.error_occurred.emit(self.t['project_exists'].format(project_name))
                return
            
            # Проверяем наличие шаблонов для выбранных инструментов
            missing_templates = self._check_templates()
            if missing_templates:
                error_msg = f"Не найдены шаблоны для: {', '.join(missing_templates)}"
                self.error_occurred.emit(error_msg)
                return
            
            # Создаем структуру проекта
            result = self._create_project_structure(project_path, project_name)
            self.finished.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _create_project_structure(self, project_path: str, project_name: str) -> Dict[str, Any]:
        """
        Создает структуру проекта
        
        Args:
            project_path: Путь к проекту
            project_name: Имя проекта
            
        Returns:
            Словарь с информацией о созданном проекте
        """
        # Получаем список всех папок для создания
        folders = self._get_folder_list()
        
        # Подсчитываем общее количество шагов
        total_steps = len(folders) + len(self.project_data['tools']) + 2
        current_step = 0
        
        # Создаем основную папку проекта
        os.makedirs(project_path, exist_ok=True)
        current_step += 1
        self.progress_updated.emit(int((current_step / total_steps) * 100))
        time.sleep(0.1)
        
        # Создаем структуру папок
        for folder in folders:
            folder_path = os.path.join(project_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            current_step += 1
            self.progress_updated.emit(int((current_step / total_steps) * 100))
            time.sleep(0.05)
        
        # Создаем файлы проектов для выбранных инструментов
        files_created = 0
        for tool in self.project_data['tools']:
            if self._create_tool_project_file(project_path, project_name, tool):
                files_created += 1
            
            current_step += 1
            self.progress_updated.emit(int((current_step / total_steps) * 100))
            time.sleep(0.1)
        
        # Создаем README файл
        self._create_readme(project_path, project_name)
        files_created += 1
        current_step += 1
        self.progress_updated.emit(100)
        
        return {
            'path': project_path,
            'name': project_name,
            'tools': self.project_data['tools'],
            'folders_created': len(folders),
            'files_created': files_created
        }
    
    def _check_templates(self) -> List[str]:
        """
        Проверяет наличие шаблонов для выбранных инструментов
        
        Returns:
            Список инструментов, для которых не найдены шаблоны
        """
        missing_templates = []
        
        for tool in self.project_data['tools']:
            if tool == 'ae':
                # Ищем любой .aep файл в папке templates
                aep_files = glob.glob(os.path.join(self.templates_dir, "*.aep"))
                if not aep_files:
                    missing_templates.append("After Effects (.aep)")
            elif tool == 'c4d':
                # Ищем любой .c4d файл в папке templates
                c4d_files = glob.glob(os.path.join(self.templates_dir, "*.c4d"))
                if not c4d_files:
                    missing_templates.append("Cinema 4D (.c4d)")
        
        return missing_templates
    def _get_folder_list(self) -> List[str]:
        """
        Получает список папок для создания с учетом выбранных инструментов
        
        Returns:
            Список путей папок
        """
        if self.folder_structure_manager:
            try:
                # Используем новый менеджер структуры
                return self.folder_structure_manager.get_folder_list(self.project_data['tools'])
            except Exception as e:
                print(f"⚠️ Ошибка в менеджере структуры, используем fallback: {e}")
        
        # Fallback на старую логику
        folders = self.base_folders.copy()
        
        # Добавляем папки для инструментов
        tool_folders = {
            'ae': '02_PROCESS/AE',
            'c4d': '02_PROCESS/C4D',
            'pr': '02_PROCESS/PR',
            'houdini': '02_PROCESS/HOUDINI',
            'blender': '02_PROCESS/BLENDER'
        }
        
        for tool in self.project_data['tools']:
            if tool in tool_folders:
                folders.append(tool_folders[tool])
        
        return folders
    
    def _create_tool_project_file(self, project_path: str, project_name: str, tool: str) -> bool:
        """
        Копирует шаблон проекта для конкретного инструмента
        
        Args:
            project_path: Путь к проекту
            project_name: Имя проекта
            tool: Инструмент ('ae' или 'c4d')
            
        Returns:
            True если файл скопирован успешно
        """
        try:
            if tool == 'ae':
                # Ищем .aep файл в папке templates
                template_files = glob.glob(os.path.join(self.templates_dir, "*.aep"))
                destination_dir = os.path.join(project_path, "02_PROCESS/AE")
                new_filename = f"{project_name}.aep"
                
            elif tool == 'c4d':
                # Ищем .c4d файл в папке templates
                template_files = glob.glob(os.path.join(self.templates_dir, "*.c4d"))
                destination_dir = os.path.join(project_path, "02_PROCESS/C4D")
                new_filename = f"{project_name}.c4d"
            else:
                print(f"Неизвестный инструмент: {tool}")
                return False
            
            if not template_files:
                print(f"Шаблон для {tool} не найден")
                return False
            
            # Используем первый найденный шаблон
            template_file = template_files[0]
            destination_file = os.path.join(destination_dir, new_filename)
            
            # Копируем файл
            shutil.copy2(template_file, destination_file)
            print(f"Шаблон {tool} скопирован: {template_file} -> {destination_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка копирования шаблона для {tool}: {e}")
            return False
    
    def _create_readme(self, project_path: str, project_name: str) -> None:
        """
        Создает README файл с описанием проекта
        
        Args:
            project_path: Путь к проекту
            project_name: Имя проекта
        """
        readme_content = self._generate_readme_content(project_name)
        readme_path = os.path.join(project_path, "README.md")
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
        except Exception as e:
            print(f"Предупреждение: Не удалось создать README файл: {e}")
    
    def _generate_readme_content(self, project_name: str) -> str:
        """
        Генерирует содержимое README файла
        
        Args:
            project_name: Имя проекта
            
        Returns:
            Содержимое README файла
        """
        if self.lang == 'ru':
            return f"""# {project_name}

## Структура проекта

### 01_IN - Входящие материалы
- **FOOTAGES/** - Исходные видеофайлы
- **SFX/** - Звуковые эффекты и музыка  
- **FONTS/** - Шрифты для проекта
- **ASSETS/** - Графические материалы, текстуры, изображения

### 02_PROCESS - Рабочие файлы
- **AE/** - Проекты After Effects (.aep)
- **C4D/** - Проекты Cinema 4D (.c4d)

### 03_RENDER - Промежуточный рендер
- Временные файлы рендера
- Тестовые версии

### 04_OUT - Итоговые материалы
- **01_PREVIEW/** - Превью для заказчика
- **02_STILLSHOTS/** - Стоп-кадры
- **03_ANIMATIC/** - Аниматик проекта
- **04_MASTER/** - Финальные файлы для публикации

## Информация о проекте

- **Создан:** {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Инструменты:** {', '.join(self.project_data['tools'])}

---
Создано с помощью Project Creator
"""
        else:
            return f"""# {project_name}

## Project Structure

### 01_IN - Input Materials
- **FOOTAGES/** - Source video files
- **SFX/** - Sound effects and music  
- **FONTS/** - Project fonts
- **ASSETS/** - Graphic materials, textures, images

### 02_PROCESS - Work Files
- **AE/** - After Effects projects (.aep)
- **C4D/** - Cinema 4D projects (.c4d)

### 03_RENDER - Intermediate Render
- Temporary render files
- Test versions

### 04_OUT - Final Materials
- **01_PREVIEW/** - Client preview
- **02_STILLSHOTS/** - Still frames
- **03_ANIMATIC/** - Project animatic
- **04_MASTER/** - Final files for publication

## Project Information

- **Created:** {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Tools:** {', '.join(self.project_data['tools'])}

---
Created with Project Creator
"""