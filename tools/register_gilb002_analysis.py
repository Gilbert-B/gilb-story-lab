#!/usr/bin/env python3
"""Idempotently register GILB-002 analysis without approving claims or publication.

Run from the GilB repository root with:
    py -3 tools/register_gilb002_analysis.py
    py -3 tools/registry.py validate
    py -3 tools/registry.py build
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import registry
import check_gilb002_data

ROOT = Path(__file__).resolve().parents[1]
SID = 'GILB-002'
REC = ROOT / 'stories' / SID / 'record.json'
BASE = f'stories/{SID}'
DATA = f'{BASE}/data/clean/GILB002_mobile_internet_operator_monthly_2024_2026-07.csv'
RAW = f'{BASE}/data/raw/GILB002_mno_source_transcription_2024_2026-07.csv'
REPORT = f'{BASE}/analysis/GILB002_findings_v1.md'
WORKBOOK = f'{BASE}/analysis/GILB002_Analysis_Workbook_v1.xlsx'
PANEL = f'{BASE}/analysis/GILB002_monthly_analysis_panel_v1.csv'
WINDOWS = f'{BASE}/analysis/GILB002_window_sensitivity_v1.csv'
METRICS = f'{BASE}/analysis/GILB002_analysis_metrics_v1.json'
SOURCE_NOTE = f'{BASE}/data/source_links/README_NCA_SOURCES.md'
SOURCE = 'https://nca.org.gh/mobile-data/'
TODAY = '2026-11-08'


def main() -> None:
    required = [RAW, DATA, REPORT, WORKBOOK, PANEL, WINDOWS, METRICS, SOURCE_NOTE]
    for rel in required:
        if not (ROOT / rel).is_file():
            raise RuntimeError(f'Missing {rel}. Extract the ZIP contents into the repository root first.')
    check_gilb002_data.check()
    if not REC.is_file():
        raise RuntimeError('Cannot find GILB-002 record.json; are you in the correct repository?')
    previous = REC.read_text(encoding='utf-8')
    record = json.loads(previous)
    story = record['story']
    if story.get('id') != SID:
        raise RuntimeError('Story ID mismatch; refusing update.')
    if story.get('stage') == 'Published':
        raise RuntimeError('GILB-002 is already Published; require manual reconciliation before change.')

    changes = []
    def update(row, fields, label):
        for key, val in fields.items():
            if row.get(key) != val:
                row[key] = val
                changes.append(f'{label}.{key}')

    # Reuse existing placeholder IDs instead of duplicating records.
    datasets = record.setdefault('datasets', [])
    dataset = next((x for x in datasets if x.get('id') == 'DATA-002'), None)
    if not dataset:
        raise RuntimeError('Expected placeholder dataset DATA-002 missing. Inspect current registry manually.')
    update(dataset, {
        'publisher': 'National Communications Authority (NCA)',
        'name': 'Official monthly MNO mobile internet subscription counts, 2024–July 2026',
        'source_url': SOURCE,
        'reference_period': 'January 2024 to July 2026',
        'granularity': 'operator-month (31 months × 3 operators)',
        'classification': 'Official regulator; source transcribed and reconciled',
        'acquisition_status': 'Acquired',
        'acquired_on': TODAY,
        'raw_file': RAW,
        'clean_file': DATA,
        'reuse_license': 'Check NCA data reuse terms before republication of full source tables',
        'quality_next_check': 'Transcribed CSV acquired, but primary PDFs not archived. Independently compare all 93 counts against NCA PDFs before publishing',
        'owner': 'GilB'
    }, 'DATA-002')
    analyses = record.setdefault('analyses', [])
    primary = next((x for x in analyses if x.get('id') == 'AN-003'), None)
    if not primary:
        raise RuntimeError('Expected placeholder analysis AN-003 missing. Inspect current registry manually.')
    update(primary, {
        'input_dataset_ids': 'DATA-002',
        'question': 'How have Ghana mobile internet subscription counts and market shares changed over 31 months?',
        'approach': 'Monthly shares, relative count growth, share percentage-point changes, net-growth contribution, alternative date windows, and anomalies',
        'finding': 'MTN added 5,673,061 subscriptions Jan 2024–Jul 2026 while share fell 81.61% to 80.02%; Telecel share gained 2.92pp; AT lost 1.33pp.',
        'run_date': TODAY,
        'status': 'Initial analysis complete; independent source audit and editorial approval pending',
        'output_file': REPORT,
        'peer_check': 'Pending independent transcription review; source endpoint PDF checks completed',
        'supporting_evidence_id': 'EV-003',
        'repro_notes': f'Read {DATA}; verify against {WORKBOOK}, {PANEL}, {WINDOWS}, {METRICS}',
        'limitations': 'Subscriptions ≠ people; operator MNO data only; short and long windows produce different conclusions. No causal inference.'
    }, 'AN-003')
    evidence = record.setdefault('evidence', [])
    ev = next((x for x in evidence if x.get('id') == 'EV-003'), None)
    if not ev:
        raise RuntimeError('Expected placeholder EV-003 missing; cannot alter safely.')
    # Do not erase any existing Verified / approved evidence: refuse rather than silently override.
    if str(ev.get('safe_to_publish', '')).lower() in ('yes', 'true'):
        raise RuntimeError('EV-003 already publication approved; manual review required.')
    update(ev, {
        'claim': 'MTN held 80.02% of active mobile network data subscriptions in July 2026 (not of unique people)',
        'source_dataset_id': 'DATA-002',
        'source_url': 'https://nca.org.gh/wp-content/uploads/2026/10/Monthly-Industry-Data_July_2026-.pdf',
        'proof_file': REPORT,
        'verification_status': 'Preliminary — official PDF spot checked; independent full-series audit pending',
        'safe_to_publish': 'No',
        'qualification': 'Only MNO mobile internet subscriptions; excludes fixed network/BWA, revenue and data traffic.'
    }, 'EV-003')

    # Add references for discoveries without treating them as verified publication claims.
    used = {r.get('id') for _,s in registry.load(ROOT)[0] for k in ('datasets','analyses','evidence','assets','posts','issues') for r in s.get(k, [])}
    def new_id(prefix):
        n = 1
        while f'{prefix}-{n:03}' in used: n += 1
        x = f'{prefix}-{n:03}';used.add(x);return x
    def evidence_add(marker, claim, url, caveat):
        if any(marker in str(e.get('claim','')) for e in evidence): return
        eid = new_id('EV')
        evidence.append({
            'id':eid,'claim':f'{marker} — {claim}', 'source_dataset_id':'DATA-002',
            'source_url':url, 'proof_file':REPORT,
            'verification_status':'Research calculation; independent check pending',
            'checked_by':'','checked_on':'','safe_to_publish':'No',
            'approved_by':'','approval_date':'','qualification':caveat
        })
        changes.append('evidence.'+eid)
    evidence_add('GILB002-SHARE-TREND', 'Jan 2024–Jul 2026 MTN share fell 1.60pp; Telecel rose 2.92pp; AT fell 1.33pp', SOURCE,
                 'End-to-end comparison only; MTN share rebounded from mid-2025 low.')
    evidence_add('GILB002-SUBSCRIPTION-GROWTH', 'Total MNO subscriptions grew 7,553,079 (+32.49%) between Jan 2024 and Jul 2026', SOURCE,
                 'Net active subscriptions, not newly acquired people or unique customers.')
    evidence_add('GILB002-WINDOW-SENSITIVITY', 'MTN contributed 84.6% of net growth Dec25–Jul26, versus 75.1% Jan24–Jul26', SOURCE,
                 'Denominator is net stock change; operator negative change means contributions can exceed 100% before offsets.')

    assets = record.setdefault('assets', [])
    for path,asset_type,name in [
        (WORKBOOK,'Analysis workbook','GILB-002 31-month analysis workbook v1'),
        (REPORT,'Research findings','GILB-002 editorial findings v1'),
        (PANEL,'Analysis data','Monthly 31-month trend panel'),
        (WINDOWS,'Sensitivity analysis','Time window comparisons'),
        (METRICS,'Analysis evidence','Computed metrics, derived from counts'),
    ]:
        match = next((x for x in assets if x.get('path') == path), None)
        if match is None:
            rid = new_id('AS')
            assets.append({'id':rid,'asset_type':asset_type,'version':'v1.0','name':name,'path':path,
                           'status':'Research asset; not publication-approved','owner':'GilB','updated_on':TODAY,
                           'quality_review':'Source endpoints spot-checked; independent audit outstanding',
                           'notes':'Keep baseline source data and previous versions. Not a script or final video.'})
            changes.append('asset.'+rid)

    issues = record.setdefault('issues', [])
    for marker,desc,prio,action in [
        ('GILB002-PDF-ARCHIVE','Original NCA PDFs are linked but not stored inside the repo.','Medium','Download the three NCA original PDF files; retain URL and date for each.'),
        ('GILB002-ROW-QA','All 93 operator-month transcriptions need a second, independent source comparison.','High','Compare every CSV count with source PDFs and note any corrections.'),
        ('GILB002-OPERATOR-SHIFTS','Abrupt Telecel 2025 and AT December 2025 subscription changes need follow-up.','Medium','Search NCA bulletins and operator announcements; do not assert causes prematurely.'),
    ]:
        if any(marker in str(i.get('description', '')) for i in issues): continue
        rid = new_id('ISS')
        issues.append({'id':rid,'type':'Research follow-up','description':f'{marker} — {desc}',
                       'priority':prio,'owner':'GilB','opened_on':TODAY,'due':'',
                       'status':'Open','resolution':'','next_action':action})
        changes.append('issue.'+rid)

    if story.get('stage') in ('Idea','Research queued','Research underway','Data cleaning'):
        update(story, {'stage':'Analysis','editorial_decision':'Analysis findings prepared — no story angle or narration approved',
                       'claim_confidence':'Preliminary; independent full data verification required',
                       'next_action':'Review the analysis and select a defensible story angle; audit 93 monthly values and research unusual movements',
                       'blocker':'NCA raw PDFs not yet archived; independent transcription and editorial verification pending'},'story')

    if not changes:
        print('NO CHANGES: GILB-002 analysis already registered; no duplicate audit event.')
        return
    registry.dump(REC, record)
    try:
        problems = registry.validate(ROOT)
        if problems: raise RuntimeError('; '.join(problems))
        registry.build(ROOT)
    except Exception:
        REC.write_text(previous, encoding='utf-8')
        try:registry.build(ROOT)
        except Exception:pass
        raise
    registry.events(ROOT, 'register-gilb002-initial-analysis', SID, {
        'period':'2024-01 to 2026-07', 'months':31,'operator_month_records':93,
        'editorial_decision':'pending','publication_approved':False,'updates':changes})
    print(f'PASS: GILB-002 analysis registered ({len(changes)} changes); NOT approved or published.')
    print('The dataset, findings, analysis, evidence and follow-up issues are now linked to GILB-002.')

if __name__ == '__main__':
    try:main()
    except Exception as exc:
        print('ERROR:',str(exc),file=sys.stderr)
        raise SystemExit(1)
