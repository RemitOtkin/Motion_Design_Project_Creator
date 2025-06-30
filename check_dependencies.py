#!/usr/bin/env python3
"""
Project Creator - Утилита проверки зависимостей
Проверяет наличие всех необходимых библиотек и их версии
"""

import sys
import subprocess
import importlib
import pkg_resources
from typing import Dict, List, Tuple


class DependencyChecker:
    """Проверяет зависимости проекта"""
    
    REQUIRED_PACKAGES = {
        'PyQt5': '5.15.0',
        'glob2': None,  # Любая версия
    }
    
    OPTIONAL_PACKAGES = {
        'requests': '2.25.0',
        'psutil': '5.8.0',
        'colorama': '0.4.4',
        'packaging': '21.0',
    }
    
    def __init__(self):
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.results = {
            'python': True,
            'required': {},
            'optional': {},
            'missing': [],
            'outdated': []
        }
    
    def check_python_version(self) -> bool:
        """Проверяет версию Python"""
        print(f"🐍 Python версия: {self.python_version}")
        
        if sys.version_info < (3, 7):
            print("❌ Требуется Python 3.7 или выше!")
            self.results['python'] = False
            return False
        
        print("✅ Версия Python подходит")
        return True
    
    def check_package(self, package_name: str, min_version: str = None) -> Tuple[bool, str]:
        """
        Проверяет наличие и версию пакета
        
        Args:
            package_name: Имя пакета
            min_version: Минимальная требуемая версия
            
        Returns:
            Tuple[bool, str]: (установлен, версия)
        """
        try:
            # Пытаемся импортировать
            importlib.import_module(package_name)
            
            # Получаем версию
            installed_version = 'unknown'
            try:
                installed_version = pkg_resources.get_distribution(package_name).version
            except:
                try:
                    module = importlib.import_module(package_name)
                    installed_version = getattr(module, '__version__', 'unknown')
                except:
                    installed_version = 'unknown'
            
            # Простая проверка версии
            if min_version and installed_version != 'unknown':
                try:
                    # Простое сравнение версий
                    if installed_version < min_version:
                        return False, f"{installed_version} (требуется {min_version}+)"
                except:
                    pass  # Игнорируем ошибки сравнения версий
            
            return True, installed_version
            
        except ImportError:
            return False, "не установлен"
    
    def check_required_packages(self) -> None:
        """Проверяет обязательные пакеты"""
        print("\n📚 Проверка обязательных пакетов:")
        
        for package, min_version in self.REQUIRED_PACKAGES.items():
            is_installed, version_info = self.check_package(package, min_version)
            
            if is_installed:
                print(f"✅ {package}: {version_info}")
                self.results['required'][package] = version_info
            else:
                print(f"❌ {package}: {version_info}")
                self.results['missing'].append(package)
                if "требуется" in version_info:
                    self.results['outdated'].append(package)
    
    def check_optional_packages(self) -> None:
        """Проверяет опциональные пакеты"""
        print("\n📦 Проверка опциональных пакетов:")
        
        for package, min_version in self.OPTIONAL_PACKAGES.items():
            is_installed, version_info = self.check_package(package, min_version)
            
            if is_installed:
                print(f"✅ {package}: {version_info}")
                self.results['optional'][package] = version_info
            else:
                print(f"⚪ {package}: {version_info} (опционально)")
    
    def install_missing_packages(self) -> bool:
        """Устанавливает недостающие обязательные пакеты"""
        if not self.results['missing']:
            return True
        
        print(f"\n🚀 Установка недостающих пакетов: {', '.join(self.results['missing'])}")
        
        try:
            # Обновляем pip
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Устанавливаем пакеты
            for package in self.results['missing']:
                min_version = self.REQUIRED_PACKAGES.get(package)
                package_spec = f"{package}>={min_version}" if min_version else package
                
                print(f"📥 Установка {package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package_spec, '--user'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("✅ Все пакеты установлены!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки: {e}")
            return False
    
    def generate_report(self) -> str:
        """Генерирует отчет о проверке"""
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          🔍 ОТЧЕТ О ЗАВИСИМОСТЯХ                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║ Python версия: {self.python_version:<60} ║
║ Статус Python: {'✅ OK' if self.results['python'] else '❌ Проблема':<58} ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║ ОБЯЗАТЕЛЬНЫЕ ПАКЕТЫ:                                                                ║
"""
        
        for package, version in self.results['required'].items():
            status = "✅ OK"
            report += f"║ {package:<20} {version:<20} {status:<30} ║\n"
        
        for package in self.results['missing']:
            if package in self.REQUIRED_PACKAGES:
                status = "❌ ОТСУТСТВУЕТ"
                report += f"║ {package:<20} {'не установлен':<20} {status:<30} ║\n"
        
        if self.results['optional']:
            report += "╠══════════════════════════════════════════════════════════════════════════════════════╣\n"
            report += "║ ОПЦИОНАЛЬНЫЕ ПАКЕТЫ:                                                                 ║\n"
            
            for package, version in self.results['optional'].items():
                status = "✅ OK"
                report += f"║ {package:<20} {version:<20} {status:<30} ║\n"
        
        # Резюме
        report += "╠══════════════════════════════════════════════════════════════════════════════════════╣\n"
        report += "║ РЕЗЮМЕ:                                                                                  ║\n"
        
        if not self.results['missing'] and self.results['python']:
            report += "║ 🎉 Все зависимости в порядке! Приложение готово к запуску.                         ║\n"
        else:
            if self.results['missing']:
                report += f"║ ⚠️  Отсутствуют пакеты: {', '.join(self.results['missing']):<50} ║\n"
            if not self.results['python']:
                report += "║ ⚠️  Проблема с версией Python                                                      ║\n"
        
        report += "╚══════════════════════════════════════════════════════════════════════════════════════╝"
        
        return report
    
    def run_check(self, auto_install: bool = False) -> bool:
        """
        Запускает полную проверку
        
        Args:
            auto_install: Автоматически устанавливать недостающие пакеты
            
        Returns:
            bool: True если все в порядке
        """
        print("🔍 Запуск проверки зависимостей...\n")
        
        # Проверяем Python
        python_ok = self.check_python_version()
        
        # Проверяем пакеты
        self.check_required_packages()
        self.check_optional_packages()
        
        # Автоустановка если требуется
        if auto_install and self.results['missing']:
            install_success = self.install_missing_packages()
            if install_success:
                # Повторно проверяем после установки
                print("\n🔄 Повторная проверка после установки...")
                self.results['required'] = {}
                self.results['missing'] = []
                self.check_required_packages()
        
        # Генерируем отчет
        print(self.generate_report())
        
        # Возвращаем результат
        return python_ok and not self.results['missing']


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Проверка зависимостей для Project Creator"
    )
    parser.add_argument(
        '--install', '-i', 
        action='store_true',
        help='Автоматически устанавливать недостающие пакеты'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Тихий режим (только ошибки)'
    )
    parser.add_argument(
        '--requirements', '-r',
        help='Путь к файлу requirements.txt'
    )
    
    args = parser.parse_args()
    
    # Настройка вывода
    if args.quiet:
        import sys
        sys.stdout = open('dependency_check.log', 'w', encoding='utf-8')
    
    checker = DependencyChecker()
    
    # Если указан файл requirements.txt, читаем его
    if args.requirements:
        try:
            with open(args.requirements, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"📋 Чтение зависимостей из {args.requirements}")
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '>=' in line:
                        package, version = line.split('>=')
                        checker.REQUIRED_PACKAGES[package.strip()] = version.strip()
                    else:
                        checker.REQUIRED_PACKAGES[line] = None
                        
        except FileNotFoundError:
            print(f"❌ Файл {args.requirements} не найден")
            return False
        except Exception as e:
            print(f"❌ Ошибка чтения {args.requirements}: {e}")
            return False
    
    # Запускаем проверку
    success = checker.run_check(auto_install=args.install)
    
    if args.quiet:
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        
        if success:
            print("✅ Проверка завершена успешно (детали в dependency_check.log)")
        else:
            print("❌ Обнаружены проблемы (детали в dependency_check.log)")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)