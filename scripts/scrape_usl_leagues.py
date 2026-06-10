#!/usr/bin/env python3
"""
Best-effort USL league team scraper.

What this script tries:
1. Standard browser-like HTTP requests with rotated User-Agent headers.
2. robots.txt / sitemap.xml discovery to find public team-page URLs.
3. Common REST/API patterns such as /api/* and /wp-json/*.
4. Optional JavaScript rendering via requests-html if it is installed.

Notes:
- The script intentionally stays within ordinary public fetch paths.
- If a site returns 403 or blocks requests, the script falls back gracefully.
- Output: data/usl_teams.csv with columns:
  league, team_name, city, state, website_url
"""

from __future__ import annotations

import csv
import json
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


try:
    from requests_html import HTMLSession  # type: ignore
except Exception:  # pragma: no cover
    HTMLSession = None


ROOT = Path("/Users/Eric/Documents/Claude/soccer")
DATA_DIR = ROOT / "data"
OUT_CSV = ROOT / "data" / "usl_teams.csv"

TARGETS = [
    {
        "league": "USL League Two",
        "base_url": "https://www.uslleaguetwo.com",
        "url": "https://www.uslleaguetwo.com/league-teams",
    },
    {
        "league": "USL Championship",
        "base_url": "https://www.uslchampionship.com",
        "url": "https://www.uslchampionship.com/league-teams",
    },
    {
        "league": "USL League One",
        "base_url": "https://www.uslleagueone.com",
        "url": "https://www.uslleagueone.com/league-teams",
    },
    {
        "league": "USL Academy",
        "base_url": "https://www.usl-academy.com",
        "url": "https://www.usl-academy.com/league-standings",
    },
    {
        "league": "USL W League",
        "base_url": "https://www.uslwleague.com",
        "url": "https://www.uslwleague.com/league-teams",
    },
]

TEAM_PAGE_PROBES = [
    {
        "league": "USL League Two",
        "base_url": "https://www.uslleaguetwo.com",
        "url": "https://www.uslleaguetwo.com/ac-connecticut",
    },
]

UA_STRINGS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) Gecko/20100101 Firefox/139.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
]

COMMON_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

RESERVED_PATHS = {
    "/about",
    "/contact",
    "/news",
    "/notices",
    "/transactions",
    "/features",
    "/spotlight",
    "/game-reports",
    "/rankings",
    "/privacy_policy",
    "/privacy-policy",
    "/assets",
    "/watch",
    "/league-teams",
    "/league-standings",
    "/league-announcements",
}

STATE_MAP = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "conn.": "CT",
    "ct": "CT",
    "delaware": "DE",
    "dela.": "DE",
    "de": "DE",
    "florida": "FL",
    "fla.": "FL",
    "fl": "FL",
    "georgia": "GA",
    "ga": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "ill.": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "mass.": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
}


@dataclass
class TeamRow:
    league: str
    team_name: str
    city: str
    state: str
    website_url: str

    def as_dict(self) -> dict[str, str]:
        return {
            "league": self.league,
            "team_name": self.team_name,
            "city": self.city,
            "state": self.state,
            "website_url": self.website_url,
        }


def build_session() -> Session:
    session = requests.Session()
    retry = Retry(
        total=1,
        connect=1,
        read=1,
        backoff_factor=0.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def browser_headers(base_url: str, referer: Optional[str] = None) -> list[dict[str, str]]:
    headers: list[dict[str, str]] = []
    for ua in UA_STRINGS:
        h = dict(COMMON_HEADERS)
        h["User-Agent"] = ua
        h["Accept-Encoding"] = "gzip, deflate, br"
        if referer:
            h["Referer"] = referer
            h["Sec-Fetch-Site"] = "same-origin"
        else:
            h["Sec-Fetch-Site"] = "none"
        headers.append(h)
    random.shuffle(headers)
    return headers


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text or "")).strip()


