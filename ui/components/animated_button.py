"""
Компонент анимированной кнопки
Обеспечивает плавную анимацию при наведении курсора
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtGui import QEnterEvent, QCursor
from PyQt5.QtCore import Qt


class AnimatedButton(QPushButton):
    """Кнопка с анимацией при наведении курсора"""

    def __init__(self, text: str, parent=None):
        """
        Инициализация анимированной кнопки
        
        Args:
            text: Текст кнопки
            parent: Родительский виджет
        """
        super().__init__(text, parent)
        
        # Настройка анимации
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)  # Длительность анимации в мс
        self.original_size = None
        
        # Настройка курсора - исправлено!
        self.setCursor(QCursor(Qt.PointingHandCursor))
    
    def enterEvent(self, event: QEnterEvent) -> None:
        """
        Обработка события входа курсора в область кнопки
        
        Args:
            event: Событие входа курсора
        """
        if self.original_size is None:
            self.original_size = self.geometry()
        
        # Создаем увеличенную геометрию
        new_geometry = QRect(
            self.original_size.x() - 2,
            self.original_size.y() - 2,
            self.original_size.width() + 4,
            self.original_size.height() + 4
        )
        
        # Запускаем анимацию увеличения
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(new_geometry)
        self.animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """
        Обработка события выхода курсора из области кнопки
        
        Args:
            event: Событие выхода курсора
        """
        if self.original_size:
            # Запускаем анимацию возврата к исходному размеру
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.original_size)
            self.animation.start()
        
        super().leaveEvent(event)
    
    def set_animation_duration(self, duration: int) -> None:
        """
        Устанавливает длительность анимации
        
        Args:
            duration: Длительность в миллисекундах
        """
        self.animation.setDuration(duration)
    
    def reset_size(self) -> None:
        """Сбрасывает сохраненный оригинальный размер"""
        self.original_size = None