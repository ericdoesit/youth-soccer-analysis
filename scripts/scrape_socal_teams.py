#!/usr/bin/env python3
"""
Scrape SoCal Soccer league teams from GotSport.
Hits every club page under event 43086, extracts the Teams widget,
and saves a combined CSV with: club, team_name, team_url, gender, age, division, bracket
"""

import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://system.gotsport.com"
CLUBS_URL = f"{BASE}/org_event/events/43086/clubs"
OUT_PATH = "data/socal_league_teams.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def get_soup(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def get_club_links(soup):
    """Return list of (club_name, club_url) from the clubs index page."""
    links = []
    for a in soup.select("a[href*='/clubs/']"):
        href = a["href"].strip()
        if href.startswith("/"):
            href = BASE + href
        name = a.get_text(strip=True)
        if name:
            links.append((name, href))
    # deduplicate by URL
    seen = set()
    out = []
    for name, url in links:
        if url not in seen:
            seen.add(url)
            out.append((name, url))
    return out


def get_teams(club_name, club_url, soup):
    """Extract rows from the Teams widget table."""
    rows = []
    # Find the Teams widget header, then the table inside it
    for h4 in soup.find_all("h4", class_="widget-title"):
        if "teams" in h4.get_text(strip=True).lower():
            widget = h4.find_parent(class_="widget")
            if not widget:
                continue
            table = widget.find("table")
            if not table:
                continue
            for tr in table.select("tbody tr"):
                cells = tr.find_all("td")
                if len(cells) < 5:
                    continue
                name_cell = cells[0]
                a = name_cell.find("a")
                team_name = name_cell.get_text(strip=True)
                team_url = ""
                if a and a.get("href"):
                    team_url = urljoin(BASE, a["href"])
                gender = cells[1].get_text(strip=True)
                age = cells[2].get_text(strip=True)
                division = cells[3].get_text(strip=True)
                bracket = cells[4].get_text(strip=True)
                rows.append({
                    "club": club_name,
                    "team_name": team_name,
                    "team_url": team_url,
                    "gender": gender,
                    "age": age,
                    "division": division,
                    "bracket": bracket,
                })
    return rows


def main():
    print(f"Fetching clubs list: {CLUBS_URL}")
    clubs_soup = get_soup(CLUBS_URL)
    club_links = get_club_links(clubs_soup)
    print(f"Found {len(club_links)} clubs")

    all_rows = []
    for i, (club_name, club_url) in enumerate(club_links, 1):
        try:
            print(f"  [{i}/{len(club_links)}] {club_name} — {club_url}")
            soup = get_soup(club_url)
            rows = get_teams(club_name, club_url, soup)
            print(f"    → {len(rows)} teams")
            all_rows.extend(rows)
            time.sleep(5)  # polite crawl rate
        except Exception as e:
            print(f"    ERROR: {e}")
            continue

    print(f"\nTotal teams found: {len(all_rows)}")

    fieldnames = ["club", "team_name", "team_url", "gender", "age", "division", "bracket"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved to {OUT_PATH}")

    # Quick summary
    print("\n--- Summary ---")
    from collections import Counter
    ages = Counter(r["age"] for r in all_rows)
    for age, count in sorted(ages.items()):
        print(f"  {age}: {count} teams")
    genders = Counter(r["gender"] for r in all_rows)
    for g, count in genders.items():
        print(f"  {g}: {count} teams")


if __name__ == "__main__":
    main()
