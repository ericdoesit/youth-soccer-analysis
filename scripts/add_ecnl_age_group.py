#!/usr/bin/env python3
"""
Read ECNL standings table HTML from stdin and append to the running club CSV.

Usage (Mac):
  pbpaste | python3 scripts/add_ecnl_age_group.py b2012

The age group arg sets the label stored in the CSV.
Run once per age group; duplicate club_ids across age groups are fine —
consolidation happens in build_ecnl_clubs.py.
"""

import re
import sys
import csv
from pathlib import Path

OUT = Path(__file__).parent.parent / "data" / "ecnl_clubs_raw.csv"
FIELDNAMES = ["club_id", "team_id", "club_name", "conference", "age_group"]

SPAN_RE = re.compile(
    r'<span\s+class="individual-team-item"\s+'
    r'data-event-id="(\d+)"\s+'
    r'data-club-id="(\d+)"\s+'
    r'data-team-id="(\d+)"[^>]*>'
    r'(.*?)'
    r'</span>'
    r'.*?'
    r'<span[^>]*>AQ:</span>'
    r'<span[^>]*>([^<]+)</span>',
    re.DOTALL,
)
AGE_SUFFIX_RE = re.compile(r'\s+ECNL\s+B\d{2}\s*$', re.IGNORECASE)


def normalize(raw: str) -> str:
    return AGE_SUFFIX_RE.sub("", raw).strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: pbpaste | python3 add_ecnl_age_group.py <age_group>")
        print("  e.g.  pbpaste | python3 add_ecnl_age_group.py b2012")
        sys.exit(1)

    age_group = sys.argv[1].upper()
    html = sys.stdin.read()

    rows = []
    for m in SPAN_RE.finditer(html):
        raw_name = m.group(4).strip()
        rows.append({
            "club_id":   int(m.group(2)),
            "team_id":   int(m.group(3)),
            "club_name": normalize(raw_name),
            "conference": m.group(5).strip(),
            "age_group": age_group,
        })

    if not rows:
        print(f"No teams found in stdin for {age_group}. Check that you copied the full table HTML.")
        sys.exit(1)

    write_header = not OUT.exists()
    with open(OUT, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if write_header:
            w.writeheader()
        w.writerows(rows)

    print(f"Added {len(rows)} teams for {age_group} → {OUT.name}")
