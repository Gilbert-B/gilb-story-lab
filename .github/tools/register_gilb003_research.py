#!/usr/bin/env python3
"""Conservatively register the owner-approved GILB-003 topic and initial research stage.
Requires the existing gilb-story-lab repository and its tools/registry.py.
Refuses unexpected IDs, published records, or records with existing non-placeholder
GILB-003/GILB-004 work. NEVER changes evidence approvals, datasets, analyses, or posts.
"""
from pathlib import Path
import sys,json
import registry
ROOT=Path(__file__).resolve().parents[1]
DATE='2026-11-11'
MARK='GILB003-STORY-ASSIGNMENT-2026-11-11'
PATHS={s:ROOT/'stories'/s/'record.json' for s in ('GILB-003','GILB-004')}

def main():
    evidence=ROOT/'stories'/'GILB-003'/'analysis'/'GILB-003_Analysis_and_Verification_v1.docx'
    if not evidence.is_file():raise RuntimeError('First copy the research package into the repo; report missing.')
    if any(not p.is_file() for p in PATHS.values()):
        raise RuntimeError('One or both story record.json files are missing. Do not create records from guesses; inspect the repository.')
    originals={sid:p.read_text(encoding='utf-8') for sid,p in PATHS.items()}
    records={sid:json.loads(orig) for sid,orig in originals.items()}
    for sid,d in records.items():
        story=d.get('story',{})
        if story.get('id')!=sid:raise RuntimeError('Incorrect story ID in '+str(PATHS[sid]))
        if story.get('stage') in ('Published','Archived','Ready to publish','Review'):
            raise RuntimeError(sid+' is not a safe idea-stage record; manual review required')
        if d.get('posts') and any(p.get('actual_date') or str(p.get('publish_status','')).lower()=='published' for p in d['posts']):
            raise RuntimeError(sid+' contains a publication record; aborting')
        # Real tracked assets or a non-placeholder analysis mean this is not an untouched placeholder.
        for field in ('assets','analyses','datasets','evidence'):
            for x in d.get(field,[]):
                combined=' '.join(str(x.get(k,'')) for k in ('path','raw_file','clean_file','output_file','proof_file','run_date','acquired_on'))
                if any(v in combined.lower() for v in ('g ilb','music','listening','spotify','audiomack','shazam','momo','wallet')):
                    raise RuntimeError(sid+' may contain pre-existing work: '+field+'. Preserve and reconcile manually.')
    changes=[]
    def update(sid,m):
        story=records[sid]['story']
        for k,v in m.items():
            if story.get(k)!=v:
                story[k]=v;changes.append(sid+'.'+k)
    update('GILB-003',{
        'title':"Ghana's Sleeping Wallets",
        'stage':'Analysis',
        'editorial_decision':'Owner selected Sleeping Wallets for GILB-003 on 2026-11-11. Previous GILB-004 concept label is historical, not an additional story. Script not approved.',
        'next_action':'Review BoG Table 11 analysis at stories/GILB-003/analysis/GILB-003_Analysis_and_Verification_v1.docx; approve editorial hook before script and storyboard.',
        'blocker':'Publication claims, final script, design and release QA not approved. Research relies on BoG September 2026 source; recheck future revisions.',
        'claim_confidence':'BoG source and arithmetic checked; independent cross-release audit and owner claim sign-off pending.'
    })
    update('GILB-004',{
        'title':"Ghana's Music Listening Habits",
        'stage':'Idea',
        'editorial_decision':'Research deferred on 2026-11-11. Local pre-reassignment documents may carry GILB-003 in their filenames; preserve originals and note historical ID.',
        'next_action':'Deferred. Preserve pre-reassignment music feasibility research; resume only when owner authorises.',
        'blocker':'None — deferred by owner, no active production task.'
    })
    if not changes:
        print('NO CHANGES — story assignment already registered; no duplicate event.');return
    try:
        for sid,p in PATHS.items():registry.dump(p,records[sid])
        errors=registry.validate(ROOT)
        if errors:raise RuntimeError('Validation failed: '+'; '.join(map(str,errors)))
        registry.build(ROOT)
    except Exception:
        for sid,p in PATHS.items():p.write_text(originals[sid],encoding='utf-8')
        try:registry.build(ROOT)
        except Exception:pass
        raise
    registry.events(ROOT,'gilb003-topic-assignment-and-initial-research','GILB-003',{
      'marker':MARK,'when':DATE,'selected':'Ghana\'s Sleeping Wallets',
      'deferred':'GILB-004 Ghana music listening',
      'research_report':'stories/GILB-003/analysis/GILB-003_Analysis_and_Verification_v1.docx',
      'production_approved':False,'publication_approved':False,'evidence_approvals':'untouched',
      'changes':changes})
    print('PASS — GILB-003 assigned Sleeping Wallets; GILB-004 music deferred; no evidence or publication approvals modified.')
    print('PASS — validation and dashboard build completed.')
if __name__=='__main__':
 try:main()
 except Exception as e:
  print('ERROR:',str(e),file=sys.stderr)
  raise SystemExit(1)