def looks_like_team_name(text: str) -> bool:
    text = normalize_whitespace(text)
    if not text or len(text) < 3:
        return False
    lowered = text.lower()
    if lowered in {
        "team website",
        "schedule",
        "news",
        "roster",
        "player stats",
        "team stats",
        "players",
        "goalkeepers",
        "home",
        "about",
        "standings",
        "latest news",
        "latest results",
        "next game",
        "page search",
        "search",
    }:
        return False
    if "division" in lowered or "conference" in lowered:
        return False
    if text.startswith("USL "):
        return False
    if len(text.split()) > 6:
        return False
    return True


def is_internal_team_path(href: str, base_url: str) -> bool:
    if not href:
        return False
    parsed = urlparse(urljoin(base_url, href))
    if parsed.netloc and parsed.netloc != urlparse(base_url).netloc:
        return False
    path = parsed.path.rstrip("/")
    if not path or path == "/":
        return False
    if any(path == r or path.startswith(f"{r}/") for r in RESERVED_PATHS):
        return False
    if path.startswith("/page/show/") or path.startswith("/page/"):
        return True
    # Single-segment slugs are typical for the club landing pages.
    parts = [p for p in path.split("/") if p]
    return len(parts) == 1


def is_external_url(href: str, base_url: str) -> bool:
    if not href:
        return False
    href = href.strip()
    if href.startswith("mailto:") or href.startswith("tel:"):
        return False
    parsed = urlparse(urljoin(base_url, href))
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc and parsed.netloc != urlparse(base_url).netloc)


def looks_like_team_page_url(url: str, base_url: str) -> bool:
    parsed = urlparse(urljoin(base_url, url))
    if parsed.netloc != urlparse(base_url).netloc:
        return False
    path = parsed.path.rstrip("/")
    if not path:
        return False
    if path.startswith("/page/show/"):
        return True
    if path.startswith("/page/nav/"):
        return False
    if any(path == r or path.startswith(f"{r}/") for r in RESERVED_PATHS):
        return False
    parts = [p for p in path.split("/") if p]
    # Single-segment club slugs are typical for SportsEngine club landing pages.
    if len(parts) == 1:
        return True
    # Some team pages on SportsEngine use short paths that include a numeric page id.
    if len(parts) == 2 and parts[0] in {"club", "team", "page"}:
        return True
    return False


def clean_team_website(url: str) -> str:
    url = normalize_whitespace(url)
    if not url:
        return ""
    if not re.match(r"^https?://", url):
        url = "http://" + url.lstrip("/")
    return url


def split_location(location_text: str) -> tuple[str, str]:
    """
    Split location text like:
    - "Newtown, CT"
    - "Newtown, Conn."
    - "Tampa, Florida"
    into city/state.
    """
    location_text = normalize_whitespace(location_text)
    if not location_text:
        return "", ""

    # Strip leading label.
    location_text = re.sub(r"^Location:\s*", "", location_text, flags=re.I)
    if "," not in location_text:
        return location_text, ""

    left, right = [part.strip(" .") for part in location_text.rsplit(",", 1)]
    city = normalize_whitespace(left)
    state_raw = normalize_whitespace(right).lower().strip(".")
    state = STATE_MAP.get(state_raw, "")
    if not state and len(state_raw) == 2:
        state = state_raw.upper()
    return city, state


def get_text_from_response(response: requests.Response) -> str:
    response.encoding = response.encoding or "utf-8"
    return response.text


def fetch_url(
    session: Session,
    url: str,
    *,
    referer: Optional[str] = None,
    allow_render: bool = True,
    timeout: int = 8,
) -> tuple[Optional[str], str, int]:
    """
    Try multiple fetch strategies.

    Returns: (html_or_text, method_name, status_code)
    """
    last_status = 0
    for headers in browser_headers(url, referer=referer):
        try:
            r = session.get(url, headers=headers, timeout=timeout)
            last_status = r.status_code
            body = get_text_from_response(r)
            if r.status_code == 200 and body:
                return body, "requests", r.status_code
            if r.status_code in {301, 302, 303, 307, 308} and "Location" in r.headers:
                loc = r.headers["Location"]
                return fetch_url(session, urljoin(url, loc), referer=referer, allow_render=allow_render, timeout=timeout)
        except Exception:
            continue

    if allow_render and HTMLSession is not None:
        try:
            html_session = HTMLSession()
            r = html_session.get(url, headers={"User-Agent": random.choice(UA_STRINGS), "Referer": referer or url})
            if hasattr(r, "html"):
                try:
                    r.html.render(timeout=25, sleep=1, keep_page=False)
                except Exception:
                    pass
                body = r.html.html or ""
                if body:
                    return body, "requests-html", getattr(r, "status_code", 0)
        except Exception:
            pass

    return None, "failed", last_status


