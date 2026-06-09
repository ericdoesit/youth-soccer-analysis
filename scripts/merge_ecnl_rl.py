#!/usr/bin/env python3
"""
Merge ECNL-RL datasets:
  1. Read existing conference-only ecnl_rl_teams.csv (clean attribution)
  2. Run playoff bracket scrapes to find additional teams not in conf standings
  3. Merge by team_id — conference-standings rows take priority
  4. Write merged ecnl_rl_teams.csv and ecnl_rl_clubs.csv
"""

import requests
import csv
import time
from html.parser import HTMLParser
from collections import defaultdict

HEADERS = {
    "Referer": "https://theecnl.com/sports/2023/8/8/ECNLRLB_0808230006.aspx",
    "Origin": "https://theecnl.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

ORG_ID    = 16
SEASON_ID = 72

CONFERENCES = {
    3891: "Carolinas",
    3892: "Chicago Metro",
    3893: "Far West",
    3894: "Florida",
    3895: "Frontier",
    3896: "Golden State",
    3899: "Great Lakes Alliance",
    3898: "Greater Michigan Alliance",
    3900: "Gulf Coast",
    3901: "Heartland",
    3902: "Mid-America",
    3903: "Midwest",
    3904: "Mountain",
    3905: "New England",
    3906: "NorCal",
    3907: "North Atlantic",
    3908: "Northeast",
    3910: "Northwest",
    3909: "NTX",
    3911: "SoCal",
    3912: "Southeast",
    4001: "Southwest",
    3973: "STXCL",
    3913: "Texas",
    3998: "Twin Cities",
    3915: "Virginia",
}

AGE_GROUPS = {
    18364: "B2013",
    18363: "B2012",
    18362: "B2011",
    18361: "B2010",
    18360: "B2009",
    18359: "B2008/2007",
}

PLAYOFF_TYPES = {
    23: "Playoffs-East",
    24: "Playoffs-Central",
    25: "Playoffs-South",
    26: "Playoffs-West",
}

TEAMS_PATH = "/Users/Eric/Documents/Claude/soccer/data/ecnl_rl_teams.csv"
CLUBS_PATH = "/Users/Eric/Documents/Claude/soccer/data/ecnl_rl_clubs.csv"


class StandingsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.teams = []
        self.in_team = False
        self.in_conf_span = False
        self.current = {}

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        if tag == "span" and "individual-team-item" in attrs_d.get("class", ""):
            if self.current.get("team_name"):
                self.teams.append(dict(self.current))
            self.in_team = True
            self.current = {
                "club_id":    attrs_d.get("data-club-id", ""),
                "team_id":    attrs_d.get("data-team-id", ""),
                "event_id":   attrs_d.get("data-event-id", ""),
                "team_name":  "",
                "conf_label": "",
            }
        elif tag == "span" and not attrs_d.get("class") and self.current.get("team_name"):
            self.in_conf_span = True

    def handle_data(self, data):
        d = data.strip()
        if not d:
            return
        if self.in_team and not self.current.get("team_name"):
            self.current["team_name"] = d
            self.in_team = False
        elif self.in_conf_span:
            if "ECNL RL Boys" in d:
                conf = d.replace("ECNL RL Boys", "").replace("2025-26", "").strip()
                self.current["conf_label"] = conf
            self.in_conf_span = False

    def handle_endtag(self, tag):
        if self.in_conf_span:
            self.in_conf_span = False

    def finalize(self):
        if self.current.get("team_name"):
            self.teams.append(dict(self.current))
            self.current = {}


def fetch(event_id, division_id, standing_id):
    url = (
        f"https://api.athleteone.com/api/Script/get-conference-standings"
        f"/{event_id}/{ORG_ID}/{SEASON_ID}/{division_id}/{standing_id}"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        p = StandingsParser()
        p.feed(r.text)
        p.finalize()
        return p.teams
    except Exception as e:
        print(f"  ERROR: {e}")
        return []


def clean_club_name(team_name):
    for ag in AGE_GROUPS.values():
        suffix = f" ECNL RL {ag}"
        if team_name.endswith(suffix):
            return team_name[: -len(suffix)].strip()
    return team_name


def main():
    # ── Step 1: load conference-only data (clean attribution) ─────
    existing = {}
    with open(TEAMS_PATH, newline="") as f:
        for row in csv.DictReader(f):
            existing[row["team_id"]] = row
    print(f"Loaded {len(existing)} teams from conference-only file")

    # ── Step 2: scrape playoff brackets for additional teams ──────
    new_teams = []
    total = len(CONFERENCES) * len(AGE_GROUPS) * len(PLAYOFF_TYPES)
    done = 0

    for event_id, conf_name in CONFERENCES.items():
        for div_id, age_group in AGE_GROUPS.items():
            for standing_id, standing_name in PLAYOFF_TYPES.items():
                teams = fetch(event_id, div_id, standing_id)
                for t in teams:
                    if t["team_id"] not in existing:
                        # Derive conference from conf_label in the HTML,
                        # fall back to CONFERENCES dict by event_id attr
                        actual_conf = (
                            t.get("conf_label")
                            or CONFERENCES.get(int(t["event_id"]) if t["event_id"] else 0, conf_name)
                        )
                        new_teams.append({
                            "team_id":    t["team_id"],
                            "club_id":    t["club_id"],
                            "team_name":  t["team_name"],
                            "club_name":  clean_club_name(t["team_name"]),
                            "age_group":  age_group,
                            "conference": actual_conf,
                            "league":     "ECNL RL Boys",
                            "season":     "2025-26",
                        })
                        existing[t["team_id"]] = new_teams[-1]

                done += 1
                if done % 26 == 0:
                    print(f"  {done}/{total} playoff calls done, {len(new_teams)} new teams found")
                time.sleep(0.15)

    print(f"\nNew teams from playoffs: {len(new_teams)}")
    all_teams = list(existing.values())
    print(f"Total merged teams: {len(all_teams)}")

    # ── Step 3: write merged teams CSV ───────────────────────────
    fieldnames = ["team_id", "club_id", "team_name", "club_name",
                  "age_group", "conference", "league", "season"]
    with open(TEAMS_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(all_teams, key=lambda x: (x["conference"], x["age_group"], x["team_name"])))
    print(f"Teams written to {TEAMS_PATH}")

    # ── Step 4: deduplicate to clubs CSV ─────────────────────────
    clubs = {}
    for t in all_teams:
        cid = t["club_id"]
        if cid not in clubs:
            clubs[cid] = {
                "club_id":    cid,
                "club_name":  t["club_name"],
                "conference": t["conference"],
                "league":     "ECNL RL Boys",
                "season":     "2025-26",
                "age_groups": set(),
            }
        clubs[cid]["age_groups"].add(t["age_group"])

    clubs_list = []
    for c in clubs.values():
        row = dict(c)
        row["age_groups"] = " | ".join(sorted(row["age_groups"]))
        clubs_list.append(row)

    with open(CLUBS_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "club_id", "club_name", "conference", "age_groups", "league", "season"
        ])
        w.writeheader()
        w.writerows(sorted(clubs_list, key=lambda x: (x["conference"], x["club_name"])))

    print(f"Clubs written to {CLUBS_PATH}")
    print(f"Unique clubs: {len(clubs_list)}")

    conf_summary = defaultdict(set)
    for t in all_teams:
        conf_summary[t["conference"]].add(t["club_id"])
    print("\nClubs per conference:")
    for conf, ids in sorted(conf_summary.items()):
        print(f"  {conf}: {len(ids)} clubs")


if __name__ == "__main__":
    main()
