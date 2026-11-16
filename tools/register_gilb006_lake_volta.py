#!/usr/bin/env python3
"""Targeted, repeatable registry update: GILB-006 becomes the Lake Volta episode.

Owner direction (GilB, 2026-11-16):
  * "Lake Volta is GILB-006".
  * The former GILB-006 seed idea (youth employment) moves to GILB-007, unchanged, with its dataset.
  * "Everything has been checked and approved" (final cut, on-screen statements, sources).

Copies NO media and does NO git operations. The final files must already be in
stories/GILB-006/production/final/. Never marks the story Published.
"""
from __future__ import annotations
from pathlib import Path
import copy
import hashlib
import json
import sys
import registry

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-11-16'
SID, NEW_SID = 'GILB-006', 'GILB-007'
OLD_TITLE = 'Where are young Ghanaians struggling to find work?'
FINAL = f'stories/{SID}/production/final/'
VIDEO = 'GILB006_Lake_Volta_Largest_By_What_Final.mp4'
SHA = 'bf17dae3c42b56df52f0220429bd53a3d9b05cc233f8f1771fb7e037c81de0f9'
BYTES = 18962828
APPROVAL = 'GilB (owner): "everything has been checked and approved", 2026-11-16'


def sha256(p: Path) -> str:
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    rec6 = registry.story_path(ROOT, SID)
    rec7 = registry.story_path(ROOT, NEW_SID)
    old = json.loads(rec6.read_text(encoding='utf-8'))
    # ---- preflight: only run against the untouched seed record
    if rec7.exists():
        raise RuntimeError(f'{NEW_SID} already exists; reconcile before running.')
    if old['story'].get('title') != OLD_TITLE:
        if old['story'].get('title', '').startswith('Lake Volta'):
            print('NO CHANGES: GILB-006 is already the Lake Volta episode.')
            return
        raise RuntimeError('Unexpected GILB-006 record; reconcile before running.')
    for name in (VIDEO, VIDEO + '.sha256', 'GILB006_Lake_Volta_Largest_By_What_Final.en.srt', 'PROVENANCE.md',
                 'PRODUCTION_RELEASE_RECORD.md', 'RELEASE_QA_CHECKLIST.md'):
        if not (ROOT / FINAL / name).is_file():
            raise RuntimeError(f'Missing {FINAL}{name}')
    v = ROOT / FINAL / VIDEO
    if v.stat().st_size != BYTES or sha256(v) != SHA:
        raise RuntimeError('Final MP4 size/hash mismatch')
    if SHA not in (ROOT / FINAL / (VIDEO + '.sha256')).read_text(encoding='utf-8'):
        raise RuntimeError('Fingerprint file mismatch')

    # ---- 1. youth-employment seed idea -> GILB-007, content unchanged except ID + provenance note
    moved = copy.deepcopy(old)
    moved['story']['id'] = NEW_SID
    moved['story']['editorial_decision'] = (
        'Candidate. Moved unchanged from GILB-006 on 2026-11-16 by owner direction, when GILB-006 was '
        'assigned to the Lake Volta episode. DATA-006 keeps its permanent ID.')

    # ---- 2. GILB-006 = Lake Volta
    ds = [
        dict(id='DATA-006-LV-VRA', publisher='Volta River Authority (VRA)', name='Lake Volta surface area and storage capacity',
             source_url='https://www.vra.com/', reference_period='Full supply level (published reference figures)',
             granularity='Single reservoir', classification='Published reference figures',
             acquisition_status='Figures transcribed; source pages checked by owner, not archived in repo', acquired_on='',
             raw_file='', clean_file='', reuse_license='Facts cited with attribution',
             quality_next_check='Optionally archive the exact VRA page and retrieval date', owner='GilB'),
        dict(id='DATA-006-LV-ZRA', publisher='Zambezi River Authority (ZRA)', name='Lake Kariba surface area and storage capacity',
             source_url='https://www.zambezira.org/', reference_period='Full supply level (published reference figures)',
             granularity='Single reservoir', classification='Published reference figures',
             acquisition_status='Figures transcribed; source pages checked by owner, not archived in repo', acquired_on='',
             raw_file='', clean_file='', reuse_license='Facts cited with attribution',
             quality_next_check='Optionally archive the exact ZRA page and retrieval date', owner='GilB'),
        dict(id='DATA-006-LV-WLD', publisher='ILEC World Lake Database', name='Lake Volta and Lake Kariba entries (area, volume, mean depth)',
             source_url='https://wldb.ilec.or.jp/', reference_period='Database reference values',
             granularity='Per lake', classification='Published reference figures',
             acquisition_status='Figures transcribed; source pages checked by owner, not archived in repo', acquired_on='',
             raw_file='', clean_file='', reuse_license='Facts cited with attribution',
             quality_next_check='Published mean depths do not reconcile exactly with area x capacity (see ISS note)', owner='GilB'),
        dict(id='DATA-006-LV-NE', publisher='Natural Earth', name='1:10m lakes v5, admin-0 countries, rivers',
             source_url='https://www.naturalearthdata.com/', reference_period='v5',
             granularity='Vector polygons', classification='Map geometry',
             acquisition_status='Downloaded to production workspace; simplified copies in animations/remotion/src/geo',
             acquired_on='2026-11-15', raw_file='Production workspace _geo_raw/ (not in repo)',
             clean_file=f'stories/{SID}/animations/remotion/src/geo/', reuse_license='Public domain',
             quality_next_check='Lake Volta outline measures 7,994 km2 (94% of published 8,502)', owner='GilB'),
        dict(id='DATA-006-LV-OSM', publisher='OpenStreetMap contributors', name='Lake Kariba outline (relation 318675)',
             source_url='https://www.openstreetmap.org/relation/318675', reference_period='Retrieved 2026-11-15',
             granularity='Vector polygon', classification='Map geometry',
             acquisition_status='Downloaded to production workspace; simplified copy in animations/remotion/src/geo',
             acquired_on='2026-11-15', raw_file='Production workspace _geo_raw/ (not in repo)',
             clean_file=f'stories/{SID}/animations/remotion/src/geo/lakes.json', reuse_license='ODbL 1.0 — credit "© OpenStreetMap contributors" (shown on screen)',
             quality_next_check='Outline measures 5,371 km2 (96% of published 5,580)', owner='GilB'),
    ]
    # registry IDs must be PREFIX-<digits>: allocate permanent numeric DATA IDs
    used = set()
    for _, d in registry.load(ROOT)[0]:
        for coll in ('datasets', 'analyses', 'evidence', 'assets', 'posts', 'issues'):
            for r in d.get(coll, []):
                used.add(r.get('id'))
    for r in registry.load(ROOT)[1].get('records', []):
        used.add(r.get('id'))

    def new_id(prefix):
        nums = [int(x.split('-')[1]) for x in used if x and x.startswith(prefix + '-') and x.split('-')[1].isdigit()]
        rid = f'{prefix}-{max(nums + [0]) + 1:03d}'
        used.add(rid)
        return rid

    key = {}
    for d in ds:
        key[d['id']] = new_id('DATA')
        d['id'] = key[d['id']]
    VRA, ZRA, WLD, NE, OSM = (key[k] for k in ('DATA-006-LV-VRA', 'DATA-006-LV-ZRA', 'DATA-006-LV-WLD', 'DATA-006-LV-NE', 'DATA-006-LV-OSM'))

    an_id = new_id('AN')
    analyses = [dict(
        id=an_id, input_dataset_ids=f'{VRA},{ZRA},{WLD},{NE},{OSM}',
        question='Is Lake Volta the largest man-made lake — and by what measure?',
        approach='Compare published surface area and full-capacity storage for Lake Volta and Lake Kariba; draw both outlines on one Lambert azimuthal equal-area scale; simple arithmetic for the gap and the Polytank comparison.',
        finding='Volta is larger by surface area (8,502 vs 5,580 km2); Kariba stores more at full capacity (181 vs 148 km3, +33 km3). 148 trillion L / 5,000 L = 29.6 billion tanks.',
        run_date='2026-11-15', status='Complete — owner approved', output_file=FINAL + 'PROVENANCE.md',
        peer_check='Owner checked and approved 2026-11-16', supporting_evidence_id='',
        repro_notes='Geometry prep: animations/remotion/scripts/prep_geo.py. Animation: animations/remotion (Remotion 4.0.543), see PROVENANCE.md.',
        limitations='Published mean depths (18.8 m, 29.2 m) do not reconcile exactly with area x capacity (17.4 m, 32.4 m implied), likely different water levels/survey dates; the video never shows area x depth = volume and labels depth visuals as illustration.')]

    def ev(claim, dsid, url, qual):
        return dict(id=new_id('EV'), claim=claim, source_dataset_id=dsid, source_url=url, proof_file=FINAL + 'PROVENANCE.md',
                    verification_status='Verified', checked_by='GilB (owner)', checked_on=DATE, safe_to_publish='Yes',
                    approved_by='GilB', approval_date=DATE, qualification=qual)

    evidence = [
        ev('Lake Volta is the largest man-made lake in the world by surface area, about 8,500 km2.', VRA, 'https://www.vra.com/',
           'Published figure 8,502 km2, shown rounded. Qualified "by surface area" throughout.'),
        ev('At full capacity Lake Volta holds about 148 km3 (148 trillion litres).', VRA, 'https://www.vra.com/', 'Full-capacity figure; actual storage varies with water level.'),
        ev('Lake Kariba covers about 5,600 km2, a smaller area than Lake Volta.', ZRA, 'https://www.zambezira.org/', 'Published figure 5,580 km2, shown rounded.'),
        ev('At full capacity Lake Kariba holds about 181 km3 (181 trillion litres) — more than thirty cubic kilometres more than Lake Volta.', ZRA,
           'https://www.zambezira.org/', '181 - 148 = 33 km3; full-capacity figures.'),
        ev("Lake Volta's water would fill almost 30 billion 5,000-litre tanks.", VRA, 'https://www.vra.com/', 'Arithmetic: 148e12 L / 5,000 L = 29.6e9. Generic tank drawing, no brand implied.'),
        ev('Lake Kariba is on average about one and a half times as deep as Lake Volta.', WLD, 'https://wldb.ilec.or.jp/',
           'Published mean depths 18.8 m vs 29.2 m. Depth gauges labelled as published means, not surveyed profiles; containers labelled illustration.'),
    ]
    analyses[0]['supporting_evidence_id'] = ','.join(e['id'] for e in evidence)

    def asset(kind, version, name, path, status, notes):
        return dict(id=new_id('AS'), asset_type=kind, version=version, name=name, path=path, status=status, owner='GilB',
                    updated_on=DATE, quality_review='Owner checked and approved 2026-11-16', notes=notes)

    assets = [
        asset('Final video', 'v2 final', 'Lake Volta — Largest by what? (final master)', FINAL + VIDEO, 'Final — owner approved',
              f'1080x1920, 30 fps, 3,581 frames (119.4 s), H.264/AAC 48 kHz stereo, -14.2 LUFS, -1.7 dBTP. SHA-256 {SHA}'),
        asset('Master verification', 'v2', 'Final-video SHA-256', FINAL + VIDEO + '.sha256', 'Recorded', 'Byte-level fingerprint.'),
        asset('Captions', 'v1', 'English sidecar captions (approved script wording)', FINAL + 'GILB006_Lake_Volta_Largest_By_What_Final.en.srt',
              'Final — owner approved', '33 cues, not burned in.'),
        asset('Production record', 'v1', 'Sources, assets, method and audio provenance', FINAL + 'PROVENANCE.md', 'Recorded',
              'Narration hash, timing method, geometry licences, original music/SFX method, QA.'),
        asset('Animation source', 'v2', 'Remotion project (scenes, geometry, timing, music/SFX synthesis)', f'stories/{SID}/animations/remotion/',
              'Final', 'Narration and rendered WAV/MP4 files are not stored here (media kept out of Git except the final master).'),
        asset('Music and sound effects', 'v1', 'Original score and SFX synthesised in code', f'stories/{SID}/animations/remotion/audio/make_audio.py',
              'Final — owner approved', 'Original; no samples, stock audio or third-party licence.'),
        asset('Release QA checklist', 'v1', 'Release checks', FINAL + 'RELEASE_QA_CHECKLIST.md', 'Complete except publishing',
              'Public post URL/date to be recorded after publishing.'),
    ]
    issues = [dict(
        id=new_id('ISS'), type='Decision',
        description='Story ID: GILB-006 assigned to the Lake Volta episode by owner direction; former GILB-006 seed idea (youth employment) moved unchanged to GILB-007.',
        priority='Medium', owner='GilB', opened_on=DATE, due='', status='Resolved', resolution='Owner decision 2026-11-16.',
        next_action='None.'), dict(
        id=new_id('ISS'), type='Data limitation',
        description='Published mean depths and capacities do not reconcile exactly with surface areas (different water levels/survey dates likely).',
        priority='Low', owner='GilB', opened_on=DATE, due='', status='Resolved',
        resolution='Video avoids area x depth = volume; depth visuals labelled as published means / illustration. Owner approved.',
        next_action='Keep the qualification in any derivative content.')]

    new6 = {
        'story': {
            'id': SID,
            'title': 'Lake Volta — Largest by what?',
            'pillar': 'Ghana by region & district',
            'angle': 'Largest man-made lake by surface area vs by storage capacity (Lake Volta vs Lake Kariba)',
            'visual_format': 'Unpacked by GilB — data story',
            'audience': 'Ghanaian public and diaspora',
            'priority': 'High',
            'stage': 'Ready to publish',
            'editorial_decision': 'Final video, script, on-screen statements and sources checked and approved by GilB on 2026-11-16. Not yet published. Replaces the former GILB-006 seed idea (now GILB-007).',
            'claim_confidence': 'Owner-verified published reference figures (VRA, ZRA, ILEC World Lake Database). Mean-depth vs capacity inconsistency documented and qualified on screen.',
            'added_on': '2026-11-15',
            'target_publish': '',
            'owner': 'GilB',
            'next_action': 'Publish on TikTok, Instagram Reels and YouTube Shorts; then record post URLs and dates.',
            'blocker': '',
            'video_url': '',
            'production_status': 'Completed — owner approved',
            'production_completed_on': DATE,
            'final_master_file': FINAL + VIDEO,
            'final_master_sha256': SHA,
        },
        'datasets': ds, 'analyses': analyses, 'evidence': evidence, 'assets': assets, 'posts': [], 'issues': issues,
    }

    backup6 = rec6.read_text(encoding='utf-8')
    try:
        for sub in ('analysis', 'animations', 'data/clean', 'data/raw', 'evidence', 'scripts', 'storyboards'):
            (rec7.parent / sub).mkdir(parents=True, exist_ok=True)
            (rec7.parent / sub / '.gitkeep').touch()
        registry.dump(rec7, moved)
        registry.dump(rec6, new6)
        err = registry.validate(ROOT)
        if err:
            raise RuntimeError('Registry validation failed: ' + '; '.join(err))
        registry.build(ROOT)
    except Exception:
        rec6.write_text(backup6, encoding='utf-8')
        if rec7.exists():
            rec7.unlink()
        try:
            registry.build(ROOT)
        except Exception:
            pass
        raise
    registry.events(ROOT, 'story-id-reassigned', SID, {
        'from': OLD_TITLE, 'moved_to': NEW_SID, 'new_title': new6['story']['title'], 'authority': 'GilB owner direction 2026-11-16'})
    registry.events(ROOT, 'final-video-archived', SID, {
        'master': FINAL + VIDEO, 'sha256': SHA, 'stage': 'Ready to publish', 'approval': APPROVAL,
        'public_post_status': 'not published'})
    print(f'PASS: {NEW_SID} created from the former {SID} seed idea (unchanged content).')
    print(f'PASS: {SID} is now the Lake Volta episode, stage Ready to publish (not Published).')
    print('PASS: registry validated and exports rebuilt.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', str(exc), file=sys.stderr)
        raise SystemExit(1)
