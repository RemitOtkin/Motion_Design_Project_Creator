"""
Компонент адаптивной анимированной кнопки
Обеспечивает плавную анимацию при наведении курсора с учетом масштабирования
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QEnterEvent, QCursor
from PyQt5.QtCore import Qt


class AnimatedButton(QPushButton):
    """Адаптивная кнопка с анимацией при наведении курсора"""

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
        self.animation.setEasingCurve(QEasingCurve.OutCubic)  # Плавная анимация
        
        # Размер эффекта hover (адаптивный)
        self.hover_offset = 2  # Будет установлен через set_hover_effect
        
        # Настройка курсора
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Флаги состояния
        self.is_hovered = False
        self.is_pressed = False
        self.is_animating = False
        
        # Оригинальный размер будет установлен при первом показе
        self.original_geometry = None
        self.size_captured = False
    
    def showEvent(self, event):
        """
        Захватываем оригинальный размер при первом показе
        
        Args:
            event: Событие показа виджета
        """
        super().showEvent(event)
        if not self.size_captured:
            # Захватываем размер после того, как виджет полностью отрисован
            self.original_geometry = self.geometry()
            self.size_captured = True
    
    def set_hover_effect(self, offset: int) -> None:
        """
        Устанавливает размер эффекта при наведении
        
        Args:
            offset: Смещение в пикселях при hover
        """
        self.hover_offset = max(1, offset)
    
    def enterEvent(self, event: QEnterEvent) -> None:
        """
        Обработка события входа курсора в область кнопки
        
        Args:
            event: Событие входа курсора
        """
        if not self.is_hovered and not self.is_pressed and not self.is_animating:
            # Захватываем текущую геометрию как оригинальную, если еще не захвачена
            if not self.size_captured:
                self.original_geometry = self.geometry()
                self.size_captured = True
            
            self.is_hovered = True
            self._animate_to_hover_state()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        """
        Обработка события выхода курсора из области кнопки
        
        Args:
            event: Событие выхода курсора
        """
        if self.is_hovered and not self.is_pressed:
            self.is_hovered = False
            self._animate_to_normal_state()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        """
        Обработка нажатия мыши
        
        Args:
            event: Событие нажатия мыши
        """
        if not self.is_animating:
            self.is_pressed = True
            self._animate_to_pressed_state()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """
        Обработка отпускания мыши
        
        Args:
            event: Событие отпускания мыши
        """
        self.is_pressed = False
        
        # Проверяем, находится ли курсор еще над кнопкой
        if self.rect().contains(event.pos()):
            if not self.is_hovered:
                self.is_hovered = True
            self._animate_to_hover_state()
        else:
            self.is_hovered = False
            self._animate_to_normal_state()
        
        super().mouseReleaseEvent(event)
    
    def _animate_to_hover_state(self) -> None:
        """Анимация к состоянию hover"""
        if self.original_geometry and not self.is_animating:
            new_geometry = QRect(
                self.original_geometry.x() - self.hover_offset,
                self.original_geometry.y() - self.hover_offset,
                self.original_geometry.width() + 2 * self.hover_offset,
                self.original_geometry.height() + 2 * self.hover_offset
            )
            self._start_animation(new_geometry)
    
    def _animate_to_pressed_state(self) -> None:
        """Анимация к состоянию нажатия"""
        if self.original_geometry and not self.is_animating:
            # Уменьшаем кнопку при нажатии
            press_offset = max(1, self.hover_offset // 2)
            new_geometry = QRect(
                self.original_geometry.x() + press_offset,
                self.original_geometry.y() + press_offset,
                self.original_geometry.width() - 2 * press_offset,
                self.original_geometry.height() - 2 * press_offset
            )
            self._start_animation(new_geometry, duration=100)
    
    def _animate_to_normal_state(self) -> None:
        """Анимация к нормальному состоянию"""
        if self.original_geometry and not self.is_animating:
            self._start_animation(self.original_geometry)
    
    def _start_animation(self, target_geometry: QRect, duration: int = None) -> None:
        """
        Запускает анимацию к целевой геометрии
        
        Args:
            target_geometry: Целевая геометрия
            duration: Длительность анимации (если не указана, используется стандартная)
        """
        if self.is_animating:
            return
        
        self.is_animating = True
        
        # Останавливаем текущую анимацию если она идет
        if self.animation.state() == QPropertyAnimation.Running:
            self.animation.stop()
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(target_geometry)
        
        if duration is not None:
            original_duration = self.animation.duration()
            self.animation.setDuration(duration)
        
        # Подключаем обработчик завершения анимации
        def on_animation_finished():
            self.is_animating = False
            if duration is not None:
                self.animation.setDuration(original_duration)
        
        self.animation.finished.disconnect()  # Отключаем предыдущие соединения
        self.animation.finished.connect(on_animation_finished)
        
        self.animation.start()
    
    def set_animation_duration(self, duration: int) -> None:
        """
        Устанавливает длительность анимации
        
        Args:
            duration: Длительность в миллисекундах
        """
        self.animation.setDuration(max(50, duration))
    
    def set_easing_curve(self, curve: QEasingCurve.Type) -> None:
        """
        Устанавливает кривую сглаживания анимации
        
        Args:
            curve: Тип кривой сглаживания
        """
        self.animation.setEasingCurve(curve)
    
    def reset_size(self) -> None:
        """Сбрасывает сохраненный оригинальный размер"""
        self.original_geometry = None
        self.size_captured = False
        self.is_hovered = False
        self.is_pressed = False
        self.is_animating = False
    
    def resizeEvent(self, event) -> None:
        """
        Обработчик изменения размера кнопки
        
        Args:
            event: Событие изменения размера
        """
        super().resizeEvent(event)
        
        # Обновляем оригинальную геометрию при изменении размера
        if not self.is_animating:
            self.original_geometry = self.geometry()
            self.size_captured = True