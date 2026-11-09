#!/usr/bin/env python3
"""GilB GILB-001 — independent, reproducible silent draft render.

No network, paid services, third-party photos, music, or proprietary assets.
Uses installed Inter fonts; font files are NOT redistributed.
The scene timeline is a temp guide until owner voiceover is recorded.
"""
from __future__ import annotations
import argparse, csv, math, os, subprocess, sys
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Internal story identifiers are only in the source / filenames, never in video frames.
W,H=720,1280
FPS=24
SCENES=[
    ("The mystery",8), ("Just 15 conceded",7), ("24 clean sheets",6),
    ("13 of the 24 ended 0–0",9), ("Neither team scored",6),
    ("Defence is not attack",7), ("25 in 34",7), ("Below average",8),
    ("18 without a goal",7), ("Equal defeats",9), ("Wins separate them",8),
    ("Eight-point gap",8), ("The takeaway",9), ("GilB",5)
]
TOTAL=sum(d for _,d in SCENES)
C={
    'bg':(9,21,33),'navy':(16,28,43),'panel':(22,42,58),
    'ivory':(243,240,232),'amber':(217,171,86),'teal':(54,167,163),
    'muted':(147,168,182),'subtle':(70,93,107),'dark':(12,33,42),
    'slate':(34,54,69),'white':(252,252,249), 'red':(204,105,100)
}
FONT_ROOT='/usr/share/fonts/opentype/inter'
FONT_FILES={'regular':'Inter-Regular.otf','medium':'Inter-Medium.otf','semibold':'Inter-SemiBold.otf',
            'bold':'Inter-Bold.otf','heavy':'Inter-ExtraBold.otf'}
@lru_cache(maxsize=96)
def font(size:int,weight:str='regular'):
    path=os.path.join(FONT_ROOT, FONT_FILES.get(weight,'Inter-Regular.otf'))
    if not os.path.isfile(path):
        # Cross-platform fallback: we never package or distribute font files.
        candidates = [
            os.path.join(os.environ.get('WINDIR',r'C:\\Windows'),'Fonts', 'segoeuib.ttf' if weight in ('heavy','bold') else 'segoeui.ttf'),
            os.path.join(os.environ.get('WINDIR',r'C:\\Windows'),'Fonts','arialbd.ttf' if weight in ('heavy','bold') else 'arial.ttf'),
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            'DejaVuSans.ttf'
        ]
        for candidate in candidates:
            try: return ImageFont.truetype(candidate,max(8,int(size)))
            except OSError: pass
        return ImageFont.load_default()
    return ImageFont.truetype(path, max(8,int(size)))

def ease(v:float)->float:
    v=max(0,min(1,v)); return v*v*(3-2*v)
def expout(v:float)->float:
    v=max(0,min(1,v));return 1-(1-v)**3

def txt(d, text, x, y, size=30, color='ivory', weight='medium', maxw=None, align='left'):
    text=str(text); f=font(size,weight)
    if maxw:
        while size>13 and d.textbbox((0,0),text,font=f)[2]>maxw:
            size-=1; f=font(size,weight)
    if align!='left':
        width=d.textbbox((0,0),text,font=f)[2]
        if align=='center': x-=width/2
        elif align=='right': x-=width
    d.text((int(x),int(y)),text,font=f,fill=C.get(color,color),stroke_width=0)
    return d.textbbox((0,0),text,font=f)[2]

def rule(d,x,y,x2,col='subtle',width=2):
    d.line((int(x),int(y),int(x2),int(y)), fill=C[col],width=width)

def panel(d,box,fill='panel',radius=14,outline=None,width=1):
    d.rounded_rectangle(tuple(map(int,box)),radius=radius,fill=C[fill],outline=C[outline] if outline else None,width=width)

def kicker(d,text,y=194):
    txt(d,text,58,y,20,'muted','semibold',maxw=610)

def hero(d,num, y=290,col='amber',size=190,sub=None, x=58):
    txt(d,num,x,y,size,col,'heavy',maxw=640)
    if sub:txt(d,sub,x,y+size+10,24,'muted','medium')

