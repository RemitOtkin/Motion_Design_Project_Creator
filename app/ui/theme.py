"""Design tokens, Qt palette and the app stylesheet."""

from __future__ import annotations

import sys

from ..paths import resource

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

# Colors
BG = "#0E0F11"
PANEL = "#141518"
TILE = "#16171A"
FIELD = "#1B1C20"
FIELD_HOVER = "#202126"
BORDER = "#2A2C31"
BORDER_STRONG = "#3A3D44"
DIVIDER = "#1F2125"
TEXT = "#EDEEF0"
MUTED = "#A3A7AE"
SUBTLE = "#8A8F98"
TREE_TEXT = "#D7D9DD"
ACCENT = "#C5F36A"
ACCENT_HOVER = "#D3F786"
ACCENT_PRESSED = "#B2E055"
ACCENT_INK = "#11130D"
DANGER = "#FF8A7A"
DANGER_BG = "#2A1715"
SUCCESS_BG = "#1B2212"

UI_FONTS = ["Inter", "Segoe UI Variable Text", "Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"]
MONO_FONTS = ["JetBrains Mono", "Cascadia Mono", "Cascadia Code", "Consolas", "Menlo", "DejaVu Sans Mono"]


def _css_family(families: list[str]) -> str:
    return ", ".join(f'"{f}"' for f in families)


UI = _css_family(UI_FONTS)
MONO = _css_family(MONO_FONTS)
CHEVRON = resource("img", "chevron.svg").as_posix()


def ui_font(px: int = 14, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    f = QFont()
    f.setFamilies(UI_FONTS)
    f.setPixelSize(px)
    f.setWeight(weight)
    return f


def mono_font(px: int = 13) -> QFont:
    f = QFont()
    f.setFamilies(MONO_FONTS)
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setPixelSize(px)
    return f


def apply(app: QApplication) -> None:
    app.setStyle("Fusion")
    pal = QPalette()
    roles = {
        QPalette.ColorRole.Window: BG,
        QPalette.ColorRole.WindowText: TEXT,
        QPalette.ColorRole.Base: FIELD,
        QPalette.ColorRole.AlternateBase: PANEL,
        QPalette.ColorRole.Text: TEXT,
        QPalette.ColorRole.Button: FIELD,
        QPalette.ColorRole.ButtonText: TEXT,
        QPalette.ColorRole.Highlight: ACCENT,
        QPalette.ColorRole.HighlightedText: ACCENT_INK,
        QPalette.ColorRole.ToolTipBase: FIELD,
        QPalette.ColorRole.ToolTipText: TEXT,
        QPalette.ColorRole.PlaceholderText: "#7D828B",
        QPalette.ColorRole.Link: ACCENT,
    }
    for role, color in roles.items():
        pal.setColor(role, QColor(color))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(SUBTLE))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(SUBTLE))
    app.setPalette(pal)
    app.setFont(ui_font(14))
    app.setStyleSheet(STYLESHEET)


