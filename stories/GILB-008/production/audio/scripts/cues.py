"""Word-anchored cue times for GILB-006 audio (video time = narration time + PRE). Mirrors Wd()/L() in scenes.js."""
import json, re
PRE = 0.5
T = json.load(open('/home/claude/gilb006_sb/timing.json'))
TL = T['lines']; AUDIO_LEN = T['audio_len']; TOTAL = round(AUDIO_LEN + PRE + 1.6, 1)
norm = lambda s: re.sub(r"[^a-z0-9'-]", '', s.lower())
def Wd(i, w, n=1):
    c = 0
    for x in TL[i]['words']:
        if norm(x['w']) == norm(w):
            c += 1
            if c == n: return x['s'] + PRE
    raise KeyError((i, w, n))
def WdE(i, w, n=1):
    c = 0
    for x in TL[i]['words']:
        if norm(x['w']) == norm(w):
            c += 1
            if c == n: return x['e'] + PRE
    raise KeyError((i, w, n))
L = lambda i: TL[i]['s'] + PRE
LE = lambda i: TL[i]['e'] + PRE
import subprocess
SCENES = json.loads(subprocess.run(['node', '-e', '''
const fs=require("fs");globalThis.TIMING=JSON.parse(fs.readFileSync("/home/claude/gilb006_sb/timing.json","utf8"));
eval(fs.readFileSync("/home/claude/gilb006_sb/src/scenes.js","utf8").replace("const SCENES","globalThis.SCENES"));
console.log(JSON.stringify(SCENES.map(s=>[s.a0+.5,s.a1+.5])))'''], capture_output=True, text=True).stdout)
