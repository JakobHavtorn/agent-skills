#!/usr/bin/env python3
"""Parse a Slack MCP overflow dump into a compact, context-friendly listing.

When `slack_search_public_and_private` returns too much text, the MCP harness
writes the raw tool result to a file and hands the path back instead of the
content. The file is a JSON array of `{type, text}` parts; the `text` field
is itself a JSON string with a `results` block formatted for humans.

This script extracts the results block, splits it into individual messages,
and prints one compact line per message so the agent can read the whole
window without re-blowing the context budget.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MESSAGE_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)


def load_results_text(path: Path) -> str:
    """Return the human-readable `results` blob from the overflow file."""
    raw = path.read_text()
    parts = json.loads(raw)
    chunks: list[str] = []
    for part in parts:
        text = part.get("text", "")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            chunks.append(text)
            continue
        chunks.append(payload.get("results", text))
    return "\n".join(chunks)


def parse_message(block: str) -> dict[str, str] | None:
    """Extract the fields we care about from one `### Result` block."""
    if "### Result" not in block:
        return None
    fields: dict[str, str] = {"is_bot": "false"}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("Channel:"):
            fields["channel"] = line.split(":", 1)[1].strip()
        elif line.startswith("From:"):
            value = line.split(":", 1)[1].strip()
            fields["from"] = value
            if "[BOT]" in value:
                fields["is_bot"] = "true"
        elif line.startswith("Time:"):
            fields["time"] = line.split(":", 1)[1].strip()
        elif line.startswith("Permalink:"):
            match = re.search(r"\((https?://[^)]+)\)", line)
            if match:
                fields["permalink"] = match.group(1)
        elif line.startswith("Text:"):
            text_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith(
                ("Context before:", "Context after:", "### Result")
            ):
                text_lines.append(lines[i])
                i += 1
            fields["text"] = "\n".join(text_lines).strip()
            continue
        i += 1
    return fields if "time" in fields else None


def format_message(msg: dict[str, str], max_text: int) -> str:
    time = msg.get("time", "?")
    channel = msg.get("channel", "?")
    author = msg.get("from", "?").split("(ID:")[0].strip()
    text = " ".join(msg.get("text", "").split())
    if max_text > 0 and len(text) > max_text:
        text = text[: max_text - 1].rstrip() + "…"
    return f"[{time}] {channel} — {author}: {text}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to the Slack overflow .txt file")
    parser.add_argument(
        "--include-bots",
        action="store_true",
        help="Include messages from bots (default: excluded as noise).",
    )
    parser.add_argument(
        "--max-text",
        type=int,
        default=240,
        help="Truncate each message body to N chars (0 = no truncation).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Skip parsing and just print the inner `results` blob verbatim.",
    )
    args = parser.parse_args()

    if not args.path.exists():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 1

    results = load_results_text(args.path)

    if args.raw:
        print(results)
        return 0

    blocks = MESSAGE_SEPARATOR.split(results)
    total = 0
    printed = 0
    for block in blocks:
        msg = parse_message(block)
        if msg is None:
            continue
        total += 1
        if not args.include_bots and msg.get("is_bot") == "true":
            continue
        print(format_message(msg, args.max_text))
        printed += 1

    print(
        f"\n-- {printed} message(s) shown "
        f"({total - printed} bot/noise skipped, {total} total) --",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
