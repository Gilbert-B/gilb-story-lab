#!/usr/bin/env python3
"""Safely record the GilB-001 creative benchmark in an existing GilB Story Lab registry.

Idempotent: re-running does not add duplicate assets/issues/audit events.
No publication, evidence approval, or post metadata is modified.
"""
from __future__ import annotations
import json, sys, hashlib
from pathlib import Path
import registry

ROOT=Path(__file__).resolve().parents[1]
SID='GILB-001'
RECORD=ROOT/'stories'/SID/'record.json'
BASE=f'stories/{SID}/production/benchmark_rc1/'
MP4=BASE+'GILB001_Hearts_of_Oak_Creative_Benchmark_RC1.mp4'
QA=BASE+'FINAL_RELEASE_QA.md'
MANIFEST=BASE+'ASSET_MANIFEST.json'
STANDARD='docs/GilB_PRODUCTION_QUALITY_STANDARD_v1.md'
RELEASE=BASE+'RELEASE_NOTES.md'


def main():
    needed=(MP4,QA,MANIFEST,STANDARD,RELEASE)
    for rel in needed:
        if not (ROOT/rel).is_file():
            raise RuntimeError(f'Missing file {rel}. Copy extracted package contents into repo root.')
    mani=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))
    expected=next((x['sha256'] for x in mani['files'] if x['path']==Path(MP4).name),None)
    actual=hashlib.sha256((ROOT/MP4).read_bytes()).hexdigest()
    if not expected or expected!=actual:
        raise RuntimeError('Video SHA-256 does not match package manifest; do not register damaged video.')
    if not RECORD.exists():
        raise RuntimeError('Missing stories/GILB-001/record.json. Use the existing GilB repo.')
    original=RECORD.read_text(encoding='utf-8')
    obj=json.loads(original)
    st=obj.get('story',{})
    if st.get('id')!=SID:raise RuntimeError('Wrong story record ID.')
    if st.get('stage') in ('Ready to publish','Published','Archived') or any(p.get('publish_status')=='Published' for p in obj.get('posts',[])):
        raise RuntimeError('Story is already ready/published/archived. Review manually to avoid downgrading release status.')
    changes=[]
    used={r.get('id') for _,s in registry.load(ROOT)[0] for k in ('datasets','analyses','evidence','assets','posts','issues') for r in s.get(k,[])}
    used|={r.get('id') for r in registry.load(ROOT)[1].get('records',[])}
    def new_id(prefix):
        n=1
        while f'{prefix}-{n:03d}' in used:n+=1
        rid=f'{prefix}-{n:03d}';used.add(rid);return rid
    assets=obj.setdefault('assets',[])
    def add_asset(path,typ,name,version,description,review):
        if any(a.get('path')==path for a in assets):return
        rid=new_id('AS')
        assets.append({'id':rid,'asset_type':typ,'version':version,'name':name,'path':path,
                       'status':description,'owner':'GilB','updated_on':registry.today(),
                       'quality_review':review,'notes':'Preserve this reference; do not overwrite prior versions.'})
        changes.append(f'asset {rid}: {path}')
    add_asset(MP4,'Creative benchmark video','Hearts of Oak — Claude RC1 owner-approved creative benchmark','RC1',
        'Creative benchmark approved; NOT publication cleared',
        'GilB approved as future quality baseline on 2026-11-08. Video 512x910, 30fps, 99.6s. Native 1080p and factual release checks pending.')
    add_asset(STANDARD,'Production quality standard','GilB all-content quality checklist','v1.0',
        'Approved standard for subsequent episodes',
        'Covers evidence, visual accuracy, narration, audio, captions, technical export, source retention and publication.')
    add_asset(QA,'Release QA tracker','GILB-001 outstanding final release checks','v1.0',
        'Open — not signed off',
        'Native 1080x1920 master, Claude project source, final evidence review, captions and audio/rights checks still open.')
    add_asset(MANIFEST,'Archive manifest','GILB-001 archive provenance and file hashes','v1.0',
        'Reference archive', 'Preserved source snapshots are not Claude editable source files.')
    issues=obj.setdefault('issues',[])
    def add_issue(marker,description,priority,next_action):
        if any(marker in str(i.get('description','')) for i in issues):return
        rid=new_id('ISS')
        issues.append({'id':rid,'type':'Release blocker','description':marker+' — '+description,
                       'priority':priority,'owner':'GilB','opened_on':registry.today(),
                       'due':'','status':'Open','resolution':'','next_action':next_action})
        changes.append(f'issue {rid}')
    add_issue('BENCHMARK-RC1-EXPORT',
      'Approved review file is 512x910; native 1080x1920 master is required before publication.',
      'High','Export from Claude production project; verify native resolution. Do not upscale and label as native.')
    add_issue('BENCHMARK-RC1-RELEASE-QA',
      'Final match-data verification, audio/music rights, caption and mobile playback sign-off outstanding.',
      'High','Use FINAL_RELEASE_QA.md and PRODUCTION_QUALITY_STANDARD_v1.md; explicitly approve every release claim.')
    add_issue('BENCHMARK-RC1-SOURCE',
      'Claude editable animation project not present in uploaded MP4 or reference source snapshots.',
      'Medium','Add Claude code/project/assets to private versioned storage and link the canonical folder.')

    if st.get('stage')!='Review':
        st['stage']='Review';changes.append('stage Review')
    decision='Creative benchmark approved 2026-11-08; final factual/technical publication sign-off pending'
    if st.get('editorial_decision')!=decision:
        st['editorial_decision']=decision;changes.append('editorial decision')
    next_action='Obtain native full-resolution export and Claude source; complete evidence, audio/rights and caption QA; then approve release separately.'
    if st.get('next_action')!=next_action:
        st['next_action']=next_action;changes.append('next action')
    # Preserve claim_confidence, blocker, evidence, publishing, source links and previously reviewed assets.
    if not changes:
        print('NO CHANGES: benchmark already registered; no duplicate event.')
        return
    registry.dump(RECORD,obj)
    try:
        problems=registry.validate(ROOT)
        if problems:raise RuntimeError('; '.join(problems))
        registry.build(ROOT)
    except Exception:
        RECORD.write_text(original,encoding='utf-8')
        try:registry.build(ROOT)
        except Exception:pass
        raise
    registry.events(ROOT,'approve-creative-benchmark-rc1',SID,{
        'owner_approved':'Creative quality benchmark, 2026-11-08',
        'publication_clearance':'Not granted',
        'video_sha256':actual,'changed':changes})
    print('PASS: GILB-001 creative benchmark registered; stage Review; video NOT published.')
    print(f'PASS: {len(changes)} changes; assets, checks and source files linked. See exports/index.html')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('ERROR:',exc,file=sys.stderr)
        sys.exit(1)
