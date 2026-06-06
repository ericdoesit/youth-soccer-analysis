#!/usr/bin/env python3
"""
Build DPL (Development Player League) clubs CSV.
Data sourced from playclubsoccer.org/directory + dpleague.org + search results.
DPL is an all-girls elite league with 10 conferences, 70+ clubs, 16k+ players.
Output: data/dpl_clubs.csv
"""

import csv, os

DATA_DIR = "data"

# (club_name, city, state, conference)
# conference derived from region; "Unknown" where not confirmed
DPL_CLUBS = [
    # === CALIFORNIA ===
    ("Albion SC Central Cal",           "Bakersfield",        "CA", "Southwest"),
    ("Albion SC Central Valley",        "Clovis",             "CA", "Southwest"),
    ("Albion SC Riverside",             "Riverside",          "CA", "Southwest"),
    ("Albion SC Santa Monica",          "Santa Monica",       "CA", "Southwest"),
    ("Albion SC Silicon Valley",        "San Jose",           "CA", "NorCal"),
    ("AYSO United SoCal",               "Pacific Palisades",  "CA", "Southwest"),
    ("Boca Orange County",              "Huntington Beach",   "CA", "Southwest"),
    ("Central Coast Surf SC",           "Atascadero",         "CA", "NorCal"),
    ("Central Coast United SC",         "San Luis Obispo",    "CA", "NorCal"),
    ("Ceres Rush",                      "Ceres",              "CA", "NorCal"),
    ("Chula Vista FC",                  "Chula Vista",        "CA", "Southwest"),
    ("City SC Central Valley",          "Tracy",              "CA", "NorCal"),
    ("City SC San Marcos",              "San Marcos",         "CA", "Southwest"),
    ("City SC Southwest",               "Temecula",           "CA", "Southwest"),
    ("Dublin United",                   "Dublin",             "CA", "NorCal"),
    ("FC Premier",                      "Folsom",             "CA", "NorCal"),
    ("FLYTE SC Inland Empire",          "Rancho Cucamonga",   "CA", "Southwest"),
    ("Inland Surf SC",                  "Winchester",         "CA", "Southwest"),
    ("LA Surf SC",                      "San Marino",         "CA", "Southwest"),
    ("Los Angeles Bulls SC",            "Santa Monica",       "CA", "Southwest"),
    ("Oaks FC",                         "Thousand Oaks",      "CA", "Southwest"),
    ("Rangers FC",                      "Fullerton",          "CA", "Southwest"),
    ("Roseville Youth Soccer Club",     "Roseville",          "CA", "NorCal"),
    ("So Cal Blues SC",                 "Laguna Hills",       "CA", "Southwest"),
    ("SoCal Elite FC",                  "Chino",              "CA", "Southwest"),
    ("SoCal Reds FC",                   "Irvine",             "CA", "Southwest"),
    ("Sporting Slammers FC",            "Irvine",             "CA", "Southwest"),
    ("Ventura County Fusion",           "Ventura",            "CA", "Southwest"),
    ("West Coast FC",                   "San Juan Capistrano","CA", "Southwest"),

    # === TEXAS ===
    ("956 United",                      "McAllen",            "TX", "Lone Star"),
    ("Capital City SC",                 "Austin",             "TX", "Lone Star"),
    ("El Paso Surf SC",                 "El Paso",            "TX", "Lone Star"),
    ("GFI Academy",                     "Spring",             "TX", "Lone Star"),
    ("Houston Rangers",                 "Houston",            "TX", "Lone Star"),
    ("Houston Surf SC",                 "Klein",              "TX", "Lone Star"),
    ("HTX Soccer",                      "The Woodlands",      "TX", "Lone Star"),
    ("Premier Futbol Academy SA",       "San Antonio",        "TX", "Lone Star"),
    ("Real Salt Lake El Paso East",     "Socorro",            "TX", "Lone Star"),
    ("RSL Royals West",                 "El Paso",            "TX", "Lone Star"),
    ("SA United SC",                    "San Antonio",        "TX", "Lone Star"),

    # === FLORIDA ===
    ("ASG",                             "Tallahassee",        "FL", "Southeast"),
    ("Clay County SC United",           "Fleming Island",     "FL", "Southeast"),
    ("Football Club Sarasota",          "Sarasota",           "FL", "Southeast"),
    ("Florida Celtic",                  "Largo",              "FL", "Southeast"),
    ("Florida Prime Soccer",            "St. Augustine",      "FL", "Southeast"),
    ("IdeaSport Soccer Academy",        "Orlando",            "FL", "Southeast"),
    ("Kings Hammer Swan City SC",       "Lakeland",           "FL", "Southeast"),
    ("Naples United Soccer Academy",    "Naples",             "FL", "Southeast"),
    ("Orlando City Soccer School",      "Orlando",            "FL", "Southeast"),
    ("Palm Beach Kicks",                "Palm Beach Gardens", "FL", "Southeast"),
    ("West Florida Flames",             "Brandon",            "FL", "Southeast"),
    ("Weston FC",                       "Weston",             "FL", "Southeast"),

    # === GEORGIA ===
    ("Albion SC Atlanta",               "Alpharetta",         "GA", "Southeast"),
    ("Augusta Arsenal SC",              "Martinez",           "GA", "Carolinas"),
    ("Georgia Impact SC",               "Canton",             "GA", "Southeast"),
    ("Inter Atlanta FC",                "Atlanta",            "GA", "Southeast"),
    ("Lanier Soccer Academy",           "Gainesville",        "GA", "Southeast"),
    ("NTH NASA",                        "Marietta",           "GA", "Southeast"),
    ("Roswell Soccer Club",             "Roswell",            "GA", "Southeast"),
    ("Rush Union Soccer",               "Milton",             "GA", "Southeast"),
    ("Southern Soccer Academy",         "Marietta",           "GA", "Southeast"),
    ("Tormenta FC Academy",             "Statesboro",         "GA", "Carolinas"),
    ("Triumph Youth Soccer",            "Tucker",             "GA", "Southeast"),

    # === NORTH CAROLINA ===
    ("Carolina Velocity FC",            "Raleigh",            "NC", "Carolinas"),
    ("Charlotte DA",                    "Charlotte",          "NC", "Carolinas"),
    ("Charlotte Independence SC",       "Cornelius",          "NC", "Carolinas"),
    ("Fox Soccer Academy Carolinas",    "Cornelius",          "NC", "Carolinas"),
    ("Triangle United Soccer Assoc.",   "Chapel Hill",        "NC", "Carolinas"),
    ("Wake FC",                         "Holly Springs",      "NC", "Carolinas"),

    # === SOUTH CAROLINA ===
    ("Charleston SC",                   "Charleston",         "SC", "Carolinas"),
    ("James Island Soccer Club",        "James Island",       "SC", "Carolinas"),

    # === COLORADO ===
    ("Albion SC Colorado",              "Longmont",           "CO", "Mountain"),
    ("Albion SC Denver",                "Denver",             "CO", "Mountain"),
    ("Broomfield SC",                   "Broomfield",         "CO", "Mountain"),
    ("City SC NOCO",                    "Fort Collins",       "CO", "Mountain"),
    ("Colorado Rapids Youth",           "Aurora",             "CO", "Mountain"),
    ("Colorado Rush",                   "Littleton",          "CO", "Mountain"),
    ("Colorado United",                 "Littleton",          "CO", "Mountain"),
    ("Real Colorado",                   "Centennial",         "CO", "Mountain"),

    # === ILLINOIS ===
    ("Chicago City SC",                 "Chicago",            "IL", "Midwest"),
    ("Chicago Empire FC",               "Mokena",             "IL", "Midwest"),
    ("Chicago Fire Youth SC",           "Chicago",            "IL", "Midwest"),
    ("Chicago Kics FC",                 "Chicago",            "IL", "Midwest"),
    ("Chicago Rush SC",                 "Rosemont",           "IL", "Midwest"),
    ("Metro Alliance FC",               "O'Fallon",           "IL", "Midwest"),
    ("Chicagoland United Elite",        "La Grange",          "IL", "Midwest"),

    # === NEW JERSEY ===
    ("Cheshire Soccer Academy",         "Mendham",            "NJ", "Northeast"),
    ("Ironbound SC",                    "Newark",             "NJ", "Northeast"),
    ("NJ14 Soccer Club",               "Flemington",         "NJ", "Northeast"),
    ("STA Mount Olive SC",              "Budd Lake",          "NJ", "Northeast"),
    ("Westfield NJ Soccer",             "Westfield",          "NJ", "Northeast"),

    # === MASSACHUSETTS ===
    ("FC Boston Bolts",                 "Newton",             "MA", "Northeast"),
    ("FC Stars",                        "Acton",              "MA", "Northeast"),
    ("Intercontinental Football Academy NE", "Granby",        "MA", "Northeast"),
    ("New England Futbol Club (NEFC)",  "Mendon",             "MA", "Northeast"),
    ("New England Force",               "Pembroke",           "MA", "Northeast"),
    ("Seacoast United Massachusetts",   "Andover",            "MA", "Northeast"),
    ("Western United Pioneers FC",      "Ludlow",             "MA", "Northeast"),

    # === MARYLAND ===
    ("Harford FC United",               "Forest Hill",        "MD", "Mid-Atlantic"),

    # === UTAH ===
    ("Albion SC Utah",                  "Salt Lake City",     "UT", "Mountain"),

    # === IDAHO ===
    ("Indie Chicas",                    "Meridian",           "ID", "Mountain"),

    # === OTHER STATES ===
    ("Skyline Soccer Association",      "Englewood",          "CO", "Mountain"),
    ("Vero FC",                         "Vero Beach",         "FL", "Southeast"),
    ("Houston Futsal Club",             "Houston",            "TX", "Lone Star"),
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "dpl_clubs.csv")
    fields = ["club_name", "city", "state", "conference", "league", "gender", "source"]

    rows = []
    for name, city, state, conf in DPL_CLUBS:
        rows.append({
            "club_name": name,
            "city": city,
            "state": state,
            "conference": conf,
            "league": "Development Player League",
            "gender": "Girls",
            "source": "playclubsoccer.org + dpleague.org",
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    from collections import Counter
    by_state = Counter(r["state"] for r in rows)
    print(f"Saved {len(rows)} DPL clubs -> {out_path}")
    print("Top states: " + ", ".join(f"{s}({c})" for s, c in by_state.most_common(8)))
    print(f"\nTotal: {len(rows)} clubs across {len(set(r['conference'] for r in rows))} conferences")


if __name__ == "__main__":
    main()
