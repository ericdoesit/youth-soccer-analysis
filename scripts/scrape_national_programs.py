#!/usr/bin/env python3
"""
Phase 2 national scraper: reads national_clubs.csv (from scrape_national_clubs.py),
visits each club website, extracts program pages and fee data.

Resumable — skips clubs already in ussoccerparent_programs_scrape.csv.

Output: data/ussoccerparent_programs_scrape.csv  — state, club, website, program_name, program_url, program_type
        data/national_fees.csv      — state, club, program_name, age_group, fee, fee_url
"""

import csv
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

DATA_DIR = "data"
CLUBS_IN   = os.path.join(DATA_DIR, "national_clubs.csv")
PROGRAMS_CSV = os.path.join(DATA_DIR, "ussoccerparent_programs_scrape.csv")
FEES_CSV     = os.path.join(DATA_DIR, "national_fees.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

PROGRAM_KEYWORDS = [
    "elite", "academy", "competitive", "travel", "recreational", "rec",
    "select", "program", "team", "league", "ecnl", "mls", "npl", "eal",
    "spring", "fall", "futsal", "tryout", "register", "development",
    "girls", "boys", "premier", "flight", "division", "socal", "club soccer",
    "dpl", "ga ", "homegrown", "social soccer",
    "micro", "tots", "u6", "u7", "u8", "u9", "u10", "u11", "u12",
    "u13", "u14", "u15", "u16", "u17", "u18", "u19",
    "aspire", "pathway", "prep", "pre-academy", "pre academy",
    "fees", "cost", "pricing", "registration",
]

WILDCARD_SUFFIXES = re.compile(
    r'([-/])(soccer|league|teams?|program|academy|registration|tryout|'
    r'futsal|training|camp|clinic|select|travel|competitive|recreational|rec|'
    r'elite|boys|girls|spring|fall|seasonal|schedule|division|flight|'
    r'structure|overview|pricing|fees?|cost|rates?)(/|$)',
    re.IGNORECASE
)
WILDCARD_PREFIXES = re.compile(
    r'/(our-|boys-|girls-|fall-|spring-|summer-|winter-|u\d{1,2}-)',
    re.IGNORECASE
)

SKIP_PATTERNS = [
    "facebook", "instagram", "twitter", "youtube", "tiktok", "linkedin",
    "mailto:", "tel:", "javascript:", "#", "privacy", "terms", "login",
    "logout", "signin", "contact", "about-us", "staff", "news", "blog",
    "photo", "gallery", "sponsor", "donate", "shop", "store",
]

MONEY_RE = re.compile(r'\$[\d,]+')
AGE_RE = re.compile(r'U\d{1,2}|Ages?\s*\d+[-–]\d+|\d{4}/\d{2,4}', re.IGNORECASE)


def get_soup(url, timeout=12):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def should_skip(text, href):
    tl = (text + " " + href).lower()
    return any(s in tl for s in SKIP_PATTERNS)


def is_nav_link(tag):
    for parent in tag.parents:
        if parent.name in ("nav", "header"):
            return True
        classes = " ".join(parent.get("class", []))
        if any(c in classes.lower() for c in ("nav", "menu", "navbar", "sidebar")):
            return True
    return False


def classify_program(text, url):
    combined = (text + " " + url).lower()
    if any(k in combined for k in ["mls next", "mlsnext", "mls-next", "homegrown",
                                    "ecnl national", "ecnl boys", "ecnl girls"]):
        return "Top Elite"
    if any(k in combined for k in ["ecnl regional", "ecnl rl", "dpl", "eal", "npl",
                                    "girls academy", "elite academy"]):
        return "Elite"
    if any(k in combined for k in ["pre-ecnl", "pre ecnl", "pre-rl", "aspire", "pre-academy"]):
        return "Elite/Competitive"
    if any(k in combined for k in ["competitive", "travel", "select", "premier", "elite"]):
        return "Competitive"
    if any(k in combined for k in ["rec ", "recreational"]):
        return "Recreational"
    if any(k in combined for k in ["micro", "tots", "development", "u6", "u7", "u8", "pathway"]):
        return "Development"
    return "Program"


def collect_program_links(soup, base_url):
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    found = {}

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = a["href"].strip()

        if not text or len(text) < 3:
            continue
        if href.startswith("/") or not href.startswith("http"):
            href = urljoin(base_url, href)

        link_domain = urlparse(href).netloc.replace("www.", "")
        same_domain = (base_domain in link_domain or link_domain in base_domain)
        third_party = any(p in link_domain for p in [
            "ottosport.ai", "sprocketsports.com", "gotsport.com",
            "demosphere.com", "affinitysoccer.com",
        ])
        if not (same_domain or third_party):
            continue
        if should_skip(text, href):
            continue
        parsed_path = urlparse(href).path
        if parsed_path in ("", "/"):
            continue

        combined = (text + " " + href).lower()
        keyword_match = any(kw in combined for kw in PROGRAM_KEYWORDS)
        wildcard_match = bool(WILDCARD_SUFFIXES.search(href) or WILDCARD_PREFIXES.search(href))
        nav_match = is_nav_link(a)

        if (keyword_match or wildcard_match or nav_match) and href not in found:
            found[href] = text

    return list(found.items())


def extract_fees(club_name, program_name, url, soup):
    fees = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows[1:]:
            cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
            row_text = " ".join(cells)
            if MONEY_RE.search(row_text):
                age = next((c for c in cells if AGE_RE.search(c)), "")
                fee = next((c for c in cells if MONEY_RE.search(c)), "")
                label = next((c for c in cells if c and c != age and c != fee), "")
                fees.append({
                    "club": club_name, "program_name": program_name or label,
                    "age_group": age, "fee": fee, "fee_url": url,
                })

    if not fees:
        for elem in soup.find_all(["li", "p", "div", "td"]):
            text = elem.get_text(" ", strip=True)
            if MONEY_RE.search(text) and AGE_RE.search(text):
                age_m = AGE_RE.search(text)
                fee_m = MONEY_RE.search(text)
                fees.append({
                    "club": club_name, "program_name": program_name,
                    "age_group": age_m.group() if age_m else "",
                    "fee": fee_m.group() if fee_m else "",
                    "fee_url": url,
                })

    seen = set()
    deduped = []
    for f in fees:
        key = (f["age_group"], f["fee"])
        if key not in seen and key != ("", ""):
            seen.add(key)
            deduped.append(f)
    return deduped


def main():
    if not os.path.exists(CLUBS_IN):
        print(f"ERROR: {CLUBS_IN} not found. Run scrape_national_clubs.py first.")
        return

    with open(CLUBS_IN, newline="", encoding="utf-8") as f:
        clubs = list(csv.DictReader(f))
    print(f"Loaded {len(clubs)} clubs from {CLUBS_IN}")

    # Build resume set from existing programs CSV
    done_clubs = set()
    if os.path.exists(PROGRAMS_CSV):
        with open(PROGRAMS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done_clubs.add((row["state"], row["club"]))
        print(f"Resume: {len(done_clubs)} clubs already scraped")

    to_scrape = [c for c in clubs if (c["state"], c["club_name"]) not in done_clubs]
    print(f"Scraping {len(to_scrape)} remaining clubs...\n")

    prog_fields = ["state", "club", "website", "program_name", "program_url", "program_type"]
    fee_fields  = ["state", "club", "program_name", "age_group", "fee", "fee_url"]

    # Open in append mode (handles resume)
    prog_mode = "a" if done_clubs else "w"
    fee_mode  = "a" if os.path.exists(FEES_CSV) and done_clubs else "w"

    prog_f = open(PROGRAMS_CSV, prog_mode, newline="", encoding="utf-8")
    fee_f  = open(FEES_CSV,     fee_mode,  newline="", encoding="utf-8")
    prog_w = csv.DictWriter(prog_f, fieldnames=prog_fields)
    fee_w  = csv.DictWriter(fee_f,  fieldnames=fee_fields)
    if prog_mode == "w":
        prog_w.writeheader()
    if fee_mode == "w":
        fee_w.writeheader()

    total_programs = 0
    total_fees = 0

    try:
        for i, club in enumerate(to_scrape, 1):
            state      = club["state"]
            club_name  = club["club_name"]
            website    = club.get("website_url", "").strip()

            print(f"[{i:04d}/{len(to_scrape)}] {state} | {club_name}")

            if not website or not website.startswith("http"):
                print(f"  skip — no website")
                continue

            # Phase 2: get program links from homepage
            try:
                soup = get_soup(website)
                links = collect_program_links(soup, website)
                print(f"  {len(links)} program links")

                for prog_url, prog_text in links:
                    prog_type = classify_program(prog_text, prog_url)
                    prog_w.writerow({
                        "state": state, "club": club_name, "website": website,
                        "program_name": prog_text, "program_url": prog_url,
                        "program_type": prog_type,
                    })
                    total_programs += 1

                    # Phase 3: extract fees from each program page
                    try:
                        prog_soup = get_soup(prog_url)
                        fees = extract_fees(club_name, prog_text, prog_url, prog_soup)
                        for fee in fees:
                            fee["state"] = state
                            fee_w.writerow(fee)
                        total_fees += len(fees)
                        if fees:
                            print(f"    {prog_text[:50]}: {len(fees)} fee entries")
                        time.sleep(1)
                    except Exception as e:
                        print(f"    ERROR phase3 [{prog_text[:40]}]: {type(e).__name__}: {e}")

            except Exception as e:
                print(f"  ERROR phase2 [{club_name}]: {type(e).__name__}: {e}")

            prog_f.flush()
            fee_f.flush()
            time.sleep(2)

    finally:
        prog_f.close()
        fee_f.close()

    print(f"\nDone.")
    print(f"  Programs: {total_programs} -> {PROGRAMS_CSV}")
    print(f"  Fees:     {total_fees} -> {FEES_CSV}")


if __name__ == "__main__":
    main()