def label(d,text,y=510,size=42,col='ivory'):
    txt(d,text,58,y,size,col,'bold',maxw=604)

def line_2(d,first,second,y,size=48,col='ivory',col2='amber'):
    txt(d,first,58,y,size,col,'bold',maxw=610)
    txt(d,second,58,y+size+16,size,col2,'bold',maxw=610)

def slide(t,delay=0.10,span=.8,amp=24):
    return int(amp*(1-expout((t-delay)/span)))

# A complete, source-backed season timeline. Each tile is a match played, never an
# arbitrary grouped index or unsorted matchweek. Matchweek 31 was played before 30.
MATCHES_PATH=Path(__file__).resolve().parent.parent/'data'/'hearts_2025-26_chronological_matches.csv'
with MATCHES_PATH.open(newline='',encoding='utf-8-sig') as _f:
    MATCHES=list(csv.DictReader(_f))
for _r in MATCHES:
    for _k in ('round','match_order','hearts_goals','opponent_goals','clean_sheet','goalless_draw','scoreless_loss','failed_to_score'):
        _r[_k]=int(_r[_k])
assert len(MATCHES)==34 and [r['match_order'] for r in MATCHES]==list(range(1,35))
assert [r['round'] for r in MATCHES][29:31]==[31,30], 'Chronological rounds 31 and 30 reversed'
assert sum(r['clean_sheet'] for r in MATCHES)==24
assert sum(r['goalless_draw'] for r in MATCHES)==13
assert sum(r['scoreless_loss'] for r in MATCHES)==5
assert sum(r['failed_to_score'] for r in MATCHES)==18
assert sum(r['hearts_goals'] for r in MATCHES)==25
assert sum(r['opponent_goals'] for r in MATCHES)==15
assert sum(r['result']=='W' for r in MATCHES)==13
assert sum(r['result']=='D' for r in MATCHES)==15
assert sum(r['result']=='L' for r in MATCHES)==6
DRAW_ORDER=[r['match_order'] for r in MATCHES if r['goalless_draw']]
CS_ORDER=[r['match_order'] for r in MATCHES if r['clean_sheet']]
SCORELESS_OTHER=[r['match_order'] for r in MATCHES if r['scoreless_loss']]

def draw_tile_grid(d,t,mode, y=604, x=64, w=88,h=78,gx=11,gy=11):
    """Persistent chronological 34-game grid with match-number labels 01–34.

    Clean sheets stay in their real fixture positions; 0-0 results and additional
    scoreless defeats are revealed in place. Each numbered tile is the ORDER
    PLAYED (not nominal matchweek; 31 and 30 were swapped).
    """
    reveal_start=1.45
    cs_start=0.8
    draw_start=1.55
    extra_start=2.7
    for i,r in enumerate(MATCHES):
        col=i%6;row=i//6;X=x+col*(w+gx);Y=y+row*(h+gy)
        order=r['match_order']
        cs=r['clean_sheet']==1
        gd=r['goalless_draw']==1
        other=r['scoreless_loss']==1
        if mode=='clean':
            if t<.42+i*.022:continue
            idx=CS_ORDER.index(order) if cs else 100
            typ='gold' if cs and t>=cs_start+idx*.115 else 'off'
        elif mode=='reveal':
            if gd:
                idx=DRAW_ORDER.index(order)
                typ='teal' if t>=draw_start+idx*.38 else 'gold'
            else:typ='gold' if cs else 'off'
        elif mode=='reflect':
            typ='teal' if gd else 'gold' if cs else 'off'
        elif mode=='scoreless':
            if gd:
                idx=DRAW_ORDER.index(order)
                typ='teal' if t>=.9+idx*.07 else 'gold'
            elif other:
                idx=SCORELESS_OTHER.index(order)
                typ='red' if t>=extra_start+idx*.43 else 'off'
            else:typ='gold' if cs else 'off'
        else: typ='off'
        fill={'gold':'amber','teal':'teal','off':'slate','red':'red'}[typ]
        # Flip only when a genuine 0-0 tile changes from amber to teal.
        phase=(t-(draw_start+DRAW_ORDER.index(order)*.38))/.36 if gd and mode=='reveal' else -1
        shrink=.70*math.sin(math.pi*phase) if 0<=phase<1 else 0
        ww=max(2,w*(1-shrink));xx=X+(w-ww)*.5
        panel(d,(xx,Y,xx+ww,Y+h),fill,10,outline='subtle' if typ=='off' else None)
        if ww<38:continue
        # Small match-order marker reinforces that these are the original 34 games.
        index_color='dark' if typ in ('gold','teal','red') else 'muted'
        txt(d,f'{order:02d}',X+9,Y+6,13,index_color,'semibold')
        if typ=='teal' and gd:
            txt(d,'0–0',X+w*.5,Y+h*.37,25,'dark','heavy',align='center')
        elif typ=='red' and other:
            txt(d,f"0–{r['opponent_goals']}",X+w*.5,Y+h*.37,24,'dark','heavy',align='center')
        else:
            cy=Y+h*.57
            d.ellipse((X+w*.5-3.5,cy-3.5,X+w*.5+3.5,cy+3.5),fill=C['dark'] if typ=='gold' else C['muted'])

