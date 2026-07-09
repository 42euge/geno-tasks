"""Core task file read/write — pure stdlib, no external deps."""

from __future__ import annotations

import re
import time
from pathlib import Path

from .paths import TASKS_DIR, task_file, find_task_file, ensure_dirs

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        import yaml
        return yaml.safe_load(m.group(1)) or {}
    except ImportError:
        pass
    except Exception:
        return {}
    # Fallback: simple key: value regex
    result = {}
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w[\w.-]*):\s*(.*)', line)
        if kv:
            k, v = kv.group(1), kv.group(2).strip().strip("'\"")
            result[k] = v
    return result


def _render_frontmatter(meta: dict) -> str:
    try:
        import yaml
        return "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True) + "---\n"
    except Exception:
        lines = ["---"]
        for k, v in meta.items():
            lines.append(f"{k}: {v!r}")
        lines.append("---")
        return "\n".join(lines) + "\n"


def load(node: str) -> dict:
    """Return {meta: dict, body: str} for a task file, searching all subdirs."""
    p = find_task_file(node)
    if not p or not p.exists():
        return {"meta": {"node": node, "created": time.strftime("%Y-%m-%d")}, "body": ""}
    text = p.read_text(encoding="utf-8", errors="replace")
    meta = _parse_frontmatter(text)
    body = _FRONTMATTER_RE.sub("", text, count=1)
    return {"meta": meta, "body": body}


def save(node: str, meta: dict, body: str) -> None:
    """Save a task file, placing it in the correct subfolder based on status/source."""
    ensure_dirs()
    status = meta.get("status", "inbox")
    source = meta.get("source", "jira")
    # If file already exists somewhere, update it in place
    existing = find_task_file(node)
    dest = existing if existing else task_file(node, status=status, source=source)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_render_frontmatter(meta) + body, encoding="utf-8")
    # Move to correct folder if status changed
    correct = task_file(node, status=status, source=source)
    if dest != correct and dest.exists():
        correct.parent.mkdir(parents=True, exist_ok=True)
        dest.rename(correct)


def add_note(node: str, note: str) -> None:
    """Append a timestamped note to a task file."""
    d = load(node)
    ts = time.strftime("%Y-%m-%d %H:%M")
    d["body"] = d["body"].rstrip() + f"\n\n- **{ts}** {note}\n"
    save(node, d["meta"], d["body"])


def set_status(node: str, status: str) -> None:
    """Update status and move the file to the matching folder."""
    d = load(node)
    old_path = find_task_file(node)
    d["meta"]["status"] = status
    d["meta"]["updated"] = time.strftime("%Y-%m-%d")
    save(node, d["meta"], d["body"])


def list_tasks(status: str | None = None) -> list[dict]:
    """Return all task files from all subdirs, optionally filtered by status."""
    ensure_dirs()
    out = []
    for p in sorted(TASKS_DIR.rglob("*.md")):
        if ".wiki" in str(p):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        meta = _parse_frontmatter(text)
        node = meta.get("node", p.stem)
        if status and meta.get("status") != status:
            continue
        out.append({"node": node, "path": str(p.relative_to(TASKS_DIR)), **meta})
    return out
