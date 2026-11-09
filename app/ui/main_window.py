"""The single main screen: form on the left, live folder preview on the right."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QByteArray, QPoint, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QMenu, QPushButton, QSizePolicy, QVBoxLayout,
                               QWidget)

from ..creator import CreateError, CreateResult, create_project
from ..i18n import LANGUAGES, Translator
from ..paths import open_in_file_manager, resource
from ..settings import Settings
from ..structure import (TOOLS, Layout, Lid, build_plan, clean_name, clone, contains_process, count,
                         default_layout, get_node, invalid_chars, name_taken, new_folder, sanitize_layout,
                         siblings_of, suggest_name)
from ..version import __version__
from . import theme
from .settings_dialog import SettingsDialog
from .widgets import (LID_ROLE, LOCK_ROLE, PROCESS_ROLE, Banner, ElidedLabel, PreviewTree, Segmented,
                      ToolTile, str_to_lid, svg_icon, svg_pixmap)


class CreateWorker(QThread):
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, base: Path, plan, tools, tr):
        super().__init__()
        self.base, self.plan, self.tools, self.tr = base, plan, tools, tr

    def run(self) -> None:
        try:
            self.done.emit(create_project(self.base, self.plan, self.tools, resource("templates"), self.tr))
        except CreateError as e:
            self.failed.emit(str(e))
        except Exception as e:  # pragma: no cover - last-resort safety net
            self.failed.emit(self.tr("err_generic", error=e))


def _label(object_name: str, text: str = "") -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName(object_name)
    return lbl


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.tr_ = Translator(settings.get("language"))
        self.worker: CreateWorker | None = None
        self._last_created: Path | None = None
        saved = settings.get("layout")
        self.layout: Layout = sanitize_layout(saved) if saved else default_layout()
        self._undo: list[Layout] = []
        self._flash_timer = QTimer(self, singleShot=True, interval=4500)
        self._flash_timer.timeout.connect(self._clear_flash)

        self.setWindowTitle(f"Project Creator {__version__}")
        self.setMinimumSize(980, 660)
        self.resize(1180, 720)
        self.setAcceptDrops(True)

        self._build()
        self._retranslate()
        self._restore_geometry()
        self._refresh()

        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self._create)
        QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self._create)
        self.name_edit.setFocus()

    # ---------------------------------------------------------------- layout
    def _build(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Left: form
        form = QWidget()
        form.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        fl = QVBoxLayout(form)
        fl.setContentsMargins(40, 30, 32, 28)
        fl.setSpacing(0)

        # Header
        head = QHBoxLayout()
        head.setSpacing(12)
        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"background: {theme.ACCENT}; border-radius: 10px;")
        logo.setPixmap(svg_pixmap("folder_plus", theme.ACCENT_INK, 22, 2.2))
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.app_title = _label("appTitle")
        self.app_sub = _label("appSub")
        self.app_sub.setWordWrap(True)
        titles.addWidget(self.app_title)
        titles.addWidget(self.app_sub)
        self.lang_switch = Segmented({k: k.upper() for k in LANGUAGES}, self.tr_.lang)
        self.lang_switch.changed.connect(self._set_language)
        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("iconButton")
        self.settings_btn.setIcon(svg_icon("gear", theme.MUTED, 18))
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self._open_settings)
        head.addWidget(logo, 0, Qt.AlignmentFlag.AlignTop)
        head.addLayout(titles, 1)
        head.addWidget(self.lang_switch, 0, Qt.AlignmentFlag.AlignTop)
        head.addWidget(self.settings_btn, 0, Qt.AlignmentFlag.AlignTop)
        fl.addLayout(head)
        fl.addSpacing(30)

        # Project name
        self.name_label = _label("fieldLabel")
        self.name_edit = QLineEdit()
        self.name_edit.setClearButtonEnabled(True)
        self.name_label.setBuddy(self.name_edit)
        self.name_msg = _label("hint")
        self.name_edit.textChanged.connect(self._on_input)
        fl.addWidget(self.name_label)
        fl.addSpacing(8)
        fl.addWidget(self.name_edit)
        fl.addSpacing(6)
        fl.addWidget(self.name_msg)
        fl.addSpacing(16)

        # Location
        self.loc_label = _label("fieldLabel")
        loc_row = QHBoxLayout()
        loc_row.setSpacing(8)
        self.path_edit = QLineEdit(self.settings.get("default_path"))
        self.path_edit.setObjectName("pathEdit")
        self.loc_label.setBuddy(self.path_edit)
        self.path_edit.textChanged.connect(self._on_input)
        self.browse_btn = QPushButton()
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.clicked.connect(self._browse)
        loc_row.addWidget(self.path_edit, 1)
        loc_row.addWidget(self.browse_btn)
        self.loc_msg = _label("hint")
        fl.addWidget(self.loc_label)
        fl.addSpacing(8)
        fl.addLayout(loc_row)
        fl.addSpacing(6)
        fl.addWidget(self.loc_msg)
        fl.addSpacing(22)

        # Tools
        tools_head = QHBoxLayout()
        tools_head.setSpacing(6)
        self.tools_label = _label("fieldLabel")
        self.tools_hint = _label("smallMuted")
        tools_head.addWidget(self.tools_label)
        tools_head.addWidget(self.tools_hint, 1)
        fl.addLayout(tools_head)
        fl.addSpacing(10)
        grid = QGridLayout()
        grid.setSpacing(10)
        self.tiles: dict[str, ToolTile] = {}
        remembered = set(self.settings.get("last_tools") or [])
        for i, tool in enumerate(TOOLS):
            tile = ToolTile(tool)
            tile.setChecked(tool.id in remembered)
            tile.toggled.connect(lambda _checked: self._refresh())
            self.tiles[tool.id] = tile
            grid.addWidget(tile, 0, i)
        fl.addLayout(grid)

        fl.addStretch(1)
        fl.addSpacing(20)
        self.banner = Banner()
        self.banner.open_clicked.connect(self._open_created)
        fl.addWidget(self.banner)
        fl.addSpacing(16)

        divider = QFrame()
        divider.setObjectName("divider")
        fl.addWidget(divider)
        fl.addSpacing(20)

        foot = QHBoxLayout()
        foot.setSpacing(16)
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        self.final_caption = _label("smallMuted")
        self.final_name = ElidedLabel(object_name="finalName")
        name_col.addWidget(self.final_caption)
        name_col.addWidget(self.final_name)
        self.create_btn = QPushButton()
        self.create_btn.setObjectName("primary")
        self.create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_btn.clicked.connect(self._create)
        self.create_btn.setMinimumWidth(210)
        foot.addLayout(name_col, 1)
        foot.addWidget(self.create_btn)
        fl.addLayout(foot)

        # Right: preview panel
        side = QWidget()
        side.setMinimumWidth(360)
        side.setMaximumWidth(520)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 20, 20, 20)
        panel = QFrame()
        panel.setObjectName("panel")
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 20, 0, 14)
        pl.setSpacing(12)
        ph = QHBoxLayout()
        ph.setContentsMargins(20, 0, 20, 0)
        self.preview_title = _label("panelTitle")
        self.counts = _label("counts")
        self.custom_chip = _label("chip")
        self.custom_chip.hide()
        ph.addWidget(self.preview_title)
        ph.addWidget(self.custom_chip)
        ph.addStretch(1)
        ph.addWidget(self.counts)
        pl.addLayout(ph)
        path_wrap = QHBoxLayout()
        path_wrap.setContentsMargins(20, 0, 20, 0)
        self.preview_path = ElidedLabel(object_name="pathLine")
        path_wrap.addWidget(self.preview_path)
        pl.addLayout(path_wrap)
        self.tree = PreviewTree()
        self.tree.customContextMenuRequested.connect(self._tree_menu)
        self.tree.rename_requested.connect(self._rename_folder)
        self.tree.delete_requested.connect(self._delete_folder)
        self.tree.locked_activated.connect(lambda msg: self._flash(msg))
        QShortcut(QKeySequence.StandardKey.Undo, self.tree, activated=self._undo_layout,
                  context=Qt.ShortcutContext.WidgetWithChildrenShortcut)
        tree_wrap = QHBoxLayout()
        tree_wrap.setContentsMargins(8, 0, 12, 0)
        tree_wrap.addWidget(self.tree)
        pl.addLayout(tree_wrap, 1)
        legend_div = QFrame()
        legend_div.setObjectName("divider")
        pl.addWidget(legend_div)
        legend = QHBoxLayout()
        legend.setContentsMargins(20, 0, 20, 0)
        legend.setSpacing(8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {theme.ACCENT}; border-radius: 4px;")
        self.legend_label = _label("counts")
        self.tree_hint = ElidedLabel(object_name="smallMuted")
        self.tree_hint.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        legend.addWidget(dot)
        legend.addWidget(self.legend_label)
        legend.addSpacing(12)
        legend.addWidget(self.tree_hint, 1)
        pl.addLayout(legend)
        sl.addWidget(panel)

        outer.addWidget(form, 3)
        outer.addWidget(side, 2)

    # ------------------------------------------------------------- text
    def _retranslate(self) -> None:
        t = self.tr_
        self.app_title.setText(t("app_title"))
        self.app_sub.setText(t("subtitle"))
        self.name_label.setText(t("project_name"))
        self.name_edit.setPlaceholderText(t("project_name_ph"))
        self.loc_label.setText(t("location"))
        self.browse_btn.setText(t("browse"))
        self.tools_label.setText(t("tools"))
        self.tools_hint.setText("· " + t("tools_hint"))
        self.final_caption.setText(t("will_be_created"))
        self.create_btn.setText(f"{t('create')}    Ctrl ↵")
        self.preview_title.setText(t("preview"))
        self.legend_label.setText(t("legend_tools"))
        self.custom_chip.setText(t("tree_edited"))
        if not self._flash_timer.isActive():
            self._clear_flash()
        self.settings_btn.setToolTip(t("settings"))
        self.settings_btn.setAccessibleName(t("settings"))
        self.banner.open_btn.setText(t("open_folder"))
        if self.banner.isVisible() and self._last_created is not None:
            self.banner.title.setText(t("created_title"))

    def _set_language(self, lang: str) -> None:
        self.tr_.set_language(lang)
        self.settings.set("language", lang)
        self.settings.save()
        self.lang_switch.set_current(lang)
        self._retranslate()
        self._refresh()

    # ------------------------------------------------------------ state
    def _selected_tools(self) -> list[str]:
        return [t.id for t in TOOLS if self.tiles[t.id].isChecked()]

    def _on_input(self) -> None:
        self._refresh()

    def _validate(self) -> tuple[bool, str]:
        """Update field messages; return (valid, cleaned name)."""
        t = self.tr_
        raw = self.name_edit.text()
        name = clean_name(raw)
        base = Path(self.path_edit.text().strip())
        ok = True

        name_err = ""
        name_note = ""
        if raw.strip() and len(name) < 3:
            name_err = t("err_name_short")
        elif bad := invalid_chars(raw):
            name_note = t("err_name_invalid", chars=bad) + "  " + t("note_cleaned")
        if len(name) < 3:
            ok = False

        loc_err = ""
        if not self.path_edit.text().strip() or not base.is_dir():
            loc_err = t("err_path_missing")
            ok = False
        elif len(name) >= 3 and (base / name).exists():
            name_err = t("err_exists")
            ok = False

        self._set_msg(self.name_msg, self.name_edit, name_err, name_note)
        self._set_msg(self.loc_msg, self.path_edit, loc_err, t("location_hint"))
        return ok, name

    @staticmethod
    def _set_msg(label: QLabel, field: QLineEdit, error: str, hint: str) -> None:
        label.setObjectName("error" if error else "hint")
        label.setText(error or hint)
        label.setVisible(bool(error or hint))
        label.style().unpolish(label)
        label.style().polish(label)
        field.setProperty("invalid", bool(error))
        field.style().unpolish(field)
        field.style().polish(field)

    def _locks(self) -> dict[str, str]:
        t = self.tr_
        tool_msg = t("locked_tool", tool="{tool}")
        return {**{tool.id: tool_msg for tool in TOOLS}, "file": t("locked_readme"), "placeholder": ""}

    def _refresh(self, select: Lid | None = None) -> None:
        valid, name = self._validate()
        plan = build_plan(name or "Untitled", self._selected_tools(), self.tr_, self.layout)
        folders, files = count(plan)
        self.tree.show_plan(plan, select, self._locks())
        self.custom_chip.setVisible(self.layout != default_layout())
        self.counts.setText(self.tr_("counts", folders=folders, files=files))
        base = self.path_edit.text().strip()
        self.preview_path.setText(str(Path(base) / (name or "…")) if base else (name or "…"))
        self.final_name.setText(name or "—")
        self.final_name.setStyleSheet("" if name else f"color: {theme.SUBTLE};")
        busy = self.worker is not None and self.worker.isRunning()
        self.create_btn.setEnabled(valid and not busy)

    # ---------------------------------------------------------- actions
    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.tr_("choose_folder"), self.path_edit.text())
        if folder:
            self.path_edit.setText(str(Path(folder)))

    def _create(self) -> None:
        valid, name = self._validate()
        if not valid or (self.worker and self.worker.isRunning()):
            return
        tools = self._selected_tools()
        plan = build_plan(name, tools, self.tr_, self.layout)
        self.banner.hide()
        self.create_btn.setEnabled(False)
        self.create_btn.setText(self.tr_("creating"))
        self.worker = CreateWorker(Path(self.path_edit.text().strip()), plan, tools, self.tr_)
        self.worker.done.connect(self._on_created)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _on_created(self, result: CreateResult) -> None:
        self._last_created = result.path
        self.settings.set("last_tools", self._selected_tools())
        self.settings.save()
        self.banner.show_success(
            self.tr_("created_title") + " · " + self.tr_("created_body", folders=result.folders, files=result.files),
            str(result.path), self.tr_("open_folder"), self.tr_("dismiss"))
        self.name_edit.clear()
        self.name_edit.setFocus()

    def _on_failed(self, message: str) -> None:
        self.banner.show_error(self.tr_("err_generic", error="").rstrip(": "), message, self.tr_("dismiss"))

    def _on_worker_finished(self) -> None:
        self.worker = None
        self.create_btn.setText(f"{self.tr_('create')}    Ctrl ↵")
        self._refresh()

    def _open_created(self) -> None:
        if self._last_created:
            open_in_file_manager(self._last_created)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self, self.tr_, self.settings.get("default_path"), self.tr_.lang)
        if dlg.exec():
            path, lang = dlg.values()
            self.settings.set("default_path", path)
            self.settings.save()
            self.path_edit.setText(path)
            if lang != self.tr_.lang:
                self._set_language(lang)

    # ------------------------------------------------- structure editing
    def _commit_layout(self, layout: Layout, select: Lid | None = None, rename: Lid | None = None,
                       message: str = "") -> None:
        if layout == self.layout:
            return
        self._undo = (self._undo + [clone(self.layout)])[-50:]
        self.layout = layout
        self.settings.set("layout", None if layout == default_layout() else layout)
        self.settings.save()
        self._refresh(select=select or rename)
        if message:
            self._flash(message)
        if rename is not None:
            QTimer.singleShot(0, lambda: self.tree.rename_lid(rename))

    def _undo_layout(self) -> None:
        if not self._undo:
            return
        self.layout = self._undo.pop()
        self.settings.set("layout", None if self.layout == default_layout() else self.layout)
        self.settings.save()
        self._refresh()

    def _add_folder(self, parent: Lid | None, after: Lid | None = None) -> None:
        """New folder inside `parent` (None = project root), or right after the sibling `after`."""
        layout = clone(self.layout)
        if after is not None:
            siblings, index = siblings_of(layout, after)
            siblings.insert(index + 1, new_folder(suggest_name(siblings)))
            lid = after[:-1] + (index + 1,)
        else:
            siblings = get_node(layout, parent)["children"] if parent else layout
            siblings.append(new_folder(suggest_name(siblings)))
            lid = (parent or ()) + (len(siblings) - 1,)
        self._commit_layout(layout, rename=lid)

    def _rename_folder(self, lid: Lid, text: str) -> None:
        name = clean_name(text)
        if not name:
            if text.strip():
                self._flash(self.tr_("err_name_invalid", chars=invalid_chars(text)), error=True)
            else:
                self._flash(self.tr_("err_empty"), error=True)
            return
        layout = clone(self.layout)
        node = get_node(layout, lid)
        if node["name"] == name:
            return
        siblings, _ = siblings_of(layout, lid)
        if name_taken(siblings, name, ignore=node):
            self._flash(self.tr_("err_dup", name=name), error=True)
            QTimer.singleShot(0, lambda: self.tree.rename_lid(lid))
            return
        node["name"] = name
        note = self.tr_("renamed_clean", name=name) if name != text.strip() else ""
        self._commit_layout(layout, select=lid, message=note)

    def _delete_folder(self, lid: Lid) -> None:
        layout = clone(self.layout)
        siblings, index = siblings_of(layout, lid)
        node = siblings[index]
        if contains_process(node):
            self._flash(self.tr_("locked_process"), error=True)
            return
        del siblings[index]
        select = lid[:-1] + (index - 1,) if index > 0 else (lid[:-1] or None)
        self._commit_layout(layout, select=select, message=self.tr_("deleted", name=node["name"]))

    def _reset_layout(self) -> None:
        self._commit_layout(default_layout(), message=self.tr_("reset_done"))

    def _tree_menu(self, pos: QPoint) -> None:
        t = self.tr_
        item = self.tree.itemAt(pos)
        if item is not None:
            self.tree.setCurrentItem(item)
        lid = str_to_lid(item.data(0, LID_ROLE)) if item else None

        menu = QMenu(self.tree)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.NoDropShadowWindowHint)
        menu.setToolTipsVisible(True)
        icon = lambda name: svg_icon(name, theme.MUTED, 16)  # noqa: E731

        if lid is not None:
            menu.addAction(icon("subfolder"), t("menu_new_subfolder"), lambda: self._add_folder(lid))
            menu.addAction(icon("plus"), t("menu_new_folder"), lambda: self._add_folder(None, after=lid))
            menu.addSeparator()
            rename = menu.addAction(icon("pencil"), t("menu_rename"), lambda: self.tree.rename_lid(lid))
            rename.setShortcut(QKeySequence("F2"))
            delete = menu.addAction(icon("trash"), t("menu_delete"), lambda: self._delete_folder(lid))
            delete.setShortcut(QKeySequence("Del"))
            if item.data(0, PROCESS_ROLE) or contains_process(get_node(self.layout, lid)):
                delete.setEnabled(False)
                delete.setToolTip(t("locked_process"))
        else:
            if item is not None and item.data(0, LOCK_ROLE):
                info = menu.addAction(svg_icon("lock", theme.SUBTLE, 16), item.data(0, LOCK_ROLE))
                info.setEnabled(False)
                menu.addSeparator()
            menu.addAction(icon("plus"), t("menu_new_folder"), lambda: self._add_folder(None))
        menu.addSeparator()
        undo = menu.addAction(icon("undo"), t("menu_undo"), self._undo_layout)
        undo.setShortcut(QKeySequence.StandardKey.Undo)
        undo.setEnabled(bool(self._undo))
        reset = menu.addAction(icon("reset"), t("menu_reset"), self._reset_layout)
        reset.setEnabled(self.layout != default_layout())
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def _flash(self, text: str, error: bool = False) -> None:
        self.tree_hint.setText(text)
        self.tree_hint.setStyleSheet(f"color: {theme.DANGER if error else theme.MUTED};")
        self._flash_timer.start()

    def _clear_flash(self) -> None:
        self.tree_hint.setText(self.tr_("tree_hint"))
        self.tree_hint.setStyleSheet("")

    # ------------------------------------------------------- drag & drop
    @staticmethod
    def _dropped_dir(event) -> Path | None:
        urls = event.mimeData().urls() if event.mimeData().hasUrls() else []
        for url in urls:
            if url.isLocalFile():
                p = Path(url.toLocalFile())
                return p if p.is_dir() else p.parent
        return None

    def dragEnterEvent(self, event):
        if self._dropped_dir(event):
            event.acceptProposedAction()

    def dropEvent(self, event):
        folder = self._dropped_dir(event)
        if folder:
            self.path_edit.setText(str(folder))
            event.acceptProposedAction()

    # ---------------------------------------------------------- window
    def showEvent(self, e):
        super().showEvent(e)
        theme.dark_title_bar(self)

    def _restore_geometry(self) -> None:
        geo = self.settings.get("window_geometry")
        if geo:
            try:
                self.restoreGeometry(QByteArray.fromBase64(geo.encode()))
                return
            except Exception:
                pass
        screen = QApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            self.move(area.center() - self.rect().center())

    def closeEvent(self, e):
        if self.worker and self.worker.isRunning():
            self.worker.wait(5000)
        self.settings.set("window_geometry", bytes(self.saveGeometry().toBase64()).decode())
        self.settings.save()
        super().closeEvent(e)
