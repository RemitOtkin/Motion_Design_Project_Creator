"""The one place the project layout is defined.

The folder layout is plain data (a list of dicts) so the user can edit it in the
preview and have it saved. Tool folders and files are not part of the saved
layout: they are generated into the "process" folder from the tool selection.

The preview tree, the folders written to disk and the README are all built from
`build_plan()`, so they can't drift apart.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Sequence


@dataclass(frozen=True)
class Tool:
    id: str
    label: str
    folder: str      # subfolder inside the process folder
    ext: str         # template / project file extension
    icon: str        # file in resources/icons
    mono: str        # short label used when the icon is missing


TOOLS: tuple[Tool, ...] = (
    Tool("ae", "After Effects", "AE", ".aep", "after_effects.png", "Ae"),
    Tool("c4d", "Cinema 4D", "C4D", ".c4d", "cinema4d.png", "C4D"),
    Tool("pr", "Premiere Pro", "PR", ".prproj", "premiere_pro.png", "Pr"),
    Tool("houdini", "Houdini", "HOUDINI", ".hip", "houdini.png", "Hou"),
    Tool("blender", "Blender", "BLENDER", ".blend", "blender.png", "Bl"),
)
TOOLS_BY_ID = {t.id: t for t in TOOLS}

FIRST_VERSION = "v001"

# The default layout: (name, note key, children). The folder flagged as
# process receives the tool folders.
PROCESS_FOLDER = "02_PROCESS"
_DEFAULT: list[tuple[str, str, list]] = [
    ("01_IN", "n_in", [
        ("FOOTAGES", "n_footages", []),
        ("SFX", "n_sfx", []),
        ("FONTS", "n_fonts", []),
        ("ASSETS", "n_assets", []),
    ]),
    (PROCESS_FOLDER, "n_process", []),
    ("03_RENDER", "n_render", []),
    ("04_OUT", "n_out", [
        ("01_PREVIEW", "n_preview", []),
        ("02_STILLSHOTS", "n_stillshots", []),
        ("03_ANIMATIC", "n_animatic", []),
        ("04_MASTER", "n_master", []),
    ]),
]

# A layout is a list of folder dicts:
#   {"name": str, "note_key": str | None, "process": bool, "children": [...]}
Layout = list[dict[str, Any]]
Lid = tuple[int, ...]   # path of indices into a layout, e.g. (3, 1) = 04_OUT/02_STILLSHOTS


def default_layout() -> Layout:
    def conv(spec) -> dict:
        name, note_key, children = spec
        return {"name": name, "note_key": note_key, "process": name == PROCESS_FOLDER,
                "children": [conv(c) for c in children]}
    return [conv(s) for s in _DEFAULT]


def sanitize_layout(data: Any) -> Layout:
    """Validate a layout loaded from settings; fall back to the default if it is unusable."""
    def conv(item) -> dict | None:
        if not isinstance(item, dict):
            return None
        name = clean_name(str(item.get("name", "")))
        if not name:
            return None
        children = [c for c in (conv(x) for x in item.get("children") or []) if c]
        note_key = item.get("note_key")
        return {"name": name, "note_key": note_key if isinstance(note_key, str) else None,
                "process": bool(item.get("process")), "children": children}

    if not isinstance(data, list):
        return default_layout()
    layout = [c for c in (conv(x) for x in data) if c]
    flagged = [n for n in iter_layout(layout) if n["process"]]
    if not layout or len(flagged) != 1:
        return default_layout()
    return layout


def iter_layout(layout: Layout) -> Iterator[dict]:
    for node in layout:
        yield node
        yield from iter_layout(node["children"])


def get_node(layout: Layout, lid: Lid) -> dict:
    siblings, index = siblings_of(layout, lid)
    return siblings[index]


def siblings_of(layout: Layout, lid: Lid) -> tuple[list, int]:
    """The list that holds the node at `lid`, and the node's index in it."""
    siblings = layout
    for i in lid[:-1]:
        siblings = siblings[i]["children"]
    return siblings, lid[-1]


