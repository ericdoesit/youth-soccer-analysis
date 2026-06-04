"""
Run this script to regenerate all derived tables in data/analysis/.
Usage: python scripts/build_summary_tables.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
PROCESSED = BASE / 'data' / 'processed'
ANALYSIS  = BASE / 'data' / 'analysis'
ANALYSIS.mkdir(exist_ok=True)

costs  = pd.read_csv(PROCESSED / 'costs.csv')
schols = pd.read_csv(PROCESSED / 'scholarship_outcomes.csv')
pros   = pd.read_csv(PROCESSED / 'pro_outcomes.csv')

# Career cost by tier
career_years = {1: 13, 2: 9, 3: 7, 4: 7}
tier_cost = costs.groupby('tier')[['total_low','total_mid','total_high']].mean()
rows = []
for tier, years in career_years.items():
    if tier in tier_cost.index:
        row = tier_cost.loc[tier]
        rows.append({
            'tier': tier, 'career_years': years,
            'career_low':  round(row['total_low']  * years),
            'career_mid':  round(row['total_mid']  * years),
            'career_high': round(row['total_high'] * years),
        })
career_df = pd.DataFrame(rows)
career_df.to_csv(ANALYSIS / 'career_cost_by_tier.csv', index=False)
print('Wrote career_cost_by_tier.csv')

# Probability funnel
funnel = pd.DataFrame([
    {'stage': 'All youth soccer players',    'count': 4_000_000},
    {'stage': 'Competitive travel (Tier 2)', 'count': 1_200_000},
    {'stage': 'ECNL / MLS NEXT (Tier 3)',    'count': 150_000},
    {'stage': 'Pro Academies (Tier 4)',       'count': 20_000},
    {'stage': 'Any pro contract (US)',        'count': 2_500},
    {'stage': 'MLS/NWSL first division',     'count': 600},
    {'stage': 'Top European league',          'count': 50},
])
funnel['prob_from_start_pct'] = (funnel['count'] / funnel['count'].iloc[0] * 100).round(4)
funnel.to_csv(ANALYSIS / 'probability_matrix.csv', index=False)
print('Wrote probability_matrix.csv')

print('\nAll summary tables written to data/analysis/')
