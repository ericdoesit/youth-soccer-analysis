#!/usr/bin/env python3
"""
Scrape Pre-ECNL Boys standings — U11 (B2015) and U12 (B2014) only.
Same TGS API as ECNL-RL but different org/season IDs.

API: https://api.athleteone.com/api/Script/get-conference-standings/
     {eventId}/{orgId}/{seasonId}/{divisionId}/{standingId}
"""

import requests
import csv
import time
from html.parser import HTMLParser
from collections import defaultdict

HEADERS = {
    "Referer": "https://theecnl.com/sports/2023/8/8/Pre-ECNLB_0808231942.aspx",
    "Origin": "https://theecnl.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

ORG_ID    = 22
SEASON_ID = 76
STANDING_CONFERENCE = 0

# NTX and Ohio Valley have both Fall 2025 and Spring 2026 events;
# both are included and teams are deduplicated by team_id.
CONFERENCES = {
    4011: "Florida",
    4007: "Frontier",
    4008: "GMA",
    4009: "Heartland",
    3916: "Lake Michigan",
    4023: "Mountain",
    3919: "New England",
    3920: "North Atlantic",
    3918: "Northeast",
    4010: "Northern Cal",
    3921: "NTX",
    4171: "NTX",
    3981: "Ohio Valley",
    4168: "Ohio Valley",
    3923: "SoCal",
}

AGE_GROUPS = {
    19178: "B2015",  # U11
    19179: "B2014",  # U12
}


class StandingsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.teams = []
        self.in_team = False
        self.current = {}

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == "span" and "individual-team-item" in attrs_d.get("class", ""):
            if self.current.get("team_name"):
                self.teams.append(dict(self.current))
            self.in_team = True
            self.current = {
                "club_id":   attrs_d.get("data-club-id", ""),
                "team_id":   attrs_d.get("data-team-id", ""),
                "team_name": "",
            }

    def handle_data(self, data):
        d = data.strip()
        if self.in_team and d and not self.current.get("team_name"):
            self.current["team_name"] = d
            self.in_team = False

    def finalize(self):
        if self.current.get("team_name"):
            self.teams.append(dict(self.current))
            self.current = {}


def fetch_standings(event_id, division_id):
    url = (
        f"https://api.athleteone.com/api/Script/get-conference-standings"
        f"/{event_id}/{ORG_ID}/{SEASON_ID}/{division_id}/{STANDING_CONFERENCE}"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} for event={event_id} div={division_id}")
            return []
        p = StandingsParser()
        p.feed(r.text)
        p.finalize()
        return p.teams
    except Exception as e:
        print(f"  ERROR {url}: {e}")
        return []


def clean_club_name(team_name, age_group):
    """Strip age group suffix to approximate club name."""
    for ag in AGE_GROUPS.values():
        suffix = f" Pre-ECNL {ag}"
        if team_name.endswith(suffix):
            return team_name[: -len(suffix)].strip()
        # Also try plain birth year
        suffix2 = f" {ag}"
        if team_name.endswith(suffix2):
            return team_name[: -len(suffix2)].strip()
    return team_name


def main():
    all_teams = []
    seen_team_ids = set()

    total = len(CONFERENCES) * len(AGE_GROUPS)
    done = 0

    for event_id, conf_name in CONFERENCES.items():
        for div_id, age_group in AGE_GROUPS.items():
            teams = fetch_standings(event_id, div_id)
            for t in teams:
                if t["team_id"] not in seen_team_ids:
                    seen_team_ids.add(t["team_id"])
                    all_teams.append({
                        "team_id":    t["team_id"],
                        "club_id":    t["club_id"],
                        "team_name":  t["team_name"],
                        "club_name":  clean_club_name(t["team_name"], age_group),
                        "age_group":  age_group,
                        "conference": conf_name,
                        "league":     "Pre-ECNL Boys",
                        "season":     "2025-26",
                    })

            done += 1
            print(f"  {done}/{total} — {conf_name} {age_group}: {len(teams)} teams")
            time.sleep(0.15)

    print(f"\nTotal unique teams: {len(all_teams)}")

    # ── Write teams CSV ───────────────────────────────────────────
    teams_path = "/Users/Eric/Documents/Claude/soccer/data/pre_ecnl_teams.csv"
    with open(teams_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "team_id", "club_id", "team_name", "club_name",
            "age_group", "conference", "league", "season"
        ])
        w.writeheader()
        w.writerows(sorted(all_teams, key=lambda x: (x["conference"], x["age_group"], x["team_name"])))
    print(f"Teams written to {teams_path}")

    # ── Deduplicate to clubs CSV ──────────────────────────────────
    clubs = {}
    for t in all_teams:
        cid = t["club_id"]
        if cid not in clubs:
            clubs[cid] = {
                "club_id":    cid,
                "club_name":  t["club_name"],
                "conference": t["conference"],
                "league":     "Pre-ECNL Boys",
                "season":     "2025-26",
                "age_groups": set(),
            }
        clubs[cid]["age_groups"].add(t["age_group"])

    clubs_list = []
    for c in clubs.values():
        row = dict(c)
        row["age_groups"] = " | ".join(sorted(row["age_groups"]))
        clubs_list.append(row)

    clubs_path = "/Users/Eric/Documents/Claude/soccer/data/pre_ecnl_clubs.csv"
    with open(clubs_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "club_id", "club_name", "conference", "age_groups", "league", "season"
        ])
        w.writeheader()
        w.writerows(sorted(clubs_list, key=lambda x: (x["conference"], x["club_name"])))

    print(f"Clubs written to {clubs_path}")
    print(f"Unique clubs: {len(clubs_list)}")

    conf_summary = defaultdict(set)
    for t in all_teams:
        conf_summary[t["conference"]].add(t["club_id"])
    print("\nClubs per conference:")
    for conf, club_ids in sorted(conf_summary.items()):
        print(f"  {conf}: {len(club_ids)} clubs")


if __name__ == "__main__":
    main()