def parse_canonical_url(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for selector in ("link[rel='canonical']", "meta[property='og:url']", "meta[name='twitter:url']"):
        tag = soup.select_one(selector)
        if not tag:
            continue
        if selector.startswith("meta"):
            candidate = tag.get("content", "").strip()
        else:
            candidate = tag.get("href", "").strip()
        if candidate:
            return urljoin(base_url, candidate)
    return ""


def parse_team_page(html: str, page_url: str, league: str) -> tuple[str, str, str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # Team name: prefer title / headings.
    candidates = []
    for selector in ("h1", "h2", "h3", "title", "meta[property='og:title']"):
        for tag in soup.select(selector):
            if selector.startswith("meta"):
                value = tag.get("content", "")
            else:
                value = tag.get_text(" ", strip=True)
            value = normalize_whitespace(value)
            if looks_like_team_name(value):
                candidates.append(value)
    team_name = candidates[0] if candidates else ""
    if not team_name:
        # Sometimes the first meaningful heading is the only visible team label.
        for heading in soup.find_all(["h1", "h2", "h3"]):
            value = normalize_whitespace(heading.get_text(" ", strip=True))
            if looks_like_team_name(value):
                team_name = value
                break

    text = normalize_whitespace(soup.get_text("\n", strip=True))

    # Location may be visible in plain text or within markup.
    location = ""
    m = re.search(r"(Location:\s*.+?)(?:\s{2,}|Website:|Tweets by|Latest News|$)", text, flags=re.I)
    if m:
        location = normalize_whitespace(m.group(1))
    else:
        m = re.search(r"Location:\s*([^\n]+)", text, flags=re.I)
        if m:
            location = normalize_whitespace(m.group(1))
    city, state = split_location(location)

    website_url = ""
    # Look for a visible Website field first.
    website_match = re.search(r"Website:\s*(https?://[^\s]+)", text, flags=re.I)
    if website_match:
        website_url = clean_team_website(website_match.group(1))
    else:
        # Then inspect anchors for the first off-site team website.
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            label = normalize_whitespace(a.get_text(" ", strip=True))
            if is_external_url(href, page_url):
                if label and label.lower() in {"read more", "login", "privacy policy", "sports relationship management", "sportsengine"}:
                    continue
                website_url = clean_team_website(urljoin(page_url, href))
                break

    # Some pages expose the city/state on the canonical page but not the slug page.
    if (not city or not state) and league and not page_url.endswith("/"):
        # No-op hook for future league-specific handling.
        pass

    return team_name, city, state, website_url


def discover_from_robots_and_sitemaps(session: Session, base_url: str) -> list[str]:
    discovered: list[str] = []
    seen = set()

    robots_url = urljoin(base_url, "/robots.txt")
    sitemap_urls: list[str] = []
    html, _, status = fetch_url(session, robots_url, referer=base_url, allow_render=False, timeout=6)
    if html and status == 200:
        for line in html.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_urls.append(line.split(":", 1)[1].strip())

    common_sitemaps = [
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemap-index.xml",
        "/sitemapindex.xml",
    ]
    for rel in common_sitemaps:
        sitemap_urls.append(urljoin(base_url, rel))

    def add_url(candidate: str) -> None:
        candidate = candidate.strip()
        if candidate and candidate not in seen:
            seen.add(candidate)
            discovered.append(candidate)

    for sitemap_url in sitemap_urls:
        body, _, status = fetch_url(session, sitemap_url, referer=base_url, allow_render=False, timeout=6)
        if not body or status >= 400:
            continue
        try:
            root = BeautifulSoup(body, "xml")
        except Exception:
            continue
        if root.find("sitemapindex"):
            for loc in root.find_all("loc"):
                nested = normalize_whitespace(loc.get_text())
                if nested:
                    body2, _, status2 = fetch_url(session, nested, referer=base_url, allow_render=False, timeout=6)
                    if not body2 or status2 >= 400:
                        continue
                    try:
                        nested_root = BeautifulSoup(body2, "xml")
                    except Exception:
                        continue
                    for loc2 in nested_root.find_all("loc"):
                        add_url(normalize_whitespace(loc2.get_text()))
        else:
            for loc in root.find_all("loc"):
                add_url(normalize_whitespace(loc.get_text()))

    return discovered


def discover_public_api(session: Session, base_url: str) -> list[str]:
    """
    Probe common REST patterns. This does not assume a specific vendor.
    Returns any URLs discovered in JSON payloads.
    """
    candidate_paths = [
        "/api",
        "/api/teams",
        "/api/team",
        "/api/v1/teams",
        "/api/v2/teams",
        "/wp-json/",
        "/wp-json/wp/v2/pages",
        "/wp-json/wp/v2/posts",
        "/wp-json/wp/v2/team",
        "/wp-json/wp/v2/teams",
        "/wp-json/wp/v2/club",
        "/wp-json/wp/v2/clubs",
    ]
    found: list[str] = []
    for rel in candidate_paths:
        url = urljoin(base_url, rel)
        body, _, status = fetch_url(session, url, referer=base_url, allow_render=False, timeout=6)
        if not body or status >= 400:
            continue
        parsed = None
        try:
            parsed = json.loads(body)
        except Exception:
            continue
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    for key in ("link", "url", "permalink", "canonical", "slug"):
                        value = item.get(key)
                        if isinstance(value, str) and value.startswith("http") and looks_like_team_page_url(value, base_url):
                            found.append(value)
        elif isinstance(parsed, dict):
            for key in ("link", "url", "permalink", "canonical"):
                value = parsed.get(key)
                if isinstance(value, str) and value.startswith("http") and looks_like_team_page_url(value, base_url):
                    found.append(value)
    return found


def can_reach_domain(session: Session, base_url: str) -> bool:
    """
    Quick preflight so we do not spend minutes retrying against a dead network path.
    """
    probe_urls = [
        base_url,
        urljoin(base_url, "/robots.txt"),
    ]
    for probe in probe_urls:
        body, _, status = fetch_url(session, probe, referer=base_url, allow_render=False, timeout=4)
        if body and status < 400:
            return True
    return False


def extract_team_links_from_league_page(html: str, base_url: str) -> list[tuple[str, str]]:
    """
    Extract team name + page URL from a league page.
    Works best against SportsEngine-style pages where team cards are rendered in HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str, str]] = []
    seen = set()

    # Pass 1: direct internal links with obvious team slugs.
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        name = normalize_whitespace(a.get_text(" ", strip=True))
        if is_internal_team_path(href, base_url) and looks_like_team_name(name):
            full = urljoin(base_url, href)
            key = (name, full)
            if key not in seen:
                seen.add(key)
                results.append(key)

    # Pass 2: headings that may wrap or sit near an external website link.
    for heading in soup.find_all(["h2", "h3", "h4"]):
        name = normalize_whitespace(heading.get_text(" ", strip=True))
        if not looks_like_team_name(name):
            continue
        parent = heading.find_parent(["article", "section", "div", "li"]) or heading.parent
        if not parent:
            continue
        page_url = ""
        for a in parent.find_all("a", href=True):
            href = a["href"].strip()
            if is_internal_team_path(href, base_url):
                page_url = urljoin(base_url, href)
                break
        if page_url and (name, page_url) not in seen:
            seen.add((name, page_url))
            results.append((name, page_url))

    # De-duplicate while keeping order.
    deduped: list[tuple[str, str]] = []
    seen_urls = set()
    for name, url in results:
        if url not in seen_urls:
            seen_urls.add(url)
            deduped.append((name, url))
    return deduped


def extract_team_links_from_standings(html: str, base_url: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str, str]] = []
    seen = set()

    # Standings pages often have tables; get team names from table rows.
    for a in soup.find_all("a", href=True):
        name = normalize_whitespace(a.get_text(" ", strip=True))
        href = a["href"].strip()
        if looks_like_team_name(name) and is_internal_team_path(href, base_url):
            full = urljoin(base_url, href)
            key = (name, full)
            if key not in seen:
                seen.add(key)
                results.append(key)

    for cell in soup.find_all(["td", "th"]):
        text = normalize_whitespace(cell.get_text(" ", strip=True))
        if looks_like_team_name(text):
            # Standings pages typically don't link every team; still keep names.
            key = (text, "")
            if key not in seen:
                seen.add(key)
                results.append(key)

    return results


def fetch_team_page_candidates(
    session: Session,
    league: str,
    base_url: str,
    page_url: str,
    html: str,
) -> list[TeamRow]:
    rows: list[TeamRow] = []
    canonical = parse_canonical_url(html, base_url)
    candidate_urls = [page_url]
    if canonical and canonical not in candidate_urls:
        candidate_urls.insert(0, canonical)

    # Try the page that we already have, plus any canonical page.
    for candidate in candidate_urls:
        body = html if candidate == page_url else None
        method = "cached"
        status = 200
        if body is None:
            body, method, status = fetch_url(session, candidate, referer=page_url, allow_render=True, timeout=20)
        if not body or status >= 400:
            continue
        team_name, city, state, website_url = parse_team_page(body, candidate, league)
        if team_name or website_url or city or state:
            rows.append(TeamRow(league, team_name, city, state, website_url))

        # If the page was a slim slug page, also try to chase the canonical page.
        if canonical and candidate == page_url and canonical != page_url:
            body2, _, status2 = fetch_url(session, canonical, referer=page_url, allow_render=True, timeout=20)
            if body2 and status2 < 400:
                team_name2, city2, state2, website_url2 = parse_team_page(body2, canonical, league)
                if team_name2 or website_url2 or city2 or state2:
                    rows.append(TeamRow(league, team_name2, city2, state2, website_url2))

    # Deduplicate rows within a team page.
    deduped: list[TeamRow] = []
    seen = set()
    for row in rows:
        key = (row.league, row.team_name, row.city, row.state, row.website_url)
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def scrape_league(session: Session, league: str, base_url: str, url: str) -> list[TeamRow]:
    print(f"\n=== {league} ===")
    rows: list[TeamRow] = []

    if not can_reach_domain(session, base_url):
        print("  domain preflight failed; skipping live scrape for this league")
        return rows

    html, method, status = fetch_url(session, url, referer=base_url, allow_render=True, timeout=8)
    if not html or status >= 400:
        print(f"  primary fetch failed: status={status}, method={method}")
    else:
        print(f"  fetched league page via {method} (status {status})")

    discovered_urls = []
    if html:
        if "academy" in base_url:
            team_links = extract_team_links_from_standings(html, base_url)
        else:
            team_links = extract_team_links_from_league_page(html, base_url)
        discovered_urls.extend([u for _, u in team_links if u])
        print(f"  found {len(team_links)} team-name candidates on the league page")

    # Also gather URLs from robots/sitemaps and public API patterns.
    sitemap_urls = discover_from_robots_and_sitemaps(session, base_url)
    api_urls = discover_public_api(session, base_url)
    for candidate in sitemap_urls + api_urls:
        if candidate and looks_like_team_page_url(candidate, base_url):
            discovered_urls.append(candidate)

    # Maintain order, de-duplicate.
    team_url_order: list[str] = []
    seen_urls = set()
    for candidate in discovered_urls:
        candidate = candidate.split("#", 1)[0]
        if candidate and candidate not in seen_urls:
            seen_urls.add(candidate)
            team_url_order.append(candidate)

    print(f"  total candidate URLs after discovery: {len(team_url_order)}")

    # If the league page yielded actual team cards, scrape those first.
    if html and not "academy" in base_url:
        pairs = extract_team_links_from_league_page(html, base_url)
        team_url_order = []
        for _, candidate in pairs:
            if candidate not in seen_urls:
                seen_urls.add(candidate)
                team_url_order.append(candidate)
        # Append any sitemap/API URLs afterward.
        for candidate in sitemap_urls + api_urls:
            if candidate and looks_like_team_page_url(candidate, base_url) and candidate not in seen_urls:
                seen_urls.add(candidate)
                team_url_order.append(candidate)

    # For Academy standings pages, names may not be linked. Keep team names with blank URLs.
    if html and "academy" in base_url:
        standings_pairs = extract_team_links_from_standings(html, base_url)
        if standings_pairs:
            for name, candidate in standings_pairs:
                if candidate and candidate not in seen_urls:
                    seen_urls.add(candidate)
                    team_url_order.append(candidate)

    # Scrape team pages.
    for idx, team_url in enumerate(team_url_order, 1):
        if not team_url:
            continue
        body, method, status = fetch_url(session, team_url, referer=url, allow_render=True, timeout=8)
        if not body or status >= 400:
            continue
        team_rows = fetch_team_page_candidates(session, league, base_url, team_url, body)
        if not team_rows:
            # If the page is a bare slug, still try to parse it directly.
            team_name, city, state, website_url = parse_team_page(body, team_url, league)
            if team_name or website_url or city or state:
                team_rows = [TeamRow(league, team_name, city, state, website_url)]

        for row in team_rows:
            rows.append(row)

        if idx % 10 == 0:
            print(f"  scraped {idx}/{len(team_url_order)} candidate pages")
        time.sleep(0.35)

    # As a fallback, if no team pages were reachable, preserve any names from the league page.
    if not rows and html:
        if "academy" in base_url:
            pairs = extract_team_links_from_standings(html, base_url)
            for name, _ in pairs:
                if name:
                    rows.append(TeamRow(league, name, "", "", ""))
        else:
            pairs = extract_team_links_from_league_page(html, base_url)
            for name, candidate in pairs:
                rows.append(TeamRow(league, name, "", "", candidate))

    # De-duplicate rows.
    deduped: list[TeamRow] = []
    seen = set()
    for row in rows:
        # Prefer rows with more complete information.
        key = (row.league, row.team_name.lower(), row.website_url.lower())
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    print(f"  extracted {len(deduped)} rows")
    return deduped


def write_csv(rows: Iterable[TeamRow]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["league", "team_name", "city", "state", "website_url"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())


def print_summary(rows: list[TeamRow]) -> None:
    counts = Counter(row.league for row in rows)
    print("\n=== Summary ===")
    for league, count in counts.items():
        print(f"{league}: {count}")
    print(f"Total rows: {len(rows)}")
    print(f"CSV written to: {OUT_CSV}")


def main() -> int:
    session = build_session()
    all_rows: list[TeamRow] = []

    for target in TARGETS:
        league = target["league"]
        base_url = target["base_url"]
        url = target["url"]
        try:
            league_rows = scrape_league(session, league, base_url, url)
            all_rows.extend(league_rows)
        except Exception as exc:
            print(f"  ERROR scraping {league}: {type(exc).__name__}: {exc}")

    # Explicit probe for the sample team page that was called out in the task.
    for probe in TEAM_PAGE_PROBES:
        league = probe["league"]
        base_url = probe["base_url"]
        url = probe["url"]
        print(f"\n=== Probe: {url} ===")
        body, method, status = fetch_url(session, url, referer=base_url, allow_render=True, timeout=8)
        if body and status < 400:
            team_name, city, state, website_url = parse_team_page(body, url, league)
            if team_name or city or state or website_url:
                all_rows.append(TeamRow(league, team_name, city, state, website_url))
                print(f"  parsed via {method} (status {status})")
        else:
            print(f"  probe failed: status={status}, method={method}")

    # Clean rows and de-duplicate on content.
    final_rows: list[TeamRow] = []
    seen = set()
    for row in all_rows:
        cleaned = TeamRow(
            league=normalize_whitespace(row.league),
            team_name=normalize_whitespace(row.team_name),
            city=normalize_whitespace(row.city),
            state=normalize_whitespace(row.state).upper(),
            website_url=normalize_whitespace(row.website_url),
        )
        key = (cleaned.league, cleaned.team_name.lower(), cleaned.city.lower(), cleaned.state.lower(), cleaned.website_url.lower())
        if key not in seen:
            seen.add(key)
            final_rows.append(cleaned)

    write_csv(final_rows)
    print_summary(final_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
