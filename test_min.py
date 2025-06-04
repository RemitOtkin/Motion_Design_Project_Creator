#!/usr/bin/env python3
"""
Минимальная тестовая версия для диагностики
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class MinimalTestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        print("🔄 Создание минимального тестового приложения...")
        
        # Базовые настройки
        self.setWindowTitle("🧪 Тест Project Creator")
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Тестовые элементы
        title = QLabel("🎬 Project Creator - Тест")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; color: blue; padding: 20px;")
        
        subtitle = QLabel("Если вы видите этот текст, PyQt5 работает корректно")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: green; padding: 10px;")
        
        test_button = QPushButton("Тестовая кнопка")
        test_button.clicked.connect(lambda: print("✅ Кнопка работает!"))
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(test_button)
        layout.addStretch()
        
        print("✅ Минимальное приложение создано")

def test_minimal():
    """Запуск минимального теста"""
    app = QApplication(sys.argv)
    window = MinimalTestApp()
    window.show()
    
    print("🚀 Минимальное приложение запущено")
    print("Если окно показывается корректно, проблема в основном коде")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    test_minimal()