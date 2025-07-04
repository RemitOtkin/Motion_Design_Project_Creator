# 🎬 Project Creator - Инструкции по установке

## 🚀 Быстрый запуск

1. **Скачайте и установите Python 3.7+** с [официального сайта](https://www.python.org/downloads/)
   - ⚠️ **ВАЖНО**: При установке обязательно отметьте "Add Python to PATH"

2. **Запустите launcher**:
   - Дважды щелкните на `launch.bat`
   - Launcher автоматически проверит и установит все необходимые зависимости

3. **Готово!** Приложение запустится автоматически

## 📋 Файлы launcher'а

### `launch.bat` - Основной launcher
- ✨ **Умная проверка зависимостей**
- 🔧 **Автоматическая установка недостающих библиотек**
- 📊 **Подробная диагностика системы**
- 📝 **Логирование всех операций**

### `launch_advanced.bat` - Расширенный launcher
- 🔬 **Более детальная диагностика**
- 🛠️ **Дополнительные инструменты отладки**
- 📋 **Расширенная система отчетов**
- 🎯 **Troubleshooting-помощник**

### `check_dependencies.py` - Утилита проверки
- 🧪 **Глубокий анализ зависимостей**
- 📦 **Проверка версий пакетов**
- 🔄 **Автоматическая установка**
- 📊 **Детальные отчеты**

## 🛠️ Ручная установка (если launcher не работает)

### Установка Python
```bash
# Скачайте Python 3.7+ с https://www.python.org/downloads/
# При установке выберите "Add Python to PATH"
```

### Установка зависимостей
```bash
# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем зависимости из requirements.txt
pip install -r requirements.txt

# Или вручную
pip install PyQt5 glob2
```

### Запуск приложения
```bash
python main.py
```

## 🔧 Устранение проблем

### Python не найден
**Проблема**: `'python' is not recognized as an internal or external command`

**Решение**:
1. Переустановите Python с официального сайта
2. При установке обязательно отметьте "Add Python to PATH"
3. Перезагрузите компьютер
4. Попробуйте запустить снова

### Ошибки при установке PyQt5
**Проблема**: `Failed building wheel for PyQt5`

**Решение**:
```bash
# Обновите pip, setuptools и wheel
python -m pip install --upgrade pip setuptools wheel

# Попробуйте установить PyQt5 снова
pip install PyQt5

# Если не помогает, попробуйте другую версию
pip install PyQt5==5.15.7
```

### Проблемы с правами доступа
**Проблема**: `Permission denied` или `Access is denied`

**Решение**:
1. Запустите launcher как администратор (ПКМ → "Запуск от имени администратора")
2. Или установите пакеты в пользовательскую папку:
   ```bash
   pip install --user PyQt5 glob2
   ```

### Проблемы с отображением
**Проблема**: Приложение не запускается или черный экран

**Решение**:
1. Обновите драйверы графики
2. Попробуйте запустить в режиме совместимости
3. Временно отключите антивирус
4. Проверьте, не блокирует ли брандмауэр приложение

## 📋 Системные требования

### Минимальные требования
- **ОС**: Windows 7/8/10/11
- **Python**: 3.7+
- **RAM**: 512 MB
- **Место на диске**: 100 MB

### Рекомендуемые требования
- **ОС**: Windows 10/11
- **Python**: 3.9+
- **RAM**: 2 GB
- **Место на диске**: 500 MB

## 🧪 Режимы запуска

### Обычный запуск
```bash
launch.bat
```

### Тихий режим (только ошибки)
```bash
python check_dependencies.py --quiet
```

### Принудительная переустановка зависимостей
```bash
python check_dependencies.py --install
```

### Использование custom requirements.txt
```bash
python check_dependencies.py --requirements custom_requirements.txt --install
```

## 📝 Логи и отладка

### Файлы логов
- `launcher.log` - основной лог launcher'а
- `dependency_check.log` - лог проверки зависимостей (в тихом режиме)

### Полезные команды для отладки
```bash
# Проверка версии Python
python --version

# Список установленных пакетов
pip list

# Информация о конкретном пакете
pip show PyQt5

# Проверка импорта
python -c "import PyQt5; print('PyQt5 OK')"
```

## 🆘 Получение помощи

Если у вас возникли проблемы:

1. **Проверьте лог-файлы** `launcher.log` и `dependency_check.log`
2. **Попробуйте расширенный launcher** `launch_advanced.bat`
3. **Запустите диагностику**:
   ```bash
   python check_dependencies.py --install
   ```
4. **Создайте issue** с подробным описанием проблемы и содержимым лог-файлов

## 📚 Дополнительные ресурсы

- [Официальная документация Python](https://docs.python.org/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [pip Documentation](https://pip.pypa.io/en/stable/)

---

**🎬 Project Creator** - создан для упрощения работы с медиа-проектами!

_Если launcher не работает, не отчаивайтесь - попробуйте ручную установку или обратитесь за помощью!_