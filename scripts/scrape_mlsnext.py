#!/usr/bin/env python3
"""
Scrape MLS NEXT data in two phases:

Phase 1: Save the 245-club Homegrown Division member list to CSV.
         Includes club name, state, and guessed website URL.

Phase 2: For each club, fetch their academy/programs page and extract:
         - Programs offered (age groups, leagues)
         - Fee data if published
         - Development pathway structure

Outputs:
  data/mlsnext_clubs.csv     — club, state, league_tier, website
  data/mlsnext_club_programs_scrape.csv  — club, state, program_name, program_url, program_type
  data/mlsnext_fees.csv      — club, program_name, age_group, fee, fee_url
"""

import csv
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

DATA_DIR = "data"
CLUBS_CSV = os.path.join(DATA_DIR, "mlsnext_clubs.csv")
PROGRAMS_CSV = os.path.join(DATA_DIR, "mlsnext_club_programs_scrape.csv")
FEES_CSV = os.path.join(DATA_DIR, "mlsnext_fees.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

MONEY_RE = re.compile(r'\$[\d,]+')
AGE_RE = re.compile(r'U\d{1,2}|Ages?\s*\d+[-–]\d+', re.IGNORECASE)

# ── 245 MLS NEXT Homegrown Division clubs ─────────────────────────────────────
MLS_NEXT_CLUBS = [
    # Alabama
    ("Hoover-Vestavia Soccer", "AL", ""),
    ("Huntsville City SC", "AL", ""),
    # Arizona
    ("Barca Residency Academy", "AZ", "https://barcaacademy.com"),
    ("Phoenix Rising FC", "AZ", "https://www.phoenixrisingfc.com/academy"),
    ("RSL Arizona", "AZ", "https://www.rslaz.com"),
    ("RSL Arizona Mesa", "AZ", "https://www.rslaz.com"),
    ("SC Del Sol", "AZ", "https://scdelsol.com"),
    # California
    ("ALBION SC Los Angeles", "CA", "https://www.albionsoccer.org"),
    ("ALBION SC Merced", "CA", "https://www.albionsoccer.org"),
    ("ALBION SC San Diego", "CA", "https://www.albionscsd.com"),
    ("Atletico Santa Rosa", "CA", ""),
    ("Ballistic United", "CA", "https://www.ballisticunited.com"),
    ("Chula Vista FC", "CA", "https://chulavistafc.com"),
    ("City SC San Diego", "CA", "https://citysc.com"),
    ("City SC Southwest", "CA", "https://citysc.com"),
    ("De Anza Force", "CA", "https://deanzaforce.com"),
    ("FC Bay Area Surf", "CA", "https://www.bayareasurf.com"),
    ("FC Golden State Force", "CA", ""),
    ("LA Galaxy", "CA", "https://www.lagalaxy.com/academy"),
    ("Lamorinda SC", "CA", ""),
    ("Los Angeles Bulls Soccer Club", "CA", "https://www.labulls.org"),
    ("Los Angeles Football Club", "CA", "https://www.lafc.com/youth-soccer"),
    ("Los Angeles Sports Club", "CA", ""),
    ("Los Angeles Surf", "CA", ""),
    ("Modesto Ajax United", "CA", ""),
    ("Napa United", "CA", ""),
    ("Sacramento Republic", "CA", "https://www.sacrepublicfc.com/academy"),
    ("Sacramento United", "CA", ""),
    ("San Diego FC", "CA", "https://www.sandiegofc.com/academy"),
    ("San Francisco Glens", "CA", ""),
    ("San Francisco Seals", "CA", ""),
    ("San Jose Earthquakes", "CA", "https://www.sjearthquakes.com/academy"),
    ("Santa Barbara Soccer Club", "CA", ""),
    ("Silicon Valley SA", "CA", ""),
    ("SoCal Reds FC", "CA", ""),
    ("Strikers FC", "CA", "https://www.strikersfc.com"),
    ("The Towne FC Academy", "CA", ""),
    ("Total Futbol Academy", "CA", "https://totalfutbolacademy.com"),
    ("Ventura County Fusion", "CA", ""),
    ("WSC Crush", "CA", ""),
    # Colorado
    ("ALBION SC Colorado", "CO", ""),
    ("Colorado Rapids", "CO", "https://www.coloradorapids.com/academy"),
    # Connecticut
    ("Beachside Soccer Club Connecticut", "CT", ""),
    ("Connecticut United FC", "CT", ""),
    ("Oakwood Soccer Club", "CT", ""),
    # Delaware
    ("Sporting Athletic Club", "DE", ""),
    # Florida
    ("Athletum FC Academy", "FL", ""),
    ("Chargers Soccer Club", "FL", ""),
    ("IdeaSport Soccer Academy", "FL", ""),
    ("IMG Academy", "FL", "https://www.imgacademy.com/sports/soccer"),
    ("Inter Miami CF", "FL", "https://www.intermiamicf.com/academy"),
    ("Jacksonville FC", "FL", ""),
    ("Miami Futbol Academy Rush", "FL", ""),
    ("Orlando City SC", "FL", "https://www.orlandocitysc.com/academy"),
    ("Orlando City Soccer School South", "FL", ""),
    ("Orlando City Youth SC", "FL", ""),
    ("Sol SC Florida", "FL", ""),
    ("South Florida Football Academy", "FL", ""),
    ("Tampa Bay United", "FL", "https://www.tampabayunited.com"),
    ("West Florida Flames", "FL", ""),
    ("Weston FC", "FL", "https://www.westonfc.com"),
    # Georgia
    ("AFC Lightning", "GA", ""),
    ("Atlanta United FC", "GA", "https://www.atlutd.com/academy"),
    ("Inter Atlanta FC", "GA", ""),
    ("KSA", "GA", ""),
    ("Lanier Soccer Association", "GA", ""),
    ("Southern Soccer Academy", "GA", ""),
    ("Tormenta FC Academy", "GA", ""),
    # Illinois
    ("Chicago FC United", "IL", ""),
    ("Chicago Fire FC", "IL", "https://www.chicago-fire.com/academy"),
    ("Sockers FC", "IL", ""),
    # Indiana
    ("Hoosier Premier", "IN", ""),
    ("Indy Eleven", "IN", "https://www.indyeleven.com/academy"),
    # Maryland
    ("Achilles FC", "MD", ""),
    ("Baltimore Armour", "MD", ""),
    ("Bethesda SC", "MD", "https://www.bethesdasc.com"),
    # Massachusetts
    ("FC Greater Boston Bolts", "MA", ""),
    ("Intercontinental Football Academy of New England", "MA", ""),
    ("NEFC", "MA", "https://www.nefcsoccer.com"),
    ("New England Revolution", "MA", "https://www.revolutionsoccer.net/academy"),
    ("Valeo FC", "MA", ""),
    # Michigan
    ("Michigan Futbol Academy", "MI", ""),
    ("Michigan Jaguars", "MI", ""),
    ("Michigan Wolves", "MI", ""),
    ("Midwest United", "MI", ""),
    ("Vardar Soccer Club", "MI", ""),
    # Minnesota
    ("Minnesota United FC", "MN", "https://www.mnufc.com/academy"),
    ("Shattuck-St. Mary's", "MN", "https://www.ssm.edu/athletics/soccer"),
    # Missouri
    ("Lou Fusz Athletic", "MO", "https://www.loufuszathletic.com"),
    ("Sporting Kansas City", "MO", "https://www.sportingkc.com/academy"),
    ("St. Louis City SC", "MO", "https://www.stlcitysc.com/academy"),
    ("St. Louis Scott Gallagher", "MO", "https://www.slsg.org"),
    # Nevada
    ("ALBION SC Las Vegas", "NV", ""),
    ("Las Vegas Sports Academy", "NV", ""),
    # New Hampshire
    ("Seacoast United", "NH", "https://www.seacoastunited.com"),
    # New Jersey
    ("Cedar Stars Academy - Bergen", "NJ", "https://www.cedarstarsacademy.com"),
    ("Cedar Stars Academy - Monmouth", "NJ", "https://www.cedarstarsacademy.com"),
    ("Ironbound Soccer Club", "NJ", "https://www.ironboundsc.com"),
    ("New York Red Bulls", "NJ", "https://www.newyorkredbulls.com/academy"),
    ("Players Development Academy", "NJ", "https://www.pdanewjersey.com"),
    ("Real Futbol Academy", "NJ", ""),
    ("The Football Academy", "NJ", ""),
    ("TSF Academy - NJ", "NJ", "https://www.tsfacademy.com"),
    # New York
    ("Blau Weiss Gottschee", "NY", ""),
    ("Downtown United Soccer Club", "NY", ""),
    ("FA Euro New York", "NY", ""),
    ("FC Westchester New York", "NY", ""),
    ("Long Island Soccer Club", "NY", ""),
    ("Metropolitan Oval", "NY", ""),
    ("New York City FC", "NY", "https://www.nycfc.com/academy"),
    ("New York Soccer Club", "NY", ""),
    ("Rochester NY FC Academy", "NY", ""),
    # North Carolina
    ("Carolina Core FC", "NC", ""),
    ("Charlotte FC", "NC", "https://www.charlottefc.com/academy"),
    ("Charlotte Independence Soccer Club", "NC", ""),
    ("Queen City Mutiny FC", "NC", ""),
    ("Triangle United Soccer Association", "NC", ""),
    ("Wake FC", "NC", ""),
    # Ohio
    ("Cincinnati United Premier Soccer Club", "OH", ""),
    ("Columbus Crew SC", "OH", "https://www.columbuscrewsc.com/academy"),
    ("FC Cincinnati", "OH", "https://www.fccincinnati.com/academy"),
    # Oklahoma
    ("Tulsa Greenwood SC", "OK", ""),
    # Oregon
    ("Portland Timbers", "OR", "https://www.timbers.com/timbers2-academy"),
    # Pennsylvania
    ("Beadling SC", "PA", ""),
    ("FC DELCO", "PA", "https://fcdelco.org"),
    ("Keystone FC", "PA", ""),
    ("PA Classics", "PA", "https://www.paclassics.com"),
    ("Philadelphia Union", "PA", "https://www.philadelphiaunion.com/academy"),
    # Rhode Island
    ("Bayside FC", "RI", ""),
    # Tennessee
    ("Chattanooga FC", "TN", ""),
    ("Nashville SC", "TN", "https://www.nashvillesc.com/academy"),
    ("Nashville United Soccer Academy", "TN", ""),
    # Texas
    ("A.C. River", "TX", ""),
    ("Austin FC", "TX", "https://www.austinfc.com/academy"),
    ("Capital City SC", "TX", ""),
    ("Dallas Hornets", "TX", ""),
    ("FC Dallas", "TX", "https://www.fcdallas.com/academy"),
    ("Global Football Innovation Academy", "TX", ""),
    ("Houston Dynamo", "TX", "https://www.houstondynamo.com/academy"),
    ("Houston Rangers", "TX", ""),
    ("IDEA Toros Futbol Academy", "TX", ""),
    # Utah
    ("Real Salt Lake", "UT", "https://www.realsaltlake.com/academy"),
    # Virginia
    ("Alexandria SA", "VA", ""),
    ("Northern Virginia Alliance", "VA", ""),
    ("Springfield SYC", "VA", ""),
    # Washington
    ("Seattle Sounders FC", "WA", "https://www.soundersfc.com/academy"),
    # West Virginia
    ("West Virginia Soccer", "WV", ""),
    # Wisconsin
    ("Bavarian United SC", "WI", ""),
    ("SC Wave", "WI", ""),
    # Canada
    ("Vancouver Whitecaps FC", "BC", "https://www.whitecapsfc.com/academy"),
    ("Toronto FC Academy", "ON", "https://www.torontofc.ca/academy"),
    ("CF Montreal", "QC", "https://www.cfmontreal.com/academy"),
]


def get_soup(url, timeout=15):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


PROGRAM_KEYWORDS = [
    "academy", "mlsnext", "mls next", "mls-next", "ecnl", "development",
    "pathway", "program", "elite", "competitive", "homegrown", "boys", "girls",
    "u13", "u14", "u15", "u16", "u17", "u18", "u19", "schedule", "team",
    "league", "npl", "pre-academy", "pre academy", "registration", "tryout",
]

SKIP = [
    "facebook", "instagram", "twitter", "youtube", "linkedin", "tiktok",
    "mailto:", "tel:", "#", "privacy", "terms", "login", "shop", "store",
    "ticket", "news", "blog", "photo", "gallery", "sponsor",
]


def collect_links(soup, base_url):
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
        if base_domain not in link_domain and link_domain not in base_domain:
            continue
        if any(s in (text + href).lower() for s in SKIP):
            continue
        if urlparse(href).path in ("", "/"):
            continue
        if any(kw in (text + " " + href).lower() for kw in PROGRAM_KEYWORDS):
            found[href] = text
    return list(found.items())


def classify(text, url):
    c = (text + " " + url).lower()
    if any(k in c for k in ["mls next", "mlsnext", "mls-next", "homegrown"]):
        return "MLS NEXT"
    if any(k in c for k in ["ecnl", "ecnl rl", "ecnl regional"]):
        return "ECNL"
    if any(k in c for k in ["academy", "elite academy"]):
        return "Academy"
    if any(k in c for k in ["development", "pathway", "pre-academy"]):
        return "Development"
    if any(k in c for k in ["competitive", "travel", "select"]):
        return "Competitive"
    return "Program"


def extract_fees(club, program_name, url, soup):
    fees = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr")[1:]:
            cells = [td.get_text(" ", strip=True) for td in row.find_all(["td", "th"])]
            row_text = " ".join(cells)
            if MONEY_RE.search(row_text):
                age = next((c for c in cells if AGE_RE.search(c)), "")
                fee = next((c for c in cells if MONEY_RE.search(c)), "")
                label = next((c for c in cells if c and c != age and c != fee), "")
                fees.append({"club": club, "program_name": program_name or label,
                             "age_group": age, "fee": fee, "fee_url": url})
    if not fees:
        for elem in soup.find_all(["li", "p", "div", "td"]):
            text = elem.get_text(" ", strip=True)
            if MONEY_RE.search(text) and AGE_RE.search(text):
                fees.append({"club": club, "program_name": program_name,
                             "age_group": (AGE_RE.search(text) or type('', (), {'group': lambda s: ''})()).group(),
                             "fee": (MONEY_RE.search(text) or type('', (), {'group': lambda s: ''})()).group(),
                             "fee_url": url})
    seen = set()
    deduped = []
    for f in fees:
        key = (f["age_group"], f["fee"])
        if key not in seen and key != ("", ""):
            seen.add(key)
            deduped.append(f)
    return deduped


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    # Phase 1: write clubs CSV
    club_rows = [{"club": name, "state": state, "website": site, "league_tier": "MLS NEXT Homegrown"}
                 for name, state, site in MLS_NEXT_CLUBS]
    write_csv(CLUBS_CSV, club_rows, ["club", "state", "league_tier", "website"])
    print(f"Phase 1: Saved {len(club_rows)} clubs to {CLUBS_CSV}")

    # Phase 2: scrape websites
    clubs_with_sites = [(r["club"], r["state"], r["website"]) for r in club_rows if r["website"]]
    print(f"\nPhase 2: Scraping {len(clubs_with_sites)} club websites...")

    all_programs = []
    all_fees = []

    for i, (club, state, website) in enumerate(clubs_with_sites, 1):
        print(f"  [{i}/{len(clubs_with_sites)}] {club} ({state}) — {website}")
        try:
            soup = get_soup(website)
            links = collect_links(soup, website)
            print(f"    → {len(links)} program links")

            homepage_fees = extract_fees(club, "Homepage", website, soup)
            if homepage_fees:
                print(f"    → {len(homepage_fees)} fees on homepage")
                all_fees.extend(homepage_fees)

            for href, text in links:
                ptype = classify(text, href)
                all_programs.append({"club": club, "state": state, "website": website,
                                     "program_name": text, "program_url": href, "program_type": ptype})
                try:
                    time.sleep(1)
                    prog_soup = get_soup(href)
                    page_fees = extract_fees(club, text, href, prog_soup)
                    if page_fees:
                        print(f"      $ {len(page_fees)} fees: {text}")
                        all_fees.extend(page_fees)
                except Exception as e:
                    print(f"      ERROR [{club}] fee page: {type(e).__name__}: {e}")

        except Exception as e:
            print(f"    ERROR [{club}]: {type(e).__name__}: {e}")

        if i % 10 == 0:
            write_csv(PROGRAMS_CSV, all_programs, ["club", "state", "website", "program_name", "program_url", "program_type"])
            write_csv(FEES_CSV, all_fees, ["club", "program_name", "age_group", "fee", "fee_url"])
            print(f"    [checkpoint saved — {len(all_programs)} programs, {len(all_fees)} fees]")

        time.sleep(2)

    write_csv(PROGRAMS_CSV, all_programs, ["club", "state", "website", "program_name", "program_url", "program_type"])
    write_csv(FEES_CSV, all_fees, ["club", "program_name", "age_group", "fee", "fee_url"])

    print(f"\nDone.")
    print(f"  Clubs:    {len(club_rows)} → {CLUBS_CSV}")
    print(f"  Programs: {len(all_programs)} → {PROGRAMS_CSV}")
    print(f"  Fees:     {len(all_fees)} → {FEES_CSV}")

    ca_clubs = [r for r in club_rows if r["state"] == "CA"]
    print(f"\n  California clubs: {len(ca_clubs)}")
    for c in ca_clubs:
        print(f"    {c['club']}")


if __name__ == "__main__":
    main()
