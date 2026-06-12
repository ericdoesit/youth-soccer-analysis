#!/usr/bin/env python3
"""
Pull all committed college-recruit player profiles from SoccerWire's public
Elasticsearch proxy and write data/college_commitments_soccerwire.csv.

One row per player: name, gender, recruit (graduation) year, position,
state, youth club, youth league, college team, college division.

Caveat recorded in the data: SoccerWire profiles are self-reported and skew
heavily toward ECNL girls (SoccerWire's historic coverage partner). Boys
coverage is sparse (~30-500/class vs ~2,400 actual US D1 entrants/yr), so
league shares describe THIS dataset, not the full recruiting universe.

Rerun anytime:
    python3 scripts/pull_soccerwire_commitments.py
"""

import csv
import json
import urllib.request

ES_URL = "https://www.soccerwire.com/wp-json/v1/elastic-proxy/soccerwirecom-post-1/_search"
OUT = "data/college_commitments_soccerwire.csv"
PAGE = 500

FIELDS = [
    "player", "gender", "recruit_year", "position", "state",
    "club", "league", "college_team", "college_division", "profile_slug",
]


def first(meta_list, key="value", idx=0):
    """meta fields are lists of dicts; return the requested entry or ''. """
    if not meta_list:
        return ""
    try:
        return meta_list[idx].get(key, "") or ""
    except (IndexError, AttributeError):
        return ""


def name_of(meta_list):
    """related_clubs/leagues store [{id...}, {name...}]; take the non-numeric value."""
    if not meta_list:
        return ""
    for entry in meta_list:
        v = entry.get("value", "")
        if v and not str(v).isdigit():
            return v
    return ""


def fetch(offset):
    body = {
        "from": offset,
        "size": PAGE,
        "sort": [{"post_id": "asc"}],
        "_source": ["post_title", "post_name", "meta.gender", "meta.graduation_year",
                     "meta.positions", "meta.state_province", "meta.related_clubs_players",
                     "meta.related_leagues_players", "meta.college_team",
                     "meta.college_division_committed"],
        "query": {"bool": {"filter": [
            {"term": {"post_type.raw": "players"}},
            {"term": {"meta.is_committed.raw": "1"}},
        ]}},
    }
    req = urllib.request.Request(ES_URL, json.dumps(body).encode(),
                                 {"Content-Type": "application/json",
                                  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main():
    rows, offset, total = [], 0, None
    while total is None or offset < total:
        data = fetch(offset)
        total = data["hits"]["total"]
        hits = data["hits"]["hits"]
        if not hits:
            break
        for h in hits:
            s = h["_source"]
            m = s.get("meta", {})
            rows.append({
                "player": s.get("post_title", ""),
                "gender": first(m.get("gender")),
                "recruit_year": first(m.get("graduation_year")),
                "position": first(m.get("positions"), key="raw"),
                "state": first(m.get("state_province"), key="raw"),
                "club": name_of(m.get("related_clubs_players")),
                "league": name_of(m.get("related_leagues_players")),
                "college_team": first(m.get("college_team")),
                "college_division": first(m.get("college_division_committed")),
                "profile_slug": s.get("post_name", ""),
            })
        offset += PAGE
        print(f"  fetched {min(offset, total)}/{total}")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} players to {OUT}")


if __name__ == "__main__":
    main()
