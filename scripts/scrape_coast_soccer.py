#!/usr/bin/env python3
"""
Scrape Coast Soccer League (CSL) club and team data.
Covers two seasons:
  - Spring 2026 (79 clubs from clubs.html dropdown)
  - Fall 2025  (163 clubs from Logos?YEAR=2025&SEASON=FALL iframe)

Output: data/coast_soccer_clubs.csv  — club, club_id, season, coast_url
        data/coast_soccer_teams.csv  — club, club_id, team_name, age, gender, division, season
"""

import csv
import os
import time
import requests
from bs4 import BeautifulSoup

DATA_DIR = "data"
CLUBS_CSV = os.path.join(DATA_DIR, "coast_soccer_clubs.csv")
TEAMS_CSV = os.path.join(DATA_DIR, "coast_soccer_teams.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

BASE_URL = "https://coastsoccer.us/coastsoccer/clubs"


# ── Spring 2026 clubs (from clubs.html dropdown) ─────────────────────────────
SPRING_2026_CLUBS = [
    (412, "Alliance Indio"),
    (768, "Antelope Valley FC"),
    (417, "AYSO S1 Alliance"),
    (428, "AYSO United Redlands"),
    (903, "Brazil Stars Soccer Club"),
    (402, "C.D. Cobras"),
    (469, "California Madrid Elite"),
    (101, "California State SL"),
    (286, "Califut"),
    (273, "Central Coast Surf"),
    (249, "Club Real Atotonilco"),
    (416, "Coachella Valley SL"),
    (666, "Colton America SC"),
    (243, "Compton United FC"),
    (418, "Corona Sharks FC"),
    (889, "CYSA Premier Academy"),
    (973, "Desert Communities SC"),
    (934, "Desert Empire Surf"),
    (813, "Downey FC"),
    (946, "Downtown LA Soccer Club"),
    (421, "Evolution SC"),
    (466, "FarWest United"),
    (918, "FC California Velocity"),
    (285, "FC Katana"),
    (906, "FC United Academy"),
    (224, "FC Warriors"),
    (294, "Flyte SC"),
    (887, "Fontana FC"),
    (103, "Formadores SC"),
    (264, "Fullerton City FC"),
    (894, "Futbol Foundation of SC"),
    (104, "Galaxy United"),
    (762, "Guadalajara Valley FC"),
    (835, "Hemet Juventus"),
    (384, "Inglewood SC"),
    (537, "Inland United SC"),
    (959, "Inter-America Soccer Club"),
    (455, "Juventus Academy LA"),
    (815, "La Academia SC"),
    (225, "La Familia Soccer Club"),
    (251, "LA Futbol Academy"),
    (891, "La Mirada FC"),
    (935, "Lightning Soccer Club"),
    (274, "Los Futboleros FC"),
    (930, "Magnus FC"),
    (218, "Maquina FC"),
    (247, "Menifee Strykers"),
    (414, "Minor Soccer League"),
    (229, "Mount City Lobos FC"),
    (396, "Newbury Park Elite FC"),
    (821, "Nitemares Soccer Club"),
    (411, "OJSC"),
    (590, "Platinum IE"),
    (975, "Pumas USA"),
    (448, "Rancho Challenge FC"),
    (406, "Red Lions FC"),
    (783, "Rialto Fire"),
    (805, "Riverside FC"),
    (626, "Riverside MGFM S.C."),
    (398, "Royals Riverside"),
    (931, "SC Antelope"),
    (244, "SC Fire Legacy"),
    (269, "Sentinels FC"),
    (496, "Sherman Oaks Extreme SC"),
    (392, "So Cal Eagles"),
    (289, "Socal Blaze SC"),
    (886, "South Bay Falcons"),
    (831, "Spartans FC"),
    (989, "Sporting CA VC/Arsenal"),
    (443, "Sporting FC"),
    (387, "Sporting Revolution FC"),
    (301, "Strikers FC"),
    (947, "Team USA"),
    (236, "Titan Strikers"),
    (809, "Titans FC"),
    (257, "Torrance Soccer Club"),
    (657, "Union Independiente YSL"),
    (467, "Universal Soccer League"),
    (476, "USARMS"),
    (219, "Valley Futbol Club"),
    (486, "Veritas FC HD"),
    (942, "Worldwide SC"),
]

# ── Fall 2025 clubs (from Logos?YEAR=2025&SEASON=FALL iframe) ─────────────────
FALL_2025_CLUBS = [
    (502, "#502"),
    (242, "1570 FC"),
    (262, "805 Union"),
    (259, "A1 Since Day1 FC"),
    (389, "Alianza Azteca SC"),
    (412, "Alliance Indio"),
    (768, "Antelope Valley FC"),
    (404, "Arena FC"),
    (287, "Arete Futbol"),
    (238, "Ascend FC"),
    (292, "Aspire LASC"),
    (915, "Autobahn Soccer Club"),
    (417, "AYSO S1 Alliance"),
    (703, "Barcelona California SC"),
    (901, "Barcelona Santa Paula"),
    (903, "Brazil Stars Soccer Club"),
    (756, "California Elite SC"),
    (469, "California Madrid Elite"),
    (291, "California Natives FC"),
    (672, "California Stars Soccer"),
    (101, "California State SL"),
    (222, "California United FC"),
    (286, "Califut"),
    (228, "Cantera Soccer Academy"),
    (504, "CC Dynasty FC"),
    (402, "CD Cobras"),
    (431, "Central Coast Academy"),
    (273, "Central Coast Surf"),
    (924, "Central Coast United SC"),
    (258, "Champions YSL"),
    (462, "Chivas Soccer Academy SM"),
    (249, "Club Real Atotonilco"),
    (416, "Coachella Valley SL"),
    (666, "Colton America SC"),
    (243, "Compton United FC"),
    (418, "Corona Sharks FC"),
    (972, "Coyotes FC"),
    (498, "Crusaders FC"),
    (889, "CYSA Premier Academy"),
    (973, "Desert Communities SC"),
    (934, "Desert Empire Surf"),
    (234, "Development Academy of CA"),
    (946, "Downtown LA Soccer Club"),
    (281, "Dynamo LA"),
    (593, "Eagles Soccer Club"),
    (430, "EDA"),
    (241, "ENSO SC"),
    (421, "Evolution SC"),
    (285, "F.C. Katana"),
    (466, "FarWest United"),
    (918, "FC California Velocity"),
    (754, "FC Deportivo"),
    (906, "FC United Academy"),
    (486, "FCA Soccer Club"),
    (887, "Fontana FC"),
    (266, "Fontana Scorpions FC"),
    (103, "Formadores SC"),
    (264, "Fullerton City FC"),
    (894, "Futbol Foundation of SC"),
    (499, "Futbol Legacy"),
    (265, "Galacticos Soccer Club"),
    (104, "Galaxy United"),
    (277, "GB United"),
    (237, "Gladiators FC"),
    (965, "Glendale FC"),
    (762, "Guadalajara Valley FC"),
    (835, "Hemet Juventus"),
    (589, "HG Eagles"),
    (384, "Inglewood SC"),
    (240, "Inland Empire Coyotes FC"),
    (537, "Inland United SC"),
    (959, "Inter-America Soccer Club"),
    (425, "Jewel City United"),
    (275, "JOGA Bonito"),
    (268, "Juniors Soccer Academy"),
    (442, "JUSA Soccer"),
    (455, "Juventus Academy LA"),
    (815, "La Academia SC"),
    (856, "La Esperanza"),
    (225, "La Familia Soccer Club"),
    (251, "LA Futbol Academy"),
    (891, "La Mirada FC"),
    (464, "LA Power FC"),
    (413, "La Quinta FC"),
    (288, "LA United FC"),
    (458, "Legends Futbol Academy"),
    (296, "Leon FC"),
    (391, "Leopardos FC"),
    (935, "Lightning Soccer Club"),
    (490, "Los Angeles Bulls"),
    (388, "Los Angeles Racing Club"),
    (274, "Los Futboleros FC"),
    (930, "Magnus FC"),
    (987, "Manchester United"),
    (247, "Menifee Strykers"),
    (414, "Minor Soccer League"),
    (229, "Mount City Lobos FC"),
    (949, "MSA FC"),
    (951, "Necaxa USA FC"),
    (396, "Newbury Park Elite FC"),
    (227, "Nido Aguila SC"),
    (821, "Nitemares Soccer Club"),
    (623, "Oaks FC"),
    (451, "Olimpico FC"),
    (870, "Oxnard Eagles"),
    (435, "Oxnard Football Club"),
    (445, "Oxnard Kickers FC"),
    (794, "Oxnard PAL Soccer Club"),
    (468, "Oxnard Real Athletic Club"),
    (297, "Oxnard Soccer League"),
    (279, "Oxnard Tigres FC"),
    (839, "Oxnard United SC"),
    (497, "Pacific Coast SC"),
    (252, "Paramount FC"),
    (590, "Platinum IE"),
    (283, "Pomona Pride FC"),
    (226, "Possible FC"),
    (253, "Premier Touch FC"),
    (410, "Pride FC"),
    (461, "Pro Alliance FC"),
    (927, "Project 2000 Soccer"),
    (851, "Pumas La Habra"),
    (381, "Pumas LA Soccer Academy"),
    (975, "Pumas USA"),
    (448, "Rancho Challenge FC"),
    (403, "Real La Habra FC"),
    (239, "Real Santa Barbara FC"),
    (250, "Rebano Chivas Academy LA"),
    (406, "Red Lions FC"),
    (254, "Regal Soccer Academy"),
    (783, "Rialto Fire"),
    (293, "Rising Stars SC"),
    (233, "Riverside Elite SA"),
    (805, "Riverside FC"),
    (626, "Riverside MGFM S.C."),
    (398, "Royals Riverside"),
    (395, "San Pedro Pachuca FC"),
    (594, "Santa Anita SC"),
    (629, "Santa Barbara Soccer Club"),
    (967, "Santa Paula FC Xtreme"),
    (828, "Santa Ynez Futbol Club"),
    (270, "Santa Ynez Valley FA"),
    (932, "Santos Laguna Oxnard"),
    (931, "SC Antelope"),
    (244, "SC Fire Legacy"),
    (269, "Sentinels FC"),
    (280, "SFV Sporting Union"),
    (496, "Sherman Oaks Extreme SC"),
    (944, "Simi Valley FC Premier"),
    (392, "So Cal Eagles"),
    (474, "SoCal Elite FC"),
    (886, "South Bay Falcons"),
    (246, "South LA Youth Academy"),
    (831, "Spartans FC"),
    (970, "Spartans YSA"),
    (282, "Sporting Bakersfield SC"),
    (443, "Sporting FC"),
    (386, "Sporting Fontana"),
    (387, "Sporting Revolution FC"),
    (105, "TastClubs"),
    (947, "Team USA"),
    (236, "Titan Strikers"),
    (257, "Torrance Soccer Club"),
    (419, "Unico FC"),
    (657, "Union Independiente YSL"),
    (260, "United FC"),
    (467, "Universal Soccer League"),
    (476, "USARMS"),
    (984, "VC Galaxy"),
    (792, "Ventura County Fusion YSA"),
    (693, "Ventura County United"),
    (737, "Ventura Surf Soccer Club"),
    (432, "WAYS Soccer"),
    (942, "Worldwide SC"),
    (231, "Xclusive F.C"),
    (447, "ZeroGravity Academy"),
]


def get_soup(url, timeout=15):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def scrape_club_teams(club_id, club_name, year, season):
    url = f"{BASE_URL}?YEAR={year}&SEASON={season}&CLUB={club_id}"
    teams = []
    try:
        soup = get_soup(url)
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            header_cells = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]
            if not any(h in header_cells for h in ["team", "age", "division", "gender", "group"]):
                continue
            for row in rows[1:]:
                cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
                if not any(cells):
                    continue
                row_data = dict(zip(header_cells, cells))
                team_name = row_data.get("team", row_data.get("team name", cells[0] if cells else ""))
                age = row_data.get("age", row_data.get("age group", ""))
                gender = row_data.get("gender", row_data.get("sex", ""))
                division = row_data.get("division", row_data.get("group", ""))
                if team_name:
                    teams.append({
                        "club": club_name,
                        "club_id": club_id,
                        "team_name": team_name,
                        "age": age,
                        "gender": gender,
                        "division": division,
                        "season": f"{season} {year}",
                        "source_url": url,
                    })

        if not teams:
            page_text = soup.get_text()
            if club_name.lower() in page_text.lower() or str(club_id) in page_text:
                teams.append({
                    "club": club_name,
                    "club_id": club_id,
                    "team_name": f"{club_name} (page found, no team table)",
                    "age": "", "gender": "", "division": "",
                    "season": f"{season} {year}",
                    "source_url": url,
                })

    except Exception as e:
        print(f"    ERROR [{club_name}]: {type(e).__name__}: {e}")

    return teams


