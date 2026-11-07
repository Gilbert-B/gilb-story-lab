#!/usr/bin/env python3
"""Import GILB-001 research into the existing GilB registry; safe to run twice.

Copy the accompanying story research files and this tool into the repo, then
run `py -3 tools/import_gilb001.py` from the repository root.
It updates only GILB-001 and never marks findings safe to publish.
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
import re
import subprocess
import sys
import registry

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / 'stories/GILB-001'
RECORD = STORY / 'record.json'
DATA = STORY / 'data/raw/hearts_2025-26_results_transcribed.csv'
RESULTS = STORY / 'analysis/results.json'
RSSSF_URL = 'https://www.rsssf.org/tablesg/gha2026.html'
GFA_STATS_URL = 'https://ghanafa.org/ghana-premier-league-2025-26-statistics?amp=1'
GFA_FINAL_URL = 'https://www.ghanafa.org/official-ghana-premier-league-table-after-the-end-of-the-2025-26-season'
TODAY = date(2026,11,7).isoformat()  # Historical research capture date, not a live run timestamp.

def main():
    if not RECORD.is_file() or not DATA.is_file():
        raise RuntimeError('Run from a copy of the GilB repository with the supplied research files copied into stories/GILB-001/.')
    subprocess.run([sys.executable,str(STORY/'analysis/analyze_matches.py')],check=True)
    results=json.loads(RESULTS.read_text(encoding='utf-8'))
    if results['hearts']['clean_sheets']!=24 or results['hearts']['goalless_draws']!=13:
        raise RuntimeError('Research calculations changed; manual review required before registry update.')
    original=RECORD.read_text(encoding='utf-8')
    doc=json.loads(original)
    st=doc['story']
    if st['id']!='GILB-001' or st['stage'] in ('Ready to publish','Published'):
        raise RuntimeError('Unexpected story record/status; refusing research import.')
    # No existing approval may be downgraded or silently overwritten.
    for ev in doc.get('evidence',[]):
        if ev.get('safe_to_publish','No').strip().lower() in ('yes','true'):
            raise RuntimeError('Existing approved claim found: review manually before importing.')
    used={}
    for _,record in registry.load(ROOT)[0]:
        for collection,prefix in [('datasets','DATA'),('analyses','AN'),('evidence','EV'),('assets','AS'),('issues','ISS'),('posts','POST')]:
            for item in record.get(collection,[]):
                m=re.fullmatch(rf'{prefix}-(\d+)',item.get('id',''))
                if m:used[prefix]=max(used.get(prefix,0),int(m.group(1)))
    def fresh(prefix):
        used[prefix]=used.get(prefix,0)+1
        return f'{prefix}-{used[prefix]:03d}'
    changes=[]
    def dataset(name,source_url,publisher,classification,granularity,raw='',clean='',status='Web source located'):
        for ds in doc['datasets']:
            if ds.get('source_url')==source_url and ds.get('name')==name:return ds['id']
        obj={'id':fresh('DATA'),'publisher':publisher,'name':name,'source_url':source_url,
            'reference_period':'2025/26','granularity':granularity,'classification':classification,
            'acquisition_status':status,'acquired_on':TODAY if raw else '',
            'raw_file':raw,'clean_file':clean,'reuse_license':'RSSSF attribution required; verify reuse rules' if 'rsssf' in source_url else 'Link to source; verify any reuse terms',
            'quality_next_check':'Owner checks source and 3-5 matches; approval required before publishing',
            'owner':'GilB'}
        doc['datasets'].append(obj); changes.append(f'added {obj["id"]} source {name}')
        return obj['id']
    ds_rsssf=dataset('RSSSF manually transcribed 34 Hearts of Oak league results',RSSSF_URL,'RSSSF',
         'Secondary source; manually transcribed match results','34 matches',
         'stories/GILB-001/data/raw/hearts_2025-26_results_transcribed.csv',
         'stories/GILB-001/data/clean/hearts_2025-26_match_metrics.csv','Acquired')
    ds_gfa=dataset('Ghana FA 2025/26 season statistics',GFA_STATS_URL,'Ghana Football Association',
        'Official published report','Season summary')
    ds_final=dataset('Ghana FA final 2025/26 standings',GFA_FINAL_URL,'Ghana Football Association',
        'Official published report','League table')
    def merge_record(collection,id,fields):
        it=next((i for i in doc[collection] if i.get('id')==id),None)
        if it is None:
            raise RuntimeError(f'Existing record {id} missing; aborting to avoid duplicate research entries')
        for k,v in fields.items():
            if it.get(k)!=v:
                it[k]=v;changes.append(f'{id}.{k}')
    analysis_path='stories/GILB-001/analysis/research_findings.md'
    evidence_path='stories/GILB-001/evidence/source_register.md'
    merge_record('analyses','AN-001',{
        'input_dataset_ids':ds_rsssf,
        'finding':'34-match recount: 24 clean sheets (70.6%), including 13 goalless 0-0 draws; counts match official GFA season statistics.',
        'run_date':TODAY,'status':'Calculated; awaiting owner review','output_file':analysis_path,
        'peer_check':'Match totals reconcile to RSSSF final table; GFA season report confirms 24 clean sheets',
        'supporting_evidence_id':'EV-001','repro_notes':'Run py -3 stories/GILB-001/analysis/analyze_matches.py',
        'limitations':'Match scores only; no tactical or chance-quality evidence; owner approval still required'})
    merge_record('analyses','AN-002',{
        'input_dataset_ids':ds_rsssf,
        'finding':'13 W,15 D,6 L,25 GF,15 GA,54 points,3rd; Medeama 17 W,11 D,6 L,62 points: four additional wins in place of draws account for eight-point gap.',
        'run_date':TODAY,'status':'Calculated; awaiting owner review','output_file':analysis_path,
        'peer_check':'RSSSF final standings reconciled; Ghana FA reports Hearts 3rd, Medeama champions',
        'supporting_evidence_id':'EV-002','repro_notes':'Run py -3 stories/GILB-001/analysis/analyze_matches.py',
        'limitations':'Descriptive points arithmetic only; cannot infer causal football tactics'})
    def new_analysis(question,approach,finding,source_ids):
        if any(x.get('question')==question for x in doc['analyses']):return
        obj={'id':fresh('AN'),'input_dataset_ids':source_ids,'question':question,'approach':approach,
             'finding':finding,'run_date':TODAY,'status':'Calculated; awaiting owner review',
             'output_file':analysis_path,'peer_check':'Validated against 34 match scores and final table',
             'supporting_evidence_id':'','repro_notes':'Run py -3 stories/GILB-001/analysis/analyze_matches.py',
             'limitations':'Match-result descriptive analysis; not an explanation of tactics'}
        doc['analyses'].append(obj);changes.append(f'added {obj["id"]} {question}')
    new_analysis('How many Hearts clean sheets were 0-0 draws?',
        'Count opponent_goals=0 and hearts_goals=0 from 34 matches',
        '13 of 24 clean sheets (54.2%) were goalless draws, making 13 of 15 draws scoreless (86.7%).',ds_rsssf)
    merge_record('evidence','EV-001',{'source_dataset_id':ds_rsssf,'source_url':GFA_STATS_URL,
        'proof_file':evidence_path,'verification_status':'Reproduced; owner review pending',
        'safe_to_publish':'No','qualification':'Team clean sheets, not individual goalkeeper count; 34 match results agree with Ghana FA summary'})
    merge_record('evidence','EV-002',{'source_dataset_id':ds_final,'source_url':GFA_FINAL_URL,
        'proof_file':evidence_path,'verification_status':'Reproduced; owner review pending',
        'safe_to_publish':'No','qualification':'Match-by-match points reconcile to final table; owner approval still required'})
    def evidence(claim,ds,source,qualification):
        if any(x.get('claim')==claim for x in doc['evidence']):return
        obj={'id':fresh('EV'),'claim':claim,'source_dataset_id':ds,
             'source_url':source,'proof_file':evidence_path,
             'verification_status':'Reproduced; owner review pending',
             'checked_by':'','checked_on':'','safe_to_publish':'No',
             'approved_by':'','approval_date':'','qualification':qualification}
        doc['evidence'].append(obj);changes.append(f'added {obj["id"]}: {claim}')
    evidence('Hearts drew 13 games 0-0 in the 2025/26 league season',ds_rsssf,RSSSF_URL,
             'Computed from complete 34-game transcription, not an official GFA stat; owner spot-check required')
    evidence('Hearts and Medeama both lost six matches; Medeama had four more wins, four fewer draws and eight more points',ds_rsssf,RSSSF_URL,
             'League table comparison; descriptive arithmetic, not a causal claim')
    new_story_fields={'stage':'Verification','next_action':'Review results.json and research_findings.md; spot-check match scores and approve/select an editorial angle before scripting',
        'blocker':'Owner has not approved factual claims for publication; match-results attribution required',
        'claim_confidence':'Reproduced arithmetic; not approved'}
    for k,v in new_story_fields.items():
        if st.get(k)!=v:st[k]=v;changes.append(f'story.{k}')
    # Keep the previously opened issue until evidence has been approved.
    for issue in doc.get('issues',[]):
        if issue.get('id')=='ISS-001':
            msg='Match-level recount reproduces 24 clean sheets and GFA confirms. Owner review and editorial approval outstanding.'
            if issue.get('resolution')!=msg:issue['resolution']=msg;changes.append('ISS-001.resolution')
            next_action='Review the complete 34-match table; approve claims or request corrections.'
            if issue.get('next_action')!=next_action:issue['next_action']=next_action;changes.append('ISS-001.next_action')
    if not changes:
        print('NO CHANGES: GilB-001 research already registered.');return
    # Confirm whole repository validity before overwriting source of truth.
    registry.dump(RECORD,doc)
    problems=registry.validate(ROOT)
    if problems:
        RECORD.write_text(original,encoding='utf-8')
        raise RuntimeError('Registry validation failed; original restored: '+ '; '.join(problems))
    try:
        snapshot=registry.build(ROOT)
    except Exception:
        RECORD.write_text(original,encoding='utf-8');raise
    registry.events(ROOT,'import-research','GILB-001',{'research_date':TODAY,'source':'RSSSF/GFA results',
       'description':'Manual transcription; reproducible season statistics; owner approval pending',
       'changes':changes})
    print('PASS: imported GILB-001 research safely.')
    print(f'Updated {len(changes)} fields/records; current stage {st["stage"]}.')
    print('Registry dashboard:',ROOT/'exports/index.html')
    print('Snapshot:',snapshot)

if __name__=='__main__':
    try:main()
    except (RuntimeError,subprocess.CalledProcessError,json.JSONDecodeError) as exc:
        print('ERROR:',exc,file=sys.stderr);sys.exit(1)
