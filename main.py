#!/usr/bin/env python3
"""
Project Creator - Точка входа в приложение
Создает структуру медиа-проектов для After Effects и Cinema 4D
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from ui.main_window import ProjectCreatorApp


def main():
    """Главная функция приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("Project Creator")
    app.setApplicationVersion("0.2")
    
    # Устанавливаем иконку приложения
    app.setWindowIcon(QIcon())
    
    # Создаем и показываем главное окно
    window = ProjectCreatorApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()