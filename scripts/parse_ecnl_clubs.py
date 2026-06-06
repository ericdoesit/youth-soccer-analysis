#!/usr/bin/env python3
"""
Parse ECNL Champions League standings HTML tables and build a deduplicated club CSV.

Usage:
  Save each age group's table HTML to data/ecnl_html/<age_group>.html
  e.g. data/ecnl_html/b2013.html, b2012.html, b2011.html, b2010.html, b2009.html, b2008.html

  Then run: python3 scripts/parse_ecnl_clubs.py

Output:
  data/ecnl_clubs_all.csv   — all rows (club_id, team_id, club_name, conference, age_group)
  data/ecnl_clubs.csv       — deduplicated by club_id (most common conference kept)
"""

import re
import csv
import os
from pathlib import Path
from collections import defaultdict

HTML_DIR = Path(__file__).parent.parent / "data" / "ecnl_html"
OUT_ALL  = Path(__file__).parent.parent / "data" / "ecnl_clubs_all.csv"
OUT_DEDUP = Path(__file__).parent.parent / "data" / "ecnl_clubs.csv"

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
    re.DOTALL
)

AGE_SUFFIX_RE = re.compile(r'\s+ECNL\s+B\d{2}\s*$', re.IGNORECASE)


def infer_age_group(filename: str) -> str:
    stem = Path(filename).stem.lower()
    for ag in ("b2013", "b2012", "b2011", "b2010", "b2009", "b2008"):
        if ag in stem:
            return ag.upper()
    return stem.upper()


def normalize_name(raw: str) -> str:
    return AGE_SUFFIX_RE.sub("", raw).strip()


def parse_file(path: Path) -> list[dict]:
    age_group = infer_age_group(path.name)
    text = path.read_text(encoding="utf-8", errors="replace")
    rows = []
    for m in SPAN_RE.finditer(text):
        raw_name = m.group(4).strip()
        conference = m.group(5).strip()
        rows.append({
            "club_id":    int(m.group(2)),
            "team_id":    int(m.group(3)),
            "club_name":  normalize_name(raw_name),
            "conference": conference,
            "age_group":  age_group,
        })
    return rows


def main():
    all_rows = []
    files = sorted(HTML_DIR.glob("*.html"))
    if not files:
        print(f"No .html files found in {HTML_DIR}")
        return

    for f in files:
        rows = parse_file(f)
        print(f"  {f.name}: {len(rows)} teams parsed")
        all_rows.extend(rows)

    # Write all rows
    with open(OUT_ALL, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["club_id","team_id","club_name","conference","age_group"])
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nWrote {len(all_rows)} rows → {OUT_ALL.name}")

    # Deduplicate by club_id — keep earliest-seen name, list all conferences
    clubs: dict[int, dict] = {}
    club_conferences: dict[int, set] = defaultdict(set)

    for row in all_rows:
        cid = row["club_id"]
        club_conferences[cid].add(row["conference"])
        if cid not in clubs:
            clubs[cid] = {
                "club_id":   cid,
                "club_name": row["club_name"],
            }

    dedup_rows = []
    for cid, info in sorted(clubs.items()):
        confs = sorted(club_conferences[cid])
        dedup_rows.append({
            "club_id":     cid,
            "club_name":   info["club_name"],
            "conferences": " | ".join(confs),
        })

    with open(OUT_DEDUP, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["club_id","club_name","conferences"])
        w.writeheader()
        w.writerows(dedup_rows)
    print(f"Wrote {len(dedup_rows)} unique clubs → {OUT_DEDUP.name}")


if __name__ == "__main__":
    main()
