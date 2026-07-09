# geno-tasks

Node-linked task manager + LLM wiki synthesis for the geno ecosystem.

## Concept

Tasks are markdown files in `~/.geno/tasks/`, one per object-notation registry
node. The same namespace that `geno-vault` uses for iTerm tabs and Chrome groups
now also tracks what you're working on in each context.

```
~/.geno/tasks/
  project.area.md           ← task note for that registry node
  project.area.feature.md

  .wiki/                  ← LLM-synthesized pages
    project.area.md
```

## Install

```bash
brew tap 42euge/geno && brew install geno
# or:
pipx install git+https://github.com/42euge/geno-tasks.git
```

## Usage

```bash
geno-tasks ls                          # list all tasks
geno-tasks add project.area.feature    # create/open a task
geno-tasks note project.area.feature "resolved the config issue"
geno-tasks done project.area.feature
geno-tasks sync                        # pull from issue providers
geno-tasks wiki                        # LLM synthesis → .wiki/
```

## Issue providers

Connect any issue tracker by implementing `geno_tasks.provider.IssueProvider`
and registering it in `~/.geno/settings.json`:

```json
{
  "tasks": {
    "providers": [
      {
        "module": "your_plugin.provider",
        "class": "YourProvider",
        "config": {}
      }
    ]
  }
}
```

Enterprise plugins install via `geno-tools install` from a private namespace.
