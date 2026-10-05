#!/usr/bin/env python3
"""Print Slack canvas standup sections from the last 10 days, given a harness-spilled JSON dump."""

import json
import re
import sys
from datetime import date, timedelta

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <canvas-json-file>", file=sys.stderr)
    sys.exit(2)

with open(sys.argv[1]) as f:
    data = json.load(f)
if isinstance(data, list):
    content = json.loads(data[0]["text"])["markdown_content"]
else:
    content = data["markdown_content"]

today = date.today()
recent_dates = {(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)}

sections = re.split(r"(?=## !\[\]\(slack_date:)", content)
header_re = re.compile(r"^## !\[\]\(slack_date:(\d{4}-\d{2}-\d{2})\)")
recent = [s for s in sections if (m := header_re.match(s)) and m.group(1) in recent_dates]
print("\n".join(recent))
