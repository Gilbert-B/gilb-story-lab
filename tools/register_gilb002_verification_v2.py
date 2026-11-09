#!/usr/bin/env python3
"""Safely attach GILB-002 source-verified analysis report to the existing registry.

Run after the original v1 analysis installer:
    py -3 tools/verify_gilb002_nca_v2.py
    py -3 tools/register_gilb002_verification_v2.py
    py -3 tools/registry.py validate
    py -3 tools/registry.py build

All publication flags remain unchanged (and must be No). Preserves unrelated edits.
"""
from pathlib import Path
import json
import subprocess
import sys
import registry

ROOT=Path(__file__).resolve().parents[1]
SID='GILB-002'
REC=ROOT/'stories'/SID/'record.json'
PREFIX=f'stories/{SID}/analysis/'
DATE='2026-11-08'
REQUIRED=[
 PREFIX+'GILB002_Analysis_and_Verification_Report_v2.docx',
 PREFIX+'GILB002_Analysis_and_Verification_Report_v2.md',
 PREFIX+'GILB002_Source_to_Clean_Comparison_93_Rows_v2.csv',
 PREFIX+'GILB002_verified_metrics_v2.json',
 f'stories/{SID}/data/clean/GILB002_mobile_internet_operator_monthly_2024_2026-07.csv',
 'docs/GilB_Analysis_and_Verification_Reporting_Standard_v1.md'
]

