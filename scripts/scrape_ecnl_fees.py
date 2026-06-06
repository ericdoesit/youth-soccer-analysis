#!/usr/bin/env python3
"""
Scrape ECNL Boys club fee/tuition data from each club's website.

Tries common fee page URL patterns, scrapes dollar amounts, and stores
the best match in data/ecnl_boys_fees.csv.

Run:
    python3 scripts/scrape_ecnl_fees.py [--limit N]

Output: data/ecnl_boys_fees.csv
"""

import re
import csv
import time
import argparse
import urllib.request
import urllib.parse
from pathlib import Path

CLUBS_FILE = Path(__file__).parent.parent / "data" / "ecnl_clubs.csv"
OUT_FILE   = Path(__file__).parent.parent / "data" / "ecnl_boys_fees.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

# URL suffixes to try for fee pages, in priority order
FEE_URL_SUFFIXES = [
    "/boys-ecnl",
    "/ecnl",
    "/ecnl-boys",
    "/fees",
    "/tuition",
    "/competitive",
    "/programs",
    "/boys",
    "/",
]

# Patterns that suggest a dollar amount is an annual fee
FEE_RE = re.compile(
    r'\$\s*(\d{1,2},\d{3}|\d{3,5})(?:\s*[-–]\s*\$\s*(\d{1,2},\d{3}|\d{3,5}))?'
    r'(?:[^A-Za-z]{0,30}(?:per\s*year|\/year|annual|season|tuition|registration))?',
    re.IGNORECASE,
)

# Dollar amounts likely to be annual fees (range: $1,500–$15,000)
ANNUAL_MIN = 1500
ANNUAL_MAX = 15000


def parse_dollars(s: str) -> int | None:
    try:
        return int(s.replace(",", ""))
    except ValueError:
        return None


def fetch(url: str, timeout: int = 6) -> str | None:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return None
            ct = r.headers.get("Content-Type", "")
            if "text" not in ct and "html" not in ct:
                return None
            raw = r.read(100_000)   # only read first 100KB
            return raw.decode("utf-8", errors="replace")
    except Exception:
        return None


def extract_fees(html: str) -> list[dict]:
    """Return candidate annual fee amounts extracted from HTML text."""
    # Strip tags for text scanning
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    results = []
    for m in FEE_RE.finditer(text):
        low = parse_dollars(m.group(1))
        high = parse_dollars(m.group(2)) if m.group(2) else low
        if low and ANNUAL_MIN <= low <= ANNUAL_MAX:
            results.append({"fee_low": low, "fee_high": high or low,
                            "context": text[max(0, m.start()-60):m.end()+60].strip()})
    return results


def find_fees_for_club(base_url: str) -> dict | None:
    """Try fee URL patterns; return first page with plausible annual fees."""
    base = base_url.rstrip("/")
    for suffix in FEE_URL_SUFFIXES:
        url = base + suffix
        html = fetch(url)
        if html is None:
            continue
        fees = extract_fees(html)
        if fees:
            # Prefer fee with lowest value (most likely to be tuition-only, not total)
            fees.sort(key=lambda x: x["fee_low"])
            return {
                "fee_page_url": url,
                "tuition_low":  fees[0]["fee_low"],
                "tuition_high": fees[0]["fee_high"],
                "context":      fees[0]["context"],
            }
        time.sleep(0.3)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only process first N clubs")
    args = parser.parse_args()

    with open(CLUBS_FILE) as f:
        clubs = list(csv.DictReader(f))

    if args.limit:
        clubs = clubs[:args.limit]

    results = []
    for i, c in enumerate(clubs):
        cid, name, website = c["club_id"], c["club_name"], c["website"]
        print(f"[{i+1}/{len(clubs)}] {name}", end=" ... ", flush=True)
        if not website:
            print("no website, skipping")
            continue
        info = find_fees_for_club(website)
        if info:
            print(f"${info['tuition_low']:,}–${info['tuition_high']:,}")
        else:
            print("not found")
        results.append({
            "club_id":       cid,
            "club_name":     name,
            "state":         c["state"],
            "conference":    c["conferences"].split(" | ")[0],
            "website":       website,
            "fee_page_url":  info["fee_page_url"]  if info else "",
            "tuition_low":   info["tuition_low"]   if info else "",
            "tuition_high":  info["tuition_high"]  if info else "",
            "context":       info["context"][:200] if info else "",
        })
        time.sleep(0.5)

    with open(OUT_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "club_id","club_name","state","conference","website",
            "fee_page_url","tuition_low","tuition_high","context"
        ])
        w.writeheader()
        w.writerows(results)

    found = sum(1 for r in results if r["tuition_low"])
    print(f"\nDone: {found}/{len(results)} clubs with fee data → {OUT_FILE.name}")


if __name__ == "__main__":
    main()
