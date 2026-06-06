#!/usr/bin/env python3
"""
Scrape ussoccerparent.com state directory pages for national club listings.
Each state page lists youth soccer clubs with name + website URL.

Output: data/national_clubs.csv  — state, club_name, website_url
"""

import csv
import os
import time
import requests
from bs4 import BeautifulSoup

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "national_clubs.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

BASE = "https://ussoccerparent.com"

# (display_name, url_slug) — Florida uses /florida-state/
STATES = [
    ("Alabama",        "alabama"),
    ("Alaska",         "alaska"),
    ("Arizona",        "arizona"),
    ("Arkansas",       "arkansas"),
    ("California",     "california"),
    ("Colorado",       "colorado"),
    ("Connecticut",    "connecticut"),
    ("Delaware",       "delaware"),
    ("Florida",        "florida-state"),
    ("Georgia",        "georgia"),
    ("Hawaii",         "hawaii"),
    ("Idaho",          "idaho"),
    ("Illinois",       "illinois"),
    ("Indiana",        "indiana"),
    ("Iowa",           "iowa"),
    ("Kansas",         "kansas"),
    ("Kentucky",       "kentucky"),
    ("Louisiana",      "louisiana"),
    ("Maine",          "maine"),
    ("Maryland",       "maryland"),
    ("Massachusetts",  "massachusetts"),
    ("Michigan",       "michigan"),
    ("Minnesota",      "minnesota"),
    ("Mississippi",    "mississippi"),
    ("Missouri",       "missouri"),
    ("Montana",        "montana"),
    ("Nebraska",       "nebraska"),
    ("Nevada",         "nevada"),
    ("New Hampshire",  "new-hampshire"),
    ("New Jersey",     "new-jersey"),
    ("New Mexico",     "new-mexico"),
    ("New York",       "new-york"),
    ("North Carolina", "north-carolina"),
    ("North Dakota",   "north-dakota"),
    ("Ohio",           "ohio"),
    ("Oklahoma",       "oklahoma"),
    ("Oregon",         "oregon"),
    ("Pennsylvania",   "pennsylvania"),
    ("Rhode Island",   "rhode-island"),
    ("South Carolina", "south-carolina"),
    ("South Dakota",   "south-dakota"),
    ("Tennessee",      "tennessee"),
    ("Texas",          "texas"),
    ("Utah",           "utah"),
    ("Vermont",        "vermont"),
    ("Virginia",       "virginia"),
    ("Washington",     "washington"),
    ("West Virginia",  "west-virginia"),
    ("Wisconsin",      "wisconsin"),
    ("Wyoming",        "wyoming"),
]


def scrape_state(state_name, slug):
    url = f"{BASE}/{slug}/"
    clubs = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 404:
            print(f"  404 — {url}")
            return clubs
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Primary pattern: <strong><a href="...">Name</a></strong>
        for strong in soup.find_all("strong"):
            a = strong.find("a", href=True)
            if a:
                name = a.get_text(strip=True)
                href = a["href"].strip()
                # Skip internal site navigation links
                if name and href and not href.startswith(BASE + "/"):
                    clubs.append({
                        "state": state_name,
                        "club_name": name,
                        "website_url": href,
                        "source_page": url,
                    })

        # Fallback: plain <a> links that look like club entries
        # (some pages may not wrap in <strong>)
        if not clubs:
            for a in soup.select("article a[href]"):
                name = a.get_text(strip=True)
                href = a["href"].strip()
                if (name and href
                        and not href.startswith(BASE)
                        and len(name) > 3
                        and not name.lower().startswith("click")
                        and not name.lower().startswith("read more")):
                    clubs.append({
                        "state": state_name,
                        "club_name": name,
                        "website_url": href,
                        "source_page": url,
                    })

    except Exception as e:
        print(f"  ERROR [{state_name}]: {type(e).__name__}: {e}")

    return clubs


def main():
    fieldnames = ["state", "club_name", "website_url", "source_page"]

    # Resume: load states already scraped
    done_states = set()
    if os.path.exists(OUT_CSV):
        with open(OUT_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done_states.add(row["state"])
        print(f"Resume: {len(done_states)} states already scraped")

    remaining = [(n, s) for n, s in STATES if n not in done_states]
    print(f"Scraping {len(remaining)} remaining states...")

    # Write header only if starting fresh
    if not done_states:
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()

    all_clubs = []
    for i, (state_name, slug) in enumerate(remaining, 1):
        print(f"[{i:02d}/{len(remaining)}] {state_name}")
        clubs = scrape_state(state_name, slug)
        print(f"  -> {len(clubs)} clubs")
        all_clubs.extend(clubs)

        # Append to CSV after each state
        with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(clubs)

        time.sleep(1.5)

    print(f"\nDone. {len(all_clubs)} clubs across {len(STATES)} states -> {OUT_CSV}")

    # Summary by state
    from collections import Counter
    counts = Counter(c["state"] for c in all_clubs)
    print("\n--- Clubs per state ---")
    for state, count in sorted(counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  {state:<20s} {count}")


if __name__ == "__main__":
    main()
