#!/usr/bin/env python3
"""Validate the archived NCA transcription against GilB's normalized dataset.

This is an internal reconciliation: it does NOT replace an independent recheck
against the original PDF source tables.
"""
from __future__ import annotations
import csv, json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'stories/GILB-002/data/raw/GILB002_mno_source_transcription_2024_2026-07.csv'
CLEAN=ROOT/'stories/GILB-002/data/clean/GILB002_mobile_internet_operator_monthly_2024_2026-07.csv'
METRICS=ROOT/'stories/GILB-002/analysis/GILB002_analysis_metrics_v1.json'
OP=['MTN','Telecel','AT']

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def check():
    original, tidy, summary=read(RAW),read(CLEAN),json.loads(METRICS.read_text())
    assert len(original)==31, 'Expected 31 monthly source-transcription records'
    assert len(tidy)==93, 'Expected 93 operator-month observations'
    by=defaultdict(dict)
    for r in tidy:
        key=(r['month'],r['operator'])
        assert r['operator'] in OP, f'Unknown operator {key}'
        assert r['operator'] not in by[r['month']], f'Duplicate {key}'
        assert r['source_url'].startswith('https://nca.org.gh/'), f'Non-NCA source {key}'
        by[r['month']][r['operator']]=int(r['subscriptions'])
    assert len(by)==31
    for r in original:
        m=r['month']; v=by[m]
        assert set(v)==set(OP), f'Missing operator for {m}'
        assert all(v[op]==int(r[op.lower()]) for op in OP), f'Operator mismatch for {m}'
        assert sum(v.values())==int(r['total_subscriptions']), f'Total does not reconcile {m}'
        assert int(r['reconciliation_difference'])==0, f'Nonzero source reconciliation delta {m}'
    first,last=by['2024-01-01'],by['2026-07-01']
    assert sum(first.values())==23_247_115
    assert sum(last.values())==30_800_194
    full=next(w for w in summary['windows'] if w['start']=='2024-01-01' and w['end']=='2026-07-01')
    assert full['net_change']==sum(last.values())-sum(first.values())==7_553_079
    for op in OP:
        assert full['operators'][op]['net_change']==last[op]-first[op]
    print('PASS: 31 months, 93 operator-month counts, no duplicate keys, all totals reconcile to transcribed source.')
    print('PASS: long-period growth and market-share inputs reproduce analysis metrics.')
    print('NOTE: source PDFs still require independent 93-value comparison before publication.')

if __name__=='__main__': check()
