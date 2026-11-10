#!/usr/bin/env python3
"""Archive GILB-002's approved final MP4 and record video PRODUCTION completed.

Does not publish content, approve factual evidence, or edit GILB-001.
Safe to run repeatedly: no duplicate assets or completion events.
Designed for GilB's existing tools/registry.py (Python 3.11+).
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
import registry

ROOT = Path(__file__).resolve().parents[1]
SID = 'GILB-002'
DATE = '2026-11-10'
REL = 'stories/GILB-002/production/final/'
VIDEO = 'GILB002_v4_Score_B_Cinematic_Pulse_v2_Lower_Bed.mp4'
MASTER = REL + VIDEO
RECORD = REL + 'PRODUCTION_COMPLETION_RECORD.md'
CHECKLIST = REL + 'RELEASE_QA_CHECKLIST.md'
FINGERPRINT = REL + 'GILB002_FINAL_VIDEO_SHA256.txt'
MARKER = 'GILB002-PRODUCTION-COMPLETED-2026-11-10'
EXPECTED_HASH = 'e1531ea10e55dd79145855b5fd337935480903b743e593aad608e1a4891bd4ec'
EXPECTED_BYTES = 7404510


def main() -> None:
    record_path = ROOT / 'stories' / SID / 'record.json'
    if not record_path.is_file():
        raise RuntimeError('Missing stories/GILB-002/record.json. Copy to your gilb-story-lab repository root.')
    for rel in (MASTER, RECORD, CHECKLIST, FINGERPRINT):
        if not (ROOT / rel).is_file():
            raise RuntimeError(f'Missing required closeout file: {rel}. Copy the full ZIP contents.')
    video_path = ROOT / MASTER
    if video_path.stat().st_size != EXPECTED_BYTES:
        raise RuntimeError('The master MP4 size differs from the owner-approved file. Stopping.')
    digest = hashlib.file_digest(video_path.open('rb'), 'sha256').hexdigest()
    if digest != EXPECTED_HASH:
        raise RuntimeError('The master MP4 SHA-256 does not match the owner-approved file. Stopping.')
    if EXPECTED_HASH not in (ROOT / FINGERPRINT).read_text(encoding='utf-8'):
        raise RuntimeError('The fingerprint file disagrees with the final master.')

    original = record_path.read_text(encoding='utf-8')
    d = json.loads(original)
    story = d.get('story', {})
    if story.get('id') != SID:
        raise RuntimeError('Wrong story ID; expected GILB-002.')
    # Never reinterpret an existing publishing milestone as only production-complete.
    if story.get('stage') in ('Published', 'Archived') or any(
        str(p.get('publish_status', '')).lower() in ('published','live','posted') or p.get('actual_date')
        for p in d.get('posts', [])
    ):
        raise RuntimeError('Repository already records a published/archived GILB-002. Reconcile manually; no changes made.')

    changes = []
    def put(obj: dict, key: str, value: str, why: str):
        if obj.get(key) != value:
            obj[key] = value
            changes.append(why)

    # The registry has no separate Production Complete stage. Review means release QA is outstanding.
    if story.get('stage') != 'Ready to publish':
        put(story, 'stage', 'Review', 'stage -> Review')
    put(story, 'production_status', 'Completed — owner approved', 'production milestone')
    put(story, 'production_completed_on', DATE, 'production completion date')
    put(story, 'final_master_file', MASTER, 'approved master asset path')
    put(story, 'final_master_sha256', EXPECTED_HASH, 'approved master SHA-256')
    if story.get('stage') == 'Review':
        put(story, 'next_action', 'Production complete. Finish final factual/rights/platform checks and archive editable sources; schedule as part of three-video launch.', 'next action -> release QA')
        put(story, 'blocker', 'No production blocker. Public release requires separate factual, rights and platform sign-off.', 'production vs release separation')
        put(story, 'editorial_decision', 'Final GILB-002 cut approved by owner on 2026-11-10. Production complete; not publication approval.', 'owner creative approval')

    assets = d.setdefault('assets', [])
    specifications = 'Owner-approved original: H.264 1080x1920 24 fps; AAC stereo 48 kHz; duration 121.54 seconds; SHA-256 '+EXPECTED_HASH+'.'
    rows = [
        (MASTER, 'Final video', 'GILB-002 — Approved final master (Score B, Cinematic Pulse v2 Lower Bed)', 'Final / score B v2', 'Completed — owner approved', specifications+' Keep as immutable original; factual/rights release checks pending.'),
        (RECORD, 'Production milestone', 'GILB-002 — Production Completion Record', 'Closeout v1.0', 'Completed — owner approved', MARKER+'; production finished, not published.'),
        (CHECKLIST, 'Release QA checklist', 'GILB-002 — Remaining release checks', 'Release gate v1.0', 'Pending publication checks', 'Production complete; release checks remain open.'),
        (FINGERPRINT, 'Master verification', 'GILB-002 — Final master SHA-256', 'v1.0', 'Recorded', 'SHA-256 of the exact user-selected final MP4.'),
    ]
    for path, kind, title, version, status, note in rows:
        asset = next((x for x in assets if x.get('path') == path), None)
        if asset is None:
            asset = {
                'id': registry.next_id(ROOT, 'AS'), 'asset_type': kind, 'version': version,
                'name': title, 'path': path, 'status': status, 'owner': 'GilB',
                'updated_on': DATE,
                'quality_review': 'Owner creative approval recorded. Publication evidence and rights approval not granted here.',
                'notes': note,
            }
            # next_id scans on-disk registry, so reserve newly assigned IDs against in-memory assets too.
            used = {str(x.get('id','')) for x in assets}
            if asset['id'] in used:
                i = int(asset['id'].split('-')[-1])
                while f'AS-{i:03d}' in used: i += 1
                asset['id'] = f'AS-{i:03d}'
            assets.append(asset)
            changes.append(f'asset {asset["id"]}: {path}')
        else:
            put(asset, 'status', status, f'asset status {path}')
            if path == MASTER and EXPECTED_HASH not in str(asset.get('notes', '')):
                put(asset, 'notes', note, 'master hash metadata')

    if not changes:
        print('NO CHANGES: GILB-002 production completion is already recorded; no duplicate event.')
        return
    registry.dump(record_path, d)
    try:
        errors = registry.validate(ROOT)
        if errors: raise RuntimeError('Registry validation failed: '+'; '.join(errors))
        registry.build(ROOT)
    except Exception:
        record_path.write_text(original, encoding='utf-8')
        try: registry.build(ROOT)
        except Exception: pass
        raise
    registry.events(ROOT, 'gilb002-production-completed', SID, {
        'marker': MARKER, 'production_completed_on': DATE,
        'production_status': 'Completed — owner approved',
        'final_master_file': MASTER, 'sha256': EXPECTED_HASH,
        'story_stage': story['stage'],
        'publication_status': 'unchanged: not marked published',
        'evidence_approvals': 'unchanged',
        'changes': changes,
    })
    print('PASS: GILB-002 production marked completed — owner approved.')
    print('PASS: Approved MP4 fingerprint matched: '+EXPECTED_HASH)
    print('PASS: No posts or factual evidence approvals were changed.')
    print('PASS: Registry dashboard and exports regenerated.')

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print('ERROR:', str(exc), file=sys.stderr)
        raise SystemExit(1)
