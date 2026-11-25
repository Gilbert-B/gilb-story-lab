"""Record GilB's owner approval of the claims verified on 25 Nov 2026, and move stories to Ready to publish.

Authority: GilB, 2026-11-25: "Everything is verified. Kindly update all of them."

* Every claim checked on 2026-11-25 (tools/verify_claims_2026_11_25.py) becomes safe_to_publish=Yes,
  approved by GilB on 2026-11-25.
* GILB-005's three district-level claims had been cross-checked by Claude via citypopulation.de only (the GSS
  district table was offline). They are recorded as Verified on the owner's confirmation, and that is stated
  in each claim's checked_by and qualification.
* GILB-002's four retired claims from the excluded first angle (EV-003, EV-006 to EV-008) are not public
  claims and are NOT approved. While they are in the evidence list, the registry keeps GILB-002 at Review.
* Stages: GILB-001, -003, -005, -008 move to Ready to publish. GILB-002 stays at Review.
"""
from __future__ import annotations
from pathlib import Path
import json
import registry

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-11-25'
READY = ['GILB-001', 'GILB-003', 'GILB-005', 'GILB-008']
STORIES = ['GILB-001', 'GILB-002', 'GILB-003', 'GILB-005', 'GILB-008']
EXCLUDED = 'Historical research only'
OWNER_NOTE = ' Recorded as Verified on owner confirmation (GilB, 2026-11-25); Claude did not open the GSS district table, which was offline.'
NEXT = 'Publish on the chosen platforms, then record each post URL and date (posts) before marking Published.'


def main():
    originals, changed = {}, {}
    for sid in STORIES:
        p = registry.story_path(ROOT, sid)
        originals[p] = p.read_text(encoding='utf-8')
        rec = json.loads(originals[p])
        approved = []
        for e in rec['evidence']:
            st = str(e.get('verification_status', ''))
            if st.startswith(EXCLUDED) or str(e.get('safe_to_publish', '')).lower() == 'yes':
                continue
            if st.startswith('Cross-checked'):
                e['verification_status'] = 'Verified'
                e['checked_by'] = 'GilB (owner) on confirmation; Claude cross-check via citypopulation.de'
                e['qualification'] = (e.get('qualification', '') + OWNER_NOTE).strip()
            if e['verification_status'] != 'Verified':
                raise RuntimeError(f'{sid} {e["id"]}: unexpected status {st!r}')
            e.update(safe_to_publish='Yes', approved_by='GilB', approval_date=DATE)
            approved.append(e['id'])
        s = rec['story']
        old_stage = s['stage']
        if sid in READY:
            s['stage'] = 'Ready to publish'
            s['next_action'] = NEXT
            s['claim_confidence'] = 'All narrated claims verified (2026-11-25) and approved by GilB (2026-11-25).'
        else:
            s['claim_confidence'] = ('All narrated claims verified (2026-11-25) and approved by GilB (2026-11-25). '
                                     'Four retired claims from the excluded first angle remain in the evidence list, unapproved.')
            s['next_action'] = ('Decide how to retire EV-003 and EV-006 to EV-008 (excluded first-angle claims) so the registry '
                                'allows Ready to publish; then publish and record post URLs.')
        if sid == 'GILB-005':
            for i in rec['issues']:
                if i.get('description', '').startswith('GILB005-GSS-DISTRICT-TABLE'):
                    i.update(status='Resolved', resolution='2026-11-25: owner (GilB) confirmed the figures as verified. '
                             'Claude could not open the GSS Vol 3A table (404); the figures match citypopulation.de.')
        changed[sid] = dict(approved=approved, stage_from=old_stage, stage_to=s['stage'])
        registry.dump(p, rec)
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
    for sid, c in changed.items():
        registry.events(ROOT, 'claims-approved', sid, {'approved_by': 'GilB', 'approval_date': DATE,
                        'authority': 'GilB owner direction 2026-11-25', 'evidence': c['approved']})
        if c['stage_from'] != c['stage_to']:
            registry.events(ROOT, 'stage-changed', sid, {'from': c['stage_from'], 'to': c['stage_to'],
                            'basis': 'All evidence verified and owner-approved'})
        print(f'{sid}: approved {len(c["approved"])} claims; stage {c["stage_from"]} -> {c["stage_to"]}')
    print('PASS: registry validated and exports rebuilt.')


if __name__ == '__main__':
    main()
