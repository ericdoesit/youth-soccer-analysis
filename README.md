# Pitfalls on the Pathway — The Real Math Behind Club Soccer

US youth soccer cost-benefit analysis. Live site: https://ericdoesit.github.io/youth-soccer-analysis/

## Project Goal
Comprehensive, data-driven analysis of US youth soccer (Southern California lens, national context) covering:
- **Cost stratification** across program tiers (Rec, Travel, Elite)
- **Academic scholarship pathways** and outcomes
- **Professional soccer career probabilities** (domestic and global)
- **ROI calculations** showing cost vs. tangible benefits

## Key Findings (TL;DR)

### The Funnel
- 4M youth soccer players in US
- 730k high school players (18% retention)
- 60k college players (1.5%)
- 850 MLS roster spots (0.02%)
- 70 USMNT players (0.0018%)

### Cost by Pathway (13 years, ages 6-18)
| Pathway | Cost | Expected Return | ROI |
|---------|------|-----------------|-----|
| Recreational only | $7,150 | N/A | Joy, health |
| Rec → Travel | $30,100 | $45k (college) | 1.5x GAIN |
| Rec → Travel → Elite | $54,600 | $2.5k (avg) | 0.045x LOSS |
| Elite only (U13-U19) | $56,000 | $2.5k (avg) | 0.045x LOSS |

### Expected Value: $48,000 Elite Investment
- **85%** get $0 (no college, no pro)
- **13%** get $50k-280k (college aid)
- **0.4%** get $600k+ (professional)
- **Expected value: $19,300** (0.4x ROI = NEGATIVE)

### The Only Winner
**Competitive Travel Tier** ($18,600 cost)
- 15-20% realistic D2/D3 scholarship
- Expected value: $45,000+ (2.4x ROI = POSITIVE)
- Lower barrier to entry
- Better work-life balance

## The Biggest Losers

1. **Lower-income families** (<$50k household)
   - Cost: $0 (excluded)
   - Return: $0
   - Ratio: ∞:1 LOSS
   - Reason: Cannot afford $2k+/year; talent excluded by price

2. **Regional market elites** (KC, Austin, Nashville)
   - Cost: $56,000
   - Return: $1,000
   - Ratio: 56:1 LOSS
   - Reason: Elite locally, invisible nationally; weak academy markets

3. **Flight 2/3 at large clubs**
   - Cost: $56,000
   - Return: $2,000
   - Ratio: 28:1 LOSS
   - Reason: Same price as Flight 1, but worse coaching/exposure/playing time

4. **Average elite players**
   - Cost: $56,000
   - Return: $2,500
   - Ratio: 22:1 LOSS
   - Reason: 85% get zero tangible return

## Real Data Sources

### Professional
- **MLSPA 2026 Salary Guide**: 916 players, 31 clubs
  - Minimum: $88,025
  - Median: $325,000
  - Mean: $604,606
  - Maximum: $25,000,000 (Messi)
  - Total payroll: $553.8M

### College
- **NCAA 2025-26**: 1,852 soccer programs
  - D1 Men: 206 programs, 6,901 athletes
  - D1 Women: 341 programs, 10,931 athletes
  - D2: 479 programs, 16,872 athletes
  - D3: 830 programs, 25,242 athletes

### Youth Programs
- **MLS NEXT**: 53,000 players, 267 clubs, 6 age groups (U13-U19)
- **ECNL**: 600+ clubs (girls)
- **AYSO**: 600,000+ players (recreational)
- **USYS**: 3,000,000+ players (all levels)

### Research
- **202 research statistics** integrated from:
  - Peer-reviewed academic papers (8 sources with DOIs)
  - US Soccer official data
  - NCAA published reports
  - MLSPA salary disclosure
  - Community data (Reddit r/youth_soccer, 2024-25)
  - Fortune article on US Soccer AI scouting (June 2026)

## Files

### Scripts (survey pipeline)
The site itself is fully static (HTML/CSS/JS + D3); Python is only used for the
ongoing survey pipeline. Setup: `python3 -m venv venv && venv/bin/pip install -r requirements.txt`
```bash
python3 scripts/pull_survey_data.py      # pull legacy Typeform responses (needs .env token)
python3 scripts/typeform_to_sheet.py     # convert legacy rows for the Google Sheet master
python3 scripts/sheet_to_survey.py       # pull Tally responses from the Google Sheet
python3 scripts/merge_survey_data.py     # merge responses into data/survey_merged.csv
```
Scrapers and one-off dataset builders were removed June 2026 (data is final); see git history.

