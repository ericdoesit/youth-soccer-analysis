#!/usr/bin/env python3
"""
Scrape all 18 NPL member leagues via their GotSport event pages.
SOCAL NPL (event 43086) already scraped → skipped here.
Reuses the same club/team extraction logic as scrape_socal_teams.py.

Output: data/npl_clubs.csv   — league, club, gotsport_url
        data/npl_teams.csv   — league, club, team_name, gender, age, division, bracket
"""

import csv
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DATA_DIR = "data"
CLUBS_CSV = os.path.join(DATA_DIR, "npl_clubs.csv")
TEAMS_CSV = os.path.join(DATA_DIR, "npl_teams.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

GOTSPORT_BASE = "https://system.gotsport.com"

# NPL member leagues with GotSport event IDs
# SOCAL (43086) already scraped — excluded
# Multiple event IDs per league = list; we'll scrape each and merge
NPL_LEAGUES = [
    ("NorCal NPL",              [44145]),
    ("FCL NPL (Florida)",       [44970]),
    ("GLA NPL",                 [43157]),
    ("MDL NPL (GLA Boys)",      [43156]),
    ("Central States NPL",      [46428]),
    ("South Atlantic Premier",  [51028]),
    ("Frontier Premier League", [50988]),
    ("Red River NPL",           [45381]),
    ("Mountain West NPL",       [44839]),
    ("VPSL NPL (Virginia)",     [50339]),
    ("Minnesota NPL",           [47013]),
    ("NISL NPL (Chicago)",      [49634]),
    ("CPSL NPL (Chesapeake)",   [52692, 43268]),
    ("Mid-Atlantic Premier",    [45036]),
    ("WPL NPL (Washington)",    [44844, 44846]),
]


def get_soup(url, timeout=15):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def scrape_event_clubs(event_id):
    """Return list of (club_name, gotsport_club_url) from a GotSport event."""
    url = f"{GOTSPORT_BASE}/org_event/events/{event_id}/clubs"
    clubs = []
    try:
        soup = get_soup(url)
        for a in soup.select("a[href*='/clubs/']"):
            href = a["href"].strip()
            if href.startswith("/"):
                href = GOTSPORT_BASE + href
            name = a.get_text(strip=True)
            if name and (name, href) not in clubs:
                clubs.append((name, href))
    except Exception as e:
        print(f"    ERROR fetching event {event_id}: {type(e).__name__}: {e}")
    return clubs


def scrape_club_teams(club_name, club_url):
    """Scrape a GotSport club page for team listings."""
    teams = []
    try:
        soup = get_soup(club_url)
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            header_cells = [th.get_text(strip=True).lower()
                            for th in rows[0].find_all(["th", "td"])]
            if not any(h in header_cells for h in ["team", "gender", "age", "division", "bracket"]):
                continue
            for row in rows[1:]:
                cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
                if not any(cells):
                    continue
                d = dict(zip(header_cells, cells))
                team_name = d.get("team name", d.get("team", cells[0] if cells else ""))
                gender    = d.get("gender", "")
                age       = d.get("age group", d.get("age", ""))
                division  = d.get("division", "")
                bracket   = d.get("bracket", "")
                if team_name:
                    teams.append({
                        "team_name": team_name,
                        "gender": gender,
                        "age": age,
                        "division": division,
                        "bracket": bracket,
                    })
    except Exception as e:
        print(f"    ERROR [teams for {club_name}]: {type(e).__name__}: {e}")
    return teams


def main():
    # Load already-scraped leagues from checkpoint
    done_leagues = set()
    if os.path.exists(CLUBS_CSV):
        with open(CLUBS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done_leagues.add(row["league"])
        print(f"Resume: {len(done_leagues)} leagues already scraped")

    club_fields = ["league", "event_id", "club", "gotsport_url"]
    team_fields = ["league", "event_id", "club", "team_name", "gender", "age", "division", "bracket"]

    club_mode = "a" if done_leagues else "w"
    team_mode = "a" if os.path.exists(TEAMS_CSV) and done_leagues else "w"

    club_f = open(CLUBS_CSV, club_mode, newline="", encoding="utf-8")
    team_f = open(TEAMS_CSV, team_mode, newline="", encoding="utf-8")
    club_w = csv.DictWriter(club_f, fieldnames=club_fields)
    team_w = csv.DictWriter(team_f, fieldnames=team_fields)
    if club_mode == "w":
        club_w.writeheader()
    if team_mode == "w":
        team_w.writeheader()

    total_clubs = 0
    total_teams = 0

    try:
        for league_name, event_ids in NPL_LEAGUES:
            if league_name in done_leagues:
                print(f"SKIP (already done): {league_name}")
                continue

            print(f"\n=== {league_name} (events: {event_ids}) ===")

            # Collect clubs across all event IDs for this league
            league_clubs = {}  # name → url (deduplicate)
            for eid in event_ids:
                print(f"  Fetching event {eid}...")
                clubs = scrape_event_clubs(eid)
                print(f"    {len(clubs)} clubs")
                for name, url in clubs:
                    if name not in league_clubs:
                        league_clubs[name] = (url, eid)
                time.sleep(2)

            print(f"  Total unique clubs: {len(league_clubs)}")

            for club_name, (club_url, eid) in league_clubs.items():
                club_w.writerow({
                    "league": league_name,
                    "event_id": eid,
                    "club": club_name,
                    "gotsport_url": club_url,
                })
                total_clubs += 1

                print(f"  [{total_clubs}] {club_name}")
                teams = scrape_club_teams(club_name, club_url)
                print(f"    -> {len(teams)} teams")

                for t in teams:
                    team_w.writerow({
                        "league": league_name,
                        "event_id": eid,
                        "club": club_name,
                        **t,
                    })
                    total_teams += 1

                club_f.flush()
                team_f.flush()
                time.sleep(5)

    finally:
        club_f.close()
        team_f.close()

    print(f"\nDone.")
    print(f"  Clubs: {total_clubs} -> {CLUBS_CSV}")
    print(f"  Teams: {total_teams} -> {TEAMS_CSV}")


if __name__ == "__main__":
    main()
