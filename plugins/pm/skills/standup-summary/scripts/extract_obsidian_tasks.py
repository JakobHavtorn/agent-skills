#!/usr/bin/env python3
"""Extract open tasks from an Obsidian vault using the Tasks plugin syntax.

Scans .md files in the vault for `- [ ]` checkbox lines, parses Tasks plugin
metadata (due dates, priority, recurrence, done dates), and prints a compact
listing grouped by note. Completed tasks are excluded by default; pass
--include-completed to include them (useful for recently-done items).

Usage:
  extract_obsidian_tasks.py <vault-path>
  extract_obsidian_tasks.py <vault-path> --include-completed

Output is grouped by note path, with one task per line:
  note/path.md: Task text | 📅 2026-10-25 | [high] | 🔁 every day

Exits 0 even if no tasks are found (empty vault is not an error).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Tasks plugin emoji metadata
DUE_DATE_RE = re.compile(r"📅\s*(\d{4}-\d{2}-\d{2})")
START_DATE_RE = re.compile(r"🛫\s*(\d{4}-\d{2}-\d{2})")
SCHEDULED_RE = re.compile(r"⏳\s*(\d{4}-\d{2}-\d{2})")
DONE_DATE_RE = re.compile(r"✅\s*(\d{4}-\d{2}-\d{2})")
CREATED_DATE_RE = re.compile(r"➕\s*(\d{4}-\d{2}-\d{2})")
RECURRENCE_RE = re.compile(r"🔁\s+(.+?)(?:\s+📅|\s+🛫|\s+⏳|\s+✅|\s+➕|$)")

PRIORITY_EMOJI = {"⏫": "high", "🔼": "medium", "🔽": "low"}

# Directories to skip during vault scan
SKIP_DIRS = {".obsidian", ".trash", "templates", "node_modules", ".git"}

# Task line patterns
TASK_OPEN_RE = re.compile(r"^(\s*)- \[ \]\s+(.+)$")
TASK_DONE_RE = re.compile(r"^(\s*)- \[x\]\s+(.+)$", re.IGNORECASE)


def parse_task_line(line: str) -> dict | None:
    """Parse a markdown task line, returning a dict or None if not a task."""
    m = TASK_OPEN_RE.match(line) or TASK_DONE_RE.match(line)
    if not m:
        return None

    indent = len(m.group(1))
    raw = m.group(2)
    is_done = bool(TASK_DONE_RE.match(line))

    # Extract metadata
    due = DUE_DATE_RE.search(raw)
    done = DONE_DATE_RE.search(raw)
    priority = None
    for emoji, level in PRIORITY_EMOJI.items():
        if emoji in raw:
            priority = level
            break
    recurrence = RECURRENCE_RE.search(raw)

    # Clean text — strip all emoji metadata for display
    text = raw
    for pattern in [
        DUE_DATE_RE,
        START_DATE_RE,
        SCHEDULED_RE,
        DONE_DATE_RE,
        CREATED_DATE_RE,
        RECURRENCE_RE,
    ]:
        text = pattern.sub("", text)
    for emoji in PRIORITY_EMOJI:
        text = text.replace(emoji, "")
    text = text.strip()

    return {
        "text": text,
        "due": due.group(1) if due else None,
        "done_date": done.group(1) if done else None,
        "priority": priority,
        "recurrence": recurrence.group(1).strip() if recurrence else None,
        "indent": indent,
        "is_done": is_done,
    }


def scan_vault(vault_path: str, include_completed: bool = False) -> list[dict]:
    """Walk the vault for .md files and extract tasks."""
    vault = Path(vault_path)
    if not vault.is_dir():
        print(f"error: vault not found: {vault}", file=sys.stderr)
        sys.exit(1)

    tasks: list[dict] = []

    for md_file in vault.rglob("*.md"):
        # Skip excluded directories
        if any(part in SKIP_DIRS for part in md_file.parts):
            continue
        # Skip the Task dashboard itself — it's a query view, not a task source
        if md_file.name == "Task dashboard.md":
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for line in content.splitlines():
            task = parse_task_line(line)
            if task is None:
                continue
            if task["is_done"] and not include_completed:
                continue
            task["file"] = str(md_file.relative_to(vault))
            tasks.append(task)

    return tasks


def format_task(task: dict) -> str:
    """Format a single task for compact output."""
    parts = [task["text"]]
    if task["due"]:
        parts.append(f"📅 {task['due']}")
    if task["priority"]:
        parts.append(f"[{task['priority']}]")
    if task["recurrence"]:
        parts.append(f"🔁 {task['recurrence']}")
    if task["is_done"] and task["done_date"]:
        parts.append(f"✅ {task['done_date']}")

    indent = "  " * (task["indent"] // 2)
    file_note = task["file"]
    return f"{indent}{file_note}: {' | '.join(parts)}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vault_path", help="Path to the Obsidian vault root")
    parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Include completed tasks (useful for recently-done items).",
    )
    args = parser.parse_args()

    tasks = scan_vault(args.vault_path, args.include_completed)

    # Sort by due date (overdue/dated first), then undated
    def sort_key(t: dict) -> tuple:
        if t["due"]:
            return (0, t["due"])
        return (1, t["file"])

    tasks.sort(key=sort_key)

    # Group by file for readability
    by_file: dict[str, list[dict]] = defaultdict(list)
    for t in tasks:
        by_file[t["file"]].append(t)

    for file_path in sorted(by_file):
        print(f"=== {file_path} ===")
        for t in by_file[file_path]:
            print(format_task(t))
        print()

    total = len(tasks)
    open_count = sum(1 for t in tasks if not t["is_done"])
    done_count = total - open_count
    print(
        f"(Total: {total} task(s) — {open_count} open, {done_count} done — across {len(by_file)} note(s))",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
