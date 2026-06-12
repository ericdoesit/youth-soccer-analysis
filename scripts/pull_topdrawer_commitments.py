#!/usr/bin/env python3
"""
Pull NCAA D1 college commitments from TopDrawerSoccer's public search
(area=commitments) and write data/college_commitments_topdrawer.csv.

TDS is far more complete than SoccerWire on the boys side (985 male 2026
commitments vs SoccerWire's 31). Rows carry club + high school but no
league, so the league is inferred from the club via data/clubs.csv using
the same lookup as pull_soccerwire_commitments.py.

Rerun anytime:
    python3 scripts/pull_topdrawer_commitments.py
"""

import csv
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pull_soccerwire_commitments import infer_league, load_club_leagues  # noqa: E402

BASE = ("https://www.topdrawersoccer.com/search/?query=&divisionId=1"
        "&genderId={gender}&graduationYear={year}&positionId=0&playerRating="
        "&stateId=All&pageNo={page}&area=commitments")
OUT = "data/college_commitments_topdrawer.csv"
# TDS only exposes classes that haven't graduated (2026-2030 as of June 2026)
COMBOS = [(g, y) for g in ("m", "f") for y in (2026, 2027)]
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

ROW_RE = re.compile(
    r'club-player-profile/[^"]*/pid-(\d+)">([^<]+)</a>'      # pid, name
    r'(.*?)rating-box-blue.*?</span>\s*</span>(.*?)'          # ...club text
    r'<div class="d-flex d-md-none">',
    re.S)
CELL_RE = re.compile(
    r'<td class="d-none d-md-table-cell">([A-Z]{2})</td>\s*'
    r'<td class="d-none d-md-table-cell">([A-Z/]+)</td>\s*'
    r'<td>(\d{4})</td>.*?college-soccer-details/[^"]+">([^<]+)</a>', re.S)

FIELDS = ["player", "tds_pid", "gender", "recruit_year", "position", "state",
          "club", "high_school", "club_league_inferred", "college",
          "college_division", "verified_signing"]


def parse_page(html, gender, year):
    rows = []
    for chunk in html.split("<tr>"):
        if "club-player-profile" not in chunk:
            continue
        head = ROW_RE.search(chunk)
        cells = CELL_RE.search(chunk)
        if not head or not cells:
            continue
        club_hs = re.sub(r"\s+", " ", head.group(4)).strip()
        club, _, hs = club_hs.partition("/")
        club = "" if club.strip() in ("N/A", "") else club.strip()
        rows.append({
            "player": head.group(2).strip(),
            "tds_pid": head.group(1),
            "gender": "male" if gender == "m" else "female",
            "recruit_year": year,
            "position": cells.group(2),
            "state": cells.group(1),
            "club": club,
            "high_school": hs.strip(),
            "college": cells.group(4).strip(),
            "college_division": "ncaa_d1",
            "verified_signing": "1" if "verified-signing" in chunk else "",
        })
    return rows


def get(url, attempts=4):
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", "replace")
        except OSError as e:
            if i == attempts - 1:
                raise
            wait = 5 * (i + 1)
            print(f"  retry in {wait}s ({e})")
            time.sleep(wait)


def main():
    lookup = load_club_leagues()
    all_rows = []
    for gender, year in COMBOS:
        page, pages = 0, 1
        while page < pages:
            html = get(BASE.format(gender=gender, year=year, page=page))
            if page == 0:
                m = re.search(r"1-25 of (\d+)", html)
                total = int(m.group(1)) if m else 0
                pages = -(-total // 25)
                print(f"{gender} {year}: {total} commitments ({pages} pages)")
            rows = parse_page(html, gender, year)
            all_rows.extend(rows)
            page += 1
            time.sleep(0.4)

    for r in all_rows:
        r["club_league_inferred"] = infer_league(r["club"], r["gender"], lookup)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)
    print(f"Wrote {len(all_rows)} D1 commitments to {OUT}")


if __name__ == "__main__":
    main()
