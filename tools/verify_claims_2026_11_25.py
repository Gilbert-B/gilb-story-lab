"""Record the 25 Nov 2026 independent claim verification for GILB-001, -002, -003, -005 and -008.

Authorised by GilB on 2026-11-25 ("check and update. Everything").

What it does, per story:
  * marks each video claim that was checked against its source as verification_status 'Verified'
    (checked_by Claude, checked_on 2026-11-25), and adds claims that the video makes but the record lacked;
  * leaves safe_to_publish / approved_by for the owner: verification is not editorial approval,
    so no story moves to Ready to publish here;
  * resolves issues the check closed, adds source datasets, and appends one 'claims-verified' event per story.

Detailed proof for every claim is in stories/<ID>/evidence/CLAIM_VERIFICATION_2026-11-25.md.
Run from the repository root:  py -3 tools/verify_claims_2026_11_25.py
"""
from __future__ import annotations
from pathlib import Path
import json
import registry

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-11-25'
BY = 'Claude (independent source check, at GilB request)'
PENDING = 'Pending owner approval'
REPORT = 'stories/{sid}/evidence/CLAIM_VERIFICATION_2026-11-25.md'

# Each story entry: updates to existing evidence, new evidence, new datasets, issue resolutions, next action.
PLAN: dict = json.loads((Path(__file__).with_suffix('.json')).read_text(encoding='utf-8'))


def main():
    originals = {}
    stories = {}
    for sid in PLAN:
        p = registry.story_path(ROOT, sid)
        originals[p] = p.read_text(encoding='utf-8')
        stories[sid] = (p, json.loads(originals[p]))

    # Allocate IDs once, against the whole registry, before writing anything.
    def alloc(prefix, n):
        start = int(registry.next_id(ROOT, prefix).split('-')[1])
        return [f'{prefix}-{start + i:03d}' for i in range(n)]

    n_ds = sum(len(PLAN[s].get('new_datasets', [])) for s in PLAN)
    n_ev = sum(len(PLAN[s].get('new_evidence', [])) for s in PLAN)
    n_is = sum(len(PLAN[s].get('new_issues', [])) for s in PLAN)
    ds_ids, ev_ids, iss_ids = iter(alloc('DATA', n_ds)), iter(alloc('EV', n_ev)), iter(alloc('ISS', n_is))

    summary = {}
    for sid, plan in PLAN.items():
        p, rec = stories[sid]
        report = REPORT.format(sid=sid)
        ds_map = {}
        for d in plan.get('new_datasets', []):
            d = dict(d)
            key = d.pop('key')
            d['id'] = next(ds_ids)
            ds_map[key] = d['id']
            rec['datasets'].append(d)

        by_id = {e['id']: e for e in rec['evidence']}
        for eid, upd in plan.get('update_evidence', {}).items():
            e = by_id[eid]
            upd = dict(upd)
            if upd.get('source_dataset_id') in ds_map:
                upd['source_dataset_id'] = ds_map[upd['source_dataset_id']]
            e.update(upd)
            if upd.get('verification_status') == 'Verified':
                e.update(checked_by=BY, checked_on=DATE, proof_file=report)
                if str(e.get('safe_to_publish', '')).lower() != 'yes':
                    e.update(safe_to_publish=PENDING, approved_by='', approval_date='')

        added = []
        for ne in plan.get('new_evidence', []):
            ne = dict(ne)
            dkey = ne.pop('dataset', None)
            did = ds_map.get(dkey, dkey) if dkey else ''
            e = dict(id=next(ev_ids), claim=ne['claim'], source_dataset_id=did, source_url=ne['source_url'],
                     proof_file=report, verification_status=ne.get('verification_status', 'Verified'),
                     checked_by=BY, checked_on=DATE, safe_to_publish=PENDING, approved_by='', approval_date='',
                     qualification=ne.get('qualification', ''))
            rec['evidence'].append(e)
            added.append(e['id'])

        iss = {i['id']: i for i in rec['issues']}
        for iid, upd in plan.get('issues', {}).items():
            iss[iid].update(upd)
        for ni in plan.get('new_issues', []):
            ni = dict(ni, id=next(iss_ids))
            rec['issues'].append(ni)
            plan.setdefault('issues', {})[ni['id']] = {'status': ni['status']}

        s = rec['story']
        for k, v in plan.get('story', {}).items():
            s[k] = v
        summary[sid] = dict(updated=sorted(plan.get('update_evidence', {})), added=added,
                            datasets=list(ds_map.values()), issues=plan.get('issues', {}))
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

    for sid, sm in summary.items():
        registry.events(ROOT, 'claims-verified', sid, {
            'checked_on': DATE, 'checked_by': BY, 'report': REPORT.format(sid=sid),
            'evidence_updated': sm['updated'], 'evidence_added': sm['added'], 'datasets_added': sm['datasets'],
            'issues_changed': {k: v.get('status') for k, v in sm['issues'].items()},
            'approval': 'Owner approval still required; stage unchanged (Review)'})
        print(f'{sid}: updated {len(sm["updated"])} evidence, added {sm["added"]}, datasets {sm["datasets"]}')
    print('PASS: registry validated and exports rebuilt.')


if __name__ == '__main__':
    main()
