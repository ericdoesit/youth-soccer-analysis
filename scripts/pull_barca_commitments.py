#!/usr/bin/env python3
"""
Build data/barca_residency_commitments.csv: every college commitment listed
on barcaresidencyacademyusa.com (classes 2020+), enriched with previous
clubs and hometown from SoccerWire player profiles where they exist.

The commitments page only carries name / class / university. Previous
clubs, state, and city come from SoccerWire's public ES proxy; a profile
is only trusted when its club list actually includes a Barca entry or its
committed college agrees with the Barca page. Blank cells = no reliable
public record, not zero.

Rerun anytime:
    python3 scripts/pull_barca_commitments.py
"""

import csv
import json
import re
import time
import urllib.request
from html import unescape

PAGE = "https://barcaresidencyacademyusa.com/college-commitments/"
ES_URL = "https://www.soccerwire.com/wp-json/v1/elastic-proxy/soccerwirecom-post-1/_search"
OUT = "data/barca_residency_commitments.csv"
ACADEMY = "Barca Residency Academy (Casa Grande, AZ)"
MIN_YEAR = 2020
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

FIELDS = ["player", "grad_year", "college", "academy",
          "previous_club_1", "previous_club_2", "home_state", "home_city",
          "profile_match"]


def fetch(url, data=None):
    headers = dict(UA)
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data, headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_commitments(html):
    body = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html)
    lines = [l.strip() for l in
             unescape(re.sub(r"<[^>]+>", "\n", body)).splitlines() if l.strip()]
    rows, i = [], 0
    while i < len(lines) - 2:
        if re.fullmatch(r"20\d\d", lines[i + 1]) and lines[i] not in (
                "Student-Athlete", "Graduation Year", "University"):
            rows.append({"player": lines[i], "grad_year": int(lines[i + 1]),
                         "college": lines[i + 2]})
            i += 3
        else:
            i += 1
    return [r for r in rows if r["grad_year"] >= MIN_YEAR]


def sw_lookup(name, college):
    """Find the player's SoccerWire profile; return clubs/state/city."""
    body = {
        "size": 3,
        "_source": ["post_title", "meta.related_clubs_players",
                    "meta.state_province", "meta.birthplace_city",
                    "meta.college_team", "meta.high_school"],
        "query": {"bool": {
            "filter": [{"term": {"post_type.raw": "players"}}],
            "must": [{"match_phrase": {"post_title": name}}],
        }},
    }
    try:
        hits = json.loads(fetch(ES_URL, body))["hits"]["hits"]
    except OSError:
        return None
    for h in hits:
        m = h["_source"].get("meta", {})
        clubs = [e.get("value", "") for e in m.get("related_clubs_players", [])
                 if e.get("value") and not str(e["value"]).isdigit()]
        sw_college = " ".join(e.get("value", "") for e in m.get("college_team", []))
        barca = any("barca" in c.lower() for c in clubs)
        college_match = college and sw_college and (
            college.lower().split(" univ")[0][:12] in sw_college.lower()
            or sw_college.lower().split(" men")[0][:12] in college.lower())
        if not (barca or college_match):
            continue
        prev = [c for c in clubs if "barca" not in c.lower()]
        state = next((e.get("raw", "") for e in m.get("state_province", [])), "")
        city = next((e.get("value", "") for e in m.get("birthplace_city", [])), "")
        return {"previous_club_1": prev[0] if prev else "",
                "previous_club_2": prev[1] if len(prev) > 1 else "",
                "home_state": state, "home_city": city,
                "profile_match": "barca-club" if barca else "college-match"}
    return None


def main():
    rows = parse_commitments(fetch(PAGE))
    print(f"{len(rows)} commitments (classes {MIN_YEAR}+) on the Barca page")
    matched = 0
    for r in rows:
        r["academy"] = ACADEMY
        info = sw_lookup(r["player"], r["college"])
        r.update(info or {"previous_club_1": "", "previous_club_2": "",
                          "home_state": "", "home_city": "", "profile_match": ""})
        matched += bool(info)
        time.sleep(0.25)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}; "
          f"{matched} enriched from SoccerWire profiles")


if __name__ == "__main__":
    main()
