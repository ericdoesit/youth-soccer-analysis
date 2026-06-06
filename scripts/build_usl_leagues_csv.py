#!/usr/bin/env python3
"""
Build CSVs for USL leagues from Wikipedia data.
- USL W League (amateur women's): 87 teams
- USL League One (semi-pro men's): 17 teams
- USL Championship (pro men's): 25 teams
- USL Super League (pro women's): 8 teams

Outputs:
  data/usl_w_league_clubs.csv
  data/usl_league_one_clubs.csv
  data/usl_championship_clubs.csv
  data/usl_super_league_clubs.csv
"""

import csv, os
from collections import Counter

DATA_DIR = "data"

# ─── USL W LEAGUE ──────────────────────────────────────────────────────────────
# Source: Wikipedia 2025 USL W League season
USL_W = [
    # Eastern Conference
    # Chesapeake Division
    ("Eastern", "Chesapeake",   "Annapolis Blues FC",              "Annapolis",        "MD"),
    ("Eastern", "Chesapeake",   "Virginia Beach United FC",        "Virginia Beach",   "VA"),
    ("Eastern", "Chesapeake",   "Richmond Ivy SC",                 "Richmond",         "VA"),
    ("Eastern", "Chesapeake",   "Charlottesville Blues FC",        "Charlottesville",  "VA"),
    ("Eastern", "Chesapeake",   "Virginia Atlantic FC",            "Virginia",         "VA"),
    # Metropolitan Division
    ("Eastern", "Metropolitan", "Long Island Rough Riders",        "Long Island",      "NY"),
    ("Eastern", "Metropolitan", "Paisley Athletic FC",             "Paisley",          "NJ"),
    ("Eastern", "Metropolitan", "Morris Elite SC",                 "Morris",           "NJ"),
    ("Eastern", "Metropolitan", "Cedar Stars Academy",             "Connecticut",      "CT"),
    ("Eastern", "Metropolitan", "Hudson Valley Crusaders",         "Hudson Valley",    "NY"),
    ("Eastern", "Metropolitan", "AC Connecticut",                  "Connecticut",      "CT"),
    ("Eastern", "Metropolitan", "New Jersey Copa FC",              "New Jersey",       "NJ"),
    ("Eastern", "Metropolitan", "Manhattan SC",                    "Manhattan",        "NY"),
    # Mid Atlantic Division
    ("Eastern", "Mid Atlantic", "Eagle FC",                        "Pennsylvania",     "PA"),
    ("Eastern", "Mid Atlantic", "Northern Virginia FC",            "Northern Virginia","VA"),
    ("Eastern", "Mid Atlantic", "Virginia Marauders FC",           "Virginia",         "VA"),
    ("Eastern", "Mid Atlantic", "Lancaster Inferno FC",            "Lancaster",        "PA"),
    ("Eastern", "Mid Atlantic", "Patuxent Football Athletics",     "Maryland",         "MD"),
    # South Atlantic Division
    ("Eastern", "South Atlantic","North Carolina Courage U23",     "North Carolina",   "NC"),
    ("Eastern", "South Atlantic","South Carolina United FC",       "South Carolina",   "SC"),
    ("Eastern", "South Atlantic","Charlotte Eagles",               "Charlotte",        "NC"),
    ("Eastern", "South Atlantic","Tormenta FC",                    "Savannah",         "GA"),
    ("Eastern", "South Atlantic","Carolina Ascent FC",             "North Carolina",   "NC"),
    ("Eastern", "South Atlantic","North Carolina Fusion U23",      "North Carolina",   "NC"),
    ("Eastern", "South Atlantic","Wake FC",                        "North Carolina",   "NC"),
    # Central Conference
    # Great Forest Division
    ("Central", "Great Forest",  "Pittsburgh Riveters SC",         "Pittsburgh",       "PA"),
    ("Central", "Great Forest",  "Cleveland Force SC",             "Cleveland",        "OH"),
    ("Central", "Great Forest",  "FC Buffalo",                     "Buffalo",          "NY"),
    ("Central", "Great Forest",  "Steel City FC",                  "Pittsburgh",       "PA"),
    ("Central", "Great Forest",  "Flower City 1872",               "Rochester",        "NY"),
    ("Central", "Great Forest",  "Erie Sports Center FC",          "Erie",             "PA"),
    # Great Lakes Division
    ("Central", "Great Lakes",   "Detroit City FC",                "Detroit",          "MI"),
    ("Central", "Great Lakes",   "AFC Ann Arbor",                  "Ann Arbor",        "MI"),
    ("Central", "Great Lakes",   "Kalamazoo FC",                   "Kalamazoo",        "MI"),
    ("Central", "Great Lakes",   "Midwest United FC",              "Michigan",         "MI"),
    ("Central", "Great Lakes",   "Union FC Macomb",                "Macomb",           "MI"),
    ("Central", "Great Lakes",   "Toledo Villa FC",                "Toledo",           "OH"),
    # Heartland Division
    ("Central", "Heartland",     "Minnesota Aurora FC",            "Minnesota",        "MN"),
    ("Central", "Heartland",     "Sioux Falls City FC",            "Sioux Falls",      "SD"),
    ("Central", "Heartland",     "River Light FC",                 "Minnesota",        "MN"),
    ("Central", "Heartland",     "Rochester FC",                   "Rochester",        "MN"),
    ("Central", "Heartland",     "Chicago Dutch Lions",            "Chicago",          "IL"),
    ("Central", "Heartland",     "RKC Third Coast",                "Minnesota",        "MN"),
    # Valley Division
    ("Central", "Valley",        "Kings Hammer FC Cincinnati",     "Cincinnati",       "OH"),
    ("Central", "Valley",        "Racing Louisville FC",           "Louisville",       "KY"),
    ("Central", "Valley",        "Indy Eleven",                    "Indianapolis",     "IN"),
    ("Central", "Valley",        "Lexington SC",                   "Lexington",        "KY"),
    ("Central", "Valley",        "Dayton Dutch Lions FC",          "Dayton",           "OH"),
    # Southern Conference
    # Lone Star Division
    ("Southern","Lone Star",     "Lonestar SC",                    "Texas",            "TX"),
    ("Southern","Lone Star",     "AHFC Royals",                    "Houston",          "TX"),
    ("Southern","Lone Star",     "Challenge SC",                   "Texas",            "TX"),
    ("Southern","Lone Star",     "Lonestar San Antonio",           "San Antonio",      "TX"),
    ("Southern","Lone Star",     "San Antonio Athenians SC",       "San Antonio",      "TX"),
    # South Central Division
    ("Southern","South Central", "Asheville City SC",              "Asheville",        "NC"),
    ("Southern","South Central", "Greenville Liberty SC",          "Greenville",       "SC"),
    ("Southern","South Central", "Southern Soccer Academy",        "Tennessee",        "TN"),
    ("Southern","South Central", "Chattanooga Red Wolves SC",      "Chattanooga",      "TN"),
    ("Southern","South Central", "Birmingham Legion FC",           "Birmingham",       "AL"),
    ("Southern","South Central", "Tennessee SC",                   "Tennessee",        "TN"),
    ("Southern","South Central", "One Knoxville SC",               "Knoxville",        "TN"),
    # Southeast Division
    ("Southern","Southeast",     "Sporting Club Jacksonville",     "Jacksonville",     "FL"),
    ("Southern","Southeast",     "TLH Reckoning",                  "Tallahassee",      "FL"),
    ("Southern","Southeast",     "Fort Lauderdale United FC",      "Fort Lauderdale",  "FL"),
    ("Southern","Southeast",     "Kings Hammer FC Sun City",       "Florida",          "FL"),
    ("Southern","Southeast",     "Brevard SC Riptide",             "Brevard County",   "FL"),
    ("Southern","Southeast",     "FC Miami City",                  "Miami",            "FL"),
    ("Southern","Southeast",     "Brooke House FC",                "Florida",          "FL"),
    ("Southern","Southeast",     "Miami AC",                       "Miami",            "FL"),
    # Western Conference
    # Mountain Division
    ("Western", "Mountain",      "Utah United",                    "Utah",             "UT"),
    ("Western", "Mountain",      "Colorado Storm",                 "Colorado",         "CO"),
    ("Western", "Mountain",      "Albion SC Colorado",             "Colorado",         "CO"),
    ("Western", "Mountain",      "Flatirons Rush",                 "Colorado",         "CO"),
    ("Western", "Mountain",      "Colorado International Soccer Academy", "Colorado",  "CO"),
    # Northwest Division
    ("Western", "Northwest",     "FC Olympia",                     "Olympia",          "WA"),
    ("Western", "Northwest",     "West Seattle Rhodies FC",        "Seattle",          "WA"),
    ("Western", "Northwest",     "Salmon Bay FC",                  "Seattle",          "WA"),
    ("Western", "Northwest",     "Lane United FC",                 "Lane County",      "OR"),
    ("Western", "Northwest",     "Tacoma Galaxy",                  "Tacoma",           "WA"),
    ("Western", "Northwest",     "Bigfoot FC",                     "Washington",       "WA"),
    # Nor Cal Division
    ("Western", "Nor Cal",       "Stockton Cargo SC",              "Stockton",         "CA"),
    ("Western", "Nor Cal",       "Oakland Soul SC",                "Oakland",          "CA"),
    ("Western", "Nor Cal",       "Pleasanton RAGE",                "Pleasanton",       "CA"),
    ("Western", "Nor Cal",       "California Storm",               "California",       "CA"),
    ("Western", "Nor Cal",       "Marin FC Siren",                 "Marin",            "CA"),
    ("Western", "Nor Cal",       "Olympic Club SC",                "San Francisco",    "CA"),
    ("Western", "Nor Cal",       "San Francisco Glens",            "San Francisco",    "CA"),
    ("Western", "Nor Cal",       "Academica SC",                   "Sacramento",       "CA"),
    # SoCal Division
    ("Western", "SoCal",         "Santa Clarita Blue Heat",        "Santa Clarita",    "CA"),
    ("Western", "SoCal",         "Capo FC",                        "Orange County",    "CA"),
    ("Western", "SoCal",         "Southern California Dutch Lions","Southern CA",      "CA"),
    ("Western", "SoCal",         "OC Sporting FC",                 "Orange County",    "CA"),
    ("Western", "SoCal",         "AMSG FC",                        "Southern CA",      "CA"),
]

