"""Writes a planned project to disk. No Qt in here, so it is easy to test."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence

from .structure import TOOLS_BY_ID, Node, count
from .version import __version__


class CreateError(Exception):
    """A problem worth showing to the user as-is."""


@dataclass
class CreateResult:
    path: Path
    folders: int
    files: int


def find_template(templates_dir: Path, ext: str) -> Path | None:
    """First template with this extension (template.aep, MyStartScene.aep, …)."""
    matches = sorted(p for p in templates_dir.glob(f"*{ext}") if p.is_file())
    return matches[0] if matches else None


def missing_templates(templates_dir: Path, tool_ids: Sequence[str]) -> list[str]:
    missing = []
    for tool_id in tool_ids:
        tool = TOOLS_BY_ID[tool_id]
        if find_template(templates_dir, tool.ext) is None:
            missing.append(f"{tool.label} ({tool.ext})")
    return missing


def create_project(base_dir: Path, plan: Node, tool_ids: Sequence[str],
                   templates_dir: Path, tr: Callable[..., str]) -> CreateResult:
    base_dir = Path(base_dir)
    if not base_dir.is_dir():
        raise CreateError(tr("err_path_missing"))

    project_dir = base_dir / plan.name
    if project_dir.exists():
        raise CreateError(tr("err_exists"))

    missing = missing_templates(templates_dir, tool_ids)
    if missing:
        raise CreateError(tr("err_templates", tools=", ".join(missing)))

    project_dir.mkdir()
    try:
        for rel, node in plan.walk():
            target = base_dir.joinpath(*rel)
            if node.kind == "folder":
                target.mkdir(exist_ok=True)
            elif node.kind == "file" and node.template:
                shutil.copy2(find_template(templates_dir, node.template), target)
        (project_dir / "README.md").write_text(render_readme(plan, tool_ids, tr), encoding="utf-8")
    except Exception as exc:
        # Don't leave a half-built project behind.
        shutil.rmtree(project_dir, ignore_errors=True)
        raise CreateError(tr("err_generic", error=exc)) from exc

    folders, files = count(plan)
    return CreateResult(project_dir, folders, files)


def render_readme(plan: Node, tool_ids: Sequence[str], tr: Callable[..., str]) -> str:
    lines = [f"# {plan.name}", "", f"## {tr('readme_structure')}", "", "```"]

    def tree(node: Node, prefix: str = "") -> None:
        kids = [c for c in node.children if c.kind != "placeholder"]
        for i, child in enumerate(kids):
            last = i == len(kids) - 1
            label = child.name + ("/" if child.kind == "folder" else "")
            note = f"  # {child.note}" if child.note else ""
            lines.append(f"{prefix}{'└── ' if last else '├── '}{label}{note}")
            tree(child, prefix + ("    " if last else "│   "))

    lines.append(f"{plan.name}/")
    tree(plan)
    tools = ", ".join(TOOLS_BY_ID[t].label for t in tool_ids) or tr("readme_no_tools")
    lines += [
        "```",
        "",
        f"## {tr('readme_info')}",
        "",
        f"- **{tr('readme_created')}:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **{tr('readme_tools')}:** {tools}",
        "",
        "---",
        tr("readme_footer", version=__version__),
        "",
    ]
    return "\n".join(lines)
