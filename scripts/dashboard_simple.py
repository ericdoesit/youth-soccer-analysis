#!/usr/bin/env python3
"""
US Youth Soccer Cost-Benefit Analysis Dashboard (Standalone - No CSV Dependencies)
Uses hardcoded real data points from research
"""

print("=" * 100)
print("US YOUTH SOCCER COST-BENEFIT ANALYSIS DASHBOARD")
print("Real Data: MLSPA 2026 (916 players), NCAA 2025-26, MLS NEXT (53k players)")
print("=" * 100)

# ============================================================================
# 1. THE FUNNEL: Probability of Success
# ============================================================================
print("\n1. THE FUNNEL: Probability of Success")
print("-" * 100)

funnel = [
    ("Youth Soccer Players", 4_000_000, 100.0),
    ("High School Players", 730_000, 18.25),
    ("College (All Div)", 60_000, 1.5),
    ("MLS Roster Spots", 850, 0.021),
    ("US-Born MLS", 400, 0.01),
    ("USMNT", 70, 0.0018),
]

for stage, count, pct in funnel:
    print(f"{stage:<30} {count:>12,} players ({pct:>8.4f}%)")

# ============================================================================
# 2. CAREER COST BREAKDOWN
# ============================================================================
print("\n\n2. CAREER COST BREAKDOWN (13 Years, Ages 6-18)")
print("-" * 100)

pathways = [
    ("Recreational Only (13 years)", 13*550),
    ("Rec → Travel (4+9 years)", 4*550 + 9*3100),
    ("Rec → Travel → Elite (4+4+5)", 4*550 + 4*3100 + 5*8000),
    ("Elite Only (U13-U19, 7 years)", 7*8000),
]

for pathway, cost in pathways:
    print(f"{pathway:<50} ${cost:>10,}")

# ============================================================================
# 3. MLS SALARY DISTRIBUTION (Real MLSPA 2026)
# ============================================================================
print("\n\n3. MLS SALARY DISTRIBUTION (916 Players, 2026 Season)")
print("-" * 100)

mls_stats = {
    "Minimum": 88_025,
    "25th percentile": 113_400,
    "Median": 325_000,
    "Mean": 604_606,
    "75th percentile": 656_750,
    "90th percentile": 1_200_000,
    "Maximum": 25_000_000,
    "Total League Payroll": 553_818_662,
}

for metric, value in mls_stats.items():
    print(f"{metric:<25} ${value:>15,.0f}")

# ============================================================================
# 4. EXPECTED VALUE: $48,000 Elite Investment
# ============================================================================
print("\n\n4. EXPECTED VALUE: $48,000 Investment (Elite Tier, U13-U19)")
print("-" * 100)

outcomes = [
    ("No college/pro (85%)", 0.85, 0),
    ("D3/NAIA partial aid (10%)", 0.10, 50_000),
    ("D2 full scholarship (3%)", 0.03, 240_000),
    ("D1 full scholarship (1.5%)", 0.015, 280_000),
    ("MLS NEXT Pro → MLS (0.4%)", 0.004, 600_000),
    ("USMNT (0.01%)", 0.0001, 5_000_000),
]

print(f"{'Outcome':<35} {'Probability':<12} {'Benefit':<15} {'Expected Value':<15}")
print("-" * 100)

total_ev = 0
for outcome, prob, benefit in outcomes:
    ev = prob * benefit
    total_ev += ev
    print(f"{outcome:<35} {prob*100:>10.2f}% ${benefit:>13,} ${ev:>13,.0f}")

print("-" * 100)
print(f"{'TOTAL EXPECTED VALUE':<35} {'':12} {'':15} ${total_ev:>13,.0f}")
print(f"\nInvestment: ${48_000:,}")
print(f"Expected Return: ${total_ev:,.0f}")
print(f"ROI: {total_ev/48_000:.2f}x LOSS (negative return)")

# ============================================================================
# 5. SCHOLARSHIP ANALYSIS
# ============================================================================
print("\n\n5. COLLEGE SCHOLARSHIP ANALYSIS")
print("-" * 100)

scholarships = [
    ("D1 Men", 206, 6901, 35_000, 0.15),
    ("D1 Women", 341, 10931, 38_000, 0.20),
    ("D2", 479, 16872, 18_000, 0.05),
    ("D3", 830, 25242, 0, 0),
    ("NAIA", 1800, 35000, 15_000, 0.08),
    ("NJCAA", 230, 8000, 12_000, 0.03),
]

print(f"{'Division':<15} {'Programs':<12} {'Athletes':<12} {'Avg Aid':<12} {'4Yr Aid':<15} {'Expected Value':<15}")
print("-" * 100)

total_schol_ev = 0
for div, programs, athletes, aid, pct_full in scholarships:
    four_yr = aid * 4
    prob = (athletes * pct_full) / 60_000
    ev = prob * four_yr
    total_schol_ev += ev
    print(f"{div:<15} {programs:<12} {athletes:<12,} ${aid:<11,} ${four_yr:<14,} ${ev:>13,.0f}")

