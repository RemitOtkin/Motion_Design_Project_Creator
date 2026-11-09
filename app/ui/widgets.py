"""Small custom widgets: icons, tool tiles, segmented control, elided labels, banner, preview tree."""

from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import (QColor, QFont, QFontMetrics, QIcon, QPainter, QPainterPath, QPalette, QPen,
                           QPixmap)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QAbstractButton, QButtonGroup, QFrame, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QStyledItemDelegate, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from ..paths import resource
from ..structure import TOOLS_BY_ID, Lid, Node, Tool
from . import theme

# --- Icons -----------------------------------------------------------------

_SVG = {
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "folder_plus": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
                   '<path d="M12 11v5M9.5 13.5h5"/>',
    "file": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1'
            'a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3'
            'l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0'
            ' 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3'
            'a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0'
            '-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.5v.01"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "subfolder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
                 '<path d="M12 10.5v6M9 13.5h6"/>',
    "pencil": '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    "trash": '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    "undo": '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
    "reset": '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
}


@lru_cache(maxsize=128)
def svg_pixmap(name: str, color: str, size: int, stroke: float = 1.8, dpr: float = 2.0) -> QPixmap:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
           f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{_SVG[name]}</svg>')
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pm = QPixmap(int(size * dpr), int(size * dpr))
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    renderer.render(p)
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def svg_icon(name: str, color: str, size: int = 18, stroke: float = 1.8) -> QIcon:
    return QIcon(svg_pixmap(name, color, size, stroke))


