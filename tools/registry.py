#!/usr/bin/env python3
"""GilB Registry: source JSON -> validated CSV + interactive HTML dashboard.
Standard-library only, compatible with Python 3.11+ and GitHub Actions.
The record.json files are authoritative; exports are generated and should not be edited.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
KINDS = {
    'dataset': ('datasets', 'DATA'), 'analysis': ('analyses', 'AN'),
    'evidence': ('evidence', 'EV'), 'asset': ('assets', 'AS'),
    'post': ('posts', 'POST'), 'issue': ('issues', 'ISS')
}
COLUMNS = {
 'STORIES': ['id','title','pillar','angle','visual_format','audience','priority','stage','editorial_decision','claim_confidence','added_on','target_publish','owner','dataset_count','analysis_count','evidence_count','asset_count','next_action','blocker','video_url'],
 'DATA SOURCES': ['id','story_id','publisher','name','source_url','reference_period','granularity','classification','acquisition_status','acquired_on','raw_file','clean_file','reuse_license','quality_next_check','owner'],
 'ANALYSIS LOG': ['id','story_id','input_dataset_ids','question','approach','finding','run_date','status','output_file','peer_check','supporting_evidence_id','repro_notes','limitations'],
 'EVIDENCE': ['id','story_id','claim','source_dataset_id','source_url','proof_file','verification_status','checked_by','checked_on','safe_to_publish','approved_by','approval_date','qualification'],
 'PRODUCTION': ['id','story_id','asset_type','version','name','path','status','owner','updated_on','quality_review','notes'],
 'PUBLISHING': ['id','story_id','platform','video_version','scheduled_date','actual_date','post_url','publish_status','views','avg_watch_time_s','completion_rate','likes','comments','shares','saves','followers_gained','learning'],
 'ISSUES & DECISIONS': ['id','story_id','type','description','priority','owner','opened_on','due','status','resolution','next_action']
}
SHEET_FOR_COLLECTION = {'datasets':'DATA SOURCES','analyses':'ANALYSIS LOG','evidence':'EVIDENCE','assets':'PRODUCTION','posts':'PUBLISHING','issues':'ISSUES & DECISIONS'}
STAGES = ('Idea','Research queued','Research underway','Data cleaning','Analysis','Verification','Storyboarding','Production','Review','Ready to publish','Published','On hold','Archived')

def today(): return datetime.now(timezone.utc).date().isoformat()
def timestamp(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def dump(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def files(root): return sorted((root/'stories').glob('GILB-*/record.json'))
def load(root):
    stories=[]
    for p in files(root):
        obj=json.loads(p.read_text(encoding='utf-8'))
        stories.append((p,obj))
    global_path=root/'registry'/'global.json'
    g=json.loads(global_path.read_text(encoding='utf-8')) if global_path.exists() else {'records':[]}
    return stories,g

def validate(root):
    stories,g=load(root)
    errors=[]; seen_s=set(); seen_ids=set()
    for path,data in stories:
        s=data.get('story',{}); sid=s.get('id','')
        if not re.fullmatch(r'GILB-\d{3,}',sid): errors.append(f'{path}: invalid Story ID {sid!r}')
        if path.parent.name!=sid: errors.append(f'{sid}: folder and Story ID mismatch')
        if sid in seen_s: errors.append(f'{sid}: duplicate Story ID')
        seen_s.add(sid)
        if not s.get('title','').strip(): errors.append(f'{sid}: missing title')
        if s.get('stage') not in STAGES: errors.append(f'{sid}: unknown stage {s.get("stage")!r}')
        dataset_ids=set()
        for d in data.get('datasets',[]): dataset_ids.add(d.get('id',''))
        for collection,prefix in [(v[0],v[1]) for v in KINDS.values()]:
            arr=data.get(collection,[])
            if not isinstance(arr,list): errors.append(f'{sid}: {collection} must be a list');continue
            for r in arr:
                rid=r.get('id','')
                if not re.fullmatch(rf'{prefix}-\d{{3,}}',rid): errors.append(f'{sid}: invalid {collection} ID {rid!r}')
                if rid in seen_ids: errors.append(f'{sid}: duplicate record ID {rid}')
                seen_ids.add(rid)
        for a in data.get('analyses',[]):
            ids=a.get('input_dataset_ids','')
            if isinstance(ids,str): ids=[x.strip() for x in ids.split(',') if x.strip()]
            for did in ids:
                if did not in dataset_ids:errors.append(f'{sid}: analysis {a.get("id")} references unknown {did}')
        for e in data.get('evidence',[]):
            if e.get('source_dataset_id') and e['source_dataset_id'] not in dataset_ids:
                errors.append(f'{sid}: evidence {e.get("id")} references unknown dataset')
            if str(e.get('safe_to_publish','')).casefold() in ('yes','true'):
                required=('claim','verification_status','checked_by','checked_on','approved_by','approval_date')
                missing=[k for k in required if not e.get(k)]
                if e.get('verification_status') != 'Verified': errors.append(f'{sid}: {e.get("id")} approved without Verified status')
                if not(e.get('source_url') or e.get('proof_file')): missing.append('source_url or proof_file')
                if missing: errors.append(f'{sid}: {e.get("id")} safe-to-publish missing {", ".join(missing)}')
        for d in data.get('datasets',[]):
            if str(d.get('acquisition_status','')).lower() in ('acquired','downloaded') and not d.get('raw_file'):
                errors.append(f'{sid}: {d.get("id")} marked acquired without raw_file')
        if s.get('stage') in ('Ready to publish','Published'):
            ev=data.get('evidence',[])
            if not ev or any(str(e.get('safe_to_publish','')).lower()!='yes' for e in ev):
                errors.append(f'{sid}: cannot mark ready/published with missing or unsafe evidence')
        if s.get('stage')=='Published':
            if not any(p.get('publish_status')=='Published' and p.get('post_url') and p.get('actual_date') for p in data.get('posts',[])):
                errors.append(f'{sid}: Published story needs at least one dated published post URL')
    for x in g.get('records',[]):
        rid=x.get('id','')
        if rid in seen_ids: errors.append(f'global record ID {rid} duplicates story record')
        seen_ids.add(rid)
        if x.get('story_id') not in (None,'','ALL') and x.get('story_id') not in seen_s:
            errors.append(f'global record {rid} references unknown story')
    return errors

def as_cell(x):
    if x is None:return ''
    if isinstance(x,list):return ', '.join(str(v) for v in x)
    if isinstance(x,(dict,tuple)):return json.dumps(x,ensure_ascii=False)
    return str(x)
def build(root):
    errors=validate(root)
    if errors:raise ValueError('VALIDATION FAILED:\n- '+'\n- '.join(errors))
    stories,g=load(root)
    rows={x:[] for x in COLUMNS}
    for p,data in stories:
        s=data['story'].copy();sid=s['id']
        for typ in ('datasets','analyses','evidence','assets'):s[f'{"asset" if typ=="assets" else "dataset" if typ=="datasets" else "analysis" if typ=="analyses" else "evidence"}_count']=len(data.get(typ,[]))
        rows['STORIES'].append(s)
        for collection,sheet in SHEET_FOR_COLLECTION.items():
            for r in data.get(collection,[]): rows[sheet].append({'story_id':sid,**r})
    rows['ISSUES & DECISIONS'].extend(g.get('records',[]))
    out=root/'exports';out.mkdir(parents=True,exist_ok=True)
    for sheet,columns in COLUMNS.items():
        dest=out/(sheet.replace(' ','_').replace('&','AND')+'.csv')
        with dest.open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.writer(f);writer.writerow(columns)
            for r in rows[sheet]: writer.writerow([as_cell(r.get(k,'')) for k in columns])
    stages={s['story']['stage']:0 for _,s in stories}
    for _,d in stories: stages[d['story']['stage']]+=1
    summary={
        'stories':len(stories),
        'published_stories':sum(s['story']['stage']=='Published' for _,s in stories),
        'datasets_acquired':sum(str(d.get('acquisition_status','')).lower() in ('acquired','downloaded') for _,s in stories for d in s.get('datasets',[])),
        'verified_approved_claims':sum(e.get('verification_status')=='Verified' and str(e.get('safe_to_publish','')).lower()=='yes' for _,s in stories for e in s.get('evidence',[])),
        'open_issues':sum(r.get('status') not in ('Closed','Resolved') for r in rows['ISSUES & DECISIONS'] if r.get('type')!='Decision'),
        'stages':dict(sorted(stages.items()))
    }
    dump(out/'dashboard.json',summary)
    write_html(out/'index.html',rows['STORIES'],summary,stories)
    lines=['# GilB Registry Snapshot','',f'**Stories:** {summary["stories"]}  |  **Published:** {summary["published_stories"]}  |  **Datasets acquired:** {summary["datasets_acquired"]}  |  **Claims approved:** {summary["verified_approved_claims"]}','','| ID | Story | Stage | Next action |','|---|---|---|---|']
    for s in rows['STORIES']:lines.append('| '+' | '.join(str(s.get(k,'')).replace('|','\\|') for k in ('id','title','stage','next_action'))+' |')
    (out/'snapshot.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return summary

def write_html(dest,story_rows,summary,all_stories):
    esc=html.escape
    css='''body{font-family:Inter,system-ui,Segoe UI,sans-serif;background:#101c2b;color:#f3f0e8;max-width:1150px;margin:auto;padding:34px 22px}h1{margin-bottom:0}.sub{color:#aebdc8}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:25px 0}.card{background:#1d2c40;border:1px solid #32465c;border-radius:14px;padding:18px}.num{color:#d9ab56;font-size:30px;font-weight:750}table{width:100%;border-collapse:collapse;background:#19283a;font-size:14px}th,td{padding:12px;border-bottom:1px solid #34475a;text-align:left;vertical-align:top}th{color:#d9ab56}tr:hover{background:#23374b}input{padding:11px 14px;border-radius:10px;width:min(94%,420px);font-size:15px;border:1px solid #64748b;background:#fff;color:#102030;margin:0 0 20px}a{color:#61c9c1}small{color:#aebdc8}.tag{color:#e5bb6a}footer{padding:24px 0;color:#aebdc8}'''
    cards=''.join(f'<div class="card"><div class="num">{summary[k]}</div><div>{label}</div></div>' for k,label in [('stories','Stories'),('published_stories','Published'),('datasets_acquired','Datasets acquired'),('verified_approved_claims','Approved claims'),('open_issues','Open issues')])
    body=[]
    for s in story_rows:
        sid=esc(str(s['id']));source=esc('../stories/'+sid+'/record.json',quote=True)
        cells=[f'<a href="{source}">{sid}</a>',esc(str(s.get('title',''))),f'<span class="tag">{esc(str(s.get("pillar","")))}</span>',esc(str(s.get('stage',''))),esc(str(s.get('next_action','')))]
        body.append('<tr>'+''.join(f'<td>{c}</td>' for c in cells)+'</tr>')
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GilB Story Registry</title><style>{css}</style></head><body><h1>GilB <span style="color:#d9ab56">Story Registry</span></h1><p class="sub">Evidence-led stories, from idea to published video. Local read-only view generated from story records.</p><div class="cards">{cards}</div><label for="q">Find a story</label><br><input id="q" placeholder="Search ID, topic, stage or next action..." aria-label="Search stories"><div style="overflow-x:auto"><table id="stories"><thead><tr><th>ID</th><th>Story</th><th>Pillar</th><th>Stage</th><th>Next action</th></tr></thead><tbody>{''.join(body)}</tbody></table></div><footer>Source of truth: stories/GILB-###/record.json. This dashboard is regenerated; edit the source records, not the dashboard. No story is automatically declared verified.</footer><script>document.getElementById('q').addEventListener('input',function(){{let q=this.value.toLowerCase();document.querySelectorAll('#stories tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));}});</script></body></html>'''
    dest.write_text(page,encoding='utf-8')

def events(root, action, sid, details):
    p=root/'registry'/'events.jsonl';p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps({'at_utc':timestamp(),'action':action,'story_id':sid,'details':details},ensure_ascii=False)+'\n')

def story_path(root,sid):return root/'stories'/sid/'record.json'
def next_id(root,prefix):
    all_objs,_=load(root); nums=[]
    if prefix=='GILB':return f'GILB-{max([int(d["story"]["id"].split("-")[-1]) for _,d in all_objs]+[0])+1:03d}'
    for _,d in all_objs:
        for k in SHEET_FOR_COLLECTION:
            for r in d.get(k,[]):
                rid=str(r.get('id',''))
                if re.fullmatch(rf'{prefix}-\d+',rid):nums.append(int(rid.split('-')[-1]))
    glob=root/'registry'/'global.json'
    if glob.exists():
        for r in json.loads(glob.read_text(encoding='utf-8')).get('records',[]):
            if re.fullmatch(rf'{prefix}-\d+',str(r.get('id',''))):nums.append(int(r['id'].split('-')[-1]))
    return f'{prefix}-{max(nums+[0])+1:03d}'

def get(root,sid):
    path=story_path(root,sid)
    if not path.exists():raise ValueError('Unknown story ID: '+sid)
    return path,json.loads(path.read_text(encoding='utf-8'))

def parse_fields(kvs):
    out={}
    for item in kvs:
        if '=' not in item:raise ValueError('Use --field key=value')
        k,v=item.split('=',1)
        if not re.fullmatch(r'[a-z][a-z0-9_]*',k):raise ValueError('Invalid field name: '+k)
        if v.startswith('[') or v.startswith('{'):
            try:v=json.loads(v)
            except json.JSONDecodeError as e:raise ValueError(f'Invalid JSON for {k}: {e}')
        out[k]=v
    return out

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=ROOT,help='Repository root (for testing)')
    sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('validate');sub.add_parser('build');sub.add_parser('list')
    nw=sub.add_parser('new-story');nw.add_argument('title');nw.add_argument('--pillar',required=True);nw.add_argument('--priority',default='Medium');nw.add_argument('--next-action',default='Choose and validate sources')
    st=sub.add_parser('set-story');st.add_argument('story_id');st.add_argument('--field',action='append',default=[],required=True)
    ad=sub.add_parser('add-record');ad.add_argument('story_id');ad.add_argument('kind',choices=list(KINDS));ad.add_argument('--field',action='append',default=[],required=True)
    args=ap.parse_args(argv);root=args.root.resolve()
    try:
        if args.cmd=='validate':
            errors=validate(root)
            if errors: print('FAILED:\n- '+'\n- '.join(errors));return 1
            print(f'PASS: {len(files(root))} story records validated');return 0
        if args.cmd=='build':
            print('Generated exports:',json.dumps(build(root),ensure_ascii=False));return 0
        if args.cmd=='list':
            for _,d in load(root)[0]:print(d['story']['id'],d['story']['stage'],d['story']['title'])
            return 0
        if args.cmd=='new-story':
            sid=next_id(root,'GILB')
            rec={'story':{'id':sid,'title':args.title,'pillar':args.pillar,'angle':'','visual_format':'','audience':'','priority':args.priority,'stage':'Idea','editorial_decision':'Candidate','claim_confidence':'Unverified','added_on':today(),'target_publish':'','owner':'GilB','next_action':args.next_action,'blocker':'','video_url':''},**{k:[] for k in SHEET_FOR_COLLECTION}}
            p=story_path(root,sid);dump(p,rec)
            for f in ('data/raw','data/clean','analysis','evidence','scripts','storyboards','animations'):
                (p.parent/f).mkdir(parents=True,exist_ok=True);(p.parent/f/'.gitkeep').touch()
            events(root,'new-story',sid,{'title':args.title}); print('Created',sid)
        elif args.cmd=='set-story':
            p,d=get(root,args.story_id);fields=parse_fields(args.field)
            allowed=set(COLUMNS['STORIES'])-{'id','dataset_count','analysis_count','evidence_count','asset_count','added_on'}
            if set(fields)-allowed:raise ValueError('Unknown/immutable story fields: '+str(sorted(set(fields)-allowed)))
            d['story'].update(fields);old=p.read_text(encoding='utf-8');dump(p,d)
            if validate(root):p.write_text(old,encoding='utf-8');raise ValueError('\n'.join(validate(root)))
            events(root,'set-story',args.story_id,fields);print('Updated',args.story_id)
        elif args.cmd=='add-record':
            p,d=get(root,args.story_id);collection,prefix=KINDS[args.kind];fields=parse_fields(args.field)
            allowed=set(COLUMNS[SHEET_FOR_COLLECTION[collection]])-{'id','story_id'}
            if set(fields)-allowed:raise ValueError('Unknown fields: '+str(sorted(set(fields)-allowed)))
            rid=next_id(root,prefix);d.setdefault(collection,[]).append({'id':rid,**fields})
            old=p.read_text(encoding='utf-8');dump(p,d)
            problems=validate(root)
            if problems:p.write_text(old,encoding='utf-8');raise ValueError('\n'.join(problems))
            events(root,'add-'+args.kind,args.story_id,{'record_id':rid,'fields':fields});print('Added',rid,'to',args.story_id)
        build(root)
        return 0
    except (OSError,ValueError,json.JSONDecodeError) as e:
        print('ERROR:',str(e),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
