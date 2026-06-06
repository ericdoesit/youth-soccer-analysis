#!/usr/bin/env python3
"""
Scrape USL league team directories using cloudscraper (simulates browser).
Targets publicly accessible team directory pages.

Output: data/usl_all_teams.csv
"""

import csv, os, re, time
import cloudscraper
from bs4 import BeautifulSoup
from collections import Counter

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "usl_all_teams.csv")

TARGETS = [
    {
        "league": "USL League Two",
        "url": "https://www.uslleaguetwo.com/league-teams",
        "base": "https://www.uslleaguetwo.com",
    },
    {
        "league": "USL League One",
        "url": "https://www.uslleagueone.com/league-teams",
        "base": "https://www.uslleagueone.com",
    },
    {
        "league": "USL W League",
        "url": "https://www.uslwleague.com/league-teams",
        "base": "https://www.uslwleague.com",
    },
    {
        "league": "USL Academy",
        "url": "https://www.usl-academy.com/league-standings",
        "base": "https://www.usl-academy.com",
    },
    {
        "league": "USL Championship",
        "url": "https://www.uslchampionship.com/league-teams",
        "base": "https://www.uslchampionship.com",
    },
]

# STATE_MAP: known city → state mappings for common USL markets
STATE_MAP = {
    "Connecticut": "CT", "CT": "CT", "New England": "MA", "Boston": "MA",
    "Vermont": "VT", "New Hampshire": "NH",
    "New York": "NY", "Long Island": "NY", "Hudson Valley": "NY",
    "New Jersey": "NJ", "Staten Island": "NY", "Westchester": "NY",
    "Delaware": "DE", "Pennsylvania": "PA", "Philadelphia": "PA",
    "Reading": "PA", "Pittsburgh": "PA",
    "Maryland": "MD", "Bethesda": "MD", "Annapolis": "MD",
    "Virginia": "VA", "Northern Virginia": "VA", "Virginia Beach": "VA",
    "North Carolina": "NC", "Charlotte": "NC", "Raleigh": "NC",
    "South Carolina": "SC",
    "Georgia": "GA", "Atlanta": "GA",
    "Alabama": "AL", "Birmingham": "AL", "Montgomery": "AL",
    "Florida": "FL", "Jacksonville": "FL", "Miami": "FL", "Tampa": "FL",
    "Fort Lauderdale": "FL", "Lakeland": "FL", "Brevard County": "FL",
    "Mississippi": "MS", "Louisiana": "LA", "Arkansas": "AR", "Tennessee": "TN",
    "Texas": "TX", "Houston": "TX", "Dallas": "TX", "San Antonio": "TX",
    "Fort Worth": "TX", "Denton": "TX", "Lubbock": "TX",
    "Ohio": "OH", "Dayton": "OH", "Columbus": "OH", "Cleveland": "OH",
    "Toledo": "OH", "Akron": "OH",
    "Indiana": "IN", "Indiana FC": "IN",
    "Michigan": "MI", "Ann Arbor": "MI", "Flint": "MI", "Kalamazoo": "MI",
    "Lansing": "MI",
    "West Virginia": "WV",
    "Illinois": "IL", "Chicago": "IL", "Rockford": "IL", "Springfield": "IL",
    "Peoria": "IL",
    "Minnesota": "MN", "Minneapolis": "MN",
    "Wisconsin": "WI",
    "Iowa": "IA", "Des Moines": "IA",
    "Kansas": "KS",
    "Missouri": "MO",
    "Colorado": "CO", "Boulder": "CO", "Denver": "CO",
    "Utah": "UT",
    "Washington": "WA", "Seattle": "WA", "Tacoma": "WA", "Olympia": "WA",
    "Oregon": "OR", "Portland": "OR",
    "California": "CA", "San Francisco": "CA", "Oakland": "CA", "Sacramento": "CA",
    "San Jose": "CA", "Los Angeles": "CA", "San Diego": "CA",
    "Arizona": "AZ", "Tucson": "AZ",
}