def bg_build():
    im=Image.new('RGB',(W,H))
    px=im.load()
    for y in range(H):
        mix=y/(H-1)
        # gradient with low-contrast teal atmosphere at lower-right
        for x in range(W):
            v=(x/W)**2 * (y/H)**1.7
            px[x,y]=(int(8+8*mix+2*v),int(19+13*mix+12*v),int(31+15*mix+18*v))
    d=ImageDraw.Draw(im)
    # sparse editorial reference lines, keep center airy
    d.line((58,145,662,145),fill=(47,65,78),width=2)
    d.line((58,1172,662,1172),fill=(35,55,68),width=1)
    for iy in range(360,1140,90):
        for ix in (25,688):
            d.ellipse((ix,iy,ix+2,iy+2),fill=(28,49,61))
    return im
BG=bg_build()

def brand(d, tglobal, active_i):
    w=txt(d,'GilB',58,75,37,'ivory','heavy')
    d.ellipse((58+w+3,107,58+w+11,115),fill=C['amber'])
    txt(d,'@Ghyl_B',664,84,20,'muted','semibold',align='right')
    # final video has NO internal IDs, on-screen stage numbers, technical headers, fake crests.

def common_footer(d,i):
    # one understated detail, no explicit source/origin categories and no progress ticker
    if i!=13:
        txt(d,'UNPACKED BY GILB',58,1195,16,'muted','semibold')

