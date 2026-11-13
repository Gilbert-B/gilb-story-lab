#!/usr/bin/env python3
"""Targeted, repeatable archival updater for GILB-003 and GILB-005.

Copies NO files and does NO git operations. Run after merging the package content
into your existing repository. 003 owner creative-approved; 005 final video
received, public release QA not recorded. Never marks either Published.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sys
import registry

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-11-13'
INFO={
 'GILB-003': {'file':'GILB003_Ghanas_Sleeping_Wallets_Final.mp4','sha':'063f35f4633e66b7f94932a7900f7caa18649eb9e9ae0d96a221d7e9620d2ada','bytes':8428566,'status':'Completed — owner approved','completed':'2026-11-12'},
 'GILB-005': {'file':'GILB005_Accra_Growing_Shrinking_Final.mp4','sha':'244bdb74a393c0ed87a46357f6f8438c242e6a61406ffa137acb3627c2569378','bytes':12075215,'status':'Completed — final master delivered; publication review pending','completed':'2026-11-13'},
}


def put(o,k,v):
 if o.get(k)!=v:
  o[k]=v
  return True
 return False


def main():
 # Preflight BOTH files and BOTH authoritative records before any modification.
 for sid,info in INFO.items():
  root=ROOT/'stories'/sid
  p=root/'record.json'
  if not p.is_file():raise RuntimeError(f'Missing {sid} record.json')
  d=json.loads(p.read_text(encoding='utf-8'))
  s=d.get('story',{})
  if s.get('id')!=sid:raise RuntimeError(f'Unexpected ID in {p}')
  if s.get('stage') in ('Published','Archived','Ready to publish') or any(x.get('actual_date') or x.get('publish_status')=='Published' for x in d.get('posts',[])):
   raise RuntimeError(f'{sid} already has release state; reconcile before running this updater.')
  for name in (info['file'], info['file']+'.sha256', 'PRODUCTION_RELEASE_RECORD.md','RELEASE_QA_CHECKLIST.md'):
   if not (root/'production'/'final'/name).is_file():raise RuntimeError(f'Missing {sid} / {name}')
  video=root/'production'/'final'/info['file']
  if video.stat().st_size != info['bytes']:
   raise RuntimeError(f'{sid}: unexpected MP4 size')
  with video.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
  if digest!=info['sha']:
   raise RuntimeError(f'{sid}: MP4 hash mismatch')
  if info['sha'] not in (video.with_suffix(video.suffix+'.sha256')).read_text(encoding='utf-8'):
   raise RuntimeError(f'{sid}: fingerprint file mismatch')

 # Keep the existing seed ideas/datasets; make historical reassignment explicit.
 backups={}
 updates={}
 used=set()
 for rp,obj in registry.load(ROOT)[0]:
  for coll in ('datasets','analyses','evidence','assets','posts','issues'):
   for r in obj.get(coll,[]): used.add(r.get('id'))
 def new_id(prefix):
  i=1
  while f'{prefix}-{i:03d}' in used:i+=1
  sid=f'{prefix}-{i:03d}';used.add(sid);return sid

 for sid,info in INFO.items():
  p=ROOT/'stories'/sid/'record.json'
  original=p.read_text(encoding='utf-8')
  d=json.loads(original)
  s=d['story']
  changed=False
  def setf(k,v):
   nonlocal changed
   if put(s,k,v):changed=True

  rootrel=f'stories/{sid}/production/final/'
  master=rootrel+info['file']
  setf('stage','Review')
  setf('production_status',info['status'])
  setf('production_completed_on',info['completed'])
  setf('final_master_file',master)
  setf('final_master_sha256',info['sha'])
  if sid=='GILB-003':
   setf('title',"Ghana's Sleeping Wallets")
   setf('pillar','Technology & changing Ghana')
   setf('angle','Registered vs active mobile money accounts (August 2026)')
   setf('visual_format','Unpacked by GilB — data story')
   setf('editorial_decision','Final video owner-approved 2026-11-12. Production complete, not marked publicly published. Earlier analysis-stage description superseded. Historic DATA-003 census lead predates story reassignment and is not evidence for this episode.')
   setf('claim_confidence','BoG 2026 figures analyzed; separate final factual and rights release review not recorded in repository.')
   setf('next_action','Archive completed master (done). Complete final factual, source attribution, rights and platform QA; record public post URL/date only after publishing.')
   setf('blocker','Public release checks remain outstanding; do not infer Published from video completion.')
  else:
   setf('title','Accra Is Growing. Accra Is Shrinking.')
   setf('pillar','Ghana by region & district')
   setf('angle','2010–2021 census comparison: Greater Accra region vs former Accra Metropolitan successor districts')
   setf('visual_format','Unpacked by GilB — census data story')
   setf('audience','Ghanaian public and diaspora')
   setf('editorial_decision','Final video supplied by owner 2026-11-13. Former GILB-005 starter idea about music chart longevity is superseded; original DATA-005 retained as historical lead only. Final creative/publication approval not separately recorded.')
   setf('claim_confidence','GSS regional totals verified; 10-district comparison arithmetic reproduced. Exact same-area 2010–2021 geographic boundary equivalence unverified.')
   setf('next_action','Review final MP4 and 2010–2021 geographic qualification, complete publication fact/rights QA, then record actual post URL/date after publishing.')
   setf('blocker','No certified 2010–2021 boundary polygon crosswalk. Never claim 383,516 people left the identical geographic area based solely on reconstructed counts.')
   # Retain the original candidate dataset but flag its unrelated purpose.
   for ds in d.get('datasets',[]):
    if ds.get('id')=='DATA-005':
     note='Historical GILB-005 seed idea (Ghana music chart longevity); not evidence for current Accra census video. Retained for provenance.'
     if put(ds,'quality_next_check',note):changed=True
  assets=d.setdefault('assets',[])
  asset_rows=[
   (master,'Final video','Final HD production master','final',info['status'],'Unchanged owner-supplied file. 1080x1920; H.264/AAC; 30fps; SHA-256 '+info['sha']),
   (rootrel+info['file']+'.sha256','Master verification','Final-video SHA-256','v1','Recorded','Byte-level fingerprint of owner-provided MP4.'),
   (rootrel+'PRODUCTION_RELEASE_RECORD.md','Production record','Archive and status record','v1','Recorded','Production completion is distinct from publication clearance.'),
   (rootrel+'RELEASE_QA_CHECKLIST.md','Release QA checklist','Remaining publication checks','v1','Open','Final factual, rights and platform checks are pending.'),
  ]
  if sid=='GILB-003':
   asset_rows.append(('stories/GILB-003/scripts/narration_v3_final_owner_approved.md','Narration script','GILB-003 approved narration','v3 final','Owner approved','Exact owner-approved script text.'))
  for apath,kind,title,version,status,notes in asset_rows:
   existing=next((a for a in assets if a.get('path')==apath),None)
   if existing is None:
    assets.append({'id':new_id('AS'),'asset_type':kind,'version':version,'name':title,
      'path':apath,'status':status,'owner':'GilB','updated_on':DATE,
      'quality_review':'Final production asset verified; publication/release QA pending.',
      'notes':notes})
    changed=True
   elif put(existing,'status',status):changed=True
  if sid=='GILB-005':
   issues=d.setdefault('issues',[])
   marker='GILB005-2010-2021-BOUNDARY-CROSSWALK'
   if not any(marker in x.get('description','') for x in issues):
    issues.append({'id':new_id('ISS'),'type':'Verification blocker',
      'description':marker+': Exact equivalence of the 2010 metropolitan footprint and summed 2021 successor district polygons has not been independently confirmed.',
      'priority':'High','owner':'GilB','opened_on':DATE,'due':'','status':'Open',
      'resolution':'','next_action':'Retain on-screen qualifiers; obtain official boundary crosswalk before making an unqualified population-decline claim.'})
    changed=True
  backups[p]=original
  if changed:updates[p]=d

 # Make only exact final media paths visible in GitHub Desktop (MP4s globally ignored).
 gi=ROOT/'.gitignore'
 gi_old=gi.read_text(encoding='utf-8') if gi.exists() else ''
 extra='\n'.join(
  f'!stories/{sid}/production/final/{info["file"]}'
  for sid,info in INFO.items()
  if f'!stories/{sid}/production/final/{info["file"]}' not in gi_old
 )
 gi_changed=bool(extra)
 if gi_changed:
  gi.write_text(gi_old.rstrip() + '\n\n# Scoped exceptions: final GilB story masters\n' + extra + '\n',encoding='utf-8')

 if not updates and not gi_changed:
  print('NO CHANGES: GILB-003 and GILB-005 production records already up to date.')
  return
 try:
  for p,d in updates.items():registry.dump(p,d)
  err=registry.validate(ROOT)
  if err:raise RuntimeError('Registry validation failed: '+'; '.join(err))
  registry.build(ROOT)
 except Exception:
  for p,old in backups.items():p.write_text(old,encoding='utf-8')
  if gi_changed:gi.write_text(gi_old,encoding='utf-8')
  try:registry.build(ROOT)
  except Exception:pass
  raise
 for sid in INFO:
  if ROOT/'stories'/sid/'record.json' in updates:
   registry.events(ROOT,'final-video-archived',sid,{
    'master':f'stories/{sid}/production/final/{INFO[sid]["file"]}',
    'sha256':INFO[sid]['sha'], 'production_status':INFO[sid]['status'],
    'public_post_status':'unchanged; not marked published',
    'factual_claims':'approval flags unchanged',
   })
 print('PASS: Verified both unchanged full-HD MP4s and updated scoped story registry records.')
 print('PASS: Current Story Registry exports rebuilt; 004 and unrelated stories unchanged.')
 print('PASS: Production completion NOT treated as Published or claim approval.')
 print('PASS: Two precise .gitignore exceptions added so GitHub Desktop can see the MP4s.')

if __name__=='__main__':
 try:main()
 except Exception as exc:
  print('ERROR:',str(exc),file=sys.stderr)
  raise SystemExit(1)
