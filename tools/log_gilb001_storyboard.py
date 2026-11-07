#!/usr/bin/env python3
"""Register the GILB-001 approved script and draft storyboard without touching research/evidence.

Run from the repo root: py -3 tools/log_gilb001_storyboard.py
This script is idempotent and assumes previous research import already completed.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import registry

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / 'stories/GILB-001'
RECORD = STORY / 'record.json'
SCRIPT = 'stories/GILB-001/scripts/narration_v1_approved.md'
STORYBOARD = 'stories/GILB-001/storyboards/storyboard_v1.md'
SHOTS = 'stories/GILB-001/storyboards/shots_v1.csv'
PREREQ = STORY / 'analysis/results.json'

def main():
    if not RECORD.exists():
        raise RuntimeError('GILB-001 record.json not found; copy into an existing GilB repository.')
    for rel in [SCRIPT, STORYBOARD, SHOTS]:
        if not (ROOT/rel).is_file():
            raise RuntimeError(f'Required asset missing: {rel}')
    if not PREREQ.is_file():
        raise RuntimeError('Research import missing (analysis/results.json). Import the GILB-001 research package first; do not change story stage prematurely.')
    previous=RECORD.read_text(encoding='utf-8')
    doc=json.loads(previous)
    st=doc['story']
    if st['id'] != 'GILB-001':
        raise RuntimeError('Record is not GILB-001')
    if st['stage'] in ('Ready to publish','Published'):
        raise RuntimeError('Unexpected publication status; stop and review with owner')
    assets={a['id']:a for a in doc.get('assets',[])}
    changes=[]
    for aid, expected in [
       ('AS-001',dict(asset_type='Narration script',version='v1.0',name='GILB-001 — approved narration',path=SCRIPT,status='Editorial wording approved; claims pending',quality_review='Approved by owner for wording; factual publication sign-off pending',notes='Versioned script. Do not silently edit v1.0.')),
       ('AS-002',dict(asset_type='Storyboard',version='v1.0',name='GILB-001 — draft visual storyboard',path=STORYBOARD,status='Draft for owner visual review',quality_review='Owner visual sign-off pending',notes='Detailed shots at '+SHOTS+'; estimated ~93s, final timing after recorded narration.')),
    ]:
       if aid not in assets:
           raise RuntimeError(f'Missing expected asset {aid}: refuse to create duplicate')
       for k,v in expected.items():
           if assets[aid].get(k)!=v:
               assets[aid][k]=v
               changes.append(f'{aid}.{k}')
    for k,v in dict(stage='Storyboarding',editorial_decision='Narration v1.0 approved; storyboard draft',next_action='Review storyboard_v1.md and shots_v1.csv for scene pacing and reveal transitions before building motion proof').items():
        if st.get(k)!=v:
            st[k]=v;changes.append(f'story.{k}')
    if not changes:
        print('NO CHANGES: approved script and storyboard already registered.');return
    registry.dump(RECORD,doc)
    try:
        errors=registry.validate(ROOT)
        if errors:raise RuntimeError('; '.join(errors))
        registry.build(ROOT)
    except Exception:
        RECORD.write_text(previous,encoding='utf-8')
        raise
    registry.events(ROOT,'storyboard-draft','GILB-001',{'version':'v1.0','description':'Owner-approved narration and draft visual storyboard; claims not approved for publication','changes':changes})
    print('PASS: GILB-001 narration and storyboard registered; evidence approvals unchanged.')
    print('Updated registry and dashboard; review before committing.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('ERROR:',exc,file=sys.stderr)
        sys.exit(1)
