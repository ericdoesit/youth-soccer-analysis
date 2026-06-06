#!/usr/bin/env python3
"""
Build CSV from Girls Academy member clubs (2023-24 season, 95 clubs).
Source: https://en.wikipedia.org/wiki/Girls_Academy

Output: data/girls_academy_clubs.csv
"""

import csv, os

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "girls_academy_clubs.csv")

# (conference, club_name, state)
CLUBS = [
    # Frontier (TX, MO, LA)
    ("Frontier", "BVB International Academy NTX", "TX"),
    ("Frontier", "HTX Soccer", "TX"),
    ("Frontier", "Lonestar SC Red", "TX"),
    ("Frontier", "Lonestar SC Black", "TX"),
    ("Frontier", "Lou Fusz Athletic", "MO"),
    ("Frontier", "Louisiana TDP Elite", "LA"),
    ("Frontier", "Renegades Soccer Club", "TX"),
    ("Frontier", "RISE Soccer Club", "TX"),
    ("Frontier", "San Antonio City SC", "TX"),
    ("Frontier", "St. Louis Development Academy", "MO"),
    # Mid-America (IL, OH, IN, MI, KY)
    ("Mid-America", "Chicago FC United", "IL"),
    ("Mid-America", "Cincinnati United Premier", "OH"),
    ("Mid-America", "Indy Premier United", "IN"),
    ("Mid-America", "Lexington Sporting Club", "KY"),
    ("Mid-America", "Michigan Jaguars FC", "MI"),
    ("Mid-America", "Nationals Blue", "MI"),
    ("Mid-America", "Nationals Gray", "MI"),
    ("Mid-America", "Sockers FC", "IL"),
    # Midwest (IL, KS, MN, NE, IA, WI)
    ("Midwest", "Central Illinois United", "IL"),
    ("Midwest", "Galaxy SC", "IL"),
    ("Midwest", "Kansas Rush Soccer Club", "KS"),
    ("Midwest", "Salvo SC", "MN"),
    ("Midwest", "SC Wave", "WI"),
    ("Midwest", "Sporting Nebraska FC", "NE"),
    ("Midwest", "Tonka Fusion Elite", "MN"),
    ("Midwest", "VSA Rush", "IA"),
    # Mid-Atlantic (MD, PA, NJ, VA, DE)
    ("Mid-Atlantic", "Baltimore Armour", "MD"),
    ("Mid-Atlantic", "Baltimore Celtic", "MD"),
    ("Mid-Atlantic", "Beadling SC", "PA"),
    ("Mid-Atlantic", "Century United FC", "PA"),
    ("Mid-Atlantic", "Keystone FC", "PA"),
    ("Mid-Atlantic", "Philadelphia Ukrainian Nationals", "PA"),
    ("Mid-Atlantic", "PA Classics", "PA"),
    ("Mid-Atlantic", "Real Jersey FC", "NJ"),
    ("Mid-Atlantic", "SJEB FC", "NJ"),
    ("Mid-Atlantic", "Skyline Elite SC", "VA"),
    ("Mid-Atlantic", "Sporting AC", "DE"),
    ("Mid-Atlantic", "TSJ FC Virginia", "VA"),
    # Mountain West (NV, CO, NM, UT)
    ("Mountain West", "Albion SC Las Vegas", "NV"),
    ("Mountain West", "Broomfield Soccer Club", "CO"),
    ("Mountain West", "Colorado United", "CO"),
    ("Mountain West", "Las Vegas Sports Academy", "NV"),
    ("Mountain West", "New Mexico Soccer Academy", "NM"),
    ("Mountain West", "Rio Rapids SC", "NM"),
    ("Mountain West", "Utah Celtic FC", "UT"),
    ("Mountain West", "Wasatch SC", "UT"),
    # Northeast (NJ, NY, MA, CT, NH)
    ("Northeast", "Cedar Stars Academy - Monmouth", "NJ"),
    ("Northeast", "Cedar Stars Academy - Bergen", "NJ"),
    ("Northeast", "Long Island SC", "NY"),
    ("Northeast", "NEFC", "MA"),
    ("Northeast", "New York Soccer Club", "NY"),
    ("Northeast", "Oakwood SC", "CT"),
    ("Northeast", "Rochester NYFC Youth", "NY"),
    ("Northeast", "Seacoast United", "NH"),
    ("Northeast", "South Shore Select", "MA"),
    ("Northeast", "STA", "NJ"),
    ("Northeast", "Syracuse Development Academy", "NY"),
    # Northwest (CA - NorCal)
    ("Northwest", "Almaden FC", "CA"),
    ("Northwest", "Clovis Crossfire", "CA"),
    ("Northwest", "Lamorinda SC", "CA"),
    ("Northwest", "Los Gatos United", "CA"),
    ("Northwest", "Sacramento United", "CA"),
    ("Northwest", "San Francisco Elite Academy", "CA"),
    ("Northwest", "Santa Clara Sporting", "CA"),
    ("Northwest", "Silicon Valley SA", "CA"),
    ("Northwest", "West Coast Soccer Club", "CA"),
    # Pacific Northwest (OR, WA)
    ("Pacific Northwest", "Oregon Premier FC", "OR"),
    ("Pacific Northwest", "Capital FC", "OR"),
    ("Pacific Northwest", "Columbia Premier SC", "WA"),
    ("Pacific Northwest", "Eugene Metro Futbol Club", "OR"),
    ("Pacific Northwest", "Liverpool FC IA Washington", "WA"),
    ("Pacific Northwest", "Seattle Reign Academy", "WA"),
    ("Pacific Northwest", "Seattle Celtic", "WA"),
    ("Pacific Northwest", "Spokane Shadow", "WA"),
    ("Pacific Northwest", "Washington Rush", "WA"),
    ("Pacific Northwest", "Washington East Surf SC", "WA"),
    # Southeast (GA, FL, SC, NC)
    ("Southeast", "AFC Lightning", "GA"),
    ("Southeast", "Florida United", "FL"),
    ("Southeast", "IMG Academy", "FL"),
    ("Southeast", "PBG Predators", "FL"),
    ("Southeast", "South Carolina Surf", "SC"),
    ("Southeast", "Southern Soccer Academy", "GA"),
    ("Southeast", "Tophat Gold", "GA"),
    ("Southeast", "Tophat Navy", "GA"),
    ("Southeast", "United Soccer Alliance", "FL"),
    ("Southeast", "Wake FC", "NC"),
    ("Southeast", "West Florida Flames", "FL"),
    # Southwest (CA - SoCal, AZ)
    ("Southwest", "Albion SC San Diego", "CA"),
    ("Southwest", "City SC", "CA"),
    ("Southwest", "FC Tucson", "AZ"),
    ("Southwest", "FRAM Soccer Club", "CA"),
    ("Southwest", "LA Surf SC", "CA"),
    ("Southwest", "Murrieta Soccer Academy", "CA"),
    ("Southwest", "SC del Sol", "AZ"),
    ("Southwest", "SDSC Surf", "CA"),
    ("Southwest", "West Coast FC", "CA"),
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    fields = ["conference", "club_name", "state", "league", "gender", "source_url"]
    rows = [{
        "conference": conf,
        "club_name": name,
        "state": state,
        "league": "Girls Academy",
        "gender": "Girls",
        "source_url": "https://en.wikipedia.org/wiki/Girls_Academy",
    } for conf, name, state in CLUBS]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} Girls Academy clubs -> {OUT_CSV}")

    from collections import Counter
    by_state = Counter(r["state"] for r in rows)
    print("\n--- Clubs by state (top 10) ---")
    for state, count in by_state.most_common(10):
        print(f"  {state:<4s} {count}")


if __name__ == "__main__":
    main()
