#!/usr/bin/env python3
"""
Convert legacy Typeform responses (data/survey_merged.csv) into rows
matching the Tally -> Google Sheets column layout, for one-time append
into the master Google Sheet.

Output: data/typeform_for_sheet.csv
"""

import csv
import os

SRC = "data/survey_merged.csv"
OUT = "data/typeform_for_sheet.csv"

# Exact header row of the Google Sheet (Tally integration)
SHEET_COLUMNS = [
    "Submission ID",
    "Respondent ID",
    "Submitted at",
    "What gender league do they play in?",
    "What age group?",
    "What league does your child's team compete in?",
    "Please specify the league here. ",
    "What is the name of your child's team?",
    "How far does your team typically travel for games?",
    "How many sessions per week does your child spend in club practice?",
    "Does your athlete participate in additional soccer clubs?",
    "What are your annual club fees?",
    "If seperate from club fees. What are your annual league fees?",
    "What are your annual tournament fees?",
    "What are your annual uniform/kit fees?",
    "Estimated travel costs?",
    "How much do you spend on private coaching per year?",
    "Please provide your zip code for regional analysis.",
    "Which of these best describes your household income bracket?",
    "Anything else you'd like to share about your experience?",
]

# Typeform travel answers -> current Tally option labels
TRAVEL_MAP = {
    "Regional (2-6 hours, occasional overnight)": "Regional (2–6 hrs)",
    "National (multiple states, regular flights)": "National",
    "Local only (within 2 hours)": "Regional (1–2 hrs)",
    "Regional": "Regional (2–6 hrs)",
    "Local": "Local (under 1 hr)",
}


def coaching_bucket(val):
    """Exact dollar amount -> Tally range option."""
    if val == "":
        return ""
    n = int(val)
    if n == 0:
        return "$0"
    if n < 500:
        return "$0-$500"
    if n <= 2000:
        return "$500-$2000"
    return "$2,000+"


def import_note(row):
    """Preserve Typeform-only fields that have no column in the new sheet."""
    parts = ["Imported from Typeform"]
    if row["club_level"]:
        parts.append(f"level: {row['club_level']}")
    if row["travel_scope"]:
        parts.append(f"travel (orig): {row['travel_scope']}")
    if row["training_hours_week"]:
        parts.append(f"training {row['training_hours_week']} hrs/wk")
    if row["private_coaching_hours_week"]:
        parts.append(f"outside coaching {row['private_coaching_hours_week']} hrs/wk")
    if row["private_coaching_annual"]:
        parts.append(f"private coaching exact ${row['private_coaching_annual']}/yr")
    if row["years_in_club"]:
        parts.append(f"{row['years_in_club']} yrs in club")
    if row["recruited"]:
        parts.append(f"recruited: {row['recruited']}")
    return "; ".join(parts)


def main():
    with open(SRC, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if not r["submission_id"].startswith("tally_")]

    out_rows = []
    for r in rows:
        league = "ECNL" if "ECNL" in (r["club_name"] or "") else ""
        out_rows.append({
            "Submission ID": r["submission_id"],
            "Respondent ID": "",
            "Submitted at": r["submitted_at"].replace("T", " ").replace("Z", ""),
            "What gender league do they play in?": "",
            "What age group?": "",
            "What league does your child's team compete in?": league,
            "Please specify the league here. ": "",
            "What is the name of your child's team?": r["club_name"],
            "How far does your team typically travel for games?": TRAVEL_MAP.get(r["travel_scope"], r["travel_scope"]),
            "How many sessions per week does your child spend in club practice?": "",
            "Does your athlete participate in additional soccer clubs?": "",
            "What are your annual club fees?": r["club_fee_annual"],
            "If seperate from club fees. What are your annual league fees?": "",
            "What are your annual tournament fees?": r["tournament_annual"],
            "What are your annual uniform/kit fees?": r["equipment_annual"],
            "Estimated travel costs?": r["travel_annual"],
            "How much do you spend on private coaching per year?": coaching_bucket(r["private_coaching_annual"]),
            "Please provide your zip code for regional analysis.": r["zip_code"],
            "Which of these best describes your household income bracket?": r["income_bracket"],
            "Anything else you'd like to share about your experience?": import_note(r),
        })

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SHEET_COLUMNS)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
