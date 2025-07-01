"""
Адаптивная система стилей для Project Creator
Автоматически подстраивается под разрешение экрана
"""

import sys
from typing import Dict, Tuple
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QRect


class ScreenInfo:
    """Класс для определения информации об экране"""
    
    def __init__(self):
        """Инициализация с автоматическим определением параметров экрана"""
        self.app = QApplication.instance()
        if not self.app:
            # Создаем временное приложение для получения информации об экране
            self.app = QApplication(sys.argv)
        
        self.desktop = QDesktopWidget()
        self.screen_geometry = self.desktop.screenGeometry()
        
        # Основные параметры экрана
        self.width = self.screen_geometry.width()
        self.height = self.screen_geometry.height()
        self.diagonal_pixels = (self.width ** 2 + self.height ** 2) ** 0.5
        
        # Определяем категорию разрешения
        self.resolution_category = self._get_resolution_category()
        
        # Определяем масштабирующий коэффициент
        self.scale_factor = self._calculate_scale_factor()
        
        # DPI информация
        self.dpi = self._get_dpi()
    
    def _get_resolution_category(self) -> str:
        """
        Определяет категорию разрешения экрана
        
        Returns:
            str: Категория разрешения (HD, FHD, QHD, 4K, 8K)
        """
        if self.width >= 7680:  # 8K
            return "8K"
        elif self.width >= 3840:  # 4K
            return "4K"
        elif self.width >= 2560:  # QHD/1440p
            return "QHD"
        elif self.width >= 1920:  # Full HD
            return "FHD"
        elif self.width >= 1366:  # HD
            return "HD"
        else:  # Меньше HD
            return "LOW"
    
    def _calculate_scale_factor(self) -> float:
        """
        Вычисляет масштабирующий коэффициент
        
        Returns:
            float: Коэффициент масштабирования
        """
        # Базовое разрешение FHD (1920x1080)
        base_width = 1920
        base_height = 1080
        
        # Вычисляем коэффициент на основе диагонали
        base_diagonal = (base_width ** 2 + base_height ** 2) ** 0.5
        scale = self.diagonal_pixels / base_diagonal
        
        # Ограничиваем масштаб разумными пределами
        scale = max(0.7, min(scale, 4.0))
        
        # Округляем до удобных значений
        if scale < 0.8:
            return 0.75
        elif scale < 1.2:
            return 1.0
        elif scale < 1.6:
            return 1.25
        elif scale < 2.2:
            return 1.5
        elif scale < 2.8:
            return 2.0
        elif scale < 3.5:
            return 2.5
        else:
            return 3.0
    
    def _get_dpi(self) -> int:
        """
        Получает DPI экрана
        
        Returns:
            int: DPI экрана
        """
        try:
            screen = self.app.primaryScreen()
            return int(screen.logicalDotsPerInch())
        except:
            # Fallback для старых версий PyQt5
            return 96  # Стандартный DPI для Windows
    
    def get_info(self) -> Dict:
        """
        Возвращает полную информацию об экране
        
        Returns:
            Dict: Словарь с информацией об экране
        """
        return {
            'width': self.width,
            'height': self.height,
            'resolution': f"{self.width}x{self.height}",
            'category': self.resolution_category,
            'scale_factor': self.scale_factor,
            'dpi': self.dpi,
            'diagonal_pixels': int(self.diagonal_pixels)
        }


