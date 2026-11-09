"""Project Creator — entry point."""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.paths import resource
from app.settings import Settings
from app.ui import theme
from app.ui.main_window import MainWindow
from app.version import __version__


def main() -> int:
    if sys.platform == "win32":
        # Own taskbar group + icon instead of python.exe's.
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"RemitOtkin.ProjectCreator.{__version__}")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Project Creator")
    app.setOrganizationName("Remit Otkin")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(str(resource("img", "icon.ico"))))
    theme.apply(app)

    window = MainWindow(Settings())
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