def render_scene(i:int, t:float):
    im=BG.copy();d=ImageDraw.Draw(im)
    brand(d,t,i)
    common_footer(d,i)
    off=slide(t)
    if i==0:
        kicker(d,'2025/26  ·  GHANA PREMIER LEAGUE')
        txt(d,'WHAT IF I TOLD YOU...',58,272+off,28,'ivory','semibold')
        big=24*ease((t-.6)/1.8)
        txt(d,str(round(big)),45,352,270,'amber','heavy')
        txt(d,'CLEAN SHEETS',58,632,48,'ivory','heavy')
        txt(d,'IN 34 MATCHES',58,698,30,'muted','semibold')
        if t>4.6:
            rule(d,58,836,662,'amber',3)
            txt(d,'BUT NO LEAGUE TITLE.',58,865+slide(t,4.5,.8,28),38,'ivory','bold')
    elif i==1:
        kicker(d,'THE TEAM BEHIND THE RECORD')
        txt(d,'HEARTS OF',58,279+off,64,'ivory','heavy')
        txt(d,'OAK.',58,364+off,91,'ivory','heavy')
        rule(d,58,505,662,'subtle',2)
        n=round(15*ease((t-1.25)/2.1))
        txt(d,str(n),48,535,250,'amber','heavy')
        txt(d,'GOALS CONCEDED',58,833,41,'ivory','bold')
        txt(d,'ACROSS 34 LEAGUE MATCHES',58,899,24,'muted','semibold')
    elif i==2:
        kicker(d,'THE DEFENSIVE RECORD')
        txt(d,'24',58,273+off,167,'amber','heavy')
        txt(d,'CLEAN SHEETS',58,458+off,45,'ivory','heavy')
        txt(d,'34 MATCHES · IN PLAYED ORDER',58,521,23,'muted','medium')
        draw_tile_grid(d,t,'clean',y=604)
    elif i==3:
        kicker(d,'THE SURPRISING PART')
        n=sum(t>=1.75+j*.30 for j in range(13))
        txt(d,str(n),58,275,168,'teal','heavy')
        txt(d,'OF 24 ENDED',283,315,44,'ivory','bold',maxw=390)
        txt(d,'GOALLESS',283,381,36,'ivory','bold',maxw=380)
        txt(d,'0–0 DRAWS',58,503,48,'teal','heavy')
        draw_tile_grid(d,t,'reveal',y=604)
    elif i==4:
        kicker(d,'WHAT THE 0–0s MEANT')
        txt(d,'NEITHER',58,280+off,89,'ivory','heavy')
        txt(d,'TEAM',58,394+off,89,'ivory','heavy')
        txt(d,'SCORED.',58,509+off,89,'teal','heavy')
        draw_tile_grid(d,t,'reflect',y=728,w=77,h=58,gx=12,gy=8,x=88)
    elif i==5:
        kicker(d,'THE TURNING POINT')
        txt(d,'STOP',58,280+off,85,'amber','heavy')
        txt(d,'GOALS.',58,391+off,85,'amber','heavy')
        if t>2.0:
            x=58
            rule(d,x,600,x+604*ease((t-2)/.9),'subtle',3)
        if t>3.2:
            txt(d,'SCORE',58,692+slide(t,3.1,.9,32),85,'teal','heavy')
            txt(d,'GOALS.',58,803+slide(t,3.1,.9,32),85,'teal','heavy')
        txt(d,'DEFENCE ALONE ISN’T ENOUGH.',58,1020,25,'muted','medium')
    elif i==6:
        kicker(d,'THE ATTACKING RECORD')
        n=round(25*ease((t-.8)/1.9))
        txt(d,str(n),58,302,270,'amber','heavy')
        txt(d,'GOALS SCORED',58,626+off,48,'ivory','heavy')
        if t>2:
            txt(d,'IN 34 MATCHES',58,713+slide(t,1.7,.8,24),34,'muted','semibold')
        rule(d,58,842,662,'subtle')
        txt(d,'HEARTS OF OAK',58,874,29,'ivory','medium')
    elif i==7:
        kicker(d,'HOW DOES THAT COMPARE?')
        txt(d,'GOALS PER TEAM',58,274+off,30,'ivory','semibold')
        txt(d,'PER MATCH',58,317+off,30,'muted','medium')
        X0=65; barw=550
        vals=[(.74,'HEARTS OF OAK','amber',.65),(1.02,'LEAGUE AVERAGE','teal',3.1)]
        for k,(v,name,clr,delay) in enumerate(vals):
            Y=465+k*240
            txt(d,name,X0,Y,27,'muted','semibold')
            txt(d,f'{v:.2f}',662,Y-16,60,clr,'heavy',align='right')
            panel(d,(X0,Y+91,X0+barw,Y+131),'slate',8)
            progress=ease((t-delay)/2)
            width=barw*(1.0 if k==1 else (25/34)/(627/612))*progress
            if width>0:panel(d,(X0,Y+91,X0+width,Y+131),clr,8)
        txt(d,'LEAGUE AVERAGE = 100% BENCHMARK',58,1040,17,'muted','medium')
    elif i==8:
        kicker(d,'THE SCORELESS MATCHES')
        txt(d,'18',58,263+off,191,'teal','heavy')
        txt(d,'MATCHES',58,467,50,'ivory','heavy')
        txt(d,'WITHOUT A GOAL',58,528,35,'muted','bold')
        txt(d,'13 DRAWS + 5 SCORELESS LOSSES',58,589,20,'muted','medium',maxw=610)
        draw_tile_grid(d,t,'scoreless',y=637)
    elif i==9:
        kicker(d,'COMPARED WITH THE CHAMPIONS')
        txt(d,'BOTH CLUBS',58,260+off,48,'ivory','heavy')
        txt(d,'LOST SIX.',58,326+off,65,'ivory','heavy')
        panel(d,(58,534,345,904),'panel',16)
        panel(d,(374,534,662,904),'panel',16)
        txt(d,'HEARTS',86,565,27,'muted','bold')
        txt(d,'MEDEAMA',402,565,27,'muted','bold')
        val=int(round(6*ease((t-2.1)/1.9)))
        txt(d,val,82,650,192,'amber','heavy')
        txt(d,val,398,650,192,'teal','heavy')
        txt(d,'LOSSES OF 34',89,841,20,'muted','medium')
        txt(d,'LOSSES OF 34',405,841,20,'muted','medium')
        if t>5: txt(d,'SAME NUMBER OF DEFEATS.',58,999+slide(t,4.9,.8,20),30,'ivory','bold',maxw=600)
    elif i==10:
        kicker(d,'BUT THE WINS WERE DIFFERENT')
        txt(d,'WINS',58,284+off,75,'ivory','heavy')
        txt(d,'EACH TEAM PLAYED 34 MATCHES',58,387,24,'muted','medium')
        X0=68; barw=560
        vals=[(17,'MEDEAMA','teal'),(13,'HEARTS OF OAK','amber')]
        for k,(v,name,clr) in enumerate(vals):
            Y=510+k*252
            txt(d,name,X0,Y,29,'muted','semibold')
            txt(d,f'{v}/34',660,Y-6,67,clr,'heavy',align='right')
            panel(d,(X0,Y+94,X0+barw,Y+148),'slate',11)
            width=barw*v/34*ease((t-1.4-k*.45)/2.3)
            if width>1:panel(d,(X0,Y+94,X0+width,Y+148),clr,11)
    elif i==11:
        kicker(d,'THE POINTS THAT SEPARATED THEM')
        txt(d,'8',58,250+off,172,'amber','heavy')
        txt(d,'POINTS BEHIND',58,454,57,'ivory','heavy')
        txt(d,'BOTH CLUBS PLAYED 34 MATCHES',58,540,22,'muted','medium')
        x0=64;full=585
        for row,(name,win,draw,loss,points) in enumerate([
            ('MEDEAMA',17,11,6,62),('HEARTS OF OAK',13,15,6,54)]):
            yy=626+row*230
            txt(d,name,63,yy,27,'ivory','bold')
            txt(d,f'{points} PTS',650,yy-5,35,'amber' if row else 'teal','heavy',align='right')
            panel(d,(x0,yy+73,x0+full,yy+115),'slate',7)
            progress=ease((t-1.15-row*.50)/1.8)
            sx=x0
            for count,col in [(win,'teal'),(draw,'amber'),(loss,'red')]:
                sw=full*count/34*progress
                if sw>1:d.rectangle((int(sx),yy+73,int(sx+sw),yy+115),fill=C[col])
                sx+=sw
            txt(d,f'{win}W  ·  {draw}D  ·  {loss}L',x0,yy+139,24,'muted','medium')
        txt(d,'WINS   •   DRAWS   •   LOSSES',58,1113,18,'muted','medium')
    elif i==12:
        kicker(d,'THE TAKEAWAY')
        txt(d,'24',58,267,104,'amber','heavy')
        txt(d,'CLEAN SHEETS',222,306,29,'ivory','bold')
        rule(d,58,403,662,'subtle')
        txt(d,'13',58,432,104,'teal','heavy')
        txt(d,'GOALLESS DRAWS',222,469,29,'ivory','bold')
        rule(d,58,573,662,'subtle')
        txt(d,'DEFENCE',58,669+off,65,'ivory','heavy')
        txt(d,'ALONE WASN’T',58,761+off,52,'ivory','heavy',maxw=605)
        txt(d,'ENOUGH.',58,845+off,65,'amber','heavy')
    elif i==13:
        kicker(d,'')
        # The outro should not look like an ad; let the typography breathe.
        txt(d,'UNPACKED BY',360,312,27,'muted','semibold',align='center')
        word_w=txt(d,'GilB',112,416+off,153,'ivory','heavy')
        d.ellipse((112+word_w+9,537+off,112+word_w+31,559+off),fill=C['amber'])
        rule(d,111,636,609,'amber',4)
        txt(d,'There’s more to',360,704,42,'ivory','medium',align='center')
        txt(d,'the story.',360,761,42,'ivory','medium',align='center')
        txt(d,'@Ghyl_B',360,1030,30,'amber','semibold',align='center')
    return im