def main():
 for rel in REQUIRED:
  if not (ROOT/rel).is_file(): raise RuntimeError(f'Missing {rel}; copy ZIP into repo root first')
 if not REC.is_file():raise RuntimeError('Missing GILB-002 record.json')
 # Recompute source-table audit from independent NCA transcription before changing registry.
 subprocess.run([sys.executable,str(ROOT/'tools/verify_gilb002_nca_v2.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 audit=json.loads((ROOT/PREFIX/'GILB002_source_audit_metrics_v2.json').read_text(encoding='utf-8'))
 if audit['source_value_checks'] != 93 or audit['mismatches']:
  raise RuntimeError('Expected 93 primary source checks with zero mismatches')
 previous=REC.read_text(encoding='utf-8')
 d=json.loads(previous);s=d['story'];
 if s['id']!=SID:raise RuntimeError('Story ID mismatch')
 if s.get('stage') in ('Ready to publish','Published'):
  raise RuntimeError('Story already at publication stage; manual review required')
 if any(str(e.get('safe_to_publish','')).lower() in ('yes','true') for e in d.get('evidence',[])):
  raise RuntimeError('Already contains publication-approved evidence; manual review before changing verification text')
 changes=[]
 def upd(obj,key,value):
  if obj.get(key)!=value:obj[key]=value;changes.append(key)
 analyses=d['analyses'];a=next((r for r in analyses if r.get('id')=='AN-003'),None)
 if a is None:raise RuntimeError('Please install GILB-002 v1 analysis first; AN-003 is missing')
 upd(a,'status','Full 93-row NCA source-table audit passed; human peer review and publication approval pending')
 upd(a,'peer_check','93/93 values and 31/31 mobile totals matched NCA primary PDF tables (AI-assisted verification; external human sign-off pending)')
 upd(a,'output_file',PREFIX+'GILB002_Analysis_and_Verification_Report_v2.md')
 upd(a,'repro_notes','Read v2 report; replay tools/verify_gilb002_nca_v2.py; inspect 93-row source comparison ledger; preserve original NCA PDFs')
 upd(a,'limitations','Counts are subscriptions, not people; market share changes over time are not necessarily monotonic; monthly shifts have no verified causal explanation; NCA PDF binaries still need archiving.')
 upd(s,'claim_confidence','All 93 source values and 31 monthly MNO totals checked against NCA; human claim sign-off pending')
 upd(s,'next_action','Review v2 analysis verification report, archive original NCA PDFs, approve story angle/claim wording; do not publish yet')
 # Avoid changing editorial angle automatically. Keep existing Analysis/Verification status.
 ds=next((r for r in d['datasets'] if r.get('id')=='DATA-002'),None)
 if ds:upd(ds,'quality_next_check','93/93 source values and 31/31 official totals reconciled to NCA PDFs (2026-11-08); archive NCA PDF originals and obtain external claim sign-off')
 ev=next((r for r in d['evidence'] if r.get('id')=='EV-003'),None)
 if ev:
  upd(ev,'verification_status','Source counts verified (AI-assisted 93-row NCA audit); human publication approval pending')
  upd(ev,'proof_file',PREFIX+'GILB002_Analysis_and_Verification_Report_v2.md')
  upd(ev,'qualification','80.02% of active MNO mobile internet subscriptions in July 2026; not people, revenues, traffic, or all internet subscriptions')
 # Mark source verification issue addressed; maintain separate human reviewer + PDF archival open gates.
 for issue in d.get('issues',[]):
  if 'GILB002-ROW-QA' in issue.get('description',''):
   upd(issue,'status','Resolved')
   upd(issue,'resolution','93/93 operator-month values independently re-read from primary NCA published tables; 31/31 source totals reconciled. Human peer sign-off remains a separate publication gate.')
   upd(issue,'next_action','See v2 report and audit CSV; separate human sign-off issue remains open')
 issues=d.setdefault('issues',[]);existingids={r.get('id') for _,story in registry.load(ROOT)[0] for k in ('datasets','analyses','evidence','assets','posts','issues') for r in story.get(k,[])}
 def newid(prefix):
  i=1
  while f'{prefix}-{i:03}' in existingids:i+=1
  v=f'{prefix}-{i:03}';existingids.add(v);return v
 if not any('GILB002-HUMAN-SIGNOFF' in x.get('description','') for x in issues):
  issues.append({'id':newid('ISS'),'type':'Publication QA follow-up','description':'GILB002-HUMAN-SIGNOFF — Approve all final narrated and visual claims against NCA primary sources.','priority':'High','owner':'GilB','opened_on':DATE,'due':'','status':'Open','resolution':'','next_action':'External or owner review of v2 verification report, exact claims, period and visual scale before publication.'});changes.append('issue:human-signoff')
 assets=d.setdefault('assets',[])
 for rel,name,typ in [
 (PREFIX+'GILB002_Analysis_and_Verification_Report_v2.docx','GILB-002 reproducible analysis and verification report v2','Research verification report'),
 (PREFIX+'GILB002_Analysis_and_Verification_Report_v2.md','GILB-002 verification report markdown companion','Research verification report'),
 (PREFIX+'GILB002_Source_to_Clean_Comparison_93_Rows_v2.csv','NCA row-level independent source checks (93 rows)','QA evidence'),
 (PREFIX+'GILB002_verified_metrics_v2.json','Recomputed verified summary metrics v2','Reproducibility evidence')]:
  if any(a.get('path')==rel for a in assets):continue
  assets.append({'id':newid('AS'),'asset_type':typ,'version':'v2.0','name':name,'path':rel,'status':'Verified primary-source transcription; not publication-approved','owner':'GilB','updated_on':DATE,'quality_review':'93 source counts and 31 monthly totals passed; human claim sign-off pending','notes':'Do not approve script, video or publishing automatically; originals of NCA PDFs not archived.'});changes.append('asset:'+rel)
 if not changes: print('NO CHANGES: GILB-002 v2 verification already recorded.');return
 registry.dump(REC,d)
 try:
  probs=registry.validate(ROOT)
  if probs:raise RuntimeError('; '.join(probs))
  registry.build(ROOT)
 except Exception:
  REC.write_text(previous,encoding='utf-8')
  try:registry.build(ROOT)
  except Exception:pass
  raise
 registry.events(ROOT,'register-gilb002-primary-source-verification-v2',SID,{'date':DATE,'checked_rows':93,'source_mismatches':0,'monthly_totals':31,'human_signoff':False,'publication_approved':False,'changes':changes})
 print('PASS: GILB-002 v2 verification registered; all publication approval remains pending.')

if __name__=='__main__':
 try:main()
 except Exception as ex:
  print('ERROR:',ex,file=sys.stderr);sys.exit(1)
