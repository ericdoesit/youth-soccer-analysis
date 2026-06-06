#!/usr/bin/env python3
"""
Scrape all ECNL Boys club data from the athleteone.com API.

Each conference has its own set of division (age group) IDs, so we first
discover them, then scrape each conference × age group combination.

Also fetches the national Champions League view (all-conference top teams).

Output: data/ecnl_clubs_raw.csv, data/ecnl_clubs.csv
"""

import re
import csv
import time
import urllib.request
from pathlib import Path
from collections import defaultdict

ORG_ID     = 12
ORG_SEASON = 70
BASE       = "https://api.athleteone.com/api/Script/get-conference-standings"

# Event IDs: conferences + Champions League anchor (3876 doubles as CL event)
CONFERENCES = {
    3876: "Far West",
    3877: "Florida",
    3878: "Heartland",
    3879: "Mid-America",
    3880: "Mid-Atlantic",
    3881: "Midwest",
    3882: "Mountain",
    3883: "New England",
    # 4392: NY Alliance — broken per user
    3884: "North Atlantic",
    3885: "Northern Cal",
    3886: "Northwest",
    3887: "Ohio Valley",
    3888: "Southeast",
    3889: "Southwest",
    3890: "Texas",
    # 4139: Texas Champions Cup — special event, skip for now
}

# Known division IDs for the Champions League view (event 3876 acts as CL anchor)
CL_DIVISION_IDS = {
    "B2013": 18211,
    "B2012": 18212,
    "B2011": 18213,
    "B2010": 18214,
    "B2009": 18215,
    "B2008": 18216,
}

OPTION_RE  = re.compile(r'<option value="(\d+)"[^>]*>([^<]+)</option>')
SPAN_RE    = re.compile(
    r'<span\s+class="individual-team-item"\s+'
    r'data-event-id="(\d+)"\s+'
    r'data-club-id="(\d+)"\s+'
    r'data-team-id="(\d+)"[^>]*>'
    r'(.*?)'
    r'</span>'
    r'.*?'
    r'(?:<span[^>]*>(?:AQ:|Qualification:)</span>)'
    r'<span[^>]*>([^<]+)</span>',
    re.DOTALL,
)
AGE_SUFFIX = re.compile(r'\s+ECNL\s+B\d{2}/?\d*\s*$', re.IGNORECASE)

RAW_OUT  = Path(__file__).parent.parent / "data" / "ecnl_clubs_raw.csv"
CLUB_OUT = Path(__file__).parent.parent / "data" / "ecnl_clubs.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://theecnl.com/",
}


def fetch(event_id: int, div_id: int, standing_type: int) -> str:
    url = f"{BASE}/{event_id}/{ORG_ID}/{ORG_SEASON}/{div_id}/{standing_type}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")


def get_division_ids(event_id: int) -> dict[str, int]:
    """Fetch event page with div=0 to discover age-group division IDs."""
    html = fetch(event_id, 0, 0)
    divisions = {}
    for m in OPTION_RE.finditer(html):
        val, label = m.group(1), m.group(2).strip()
        if re.match(r'^B20\d{2}', label):
            # Normalize label: "B2013" or "B2008/2007" → "B2013" / "B2008"
            ag = re.match(r'^(B20\d{2})', label).group(1)
            divisions[ag] = int(val)
    return divisions


def parse(html: str, age_group: str, conference_name: str = "") -> list[dict]:
    rows = []
    for m in SPAN_RE.finditer(html):
        raw_name = m.group(4).strip()
        # Use passed conference_name for conf view; for CL view parse from HTML
        conf = conference_name if conference_name else m.group(5).strip()
        rows.append({
            "club_id":    int(m.group(2)),
            "team_id":    int(m.group(3)),
            "club_name":  AGE_SUFFIX.sub("", raw_name).strip(),
            "conference": conf,
            "age_group":  age_group,
        })
    return rows


def main():
    all_rows: list[dict] = []

    # Phase 1: Champions League (national top teams, ~66 per age group)
    print("=== Phase 1: Champions League ===")
    for ag, div_id in CL_DIVISION_IDS.items():
        try:
            html = fetch(3876, div_id, 1)
            rows = parse(html, ag)
            print(f"  {ag}: {len(rows)}")
            all_rows.extend(rows)
            time.sleep(0.3)
        except Exception as e:
            print(f"  {ag}: ERROR — {e}")

    # Phase 2: Each conference, each age group (captures non-CL qualifying clubs)
    print("\n=== Phase 2: Conference standings ===")
    for event_id, conf_name in CONFERENCES.items():
        try:
            div_map = get_division_ids(event_id)
            time.sleep(0.2)
        except Exception as e:
            print(f"  {conf_name}: can't get division IDs — {e}")
            continue

        conf_total = 0
        for ag, div_id in div_map.items():
            try:
                html = fetch(event_id, div_id, 0)
                rows = parse(html, ag, conf_name)
                conf_total += len(rows)
                all_rows.extend(rows)
                time.sleep(0.2)
            except Exception as e:
                print(f"  {conf_name}/{ag}: ERROR — {e}")

        print(f"  {conf_name}: {conf_total} team entries (divisions: {list(div_map.keys())})")

    # Deduplicate within (club_id, age_group, team_id)
    seen: set = set()
    unique: list[dict] = []
    for row in all_rows:
        key = (row["club_id"], row["age_group"], row["team_id"])
        if key not in seen:
            seen.add(key)
            unique.append(row)

    with open(RAW_OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["club_id","team_id","club_name","conference","age_group"])
        w.writeheader()
        w.writerows(unique)
    print(f"\nWrote {len(unique)} raw rows → {RAW_OUT.name}")

    # Build deduplicated club list
    clubs: dict[int, str] = {}
    confs: dict[int, set]  = defaultdict(set)
    ags:   dict[int, set]  = defaultdict(set)

    for row in unique:
        cid = row["club_id"]
        confs[cid].add(row["conference"])
        ags[cid].add(row["age_group"])
        if cid not in clubs:
            clubs[cid] = row["club_name"]

    dedup = []
    for cid in sorted(clubs):
        region = guess_region(sorted(confs[cid]))
        dedup.append({
            "club_id":     cid,
            "club_name":   clubs[cid],
            "region":      region,
            "conferences": " | ".join(sorted(confs[cid])),
            "age_groups":  " | ".join(sorted(ags[cid])),
            "website":     "",
        })

    with open(CLUB_OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["club_id","club_name","region","conferences","age_groups","website"])
        w.writeheader()
        w.writerows(dedup)

    print(f"Wrote {len(dedup)} unique clubs → {CLUB_OUT.name}")
    from collections import Counter
    for reg, n in sorted(Counter(r["region"] for r in dedup).items()):
        print(f"  {reg}: {n}")


def guess_region(confs: list) -> str:
    text = " ".join(confs).lower()
    if any(k in text for k in ("far west", "northern cal", "southwest", "northwest")):
        return "West"
    if any(k in text for k in ("texas", "mountain", "heartland", "mid-america")):
        return "Central"
    if any(k in text for k in ("florida", "southeast", "mid-atlantic", "ohio valley",
                                "north atlantic", "new england", "midwest")):
        return "East"
    return "Unknown"


if __name__ == "__main__":
    main()
