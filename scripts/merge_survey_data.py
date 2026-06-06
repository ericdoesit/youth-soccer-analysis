#!/usr/bin/env python3
"""
Merge old (15-question) and new (10-question) Typeform survey exports
into a single canonical CSV: data/survey_merged.csv

Canonical columns:
  submission_id, submitted_at, zip_code, income_bracket,
  club_level, club_name, travel_scope,
  club_fee_annual, private_coaching_annual,
  travel_annual*, equipment_annual*, tournament_annual*,
  training_hours_week, private_coaching_hours_week,
  years_in_club, recruited*
  (*) = old survey only; null for new responses
"""

import csv
import os
from datetime import datetime

DATA_DIR = "data"
OUT_FILE = os.path.join(DATA_DIR, "survey_merged.csv")

CANONICAL_FIELDS = [
    "submission_id",
    "submitted_at",
    "zip_code",
    "income_bracket",
    "club_level",
    "club_name",
    "travel_scope",
    "club_fee_annual",
    "private_coaching_annual",
    "travel_annual",           # old survey only
    "equipment_annual",        # old survey only
    "tournament_annual",       # old survey only
    "training_hours_week",
    "private_coaching_hours_week",
    "years_in_club",
    "recruited",               # old survey only
]

# ── Old survey (15q) column mapping ──────────────────────────────────────────
OLD_MAP = {
    "submission_id":                  "submission_id",
    "submitted_at":                   "submitted_at",
    "Please provide your zip code for regional analysis.": "zip_code",
    "Which of these best describes your household income bracket.": "income_bracket",
    "Which of these best describes your household income bracket?": "income_bracket",
    "Which level best describes your child's current club soccer?": "club_level",
    "What is the name of your child's team?":                       "club_name",
    "What is the typical geographic scope of your child's team competition?": "travel_scope",
    "What are your total annual club costs? (registration & monthly fees)":   "club_fee_annual",
    "Total annual cost for private coaching, training camps, or clinics (outside club)": "private_coaching_annual",
    "What are your annual travel costs for soccer? (hotels, gas, food, etc.)": "travel_annual",
    "How much do you spend each year on equipment (cleats, shin guards, bag, etc.)?": "equipment_annual",
    "How much do you spend on tournament or showcase entry fees each year?":    "tournament_annual",
    "How many hours per week does your child receive club training?":           "training_hours_week",
    "How many hours per week does your child receive private coaching outside the club?": "private_coaching_hours_week",
    "Total years your child has participated in club soccer":                  "years_in_club",
    "Has your child been recruited to play college soccer?":                   "recruited",
}

# ── New survey (10q) column mapping ──────────────────────────────────────────
NEW_MAP = {
    "submission_id":                  "submission_id",
    "submitted_at":                   "submitted_at",
    "Please provide your zip code for regional analysis.": "zip_code",
    "Which of these best describes your household income bracket?": "income_bracket",
    "Which level best describes your child's current club soccer?": "club_level",
    "What is the name of your child's team?":                       "club_name",
    "Which best describes your team's travel scope?":               "travel_scope",
    "What is your total annual club costs? (registration & monthly fees)": "club_fee_annual",
    "Total annual spending on private coaching, camps, clinics (even if not every month)": "private_coaching_annual",
    "How many hours per week does your child spend in soccer training?":        "training_hours_week",
    "How many hours per week does your child receive additional coaching outside the team?": "private_coaching_hours_week",
    "Total years in club soccer (if applicable)":                              "years_in_club",
}


def clean_money(val):
    """Strip $ and commas from money strings, return int or empty string."""
    if not val:
        return ""
    val = str(val).replace("$", "").replace(",", "").strip()
    try:
        return int(float(val))
    except ValueError:
        return ""


def clean_int(val):
    if not val:
        return ""
    try:
        return int(float(str(val).strip()))
    except ValueError:
        return ""


def remap_row(raw_row, col_map):
    """Map raw CSV row to canonical fields using col_map."""
    out = {f: "" for f in CANONICAL_FIELDS}
    for raw_col, canonical in col_map.items():
        if raw_col in raw_row:
            out[canonical] = raw_row[raw_col]
    return out


def compute_total(row):
    """Calculate total annual cost from available fields."""
    parts = [
        clean_money(row.get("club_fee_annual")),
        clean_money(row.get("private_coaching_annual")),
        clean_money(row.get("travel_annual")),
        clean_money(row.get("equipment_annual")),
        clean_money(row.get("tournament_annual")),
    ]
    total = sum(p for p in parts if isinstance(p, int))
    return total if total > 0 else ""


def detect_format(headers):
    """Return 'old' or 'new' based on columns present."""
    if any("Total years your child" in h for h in headers):
        return "old"
    return "new"


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def main():
    # Find all survey CSVs except the merged output
    files = sorted([
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.startswith("survey_responses") and f.endswith(".csv")
        and "merged" not in f and "master" not in f
    ])

    print(f"Found {len(files)} source files:")
    for f in files:
        print(f"  {f}")

    all_rows = {}  # submission_id → canonical row

    for path in files:
        rows, headers = load_csv(path)
        fmt = detect_format(headers)
        col_map = OLD_MAP if fmt == "old" else NEW_MAP
        print(f"\n{os.path.basename(path)} → format={fmt}, rows={len(rows)}")

        for raw in rows:
            sid = raw.get("submission_id", "").strip()
            if not sid:
                continue

            canonical = remap_row(raw, col_map)

            # Clean numeric fields
            for money_field in ["club_fee_annual", "private_coaching_annual",
                                 "travel_annual", "equipment_annual", "tournament_annual"]:
                canonical[money_field] = clean_money(canonical[money_field])

            for int_field in ["training_hours_week", "private_coaching_hours_week", "years_in_club"]:
                canonical[int_field] = clean_int(canonical[int_field])

            # Merge: old survey rows are richer — don't overwrite with blanks
            if sid in all_rows:
                existing = all_rows[sid]
                for field in CANONICAL_FIELDS:
                    if canonical[field] != "" and existing[field] == "":
                        existing[field] = canonical[field]
            else:
                all_rows[sid] = canonical

    # Sort by submitted_at
    sorted_rows = sorted(
        all_rows.values(),
        key=lambda r: r.get("submitted_at", "")
    )

    # Add computed total
    output_fields = CANONICAL_FIELDS + ["total_annual_est"]
    for row in sorted_rows:
        row["total_annual_est"] = compute_total(row)

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"\nMerged {len(sorted_rows)} unique responses → {OUT_FILE}")
    print("\n--- Summary ---")
    for row in sorted_rows:
        total = row["total_annual_est"]
        print(f"  {row['zip_code']:6s}  {row['club_level']:<20s}  club=${row['club_fee_annual'] or '?':>6}  "
              f"private=${row['private_coaching_annual'] or '?':>6}  "
              f"total_est=${total or '?':>7}  income={row['income_bracket']}")


if __name__ == "__main__":
    main()
