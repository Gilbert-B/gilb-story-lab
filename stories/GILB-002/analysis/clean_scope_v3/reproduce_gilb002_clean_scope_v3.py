#!/usr/bin/env python3
"""GILB-002 v3: check allowed cross-published percentages and source exceptions."""
from pathlib import Path
import csv
p=Path(__file__).with_name('GILB002_Q1_2026_Crosschecked_Shares_v3.csv')
rows=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
assert {r['operator'] for r in rows}=={'MTN','Telecel','AT'}
assert len(rows)==3
m=next(r for r in rows if r['operator']=='MTN')
assert m['subscription_share_pct_end_mar_2026']=='80.12'
assert m['traffic_share_pct_q1_2026']=='87.31'
assert abs(float(m['traffic_share_pct_q1_2026'])-float(m['subscription_share_pct_end_mar_2026'])-7.19)<1e-8
assert abs(sum(float(r['subscription_share_pct_end_mar_2026']) for r in rows)-100)<0.02
assert abs(sum(float(r['traffic_share_pct_q1_2026']) for r in rows)-100)<0.02
print('PASS: three reported subscription shares, traffic shares and MTN 7.19 percentage-point gap.')
print('CAVEAT: subscriber shares are March-end snapshots; traffic shares span Q1.')
print('EXCLUSION: exact AT March count and total differ by 4 across official publications.')
