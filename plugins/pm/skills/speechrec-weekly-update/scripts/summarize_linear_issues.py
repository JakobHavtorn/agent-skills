#!/usr/bin/env python3
"""Summarize a harness-spilled Linear `list_issues` JSON dump.

Groups issues into Recently Completed (last N days), In Progress, and In Review,
printing one line per issue. Tolerates the variable shapes that the Linear MCP
returns (e.g. `project`/`status` may be a string, a dict, or null).

Usage: summarize_linear_issues.py <json-file> [--days N]
"""

import json
import sys
from datetime import datetime, timedelta, timezone


def parse_args():
    args = sys.argv[1:]
    if not args:
        print(f"usage: {sys.argv[0]} <json-file> [--days N]", file=sys.stderr)
        sys.exit(2)
    path = args[0]
    days = 7
    if len(args) >= 3 and args[1] == "--days":
        days = int(args[2])
    return path, days


def field_name(value):
    if isinstance(value, dict):
        return value.get("name", "") or ""
    if isinstance(value, str):
        return value
    return ""


def main():
    path, days = parse_args()
    with open(path) as f:
        outer = json.load(f)
    # Harness spill shape: [{"type": "...", "text": "<inner-json-string>"}]
    if isinstance(outer, list) and outer and isinstance(outer[0], dict) and "text" in outer[0]:
        inner = json.loads(outer[0]["text"])
    else:
        inner = outer
    issues = inner.get("issues", [])
    issues.sort(key=lambda i: i.get("updatedAt", ""), reverse=True)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    def fmt(i):
        ident = i.get("id", "") or ""
        title = (i.get("title", "") or "")[:88]
        updated = (i.get("updatedAt", "") or "")[:10]
        status = field_name(i.get("status"))
        project = field_name(i.get("project"))
        return f"{updated} {status[:14]:14} {ident:10} {title}  [{project[:38]}]"

    def section(title, predicate):
        rows = [fmt(i) for i in issues if predicate(i)]
        if not rows:
            return
        print(f"=== {title} ({len(rows)}) ===")
        for r in rows:
            print(r)
        print()

    section(
        f"RECENTLY COMPLETED (last {days} days)",
        lambda i: (i.get("completedAt") or "") > cutoff,
    )
    section(
        "IN PROGRESS",
        lambda i: i.get("statusType") == "started" and "review" not in field_name(i.get("status")).lower(),
    )
    section(
        "IN REVIEW",
        lambda i: "review" in field_name(i.get("status")).lower(),
    )
    print(f"(Total issues in dump: {len(issues)})")


if __name__ == "__main__":
    main()