### Data
```
data/
├── *.csv            active datasets used by the report pages and scripts
│                    (clubs, leagues, fees, MLS salaries/drafts, survey, outcomes)
├── analysis/        generated charts and summary tables
├── raw/             raw source data
│   ├── professional/   MLSPA salary data + extracted salary-guide text (2015-2023)
│   ├── scholarships/   NCAA PDFs and participation data
│   └── programs/       club databases
├── pdf/             source PDFs (MLSPA salary guides, research reports)
└── archive/         superseded or unused datasets
```

### Docs
```
md/                  project docs (THESIS.md, VOICE.md, case-study notes)
```

## Key Insights

### 1. Geography Matters
- Philadelphia academy (ranked #1): 8x better MLS odds than KC
- But even elite academies: <1% MLS conversion
- Moving to coastal academy: +$20-40k additional cost

### 2. Pay-to-Play Creates Equity Gaps
- 40% of US households (<$50k) completely excluded
- Elite tier = 16% of household income for poor families
- Talent screened OUT by price before evaluation
- **Solution**: AI scouting (video-based, bypasses pay-to-play)

### 3. Academy Quality Varies Dramatically
- Top 3 academies (Philly, NE, Chicago) dominate
- Other 26 MLS academies produce far fewer pros
- Club ranking directly predicts player outcomes

### 4. Female Soccer Players Face Professional Earnings Gap
- Same elite tier cost ($52.5k) as boys
- But NWSL average: $35k/year vs MLS median: $325k/year
- Women's professional career earnings: 1/9 of men's
- **Better strategy for women**: Focus on college scholarship (more available)

### 5. New Fan Growth (For Soccer Context)
- 57% year-over-year growth in new soccer fans
- 93% of US youth national team players from MLS NEXT
- But only 70 reach USMNT overall (0.0018% of youth)
- Non-traditional entry paths (gaming, gambling): +22-32% for new arrivals

## Recommendations

### For Families (No Pro Aspirations)
1. **Ages 6-11**: Rec league ($550/year, ~$3,300 career)
   - Goal: Fall in love with sport
   - Build fundamentals, friendships
   
2. **Ages 11-15**: Competitive travel ($3,100/year, ~$15,500 career)
   - Goal: Compete at high level
   - Build college recruiting profile
   
3. **Ages 15+**: Select travel / local club
   - Goal: Get recruited
   - Land scholarship offer

**Total cost: ~$30k** (vs $56k for elite)
**Expected college outcome: 15-20%** (vs 1.5% from elite for D1)
**ROI: Positive** (expected value ~$45k)

### For Families (Pro Aspirations)
- Only invest in elite tier if child identified as top 1% talent by age 13-14
- Philadelphia/coastal academies only (ranked #1-3)
- Be realistic: 0.4% still reach MLS, even from elite academies
- Have college fallback plan (happens for 85%)

### For Policy
- **Fund AI scouting**: Video-based talent ID at scale
  - Reaches 50-70M US-eligible teenagers globally
  - Bypasses geographic and economic bias
  - Could disrupt current pay-to-play gatekeeping
  
- **Support school soccer**: Dual pathways (club + school)
  - School soccer free or low-cost
  - College coaches watch school games
  - Better retention rates
  
- **Regulate club pricing**: Tier-pricing transparency
  - Large clubs charge same fee for different products
  - Flight 2/3 subsidize Flight 1
  - Families should know actual value delivered

## Questions This Project Answers

✓ How much does youth soccer cost by tier?
✓ What's the realistic probability of scholarships?
✓ What's the realistic probability of professional soccer?
✓ What's the ROI on youth soccer investment?
✓ Which groups pay the most with the least return?
✓ How do geography and economics affect outcomes?
✓ How does the gender differ between boys and girls?
✓ What's the AI scouting disruption opportunity?

## Data Updates (June 2026)

- MLSPA 2026 salary data: Live as of April 14, 2026
- NCAA 2025-26 sponsorship data: Published June 2026
- MLS NEXT enrollment: 53,000 players (2026-27 season)
- MLS academy rankings: 2025 (Philadelphia #1)
- US Soccer AI scouting: Deployed June 2026 (Fortune)
- For Soccer fandom report: Q4 2023 data (2,040 respondents)

## Next Steps

1. Build interactive dashboard (Plotly)
2. Monte Carlo simulation for career uncertainty
3. Regional cost-benefit comparisons (by state)
4. NWSL/international pathway analysis
5. School soccer ROI comparison
6. AI scouting impact modeling

---

**Last Updated**: June 4, 2026
**Author**: Claude + user research
**Status**: Active analysis (data collected, analysis complete, visualization in progress)