def contains_process(node: dict) -> bool:
    return any(n["process"] for n in iter_layout([node]))


def name_taken(siblings: list, name: str, ignore: dict | None = None) -> bool:
    """Windows names are case-insensitive, so compare that way."""
    low = name.lower()
    return any(s is not ignore and s["name"].lower() == low for s in siblings)


def suggest_name(siblings: list, base: str = "NEW_FOLDER") -> str:
    """Continue a numbered sequence (01_, 02_ … → 05_NEW_FOLDER) and avoid duplicates."""
    numbers = [int(m.group(1)) for s in siblings if (m := re.match(r"^(\d{2})_", s["name"]))]
    if siblings and len(numbers) == len(siblings):
        base = f"{max(numbers) + 1:02d}_{base}"
    name, n = base, 2
    while name_taken(siblings, name):
        name, n = f"{base}_{n}", n + 1
    return name


def new_folder(name: str) -> dict:
    return {"name": name, "note_key": None, "process": False, "children": []}


def clone(layout: Layout) -> Layout:
    return copy.deepcopy(layout)


@dataclass
class Node:
    name: str
    kind: str                      # "folder" | "file" | "placeholder"
    note: str = ""
    tool: str | None = None        # set when the node exists because of a tool
    template: str | None = None    # for tool files: extension of the template to copy
    lid: Lid | None = None         # position in the editable layout (None = generated)
    process: bool = False
    children: list["Node"] = field(default_factory=list)

    def walk(self, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], "Node"]]:
        path = prefix + (self.name,)
        yield path, self
        for child in self.children:
            yield from child.walk(path)


# Windows forbids these in file and folder names (plus control characters).
_INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def invalid_chars(name: str) -> str:
    """The distinct forbidden characters found in `name`, for messages."""
    seen = []
    for ch in _INVALID.findall(name):
        shown = ch if ch.isprintable() else repr(ch)
        if shown not in seen:
            seen.append(shown)
    return " ".join(seen)


def clean_name(name: str) -> str:
    """The folder name that will actually be used on disk."""
    out = _INVALID.sub("", name).strip().rstrip(". ")
    out = re.sub(r"\s{2,}", " ", out)
    if out.upper() in _RESERVED:
        out = f"{out}_"
    return out


def versioned_filename(project_name: str, tool: Tool) -> str:
    return f"{project_name}_{FIRST_VERSION}{tool.ext}"


def build_plan(project_name: str, tool_ids: Sequence[str], tr: Callable[..., str],
               layout: Layout | None = None) -> Node:
    """Return the full tree for a project: folders, tool files and the README."""
    layout = layout if layout is not None else default_layout()
    selected = [t for t in TOOLS if t.id in set(tool_ids)]

    def make(spec: dict, lid: Lid) -> Node:
        note = tr(spec["note_key"]) if spec.get("note_key") else ""
        node = Node(spec["name"], "folder", note, lid=lid, process=spec["process"],
                    children=[make(c, lid + (i,)) for i, c in enumerate(spec["children"])])
        if spec["process"]:
            for tool in selected:
                node.children.append(Node(
                    tool.folder, "folder", tr("n_tool", tool=tool.label), tool=tool.id,
                    children=[Node(versioned_filename(project_name, tool), "file",
                                   tool=tool.id, template=tool.ext)],
                ))
            if not selected and not spec["children"]:
                node.children.append(Node(tr("empty_process"), "placeholder", tr("empty_process_note")))
        return node

    root = Node(project_name, "folder", children=[make(s, (i,)) for i, s in enumerate(layout)])
    root.children.append(Node("README.md", "file", tr("n_readme")))
    return root


def count(plan: Node) -> tuple[int, int]:
    """(folders, files) in the plan, including the project folder itself."""
    folders = files = 0
    for _, node in plan.walk():
        if node.kind == "folder":
            folders += 1
        elif node.kind == "file":
            files += 1
    return folders, files
