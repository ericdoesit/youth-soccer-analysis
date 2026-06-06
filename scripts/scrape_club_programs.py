#!/usr/bin/env python3
"""
Phase 1: For each club on GotSport event 43086, extract the external website URL.
         Handles two cases:
           a) Normal: /clubs/12345  → look for external link on page
           b) Malformed: /clubs/www.someclub.org → domain is in the path itself

Phase 2: Fetch each club homepage, find program/league/team pages.

Phase 3: For each program page, try to extract a fee table.

Outputs:
  data/club_websites.csv   — club, gotsport_url, website
  data/club_programs.csv   — club, website, program_name, program_url, program_type
  data/club_fees.csv       — club, program_name, age_group, fee, fee_url
"""

import csv
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_GOTSPORT = "https://system.gotsport.com"
CLUBS_CSV = "data/socal_league_teams.csv"
WEBSITE_CSV = "data/club_websites.csv"
PROGRAMS_CSV = "data/club_programs.csv"
FEES_CSV = "data/club_fees.csv"

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
]

# URL path suffixes/prefixes that indicate a program page regardless of name
# e.g. /xyz-soccer, /xyz-league, /our-boys, /spring-xyz
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

# Don't follow these as program links
SKIP_PATTERNS = [
    "facebook", "instagram", "twitter", "youtube", "tiktok", "linkedin",
    "mailto:", "tel:", "javascript:", "#", "privacy", "terms", "login",
    "logout", "signin", "contact", "about-us", "staff", "news", "blog",
    "photo", "gallery", "sponsor", "donate", "shop", "store",
]


def get_soup(url, timeout=15):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def looks_like_domain(s):
    """Return True if string looks like a domain (www.foo.org, foo.com, etc.)"""
    return bool(re.match(r'^(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}.*$', s))


def extract_website_from_gotsport(soup, gotsport_url):
    """
    Two strategies:
    1. If the GotSport URL path ends in a domain (malformed link), extract it directly.
    2. Otherwise scan the page for the first external link.
    """
    # Strategy 1: malformed URL like /clubs/www.anaheimfc.org
    path_segments = urlparse(gotsport_url).path.rstrip("/").split("/")
    last_segment = path_segments[-1] if path_segments else ""
    if looks_like_domain(last_segment):
        domain = last_segment
        if not domain.startswith("http"):
            domain = "https://" + domain
        return domain.rstrip("/")

    # Strategy 2: find external link on page
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("http") and "gotsport.com" not in href:
            # Skip social links
            if not any(skip in href.lower() for skip in ["facebook", "instagram", "twitter", "youtube"]):
                return href.rstrip("/")
    return None


def get_club_gotsport_urls():
    """Fetch the clubs index and return {club_name: gotsport_club_url}."""
    print("Fetching GotSport clubs index...")
    soup = get_soup(f"{BASE_GOTSPORT}/org_event/events/43086/clubs")
    mapping = {}
    for a in soup.select("a[href*='/clubs/']"):
        href = a["href"].strip()
        if href.startswith("/"):
            href = BASE_GOTSPORT + href
        name = a.get_text(strip=True)
        if name and name not in mapping:
            mapping[name] = href
    print(f"  Found {len(mapping)} clubs")
    return mapping


# ── Phase 2 helpers ───────────────────────────────────────────────────────────

def classify_program(text, url):
    combined = (text + " " + url).lower()
    # Top tier: ECNL National, MLS Next, Homegrown
    if any(k in combined for k in ["mls next", "mlsnext", "mls-next", "mls homegrown", "homegrown",
                                    "ecnl-overview", "ecnl national", "ecnl boys", "ecnl girls"]):
        return "Top Elite"
    # High elite: ECNL Regional League, DPL, EAL, NPL
    if any(k in combined for k in ["ecnl-rl", "ecnl rl", "ecnl regional", "ecnl_rl",
                                    "dpl", "eal", "npl", "ga white", "ga blue", "girls academy",
                                    "elite academy"]):
        return "Elite"
    # Pipeline: Pre-ECNL, Pre-RL, Academy prep
    if any(k in combined for k in ["pre-ecnl", "pre ecnl", "pre-rl", "pre rl",
                                    "aspire", "pre-academy", "pre academy"]):
        return "Elite/Competitive"
    # Competitive travel leagues
    if any(k in combined for k in ["competitive", "travel", "select", "socal", "flight",
                                    "social soccer", "premier", "elite"]):
        return "Competitive"
    # Recreational
    if any(k in combined for k in ["rec ", "recreational", "fall rec", "spring rec"]):
        return "Recreational"
    # Development / youngest players
    if any(k in combined for k in ["micro", "tots", "juniors", "development", "u6", "u7", "u8", "pathway", "mini"]):
        return "Development"
    return "Program"