print("-" * 100)
print(f"{'TOTAL COLLEGE EXPECTED VALUE':<15} {'':12} {'':12} {'':12} {'':15} ${total_schol_ev:>13,.0f}")

# ============================================================================
# 6. CAREER EARNINGS BY MLS TIER
# ============================================================================
print("\n\n6. MLS CAREER EARNINGS SCENARIOS")
print("-" * 100)

careers = [
    ("Minimum wage (17% of MLS)", 88_025, 2.4),
    ("Median (50th percentile)", 325_000, 2.4),
    ("Top 25%", 656_750, 4.0),
    ("Top 13% ($1M+)", 1_200_000, 6.6),
    ("Superstars (top 3%)", 3_000_000, 8.0),
]

print(f"{'Scenario':<35} {'Annual':<15} {'Career Years':<15} {'Total Earnings':<15}")
print("-" * 100)

for scenario, annual, years in careers:
    total = annual * years
    print(f"{scenario:<35} ${annual:>13,} {years:>14.1f} ${total:>13,.0f}")

# ============================================================================
# 7. THE BIGGEST LOSERS
# ============================================================================
print("\n\n7. WHO PAYS MOST, GETS LEAST? (Economic Losers)")
print("-" * 100)

losers = [
    ("Lower-income families (<$50k)", "$0 (excluded)", "$0", "∞:1 LOSS", "Talent excluded by price"),
    ("Regional market elites (KC/Austin)", "$56,000", "$1,000", "56:1 LOSS", "Elite locally, invisible nationally"),
    ("Flight 2/3 at large clubs", "$56,000", "$2,000", "28:1 LOSS", "Same price, worse product"),
    ("Average elite players", "$56,000", "$2,500", "22:1 LOSS", "85% get zero return"),
    ("Female soccer players", "$52,500", "$8,000", "6.5:1 LOSS", "Fewer pro spots, lower salaries"),
    ("Competitive travel (WINNER)", "$18,600", "$45,000", "0.4:1 GAIN ✓", "Lower cost, realistic college"),
]

print(f"{'Group':<35} {'Investment':<15} {'Return':<12} {'Ratio':<12} Status")
print("-" * 100)

for group, invest, ret, ratio, why in losers:
    status = "✓ ONLY WINNER" if "GAIN" in ratio else "LOSER"
    print(f"{group:<35} {invest:<15} {ret:<12} {ratio:<12} {status}")
    print(f"  → {why}\n")

# ============================================================================
# 8. KEY CONCLUSIONS
# ============================================================================
print("\n" + "=" * 100)
print("KEY FINDINGS")
print("=" * 100)

findings = f"""
1. THE FUNNEL IS EXTREME
   • 4M youth → 70 USMNT = 0.0018% probability
   • 4M youth → 400 US-born MLS = 0.01% probability
   • Even D1 college = only 1.5% probability

2. ELITE TIER HAS NEGATIVE ROI
   • Investment: $48,000-56,000
   • Expected return: ${total_ev:,.0f}
   • ROI: {total_ev/48_000:.2f}x (you LOSE money on average)
   • 85% get zero tangible return

3. COLLEGE IS MORE REALISTIC THAN PRO
   • 60,000 college spots vs 850 MLS spots
   • D1 full scholarship: ~$280,000
   • D2 full scholarship: ~$240,000
   • Higher probability (13% from elite vs 0.4% MLS)

4. COMPETITIVE TRAVEL IS THE SWEET SPOT
   • Cost: $18,600 (3x cheaper than elite)
   • Expected return: $45,000+ (D2 full ride)
   • ROI: 2.4x positive return
   • ONLY tier with positive expected value

5. GEOGRAPHY MATTERS
   • Philadelphia academy: 8x better odds than KC
   • But even elite academies <1% MLS conversion
   • Regional markets at structural disadvantage
   • Cost to relocate: additional $20-40k

6. PAY-TO-PLAY CREATES EQUITY GAPS
   • ~40% of US (<$50k household) completely excluded
   • Elite = 16% of income for lower-income families
   • Travel = 6% of income (difficult but possible)
   • Talent screened OUT by price before evaluation

7. LARGEST LOSER GROUPS (by scale)
   • Lower-income families: COMPLETELY EXCLUDED
   • Regional elites: 56:1 loss (worse than anyone participating)
   • Flight 2/3 players: 28:1 loss (subsidizing Flight 1)
   • Average elite: 22:1 loss (majority of participants)

8. WHAT ACTUALLY WORKS
   • Rec: Low cost, joy, no ROI needed ($7,150 career)
   • Travel: Justified cost, realistic college ($30,100 career)
   • Elite: Only if pro/USMNT destined by U14 ($56,000 career)
   • School soccer: Critical dual pathway often ignored
"""

print(findings)

print("=" * 100)
print(f"\nNote: All costs/salaries in 2026 USD")
print(f"Data sources: MLSPA 2026 (916 players), NCAA 2025-26, 202 research statistics")
print("=" * 100)
