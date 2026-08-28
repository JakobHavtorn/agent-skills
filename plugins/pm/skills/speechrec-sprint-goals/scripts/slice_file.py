#!/usr/bin/env python3
"""Slice a large file into ~N-character spans for agent consumption.

Slack channel reads can exceed the single-response token budget and get
saved to a file. This script chunks that file into spans small enough for
a subagent to process, printing each with a header so the caller can
request specific spans or process them sequentially.

Usage:
  python3 slice_file.py <file> [--span 80000]
  python3 slice_file.py <file> --span 80000 --index 2   # print only span 2

Output is written to stdout. Each span is preceded by a header line:
  ===== SPAN 1/5 (chars 0-79999) =====
"""

import argparse
import sys
from pathlib import Path


def slice_file(path: Path, span: int, index: int | None) -> str:
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print("error: file is empty", file=sys.stderr)
        sys.exit(1)

    total = len(text)
    spans = []
    pos = 0
    while pos < total:
        end = min(pos + span, total)
        if end < total:
            newline_pos = text.rfind("\n", pos, end)
            if newline_pos > pos:
                end = newline_pos + 1
        spans.append((pos, end, text[pos:end]))
        pos = end

    if index is not None:
        if index < 1 or index > len(spans):
            print(f"error: index {index} out of range (1-{len(spans)})", file=sys.stderr)
            sys.exit(1)
        start, end, chunk = spans[index - 1]
        print(f"===== SPAN {index}/{len(spans)} (chars {start}-{end - 1}) =====")
        print(chunk, end="")
        return

    for i, (start, end, chunk) in enumerate(spans, 1):
        print(f"===== SPAN {i}/{len(spans)} (chars {start}-{end - 1}) =====")
        print(chunk, end="")
        if i < len(spans):
            print()


def main():
    parser = argparse.ArgumentParser(description="Slice a large file into spans for agent consumption.")
    parser.add_argument("file", help="Path to the file to slice")
    parser.add_argument("--span", type=int, default=80000, help="Approximate span size in characters (default: 80000)")
    parser.add_argument("--index", type=int, default=None, help="Print only this span (1-based)")
    args = parser.parse_args()

    slice_file(Path(args.file), args.span, args.index)


if __name__ == "__main__":
    main()