def render_frame(seconds:float):
    sumd=0
    for i,(_,dur) in enumerate(SCENES):
        if seconds<sumd+dur or i==len(SCENES)-1:break
        sumd+=dur
    t=max(0,seconds-sumd)
    im=render_scene(i,t)
    # short crossfade only after frame establishes full intended meaning
    cross=.34
    if t>=SCENES[i][1]-cross and i<len(SCENES)-1:
        alpha=ease((t-(SCENES[i][1]-cross))/cross)
        nxt=render_scene(i+1,0)
        im=Image.blend(im,nxt,alpha)
    return im

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',default='GILB001_Full_Animation_Silent_Draft_v1.mp4')
    ap.add_argument('--preview-dir',default='')
    ap.add_argument('--fps',type=int,default=FPS)
    ap.add_argument('--scale',type=int,default=1080,choices=[720,1080])
    ap.add_argument('--short-test',action='store_true',help='render first ten seconds only')
    args=ap.parse_args()
    if args.preview_dir:
        p=Path(args.preview_dir);p.mkdir(exist_ok=True,parents=True)
        at=0
        shots=[]
        for i,(_,dur) in enumerate(SCENES):
            sample=at+(dur*.75 if i in [0,2,3,7,8,10,11] else dur*.60)
            im=render_frame(sample)
            im.save(p/f'scene_{i+1:02d}.png')
            shots.append(im.resize((252,448),Image.Resampling.LANCZOS))
            at+=dur
        columns=4;rows=math.ceil(len(shots)/columns)
        montage=Image.new('RGB',(columns*252,rows*448),(6,15,25))
        for j,s in enumerate(shots):montage.paste(s,((j%columns)*252,(j//columns)*448))
        montage.save(p/'scene_montage.jpg',quality=88)
        print('Saved previews',p,flush=True)
    if args.output:
        duration=10 if args.short_test else TOTAL
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24',
             '-video_size',f'{W}x{H}','-framerate',str(args.fps),'-i','pipe:0',
             '-vf',f'scale={args.scale}:{round(args.scale*16/9)}:flags=lanczos,format=yuv420p',
             '-c:v','libx264','-preset','veryfast','-crf','19','-movflags','+faststart','-an',args.output]
        print('Rendering silent animation:', duration,'seconds /',args.fps,'fps',flush=True)
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for fidx in range(int(duration*args.fps)):
                im=render_frame(fidx/args.fps)
                proc.stdin.write(im.tobytes())
                if fidx%(args.fps*10)==0:
                    print(f'  {fidx/args.fps:.0f}s of {duration}s',flush=True)
            proc.stdin.close()
        except (BrokenPipeError,KeyboardInterrupt):
            try:proc.stdin.close()
            except:pass
            proc.kill();raise
        err=proc.stderr.read().decode('utf-8','replace')
        code=proc.wait()
        if code:raise RuntimeError(f'ffmpeg failed {code}: {err}')
        print('Saved:',args.output,flush=True)
if __name__=='__main__':main()
