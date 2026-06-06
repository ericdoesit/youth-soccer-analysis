"""
MLS Draft Survival Analysis: 2020-2025 picks vs. 2026 active rosters.
Cross-references our draft CSV against Capology 2026 salary data.
"""
import csv, re
from pathlib import Path
from difflib import SequenceMatcher

BASE = Path(__file__).parent.parent / "data"

# ── Load Capology 2026 active players ──────────────────────────────────────
def load_capology():
    players = {}
    with open(BASE / "capology_2026_raw.txt") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Rk"):
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                continue
            try:
                int(parts[0])  # first col must be a rank number
            except ValueError:
                continue
            name = parts[1].strip()
            squad = parts[4].strip() if len(parts) > 4 else ""
            salary = parts[6].strip() if len(parts) > 6 else ""
            # strip duplicate marker
            name_clean = re.sub(r"\s+dup\d*$", "", name, flags=re.IGNORECASE)
            players[name_clean.lower()] = {"name": name_clean, "squad": squad, "salary": salary}
    return players

# ── Load draft picks ───────────────────────────────────────────────────────
def load_drafts():
    picks = []
    with open(BASE / "mls_draft_picks_2020_2025.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            picks.append(row)
    return picks

# ── Name matching ──────────────────────────────────────────────────────────
def normalize(name):
    """Lowercase, strip accents approximation, remove punctuation."""
    s = name.lower()
    # common accent replacements
    for a, b in [("é","e"),("è","e"),("ê","e"),("á","a"),("à","a"),("ä","a"),
                 ("ó","o"),("ö","o"),("ú","u"),("ü","u"),("ñ","n"),("ç","c"),
                 ("í","i"),("ï","i"),("ã","a"),("â","a"),("ô","o"),("ő","o"),
                 ("ä","a"),("ā","a")]:
        s = s.replace(a, b)
    s = re.sub(r"[^a-z\s]", "", s)
    return s.strip()

def fuzzy_match(draft_name, capology_dict):
    """Try exact, then normalized, then fuzzy last-name match."""
    dn = normalize(draft_name)
    # exact normalized
    for key, val in capology_dict.items():
        if normalize(key) == dn:
            return val
    # last-name match (both last names must match + first initial)
    dn_parts = dn.split()
    if len(dn_parts) >= 2:
        d_first, d_last = dn_parts[0], dn_parts[-1]
        for key, val in capology_dict.items():
            kp = normalize(key).split()
            if not kp:
                continue
            k_last = kp[-1]
            k_first = kp[0] if len(kp) > 1 else ""
            if k_last == d_last and (not k_first or k_first[0] == d_first[0]):
                return val
    return None

# ── Main analysis ──────────────────────────────────────────────────────────
def run():
    cap = load_capology()
    picks = load_drafts()

    results = []
    for p in picks:
        name = p["player_name"]
        match = fuzzy_match(name, cap)
        results.append({
            "year": int(p["year"]),
            "overall": int(p["overall_pick"]),
            "round": p["round"],
            "player": name,
            "nationality": p["nationality"],
            "college": p["college"],
            "team_drafted": p["team_drafted"],
            "active_2026": bool(match),
            "squad_2026": match["squad"] if match else "",
            "salary_2026": match["salary"] if match else "",
        })

    # ── Print survival table ─────────────────────────────────────────────
    print("\n" + "="*70)
    print("MLS DRAFT SURVIVAL ANALYSIS: 2020-2025 → Active 2026 Rosters")
    print("="*70)
    print(f"\n{'Year':<6} {'Picks':<7} {'Active':<8} {'Survival%':<12} {'R1%':<8} {'R2%':<8} {'R3%'}")
    print("-"*65)

    year_stats = {}
    for year in range(2020, 2026):
        yr = [r for r in results if r["year"] == year]
        active = [r for r in yr if r["active_2026"]]
        r1 = [r for r in yr if r["round"] == "R1"]
        r1a = [r for r in r1 if r["active_2026"]]
        r2 = [r for r in yr if r["round"] == "R2"]
        r2a = [r for r in r2 if r["active_2026"]]
        r3 = [r for r in yr if r["round"] == "R3"]
        r3a = [r for r in r3 if r["active_2026"]]
        pct = len(active)/len(yr)*100 if yr else 0
        r1p = len(r1a)/len(r1)*100 if r1 else 0
        r2p = len(r2a)/len(r2)*100 if r2 else 0
        r3p = len(r3a)/len(r3)*100 if r3 else 0
        year_stats[year] = {"total":len(yr),"active":len(active),"pct":pct,
                            "r1":len(r1),"r1a":len(r1a),"r1p":r1p,
                            "r2":len(r2),"r2a":len(r2a),"r2p":r2p,
                            "r3":len(r3),"r3a":len(r3a),"r3p":r3p}
        print(f"{year:<6} {len(yr):<7} {len(active):<8} {pct:<12.1f} {r1p:<8.1f} {r2p:<8.1f} {r3p:.1f}")

    all_active = [r for r in results if r["active_2026"]]
    total = len(results)
    print("-"*65)
    print(f"{'TOTAL':<6} {total:<7} {len(all_active):<8} {len(all_active)/total*100:<12.1f}")

    # ── Round-level summary ───────────────────────────────────────────────
    print("\n\n--- Survival by Round (all years combined) ---")
    for rnd in ["R1","R2","R3"]:
        rp = [r for r in results if r["round"] == rnd]
        ra = [r for r in rp if r["active_2026"]]
        print(f"  {rnd}: {len(ra)}/{len(rp)} = {len(ra)/len(rp)*100:.1f}%")

    # ── Nationality breakdown ─────────────────────────────────────────────
    print("\n--- US vs International survival ---")
    us = [r for r in results if r["nationality"] in ("United States", "USA", "US", "American")]
    if not us:
        us = [r for r in results if r["nationality"] == "United States"]
    usa = [r for r in us if r["active_2026"]]
    intl = [r for r in results if r not in us]
    intla = [r for r in intl if r["active_2026"]]
    print(f"  US players:    {len(usa)}/{len(us)} = {len(usa)/len(us)*100:.1f}%")
    print(f"  International: {len(intla)}/{len(intl)} = {len(intla)/len(intl)*100:.1f}%")

    # ── Show confirmed active players ────────────────────────────────────
    print("\n--- Confirmed active 2026 (draft picks still in MLS) ---")
    for r in sorted(all_active, key=lambda x: (x["year"], x["overall"])):
        print(f"  {r['year']} Rd{r['round'][1]} #{r['overall']:>3}  {r['player']:<28} "
              f"→ {r['squad_2026']:<25} {r['salary_2026']}")

    # ── Save results CSV ──────────────────────────────────────────────────
    out = BASE / "mls_draft_survival_results.csv"
    with open(out, "w", newline="") as f:
        fields = ["year","overall","round","player","nationality","college",
                  "team_drafted","active_2026","squad_2026","salary_2026"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(results)
    print(f"\nSaved → {out}")

    # ── Print key stats for report ───────────────────────────────────────
    print("\n\n=== KEY STATS FOR REPORT ===")
    print(f"Total 2020-2025 MLS draft picks: {total}")
    print(f"Still active on MLS roster 2026: {len(all_active)} ({len(all_active)/total*100:.1f}%)")
    print(f"Did NOT survive to 2026 MLS roster: {total - len(all_active)} ({(total-len(all_active))/total*100:.1f}%)")
    r1all = [r for r in results if r["round"]=="R1"]
    r1act = [r for r in r1all if r["active_2026"]]
    print(f"R1 survival: {len(r1act)}/{len(r1all)} = {len(r1act)/len(r1all)*100:.1f}%")
    r2all = [r for r in results if r["round"]=="R2"]
    r2act = [r for r in r2all if r["active_2026"]]
    print(f"R2 survival: {len(r2act)}/{len(r2all)} = {len(r2act)/len(r2all)*100:.1f}%")
    r3all = [r for r in results if r["round"]=="R3"]
    r3act = [r for r in r3all if r["active_2026"]]
    print(f"R3 survival: {len(r3act)}/{len(r3all)} = {len(r3act)/len(r3all)*100:.1f}%")

if __name__ == "__main__":
    run()