def parse_teams_from_text(league, text):
    """
    Parse division/conference headers and team names from the flat body text.
    Headers look like: 'NORTHEAST DIVISION', 'EASTERN CONFERENCE', 'Central Conference'
    Team names follow each header.
    """
    # Split on DIVISION or CONFERENCE tokens (keep delimiter)
    # Pattern: word(s) all-caps ending in DIVISION or CONFERENCE
    pattern = r'([A-Z][A-Z ]+(?:DIVISION|CONFERENCE))'
    chunks = re.split(pattern, text)

    teams = []
    current_conf = ""
    current_div = ""

    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk:
            continue

        # This chunk IS a header
        if re.match(r'[A-Z][A-Z ]+(?:DIVISION|CONFERENCE)$', chunk):
            if "CONFERENCE" in chunk:
                current_conf = chunk.title().replace(" Conference", "").strip()
                current_div = ""
            else:
                current_div = chunk.title().replace(" Division", "").strip()
            continue

        # This chunk has team names — split them by using title-case boundaries
        # Teams are sequences of title-case words. Split on transition back to all-caps
        # Actually just split on patterns like "FC" appearing mid-sentence
        # Better: teams are separated by newlines in the rendered page but flatten here
        # Use a heuristic: split when we see a new Capitalized word after a word that
        # ends with FC, SC, AC, United, City, etc.

        # Simple approach: the text has no delimiters, so we need to use known team names
        # OR try a different extraction strategy.

        # Strategy: Look for team name patterns in the HTML directly (anchor tags or spans)
        pass

    return current_conf, current_div, teams


def extract_teams_from_html(league, html, base_url):
    """Extract teams from page HTML using multiple strategies."""
    soup = BeautifulSoup(html, "html.parser")
    teams = []

    # Strategy 1: Find team links (slug-style hrefs on anchor tags)
    team_link_pattern = re.compile(r'^/[a-z0-9-]+$')
    conf_div_headers = {"conference", "division", "eastern", "western", "central", "southern",
                        "northern", "northern", "schedule", "standings", "news", "about",
                        "contact", "home", "login", "search", "privacy", "league-teams",
                        "league-standings", "league-schedule", "history"}

    seen_hrefs = set()
    seen_names = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        name = a.get_text(strip=True)
        if (team_link_pattern.match(href) and
                len(name) > 2 and len(name) < 60 and
                href.lstrip("/") not in conf_div_headers and
                name.lower() not in conf_div_headers and
                href not in seen_hrefs):
            seen_hrefs.add(href)
            if name not in seen_names:
                seen_names.add(name)
                teams.append({
                    "league": league,
                    "team_name": name,
                    "conference": "",
                    "division": "",
                    "city": "",
                    "state": "",
                    "team_url": base_url + href,
                })

    if teams:
        print(f"    Strategy 1 (links): {len(teams)} teams")
        return teams

    # Strategy 2: Parse body text using DIVISION/CONFERENCE boundaries
    body_text = soup.get_text(" ", strip=True)

    # Find the section that starts with conference/division headers
    # Look for the first all-caps "XXX CONFERENCE" or "XXX DIVISION"
    start_match = re.search(r'[A-Z]{3,}(?:\s+[A-Z]{3,})*\s+(?:DIVISION|CONFERENCE)', body_text)
    if not start_match:
        print("    Strategy 2: no division headers found")
        return []

    relevant = body_text[start_match.start():]

    # Now parse: split on division/conference headers
    # The team names in between are separated by spaces but each team name is
    # title-case words. We need to identify team boundaries.

    # Split the text into tokens by ALL-CAPS words (headers) vs mixed-case (team names)
    # Tokenize: each word is either ALL_CAPS or Mixed_Case
    current_conf = ""
    current_div = ""

    # Split text by known division/conference header patterns
    header_re = re.compile(
        r'\b([A-Z][A-Z ]{2,}(?:CONFERENCE|DIVISION))\b'
    )
    parts = header_re.split(relevant)

    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        if header_re.fullmatch(part.strip()):
            if "CONFERENCE" in part:
                current_conf = part.title().replace(" Conference", "").strip()
                current_div = ""
            else:
                current_div = part.title().replace(" Division", "").strip()
            continue

        # This part contains team names concatenated by spaces
        # Split into individual team names using capitalization boundaries
        # A team name typically: one or more title-case words possibly followed by
        # FC, SC, AC, etc.
        extracted = split_team_names(part)
        for name in extracted:
            if name and name not in seen_names:
                seen_names.add(name)
                teams.append({
                    "league": league,
                    "team_name": name,
                    "conference": current_conf,
                    "division": current_div,
                    "city": "",
                    "state": "",
                    "team_url": "",
                })

    print(f"    Strategy 2 (body text): {len(teams)} teams")
    return teams