def should_skip(text, href):
    tl = (text + " " + href).lower()
    return any(s in tl for s in SKIP_PATTERNS)


def is_nav_link(tag):
    """Return True if this <a> tag lives inside a nav, header, or menu element."""
    for parent in tag.parents:
        if parent.name in ("nav", "header"):
            return True
        classes = " ".join(parent.get("class", []))
        if any(c in classes.lower() for c in ("nav", "menu", "navbar", "sidebar")):
            return True
    return False


def collect_program_links(soup, base_url):
    """
    Return deduplicated list of (href, text) that look like program pages.

    Three ways a link qualifies:
    1. Keyword match — text or URL contains a known program keyword
    2. Wildcard URL pattern — URL path matches a common suffix/prefix pattern
    3. Nav link — lives in a <nav>/<header> and isn't skipped
       (nav items are almost always top-level program sections)
    """
    base_domain = urlparse(base_url).netloc.replace("www.", "")
    found = {}

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = a["href"].strip()

        if not text or len(text) < 3:
            continue

        # Resolve relative URLs
        if href.startswith("/") or not href.startswith("http"):
            href = urljoin(base_url, href)

        # Must be same domain or a known club management platform
        link_domain = urlparse(href).netloc.replace("www.", "")
        same_domain = (base_domain in link_domain or link_domain in base_domain)
        third_party = any(p in link_domain for p in [
            "ottosport.ai",
            "sprocketsports.com",
            "gotsport.com",
            "demosphere.com",
            "affinitysoccer.com",
        ])
        if not (same_domain or third_party):
            continue

        # Skip homepage, anchors, and social/utility links
        if should_skip(text, href):
            continue
        parsed_path = urlparse(href).path
        if parsed_path in ("", "/", base_url):
            continue

        combined = (text + " " + href).lower()
        keyword_match = any(kw in combined for kw in PROGRAM_KEYWORDS)
        wildcard_match = bool(WILDCARD_SUFFIXES.search(href) or WILDCARD_PREFIXES.search(href))
        nav_match = is_nav_link(a)

        if (keyword_match or wildcard_match or nav_match) and href not in found:
            found[href] = text

    return list(found.items())  # [(href, text), ...]


# ── Phase 3: Fee extraction ───────────────────────────────────────────────────

MONEY_RE = re.compile(r'\$[\d,]+')
AGE_RE = re.compile(r'U\d{1,2}|Ages?\s*\d+[-–]\d+|\d{4}/\d{2,4}', re.IGNORECASE)