# ─── USL LEAGUE ONE ─────────────────────────────────────────────────────────────
# Source: Wikipedia 2026 USL League One season — 17 teams
USL_L1 = [
    ("Athletic Club Boise",       "Garden City",  "ID"),
    ("AV Alta FC",                "Lancaster",    "CA"),
    ("Charlotte Independence",    "Charlotte",    "NC"),
    ("Chattanooga Red Wolves SC", "East Ridge",   "TN"),
    ("Corpus Christi FC",         "Corpus Christi","TX"),
    ("Fort Wayne FC",             "Fort Wayne",   "IN"),
    ("Forward Madison FC",        "Madison",      "WI"),
    ("Greenville Triumph SC",     "Greenville",   "SC"),
    ("FC Naples",                 "Naples",       "FL"),
    ("New York Cosmos",           "Paterson",     "NJ"),
    ("One Knoxville SC",          "Knoxville",    "TN"),
    ("Portland Hearts of Pine",   "Portland",     "ME"),
    ("Richmond Kickers",          "Richmond",     "VA"),
    ("Sarasota Paradise",         "Lakewood Ranch","FL"),
    ("Spokane Velocity FC",       "Spokane",      "WA"),
    ("Union Omaha",               "Omaha",        "NE"),
    ("Westchester SC",            "Mount Vernon", "NY"),
]