def split_team_names(text):
    """
    Split a run of concatenated team names like:
    'AC Connecticut Albany Rush Black Rock FC Boston Bolts'
    into individual team names.

    Strategy: Use regex to find sequences of capitalized words that form team names.
    A new team starts when we see a capitalized word that's not a continuation of
    an existing team name pattern.
    """
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []

    # Known team-name endings that indicate the last word of a team
    endings = {
        "FC", "SC", "AC", "United", "City", "FC.", "SC.", "AC.",
        "Rush", "Bucks", "Force", "Flames", "Stars", "Rangers",
        "Wanderers", "Athletics", "Athletic", "Soccer", "Club",
        "2", "II", "B", "U23", "U-23", "North", "South", "East", "West",
        "Bolts", "Hammers", "Menace", "Toucans", "Phantoms", "Raptors",
        "Legends", "Eagles", "Nomads", "Wolves", "Express", "Fury",
        "FC2", "II", "Diablo", "Sabres", "Surf", "Thunder",
        "Vaqueros", "Matadors", "Chupacabras", "Krewe", "Diablos",
        "Lobos", "Leviathan", "Royals", "Torrent", "Braveheart",
        "Stallions", "Roughnecks", "Assembly", "Forge", "Phoenix",
        "Clash", "Revolution", "Cosmos", "Fury", "Glory",
    }

    # Use a regex to split on boundaries between team names
    # Pattern: a new team starts with a capital letter after a word in `endings`
    # or after a digit (like "2" for reserves)

    # Simple tokenization by capital letters
    words = text.split(" ")
    teams = []
    current = []

    for word in words:
        if not word:
            continue
        # Check if this word starts a new team (capital + previous word was an ending)
        if (current and
                word and word[0].isupper() and
                current[-1] in endings):
            # Previous word was an ending → save current team, start new
            team_name = " ".join(current).strip()
            if team_name and len(team_name) > 2:
                teams.append(team_name)
            current = [word]
        else:
            current.append(word)

    # Save last team
    if current:
        team_name = " ".join(current).strip()
        if team_name and len(team_name) > 2:
            teams.append(team_name)

    return teams


def scrape_league(league, url, base, scraper):
    print(f"  Fetching {url}...")
    try:
        r = scraper.get(url, timeout=25)
        print(f"  Status: {r.status_code}, Length: {len(r.text)}")
        if r.status_code != 200:
            return []
    except Exception as e:
        print(f"  ERROR: {e}")
        return []
    return extract_teams_from_html(league, r.text, base)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "darwin", "mobile": False}
    )

    fields = ["league", "team_name", "conference", "division", "city", "state", "team_url"]
    all_teams = []

    for target in TARGETS:
        league = target["league"]
        print(f"\n=== {league} ===")
        teams = scrape_league(league, target["url"], target["base"], scraper)
        all_teams.extend(teams)
        print(f"  -> {len(teams)} teams")
        time.sleep(3)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_teams)

    print(f"\nSaved {len(all_teams)} total -> {OUT_CSV}")
    by_league = Counter(t["league"] for t in all_teams)
    for lg, cnt in by_league.most_common():
        print(f"  {lg}: {cnt}")


if __name__ == "__main__":
    main()
