from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QTimer

def animate_buttons(*buttons, hover_offset=2, duration=150):
    """
    Добавляет анимацию к нескольким кнопкам сразу
    
    Args:
        *buttons: Кнопки для анимации
        hover_offset: Размер эффекта hover
        duration: Длительность анимации в мс
    """
    
    def setup_single_button(button):
        """Настраивает анимацию для одной кнопки"""
        # Создаем анимацию для кнопки
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Функция для получения актуальной оригинальной геометрии
        def get_original_geometry():
            """Возвращает актуальную оригинальную геометрию кнопки"""
            # Если кнопка не анимируется, используем текущую геометрию
            if not getattr(button, '_is_animating', False):
                return button.geometry()
            # Если анимируется, используем сохраненную оригинальную
            return getattr(button, '_original_geometry', button.geometry())
        
        def on_hover_enter(event):
            """Обработчик входа курсора"""
            if getattr(button, '_is_animating', False):
                return
            
            # Получаем актуальную оригинальную геометрию
            original_rect = get_original_geometry()
            button._original_geometry = original_rect
            button._is_animating = True
            
            hover_rect = QRect(
                original_rect.x() - hover_offset,
                original_rect.y() - hover_offset,
                original_rect.width() + 2 * hover_offset,
                original_rect.height() + 2 * hover_offset
            )
            
            animation.setStartValue(button.geometry())
            animation.setEndValue(hover_rect)
            
            # Отключаем предыдущие соединения
            try:
                animation.finished.disconnect()
            except TypeError:
                pass
            
            animation.finished.connect(lambda: setattr(button, '_is_animating', False))
            animation.start()
        
        def on_hover_leave(event):
            """Обработчик выхода курсора"""
            if getattr(button, '_is_animating', False):
                return
            
            # Используем сохраненную оригинальную геометрию
            original_rect = getattr(button, '_original_geometry', button.geometry())
            button._is_animating = True
            
            animation.setStartValue(button.geometry())
            animation.setEndValue(original_rect)
            
            # Отключаем предыдущие соединения
            try:
                animation.finished.disconnect()
            except TypeError:
                pass
            
            animation.finished.connect(lambda: setattr(button, '_is_animating', False))
            animation.start()
        
        def update_geometry():
            """Обновляет оригинальную геометрию кнопки"""
            if not getattr(button, '_is_animating', False):
                button._original_geometry = button.geometry()
        
        # Сохраняем оригинальные методы
        button._original_enterEvent = button.enterEvent
        button._original_leaveEvent = button.leaveEvent
        button._original_resizeEvent = getattr(button, 'resizeEvent', None)
        
        # Устанавливаем новые обработчики
        button.enterEvent = on_hover_enter
        button.leaveEvent = on_hover_leave
        
        # Переопределяем resizeEvent для обновления геометрии
        def on_resize(event):
            if button._original_resizeEvent:
                button._original_resizeEvent(event)
            # Обновляем геометрию с задержкой
            QTimer.singleShot(50, update_geometry)
        
        button.resizeEvent = on_resize
        
        # Сохраняем ссылки
        button._animation = animation
        button._original_geometry = button.geometry()
        button._is_animating = False
        button._update_geometry = update_geometry
    
    # Настраиваем анимацию для всех кнопок
    for button in buttons:
        setup_single_button(button)

def setup_button_animations_delayed(buttons, delay=150, **kwargs):
    """
    Настраивает анимацию кнопок с задержкой
    
    Args:
        buttons: Список кнопок или отдельные кнопки
        delay: Задержка в миллисекундах
        **kwargs: Параметры для animate_buttons
    """
    def apply_animations():
        if isinstance(buttons, (list, tuple)):
            animate_buttons(*buttons, **kwargs)
        else:
            animate_buttons(buttons, **kwargs)
    
    QTimer.singleShot(delay, apply_animations)

def reset_button_animation(button):
    """
    Сбрасывает анимацию кнопки к исходному состоянию
    
    Args:
        button: Кнопка для сброса
    """
    # Останавливаем анимацию
    if hasattr(button, '_animation'):
        button._animation.stop()
    
    # Сбрасываем флаги
    button._is_animating = False
    
    # Восстанавливаем оригинальные методы
    if hasattr(button, '_original_enterEvent'):
        button.enterEvent = button._original_enterEvent
    if hasattr(button, '_original_leaveEvent'):
        button.leaveEvent = button._original_leaveEvent
    if hasattr(button, '_original_resizeEvent') and button._original_resizeEvent:
        button.resizeEvent = button._original_resizeEvent
    
    # Возвращаем к оригинальной геометрии
    if hasattr(button, '_original_geometry'):
        button.setGeometry(button._original_geometry)