# ─── USL CHAMPIONSHIP ──────────────────────────────────────────────────────────
# Source: Wikipedia 2026 USL Championship season — 25 teams (pro)
USL_CHAMP = [
    # Eastern Conference
    ("Eastern", "Birmingham Legion FC",       "Birmingham",         "AL"),
    ("Eastern", "Brooklyn FC",               "Brooklyn",           "NY"),
    ("Eastern", "Charleston Battery",        "Charleston",         "SC"),
    ("Eastern", "Detroit City FC",           "Detroit",            "MI"),
    ("Eastern", "Hartford Athletic",         "Hartford",           "CT"),
    ("Eastern", "Indy Eleven",               "Indianapolis",       "IN"),
    ("Eastern", "Louisville City FC",        "Louisville",         "KY"),
    ("Eastern", "Loudoun United FC",         "Leesburg",           "VA"),
    ("Eastern", "Miami FC",                  "Miami",              "FL"),
    ("Eastern", "Pittsburgh Riverhounds SC", "Pittsburgh",         "PA"),
    ("Eastern", "Rhode Island FC",           "Providence",         "RI"),
    ("Eastern", "Sporting Club Jacksonville","Jacksonville",       "FL"),
    ("Eastern", "Tampa Bay Rowdies",         "Tampa",              "FL"),
    # Western Conference
    ("Western", "Colorado Springs Switchbacks FC","Colorado Springs","CO"),
    ("Western", "El Paso Locomotive FC",     "El Paso",            "TX"),
    ("Western", "FC Tulsa",                  "Tulsa",              "OK"),
    ("Western", "Las Vegas Lights FC",       "Las Vegas",          "NV"),
    ("Western", "Lexington SC",              "Lexington",          "KY"),
    ("Western", "Monterey Bay FC",           "Monterey",           "CA"),
    ("Western", "New Mexico United",         "Albuquerque",        "NM"),
    ("Western", "Oakland Roots SC",          "Oakland",            "CA"),
    ("Western", "Orange County SC",          "Irvine",             "CA"),
    ("Western", "Phoenix Rising FC",         "Phoenix",            "AZ"),
    ("Western", "Sacramento Republic FC",    "Sacramento",         "CA"),
    ("Western", "San Antonio FC",            "San Antonio",        "TX"),
]

