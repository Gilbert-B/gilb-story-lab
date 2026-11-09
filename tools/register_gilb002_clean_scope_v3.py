#!/usr/bin/env python3
"""Record owner decision to exclude disputed historical trends from GILB-002.

Existing evidence and original datasets are preserved; no publication flags set.
Idempotent: running it twice creates no duplicate assets, analyses or issues.
"""
from pathlib import Path
import csv
import json
import sys
import registry

ROOT=Path(__file__).resolve().parents[1]
SID='GILB-002'
REC=ROOT/'stories'/SID/'record.json'
BASE=f'stories/{SID}/analysis/clean_scope_v3/'
SOURCE='https://nca.org.gh/wp-content/uploads/2026/06/Q1_2026_Statistical_Bulletin.pdf'
DATE='2026-11-09'
FILES=[
 BASE+'GILB002_Q1_2026_Crosschecked_Shares_v3.csv',
 BASE+'GILB002_Source_Exceptions_v3.csv',
 BASE+'GILB002_Clean_Evidence_Scope_And_Verification_v3.md',
 BASE+'GILB002_Clean_Evidence_Scope_And_Verification_v3.docx',
 BASE+'reproduce_gilb002_clean_scope_v3.py',
]

def run():
 for rel in FILES:
  if not (ROOT/rel).is_file():raise RuntimeError(f'Missing package file: {rel}')
 if not REC.is_file():raise RuntimeError('Missing GILB-002 record.json')
 rows=list(csv.DictReader((ROOT/FILES[0]).open(encoding='utf-8',newline='')))
 if len(rows)!=3:raise RuntimeError('Expected exactly three Q1 operator share rows')
 by={r['operator']:r for r in rows}
 if set(by)!={'MTN','Telecel','AT'}:raise RuntimeError('Unexpected operators')
 if abs(float(by['MTN']['traffic_share_pct_q1_2026'])-float(by['MTN']['subscription_share_pct_end_mar_2026'])-7.19)>1e-6:
  raise RuntimeError('Unexpected MTN share difference; aborting')
 previous=REC.read_text(encoding='utf-8')
 d=json.loads(previous);story=d['story']
 if story.get('id')!=SID:raise RuntimeError('Unexpected Story ID')
 if story.get('stage') in ('Ready to publish','Published'):
  raise RuntimeError('Story already release-ready; requires manual reconciliation')
 if any(str(e.get('safe_to_publish','')).casefold() in ('yes','true') for e in d.get('evidence',[])):
  raise RuntimeError('Existing evidence marked publication-approved; manual review required')
 changes=[]
 def setfield(rec,key,val):
  if rec.get(key)!=val:rec[key]=val;changes.append(key)

 # Story remains in research; no publication approval.
 if story.get('stage') in ('Idea','Research queued','Research underway','Data cleaning'):
  setfield(story,'stage','Analysis')
 setfield(story,'angle','Working candidate: Q1 2026 mobile data subscription share vs traffic share; historical paradox excluded')
 setfield(story,'editorial_decision','Original historical market-share paradox excluded; new Q1 cross-metric comparison pending review')
 setfield(story,'claim_confidence','Q1 shares crosschecked and traffic reconciled within NCA Bulletin; user-level and causal claims not supported; publication not approved')
 setfield(story,'next_action','Review v3 clean-evidence report; if editorial angle is accepted, draft narration using Q1 shares only. No NCA contact required.')
 setfield(story,'blocker','Exclude disputed December 2025 reporting series and exact March 2026 AT/total counts from public story; preserve audit trail.')

 # Preserve older analysis and calculations while explicitly taking the former headline out of scope.
 for a in d.get('analyses',[]):
  if a.get('id')=='AN-003':
   setfield(a,'status','Historical analysis retained; headline excluded from active GILB-002 editorial scope (NCA conflicting releases)')
   setfield(a,'limitations','Historical time-series comparison is not selected for public story because of cross-publication conflicts; original analysis files retained for audit.')
 for ds in d.get('datasets',[]):
  if ds.get('id')=='DATA-002':
   setfield(ds,'quality_next_check','Historical source series retained for audit ONLY; conflicting releases excluded from present video. See GILB002 v3 decision report.')
 for ev in d.get('evidence',[]):
  if ev.get('id')=='EV-003' or any(tag in str(ev.get('claim','')) for tag in ('GILB002-SHARE-TREND','GILB002-SUBSCRIPTION-GROWTH','GILB002-WINDOW-SENSITIVITY')):
   setfield(ev,'verification_status','Historical research only — excluded from GILB-002 active public-story scope')
   setfield(ev,'safe_to_publish','No')
   setfield(ev,'qualification','Kept as background/audit only. Do not use this claim in GILB-002 public script without new editorial verification.')

 # Reserve unique identifiers locally, including those created during this same update.
 used=set()
 for _,record in registry.load(ROOT)[0]:
  for section in ('datasets','analyses','evidence','assets','posts','issues'):
   for item in record.get(section,[]):
    if item.get('id'):used.add(str(item['id']))
 def fresh(prefix):
  n=1
  while f'{prefix}-{n:03}' in used:n+=1
  val=f'{prefix}-{n:03}'
  used.add(val)
  return val
 datasets=d.setdefault('datasets',[])
 ds=next((a for a in datasets if 'GILB002_Q1_2026_Crosschecked_Shares_v3.csv' in str(a.get('clean_file',''))),None)
 if ds is None:
  ds={'id':fresh('DATA'),'publisher':'National Communications Authority',
      'name':'Q1 2026 reconciled operator subscription and traffic percentage shares (restricted story table)',
      'source_url':SOURCE,'reference_period':'End-March subscription snapshot and Jan–Mar 2026 traffic totals',
      'granularity':'operator-quarter; shares of two separate measures',
      'classification':'Official Q1 2026 NCA Bulletin Tables 15 & 18; printed shares confirmed across 2 releases',
      'acquisition_status':'Source transcribed; original official PDF accessible by URL (not bundled)',
      'acquired_on':DATE,'raw_file':'','clean_file':FILES[0],
      'reuse_license':'Check NCA reuse rights before republishing source tables or original PDF',
      'quality_next_check':'Original report source reviewed; AT exact count differs by 4 from July release. All new video claims need owner final sign-off.',
      'owner':'GilB'}
  datasets.append(ds);changes.append('dataset-added')

 analyses=d.setdefault('analyses',[])
 marker='GILB002-SAFE-SCOPE-Q1-2026'
 a=next((r for r in analyses if marker in str(r.get('question',''))),None)
 if a is None:
  a={'id':fresh('AN'),'input_dataset_ids':ds['id'],
     'question':marker+' — Compare Q1 2026 subscription shares with traffic shares',
     'approach':'Read NCA Q1 2026 Tables 15/18, reconcile traffic TB and compute traffic share minus end-quarter subscription share; exclude conflicting cross-report values.',
     'finding':'MTN: 80.12% share of March-end MNO mobile data subscriptions vs 87.31% of Jan–Mar 2026 data traffic, +7.19 percentage points.',
     'run_date':DATE,'status':'Clean source-scope comparison prepared; editorial approval and final factual sign-off pending',
     'output_file':FILES[2], 'peer_check':'Q1 shares and MTN/Telecel March counts agree with July monthly release; traffic arithmetic checks pass in Q1 bulletin.',
     'supporting_evidence_id':'',
     'repro_notes':'Read the Word methodology report, CSV and run the v3 Python reproduction script.',
     'limitations':'Q1 traffic is aggregate volume while subscription share is March-end stock. AT exact March counts differ by 4 across sources; no causal or customer-level inference.'}
  analyses.append(a);changes.append('analysis-added')
 evs=d.setdefault('evidence',[])
 marker='GILB002-CROSS-METRIC-GAP-Q1-2026'
 ev=next((r for r in evs if marker in str(r.get('claim',''))),None)
 if ev is None:
  ev={'id':fresh('EV'),'claim':marker+' — MTN 80.12% of mobile data subscriptions at end-March versus 87.31% of Q1 mobile traffic',
      'source_dataset_id':ds['id'],'source_url':SOURCE,'proof_file':FILES[2],
      'verification_status':'Official-source table and arithmetic cross-check; human editorial approval pending',
      'checked_by':'AI-assisted source comparison', 'checked_on':DATE,'safe_to_publish':'No',
      'approved_by':'','approval_date':'',
      'qualification':'Two measures over different temporal windows; not per-customer usage. Exclude AT exact counts and disputed historical comparisons.'}
  evs.append(ev);changes.append('evidence-added')
 if a.get('supporting_evidence_id')!=ev['id']:
  setfield(a,'supporting_evidence_id',ev['id'])

 assets=d.setdefault('assets',[])
 for rel,typ,name in [(FILES[3],'Analysis verification report','GILB-002 clean-evidence editorial scope and verification report v3'),(FILES[2],'Analysis documentation','GILB-002 clean-evidence scope markdown v3'),(FILES[0],'Verified source excerpt','NCA Q1 cross-checked source shares v3'),(FILES[1],'Evidence exclusions','Cross-publication source conflicts excluded v3'),(FILES[4],'Reproducibility script','Reproduce Q1 share comparison v3')]:
  if any(r.get('path')==rel for r in assets):continue
  assets.append({'id':fresh('AS'),'asset_type':typ,'version':'v3.0','name':name,
    'path':rel,'status':'Prepared for editorial review — not publication-approved',
    'owner':'GilB','updated_on':DATE,'quality_review':'Published source table and arithmetic checks complete; owner sign-off outstanding',
    'notes':'Historical discrepancies are excluded from GILB-002 active script, not erased from the research history.'})
  changes.append('asset-added:'+rel)

 issues=d.setdefault('issues',[])
 marker='GILB002-EXCLUDE-DISPUTED-SERIES-V3'
 if not any(marker in str(x.get('description','')) for x in issues):
  issues.append({'id':fresh('ISS'),'type':'Decision','description':marker+' — Exclude disputed NCA historical comparisons and exact March 2026 AT/total values from active public story.',
       'priority':'High','owner':'GilB','opened_on':DATE,'due':'','status':'Closed',
       'resolution':'Owner chose no NCA outreach; problematic numbers retained in audit archive but prohibited in current GILB-002 narration.',
       'next_action':'Focus on source-consistent Q1 subscription and traffic shares; preserve original datasets.'})
  changes.append('editorial-decision-added')

 if not changes:
  print('NO CHANGES: GILB-002 clean evidence scope v3 already registered.')
  return
 registry.dump(REC,d)
 try:
  errs=registry.validate(ROOT)
  if errs:raise RuntimeError('; '.join(errs))
  registry.build(ROOT)
 except Exception:
  REC.write_text(previous,encoding='utf-8')
  try:registry.build(ROOT)
  except Exception:pass
  raise
 registry.events(ROOT,'gilb002-restrict-scope-to-consistent-evidence-v3',SID,{'changes':changes,'owner_decision':'No NCA contact; preserve excluded records','evidence_publication_approved':False})
 print('PASS: GILB-002 v3 scope updated; original evidence retained; publication approval unchanged.')

if __name__=='__main__':
 try:run()
 except Exception as exc:
  print('ERROR:',exc,file=sys.stderr);sys.exit(1)
