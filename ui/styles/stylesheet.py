"""
Модуль стилей для Project Creator
Содержит все CSS стили для оформления интерфейса с адаптивными возможностями
"""

import os
from utils.resource_manager import resource_path


class StyleSheet:
    """Класс для управления стилями приложения"""
    
    # Глобальный экземпляр адаптивных стилей
    _adaptive_styles = None
    
    @classmethod
    def get_adaptive_styles(cls):
        """
        Получает экземпляр адаптивных стилей (singleton)
        
        Returns:
            AdaptiveStyles: Экземпляр адаптивных стилей
        """
        if cls._adaptive_styles is None:
            try:
                from ui.styles.adaptive_styles import AdaptiveStyles
                cls._adaptive_styles = AdaptiveStyles()
            except ImportError as e:
                print(f"⚠️ Адаптивные стили недоступны: {e}")
                cls._adaptive_styles = None
        return cls._adaptive_styles
    
    @classmethod
    def get_main_stylesheet(cls) -> str:
        """
        Возвращает основную адаптивную таблицу стилей для приложения
        
        Returns:
            CSS строка со стилями
        """
        try:
            adaptive_styles = cls.get_adaptive_styles()
            if adaptive_styles:
                return adaptive_styles.get_stylesheet()
            else:
                # Fallback на статичные стили
                return cls._get_fallback_stylesheet()
        except Exception as e:
            print(f"⚠️ Ошибка загрузки адаптивных стилей: {e}")
            return cls._get_fallback_stylesheet()
    
    @classmethod
    def get_dialog_stylesheet(cls) -> str:
        """
        Возвращает адаптивные стили для диалоговых окон
        
        Returns:
            CSS строка со стилями для диалогов
        """
        try:
            adaptive_styles = cls.get_adaptive_styles()
            if adaptive_styles:
                return adaptive_styles.get_dialog_stylesheet()
            else:
                return cls._get_fallback_dialog_stylesheet()
        except Exception as e:
            print(f"⚠️ Ошибка загрузки адаптивных стилей диалогов: {e}")
            return cls._get_fallback_dialog_stylesheet()
    
    @classmethod
    def get_window_size(cls) -> tuple:
        """
        Возвращает рекомендуемый размер окна для текущего экрана
        
        Returns:
            tuple: (width, height)
        """
        try:
            adaptive_styles = cls.get_adaptive_styles()
            if adaptive_styles:
                return adaptive_styles.get_window_size()
            else:
                return (1280, 960)  # Fallback размер
        except Exception as e:
            print(f"⚠️ Ошибка определения размера окна: {e}")
            return (1280, 960)  # Fallback размер
    
    @staticmethod
    def _get_fallback_stylesheet() -> str:
        """
        Возвращает fallback стили в случае проблем с адаптивной системой
        
        Returns:
            CSS строка со статичными стилями
        """
        return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #1d3557, stop:0.5 #457b9d, stop:1 #a8dadc);
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
        }
                
        #title {
            font-family: "Arial", "Segoe UI", sans-serif;
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin: 5px;
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.25);
            border: 0.5px solid #e0e0e0;
            border-radius: 10px;
            max-width: 600px;
        }
        
        #subtitle {
            font-family: "Arial", "Segoe UI", sans-serif;
            font-size: 14px;
            color: white;
            margin: 5px;
            padding: 10px 16px;
            background: rgba(255, 255, 255, 0.25);
            border: 0.5px solid #e0e0e0;
            border-radius: 8px;
            max-width: 500px;
        }
        
        QGroupBox {
            font-family: "Arial", "Segoe UI", sans-serif;
            font-weight: bold;
            font-size: 14px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            margin-top: 25px;
            padding-top: 5px;
            background: rgba(255, 255, 255, 0.25);
            color: #333;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 15px;
            top: 0px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            color: #333;
            font-family: "Arial", "Segoe UI", sans-serif;
            font-weight: bold;
            font-size: 13px;
        }
        
        #form_label {
            color: #333;
            font-family: "Arial", "Segoe UI", sans-serif;
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 5px;
        }
        
        QLineEdit {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-family: "Arial", "Segoe UI", sans-serif;
            font-size: 14px;
            background: white;
            color: #333;
        }
        
        QLineEdit:focus {
            border-color: #4facfe;
            background: #f8f9fa;
        }
        
        #tool_checkbox {
            font-family: "Arial", "Segoe UI", sans-serif;
            font-size: 14px;
            font-weight: normal;
            spacing: 10px;
            color: #333;
            background: transparent;
        }
        
        #tool_checkbox::indicator {
            width: 20px;
            height: 20px;
        }
        
        #tool_checkbox::indicator:unchecked {
            border: 2px solid #ccc;
            border-radius: 4px;
            background: white;
        }
        
        #tool_checkbox::indicator:checked {
            border: 2px solid #4facfe;
            border-radius: 4px;
            background: #4facfe;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        
        QTextEdit {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: #f8f9fa;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 12px;
            color: #333;
        }
        
        QPushButton {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-family: "Arial", "Segoe UI", sans-serif;
            font-size: 14px;
            font-weight: bold;
            min-width: 120px;
        }
        
        QPushButton:hover {
            padding: 14px 26px;
        }

        QPushButton:pressed {
            padding: 10px 22px;
        }
        
        #create_button {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4facfe, stop:1 #00f2fe);
            color: white;
        }
        
        #create_button:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3d8bfe, stop:1 #00d2fe);
        }
        
        #create_button:disabled {
            background: #cccccc;
            color: #666666;
        }
        
        #secondary_button {
            background: #6c757d;
            color: white;
        }
        
        #secondary_button:hover {
            background: #5a6268;
        }
        
        #browse_button {
            background: #e63946;
            color: white;
            min-width: 100px;
        }
        
        #browse_button:hover {
            background: #c1121f;
        }
        
        QProgressBar {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            background: white;
            color: #333;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4facfe, stop:1 #00f2fe);
            border-radius: 6px;
        }
        
        QStatusBar {
            background: rgba(255, 255, 255, 0.95);
            border-top: 1px solid #e0e0e0;
            color: #333;
            font-family: "Arial", "Segoe UI", sans-serif;
            font-weight: bold;
        }
        
        QComboBox {
            padding: 8px 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            background: white;
            color: #333;
            font-family: "Arial", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        QComboBox:focus {
            border-color: #4facfe;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        """
    
    @staticmethod
    def _get_fallback_dialog_stylesheet() -> str:
        """
        Возвращает fallback стили для диалогов
        
        Returns:
            CSS строка со стилями
        """
        return """
            QDialog {
                background: white;
            }
            QLabel {
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background: white;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton[objectName="save_btn"] {
                background: #28a745;
                color: white;
            }
            QPushButton[objectName="save_btn"]:hover {
                background: #218838;
            }
            QPushButton[objectName="cancel_btn"] {
                background: #6c757d;
                color: white;
            }
            QPushButton[objectName="cancel_btn"]:hover {
                background: #5a6268;
            }
            QPushButton[objectName="browse_btn"] {
                background: #007bff;
                color: white;
            }
            QPushButton[objectName="browse_btn"]:hover {
                background: #0056b3;
            }
        """