# ─── USL SUPER LEAGUE ──────────────────────────────────────────────────────────
# Source: Gainbridge Super League / uslsuperleague.com 2025-26 season — 9 teams (pro women's)
USL_SUPER = [
    ("Brooklyn FC",               "New York City",    "NY"),
    ("Carolina Ascent FC",        "Charlotte",        "NC"),
    ("Dallas Trinity FC",         "Dallas",           "TX"),
    ("DC Power Football Club",    "Washington",       "DC"),
    ("Fort Lauderdale United FC", "Fort Lauderdale",  "FL"),
    ("Lexington SC",              "Lexington",        "KY"),
    ("Spokane Zephyr FC",         "Spokane",          "WA"),
    ("Sporting JAX",              "Jacksonville",     "FL"),
    ("Tampa Bay Sun FC",          "Tampa",            "FL"),
]


def write_csv(path, fields, rows):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    by_state = Counter(r["state"] for r in rows)
    print(f"  Saved {len(rows)} rows -> {path}")
    print(f"  Top states: " + ", ".join(f"{s}({c})" for s, c in by_state.most_common(5)))


def main():
    # W League
    w_rows = [{
        "conference": conf, "division": div, "club_name": name,
        "city": city, "state": state, "league": "USL W League",
        "source_url": "https://en.wikipedia.org/wiki/2025_USL_W_League_season",
    } for conf, div, name, city, state in USL_W]
    write_csv(os.path.join(DATA_DIR, "usl_w_league_clubs.csv"),
              ["conference","division","club_name","city","state","league","source_url"], w_rows)

    # League One
    l1_rows = [{
        "team_name": name, "city": city, "state": state,
        "league": "USL League One",
        "source_url": "https://en.wikipedia.org/wiki/2026_USL_League_One_season",
    } for name, city, state in USL_L1]
    write_csv(os.path.join(DATA_DIR, "usl_league_one_clubs.csv"),
              ["team_name","city","state","league","source_url"], l1_rows)

    # Championship
    champ_rows = [{
        "conference": conf, "team_name": name, "city": city, "state": state,
        "league": "USL Championship",
        "source_url": "https://en.wikipedia.org/wiki/2026_USL_Championship_season",
    } for conf, name, city, state in USL_CHAMP]
    write_csv(os.path.join(DATA_DIR, "usl_championship_clubs.csv"),
              ["conference","team_name","city","state","league","source_url"], champ_rows)

    # Super League
    super_rows = [{
        "team_name": name, "city": city, "state": state,
        "league": "USL Super League",
        "source_url": "https://en.wikipedia.org/wiki/USL_Super_League",
    } for name, city, state in USL_SUPER]
    write_csv(os.path.join(DATA_DIR, "usl_super_league_clubs.csv"),
              ["team_name","city","state","league","source_url"], super_rows)

    total = len(w_rows) + len(l1_rows) + len(champ_rows) + len(super_rows)
    print(f"\nTotal USL teams written: {total}")


if __name__ == "__main__":
    main()
