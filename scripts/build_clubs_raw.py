#!/usr/bin/env python3
"""
Build a master clubs index combining all collected league data.
Adds a 'tier' classification to each club based on league.

Output: data/clubs_raw.csv

Tier definitions (per the plan):
  T1  Recreational       AYSO Rec, USYS Rec              ~$550/yr
  T2  Competitive Travel Coast Soccer, NPL, Nat'l League ~$3,100/yr
  T3  Elite Club         ECNL, Girls Academy, USL Youth  ~$6,000-8,000/yr
  T4  Top Elite          MLS Next (HD)                   ~$8,000-12,000+/yr
  T4B Public Elite       LA City United                  $120/yr
  T5  Pro Academy        MLS Academies                   $0/yr
  PRO Professional       USL Championship, Super League  n/a (pro)
"""

import csv, os, re
from collections import Counter

DATA_DIR = "data"
OUT_CSV = os.path.join(DATA_DIR, "clubs_raw.csv")

FIELDS = [
    "club_name", "city", "state", "league", "tier", "tier_label",
    "conference", "division", "gender", "source_file",
]

# Map full state names → 2-letter abbreviations
STATE_ABBREV = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA",
    "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
    "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
    "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT",
    "Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI",
    "Wyoming":"WY","District of Columbia":"DC","DC":"DC",
}

TIER_MAP = {
    "MLS Next":          ("T3-T4", "Elite / Top Elite"),
    "Girls Academy":     ("T3",    "Elite Club"),
    "USL Youth":         ("T3",    "Elite Club"),
    "ECNL":              ("T3",    "Elite Club"),
    "The National League": ("T2",  "Competitive Travel"),
    "NPL":               ("T2",    "Competitive Travel"),
    "NorCal NPL":        ("T2",    "Competitive Travel"),
    "FCL NPL (Florida)": ("T2",    "Competitive Travel"),
    "GLA NPL":           ("T2",    "Competitive Travel"),
    "MDL NPL (GLA Boys)":("T2",    "Competitive Travel"),
    "Central States NPL":("T2",    "Competitive Travel"),
    "South Atlantic Premier":("T2","Competitive Travel"),
    "Frontier Premier League":("T2","Competitive Travel"),
    "Red River NPL":     ("T2",    "Competitive Travel"),
    "Mountain West NPL": ("T2",    "Competitive Travel"),
    "VPSL NPL (Virginia)":("T2",  "Competitive Travel"),
    "Minnesota NPL":     ("T2",    "Competitive Travel"),
    "NISL NPL (Chicago)":("T2",   "Competitive Travel"),
    "CPSL NPL (Chesapeake)":("T2","Competitive Travel"),
    "Mid-Atlantic Premier":("T2",  "Competitive Travel"),
    "WPL NPL (Washington)":("T2",  "Competitive Travel"),
    "Coast Soccer":      ("T2",    "Competitive Travel"),
    "SoCal Soccer League":("T2",   "Competitive Travel"),
    "USL League Two":    ("T2-T3", "Competitive / Elite"),
    "USL W League":      ("T2-T3", "Competitive / Elite"),
    "USL League One":    ("T3-PRO","Semi-Pro"),
    "USL Championship":  ("PRO",   "Professional"),
    "USL Super League":  ("PRO",   "Professional (Women's)"),
    "Development Player League": ("T3", "Elite Club (Girls)"),
    "EDP Soccer":        ("T2",    "Competitive Travel"),
    "National Clubs":    ("T1-T4", "All Levels"),
}


def get_tier(league):
    for key, (tier, label) in TIER_MAP.items():
        if key.lower() in league.lower():
            return tier, label
    return "TBD", "Unknown"


def abbrev_state(s):
    s = s.strip()
    return STATE_ABBREV.get(s, s)


