#!/usr/bin/env python3
"""Idempotently register the GILB-001 silent animation v2 for review.

Run at the root of an existing GilB Story Lab repo. Never approves claims,
publishes the video, or overwrites a pre-existing owner's asset review.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
import registry

ROOT=Path(__file__).resolve().parents[1]
STORY=ROOT/'stories/GILB-001/record.json'
REL='stories/GILB-001/production/full_animation_v2/GILB001_Full_Animation_Silent_Draft_v2.mp4'
CSV='stories/GILB-001/production/full_animation_v2/data/hearts_2025-26_chronological_matches.csv'
RENDERER='stories/GILB-001/production/full_animation_v2/source/render.py'

def main():
    for rel in [REL,CSV,RENDERER]:
        if not (ROOT/rel).is_file():raise RuntimeError(f'Missing {rel}. Copy the complete extracted ZIP contents into the REPOSITORY ROOT before running this script.')
    if not STORY.exists():raise RuntimeError('GILB-001 record.json is missing.')
    original=STORY.read_text(encoding='utf-8')
    obj=json.loads(original)
    st=obj['story']
    if st['id']!='GILB-001':raise RuntimeError('Wrong story record')
    if st['stage'] in ('Published','Ready to publish','Archived'):
        raise RuntimeError('Story has a final status. Do not downgrade it.')
    if any(p.get('publish_status')=='Published' for p in obj.get('posts',[])):
        raise RuntimeError('A published post exists; review manually.')
    assets=obj.setdefault('assets',[])
    old=next((a for a in assets if a.get('path')==REL),None)
    if old:
        print(f'NO CHANGES: v2 already registered as {old.get("id")}; preserving your status and review.')
        return
    rid=registry.next_id(ROOT,'AS')
    used={a['id'] for a in assets}
    while rid in used:rid=f'AS-{int(rid.split("-")[1])+1:03d}'
    assets.append({
        'id':rid,'asset_type':'Animation draft','version':'v2.0',
        'name':'GILB-001 full silent motion animation v2 (chronological matches)',
        'path':REL,'status':'Draft — owner review pending','owner':'GilB',
        'updated_on':registry.today(),'quality_review':'Technical validation complete; owner has not yet approved v2 or factual release',
        'notes':f'14 scenes / 104s / silent / 1080x1920 / match chronology data: {CSV}; editable code: {RENDERER}. V1 remains preserved.'
    })
    st['stage']='Production'
    st['next_action']='Review v2 chronological-match animation and league/wins benchmarks; request refinements or approve visuals. Record owner voiceover next. Publication fact-check still pending.'
    registry.dump(STORY,obj)
    try:
        errors=registry.validate(ROOT)
        if errors:raise RuntimeError('; '.join(errors))
        registry.build(ROOT)
    except Exception:
        STORY.write_text(original,encoding='utf-8')
        raise
    registry.events(ROOT,'log-animation-v2-review','GILB-001',{
        'asset_id':rid,'version':'v2.0','review_status':'awaiting owner review',
        'claim_approval':'unchanged','publication':'not started',
        'updates':'actual game-order tiles, 13 draw positions, five losses, relative league benchmark and win denominator 34'
    })
    print('PASS: Registered GILB-001 silent animation v2 for REVIEW; no claims approved or video published.')
    print('Updated dashboard: exports/index.html')

if __name__=='__main__':
    try:main()
    except Exception as ex:
        print(f'ERROR: {ex}',file=sys.stderr)
        sys.exit(1)
