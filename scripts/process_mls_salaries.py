"""
Placeholder for MLS salary data processing.
MLSPA publishes salary data annually at:
  https://mlsplayers.org/resources/salary-guide

When raw salary CSV is in data/raw/professional/, this script
normalizes it into the pro_outcomes.csv schema.
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
RAW  = BASE / 'data' / 'raw' / 'professional'
OUT  = BASE / 'data' / 'processed' / 'pro_outcomes.csv'

print('MLS salary processor — not yet implemented.')
print(f'Place raw MLSPA CSV in: {RAW}')
print(f'Output target: {OUT}')
print('\nData sources to download manually:')
print('  MLSPA Salary Guide: https://mlsplayers.org/resources/salary-guide')
print('  Transfermarkt US players: https://www.transfermarkt.us/statistik/topmarktwerte/marktwertetop/200/page/1/land_id/184')
