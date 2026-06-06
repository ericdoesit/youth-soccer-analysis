# ECNL Boys Club Database — Public Dataset

Free, open-source data on all **154 ECNL Boys** member clubs for the 2025-26 season.
No paywall, no signup required. Use it, share it, build on it.

## Files

| File | Rows | Description |
|------|------|-------------|
| `ecnl_boys_clubs.csv` | 154 | Club directory: name, state, conference, website |
| `ecnl_boys_fees.csv` | growing | Annual tuition data scraped from club websites |

## Column Definitions

### ecnl_boys_clubs.csv

| Column | Description |
|--------|-------------|
| `club_id` | TGS/AthleteOne internal ID (stable across seasons) |
| `club_name` | Official club name as shown in ECNL standings |
| `region` | West / Central / East (derived from conference) |
| `state` | US state abbreviation (primary location) |
| `conferences` | ECNL conference(s); multi-value separated by ` \| ` |
| `age_groups` | Birth years with active ECNL teams |
| `website` | Club's primary website |

### ecnl_boys_fees.csv

| Column | Description |
|--------|-------------|
| `club_id` | Matches `ecnl_boys_clubs.csv` |
| `tuition_low` | Lowest annual club fee found (USD, registration/tuition only) |
| `tuition_high` | Highest annual fee found (some clubs charge more for older groups) |
| `fee_page_url` | Source page where the fee was scraped |
| `context` | Surrounding text snippet for manual verification |

**Important:** `tuition_low/high` is the **club registration fee only**. Total annual cost
(including travel, hotels, uniforms, ID camps) is typically **2–4× higher**. See cost methodology below.

## Cost Context

Based on aggregated research (2024-25 data):

| Component | Typical Range |
|-----------|---------------|
| Club registration/tuition | $2,200–$4,500/year |
| Uniforms + gear | $400–$600 |
| Tournament entry fees | $400–$1,200/year |
| Regional travel (hotels, flights) | $1,500–$4,000/year |
| National showcase travel | $1,500–$3,500/year |
| College ID camps (U16+) | $0–$2,000/year |
| **Total all-in (U13-U15)** | **$6,400–$12,000/year** |
| **Total all-in (U16-U19)** | **$8,700–$15,000/year** |

Source: ECNL / TopDrawerSoccer / Soccer America survey data 2024.

## Conference Map

| Conference | States Covered |
|------------|---------------|
| Far West | AZ, CA, ID, NV, OR |
| Florida | FL |
| Heartland | IA, IL, KS, KY, MO, NE, OH |
| Mid-America | AL, AR, LA, MO, MS, TN |
| Mid-Atlantic | DC, DE, MD, NC, NJ, PA, VA |
| Midwest | IL, IN, MI, MN, MO, WI |
| Mountain | AZ, CO, MT, NM, UT, WY |
| New England | CT, MA, ME, NH, NY, RI, VT |
| North Atlantic | CT, DE, NJ, NY, PA |
| Northern Cal | CA (Bay Area / Central Valley) |
| Northwest | ID, OR, WA |
| Ohio Valley | IN, KY, OH, WV |
| Southeast | AL, FL, GA, NC, SC, TN |
| Southwest | AZ, CA (Southern), NV |
| Texas | OK, TX |

## Data Sources

- **Club list**: Scraped from ECNL standings API (`api.athleteone.com`) — all 15 conferences × 6 age groups, deduplicated
- **Websites**: Combination of manual research and web searches (June 2026)
- **State**: Derived from conference membership + club name; manually verified for ambiguous cases
- **Fees**: Scraped from club websites; many clubs do not publish fees publicly

## Methodology

The club list was built by querying the AthleteOne API that powers `theecnl.com`:

```
GET https://api.athleteone.com/api/Script/get-conference-standings
    /{eventId}/{orgId=12}/{orgSeasonId=70}/{divisionId}/{standingType}
```

- `orgId=12` = ECNL Boys
- `orgSeasonId=70` = 2025-26 season
- 15 conferences × 6 age groups (B2008–B2013) = 90 API calls
- Champions League view + per-conference view to capture all clubs (not just CL qualifiers)

See `scripts/scrape_ecnl_clubs.py` for the full implementation.

## How to Contribute

Found a club website that's wrong? Have fee data to add?

1. Open an issue with the correction
2. Submit a PR editing `ecnl_boys_clubs.csv` or `ecnl_boys_fees.csv`

The fee CSV especially needs community contributions — most clubs don't publish fees publicly
and the data needs to be collected one club at a time.

## License

**CC0 1.0 Universal** — no rights reserved.  
Use freely for any purpose, commercial or otherwise. Attribution appreciated but not required.

## Related Research

This dataset was built as part of a broader analysis of the economics of US youth soccer.
See the full research report for analysis of:
- Annual cost burden by tier (AYSO through MLS Academy)
- Scholarship probability and ROI analysis
- Equity and access issues
- Professional pathway success rates

---
*Data current as of June 2026. ECNL 2025-26 season.*
