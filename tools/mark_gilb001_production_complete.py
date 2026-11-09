#!/usr/bin/env python3
"""Mark GILB-001's video PRODUCTION complete, without approving publication.

Safe for starter and updated GilB Story Registry repositories. Idempotent.
Only changes GILB-001; never edits evidence verification or publishing posts.
Python 3.11+; uses existing tools/registry.py module.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import registry

ROOT = Path(__file__).resolve().parents[1]
SID = 'GILB-001'
REC = ROOT / 'stories' / SID / 'record.json'
CLOSEOUT = 'stories/GILB-001/production/production_closeout_v1/PRODUCTION_COMPLETION_RECORD.md'
QA = 'stories/GILB-001/production/production_closeout_v1/RELEASE_GATE_CHECKLIST.md'
APPROVAL_DATE = '2026-11-09'
MARKER = 'GILB-001-PRODUCTION-CLOSEOUT-2026-11-09'


def main():
    for rel in (CLOSEOUT, QA):
        if not (ROOT / rel).is_file():
            raise RuntimeError(f'Missing {rel}. Copy the FULL update package into repository root first.')
    if not REC.is_file():
        raise RuntimeError('GILB-001/record.json not found. Run from GilB story repository.')
    original = REC.read_text(encoding='utf-8')
    obj = json.loads(original)
    story = obj.get('story', {})
    if story.get('id') != SID:
        raise RuntimeError('Incorrect record ID: must be GILB-001.')

    changes = []
    def change(dest, field, val, detail):
        if dest.get(field) != val:
            dest[field] = val
            changes.append(detail)

    # The parent stage remains Review because evidence clearance and publishing are separate.
    # Never downgrade a story that has progressed to Ready to publish, Published or Archived.
    current_stage = story.get('stage')
    if current_stage not in ('Review', 'Ready to publish', 'Published', 'Archived'):
        change(story, 'stage', 'Review', f'stage {current_stage} -> Review')

    change(story, 'production_status', 'Completed — owner approved', 'explicit production completion recorded')
    change(story, 'production_completed_on', APPROVAL_DATE, 'production completion date recorded')
    change(story, 'creative_benchmark', 'GILB-001 benchmark RC1 (owner approved)', 'creative benchmark recorded')
    if current_stage not in ('Ready to publish','Published','Archived'):
        change(story, 'editorial_decision',
            'PRODUCTION COMPLETE — approved by GilB 2026-11-09. Creative benchmark locked; publication clearance pending.',
            'editorial decision set to production completed')
        change(story, 'next_action',
            'Production complete. Archive original master and editable Claude project; complete factual, rights and final release QA; then schedule launch.',
            'next action is release QA, not production')
        change(story, 'blocker',
            'No production blocker. Publication checks remain open; do not mark Published before posting.',
            'production/release blockers distinguished')

    assets = obj.setdefault('assets', [])
    prior = next((a for a in assets if MARKER in str(a.get('notes','')) or a.get('path') == CLOSEOUT), None)
    if prior is None:
        rid = registry.next_id(ROOT,'AS')
        prior = {
            'id': rid,
            'asset_type':'Production milestone',
            'version':'Closeout v1.0',
            'name':'GILB-001 — Production Complete (Owner Approved)',
            'path':CLOSEOUT,
            'status':'Completed — owner approved',
            'owner':'GilB',
            'updated_on':APPROVAL_DATE,
            'quality_review':'Creative approval received. Final factual/rights/archive review tracked separately.',
            'notes':MARKER+'; video production finished; not a publication approval.'
        }
        assets.append(prior)
        changes.append(f'production milestone asset {rid} created')
    else:
        for k,v in (
            ('status','Completed — owner approved'),
            ('quality_review','Creative approval received. Final factual/rights/archive review tracked separately.'),
            ('notes', MARKER+'; video production finished; not a publication approval.')
        ):
            change(prior,k,v,f'production milestone {k} updated')

    # Update only a known uncompleted final-video placeholder. Do not overwrite paths,
    # hashes, metadata or status of an already approved/archived master asset.
    for a in assets:
        if a is prior: continue
        if (a.get('asset_type') == 'Final video' and a.get('status') in ('Not started','Planned','In progress')):
            change(a,'status','Production completed — original master owned by GilB; archive pending',
                   f'final-video placeholder {a.get("id")} updated')
            change(a,'quality_review','Approved as creative benchmark; publication review separate',
                   f'final-video placeholder {a.get("id")} approval recorded')

    # If the prior export task is still open, close only that task (the owner has
    # confirmed that the ORIGINAL file had the proper dimensions).
    for iss in obj.get('issues', []):
        if 'BENCHMARK-RC1-EXPORT' in str(iss.get('description','')) and iss.get('status') != 'Closed':
            change(iss,'status','Closed',f'false re-export issue {iss.get("id")} closed')
            change(iss,'resolution',
                   'Owner confirmed original master was correct resolution; smaller chat-upload copy was compressed. No re-export required.',
                   f'export issue {iss.get("id")} resolution recorded')
            change(iss,'next_action','',f'export issue {iss.get("id")} next action cleared')

    if not changes:
        print('NO CHANGES: GILB-001 production completion already registered; no duplicate event.')
        return

    registry.dump(REC,obj)
    try:
        problems = registry.validate(ROOT)
        if problems: raise RuntimeError('Registry validation failed: '+ '; '.join(problems))
        registry.build(ROOT)
    except Exception:
        REC.write_text(original, encoding='utf-8')
        try: registry.build(ROOT)
        except Exception: pass
        raise
    registry.events(ROOT,'production-completed',SID,{
        'milestone': MARKER,
        'production_status':'Completed — owner approved',
        'production_completed_on':APPROVAL_DATE,
        'story_stage':story.get('stage'),
        'publication_status':'unchanged (not automatically published)',
        'evidence_approvals':'unchanged',
        'changes':changes
    })
    print('PASS: GILB-001 PRODUCTION COMPLETED (owner approved).')
    print('PASS: Publication status and evidence approvals remain unchanged.')
    print('PASS: Registry exports and dashboard rebuilt. Changes:',len(changes))

if __name__ == '__main__':
    try:main()
    except Exception as e:
        print('ERROR:',str(e),file=sys.stderr)
        raise SystemExit(1)