def read_csv_file(path):
    if not os.path.exists(path):
        print(f"  SKIP (not found): {path}")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize(rows, source_file, league_field, name_field,
              state_field=None, city_field=None, conf_field=None,
              div_field=None, gender_field=None, gender_default="",
              league_override=None):
    out = []
    for r in rows:
        league = league_override or r.get(league_field, "").strip()
        name   = r.get(name_field,   "").strip()
        state  = abbrev_state(r.get(state_field, "") if state_field else "")
        city   = r.get(city_field,   "") if city_field  else ""
        conf   = r.get(conf_field,   "") if conf_field  else ""
        div    = r.get(div_field,    "") if div_field   else ""
        gender = r.get(gender_field, "") if gender_field else gender_default
        if not name:
            continue
        tier, label = get_tier(league)
        out.append({
            "club_name": name,
            "city":      city.strip(),
            "state":     state,
            "league":    league,
            "tier":      tier,
            "tier_label":label,
            "conference":conf.strip(),
            "division":  div.strip(),
            "gender":    gender.strip(),
            "source_file":source_file,
        })
    return out


def main():
    all_rows = []

    # 1. National clubs (all 50 states from ussoccerparent.com)
    rows = read_csv_file(os.path.join(DATA_DIR, "national_clubs.csv"))
    all_rows += normalize(rows, "national_clubs.csv",
                          "league", "club_name",
                          state_field="state",
                          gender_default="Mixed",
                          league_override="National Directory (ussoccerparent.com)")

    # 2. MLS Next clubs
    rows = read_csv_file(os.path.join(DATA_DIR, "mlsnext_clubs.csv"))
    if rows and rows[0]:
        # Determine field names dynamically
        fields = list(rows[0].keys())
        name_f = next((f for f in fields if 'club' in f.lower() or 'name' in f.lower()), fields[0])
        state_f = next((f for f in fields if 'state' in f.lower()), None)
        for r in rows:
            name = r.get(name_f, "").strip()
            state = r.get(state_f, "").strip() if state_f else ""
            league = r.get("league", "MLS Next").strip()
            if not name:
                continue
            tier, label = get_tier(league)
            all_rows.append({
                "club_name": name, "city": "", "state": state,
                "league": league, "tier": tier, "tier_label": label,
                "conference": "", "division": "", "gender": "Mixed",
                "source_file": "mlsnext_clubs.csv",
            })

    # 3. The National League clubs
    rows = read_csv_file(os.path.join(DATA_DIR, "national_league_clubs.csv"))
    all_rows += normalize(rows, "national_league_clubs.csv",
                          "league", "club_name",
                          state_field="state",
                          conf_field="region",
                          div_field="division",
                          gender_field="gender")

    # 4. Girls Academy clubs
    rows = read_csv_file(os.path.join(DATA_DIR, "girls_academy_clubs.csv"))
    all_rows += normalize(rows, "girls_academy_clubs.csv",
                          "league", "club_name",
                          state_field="state",
                          conf_field="conference",
                          gender_field="gender")

    # 5. Coast Soccer clubs
    rows = read_csv_file(os.path.join(DATA_DIR, "coast_soccer_clubs.csv"))
    if rows:
        for r in rows:
            name = r.get("club_name", "").strip()
            season = r.get("season", "").strip()
            if not name:
                continue
            all_rows.append({
                "club_name": name, "city": "", "state": "CA",
                "league": "Coast Soccer", "tier": "T2", "tier_label": "Competitive Travel",
                "conference": "", "division": season, "gender": "Mixed",
                "source_file": "coast_soccer_clubs.csv",
            })

    # 6. NPL clubs (from all scraped leagues)
    rows = read_csv_file(os.path.join(DATA_DIR, "npl_clubs.csv"))
    if rows:
        for r in rows:
            name   = r.get("club",   "").strip()
            league = r.get("league", "NPL").strip()
            if not name:
                continue
            tier, label = get_tier(league)
            all_rows.append({
                "club_name": name, "city": "", "state": "",
                "league": league, "tier": tier, "tier_label": label,
                "conference": "", "division": "", "gender": "Mixed",
                "source_file": "npl_clubs.csv",
            })

    # 7. USL League Two
    rows = read_csv_file(os.path.join(DATA_DIR, "usl_league_two_clubs.csv"))
    all_rows += normalize(rows, "usl_league_two_clubs.csv",
                          "league", "team_name",
                          state_field="state",
                          city_field="city",
                          conf_field="conference",
                          div_field="division")

    # 8. USL W League
    rows = read_csv_file(os.path.join(DATA_DIR, "usl_w_league_clubs.csv"))
    all_rows += normalize(rows, "usl_w_league_clubs.csv",
                          "league", "club_name",
                          state_field="state",
                          city_field="city",
                          conf_field="conference",
                          div_field="division",
                          gender_default="Women")

    # 9. USL League One
    rows = read_csv_file(os.path.join(DATA_DIR, "usl_league_one_clubs.csv"))
    all_rows += normalize(rows, "usl_league_one_clubs.csv",
                          "league", "team_name",
                          state_field="state",
                          city_field="city")

    # 10. USL Championship
    rows = read_csv_file(os.path.join(DATA_DIR, "usl_championship_clubs.csv"))
    all_rows += normalize(rows, "usl_championship_clubs.csv",
                          "league", "team_name",
                          state_field="state",
                          city_field="city",
                          conf_field="conference")

    # 11. USL Super League
    rows = read_csv_file(os.path.join(DATA_DIR, "usl_super_league_clubs.csv"))
    all_rows += normalize(rows, "usl_super_league_clubs.csv",
                          "league", "team_name",
                          state_field="state",
                          city_field="city",
                          gender_default="Women")

    # 12. USL Youth
    rows = read_csv_file(os.path.join(DATA_DIR, "usl_youth_clubs.csv"))
    all_rows += normalize(rows, "usl_youth_clubs.csv",
                          "league", "club_name",
                          state_field="state",
                          div_field="division")

    # 13. DPL (Development Player League — all-girls, 70+ clubs)
    rows = read_csv_file(os.path.join(DATA_DIR, "dpl_clubs.csv"))
    all_rows += normalize(rows, "dpl_clubs.csv",
                          "league", "club_name",
                          state_field="state",
                          city_field="city",
                          conf_field="conference",
                          gender_field="gender")

    # 15. EDP Soccer (East Coast competitive travel — NJ/PA/MD/CT/NY/VA)
    rows = read_csv_file(os.path.join(DATA_DIR, "edp_clubs.csv"))
    if rows:
        for r in rows:
            name = r.get("club_name", "").strip()
            city = r.get("city", "").strip()
            state = r.get("state", "").strip()
            if not name:
                continue
            all_rows.append({
                "club_name": name, "city": city, "state": state,
                "league": "EDP Soccer", "tier": "T2",
                "tier_label": "Competitive Travel",
                "conference": "", "division": "", "gender": "Mixed",
                "source_file": "edp_clubs.csv",
            })

    # 14. SoCal Soccer League (deduplicated from team-level data)
    rows = read_csv_file(os.path.join(DATA_DIR, "socal_soccer_clubs.csv"))
    if rows:
        for r in rows:
            name = r.get("club_name", "").strip()
            if not name:
                continue
            all_rows.append({
                "club_name": name, "city": "", "state": "CA",
                "league": "SoCal Soccer League", "tier": "T2",
                "tier_label": "Competitive Travel",
                "conference": "", "division": "", "gender": r.get("gender",""),
                "source_file": "socal_soccer_clubs.csv",
            })

    # Write master index
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n=== MASTER CLUBS INDEX ===")
    print(f"Total records: {len(all_rows)}")
    print(f"Written to: {OUT_CSV}")

    by_league = Counter(r["league"] for r in all_rows)
    print(f"\n--- By League (top 15) ---")
    for lg, cnt in by_league.most_common(15):
        print(f"  {lg:<35s} {cnt:>5}")

    by_tier = Counter(r["tier"] for r in all_rows)
    print(f"\n--- By Tier ---")
    for tier, cnt in sorted(by_tier.items()):
        label = TIER_MAP.get(tier, ("", tier))[1] if tier in TIER_MAP else ""
        print(f"  {tier:<10s} {cnt:>5}")

    by_state = Counter(r["state"] for r in all_rows if r["state"])
    print(f"\n--- By State (top 15) ---")
    for state, cnt in by_state.most_common(15):
        print(f"  {state:<4s} {cnt:>5}")


if __name__ == "__main__":
    main()