@lru_cache(maxsize=16)
def tool_pixmap(filename: str, size: int, dpr: float) -> QPixmap | None:
    pm = QPixmap(str(resource("icons", filename)))
    if pm.isNull():
        return None
    scaled = pm.scaled(int(size * dpr), int(size * dpr), Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
    scaled.setDevicePixelRatio(dpr)
    return scaled


# --- Tool tile ---------------------------------------------------------------

class ToolTile(QAbstractButton):
    """A large toggle with the tool's icon, name and file extension."""

    def __init__(self, tool: Tool, parent: QWidget | None = None):
        super().__init__(parent)
        self.tool = tool
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(96)
        self.setFixedHeight(116)
        self.setAccessibleName(tool.label)
        self.setToolTip(f"{tool.label} — {tool.folder}/  ·  {tool.ext}")

    def sizeHint(self) -> QSize:
        return QSize(120, 116)

    def enterEvent(self, e):
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        on = self.isChecked()
        hover = self.underMouse()

        bg = QColor(theme.ACCENT) if on else QColor(theme.TILE)
        if on:
            bg.setAlphaF(0.07)
        border = QColor(theme.ACCENT if on else (theme.BORDER_STRONG if hover else "#26282D"))
        if self.hasFocus() and not on:
            border = QColor(theme.MUTED)
        path = QPainterPath()
        path.addRoundedRect(r, 12, 12)
        p.fillPath(path, QColor(theme.TILE))
        p.fillPath(path, bg)
        p.setPen(QPen(border, 1.5))
        p.drawPath(path)

        # icon
        x, y, icon_size = 14, 14, 32
        pm = tool_pixmap(self.tool.icon, icon_size, self.devicePixelRatioF())
        if pm is not None:
            if not on:
                p.setOpacity(0.55)
            w = pm.width() / pm.devicePixelRatio()
            h = pm.height() / pm.devicePixelRatio()
            p.drawPixmap(int(x + (icon_size - w) / 2), int(y + (icon_size - h) / 2), pm)
            p.setOpacity(1.0)
        else:
            mono = QRectF(x, y, 38, icon_size)
            mp = QPainterPath()
            mp.addRoundedRect(mono, 7, 7)
            p.fillPath(mp, QColor(theme.ACCENT if on else theme.BORDER))
            p.setPen(QColor(theme.ACCENT_INK if on else theme.TEXT))
            p.setFont(theme.ui_font(13, QFont.Weight.DemiBold))
            p.drawText(mono, Qt.AlignmentFlag.AlignCenter, self.tool.mono)

        # check badge
        if on:
            badge = QRectF(r.right() - 30, r.top() + 10, 20, 20)
            bp = QPainterPath()
            bp.addEllipse(badge)
            p.fillPath(bp, QColor(theme.ACCENT))
            p.drawPixmap(int(badge.x() + 3), int(badge.y() + 3), svg_pixmap("check", theme.ACCENT_INK, 14, 3))

        # text: the name wraps to a second line on narrow tiles instead of being cut off
        p.setPen(QColor(theme.TEXT if on or hover else "#C9CCD1"))
        p.setFont(theme.ui_font(13, QFont.Weight.Medium))
        width = int(r.width() - 24)
        flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap)
        bound = QFontMetrics(p.font()).boundingRect(0, 0, width, 40, flags, self.tool.label)
        text_h = min(bound.height(), 36)
        top = 58 if text_h <= 20 else 54
        p.drawText(QRectF(14, top, width, text_h + 2), flags, self.tool.label)
        p.setPen(QColor(theme.SUBTLE))
        p.setFont(theme.mono_font(11))
        p.drawText(QRectF(14, top + text_h + 2, width, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   self.tool.ext)
        p.end()


# --- Segmented control ---------------------------------------------------------

class Segmented(QFrame):
    changed = Signal(str)

    def __init__(self, options: dict[str, str], current: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("segmented")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self._group = QButtonGroup(self)
        self._buttons: dict[str, QPushButton] = {}
        for key, label in options.items():
            b = QPushButton(label)
            b.setObjectName("seg")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setChecked(key == current)
            b.clicked.connect(lambda _=False, k=key: self.changed.emit(k))
            self._group.addButton(b)
            self._buttons[key] = b
            lay.addWidget(b)

    def set_current(self, key: str) -> None:
        if key in self._buttons:
            self._buttons[key].setChecked(True)


# --- Labels ------------------------------------------------------------------

class ElidedLabel(QLabel):
    """Single-line label that elides in the middle (good for paths and long names)."""

    def __init__(self, text: str = "", object_name: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        if object_name:
            self.setObjectName(object_name)
        self._full = text
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(40)
        self._refresh()

    def setText(self, text: str) -> None:  # noqa: N802 (Qt naming)
        self._full = text
        self.setToolTip(text)
        self._refresh()

    def full_text(self) -> str:
        return self._full

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._refresh()

    def _refresh(self) -> None:
        m = self.contentsMargins()
        avail = max(10, self.width() - m.left() - m.right() - 26)
        super().setText(QFontMetrics(self.font()).elidedText(self._full, Qt.TextElideMode.ElideMiddle, avail))


# --- Result banner -------------------------------------------------------------

class Banner(QFrame):
    open_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 12, 12)
        lay.setSpacing(12)
        self.icon = QLabel()
        self.icon.setFixedSize(28, 28)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text = QVBoxLayout()
        text.setSpacing(2)
        self.title = QLabel()
        self.title.setObjectName("bannerTitle")
        self.body = ElidedLabel(object_name="bannerBody")
        self.body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text.addWidget(self.title)
        text.addWidget(self.body)
        self.open_btn = QPushButton()
        self.open_btn.setObjectName("smallPrimary")
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn.clicked.connect(self.open_clicked)
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("iconButton")
        self.close_btn.setStyleSheet("QPushButton#iconButton{min-height:30px;min-width:30px;max-width:30px;"
                                     "background:transparent;border:none;}")
        self.close_btn.setIcon(svg_icon("close", theme.MUTED, 16))
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide)
        lay.addWidget(self.icon)
        lay.addLayout(text, 1)
        lay.addWidget(self.open_btn)
        lay.addWidget(self.close_btn)
        self.hide()

    def _restyle(self, name: str) -> None:
        self.setObjectName(name)
        self.style().unpolish(self)
        self.style().polish(self)

    def show_success(self, title: str, body: str, open_label: str, close_label: str) -> None:
        self._restyle("bannerOk")
        self.icon.setPixmap(svg_pixmap("check", theme.ACCENT, 22, 2.4))
        self.title.setText(title)
        self.body.setText(body)
        self.open_btn.setText(open_label)
        self.open_btn.show()
        self.close_btn.setAccessibleName(close_label)
        self.show()

    def show_error(self, title: str, body: str, close_label: str) -> None:
        self._restyle("bannerErr")
        self.icon.setPixmap(svg_pixmap("alert", theme.DANGER, 22, 2))
        self.title.setText(title)
        self.body.setText(body)
        self.open_btn.hide()
        self.close_btn.setAccessibleName(close_label)
        self.show()


# --- Preview tree --------------------------------------------------------------

LID_ROLE = Qt.ItemDataRole.UserRole + 1     # "0/2/1" index path into the layout ("" = generated)
NAME_ROLE = Qt.ItemDataRole.UserRole + 2    # folder name without the trailing slash
LOCK_ROLE = Qt.ItemDataRole.UserRole + 3    # why a generated item can't be edited
PROCESS_ROLE = Qt.ItemDataRole.UserRole + 4


def lid_to_str(lid: Lid | None) -> str:
    return "/".join(map(str, lid)) if lid else ""


def str_to_lid(text: str | None) -> Lid | None:
    return tuple(int(x) for x in text.split("/")) if text else None


class _RenameDelegate(QStyledItemDelegate):
    """Inline editor for folder names. Instead of writing to the item it reports the new
    name, and the window rebuilds the tree from the updated layout."""

    def __init__(self, tree: "PreviewTree"):
        super().__init__(tree)
        self.tree = tree

    def createEditor(self, parent, option, index):  # noqa: N802
        editor = QLineEdit(parent)
        editor.setObjectName("treeEditor")
        editor.setFont(theme.mono_font(13))
        return editor

    def setEditorData(self, editor, index):  # noqa: N802
        editor.setText(index.data(NAME_ROLE) or "")
        editor.selectAll()

    def setModelData(self, editor, model, index):  # noqa: N802
        lid, text = str_to_lid(index.data(LID_ROLE)), editor.text()
        if lid is not None:
            # Defer: the window rebuilds the tree, which must not happen while the editor closes.
            QTimer.singleShot(0, lambda: self.tree.rename_requested.emit(lid, text))


class PreviewTree(QTreeWidget):
    rename_requested = Signal(object, str)   # lid, new name
    delete_requested = Signal(object)        # lid
    locked_activated = Signal(str)           # reason a generated item can't be edited

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.setExpandsOnDoubleClick(False)
        self.setIndentation(20)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setUniformRowHeights(True)
        self.setIconSize(QSize(15, 15))
        self.setItemDelegateForColumn(0, _RenameDelegate(self))
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(theme.TEXT))
        self.setPalette(pal)
        hdr = self.header()
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(0, hdr.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, hdr.ResizeMode.ResizeToContents)
        self.itemDoubleClicked.connect(lambda item, _col: self.start_rename(item))

    # -- building
    def show_plan(self, plan: Node, select: Lid | None = None, locks: dict[str, str] | None = None) -> None:
        """Rebuild from a plan, keeping the scroll position. `locks` maps lock kinds to messages."""
        locks = locks or {}
        scroll = self.verticalScrollBar().value()
        if select is None:
            select = self.current_lid()
        self.clear()
        note_font = theme.ui_font(11)
        mono = theme.mono_font(13)
        to_select = None

        def add(parent, node: Node):
            nonlocal to_select
            item = QTreeWidgetItem(parent)
            from_tool = node.tool is not None
            if node.kind == "placeholder":
                color, icon = theme.SUBTLE, None
                label = node.name
            else:
                color = theme.ACCENT if from_tool else theme.TREE_TEXT
                icon_color = theme.ACCENT if from_tool else theme.SUBTLE
                icon = svg_icon("folder" if node.kind == "folder" else "file", icon_color, 15)
                label = node.name + ("/" if node.kind == "folder" else "")
            item.setText(0, label)
            item.setFont(0, mono)
            item.setForeground(0, QColor(color))
            if icon:
                item.setIcon(0, icon)
            item.setText(1, node.note)
            item.setFont(1, note_font)
            item.setForeground(1, QColor(theme.SUBTLE))
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item.setData(0, NAME_ROLE, node.name)
            item.setData(0, LID_ROLE, lid_to_str(node.lid))
            item.setData(0, PROCESS_ROLE, node.process)
            flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            if node.lid is not None:
                flags |= Qt.ItemFlag.ItemIsEditable
                item.setToolTip(0, label)
            else:
                lock = locks.get(node.tool or node.kind, "")
                if node.tool:
                    lock = lock.format(tool=TOOLS_BY_ID[node.tool].label)
                item.setData(0, LOCK_ROLE, lock)
                item.setToolTip(0, lock or label)
            item.setFlags(flags)
            if not node.note:
                item.setFirstColumnSpanned(True)  # long file names get the full width
            if select is not None and node.lid == select:
                to_select = item
            for child in node.children:
                add(item, child)
            return item

        for child in plan.children:
            add(self.invisibleRootItem(), child)
        self.expandAll()
        if to_select is not None:
            self.setCurrentItem(to_select)
        self.verticalScrollBar().setValue(scroll)

    # -- lookup
    def current_lid(self) -> Lid | None:
        item = self.currentItem()
        return str_to_lid(item.data(0, LID_ROLE)) if item else None

    def find(self, lid: Lid) -> QTreeWidgetItem | None:
        key = lid_to_str(lid)
        it = self.invisibleRootItem()
        stack = [it.child(i) for i in range(it.childCount())]
        while stack:
            item = stack.pop()
            if item.data(0, LID_ROLE) == key:
                return item
            stack.extend(item.child(i) for i in range(item.childCount()))
        return None

    # -- editing
    def start_rename(self, item: QTreeWidgetItem | None) -> None:
        if item is None:
            return
        if item.flags() & Qt.ItemFlag.ItemIsEditable:
            self.setCurrentItem(item)
            self.scrollToItem(item)
            self.editItem(item, 0)
        elif item.data(0, LOCK_ROLE):
            self.locked_activated.emit(item.data(0, LOCK_ROLE))

    def rename_lid(self, lid: Lid) -> None:
        self.start_rename(self.find(lid))

    def keyPressEvent(self, e):
        item = self.currentItem()
        if e.key() == Qt.Key.Key_F2 and self.state() != QTreeWidget.State.EditingState:
            self.start_rename(item)
            return
        if e.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and item is not None:
            lid = str_to_lid(item.data(0, LID_ROLE))
            if lid is not None:
                self.delete_requested.emit(lid)
            elif item.data(0, LOCK_ROLE):
                self.locked_activated.emit(item.data(0, LOCK_ROLE))
            return
        super().keyPressEvent(e)

