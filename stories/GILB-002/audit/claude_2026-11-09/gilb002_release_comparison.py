import sys,re,glob,os,warnings,json
warnings.simplefilter('ignore')
B=sys.argv[1]; sys.path.insert(0,B+'/pylib')
import fitz
MON=re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d\d)$')
MN={m:i+1 for i,m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
def ym(t):
    m=MON.match(t); return f'20{m.group(2)}-{MN[m.group(1)]:02d}'
def grab(f):
    d=fitz.open(f); out={}
    for p in d:
        ws=sorted(p.get_text('words'),key=lambda w:((w[1]+w[3])/2,w[0]))
        rows=[];cur=[];y0=None
        for w in ws:
            y=(w[1]+w[3])/2
            if y0 is None or abs(y-y0)<2.2: cur.append(w); y0=y if y0 is None else y0
            else: rows.append(sorted(cur,key=lambda v:v[0]));cur=[w];y0=y
        rows.append(sorted(cur,key=lambda v:v[0]))
        cols=None
        for r in rows:
            ms=[(ym(w[4]),(w[0]+w[2])/2) for w in r if MON.match(w[4])]
            if len(ms)>=2: cols=ms; continue
            if not cols: continue
            lab=' '.join(w[4] for w in r if not re.match(r'^-?[\d,.]+%?$',w[4]))
            op='AT' if 'Airtel' in lab else 'Telecel' if 'Telecel' in lab else 'MTN' if 'Scancom' in lab else 'TOTAL' if lab.startswith('TOTAL MOBILE') else None
            if not op: continue
            for w in r:
                if re.match(r'^[\d,]{9,}$',w[4]):
                    v=int(w[4].replace(',',''))
                    if v<500000: continue
                    x=(w[0]+w[2])/2; m,cx=min(cols,key=lambda c:abs(c[1]-x))
                    out.setdefault((m,op),v)
    return out,d.metadata.get('creationDate','')[2:10]
files=sorted(glob.glob(B+'/nca_vint/*.pdf'))+[B+'/nca_raw/Market-Data-2024.pdf',B+'/nca_raw/Data-Subscription-December-2025.pdf',B+'/nca_raw/Monthly-Industry-Data_July_2026-.pdf']
allv={}
for f in files:
    v,c=grab(f); name=os.path.basename(f); allv[(c,name)]=v; print(c,name,len(v),'months',min(k[0] for k in v),max(k[0] for k in v))
order=sorted(allv)
cells=sorted({k for v in allv.values() for k in v})
n=0; multi=0
print('--- cells with more than one published value')
rows=[]
for k in cells:
    vals=[(c,nm,allv[(c,nm)][k]) for c,nm in order if k in allv[(c,nm)]]
    if len(vals)>1: multi+=1
    if len({x[2] for x in vals})>1:
        n+=1; print(k,[(c,x) for c,nm,x in vals]); rows.append((k,vals))
print('cells published in 2+ files',multi,'cells that differ',n)