STYLESHEET = f"""
* {{ font-family: {UI}; }}
QMainWindow, QDialog, #root {{ background: {BG}; }}
QToolTip {{ background: {FIELD}; color: {TEXT}; border: 1px solid {BORDER}; padding: 6px 8px; border-radius: 6px; }}

QLabel {{ color: {TEXT}; background: transparent; }}
QLabel#appTitle {{ font-size: 20px; font-weight: 700; }}
QLabel#appSub {{ color: {MUTED}; font-size: 13px; }}
QLabel#fieldLabel {{ color: {MUTED}; font-size: 13px; font-weight: 600; }}
QLabel#hint {{ color: {SUBTLE}; font-size: 12px; }}
QLabel#error {{ color: {DANGER}; font-size: 12px; }}
QLabel#panelTitle {{ font-size: 15px; font-weight: 600; }}
QLabel#counts {{ color: {MUTED}; font-size: 12px; }}
QLabel#smallMuted {{ color: {SUBTLE}; font-size: 12px; }}
QLabel#finalName {{ font-family: {MONO}; font-size: 15px; font-weight: 500; }}
QLabel#pathLine {{ font-family: {MONO}; font-size: 12px; color: {MUTED};
    background: {FIELD}; border-radius: 8px; padding: 9px 12px; }}
QLabel#bannerTitle {{ font-size: 14px; font-weight: 600; }}
QLabel#bannerBody {{ font-family: {MONO}; font-size: 12px; color: {MUTED}; }}

QLineEdit {{
    background: {FIELD}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 0 14px; min-height: 44px; font-size: 15px; selection-background-color: {ACCENT};
    selection-color: {ACCENT_INK};
}}
QLineEdit:hover {{ border-color: {BORDER_STRONG}; }}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QLineEdit[invalid="true"] {{ border-color: {DANGER}; }}
QLineEdit#pathEdit {{ font-family: {MONO}; font-size: 13px; }}

QPushButton {{
    background: {FIELD}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 0 16px; min-height: 44px; font-size: 14px; font-weight: 500;
}}
QPushButton:hover {{ border-color: {BORDER_STRONG}; background: {FIELD_HOVER}; }}
QPushButton:pressed {{ background: {BORDER}; }}
QPushButton:focus {{ border-color: {ACCENT}; }}
QPushButton:disabled {{ color: {SUBTLE}; }}

QPushButton#primary {{
    background: {ACCENT}; color: {ACCENT_INK}; border: none; border-radius: 12px;
    min-height: 48px; padding: 0 20px; font-size: 15px; font-weight: 600;
}}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; }}
QPushButton#primary:pressed {{ background: {ACCENT_PRESSED}; }}
QPushButton#primary:focus {{ border: 2px solid {TEXT}; }}
QPushButton#primary:disabled {{ background: #2A2D24; color: #6F7562; }}
QPushButton#small {{ min-height: 34px; padding: 0 12px; font-size: 13px; border-radius: 8px; }}
QPushButton#smallPrimary {{
    min-height: 34px; padding: 0 14px; font-size: 13px; font-weight: 600; border-radius: 8px;
    background: {ACCENT}; color: {ACCENT_INK}; border: none;
}}
QPushButton#smallPrimary:hover {{ background: {ACCENT_HOVER}; }}
QPushButton#iconButton {{ min-height: 36px; min-width: 36px; max-width: 36px; padding: 0; border-radius: 9px; }}

QFrame#segmented {{ background: {FIELD}; border: 1px solid {BORDER}; border-radius: 9px; }}
QPushButton#seg {{
    min-height: 28px; padding: 0 10px; border: none; border-radius: 6px; background: transparent;
    color: {MUTED}; font-size: 12px; font-weight: 600;
}}
QPushButton#seg:hover {{ color: {TEXT}; }}
QPushButton#seg:checked {{ background: {BORDER}; color: {TEXT}; }}

QFrame#panel {{ background: {PANEL}; border: 1px solid {DIVIDER}; border-radius: 16px; }}
QFrame#divider {{ background: {DIVIDER}; max-height: 1px; min-height: 1px; border: none; }}
QFrame#bannerOk {{ background: {SUCCESS_BG}; border: 1px solid #3B4A22; border-radius: 12px; }}
QFrame#bannerErr {{ background: {DANGER_BG}; border: 1px solid #4A2622; border-radius: 12px; }}

QTreeWidget {{ background: transparent; border: none; outline: none; font-family: {MONO}; font-size: 13px; }}
QTreeWidget::item {{ height: 26px; border: none; padding: 0; }}
QTreeWidget::item:hover {{ background: {FIELD}; }}
QTreeWidget::item:selected {{ background: #23271B; }}
QTreeWidget::item:selected:hover {{ background: #283020; }}
QTreeWidget::branch {{ background: transparent; image: none; border: none; }}
QTreeWidget::branch:selected {{ background: #23271B; }}
QLineEdit#treeEditor {{
    min-height: 0; padding: 0 6px; border-radius: 5px; border: 1px solid {ACCENT};
    background: {BG}; font-family: {MONO}; font-size: 13px;
}}

QMenu {{ background: {FIELD}; border: 1px solid {BORDER}; border-radius: 10px; padding: 6px; }}
QMenu::item {{ color: {TEXT}; padding: 7px 28px 7px 10px; border-radius: 6px; font-size: 13px; }}
QMenu::item:selected {{ background: {BORDER}; }}
QMenu::item:disabled {{ color: {SUBTLE}; background: transparent; }}
QMenu::icon {{ padding-left: 8px; }}
QMenu::separator {{ height: 1px; background: {DIVIDER}; margin: 5px 8px; }}
QMenu::right-arrow {{ width: 0; }}
QLabel#chip {{ color: {ACCENT}; background: #23271B; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 600; }}

QComboBox {{
    background: {FIELD}; color: {TEXT}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 0 14px; min-height: 44px; font-size: 14px;
}}
QComboBox:hover {{ border-color: {BORDER_STRONG}; }}
QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 32px; }}
QComboBox::down-arrow {{ image: url("{CHEVRON}"); width: 12px; height: 12px; }}
QComboBox QAbstractItemView {{
    background: {FIELD}; color: {TEXT}; border: 1px solid {BORDER}; selection-background-color: {BORDER};
    selection-color: {TEXT}; outline: none; padding: 4px;
}}

QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px 2px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {BORDER_STRONG}; }}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{ height: 0; background: none; }}
QScrollBar:horizontal {{ height: 0; }}
"""


def dark_title_bar(widget) -> None:
    """Ask Windows 10/11 for a dark title bar so the window frame matches the app."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = int(widget.winId())
        value = ctypes.c_int(1)
        for attr in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (new, old builds)
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                break
    except Exception:
        pass
