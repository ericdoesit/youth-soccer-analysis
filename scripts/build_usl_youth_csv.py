#!/usr/bin/env python3
"""
Build CSV of USL Youth clubs from usl-youth.com/league-directory/
Scraped 2026-06-05. 94 clubs across 6 divisions.

Output: data/usl_youth_clubs.csv
"""

import csv, os

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "usl_youth_clubs.csv")

# (division, club_name, state)
CLUBS = [
    # Mid Atlantic (VA, MD, DC)
    ("Mid Atlantic", "Alexandria Soccer Association",   "VA"),
    ("Mid Atlantic", "Annapolis Select FC",             "MD"),
    ("Mid Atlantic", "Arlington Soccer Association",    "VA"),
    ("Mid Atlantic", "Bethesda SC",                     "MD"),
    ("Mid Atlantic", "Christos FC",                     "MD"),
    ("Mid Atlantic", "DC Eleven Football Club",         "DC"),
    ("Mid Atlantic", "Fairfax Virginia Union",          "VA"),
    ("Mid Atlantic", "FC Charles 1658",                 "MD"),
    ("Mid Atlantic", "Great Falls Reston",              "VA"),
    ("Mid Atlantic", "Loudoun Soccer",                  "VA"),
    ("Mid Atlantic", "Loudoun United FC",               "VA"),
    ("Mid Atlantic", "Maryland Rush",                   "MD"),
    ("Mid Atlantic", "Maryland United FC",              "MD"),
    ("Mid Atlantic", "Northern Virginia Soccer Club",   "VA"),
    ("Mid Atlantic", "Northern Virginia United FC",     "VA"),
    ("Mid Atlantic", "NOVA Majestics McLean",           "VA"),
    ("Mid Atlantic", "Springfield Youth Club Soccer",   "VA"),
    ("Mid Atlantic", "The St. James FC",                "VA"),
    ("Mid Atlantic", "Virginia Development Academy",    "VA"),
    ("Mid Atlantic", "Virginia Valor FC",               "VA"),
    # Mid South (TX, CA)
    ("Mid South", "Dallas Roma FC",           "TX"),
    ("Mid South", "FC Allen",                 "TX"),
    ("Mid South", "Kernow Storm FC",          "TX"),
    ("Mid South", "North Texas United FC",    "TX"),
    ("Mid South", "Rodeo Soccer Club",        "TX"),
    ("Mid South", "West Side Alliance SC",    "CA"),
    # Midwest (IL, OH, MI, WI, IN)
    ("Midwest", "Bloomingdale Lightning FC",           "IL"),
    ("Midwest", "Chicago City Soccer Club",            "IL"),
    ("Midwest", "Chicago Inferno",                     "IL"),
    ("Midwest", "Chicago Rush SC",                     "IL"),
    ("Midwest", "Chicago Soccer Academy",              "IL"),
    ("Midwest", "Chicagoland United SC",               "IL"),
    ("Midwest", "Cleveland Force SC",                  "OH"),
    ("Midwest", "Columbus Force",                      "OH"),
    ("Midwest", "DBBS",                                "MI"),
    ("Midwest", "Evolution SC",                        "MI"),
    ("Midwest", "FC Milwaukee Torrent",                "WI"),
    ("Midwest", "Force FC",                            "IL"),
    ("Midwest", "Galaxy SC",                           "IL"),
    ("Midwest", "Indy Eleven North",                   "IN"),
    ("Midwest", "Kingdom Soccer Club",                 "MI"),
    ("Midwest", "Lightning Soccer Club",               "MI"),
    ("Midwest", "Liverpool FC Michigan Central",       "MI"),
    ("Midwest", "Liverpool FC Michigan West Ann Arbor","MI"),
    ("Midwest", "Liverpool FC Michigan West Hartland", "MI"),
    ("Midwest", "Midland SC",                          "MI"),
    ("Midwest", "Midwest United FC",                   "MI"),
    ("Midwest", "Midwest United FC SCOR",              "MI"),
    ("Midwest", "Nationals",                           "WI"),
    ("Midwest", "Northern Indiana FC Academy",         "IN"),
    ("Midwest", "Portage Soccer Club",                 "MI"),
    ("Midwest", "Rush WI Southeast",                   "WI"),
    ("Midwest", "TBAYS",                               "ON"),  # Thunder Bay, Ontario (Canada)
    ("Midwest", "Team Chicago SC",                     "IL"),
    ("Midwest", "Toledo Villa FC",                     "OH"),
    ("Midwest", "Upper 90 FC",                         "OH"),
    ("Midwest", "WCOB FC",                             "IL"),
    # North Atlantic (NY, NJ, MA)
    ("North Atlantic", "Auburndale SC",                       "MA"),
    ("North Atlantic", "Barcelona SC",                        "NJ"),
    ("North Atlantic", "Brick Township Soccer Association",   "NJ"),
    ("North Atlantic", "Brooklyn Italians Youth SC",          "NY"),
    ("North Atlantic", "Commack Soccer",                      "NY"),
    ("North Atlantic", "East Meadow SC",                      "NY"),
    ("North Atlantic", "Eleftheria Pancyprian SC",            "NY"),
    ("North Atlantic", "FC Motown STA",                       "NJ"),
    ("North Atlantic", "Ironbound SC",                        "NJ"),
    ("North Atlantic", "Istria SC",                           "NJ"),
    ("North Atlantic", "Kearny Thistle United",               "NJ"),
    ("North Atlantic", "LIJSL Academy",                       "NY"),
    ("North Atlantic", "Long Island Rough Riders",            "NY"),
    ("North Atlantic", "Long Island Rough Riders East",       "NY"),
    ("North Atlantic", "Massapequa SC",                       "NY"),
    ("North Atlantic", "Morris Elite SC",                     "NJ"),
    ("North Atlantic", "New York Braveheart SC",              "NY"),
    ("North Atlantic", "New York Titans F.C",                 "NY"),
    ("North Atlantic", "Northport Cow Harbor United SC",      "NY"),
    ("North Atlantic", "NY Surf",                             "NY"),
    ("North Atlantic", "Oceanside United SC",                 "NY"),
    ("North Atlantic", "Paisley Athletic FC",                 "NY"),
    ("North Atlantic", "Red Bull New York",                   "NJ"),
    ("North Atlantic", "Staten Island Athletic Sporting Club","NY"),
    ("North Atlantic", "Union County FC",                     "NJ"),
    ("North Atlantic", "Union SC",                            "NJ"),
    ("North Atlantic", "Westchester Flames",                  "NY"),
    # Northeast (CT, NY)
    ("Northeast", "AC Connecticut",       "CT"),
    ("Northeast", "Cedar Stars Academy HV","NY"),
    ("Northeast", "Hartford Athletic",    "CT"),
    ("Northeast", "Hudson Valley Hammers","NY"),
    ("Northeast", "Inter Connecticut FC", "CT"),
    ("Northeast", "Tri-State Stars FC",   "NJ"),
    ("Northeast", "Vale SC",              "CT"),
    # SoCal (CA)
    ("SoCal", "Capo FC",            "CA"),
    ("SoCal", "LASC",               "CA"),
    ("SoCal", "Oceanside Breakers", "CA"),
    ("SoCal", "Rangers FC",         "CA"),
    ("SoCal", "West Coast FC",      "CA"),
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    fields = ["division", "club_name", "state", "league", "source_url"]
    rows = [{
        "division": div,
        "club_name": club,
        "state": state,
        "league": "USL Youth",
        "source_url": "https://www.usl-youth.com/league-directory/",
    } for div, club, state in CLUBS]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} USL Youth clubs -> {OUT_CSV}")

    from collections import Counter
    by_state = Counter(r["state"] for r in rows)
    print("\n--- Clubs by state (top 10) ---")
    for state, count in by_state.most_common(10):
        print(f"  {state:<4s} {count}")

    by_div = Counter(r["division"] for r in rows)
    print("\n--- Clubs by division ---")
    for div, count in by_div.most_common():
        print(f"  {div:<20s} {count}")


if __name__ == "__main__":
    main()
