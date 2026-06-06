#!/usr/bin/env python3
"""
Deduplicate ecnl_clubs_raw.csv → ecnl_clubs.csv
One row per unique club_id with all conferences listed.
Run after all age groups have been added.
"""

import csv
from pathlib import Path
from collections import defaultdict

RAW   = Path(__file__).parent.parent / "data" / "ecnl_clubs_raw.csv"
OUT   = Path(__file__).parent.parent / "data" / "ecnl_clubs.csv"


def main():
    if not RAW.exists():
        print(f"Missing {RAW} — run add_ecnl_age_group.py first.")
        return

    clubs: dict[int, str] = {}
    conferences: dict[int, set] = defaultdict(set)
    age_groups: dict[int, set] = defaultdict(set)

    with open(RAW) as fh:
        for row in csv.DictReader(fh):
            cid = int(row["club_id"])
            conferences[cid].add(row["conference"])
            age_groups[cid].add(row["age_group"])
            if cid not in clubs:
                clubs[cid] = row["club_name"]

    rows = []
    for cid in sorted(clubs):
        confs = sorted(conferences[cid])
        ags = sorted(age_groups[cid])
        # Guess region from conference names
        region = guess_region(confs)
        rows.append({
            "club_id":    cid,
            "club_name":  clubs[cid],
            "region":     region,
            "conferences": " | ".join(confs),
            "age_groups":  " | ".join(ags),
            "website":    "",   # to be filled in
        })

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["club_id","club_name","region","conferences","age_groups","website"])
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} unique ECNL clubs → {OUT.name}")
    # Summary by region
    from collections import Counter
    c = Counter(r["region"] for r in rows)
    for reg, n in sorted(c.items()):
        print(f"  {reg}: {n}")


def guess_region(confs: list[str]) -> str:
    text = " ".join(confs).lower()
    if any(k in text for k in ("far west", "northern cal", "southwest", "northwest")):
        return "West"
    if any(k in text for k in ("texas", "mountain", "heartland", "mid-america")):
        return "Central"
    if any(k in text for k in ("florida", "southeast", "mid-atlantic", "ohio valley", "north atlantic", "new england", "midwest")):
        return "East"
    return "Unknown"


if __name__ == "__main__":
    main()
