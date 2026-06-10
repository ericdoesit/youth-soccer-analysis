#!/usr/bin/env python3
"""
Build clubs.csv — one row per club (boys/mixed only).

Level system (L1 = most elite, L0 = recreational foundation):
  PRO  Professional (USL Championship / League One / W League)
  L1   Pro Pipeline  (MLS NEXT Homegrown Division, MLS Pro Academies)
  L2   National Elite  (ECNL Boys, USL Academy)
  L3   National Competitive  (MLS NEXT AD, ECNL-RL, EA, NAL)
  L4   Regional/National Bridge  (USYS Elite 64, The National League)
  L5   Regional Travel  (N1 districts, SoCal, Coast Soccer, EDP, USL Youth)
  L0   Foundation / Recreational  (AYSO, City/County Parks)

top_tier = most elite level the club operates at.
Backfills age_groups from: ecnl_rl_clubs, pre_ecnl_clubs, npl_teams, gotsport_cas_u10_boys.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

DATA       = Path("/Users/Eric/Documents/Claude/soccer/data")
MASTER_IN  = DATA / "clubs_raw.csv"
MASTER_OUT = DATA / "clubs.csv"

NAME_CORRECTIONS = {
    "ac delray":       "AC Delray Rush",
    "ac delray, inc.": "AC Delray Rush",
}

LEAGUE_CORRECTIONS = {
    "SoCal Soccer League":         "SoCal",
    "MLS NEXT Academy Division":   "MLS Next AD",
    "MLS NEXT Homegrown Division": "MLS Next HD",
    # NPL → N1 (all districts)
    "NorCal NPL":            "NorCal N1",
    "SoCal NPL":             "SoCal N1",
    "GLA NPL":               "GLA N1",
    "MDL NPL (GLA Boys)":    "MDL N1 (GLA Boys)",
    "Central States NPL":    "Central States N1",
    "Minnesota NPL":         "Minnesota N1",
    "Mountain West NPL":     "Mountain West N1",
    "NISL NPL (Chicago)":    "NISL N1 (Chicago)",
    "Red River NPL":         "Red River N1",
    "FCL NPL (Florida)":     "FCL N1 (Florida)",
    "CPSL NPL (Chesapeake)": "CPSL N1 (Chesapeake)",
    "VPSL NPL (Virginia)":   "VPSL N1 (Virginia)",
    "WPL NPL (Washington)":  "WPL N1 (Washington)",
}

# League → level. Applied after LEAGUE_CORRECTIONS, overrides source tier values.
TIER_OVERRIDES = {
    # L1 — Pro Pipeline
    "MLS Next HD":               "L1",
    # L2 — National Elite
    "ECNL Boys":                 "L2",
    "ECNL":                      "L2",
    "USL League Two":            "L2",
    # L3 — National Competitive
    "MLS Next AD":               "L3",
    "ECNL Regional League":      "L3",
    "Elite Academy League":      "L3",
    "National Academy League":   "L3",
    "Development Player League": "L3",
    "Girls Academy":             "L3",
    # L4 — Regional/National Bridge
    "USYS Elite 64":             "L4",
    "The National League":       "L4",
    # L5 — Regional Travel (N1 districts)
    "NorCal N1":                 "L5",
    "SoCal N1":                  "L5",
    "GLA N1":                    "L5",
    "MDL N1 (GLA Boys)":         "L5",
    "Central States N1":         "L5",
    "Minnesota N1":              "L5",
    "Mountain West N1":          "L5",
    "NISL N1 (Chicago)":         "L5",
    "Red River N1":              "L5",
    "FCL N1 (Florida)":          "L5",
    "CPSL N1 (Chesapeake)":      "L5",
    "VPSL N1 (Virginia)":        "L5",
    "WPL N1 (Washington)":       "L5",
    # L5 — Regional Travel (other regional leagues)
    "SoCal":                     "L5",
    "Coast Soccer":              "L5",
    "EDP Soccer":                "L5",
    "USL Youth":                 "L5",
    "Frontier Premier League":   "L5",
    "South Atlantic Premier":    "L5",
    "Mid-Atlantic Premier":      "L5",
    # PRO — professional
    "USL Championship":          "PRO",
    "USL League One":            "PRO",
    "USL Super League":          "PRO",
    "USL W League":              "PRO",
}

# Higher rank = more elite. Used for top_tier and sort order.
TIER_RANK = {"PRO": 8, "L1": 7, "L2": 6, "L3": 5, "L4": 4, "L5": 3, "L0": 2}

# Conference → state for ECNL RL clubs (unambiguous mappings only)
ECNL_RL_CONF_STATE = {
    "NorCal":                   "CA",
    "Golden State":             "CA",
    "Far West":                 "CA",
    "SoCal":                    "CA",
    "Florida":                  "FL",
    "Gulf Coast":               "TX",
    "NTX":                      "TX",
    "STXCL":                    "TX",
    "Texas":                    "TX",
    "Twin Cities":              "MN",
    "Virginia":                 "VA",
    "Chicago Metro":            "IL",
    "Greater Michigan Alliance":"MI",
    "Mountain":                 "CO",
    "Frontier":                 "CO",
    "Northwest":                "WA",
    "New England":              "MA",
    "Southwest":                "AZ",
}


def normalize_name(name: str) -> str:
    cleaned = name.strip()
    return NAME_CORRECTIONS.get(cleaned.lower(), cleaned)


def resolve_gender(genders: set) -> str:
    g = {v.lower().strip() for v in genders}
    if g == {"girls"}:
        return "Girls"
    if g == {"boys"}:
        return "Boys"
    return "Both"


def birth_year_to_age(by: str) -> str:
    m = re.match(r"B(\d{4})", by.strip())
    if m:
        age = 2026 - int(m.group(1))
        if 5 <= age <= 22:
            return f"U{age}"
    return by.strip()


def parse_age_groups(raw: str) -> list[str]:
    parts = re.split(r"[|,]", raw)
    return [birth_year_to_age(p.strip()) for p in parts if p.strip()]


def age_sort_key(ag: str) -> int:
    m = re.search(r"\d+", ag)
    return int(m.group()) if m else 99


def top_tier(tiers: list[str]) -> str:
    best = max((TIER_RANK.get(t, 0) for t in tiers), default=0)
    for label, rank in TIER_RANK.items():
        if rank == best:
            return label
    return ""


def strip_ecnl_rl_suffix(name: str) -> str:
    """'Club Name ECNL RL LB S.Cal B13' → 'Club Name'"""
    # Cut at " ECNL RL" (covers location codes + birth year variants)
    result = re.sub(r"\s+ECNL RL\b.*$", "", name).strip()
    if result == name:
        # Fallback for the few entries that omit "ECNL" prefix
        result = re.sub(r"\s+RL\s+[BG]\d{2,4}.*$", "", name).strip()
    return result


# ── Age group backfill ────────────────────────────────────────────────────────
def load_age_groups() -> dict[str, set[str]]:
    ag: dict[str, set[str]] = defaultdict(set)

    for fname, name_col, ag_col in [
        ("ecnl_rl_clubs.csv",  "club_name", "age_groups"),
        ("pre_ecnl_clubs.csv", "club_name", "age_groups"),
    ]:
        p = DATA / fname
        if p.exists():
            with open(p) as f:
                for row in csv.DictReader(f):
                    raw_name = row[name_col].strip()
                    key = strip_ecnl_rl_suffix(raw_name).lower()
                    for g in parse_age_groups(row.get(ag_col, "")):
                        ag[key].add(g)

    npl = DATA / "npl_teams.csv"
    if npl.exists():
        with open(npl) as f:
            for row in csv.DictReader(f):
                if row.get("gender", "").strip().lower() in ("male", "boys", "m", ""):
                    key = row["club"].strip().lower()
                    age_val = row.get("age", "").strip()
                    if age_val:
                        ag[key].add(age_val)

    gs = DATA / "gotsport_cas_u10_boys.csv"
    if gs.exists():
        with open(gs) as f:
            for row in csv.DictReader(f):
                ag[row["club_name"].strip().lower()].add("U10")

    return ag


# ── Load ECNL RL as a league data source ─────────────────────────────────────
def load_ecnl_rl_rows() -> list[dict]:
    """Return synthetic raw_rows for ECNL RL clubs (one row per unique club name)."""
    p = DATA / "ecnl_rl_clubs.csv"
    if not p.exists():
        return []

    seen: set[str] = set()
    rows: list[dict] = []

    with open(p) as f:
        for rec in csv.DictReader(f):
            raw_name = rec["club_name"].strip()
            club_name = strip_ecnl_rl_suffix(raw_name)
            key = club_name.lower()
            if key in seen:
                continue
            seen.add(key)

            state = ECNL_RL_CONF_STATE.get(rec.get("conference", "").strip(), "")

            rows.append({
                "club_name":    club_name,
                "city":         "",
                "state":        state,
                "league":       "ECNL Regional League",
                "tier":         "L3",
                "tier_label":   "National Competitive",
                "conference":   rec.get("conference", ""),
                "division":     "",
                "gender":       "Boys",
                "source_file":  "ecnl_rl_clubs.csv",
                "_clean_name":  normalize_name(club_name),
            })

    return rows


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    age_groups_lookup = load_age_groups()

    raw_rows = []
    skipped_girls = 0
    with open(MASTER_IN) as f:
        for row in csv.DictReader(f):
            if row.get("gender", "").strip().lower() == "girls":
                skipped_girls += 1
                continue
            if row.get("club_name", "").strip().startswith("***"):
                continue
            row["_clean_name"] = normalize_name(row["club_name"])
            raw_rows.append(row)

    # Add ECNL RL clubs as a proper league source
    ecnl_rl_rows = load_ecnl_rl_rows()
    raw_rows.extend(ecnl_rl_rows)
    print(f"ECNL RL rows added: {len(ecnl_rl_rows)}")

    # Canonical state: prefer non-blank (first pass)
    name_to_state: dict[str, str] = {}
    for row in raw_rows:
        key = row["_clean_name"].lower()
        state = row.get("state", "").strip()
        if state and key not in name_to_state:
            name_to_state[key] = state

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in raw_rows:
        key = row["_clean_name"].lower()
        state = name_to_state.get(key, row.get("state", "").strip())
        groups[(key, state)].append(row)

    print(f"Input rows (skipped {skipped_girls} girls-only): {len(raw_rows)}")
    print(f"Unique (name, state) groups: {len(groups)}")

    out_rows = []
    for (name_lower, state), rows in groups.items():
        club_name = rows[0]["_clean_name"]
        city      = next((r["city"].strip() for r in rows if r.get("city", "").strip()), "")

        # Collect (league, tier) pairs — skip TBD/blank tiers and blank leagues
        league_tier_pairs: list[tuple[str, str]] = []
        seen_lt_keys: set[str] = set()
        seen_sources: list[str] = []
        genders: set[str] = set()

        for r in rows:
            league = r.get("league", "").strip()
            tier   = r.get("tier", "").strip()
            src    = r.get("source_file", "").strip()
            g      = r.get("gender", "").strip()

            if league and tier and tier not in ("TBD", ""):
                league = LEAGUE_CORRECTIONS.get(league, league)
                tier   = TIER_OVERRIDES.get(league, tier)
                lt_key = f"{league}|{tier}"
                if lt_key not in seen_lt_keys:
                    seen_lt_keys.add(lt_key)
                    league_tier_pairs.append((league, tier))

            if src and src not in seen_sources:
                seen_sources.append(src)
            if g:
                genders.add(g)

        # Sort pairs least → most elite (L5 first, L1/PRO last)
        league_tier_pairs.sort(key=lambda lt: (TIER_RANK.get(lt[1], 0), lt[0]))

        # Two aligned columns: leagues = "SoCal, SoCal N1, ECNL Boys"
        #                       tiers  = "L5, L5, L2"  (same count, positionally matched)
        leagues_str = ", ".join(l for l, _ in league_tier_pairs)
        tiers_str   = ", ".join(t for _, t in league_tier_pairs)

        tiers_only = [t for _, t in league_tier_pairs]
        top = top_tier(tiers_only)

        # Age groups
        raw_ags = age_groups_lookup.get(name_lower, set())
        sorted_ags = sorted(raw_ags, key=age_sort_key) if raw_ags else []

        out_rows.append({
            "club_name":        club_name,
            "city":             city,
            "state":            state,
            "leagues":          leagues_str,
            "tiers":            tiers_str,
            "top_tier":         top,
            "age_groups":       ", ".join(sorted_ags),
            "gender":           resolve_gender(genders),
            "annual_fee_range": "",
            "travel_scope":     "",
            "source_files":     ", ".join(seen_sources),
        })

    # ── Merge blank-league stubs into real entries ────────────────────────────
    real   = {r["club_name"].lower(): r for r in out_rows if r["leagues"]}
    stubs  = [r for r in out_rows if not r["leagues"]]
    merged = 0

    for stub in stubs:
        stub_key = stub["club_name"].lower()
        for real_key, real_row in real.items():
            if real_row["state"] == stub["state"] and (
                stub_key in real_key or real_key in stub_key
            ) and stub_key != real_key:
                existing = set(real_row["source_files"].split(", "))
                for src in stub["source_files"].split(", "):
                    existing.add(src.strip())
                real_row["source_files"] = ", ".join(sorted(s for s in existing if s))
                merged += 1
                break

    out_rows = [r for r in out_rows if r["leagues"]]
    out_rows.sort(key=lambda r: (r["state"], r["club_name"].lower()))

    print(f"Stubs merged and removed: {merged + (len(stubs) - merged)} total stubs")

    fieldnames = [
        "club_name", "city", "state", "leagues", "tiers", "top_tier",
        "age_groups", "gender", "annual_fee_range", "travel_scope", "source_files",
    ]

    with open(MASTER_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print(f"\nOutput rows: {len(out_rows)}")
    print(f"Written to:  {MASTER_OUT}")

    # Spot checks
    for name in ["lafc so cal", "ac delray rush", "la breakers"]:
        matches = [r for r in out_rows if name in r["club_name"].lower()]
        print(f"\n{name.title()} ({len(matches)} row(s)):")
        for r in matches:
            print(f"  leagues    = {r['leagues']}")
            print(f"  tiers      = {r['tiers']}")
            print(f"  top_tier   = {r['top_tier']}")
            print(f"  age_groups = {r['age_groups']}")

    # Tier distribution
    from collections import Counter
    tier_dist = Counter(r["top_tier"] for r in out_rows)
    print("\ntop_tier distribution:")
    for t in ["PRO", "L1", "L2", "L3", "L4", "L5", "L0", ""]:
        if tier_dist[t]:
            print(f"  {t or '(blank)'}: {tier_dist[t]}")

    with_ages = sum(1 for r in out_rows if r["age_groups"])
    print(f"\nRows with age_groups: {with_ages} / {len(out_rows)}")

    # Verify alignment
    mismatched = []
    for r in out_rows:
        nl = len([x for x in r["leagues"].split(",") if x.strip()])
        nt = len([x for x in r["tiers"].split(",")   if x.strip()])
        if nl != nt:
            mismatched.append((r["club_name"], nl, nt))
    if mismatched:
        print(f"\nMISALIGNED rows ({len(mismatched)}):")
        for name, nl, nt in mismatched[:10]:
            print(f"  {name}: {nl} leagues, {nt} tiers")
    else:
        print(f"\nAll rows: leagues count == tiers count ✓")

    with open(MASTER_OUT) as f:
        counts = set(len(row) for row in csv.reader(f))
    print(f"Column counts: {counts}  (should be {{11}})")


if __name__ == "__main__":
    main()
