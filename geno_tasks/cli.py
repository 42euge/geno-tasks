#!/usr/bin/env python3
"""geno-tasks — node-linked task manager for the geno ecosystem."""

import argparse
import sys
from pathlib import Path

from . import __version__


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:]) if argv is None else list(argv)

    parser = argparse.ArgumentParser(prog="geno-tasks")
    parser.add_argument("--version", action="version", version=f"geno-tasks {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ls — list all tasks
    p_ls = sub.add_parser("ls", help="list tasks (optionally filter by status)")
    p_ls.add_argument("--status", default=None, help="filter by status (active, done, …)")

    # add — create or open a task for a node
    p_add = sub.add_parser("add", help="create a task for a registry node")
    p_add.add_argument("node", help="dot-notation node path (e.g. project.area.feature)")
    p_add.add_argument("--title", default="", help="short task title")
    p_add.add_argument("--status", default="active")

    # note — append a timestamped note
    p_note = sub.add_parser("note", help="append a note to a node's task")
    p_note.add_argument("node")
    p_note.add_argument("text", nargs=argparse.REMAINDER, help="note text")

    # done — mark a task done
    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("node")

    # sync — pull from registered issue providers
    sub.add_parser("sync", help="sync tasks from registered issue providers (e.g. Jira)")

    # wiki — LLM synthesis pass over all tasks
    p_wiki = sub.add_parser("wiki", help="run LLM synthesis to generate/update wiki pages")
    p_wiki.add_argument("--node", default=None, help="synthesize a specific node only")

    # watch — watch overview.md for edits, reconcile with task files via LLM
    p_watch = sub.add_parser("watch", help="watch overview/overview.md; reconcile edits with task files")
    p_watch.add_argument("--file", default=None, help="file to watch (default: ~/.geno/tasks/overview/overview.md)")
    p_watch.add_argument("--interval", type=float, default=1.0, help="poll interval in seconds (default: 1.0)")

    # deploy — build + publish via configured DeployAdapter
    p_deploy = sub.add_parser("deploy", help="build static site and publish via deploy adapter")
    p_deploy.add_argument("--build-only", action="store_true", help="build but do not publish")
    p_deploy.add_argument("--output", default=None, help="output directory (default: ~/.geno/tasks/public)")

    args = parser.parse_args(argv)

    from . import tasks, paths

    _BOLD  = "\033[1m"
    _DIM   = "\033[2m"
    _GREEN = "\033[32m"
    _RESET = "\033[0m"

    if args.cmd == "ls":
        items = tasks.list_tasks(status=args.status)
        if not items:
            print(f"{_DIM}no tasks{_RESET}")
            return 0
        for t in items:
            status = t.get("status", "?")
            color = _GREEN if status == "done" else _BOLD
            print(f"  {color}{t['node']:<40}{_RESET} {_DIM}{status}{_RESET}")
        print(f"\n{_DIM}{len(items)} task(s) in {paths.TASKS_DIR}{_RESET}")

    elif args.cmd == "add":
        d = tasks.load(args.node)
        if not d["meta"].get("title") and args.title:
            d["meta"]["title"] = args.title
        d["meta"].setdefault("status", args.status)
        tasks.save(args.node, d["meta"], d["body"] or f"# {args.node}\n\n")
        print(f"task: {args.node}")
        print(f"{_DIM}{paths.task_file(args.node)}{_RESET}")

    elif args.cmd == "note":
        text = " ".join(args.text).strip()
        if not text:
            raise SystemExit("Usage: geno-tasks note <node> <text>")
        tasks.add_note(args.node, text)
        print(f"noted → {args.node}")

    elif args.cmd == "done":
        tasks.set_status(args.node, "done")
        print(f"{_GREEN}done{_RESET} → {args.node}")

    elif args.cmd == "sync":
        from .provider import load_providers
        providers = load_providers()
        if not providers:
            print(f"{_DIM}no providers configured. Add to ~/.geno/settings.json under tasks.providers{_RESET}")
            return 0
        for p in providers:
            print(f"syncing {p.name}…")
            try:
                assigned = p.list_assigned()
                for issue in assigned:
                    node = issue.get("node") or issue.get("id", "unknown")
                    d = tasks.load(node)
                    d["meta"].update(issue)
                    tasks.save(node, d["meta"], d["body"] or f"# {node}\n\n")
                print(f"  {len(assigned)} issue(s) synced from {p.name}")
            except Exception as e:
                print(f"  error from {p.name}: {e}")

    elif args.cmd == "wiki":
        import shutil, subprocess as _sp
        if not shutil.which("geno-tools"):
            raise SystemExit("geno-tools not found — needed for LLM synthesis")
        items = tasks.list_tasks()
        if args.node:
            items = [t for t in items if t["node"] == args.node]
        paths.ensure_dirs()
        for t in items:
            node = t["node"]
            d = tasks.load(node)
            context = f"node: {node}\nstatus: {t.get('status','?')}\n{d['body'][:800]}"
            r = _sp.run(
                ["geno-tools", "llm", "suggest", "--cwd", node, "--title", context[:120]],
                capture_output=True, text=True, timeout=20,
            )
            synthesis = r.stdout.strip()
            if synthesis:
                wiki_page = paths.WIKI_DIR / f"{node}.md"
                wiki_page.write_text(f"# {node}\n\n{synthesis}\n")
                print(f"  wiki: {node}")
        print(f"wiki pages → {paths.WIKI_DIR}")

    elif args.cmd == "watch":
        watch_file = Path(args.file) if args.file else paths.TASKS_DIR / "overview" / "overview.md"
        if not watch_file.exists():
            watch_file.parent.mkdir(parents=True, exist_ok=True)
            watch_file.write_text("# Work Overview\n\nEdit freely.\n"
                                  "Draft: `///command`   Commit: `////` or `////command`\n")
        print(f"watching {watch_file}  (Ctrl-C to stop)")
        print(f"  draft: ///command   commit: ////  or  ////command")

        try:
            from geno_pear.commands import check_commit
            _use_pear_commands = True
        except ImportError:
            _use_pear_commands = False

        def on_change(p):
            if _use_pear_commands:
                check_commit(p, log=print)

        try:
            from geno_pear import watch as pear_watch
            pear_watch(str(watch_file), on_change, interval=args.interval)
        except ImportError:
            import time as _t
            last = watch_file.stat().st_mtime
            while True:
                _t.sleep(args.interval)
                cur = watch_file.stat().st_mtime if watch_file.exists() else last
                if cur != last:
                    last = cur
                    on_change(str(watch_file))

    elif args.cmd == "deploy":
        from .deploy import load_adapter
        adapter = load_adapter()
        if not adapter:
            raise SystemExit(
                "No deploy adapter configured.\n"
                "Add tasks.deploy_adapter to ~/.geno/settings.json."
            )
        output_dir = Path(args.output) if args.output else paths.TASKS_DIR / "public"
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"building → {output_dir}")
        adapter.build(paths.TASKS_DIR, output_dir)
        print(f"built {sum(1 for _ in output_dir.rglob('*'))} file(s)")
        if not args.build_only:
            adapter.publish(output_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
