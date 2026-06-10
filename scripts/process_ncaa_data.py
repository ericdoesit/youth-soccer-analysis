"""
Placeholder for NCAA data processing.
When raw NCAA scholarship data is downloaded to data/raw/scholarships/,
this script normalizes it into the scholarship_outcomes.csv schema.

Expected raw input format: NCAA sport sponsorship report (CSV or Excel)
Output: rows appended to data/scholarship_outcomes.csv
"""
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent.parent
RAW  = BASE / 'data' / 'raw' / 'scholarships'
OUT  = BASE / 'data' / 'processed' / 'scholarship_outcomes.csv'

print('NCAA data processor — not yet implemented.')
print(f'Place raw NCAA files in: {RAW}')
print(f'Output target: {OUT}')
print('\nData sources to download manually:')
print('  https://www.ncaa.org/sports/2013/11/20/ncaa-participation-statistics.aspx')
print('  https://www.ncaa.org/sports/2015/6/10/scholarship-limits.aspx')