def extract_fees_from_page(club_name, program_name, url, soup):
    """Look for tables or lists that contain dollar amounts and age groups."""
    fees = []

    # Look in <table> elements
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        header_row = rows[0] if rows else None
        headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])] if header_row else []

        for row in rows[1:]:
            cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
            row_text = " ".join(cells)
            if MONEY_RE.search(row_text):
                age = next((c for c in cells if AGE_RE.search(c)), "")
                fee = next((c for c in cells if MONEY_RE.search(c)), "")
                label = next((c for c in cells if c and c != age and c != fee), "")
                fees.append({
                    "club": club_name,
                    "program_name": program_name or label,
                    "age_group": age,
                    "fee": fee,
                    "fee_url": url,
                })

    # Also look for <li> or <p> patterns like "U13-U19: $2,855"
    if not fees:
        for elem in soup.find_all(["li", "p", "div", "td"]):
            text = elem.get_text(" ", strip=True)
            if MONEY_RE.search(text) and AGE_RE.search(text):
                age_match = AGE_RE.search(text)
                fee_match = MONEY_RE.search(text)
                fees.append({
                    "club": club_name,
                    "program_name": program_name,
                    "age_group": age_match.group() if age_match else "",
                    "fee": fee_match.group() if fee_match else "",
                    "fee_url": url,
                })

    # Deduplicate
    seen = set()
    deduped = []
    for f in fees:
        key = (f["age_group"], f["fee"])
        if key not in seen and key != ("", ""):
            seen.add(key)
            deduped.append(f)
    return deduped


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # ── Phase 1 ──
    club_gotsport = get_club_gotsport_urls()

    already_scraped = {}
    if os.path.exists(WEBSITE_CSV):
        with open(WEBSITE_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                already_scraped[row["club"]] = row["website"]
        print(f"Resume: {len(already_scraped)} clubs already have website URLs")

    clubs_to_fetch = [(n, u) for n, u in club_gotsport.items() if n not in already_scraped]
    print(f"Phase 1: Fetching website URLs for {len(clubs_to_fetch)} remaining clubs...")

    new_website_rows = []
    for i, (club_name, gotsport_url) in enumerate(clubs_to_fetch, 1):
        try:
            print(f"  [{i}/{len(clubs_to_fetch)}] {club_name}")
            soup = get_soup(gotsport_url)
            website = extract_website_from_gotsport(soup, gotsport_url)
            already_scraped[club_name] = website or ""
            new_website_rows.append({
                "club": club_name,
                "gotsport_url": gotsport_url,
                "website": website or "",
            })
            print(f"    → {website or 'no website'}")
            time.sleep(2)
        except Exception as e:
            print(f"    ERROR [{club_name}] phase1: {type(e).__name__}: {e}")
            already_scraped[club_name] = ""
            new_website_rows.append({"club": club_name, "gotsport_url": gotsport_url, "website": ""})

    write_header = not os.path.exists(WEBSITE_CSV)
    with open(WEBSITE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["club", "gotsport_url", "website"])
        if write_header:
            writer.writeheader()
        writer.writerows(new_website_rows)
    print(f"Website URLs saved to {WEBSITE_CSV}")

    # ── Phase 2 + 3 ──
    clubs_with_sites = [(c, w) for c, w in already_scraped.items() if w]
    print(f"\nPhase 2+3: Scraping {len(clubs_with_sites)} club websites for programs + fees...")

    all_programs = []
    all_fees = []

    for i, (club_name, website) in enumerate(clubs_with_sites, 1):
        print(f"  [{i}/{len(clubs_with_sites)}] {club_name} — {website}")
        try:
            soup = get_soup(website)
            links = collect_program_links(soup, website)
            print(f"    → {len(links)} program links")

            # Check homepage itself for fees
            homepage_fees = extract_fees_from_page(club_name, "Homepage", website, soup)
            if homepage_fees:
                print(f"    → {len(homepage_fees)} fee entries on homepage")
                all_fees.extend(homepage_fees)

            for href, text in links:
                ptype = classify_program(text, href)
                all_programs.append({
                    "club": club_name,
                    "website": website,
                    "program_name": text,
                    "program_url": href,
                    "program_type": ptype,
                })

                # Fetch program page for fees
                try:
                    time.sleep(1)
                    prog_soup = get_soup(href)
                    page_fees = extract_fees_from_page(club_name, text, href, prog_soup)
                    if page_fees:
                        print(f"      $ {len(page_fees)} fee entries: {text}")
                        all_fees.extend(page_fees)
                except Exception as e:
                    print(f"      ERROR [{club_name}] fee page [{text}]: {type(e).__name__}: {e}")

        except Exception as e:
            print(f"    ERROR [{club_name}] phase2: {type(e).__name__}: {e}")

        # Write incrementally every 10 clubs
        if i % 10 == 0:
            _write_programs(all_programs)
            _write_fees(all_fees)
            print(f"    [checkpoint saved]")

        time.sleep(5)

    _write_programs(all_programs)
    _write_fees(all_fees)

    print(f"\nDone.")
    print(f"  Programs: {len(all_programs)} → {PROGRAMS_CSV}")
    print(f"  Fees:     {len(all_fees)} → {FEES_CSV}")

    from collections import Counter
    types = Counter(p["program_type"] for p in all_programs)
    print("\n--- Program Types Found ---")
    for t, count in types.most_common():
        print(f"  {t}: {count}")


def _write_programs(rows):
    with open(PROGRAMS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["club", "website", "program_name", "program_url", "program_type"])
        writer.writeheader()
        writer.writerows(rows)


def _write_fees(rows):
    with open(FEES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["club", "program_name", "age_group", "fee", "fee_url"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
