"""Canonical paths for geno-tasks state.

Mirrors the old euge-tasks vault layout:
  workflow/active/PROJECT/KEY.md
  workflow/inbox/PROJECT/KEY.md
  workflow/done/PROJECT/KEY.md
  workflow/next/PROJECT/KEY.md
  projects/name.md
  ITS/assigned/  ITS/reported/
  .wiki/
"""

from pathlib import Path

TASKS_DIR     = Path.home() / ".geno" / "tasks"
WIKI_DIR      = TASKS_DIR / ".wiki"
WORKFLOW_DIR  = TASKS_DIR / "workflow"
ACTIVE_DIR    = WORKFLOW_DIR / "active"
INBOX_DIR     = WORKFLOW_DIR / "inbox"
DONE_DIR      = WORKFLOW_DIR / "done"
NEXT_DIR      = WORKFLOW_DIR / "next"
PROJECTS_DIR  = TASKS_DIR / "projects"
ITS_DIR       = TASKS_DIR / "ITS"

_STATUS_DIR = {
    "active": ACTIVE_DIR,
    "done":   DONE_DIR,
    "inbox":  INBOX_DIR,
    "next":   NEXT_DIR,
}


def task_file(node: str, status: str = "inbox", source: str = "jira") -> Path:
    """Resolve the canonical path for a task file.

    Jira tickets:  workflow/<status>/<PROJECT>/<KEY>.md
    Projects:      projects/<name>.md
    """
    if source == "project" or node.startswith("project."):
        return PROJECTS_DIR / f"{node}.md"
    folder = _STATUS_DIR.get(status, INBOX_DIR)
    # node is dot-notation (ngnet.4611) but filename should be NGNET-4611.md
    ticket_id = _node_to_ticket(node)
    project = ticket_id.split("-")[0].upper() if "-" in ticket_id else "OTHER"
    return folder / project / f"{ticket_id}.md"


def find_task_file(node: str) -> Path | None:
    """Search all subdirectories for an existing task file by node name or ticket id."""
    ticket_id = _node_to_ticket(node)
    # Search by filename
    for p in TASKS_DIR.rglob(f"{ticket_id}.md"):
        if ".wiki" not in str(p):
            return p
    # Fallback: search by node in frontmatter would be slow; try dot-notation filename too
    for p in TASKS_DIR.rglob(f"{node}.md"):
        if ".wiki" not in str(p):
            return p
    return None


def _node_to_ticket(node: str) -> str:
    """Convert dot-notation node (ngnet.4611) back to Jira key (NGNET-4611)."""
    parts = node.upper().split(".")
    if len(parts) == 2 and parts[1].isdigit():
        return f"{parts[0]}-{parts[1]}"
    # Already looks like a ticket key or project name
    return node


def ensure_dirs() -> None:
    for d in [ACTIVE_DIR, INBOX_DIR, DONE_DIR, NEXT_DIR, PROJECTS_DIR, WIKI_DIR,
              ITS_DIR / "assigned", ITS_DIR / "reported"]:
        d.mkdir(parents=True, exist_ok=True)
