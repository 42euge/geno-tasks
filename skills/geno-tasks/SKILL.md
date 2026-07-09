---
name: geno-tasks
description: >-
  Node-linked task manager for the geno ecosystem. Manages tasks tied to
  object-notation registry nodes, with LLM wiki synthesis and pluggable
  issue provider integration.
allowed-tools: "Bash(geno-tasks *)"
metadata:
  author: 42euge
  version: "0.1.0"
---

# geno-tasks

Tasks live in `~/.geno/tasks/<node>.md` — one file per registry node.

```
geno-tasks ls                      List all tasks
geno-tasks add <node>              Create/open a task for a node
geno-tasks note <node> <text>      Append a timestamped note
geno-tasks done <node>             Mark done
geno-tasks sync                    Pull from registered issue providers
geno-tasks wiki [--node <path>]    LLM synthesis → ~/.geno/tasks/.wiki/
geno-tasks watch                   Watch overview.md; reconcile edits via LLM
geno-tasks deploy                  Build static site and publish
```

## Skills

| Skill | Slash command |
|---|---|
| `geno-tasks` | umbrella |
| `geno-tasks-watch` | `/geno-tasks-watch` |

## Issue providers

Enterprise integrations (Jira, Linear, GitHub Issues) are registered in
`~/.geno/settings.json` under `tasks.providers` and implement the
`geno_tasks.provider.IssueProvider` interface. Install via `geno-tools install`.