def main():
    seasons = [
        ("2026", "spring", SPRING_2026_CLUBS),
        ("2025", "fall",   FALL_2025_CLUBS),
    ]

    # Write clubs CSV — one row per (club_id, season)
    club_rows = []
    seen = set()
    for year, season, clubs in seasons:
        for cid, name in clubs:
            key = (cid, season, year)
            if key not in seen:
                seen.add(key)
                club_rows.append({
                    "club": name,
                    "club_id": cid,
                    "season": f"{season} {year}",
                    "league": "Coast Soccer",
                    "region": "SoCal",
                    "coast_url": f"{BASE_URL}?YEAR={year}&SEASON={season}&CLUB={cid}",
                })

    with open(CLUBS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["club", "club_id", "season", "league", "region", "coast_url"])
        writer.writeheader()
        writer.writerows(club_rows)
    print(f"Saved {len(club_rows)} club-season rows to {CLUBS_CSV}")

    # Scrape each club for teams
    all_teams = []
    total = sum(len(c) for _, _, c in seasons)
    i = 0

    for year, season, clubs in seasons:
        print(f"\n--- {season.capitalize()} {year} ({len(clubs)} clubs) ---")
        for club_id, club_name in clubs:
            i += 1
            print(f"  [{i}/{total}] {club_name} (ID: {club_id}, {season} {year})")
            teams = scrape_club_teams(club_id, club_name, year, season)
            print(f"    -> {len(teams)} teams")
            all_teams.extend(teams)

            if i % 20 == 0:
                with open(TEAMS_CSV, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["club", "club_id", "team_name", "age", "gender", "division", "season", "source_url"]
                    )
                    writer.writeheader()
                    writer.writerows(all_teams)
                print(f"    [checkpoint: {len(all_teams)} teams saved]")

            time.sleep(2)

    with open(TEAMS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["club", "club_id", "team_name", "age", "gender", "division", "season", "source_url"]
        )
        writer.writeheader()
        writer.writerows(all_teams)

    print(f"\nDone.")
    print(f"  Clubs: {len(club_rows)} -> {CLUBS_CSV}")
    print(f"  Teams: {len(all_teams)} -> {TEAMS_CSV}")

    from collections import Counter
    ages = Counter(t["age"] for t in all_teams if t["age"])
    print("\n--- Teams by Age ---")
    for age, count in sorted(ages.items()):
        print(f"  {age}: {count}")


if __name__ == "__main__":
    main()
