#!/usr/bin/env python3
"""
Scrape GotSport national rankings for U10 boys, filter to CAS (California South).

API: https://system.gotsport.com/api/v1/team_ranking_data
     Uses bracket-style params: search[age]=10&search[gender]=m etc.
     Does NOT support server-side state filtering; we fetch all pages and
     filter client-side by team_association == "CAS".

Outputs: gotsport_cas_u10_boys.csv
"""

import requests
import csv
import time

BASE_URL = "https://system.gotsport.com/api/v1/team_ranking_data"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

AGE = 10
GENDER = "m"
TARGET_ASSOCIATION = "CAS"
OUT_PATH = "/Users/Eric/Documents/Claude/soccer/data/gotsport_cas_u10_boys.csv"
START_PAGE = 1  # set higher to resume after interruption


def fetch_page(page: int) -> dict:
    params = {
        "search[team_country]": "USA",
        "search[age]": str(AGE),
        "search[gender]": GENDER,
        "search[page]": str(page),  # page must be inside search object
    }
    for attempt in range(5):
        try:
            r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
            if r.status_code == 403:
                wait = 10 * (2 ** attempt)
                print(f"  403 on page {page}, waiting {wait}s (attempt {attempt+1}/5)")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Failed page {page} after 5 attempts")


FIELDNAMES = [
    "national_rank", "association_rank", "regional_rank",
    "club_name", "team_name", "team_association", "team_region",
    "total_points", "total_wins", "total_losses", "total_draws",
    "total_matches", "win_percent", "ranking_date", "team_id", "age", "gender",
]


def main():
    cas_teams = []
    page = START_PAGE
    total_pages = None

    # Open CSV for writing (append if resuming)
    write_mode = "a" if START_PAGE > 1 else "w"
    f_out = open(OUT_PATH, write_mode, newline="")
    writer = csv.DictWriter(f_out, fieldnames=FIELDNAMES)
    if write_mode == "w":
        writer.writeheader()

    try:
        while True:
            data = fetch_page(page)
            teams = data.get("team_ranking_data", [])
            pagination = data.get("pagination", {})

            if total_pages is None:
                total_pages = pagination.get("total_pages", 1)
                print(f"Total pages: {total_pages} ({pagination.get('total_count', '?')} national teams)")

            page_cas = []
            for t in teams:
                if t.get("team_association") == TARGET_ASSOCIATION:
                    row = {
                        "national_rank":    t.get("national_rank"),
                        "association_rank": t.get("association_rank"),
                        "regional_rank":    t.get("regional_rank"),
                        "club_name":        t.get("club_name", ""),
                        "team_name":        t.get("team_name", ""),
                        "team_association": t.get("team_association", ""),
                        "team_region":      t.get("team_region", ""),
                        "total_points":     t.get("total_points", 0),
                        "total_wins":       t.get("total_wins", 0),
                        "total_losses":     t.get("total_losses", 0),
                        "total_draws":      t.get("total_draws", 0),
                        "total_matches":    t.get("total_matches", 0),
                        "win_percent":      t.get("win_percent", ""),
                        "ranking_date":     t.get("ranking_date", ""),
                        "team_id":          t.get("team_id", ""),
                        "age":              t.get("age", ""),
                        "gender":           t.get("gender", ""),
                    }
                    page_cas.append(row)
                    cas_teams.append(row)

            if page_cas:
                writer.writerows(page_cas)
                f_out.flush()

            if page % 25 == 0 or page == total_pages:
                print(f"  Page {page}/{total_pages} — {len(cas_teams)} CAS teams so far")

            if page >= total_pages:
                break
            page += 1
            time.sleep(0.12)
    finally:
        f_out.close()

    print(f"\nTotal CAS U{AGE} {GENDER} teams collected: {len(cas_teams)}")
    print(f"Written to {OUT_PATH}")

    # Unique clubs
    clubs = sorted(set(t["club_name"] for t in cas_teams))
    print(f"Unique CAS clubs: {len(clubs)}")

    # Cross-reference against master
    master_path = "/Users/Eric/Documents/Claude/soccer/data/clubs_raw.csv"
    master_clubs = set()
    with open(master_path, newline="") as f:
        for row in csv.DictReader(f):
            master_clubs.add(row["club_name"].lower().strip())

    missing = [c for c in clubs if c.lower().strip() not in master_clubs]
    print(f"\nCAS clubs NOT in master ({len(missing)}):")
    for c in missing:
        print(f"  {c}")


if __name__ == "__main__":
    main()
