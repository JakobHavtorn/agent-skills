#!/usr/bin/env python3
"""Slice a large file into ~N-character spans for agent consumption.

Slack channel reads can exceed the single-response token budget and get
saved to a file. This script chunks that file into spans small enough for
a subagent to process, printing each with a header so the caller can
request specific spans or process them sequentially.

Usage:
  python3 slice_file.py <file> --count                 # print just the number of spans
  python3 slice_file.py <file> --index 2               # print only span 2

Workflow for parallel subagents:
  1. N=$(python3 slice_file.py <file> --count)
  2. Launch N subagents, each calling: python3 slice_file.py <file> --index $i

Output is written to stdout. Each span is preceded by a header line:
  ===== SPAN 1/5 (chars 0-79999) =====
"""

import argparse
import sys
from pathlib import Path


def slice_file(path: Path, span: int, index: int | None, count: bool) -> str:
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print("error: file is empty", file=sys.stderr)
        sys.exit(1)

    total = len(text)
    num_spans = 0
    pos = 0
    while pos < total:
        end = min(pos + span, total)
        if end < total:
            newline_pos = text.rfind("\n", pos, end)
            if newline_pos > pos:
                end = newline_pos + 1
        num_spans += 1
        pos = end

    if count:
        print(num_spans)
        return

    if index is not None:
        if index < 1 or index > num_spans:
            print(f"error: index {index} out of range (1-{num_spans})", file=sys.stderr)
            sys.exit(1)

    pos = 0
    span_num = 0
    while pos < total:
        span_num += 1
        end = min(pos + span, total)
        if end < total:
            newline_pos = text.rfind("\n", pos, end)
            if newline_pos > pos:
                end = newline_pos + 1
        chunk = text[pos:end]

        if index is not None and span_num != index:
            pos = end
            continue

        print(f"===== SPAN {span_num}/{num_spans} (chars {pos}-{end - 1}) =====")
        print(chunk, end="")
        if index is None and span_num < num_spans:
            print()

        pos = end


def main():
    parser = argparse.ArgumentParser(description="Slice a large file into spans for agent consumption.")
    parser.add_argument("file", help="Path to the file to slice")
    parser.add_argument("--span", type=int, default=80000, help="Approximate span size in characters (default: 80000)")
    parser.add_argument("--index", type=int, default=None, help="Print only this span (1-based)")
    parser.add_argument("--count", action="store_true", help="Print only the number of spans, then exit")
    args = parser.parse_args()

    slice_file(Path(args.file), args.span, args.index, args.count)


if __name__ == "__main__":
    main()