class AdaptiveStyles:
    """Класс для создания адаптивных стилей"""
    
    def __init__(self):
        """Инициализация адаптивных стилей"""
        self.screen_info = ScreenInfo()
        self.scale = self.screen_info.scale_factor
        
        # Базовые размеры (для FHD)
        self.base_sizes = {
            'window_width': 1280,
            'window_height': 960,
            'font_size_title': 32,
            'font_size_subtitle': 14,
            'font_size_form_label': 13,
            'font_size_text': 14,
            'font_size_button': 18,
            'font_size_monospace': 14,
            'padding_large': 30,
            'padding_medium': 20,
            'padding_small': 15,
            'padding_tiny': 12,
            'margin_large': 20,
            'margin_medium': 15,
            'margin_small': 10,
            'margin_tiny': 5,
            'border_radius': 8,
            'border_width': 2,
            'button_height': 44,
            'input_height': 44,
            'icon_size': 24,
            'checkbox_size': 20
        }
        
        # Применяем масштабирование
        self.sizes = self._scale_sizes()
        
        # Выбираем подходящие шрифты
        self.fonts = self._get_adaptive_fonts()
    
    def _scale_sizes(self) -> Dict[str, int]:
        """
        Масштабирует размеры согласно scale_factor
        
        Returns:
            Dict[str, int]: Масштабированные размеры
        """
        scaled_sizes = {}
        for key, value in self.base_sizes.items():
            scaled_value = int(value * self.scale)
            
            # Минимальные значения для читаемости
            if 'font_size' in key:
                scaled_value = max(scaled_value, 10)
            elif 'padding' in key or 'margin' in key:
                scaled_value = max(scaled_value, 5)
            elif key in ['button_height', 'input_height']:
                scaled_value = max(scaled_value, 32)
            
            scaled_sizes[key] = scaled_value
        
        return scaled_sizes
    
    def _get_adaptive_fonts(self) -> Dict[str, str]:
        """
        Выбирает подходящие шрифты для текущего масштаба
        
        Returns:
            Dict[str, str]: Семейства шрифтов
        """
        # Для высоких DPI используем более четкие шрифты
        if self.screen_info.dpi > 120:
            return {
                'primary': '"Roboto","Segoe UI", "Arial", sans-serif',
                'monospace': '"Fira Code", "Consolas", "Courier New", monospace',
                'title': '"Roboto", "Segoe UI Semibold", "Arial Black", sans-serif'
            }
        else:
            return {
                'primary': '"Arial", "Segoe UI", sans-serif',
                'monospace': '"Consolas", "Courier New", monospace',
                'title': '"Arial Black", "Arial", sans-serif'
            }
    
    def get_window_size(self) -> Tuple[int, int]:
        """
        Возвращает рекомендуемый размер окна
        
        Returns:
            Tuple[int, int]: (ширина, высота)
        """
        # Ограничиваем размер окна разумными пределами относительно экрана
        max_width = int(self.screen_info.width * 0.8)
        max_height = int(self.screen_info.height * 0.8)
        
        window_width = min(self.sizes['window_width'], max_width)
        window_height = min(self.sizes['window_height'], max_height)
        
        return window_width, window_height
    
    def get_stylesheet(self) -> str:
        """
        Генерирует адаптивную таблицу стилей
        
        Returns:
            str: CSS стили для PyQt5
        """
        s = self.sizes  # Сокращение для удобства
        f = self.fonts
        
        return f"""
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1d3557, stop:0.5 #457b9d, stop:1 #a8dadc);
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
        }}
                
        #title {{
            font-family: {f['title']};
            font-size: {s['font_size_title']}px;
            font-weight: bold;
            color: white;
            margin: {s['margin_small']}px;
            padding: {s['padding_small']}px {s['padding_medium']}px;
            background: rgba(255, 255, 255, 0.25);
            border: 1px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            max-width: {int(s['window_width'] * 0.7)}px;
        }}
        
        #subtitle {{
            font-family: {f['primary']};
            font-size: {s['font_size_subtitle']}px;
            color: white;
            margin: {s['margin_small']}px;
            padding: {s['padding_small']}px {s['padding_medium']}px;
            background: rgba(255, 255, 255, 0.25);
            border: 1px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            max-width: {int(s['window_width'] * 0.5)}px;
        }}
        
        QGroupBox {{
            font-family: {f['primary']};
            font-weight: bold;
            font-size: {s['font_size_text']}px;
            border: {s['border_width']}px solid #e0e0e0;
            border-radius: {s['border_radius'] + 4}px;
            margin-top: {s['margin_medium'] + 10}px;
            padding-top: {s['padding_medium']}px;
            background: rgba(255, 255, 255, 0.25);
            color: #333;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: {s['margin_medium']}px;
            top: {s['padding_small'] }px;
            padding: {s['padding_tiny']}px {s['padding_small']}px;
            background: rgba(255, 255, 255, 0.95);
            border: {s['border_width']}px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            color: #333;
            font-family: {f['primary']};
            font-weight: bold;
            font-size: {s['font_size_form_label']}px;
        }}
        
        #form_label {{
            color: #333;
            font-family: {f['primary']};
            font-weight: bold;
            font-size: {s['font_size_form_label']}px;
            margin-bottom: {s['margin_tiny']}px;
        }}
        
        QLineEdit {{
            padding: {s['padding_small']}px;
            border: {s['border_width']}px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            font-family: {f['primary']};
            font-size: {s['font_size_text']}px;
            background: white;
            color: #333;
            min-height: {s['input_height'] - s['padding_small'] * 2}px;
        }}
        
        QLineEdit:focus {{
            border-color: #4facfe;
            background: #f8f9fa;
        }}
        
        #tool_checkbox {{
            font-family: {f['primary']};
            font-size: {s['font_size_text']}px;
            font-weight: normal;
            spacing: {s['margin_small']}px;
            color: #333;
            background: transparent;
        }}
        
        #tool_checkbox::indicator {{
            width: {s['checkbox_size']}px;
            height: {s['checkbox_size']}px;
        }}
        
        #tool_checkbox::indicator:unchecked {{
            border: {s['border_width']}px solid #ccc;
            border-radius: {s['border_radius'] // 2}px;
            background: white;
        }}
        
        #tool_checkbox::indicator:checked {{
            border: {s['border_width']}px solid #4facfe;
            border-radius: {s['border_radius'] // 2}px;
            background: #4facfe;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }}
        
        QTextEdit {{
            border: {s['border_width']}px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            background: #f8f9fa;
            font-family: {f['monospace']};
            font-size: {s['font_size_monospace']}px;
            color: #333;
            padding: {s['padding_small']}px;
        }}
        
        QPushButton {{
            padding: {s['padding_small']}px {s['padding_medium']}px;
            border: none;
            border-radius: {s['border_radius']}px;
            font-family: {f['primary']};
            font-size: {s['font_size_button']}px;
            font-weight: bold;
            min-width: {int(s['button_height'] * 2.5)}px;
            min-height: {s['button_height']}px;
        }}
        
        QPushButton:hover {{
            padding: {s['padding_small'] + 2}px {s['padding_medium'] + 2}px;
        }}

        QPushButton:pressed {{
            padding: {s['padding_small'] - 2}px {s['padding_medium'] - 2}px;
        }}
        
        #create_button {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4facfe, stop:1 #00f2fe);
            color: white;
        }}
        
        #create_button:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3d8bfe, stop:1 #00d2fe);
        }}
        
        #create_button:disabled {{
            background: #cccccc;
            color: #666666;
        }}
        
        #secondary_button {{
            background: #6c757d;
            color: white;
        }}
        
        #secondary_button:hover {{
            background: #5a6268;
        }}
        
        #browse_button {{
            background: #e63946;
            color: white;
            min-width: {int(s['button_height'] * 2)}px;
        }}
        
        #browse_button:hover {{
            background: #c1121f;
        }}
        
        QProgressBar {{
            border: {s['border_width']}px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            text-align: center;
            font-weight: bold;
            background: white;
            color: #333;
            height: {s['button_height'] // 2}px;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4facfe, stop:1 #00f2fe);
            border-radius: {s['border_radius'] - 2}px;
        }}
        
        QStatusBar {{
            background: rgba(255, 255, 255, 0.95);
            border-top: 1px solid #e0e0e0;
            color: #333;
            font-family: {f['primary']};
            font-weight: bold;
            font-size: {s['font_size_text']}px;
            padding: {s['padding_tiny']}px;
        }}
        
        QComboBox {{
            padding: {s['padding_small']}px {s['padding_medium']}px;
            border: {s['border_width']}px solid #e0e0e0;
            border-radius: {s['border_radius']}px;
            background: white;
            color: #333;
            font-family: {f['primary']};
            font-size: {s['font_size_text']}px;
            min-height: {s['input_height'] - s['padding_small'] * 2}px;
        }}
        
        QComboBox:focus {{
            border-color: #4facfe;
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: {s['padding_medium'] + s['margin_small']}px;
        }}
        """
    
    def get_dialog_stylesheet(self) -> str:
        """
        Возвращает стили для диалоговых окон
        
        Returns:
            str: CSS стили для диалогов
        """
        s = self.sizes
        f = self.fonts
        
        return f"""
            QDialog {{
                background: white;
                font-family: {f['primary']};
            }}
            QLabel {{
                font-weight: bold;
                color: #333;
                margin-bottom: {s['margin_tiny']}px;
                font-size: {s['font_size_text']}px;
            }}
            QLineEdit {{
                padding: {s['padding_small']}px;
                border: {s['border_width']}px solid #e0e0e0;
                border-radius: {s['border_radius']}px;
                background: white;
                font-size: {s['font_size_text']}px;
                min-height: {s['input_height'] - s['padding_small'] * 2}px;
            }}
            QComboBox {{
                padding: {s['padding_small']}px;
                border: {s['border_width']}px solid #e0e0e0;
                border-radius: {s['border_radius']}px;
                background: white;
                font-size: {s['font_size_text']}px;
                min-height: {s['input_height'] - s['padding_small'] * 2}px;
            }}
            QPushButton {{
                padding: {s['padding_small']}px {s['padding_medium']}px;
                border: none;
                border-radius: {s['border_radius']}px;
                font-weight: bold;
                min-width: {int(s['button_height'] * 1.8)}px;
                min-height: {s['button_height']}px;
                font-size: {int(s['font_size_button'] * 0.9)}px;
            }}
            QPushButton[objectName="save_btn"] {{
                background: #28a745;
                color: white;
            }}
            QPushButton[objectName="save_btn"]:hover {{
                background: #218838;
            }}
            QPushButton[objectName="cancel_btn"] {{
                background: #6c757d;
                color: white;
            }}
            QPushButton[objectName="cancel_btn"]:hover {{
                background: #5a6268;
            }}
            QPushButton[objectName="browse_btn"] {{
                background: #007bff;
                color: white;
            }}
            QPushButton[objectName="browse_btn"]:hover {{
                background: #0056b3;
            }}
        """
    
    def print_debug_info(self):
        """Выводит отладочную информацию об экране и масштабировании"""
        info = self.screen_info.get_info()
        print("📊 Информация об экране:")
        print(f"   Разрешение: {info['resolution']}")
        print(f"   Категория: {info['category']}")
        print(f"   DPI: {info['dpi']}")
        print(f"   Масштаб: {info['scale_factor']}")
        print(f"   Размер окна: {self.get_window_size()}")
        print(f"   Размер шрифта заголовка: {self.sizes['font_size_title']}px")
        print(f"   Размер кнопок: {self.sizes['button_height']}px")