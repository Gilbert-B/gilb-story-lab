"""Release fixes, 25 Nov 2026 (GilB: "Fix the things you can").

GILB-002: the four retired first-angle claims (EV-003, EV-006 to EV-008) are kept on file with
  public_scope=Excluded (never approvable; registry.validate enforces this), so the story can move to
  Ready to publish on its five approved claims. ISS-009 (owner sign-off) is resolved.
GILB-001: the final master is archived in production/final/ with its SHA-256, captions are added,
  ISS-005 is resolved and ISS-003 / ISS-004 record what is done and what remains.
"""
from __future__ import annotations
from pathlib import Path
import json
import registry

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-11-25'
G1_FINAL = 'stories/GILB-001/production/final/'
G1_MP4 = 'GILB001_Hearts_of_Oak_Final.mp4'
G1_SHA = 'fe3bc8ae4f2671d22d96c04ff7ad9eefffa11d92dfb61af78803c98621c801a4'


def main():
    originals = {}
    recs = {}
    for sid in ('GILB-001', 'GILB-002'):
        p = registry.story_path(ROOT, sid)
        originals[p] = p.read_text(encoding='utf-8')
        recs[sid] = (p, json.loads(originals[p]))

    # GILB-002
    p, r = recs['GILB-002']
    excluded = []
    for e in r['evidence']:
        if str(e.get('verification_status', '')).startswith('Historical research only'):
            e['public_scope'] = 'Excluded'
            excluded.append(e['id'])
    assert excluded == ['EV-003', 'EV-006', 'EV-007', 'EV-008'], excluded
    for i in r['issues']:
        if i['id'] == 'ISS-009':
            i.update(status='Resolved', resolution='2026-11-25: all five narrated claims verified against NCA bulletins '
                     'and approved by GilB. See evidence/CLAIM_VERIFICATION_2026-11-25.md.')
    s = r['story']
    g2_from = s['stage']
    s['stage'] = 'Ready to publish'
    s['claim_confidence'] = ('All five narrated claims verified (2026-11-25) and approved by GilB (2026-11-25). '
                             'Retired first-angle claims EV-003, EV-006 to EV-008 kept on file as Excluded.')
    s['next_action'] = 'Publish on the chosen platforms, then record each post URL and date (posts) before marking Published.'

    # GILB-001
    p1, r1 = recs['GILB-001']
    asset_ids = [registry.next_id(ROOT, 'AS')]
    asset_ids.append(f'AS-{int(asset_ids[0].split("-")[1]) + 1:03d}')
    r1['assets'] += [
        dict(id=asset_ids[0], name='Final master video', path=G1_FINAL + G1_MP4,
             status=f'Final master archived {DATE}: 1080x1920, 24 fps, 99.6 s, H.264/AAC 48 kHz stereo, '
                    f'-14.0 LUFS integrated, -1.2 dBFS peak. SHA-256 {G1_SHA}. '
                    'Copied unchanged from production/full_animation_v2/ (dated 2026-11-09, the production approval date).'),
        dict(id=asset_ids[1], name='English captions (SRT)', path=G1_FINAL + 'GILB001_Hearts_of_Oak_Final.en.srt',
             status=f'Created {DATE}: 22 cues, one per approved script line, timed from speech-recognition word timestamps '
                    'of the final master (all script words matched).'),
    ]
    for i in r1['issues']:
        if i['id'] == 'ISS-005':
            i.update(status='Resolved', resolution=f'{DATE}: master archived at {G1_FINAL}{G1_MP4} (in Git) with SHA-256 '
                     f'{G1_SHA}; measured 1080x1920, 24 fps, 99.6 s, -14.0 LUFS.')
        if i['id'] == 'ISS-003':
            i.update(resolution=f'{DATE} progress: match data verified and claims approved; captions created; loudness measured '
                     '(-14.0 LUFS). Still open: provenance/licence record for the background music and sound effects, '
                     'and a phone playback check (legibility, safe areas).',
                     next_action='GilB to record where the music and sound effects came from and their licence, and to watch '
                                 'the final on a phone; then close.')
        if i['id'] == 'ISS-004':
            i.update(resolution=f'{DATE} note: the editable renderer for the v2 animation is in '
                     'production/full_animation_v2/source/render.py. The final (99.6 s, narrated) was retimed from it; '
                     'the retimed project and audio session are not in the repository.')
    s1 = r1['story']
    s1['final_master_file'] = G1_FINAL + G1_MP4
    s1['final_master_sha256'] = G1_SHA

    for sid, (p, r) in recs.items():
        registry.dump(p, r)
    try:
        err = registry.validate(ROOT)
        if err:
            raise RuntimeError('Registry validation failed: ' + '; '.join(err))
        registry.build(ROOT)
    except Exception:
        for p, text in originals.items():
            p.write_text(text, encoding='utf-8')
        try:
            registry.build(ROOT)
        except Exception:
            pass
        raise
    registry.events(ROOT, 'evidence-scoped', 'GILB-002', {'excluded': excluded, 'basis': 'Retired first-angle claims; not in the final video',
                                                          'authority': 'GilB owner direction 2026-11-25'})
    registry.events(ROOT, 'stage-changed', 'GILB-002', {'from': g2_from, 'to': 'Ready to publish',
                                                        'basis': 'All public claims verified and owner-approved'})
    registry.events(ROOT, 'final-video-archived', 'GILB-001', {'master': G1_FINAL + G1_MP4, 'sha256': G1_SHA,
                                                               'captions': G1_FINAL + 'GILB001_Hearts_of_Oak_Final.en.srt',
                                                               'assets_added': asset_ids})
    print('GILB-002: excluded', excluded, '; stage', g2_from, '-> Ready to publish')
    print('GILB-001: assets', asset_ids, '; ISS-005 resolved; ISS-003/ISS-004 updated')
    print('PASS: registry validated and exports rebuilt.')


if __name__ == '__main__':
    main()
