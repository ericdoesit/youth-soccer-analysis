#!/usr/bin/env python3
"""
Build CSV from 2026 USL League Two teams (from Wikipedia).
Source: https://en.wikipedia.org/wiki/2026_USL_League_Two_season
158 teams across 4 conferences, 17 divisions.

Output: data/usl_league_two_clubs.csv
"""

import csv, os

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "usl_league_two_clubs.csv")

# (conference, division, team_name, city, state)
TEAMS = [
    # ── EASTERN ───────────────────────────────────────────────────────────────
    ("Eastern", "Northeast",    "Albany Rush",               "Albany",           "NY"),
    ("Eastern", "Northeast",    "Black Rock FC",             "Buffalo",          "NY"),
    ("Eastern", "Northeast",    "Boston Bolts",              "Boston",           "MA"),
    ("Eastern", "Northeast",    "Boston City FC",            "Boston",           "MA"),
    ("Eastern", "Northeast",    "Connecticut Rush",          "Connecticut",      "CT"),
    ("Eastern", "Northeast",    "AC Connecticut",            "Connecticut",      "CT"),
    ("Eastern", "Northeast",    "NEFC",                      "Massachusetts",    "MA"),
    ("Eastern", "Northeast",    "Seacoast United Phantoms",  "New Hampshire",    "NH"),
    ("Eastern", "Northeast",    "Vermont Green FC",          "Burlington",       "VT"),
    ("Eastern", "Northeast",    "Western Mass Pioneers",     "Western MA",       "MA"),
    ("Eastern", "Mid Atlantic", "Delaware FC",               "Delaware",         "DE"),
    ("Eastern", "Mid Atlantic", "Eagle FC",                  "Pennsylvania",     "PA"),
    ("Eastern", "Mid Atlantic", "Lehigh Valley United",      "Allentown",        "PA"),
    ("Eastern", "Mid Atlantic", "Ocean City Nor'easters",    "Ocean City",       "MD"),
    ("Eastern", "Mid Atlantic", "Philadelphia Lone Star FC", "Philadelphia",     "PA"),
    ("Eastern", "Mid Atlantic", "Pennsylvania Classics",     "Pennsylvania",     "PA"),
    ("Eastern", "Mid Atlantic", "Reading United AC",         "Reading",          "PA"),
    ("Eastern", "Mid Atlantic", "Real Central New Jersey",   "New Jersey",       "NJ"),
    ("Eastern", "Mid Atlantic", "West Chester United SC",    "West Chester",     "PA"),
    ("Eastern", "Metropolitan", "Cedar Stars Rush",          "New Jersey",       "NJ"),
    ("Eastern", "Metropolitan", "FC Motown STA",             "New Jersey",       "NJ"),
    ("Eastern", "Metropolitan", "Hudson Valley Hammers",     "Hudson Valley",    "NY"),
    ("Eastern", "Metropolitan", "Ironbound SC",              "Newark",           "NJ"),
    ("Eastern", "Metropolitan", "Long Island Rough Riders",  "Long Island",      "NY"),
    ("Eastern", "Metropolitan", "Manhattan SC",              "New York",         "NY"),
    ("Eastern", "Metropolitan", "Morris Elite SC",           "New Jersey",       "NJ"),
    ("Eastern", "Metropolitan", "New Jersey Copa FC",        "New Jersey",       "NJ"),
    ("Eastern", "Metropolitan", "Staten Island Athletic SC", "Staten Island",    "NY"),
    ("Eastern", "Metropolitan", "Westchester Flames",        "Westchester",      "NY"),
    ("Eastern", "Chesapeake",   "Annapolis Blues FC",        "Annapolis",        "MD"),
    ("Eastern", "Chesapeake",   "Bethesda FC",               "Bethesda",         "MD"),
    ("Eastern", "Chesapeake",   "Charlottesville Blues FC",  "Charlottesville",  "VA"),
    ("Eastern", "Chesapeake",   "Christos FC",               "Maryland",         "MD"),
    ("Eastern", "Chesapeake",   "Hill City FC",              "Virginia",         "VA"),
    ("Eastern", "Chesapeake",   "Lionsbridge FC",            "Newport News",     "VA"),
    ("Eastern", "Chesapeake",   "Loudoun United FC 2",       "Leesburg",         "VA"),
    ("Eastern", "Chesapeake",   "Northern Virginia FC",      "Northern VA",      "VA"),
    ("Eastern", "Chesapeake",   "Patuxent Football Athletics","Maryland",        "MD"),
    ("Eastern", "Chesapeake",   "Virginia Beach United",     "Virginia Beach",   "VA"),
    ("Eastern", "Chesapeake",   "Virginia Marauders FC",     "Virginia",         "VA"),
    ("Eastern", "South Atlantic","Appalachian FC",            "North Carolina",   "NC"),
    ("Eastern", "South Atlantic","Asheville City SC",         "Asheville",        "NC"),
    ("Eastern", "South Atlantic","Charlotte Eagles",          "Charlotte",        "NC"),
    ("Eastern", "South Atlantic","Charlotte Independence 2",  "Charlotte",        "NC"),
    ("Eastern", "South Atlantic","Hickory FC",                "Hickory",          "NC"),
    ("Eastern", "South Atlantic","North Carolina FC U23",     "Durham",           "NC"),
    ("Eastern", "South Atlantic","Port City FC",              "Wilmington",       "NC"),
    ("Eastern", "South Atlantic","Salem City FC",             "Salem",            "NC"),
    ("Eastern", "South Atlantic","SC United Bantams",         "South Carolina",   "SC"),
    ("Eastern", "South Atlantic","Tobacco Road FC",           "North Carolina",   "NC"),
    ("Eastern", "South Atlantic","Wake FC",                   "Raleigh",          "NC"),
    # ── CENTRAL ───────────────────────────────────────────────────────────────
    ("Central", "Great Forest",  "Akron City FC",             "Akron",            "OH"),
    ("Central", "Great Forest",  "Cleveland Force SC",        "Cleveland",        "OH"),
    ("Central", "Great Forest",  "Erie Sports Center FC",     "Erie",             "PA"),
    ("Central", "Great Forest",  "FC Buffalo",                "Buffalo",          "NY"),
    ("Central", "Great Forest",  "Lorain County Leviathan FC","Lorain County",   "OH"),
    ("Central", "Great Forest",  "Pittsburgh Riverhounds 2",  "Pittsburgh",       "PA"),
    ("Central", "Great Forest",  "Steel City FC",             "Pittsburgh",       "PA"),
    ("Central", "Great Lakes",   "AFC Ann Arbor",             "Ann Arbor",        "MI"),
    ("Central", "Great Lakes",   "Flint City Bucks",          "Flint",            "MI"),
    ("Central", "Great Lakes",   "Kalamazoo FC",              "Kalamazoo",        "MI"),
    ("Central", "Great Lakes",   "Lansing City Football",     "Lansing",          "MI"),
    ("Central", "Great Lakes",   "Midwest United FC",         "Michigan",         "MI"),
    ("Central", "Great Lakes",   "Oakland County FC",         "Oakland County",   "MI"),
    ("Central", "Great Lakes",   "Union FC Macomb",           "Macomb",           "MI"),
    ("Central", "Great Plains",  "Des Moines Menace",         "Des Moines",       "IA"),
    ("Central", "Great Plains",  "FC Ambush",                 "Missouri",         "MO"),
    ("Central", "Great Plains",  "Peoria City",               "Peoria",           "IL"),
    ("Central", "Great Plains",  "Santafe Wanderers",         "Kansas",           "KS"),
    ("Central", "Great Plains",  "Springfield FC",            "Springfield",      "IL"),
    ("Central", "Great Plains",  "Sunflower State FC",        "Kansas",           "KS"),
    ("Central", "Heartland",     "Chicago City Dutch Lions",  "Chicago",          "IL"),
    ("Central", "Heartland",     "Edgewater Castle FC",       "Chicago",          "IL"),
    ("Central", "Heartland",     "Minneapolis City SC",       "Minneapolis",      "MN"),
    ("Central", "Heartland",     "River Light FC",            "Illinois",         "IL"),
    ("Central", "Heartland",     "RKC Third Coast",           "Wisconsin",        "WI"),
    ("Central", "Heartland",     "Rochester FC",              "Rochester",        "NY"),
    ("Central", "Heartland",     "Rockford Raptors FC",       "Rockford",         "IL"),
    ("Central", "Heartland",     "St. Croix Legends",         "Minnesota",        "MN"),
    ("Central", "Heartland",     "Sueno FC",                  "Illinois",         "IL"),
    ("Central", "Valley",        "Dayton Dutch Lions",        "Dayton",           "OH"),
    ("Central", "Valley",        "Kings Hammer FC Columbus",  "Columbus",         "OH"),
    ("Central", "Valley",        "Louisville City FC U23",    "Louisville",       "KY"),
    ("Central", "Valley",        "Northern Indiana FC",       "Northern Indiana", "IN"),
    ("Central", "Valley",        "Toledo Villa FC",           "Toledo",           "OH"),
    ("Central", "Valley",        "West Virginia United",      "West Virginia",    "WV"),
    # ── SOUTHERN ──────────────────────────────────────────────────────────────
    ("Southern","South Central", "Apotheos FC",               "Georgia",          "GA"),
    ("Southern","South Central", "Birmingham Legion 2",       "Birmingham",       "AL"),
    ("Southern","South Central", "Columbus United FC",        "Columbus",         "GA"),
    ("Southern","South Central", "East Atlanta Dutch Lions",  "Atlanta",          "GA"),
    ("Southern","South Central", "Montgomery United FC",      "Montgomery",       "AL"),
    ("Southern","South Central", "Swarm FC",                  "Georgia",          "GA"),
    ("Southern","Southeast",     "Brave SC",                  "Florida",          "FL"),
    ("Southern","Southeast",     "Brooke House FC",           "Florida",          "FL"),
    ("Southern","Southeast",     "Inter Gainesville KF",      "Gainesville",      "FL"),
    ("Southern","Southeast",     "Nona FC",                   "Lake Nona",        "FL"),
    ("Southern","Southeast",     "Shark Coast FC",            "Florida",          "FL"),
    ("Southern","Southeast",     "Sporting Club Jacksonville","Jacksonville",     "FL"),
    ("Southern","South Florida", "Brevard SC",                "Brevard County",   "FL"),
    ("Southern","South Florida", "FC Miami City",             "Miami",            "FL"),
    ("Southern","South Florida", "Fort Lauderdale United FC", "Fort Lauderdale",  "FL"),
    ("Southern","South Florida", "Lakeland United FC",        "Lakeland",         "FL"),
    ("Southern","South Florida", "Miami AC",                  "Miami",            "FL"),
    ("Southern","South Florida", "Weston FC",                 "Weston",           "FL"),
    ("Southern","Mid South",     "Hattiesburg FC",            "Hattiesburg",      "MS"),
    ("Southern","Mid South",     "Jackson Boom",              "Jackson",          "MS"),
    ("Southern","Mid South",     "Louisiana Krewe FC",        "Louisiana",        "LA"),
    ("Southern","Mid South",     "Little Rock Rangers",       "Little Rock",      "AR"),
    ("Southern","Mid South",     "Memphis FC",                "Memphis",          "TN"),
    ("Southern","Mid South",     "Mississippi Brilla",        "Mississippi",      "MS"),
    ("Southern","Mid South",     "Red River FC",              "Texas",            "TX"),
    ("Southern","Lone Star",     "AC Houston Sur",            "Houston",          "TX"),
    ("Southern","Lone Star",     "AHFC Royals",               "Texas",            "TX"),
    ("Southern","Lone Star",     "GFI Woodlands",             "The Woodlands",    "TX"),
    ("Southern","Lone Star",     "Hill Country Lobos",        "Texas",            "TX"),
    ("Southern","Lone Star",     "Houston FC",                "Houston",          "TX"),
    ("Southern","Lone Star",     "Laredo Heat",               "Laredo",           "TX"),
    ("Southern","Lone Star",     "Lonestar SC",               "Texas",            "TX"),
    ("Southern","Lone Star",     "San Antonio FC 2",          "San Antonio",      "TX"),
    ("Southern","Lone Star",     "Twin City Toucans FC",      "Texas",            "TX"),
    ("Southern","Ranger",        "Denton Diablos FC",         "Denton",           "TX"),
    ("Southern","Ranger",        "Fort Worth Vaqueros FC",    "Fort Worth",       "TX"),
    ("Southern","Ranger",        "Lubbock Matadors SC",       "Lubbock",          "TX"),
    ("Southern","Ranger",        "McKinney Chupacabras FC",   "McKinney",         "TX"),
    ("Southern","Ranger",        "Texoma FC",                 "Texoma",           "TX"),
    ("Southern","Ranger",        "West Texas FC",             "West Texas",       "TX"),
    # ── WESTERN ───────────────────────────────────────────────────────────────
    ("Western", "Mountain",      "Albion SC Colorado",        "Colorado",         "CO"),
    ("Western", "Mountain",      "Atletico Union",            "Colorado",         "CO"),
    ("Western", "Mountain",      "CISA",                      "Colorado",         "CO"),
    ("Western", "Mountain",      "Colorado Storm",            "Colorado",         "CO"),
    ("Western", "Mountain",      "Flatirons Rush SC",         "Boulder",          "CO"),
    ("Western", "Mountain",      "Real Colorado",             "Colorado",         "CO"),
    ("Western", "Mountain",      "Utah United",               "Utah",             "UT"),
    ("Western", "Northwest",     "Ballard FC",                "Seattle",          "WA"),
    ("Western", "Northwest",     "Bigfoot FC",                "Washington",       "WA"),
    ("Western", "Northwest",     "FC Olympia",                "Olympia",          "WA"),
    ("Western", "Northwest",     "Midlakes United",           "Washington",       "WA"),
    ("Western", "Northwest",     "Portland Bangers FC",       "Portland",         "OR"),
    ("Western", "Northwest",     "Snohomish United",          "Snohomish",        "WA"),
    ("Western", "Northwest",     "Tacoma Stars",              "Tacoma",           "WA"),
    ("Western", "Northwest",     "West Seattle Junction FC",  "Seattle",          "WA"),
    ("Western", "Nor Cal",       "Academica SC",              "Sacramento",       "CA"),
    ("Western", "Nor Cal",       "Almaden FC",                "San Jose",         "CA"),
    ("Western", "Nor Cal",       "Davis Legacy SC",           "Davis",            "CA"),
    ("Western", "Nor Cal",       "Marin FC Legends",          "Marin",            "CA"),
    ("Western", "Nor Cal",       "Project 51O",               "Oakland",          "CA"),
    ("Western", "Nor Cal",       "San Francisco City FC",     "San Francisco",    "CA"),
    ("Western", "Nor Cal",       "San Francisco Glens SC",    "San Francisco",    "CA"),
    ("Western", "Nor Cal",       "San Juan SC",               "Sacramento",       "CA"),
    ("Western", "Southwest",     "AMSG FC",                   "Southern CA",      "CA"),
    ("Western", "Southwest",     "Capo FC",                   "Southern CA",      "CA"),
    ("Western", "Southwest",     "City SC",                   "San Diego",        "CA"),
    ("Western", "Southwest",     "FC Tucson",                 "Tucson",           "AZ"),
    ("Western", "Southwest",     "Redlands FC",               "Redlands",         "CA"),
    ("Western", "Southwest",     "Southern California Eagles","Southern CA",      "CA"),
    ("Western", "Southwest",     "Stars FC",                  "Southern CA",      "CA"),
    ("Western", "Southwest",     "Ventura County Fusion",     "Ventura",          "CA"),
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    fields = ["conference", "division", "team_name", "city", "state",
              "league", "source_url"]
    rows = [{
        "conference": conf,
        "division": div,
        "team_name": name,
        "city": city,
        "state": state,
        "league": "USL League Two",
        "source_url": "https://en.wikipedia.org/wiki/2026_USL_League_Two_season",
    } for conf, div, name, city, state in TEAMS]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} USL League Two teams -> {OUT_CSV}")

    from collections import Counter
    by_state = Counter(r["state"] for r in rows)
    print("\n--- Teams by state (top 10) ---")
    for state, count in by_state.most_common(10):
        print(f"  {state:<4s} {count}")


if __name__ == "__main__":
    main()
