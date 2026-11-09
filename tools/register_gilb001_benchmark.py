#!/usr/bin/env python3
"""Register or correct the GILB-001 creative benchmark (v1.1).

Owner confirmed original export full-size; smaller copy is only chat compression.
Idempotent; does not approve claims or publish the video.
"""
from __future__ import annotations
import json,sys,hashlib,subprocess,shutil
from pathlib import Path
import registry

ROOT=Path(__file__).resolve().parents[1]
SID='GILB-001'
REC=ROOT/'stories'/SID/'record.json'
BASE=f'stories/{SID}/production/benchmark_rc1/'
PREVIEW=BASE+'GILB001_Hearts_of_Oak_Creative_Benchmark_RC1.mp4'
MASTER=BASE+'GILB001_Hearts_of_Oak_Original_Master.mp4'
QA=BASE+'FINAL_RELEASE_QA.md'
NOTES=BASE+'RELEASE_NOTES.md'
STATUS=BASE+'MASTER_STATUS.json'
MANIFEST=BASE+'ASSET_MANIFEST.json'
STANDARD='docs/GilB_PRODUCTION_QUALITY_STANDARD_v1.md'
OWNER_DATE='2026-11-08'


def get_video_metadata(path):
    cmd=shutil.which('ffprobe')
    if not cmd:return None
    try:
        p=subprocess.run([cmd,'-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate',
                          '-of','json',str(path)],capture_output=True,text=True,check=True,timeout=15)
        info=json.loads(p.stdout)
        return info['streams'][0] if info.get('streams') else None
    except Exception as e:
        print('NOTE: ffprobe inspection unavailable:',str(e));return None


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def main():
    for rel in [PREVIEW,QA,NOTES,STATUS,MANIFEST,STANDARD]:
        if not (ROOT/rel).is_file():raise RuntimeError(f'Missing {rel}; copy the complete ZIP into repository root.')
    if not REC.exists():raise RuntimeError(f'Missing {REC}; run this inside the GilB repo.')
    mani=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))
    expected=next((f.get('sha256') for f in mani.get('files',[]) if f.get('path')==Path(PREVIEW).name),None)
    preview_sha=sha(ROOT/PREVIEW)
    if not expected or preview_sha!=expected:raise RuntimeError('Compressed review video differs from package manifest.')
    original_txt=REC.read_text(encoding='utf-8')
    obj=json.loads(original_txt);st=obj.get('story',{})
    if st.get('id')!=SID:raise RuntimeError('Wrong story ID in record.')
    if st.get('stage') in ('Ready to publish','Published','Archived') or any(p.get('publish_status')=='Published' for p in obj.get('posts',[])):
        raise RuntimeError('Story progressed past Review. Check manually to avoid downgrading its release status.')
    old_status=(ROOT/STATUS).read_text(encoding='utf-8')
    status=json.loads(old_status);changes=[]
    stories,glob=registry.load(ROOT)
    used={x.get('id') for _,s in stories for key in ('datasets','analyses','evidence','assets','posts','issues') for x in s.get(key,[])}
    used.update(x.get('id') for x in glob.get('records',[]))
    def newid(prefix):
        n=1
        while f'{prefix}-{n:03d}' in used:n+=1
        key=f'{prefix}-{n:03d}';used.add(key);return key
    assets=obj.setdefault('assets',[])
    def asset(path,typ,name,version,description,review):
        found=next((a for a in assets if a.get('path')==path),None)
        if found:
            for k,v in [('quality_review',review),('status',description)]:
                if found.get(k)!=v:found[k]=v;changes.append(f'asset {found["id"]} updated {k}')
        else:
            rid=newid('AS')
            assets.append({'id':rid,'asset_type':typ,'version':version,'name':name,'path':path,
              'status':description,'owner':'GilB','updated_on':registry.today(),
              'quality_review':review,'notes':'Preserve earlier versions; not a publishing approval.'})
            changes.append(f'asset {rid} created')
    asset(PREVIEW,'Creative benchmark review video','Hearts of Oak — compressed chat review copy','RC1',
        'Creative benchmark approved; compressed chat reference, NOT source master',
        'Owner confirms separate original full-resolution video exists. This 512x910 chat copy is not the original. No re-export required; release checks still open.')
    asset(STANDARD,'Production quality standard','GilB quality checklist','v1.0','Approved reusable creative and QC standard',
        'Applies to original export, not only reduced chat copy.')
    asset(QA,'Release QA tracker','GILB-001 remaining publication sign-offs','v1.1','Open — release checks pending',
        'Original export confirmed by owner; archive/inspect existing master, do not re-export. Data, audio/rights, captions remain pending.')
    asset(MANIFEST,'Archive manifest','GILB-001 review-package integrity fingerprints','v1.1','Reference archive',
        'Hashes supplied copy and included research only; original master is separate.')
    asset(STATUS,'Owner master confirmation','Original-versus-compressed copy record','v1.1','Owner-confirmed original; independent metadata pending',
        '2026-11-08: Original export correct resolution per owner. The smaller chat file is a compressed copy. No re-export required.')
    issues=obj.setdefault('issues',[])
    def issue(marker,desc,priority,action,typ='Release blocker'):
        if any(marker in str(x.get('description','')) for x in issues):return
        rid=newid('ISS');issues.append({'id':rid,'type':typ,'description':marker+' — '+desc,
          'priority':priority,'owner':'GilB','opened_on':registry.today(),'due':'',
          'status':'Open','resolution':'','next_action':action})
        changes.append(f'issue {rid} created')
    for i in issues:
        if 'BENCHMARK-RC1-EXPORT' in str(i.get('description','')):
            res='Closed on 2026-11-08: owner confirmed the original video is correct full resolution. 512x910 applies only to the compressed chat copy; no re-export needed. Master archive/metadata check tracked separately.'
            for k,v in [('status','Closed'),('resolution',res),('next_action','')]:
                if i.get(k)!=v:i[k]=v;changes.append(f'export issue {i["id"]} {k} corrected')
    master_path=ROOT/MASTER
    if master_path.is_file():
        meta=get_video_metadata(master_path)
        digest=sha(master_path)
        masterdata=status['original_master']
        masterdata.update({'archived_path':MASTER,'sha256':digest})
        if meta:
            masterdata['measured_width']=meta.get('width');masterdata['measured_height']=meta.get('height')
            w,h=meta.get('width'),meta.get('height')
            masterdata['technical_check']='Pass: metadata inspected' if w==1080 and h==1920 else f'Review original dimensions {w}x{h} against 1080x1920 target'
        else:
            masterdata['technical_check']='Original master SHA-256 recorded; video dimensions pending ffprobe check'
        asset(MASTER,'Original master video','Hearts of Oak — owner original export','master v1',
            'Original master archived; publishing not approved',
            f'Original SHA-256 {digest}; {masterdata["technical_check"]}. Source resolution must be independently confirmed before release.')
        for i in issues:
            if 'BENCHMARK-RC1-MASTER-ARCHIVE' in str(i.get('description','')):
                if meta and meta.get('width')==1080 and meta.get('height')==1920:
                    if i.get('status')!='Closed':i['status']='Closed';changes.append('master archive issue closed')
                    i['resolution']='Original video copied to repo; SHA-256 and 1080x1920 metadata confirmed.'
                    i['next_action']=''
                else:
                    i['next_action']='Check original dimensions with ffprobe; SHA-256 has been recorded.'
    else:
        issue('BENCHMARK-RC1-MASTER-ARCHIVE',
          'Preserve and inspect the existing high-resolution original video. No re-export necessary.',
          'Medium','Copy the original master into benchmark_rc1/ or store externally and record its link/hash.','Archive follow-up')
    issue('BENCHMARK-RC1-RELEASE-QA',
      'Final match data sign-off, music rights, captions and mobile playback remain pending.',
      'High','Complete FINAL_RELEASE_QA.md, then explicitly approve for publication.')
    issue('BENCHMARK-RC1-SOURCE',
      'Editable Claude project has not been provided for archive.',
      'Medium','Archive Claude animation source files and dependencies.')
    if st.get('stage')!='Review':st['stage']='Review';changes.append('stage corrected to Review')
    decision='Creative benchmark approved 2026-11-08. Original high-resolution export confirmed by owner; chat copy reduced. Publication sign-off pending.'
    if st.get('editorial_decision')!=decision:st['editorial_decision']=decision;changes.append('editorial decision corrected')
    action='Archive and inspect existing original full-resolution master (no re-export); preserve Claude source; complete match-data, rights, captions and final release QA.'
    if st.get('next_action')!=action:
        st['next_action']=action;changes.append('next action corrected')
    new_status=json.dumps(status,indent=2,ensure_ascii=False)+'\n'
    if new_status!=old_status:changes.append('master status manifest updated')
    if not changes:
        print('NO CHANGES: already corrected; no duplicate events.')
        return
    registry.dump(REC,obj)
    (ROOT/STATUS).write_text(new_status,encoding='utf-8')
    try:
        errs=registry.validate(ROOT)
        if errs:raise RuntimeError('; '.join(errs))
        registry.build(ROOT)
    except Exception:
        REC.write_text(original_txt,encoding='utf-8')
        (ROOT/STATUS).write_text(old_status,encoding='utf-8')
        try:registry.build(ROOT)
        except Exception:pass
        raise
    registry.events(ROOT,'correct-original-master-resolution',SID,{
        'approved_creative_benchmark':'yes',
        'owner_confirmed_original_master':'correct full-resolution export exists',
        're_export_required':False,'publication_cleared':False,
        'changed':changes})
    print(f'PASS: GILB-001 benchmark corrected. {len(changes)} updates; story stays Review; video NOT published.')
    print('PASS: No re-export required. Original file archiving and final release QA still tracked.')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('ERROR:',str(e),file=sys.stderr)
        raise SystemExit(1)
