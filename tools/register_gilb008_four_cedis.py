#!/usr/bin/env python3
"""Targeted, repeatable registry update: create GILB-008 "Four Cedis in a Hundred".

Owner direction (GilB, 2026-11-25):
  * "completed Gilb006 can you update my github and website" — final video delivered and approved.
  * Story ID: a NEW story GILB-008 (GILB-006 stays Lake Volta, GILB-007 stays youth employment).
    The production files carry working names GILB006 / GILB007; they are kept as delivered.

Copies NO media and does NO git operations. The final files must already be in
stories/GILB-008/production/final/. Never marks the story Published.
Stage is Review (not Ready to publish) until every claim is Verified, as registry.validate requires.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import registry

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-11-25'
SID = 'GILB-008'
TITLE = 'Four Cedis in a Hundred'
BASE = f'stories/{SID}/'
FINAL = BASE + 'production/final/'
VIDEO = 'GILB008_Four_Cedis_In_A_Hundred_Final.mp4'
SHA = '122506aa1e73c0fb6c0024200a9b45758d01e4e1c7a227fc373623973727811e'
BYTES = 10556217
PACK = BASE + 'evidence/GILB006_Research_Pack.md'
DATA = BASE + 'data/clean/GILB006_Data.csv'
APPROVAL = 'GilB (owner): "completed Gilb006", 2026-11-25'
REVIEW = 'Owner delivered the final video as completed, 2026-11-25'

QLFS = 'https://statsghana.gov.gh/gssmain/fileUpload/pressrelease/2025%20Q1-3%20QLFS%20Report.pdf'
GDP = 'https://gna.org.gh/2026/03/ghanas-economy-grows-by-six-per-cent-in-2025-gss/'
MPR = 'https://www.bog.gov.gh/wp-content/uploads/2026/02/Monetary-Policy-Report-January-2026-1-2.pdf'
JOY = 'https://www.myjoyonline.com/credit-to-public-sector-contracted-by-25-in-2025-to-gh%C2%A24-8bn-bog/'
AKOLGO = 'https://www.africamultiple.uni-bayreuth.de/pool/dokumente/Selected-Publications/Akolgo-2025-Banking-and__.pdf'


def sha256(p: Path) -> str:
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    rec = registry.story_path(ROOT, SID)
    if rec.exists():
        if json.loads(rec.read_text(encoding='utf-8'))['story'].get('title') == TITLE:
            print(f'NO CHANGES: {SID} is already {TITLE}.')
            return
        raise RuntimeError(f'{SID} exists with a different story; reconcile before running.')
    for name in (VIDEO, VIDEO + '.sha256', 'GILB008_Four_Cedis_In_A_Hundred_Final.en.srt', 'PROVENANCE.md',
                 'RELEASE_QA_CHECKLIST.md'):
        if not (ROOT / FINAL / name).is_file():
            raise RuntimeError(f'Missing {FINAL}{name}')
    for rel in (PACK, DATA):
        if not (ROOT / rel).is_file():
            raise RuntimeError(f'Missing {rel}')
    v = ROOT / FINAL / VIDEO
    if v.stat().st_size != BYTES or sha256(v) != SHA:
        raise RuntimeError('Final MP4 size/hash mismatch')

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

    def dataset(publisher, name, url, period, gran, cls, status, qcheck, licence='Facts cited with attribution'):
        return dict(id=new_id('DATA'), publisher=publisher, name=name, source_url=url, reference_period=period,
                    granularity=gran, classification=cls, acquisition_status=status, acquired_on='',
                    raw_file='', clean_file=DATA, reuse_license=licence, quality_next_check=qcheck, owner='GilB')

    transcribed = 'Figures transcribed in the research pack; source PDF not archived in repo'
    D_QLFS = dataset('Ghana Statistical Service (GSS)', 'Quarterly Labour Force Survey, Q1–Q3 2025 report (employment by sector)',
                     QLFS, 'Q3 2025', 'National, by sector', 'Official survey statistics', transcribed,
                     'Archive the report PDF')
    D_GDP = dataset('Ghana Statistical Service (GSS), as reported by Ghana News Agency',
                    '2025 annual GDP release, 17 Mar 2026 (sector shares and real growth)', GDP, '2025 (provisional)',
                    'National, by sector', 'Official national accounts (press report)', transcribed,
                    'Confirm in the GSS release itself whether 22.8% is the real or nominal share, and the 6.8% / 6.0% growth figures')
    D_MPR = dataset('Bank of Ghana (BoG)', 'Monetary Policy Report, January 2026 (Figure 6.1 credit by sector; gross loans)',
                    MPR, 'Dec 2024 and Dec 2025 (loans outstanding)', 'Deposit money banks, by sector',
                    'Central-bank report (chart labels + text)', transcribed,
                    'Confirm the 4.7% and 4.3% shares in a BoG data table (read from chart labels; shares add to 99.9%)')
    D_JOY = dataset('MyJoyOnline, reporting Bank of Ghana data', 'Credit to public sector contracted by 25% in 2025 (gross loans GH¢111.0bn)',
                    JOY, 'Dec 2025', 'Deposit money banks, total', 'Press report of central-bank data', transcribed,
                    'Cross-check against the BoG report')
    D_AK = dataset('Akolgo (2025), Forum for Social Economics', 'Banking and Monetary Policy in Ghana, Table 1 (agriculture share of private-sector credit)',
                   AKOLGO, '1999–2023', 'Annual, national', 'Peer-reviewed study (researched, not used in the video)',
                   'Long-trend series transcribed to data/clean/GILB006_Agri_Credit_Share_1999_2026.csv',
                   'Check the column against the supplementary appendix (PDF extraction)')
    D_AK['clean_file'] = BASE + 'data/clean/GILB006_Agri_Credit_Share_1999_2026.csv'
    ds = [D_QLFS, D_GDP, D_MPR, D_JOY, D_AK]

    # The registry only allows safe_to_publish=Yes on a Verified claim. Claims the research pack still
    # lists as reported / chart reading / computed keep that status, and their approval stays pending
    # until the open checks are done (ISS below), even though the owner approved the final video.
    def ev(claim, d, status, qual):
        ok = status == 'Verified'
        return dict(id=new_id('EV'), claim=claim, source_dataset_id=d['id'], source_url=d['source_url'], proof_file=PACK,
                    verification_status=status, checked_by='GilB (owner), with research pack', checked_on=DATE,
                    safe_to_publish='Yes' if ok else 'Pending — open check (research pack §8)',
                    approved_by='GilB' if ok else '', approval_date=DATE if ok else '', qualification=qual)

    evidence = [
        ev('Out of every hundred working Ghanaians, about thirty-seven work in agriculture.', D_QLFS, 'Verified',
           '37.2% of employed persons aged 15+, Q3 2025 (GSS QLFS).'),
        ev("That's around five million people.", D_QLFS, 'Verified', 'About 5.0 million employed in agriculture, Q3 2025 (GSS QLFS).'),
        ev('Out of every hundred cedis of economic output produced in 2025, about twenty-three came from agriculture.', D_GDP,
           'Reported by GSS (via GNA); release not yet checked directly',
           '22.8% of GDP, 2025 provisional. Real vs nominal share still to confirm in the GSS release.'),
        ev("At the end of 2025, out of every hundred cedis Ghana's banks had outstanding in loans, just over four cedis were in agriculture.",
           D_MPR, 'Chart reading; BoG data table not yet checked',
           '4.3% of total bank credit outstanding, Dec 2025 (BoG MPR Jan 2026, Fig 6.1). Total credit, not private-sector credit (4.5%), not new-lending flows.'),
        ev('In 2025, agriculture grew by 6.8 percent, faster than the economy\'s overall growth of 6 percent.', D_GDP,
           'Reported by GSS (via GNA); release not yet checked directly', 'Real growth, 2025 provisional.'),
        ev('Bank loans to agriculture actually went up.', D_MPR, 'Computed',
           '≈ GH¢4.49bn (Dec 2024) → ≈ GH¢4.77bn (Dec 2025), ≈ +6%; share × gross loans. Direction holds across the shares\' rounding bands (+4% to +9%).'),
        ev('But bank loans overall went up faster.', D_JOY, 'Reported by BoG', 'Gross loans GH¢111.0bn at Dec 2025, +16.2% y/y.'),
        ev("So agriculture's share fell, from 4.7 percent to 4.3 percent.", D_MPR, 'Chart reading; BoG data table not yet checked',
           'Dec 2024 → Dec 2025, share of total bank credit outstanding.'),
        ev('Now, these are bank loans, not every source of financing agriculture relies on.', D_MPR, 'Scope note (framing, not a figure)',
           'BoG figures cover deposit money banks only; rural/community banks, microfinance, input credit and outgrower schemes are outside the measure.'),
    ]

    analyses = [dict(
        id=new_id('AN'), input_dataset_ids=','.join(d['id'] for d in ds[:4]),
        question='Is agriculture the backbone of Ghana\'s economy — by jobs, by output and by bank loans?',
        approach='Three shares for the same year (2025): employment (GSS QLFS Q3 2025), GDP (GSS 2025 release) and bank credit outstanding '
                 '(BoG MPR Jan 2026). Growth comparison from the GSS release; agriculture\'s cedi amount computed as share × gross loans, with a rounding-band check.',
        finding='Agriculture is 37.2% of jobs and 22.8% of output but 4.3% of banks\' outstanding loans (Dec 2025). Agriculture grew 6.8% vs 6.0% for the economy; '
                'bank loans to agriculture rose ≈ +6% while all bank loans rose 16.2%, so the share fell from 4.7% to 4.3%.',
        run_date='2026-11-23', status='Complete — owner approved', output_file=PACK,
        peer_check='Research pack consolidated 2026-11-25; owner delivered final video as completed 2026-11-25',
        supporting_evidence_id=','.join(e['id'] for e in evidence),
        repro_notes='Figures and computations: evidence/GILB006_Research_Pack.md §3–4; data/clean/GILB006_Data.csv.',
        limitations='BoG shares read from chart labels; GDP share and growth taken from a press report of the GSS release; bank loans cover deposit money banks only. '
                    'Bad-loan ratios, causes, targets, June 2026 data and GIRSAL researched but deliberately left out (research pack §6–7).')]

    def asset(kind, version, name, path, status, notes):
        return dict(id=new_id('AS'), asset_type=kind, version=version, name=name, path=path, status=status, owner='GilB',
                    updated_on=DATE, quality_review=REVIEW, notes=notes)

    assets = [
        asset('Final video', 'V1 final', 'Four Cedis in a Hundred (final master)', FINAL + VIDEO, 'Final — owner approved',
              f'1080x1920, 30 fps, 109.6 s, H.264/AAC 48 kHz stereo, -14 LUFS, -1.2 dBTP. Delivered as GILB006_Four_Cedis_Final_V1.mp4. SHA-256 {SHA}'),
        asset('Master verification', 'V1', 'Final-video SHA-256', FINAL + VIDEO + '.sha256', 'Recorded', 'Byte-level fingerprint.'),
        asset('Captions', 'v1', 'English sidecar captions (approved script wording)', FINAL + 'GILB008_Four_Cedis_In_A_Hundred_Final.en.srt',
              'Generated from word timings', '28 cues, one per script line, timed from the voice word timestamps + 0.5 s lead-in; not burned in.'),
        asset('Research pack', 'v1', 'Claim-by-claim verification, computations, definitions, sources', PACK, 'Recorded',
              'Includes the final narration, open checks and the material researched but left out.'),
        asset('Storyboard', 'V3', 'Synced storyboard and shot list', BASE + 'storyboards/GILB-006_Storyboard_V3_Shotlist.md', 'Final',
              'Synced to the voice master word timestamps.'),
        asset('Narration timing', 'v1', 'Voice master word timestamps (speech recognition)', BASE + 'scripts/GILB006_Narration_Word_Timings.json',
              'Recorded', 'Voice master GILB007_Four_Cedis_Voice_Master_V1.wav (1:47.5); the WAV is not stored in Git.'),
        asset('Music and sound effects', 'V1', 'Original score "Field & Ledger", SFX and mix scripts', BASE + 'production/audio/',
              'Final — owner approved', 'Original, synthesised in code. WAV stems (126 MB) kept outside Git in GILB006_Audio_V1.zip; '
              'the scripts depend on helper modules (synth, dsp) that were not delivered, so they are a record, not a runnable build.'),
        asset('Production record', 'v1', 'Sources, assets and audio provenance', FINAL + 'PROVENANCE.md', 'Recorded', 'File-name history, hashes, QA.'),
        asset('Release QA checklist', 'v1', 'Release checks', FINAL + 'RELEASE_QA_CHECKLIST.md', 'Complete except publishing',
              'Public post URL/date to be recorded after publishing.'),
    ]

    def issue(kind, desc, prio, status, resolution, nxt):
        return dict(id=new_id('ISS'), type=kind, description=desc, priority=prio, owner='GilB', opened_on=DATE, due='',
                    status=status, resolution=resolution, next_action=nxt)

    issues = [
        issue('Decision', 'Story ID: the episode was produced under working IDs GILB006 (video, research, audio) and GILB007 (voice). '
              'GILB-006 is Lake Volta and GILB-007 is youth employment, so the episode is registered as a new story GILB-008.',
              'Medium', 'Resolved', 'Owner decision 2026-11-25. Delivered file names kept unchanged except the final master.', 'None.'),
        issue('Data limitation', 'Open checks from the research pack §8: confirm BoG credit shares in a data table (not only chart labels); confirm real vs nominal '
              'GDP share and the growth figures in the GSS release itself; find BoG\'s cedi amount for agricultural loans; check newer MPRs; archive source PDFs.',
              'Medium', 'Open', '', 'Complete the checks before any derivative content quotes more precise figures.'),
    ]

    new = {
        'story': {
            'id': SID, 'title': TITLE, 'pillar': 'Money & everyday Ghana',
            'angle': 'Agriculture is the backbone of jobs (37%) and output (23%), but just over 4 cedis in every 100 of bank loans — even in a year it outgrew the economy',
            'visual_format': 'Unpacked by GilB — data story', 'audience': 'Ghanaian public and diaspora', 'priority': 'High',
            'stage': 'Review',
            'editorial_decision': f'Final video delivered and approved by GilB on {DATE} ("completed"). Not yet published. Stage held at Review because the registry '
                                  'only allows Ready to publish once every claim is Verified; 7 of 9 claims await the research-pack open checks.',
            'claim_confidence': 'Jobs figures verified in the GSS report; GDP figures as reported from the GSS release; BoG credit shares read from report chart labels. '
                                'Open checks recorded in the research pack and issues.',
            'added_on': DATE, 'target_publish': '', 'owner': 'GilB',
            'next_action': 'Complete the research-pack open checks (BoG data table, GSS release) and mark claims Verified; then Ready to publish, publish and record post URLs.',
            'blocker': '', 'video_url': '', 'production_status': 'Completed — owner approved', 'production_completed_on': DATE,
            'final_master_file': FINAL + VIDEO, 'final_master_sha256': SHA,
        },
        'datasets': ds, 'analyses': analyses, 'evidence': evidence, 'assets': assets, 'posts': [], 'issues': issues,
    }
    try:
        registry.dump(rec, new)
        err = registry.validate(ROOT)
        if err:
            raise RuntimeError('Registry validation failed: ' + '; '.join(err))
        registry.build(ROOT)
    except Exception:
        if rec.exists():
            rec.unlink()
        try:
            registry.build(ROOT)
        except Exception:
            pass
        raise
    registry.events(ROOT, 'story-created', SID, {'title': TITLE, 'authority': 'GilB owner direction 2026-11-25',
                                                 'note': 'Produced under working IDs GILB006/GILB007'})
    registry.events(ROOT, 'final-video-archived', SID, {'master': FINAL + VIDEO, 'sha256': SHA, 'stage': 'Review',
                                                        'approval': APPROVAL, 'public_post_status': 'not published'})
    print(f'PASS: {SID} {TITLE} created, stage Review (production complete; not Published).')
    print('PASS: registry validated and exports rebuilt.')


if __name__ == '__main__':
    main()
