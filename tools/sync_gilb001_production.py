#!/usr/bin/env python3
"""Idempotent GILB-001 cumulative research/storyboard/production update.

From repository root: py -3 tools/sync_gilb001_production.py
Safe for the original six-story starter or a repo with earlier GILB-001 imports.
Preserves all evidence verification and publishing fields. Never changes them.
"""
from __future__ import annotations
from pathlib import Path
import json, subprocess, sys
import registry

ROOT=Path(__file__).resolve().parents[1]
RECORD=ROOT/'stories/GILB-001/record.json'
INTERACTIVE='stories/GILB-001/storyboards/interactive/index.html'
BLUEPRINT='stories/GILB-001/production/blueprint_v1.md'
SCENES='stories/GILB-001/production/scenes_v1.csv'
MANIFEST='stories/GILB-001/production/blueprint_manifest_v1.json'
CLAIMS='stories/GILB-001/production/claims_to_verify_v1.csv'
GATES='stories/GILB-001/production/quality_gates_v1.csv'
NARRATION='stories/GILB-001/scripts/narration_v1_approved.md'
STATIC='stories/GILB-001/storyboards/storyboard_v1.md'


def run_script(name):
    result=subprocess.run([sys.executable, str(ROOT/'tools'/name)],cwd=ROOT)
    if result.returncode:raise RuntimeError(f'{name} failed; stop and review output before pushing.')

def main():
    for rel in [INTERACTIVE,BLUEPRINT,SCENES,MANIFEST,CLAIMS,GATES,NARRATION,STATIC,
                'stories/GILB-001/analysis/results.json',
                'stories/GILB-001/data/raw/hearts_2025-26_results_transcribed.csv']:
        if not (ROOT/rel).is_file():
            raise RuntimeError(f'Missing {rel}. Extract the complete cumulative package into your repository root, not a nested folder.')
    if not RECORD.is_file():raise RuntimeError('No GILB-001 record.json: this update needs the existing GilB starter repository.')
    obj=json.loads(RECORD.read_text(encoding='utf-8'))
    if obj.get('story',{}).get('id')!='GILB-001':raise RuntimeError('Story identity mismatch')
    if obj['story']['stage'] in ('Published','Ready to publish','Archived'):
        raise RuntimeError('Story is in a final stage; do not overwrite it with this preproduction update.')

    # Fill in previously released research only where absent. Never force-rerun importer on live revised research.
    has_research=any(d.get('name','').startswith('RSSSF manually transcribed') and d.get('acquisition_status')=='Acquired'
                     for d in obj.get('datasets',[]))
    if not has_research:
        print('Research metadata not yet registered: importing the previously released GILB-001 research...',flush=True)
        run_script('import_gilb001.py')
        obj=json.loads(RECORD.read_text(encoding='utf-8'))
    if not (ROOT/'stories/GILB-001/analysis/results.json').exists():
        raise RuntimeError('Research results file missing after import')

    # Register the locked v1 narration / first static storyboard if not already registered.
    approved_script=any(a.get('asset_type')=='Narration script' and a.get('version')=='v1.0' and a.get('path')==NARRATION
                        for a in obj.get('assets',[]))
    if not approved_script:
        print('Registering previously approved narration and original static storyboard...',flush=True)
        run_script('log_gilb001_storyboard.py')
        obj=json.loads(RECORD.read_text(encoding='utf-8'))

    original=RECORD.read_text(encoding='utf-8')
    st=obj['story']
    if st.get('stage') in ('Ready to publish','Published','Archived'):
        raise RuntimeError('Final status detected; do not downgrade.')
    if any(p.get('publish_status')=='Published' for p in obj.get('posts',[])):
        raise RuntimeError('Published post exists. Review manually before preproduction update.')

    changes=[]
    def set_field(d,key,value,prefix):
        if d.get(key)!=value:
            d[key]=value; changes.append(f'{prefix}.{key}')

    for a in obj.get('assets',[]):
        if a.get('id')=='AS-002' and a.get('version')=='v1.0':
            set_field(a,'status','Retained as original static concept; interactive storyboard approved','AS-002')
            set_field(a,'quality_review','Owner approved the interactive storyboard v1.0; static storyboard retained for history','AS-002')

    def upsert_asset(path, asset_type, name, status, quality, notes):
        for a in obj.get('assets',[]):
            if a.get('path')==path:
                if a.get('asset_type')!=asset_type or a.get('version')!='v1.0':
                    raise RuntimeError(f'Existing asset at {path} has different identity/version; review manually.')
                # preserve improved statuses if user has subsequently approved blueprint independently
                if a.get('status') in ('Approved','Final','Published'):
                    return
                for key,val in {'name':name,'status':status,'quality_review':quality,'notes':notes}.items():
                    set_field(a,key,val,a['id'])
                return
        rid=registry.next_id(ROOT,'AS')
        # next_id sees on-disk IDs and must also account for in-memory assets inserted this call.
        present={a['id'] for a in obj.get('assets',[])}
        while rid in present:rid=f'AS-{int(rid.split("-")[1])+1:03d}'
        record={'id':rid,'asset_type':asset_type,'version':'v1.0','name':name,'path':path,
                'status':status,'owner':'GilB','updated_on':registry.today(),
                'quality_review':quality,'notes':notes}
        obj.setdefault('assets',[]).append(record);changes.append(f'added {rid} ({asset_type})')

    upsert_asset(INTERACTIVE,'Interactive storyboard','GILB-001 interactive visual storyboard v1.0',
                 'Visual design approved; factual claims pending',
                 'GilB owner approved visual design on 2026-11-07; publication evidence sign-off pending',
                 '14 scene portrait HTML prototype; source shotlist and preview included.')
    upsert_asset(BLUEPRINT,'Production blueprint','GILB-001 animation production blueprint v1.0',
                 'Draft for owner approval',
                 'Scene implementation plan created; owner has not yet approved production blueprint',
                 f'Timing/specs: {SCENES}; data manifest: {MANIFEST}; claims checklist: {CLAIMS}; QA gates: {GATES}.')

    set_field(st,'stage','Production','story')
    set_field(st,'editorial_decision','Narration v1.0 and interactive visual storyboard v1.0 approved; blueprint v1.0 drafted (pending approval)','story')
    set_field(st,'next_action','Review animation blueprint and then create a short 24-to-13 tile-motion proof; record voiceover timing before full video','story')
    # preserve blocker, claim_confidence and all evidence statuses intentionally.
    if not changes:
        print('NO CHANGES: interactive storyboard and blueprint already registered; no audit duplicate.'); return

    registry.dump(RECORD,obj)
    try:
        problems=registry.validate(ROOT)
        if problems:raise RuntimeError('Registry validation error: '+'; '.join(problems))
        registry.build(ROOT)
    except Exception:
        RECORD.write_text(original,encoding='utf-8')
        raise
    registry.events(ROOT,'approve-visual-storyboard-and-draft-blueprint','GILB-001',{
        'approval':'Interactive visual direction and narration approved by owner; no factual release approval',
        'blueprint':'v1.0 draft for owner review',
        'scenes':14,'estimated_duration_s':104,'changed':changes,
        'publication':'Not started'})
    print('PASS: Registry updated safely. Interactive storyboard approved; production blueprint draft logged.')
    print('PASS: All evidence remains untouched and no publication status was set.')
    print('Changed:',', '.join(changes))
    print('Preview:', ROOT/'exports/index.html')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('ERROR:',str(exc),file=sys.stderr)
        raise SystemExit(1)
