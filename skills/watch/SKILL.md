---
name: geno-tasks-watch
description: >-
  Launch a geno-tasks watch session — monitors overview.md for freeform
  edits in Obsidian and reconciles changes with task files via geno-pear's
  mtime-poll loop + LLM. Use when the user says /geno-tasks-watch or wants
  to start editing their task overview and have it sync automatically.
allowed-tools: "Bash(geno-tasks *) Bash(tt *)"
metadata:
  author: 42euge
  version: "0.1.0"
---

# geno-tasks-watch

Starts the geno-tasks overview watcher in a new iTerm tab so you can edit
`~/.geno/tasks/overview/overview.md` in Obsidian and have changes reconciled
with your task files in real time.

## When to invoke

- User says `/geno-tasks-watch`
- User wants to start their task editing session
- User opens the Obsidian tasks vault and wants AI reconciliation active

## Workflow

### 1. Open the overview in Obsidian

```bash
open -a Obsidian ~/.geno/tasks/overview/overview.md
```

### 2. Launch the watcher in a named iTerm tab

```bash
tt iterm tab geno.tasks.watch --cmd "geno-tasks watch"
```

This creates a tab named `geno.tasks.watch` running `geno-tasks watch`,
which polls `overview.md` every second. The vault daemon picks up the new
tab automatically and registers it.

### 3. Confirm to the user

Tell the user:
- Obsidian is opening `overview/overview.md`
- The watcher is running in the `geno.tasks.watch` iTerm tab
- Every time they save the file, the LLM will reconcile edits with task files
- They can check the watcher tab to see what actions were taken

## Don'ts

- Don't run `geno-tasks watch` in the current session — it blocks. Always fork to a new tab.
- Don't open the raw task files — direct the user to `overview.md` as the editing surface.
