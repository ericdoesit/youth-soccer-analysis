#!/usr/bin/env python3
"""
Build CSV from hardcoded National League club directory (2025-26 season).
Source: https://www.thenationalleague.com/club-directory-2025-2026-season/
108 clubs across Girls P1, Girls P2, Boys P1, Boys P2 in regional divisions.

Output: data/national_league_clubs.csv
"""

import csv
import os

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "national_league_clubs.csv")

# (division, gender, tier, region, club_name, state_code)
CLUBS = [
    # ── GIRLS PREMIER 1 ───────────────────────────────────────────────────────
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "Atletico Dallas Youth",            "TX"),
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "BVB International Academy Texas",   "TX"),
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "D'Feeters Kicks Soccer Club",       "TX"),
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "Dallas Surf Soccer Club",           "TX"),
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "HTX Soccer Club",                   "TX"),
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "Houston Surf Soccer Club",          "TX"),
    ("Girls Premier 1", "Girls", "P1", "Frontier",    "Solar Soccer Club",                 "TX"),
    ("Girls Premier 1", "Girls", "P1", "Great Lakes", "Club Ohio",                         "OH"),
    ("Girls Premier 1", "Girls", "P1", "Great Lakes", "FC Dayton",                         "OH"),
    ("Girls Premier 1", "Girls", "P1", "Great Lakes", "Fort Wayne United Futbol Club",     "IN"),
    ("Girls Premier 1", "Girls", "P1", "Great Lakes", "Indy Eleven Academy",               "IN"),
    ("Girls Premier 1", "Girls", "P1", "Great Lakes", "NWI Lions United",                  "IN"),
    ("Girls Premier 1", "Girls", "P1", "Great Lakes", "Total Futbol Academy",              "OH"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "AYSO United So Cal",                "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "CDA Slammers",                      "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Empire Surf",                       "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Excel Soccer Academy",              "AZ"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "FC Premier",                        "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Legends FC",                        "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Legends FC San Diego",              "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Legends FC SD North",               "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Los Angeles Soccer Club",           "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Phoenix Rising FC",                 "AZ"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Rebels San Diego Soccer Club",      "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Sporting California",               "CA"),
    ("Girls Premier 1", "Girls", "P1", "Pacific",     "Strikers FC",                       "CA"),
    ("Girls Premier 1", "Girls", "P1", "Piedmont",    "Alliance Soccer Club",              "GA"),
    ("Girls Premier 1", "Girls", "P1", "Piedmont",    "Atlanta Fire United Soccer Assoc",  "GA"),
    ("Girls Premier 1", "Girls", "P1", "Piedmont",    "Bulls Rush FC",                     "SC"),
    ("Girls Premier 1", "Girls", "P1", "Piedmont",    "Carolina Elite Soccer Academy",     "SC"),
    ("Girls Premier 1", "Girls", "P1", "Piedmont",    "Charlotte Soccer Academy",          "NC"),
    ("Girls Premier 1", "Girls", "P1", "Piedmont",    "United FC-Furman",                  "SC"),
    # ── GIRLS PREMIER 2 ───────────────────────────────────────────────────────
    ("Girls Premier 2", "Girls", "P2", "Desert",      "Arizona Arsenal Soccer Club",       "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Desert",      "Arizona Rush",                      "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Desert",      "AYSO United Arizona",               "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Desert",      "CCV Stars",                         "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Desert",      "FC Tucson Youth",                   "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Desert",      "RSL-AZ West Valley",                "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Desert",      "RSL-AZ Southern",                   "AZ"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Cincinnati United Premier",         "OH"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Cincinnati West Soccer Club",       "OH"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Elite FC",                          "OH"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Fairfield Optimist Soccer Club",    "OH"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Hoosier Futbol Club",               "IN"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Indy Eleven Academy",               "IN"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Indy Premier SC",                   "IN"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Kings Hammer - NKY Academy",        "KY"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Lexington Sporting Club",           "KY"),
    ("Girls Premier 2", "Girls", "P2", "Great Lakes", "Union FC Indy",                     "IN"),
    ("Girls Premier 2", "Girls", "P2", "Lake Shores", "Libertyville FC 1974",              "IL"),
    ("Girls Premier 2", "Girls", "P2", "Lake Shores", "MI Jaguars FC",                     "MI"),
    ("Girls Premier 2", "Girls", "P2", "Lake Shores", "Michigan Futbol Academy",           "MI"),
    ("Girls Premier 2", "Girls", "P2", "Lake Shores", "Michigan Tigers",                   "MI"),
    ("Girls Premier 2", "Girls", "P2", "Lake Shores", "Team Chicago",                      "IL"),
    ("Girls Premier 2", "Girls", "P2", "North",       "Chicago Inferno",                   "IL"),
    ("Girls Premier 2", "Girls", "P2", "North",       "Croatian Eagles Soccer Club",       "WI"),
    ("Girls Premier 2", "Girls", "P2", "North",       "Evolution Soccer Club",             "IL"),
    ("Girls Premier 2", "Girls", "P2", "North",       "FC Stars Soccer Club",              "IL"),
    ("Girls Premier 2", "Girls", "P2", "North",       "Raptors / Crystal Lake Force",      "IL"),
    ("Girls Premier 2", "Girls", "P2", "North",       "WIUFC",                             "WI"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "CDA Slammers",                      "CA"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "Crusaders Soccer Club",             "CA"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "FC Man United",                     "CA"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "Legends FC - San Diego",            "CA"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "Legends FC SD North",               "CA"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "Soccer Club of Oceanside",          "CA"),
    ("Girls Premier 2", "Girls", "P2", "Pacific",     "Southwest Sporting",                "CA"),
    # ── BOYS PREMIER 1 ────────────────────────────────────────────────────────
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "Atletico Dallas Youth",             "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "Dallas Surf SC",                    "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "D'Feeters Kicks SC",                "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "HTX SC",                            "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "Houston Surf",                      "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "Solar SC",                          "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Frontier",    "Sting SC",                          "TX"),
    ("Boys Premier 1",  "Boys",  "P1", "Great Lakes", "Century United of Pittsburgh",      "PA"),
    ("Boys Premier 1",  "Boys",  "P1", "Great Lakes", "Fort Wayne United Futbol Club",     "IN"),
    ("Boys Premier 1",  "Boys",  "P1", "Great Lakes", "Hoosier Futbol Club",               "IN"),
    ("Boys Premier 1",  "Boys",  "P1", "Great Lakes", "Indy Premier SC",                   "IN"),
    ("Boys Premier 1",  "Boys",  "P1", "Great Lakes", "Pittsburgh Independence",           "PA"),
    ("Boys Premier 1",  "Boys",  "P1", "Great Lakes", "Spire FC",                          "OH"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "Central Illinois United",           "IL"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "FC 1974 Libertyville",              "IL"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "Madison 56ers",                     "WI"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "Michigan Rangers FC",               "MI"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "Midwest United SCOR",               "MI"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "PFC - Evo",                         "IL"),
    ("Boys Premier 1",  "Boys",  "P1", "Midwest",     "TKO Premier SC",                    "MI"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "Cedar Stars Academy - Hudson Valley","NY"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "Cedar Stars Academy - North",       "NJ"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "French Football Academy",           "NY"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "Future Soccer Academy",             "NJ"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "PDA SC Vistula",                    "NJ"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "Players Development Academy Hibernian","NJ"),
    ("Boys Premier 1",  "Boys",  "P1", "Northeast",   "PSC Academy",                       "NJ"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Empire Surf",                       "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Excel Soccer Academy",              "AZ"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "FC Deportivo AZ",                   "AZ"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Legends FC",                        "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Legends FC San Diego",              "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Legends FC SD North",               "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Los Angeles Soccer Club",           "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Nomads Soccer Club",                "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Phoenix Rising FC",                 "AZ"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Playmaker Futbol Academy",          "AZ"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Rebels San Diego Soccer Club",      "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Soccer Club of Oceanside Breakers", "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Southwest SC Sporting USA",         "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Pacific",     "Strikers FC",                       "CA"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "GGS - Brave SC",                    "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "Juventus Academy Miami",            "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "Miami Breakers FC",                 "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "One FC",                            "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "Pinecrest Premier Soccer Club",     "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "SABR Team Boca",                    "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "Strikers Miami FC",                 "FL"),
    ("Boys Premier 1",  "Boys",  "P1", "Southeast",   "West Pines United FC",              "FL"),
    # ── BOYS PREMIER 2 ────────────────────────────────────────────────────────
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "Barca Academy Chicago",             "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "Chicago City Soccer Club",          "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "Chicago Kics Football Club",        "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "Evolution Soccer Club",             "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "FC Stars Soccer Club",              "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "Galaxy Soccer Club",                "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "Millennium Soccer Association",     "IN"),
    ("Boys Premier 2",  "Boys",  "P2", "Chicagoland", "NWI Lions United",                  "IN"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Arizona Arsenal Soccer Club",       "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Arizona Soccer Club - Thunder",     "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Brazas Futebol Club",               "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "CCV Stars",                         "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "FC Tucson Youth",                   "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "North Scottsdale SC Sandsharks",    "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Paris Saint-Germain Academy Phoenix","AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Phoenix Rising FC SE Valley",       "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Phoenix Rising FC West Valley",     "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "RSL-AZ Southern",                   "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "RSL-AZ West Valley",                "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Desert",      "Spartans FC Academy",               "AZ"),
    ("Boys Premier 2",  "Boys",  "P2", "Erie Shores", "Cincinnati United SC",              "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Erie Shores", "Cleveland Football Academy",        "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Erie Shores", "Club Ohio",                         "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Erie Shores", "Elite FC",                          "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Erie Shores", "FC Dayton",                         "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Erie Shores", "Toledo Celtics SC",                 "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Gateway",     "KC Fusion Soccer Club",             "KS"),
    ("Boys Premier 2",  "Boys",  "P2", "Gateway",     "OP Soccer Club",                    "KS"),
    ("Boys Premier 2",  "Boys",  "P2", "Gateway",     "St. Louis Scott Gallagher",         "MO"),
    ("Boys Premier 2",  "Boys",  "P2", "Gateway",     "Toca FC",                           "KS"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "Chicago Inferno",                   "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "Croatian Eagles Soccer Club",       "WI"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "Elmbrook United",                   "WI"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "FC Wisconsin",                      "WI"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "FC1 Academy",                       "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "Libertyville FC 1974",              "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "Madison 56ers",                     "WI"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "North Shore United Soccer Club",    "WI"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "Rockford Raptors FC",               "IL"),
    ("Boys Premier 2",  "Boys",  "P2", "North",       "WIUFC",                             "WI"),
    ("Boys Premier 2",  "Boys",  "P2", "Ohio Valley", "Columbus Express",                  "IN"),
    ("Boys Premier 2",  "Boys",  "P2", "Ohio Valley", "Indy Premier SC",                   "IN"),
    ("Boys Premier 2",  "Boys",  "P2", "Ohio Valley", "Kings Hammer - NKY Academy",        "KY"),
    ("Boys Premier 2",  "Boys",  "P2", "Ohio Valley", "Total Futbol Academy",              "OH"),
    ("Boys Premier 2",  "Boys",  "P2", "Ohio Valley", "Union FC Indy",                     "IN"),
    ("Boys Premier 2",  "Boys",  "P2", "Ohio Valley", "USA of Indiana",                    "IN"),
    ("Boys Premier 2",  "Boys",  "P2", "Pacific",     "AYSO United CA",                    "CA"),
    ("Boys Premier 2",  "Boys",  "P2", "Pacific",     "Crusaders SC",                      "CA"),
    ("Boys Premier 2",  "Boys",  "P2", "Pacific",     "FC Man United",                     "CA"),
    ("Boys Premier 2",  "Boys",  "P2", "Pacific",     "Legends FC San Diego",              "CA"),
    ("Boys Premier 2",  "Boys",  "P2", "Pacific",     "Legends FC SD North",               "CA"),
    ("Boys Premier 2",  "Boys",  "P2", "Pacific",     "SoCal Elite FC",                    "CA"),
    ("Boys Premier 2",  "Boys",  "P2", "Piedmont",    "Bulls Soccer Club",                 "SC"),
    ("Boys Premier 2",  "Boys",  "P2", "Piedmont",    "Carolina Elite Soccer Academy",     "SC"),
    ("Boys Premier 2",  "Boys",  "P2", "Piedmont",    "Charleston Soccer Club",            "SC"),
    ("Boys Premier 2",  "Boys",  "P2", "Piedmont",    "Coast Futbol Alliance",             "SC"),
    ("Boys Premier 2",  "Boys",  "P2", "Piedmont",    "South Carolina United FC",          "SC"),
    ("Boys Premier 2",  "Boys",  "P2", "Piedmont",    "United FC-Furman",                  "SC"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "Doral SC",                          "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "Key Biscayne SC",                   "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "PSG Academy FL",                    "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "PSL Soccer Club Hurricanes Inc",    "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "Strikers Miami FC",                 "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "Tropical SC",                       "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "W&H America",                       "FL"),
    ("Boys Premier 2",  "Boys",  "P2", "Sunshine",    "West Pines United FC",              "FL"),
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    fields = ["division", "gender", "tier", "region", "club_name", "state",
              "league", "source_url"]
    rows = []
    for division, gender, tier, region, club_name, state in CLUBS:
        rows.append({
            "division": division,
            "gender": gender,
            "tier": tier,
            "region": region,
            "club_name": club_name,
            "state": state,
            "league": "The National League",
            "source_url": "https://www.thenationalleague.com/club-directory-2025-2026-season/",
        })

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} National League clubs -> {OUT_CSV}")

    from collections import Counter
    by_state = Counter(r["state"] for r in rows)
    print("\n--- Clubs by state (top 10) ---")
    for state, count in by_state.most_common(10):
        print(f"  {state:<4s} {count}")


if __name__ == "__main__":
    main()
