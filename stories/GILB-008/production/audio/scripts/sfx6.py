"""Sound-effects layer for GILB-006 "Four Cedis in a Hundred", placed on the storyboard's word-anchored cues.
Organic palette to match the farm look: dry-leaf rustles in place of whooshes and swishes, wooden seed knocks, soft coin clinks
for the cedi grids, marimba / kalimba notes in the score's key (G major pentatonic), a faint field-wind bed."""
import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/scripts"); sys.path.insert(0, "/home/claude/gilb006_audio")
import synth as S
from cues import Wd, WdE, L, LE, TOTAL, SCENES
import tinysoundfont
SR = S.SR; N = int(TOTAL * SR)
out = np.zeros((N, 2)); amb = np.zeros((N, 2)); rng = np.random.default_rng(606)
SF2 = "/home/claude/work/sf/gu/package/GeneralUser.sf2"
PENT = [67, 69, 71, 74, 76, 79, 81, 83, 86, 88, 91]
def eio(x): x = np.clip(x, 0, 1); return np.where(x < .5, 4 * x ** 3, 1 - (-2 * x + 2) ** 3 / 2)

# ---------- dry leaves ----------
def _grains(n, rate_env, tau, amp_spread=3.0):
    """noise crackle: Poisson grain onsets (rate per second follows rate_env), each a fast-decaying noise burst"""
    onsets = rng.random(n) < rate_env / SR
    a = np.zeros(n); k = np.flatnonzero(onsets); a[k] = (rng.pareto(amp_spread, len(k)) + .3)
    kern = np.exp(-np.arange(int(tau * 8 * SR)) / (tau * SR))
    env = np.convolve(a, kern)[:n]
    return rng.standard_normal(n) * env
def rustle(d, peak=.55, rate=900, bright=1.0, body=.35, pan0=-.4, pan1=.4, curve=1.4, hiss=.06):
    n = int(d * SR); q = np.arange(n) / n
    env = np.where(q < peak, (q / peak) ** curve, ((1 - q) / (1 - peak)) ** (curve * .8))
    env = np.clip(env, 0, 1)
    pan = pan0 + (pan1 - pan0) * eio(q)
    chans = []
    for c in (0, 1):
        w = np.cos((pan + 1) * np.pi / 4) if c == 0 else np.sin((pan + 1) * np.pi / 4)
        r = rate * env * w * 1.4
        x = (S.bp(_grains(n, r * .5, .0020), 1100, 3000) * .9 +
             S.bp(_grains(n, r * 1.0, .0012), 2400, min(6500 * bright, 9000)) * 1.0 +
             S.bp(_grains(n, r * .7, .0007), 4500, min(10500 * bright, 16000)) * .55 * bright +
             S.bp(_grains(n, r * .10, .0050, 2.2), 450, 1500) * body)
        x *= env ** .9 * (.4 + .6 * w)                                   # loudness follows the swell too, not just density
        x += S.bp(rng.standard_normal(n), 2000, 8000) * env * w * hiss
        chans.append(x)
    y = np.stack(chans, 1); fade = np.clip(np.minimum(q * d, (1 - q) * d) / .012, 0, 1); y *= fade[:, None]
    y /= np.percentile(np.abs(y), 99.7) * 2.2 + 1e-9; y = np.tanh(y * 1.2) / np.tanh(1.2)            # tame the odd giant grain
    return y
def leaves(t_peak, d=.75, g=.11, peak=.6, **kw):
    """a rustle whose loudest moment lands on t_peak"""
    S.place(out, rustle(d, peak, **kw), t_peak - peak * d, g)
def crunch(t, g=.1, d=.12):
    S.place(out, rustle(d, .12, rate=2600, bright=.8, body=1.2, pan0=-.1, pan1=.1, curve=.6, hiss=.02), t - .015, g)

# ---------- wood, coins, mallets ----------
def knock(f=1000, d=.06):
    n = int(d * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / .016) + .45 * np.sin(2 * np.pi * f * 2.71 * t) * np.exp(-t / .007)
    x += S.bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t / .002) * .5
    return x / np.abs(x).max()
def clink(f0=2900, d=.35):
    n = int(d * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for r, a, dc in ((1, 1, .09), (2.76, .55, .05), (5.40, .35, .03), (8.93, .2, .018)):
        x += a * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * np.exp(-t / dc)
    x += S.hp(rng.standard_normal(n), 5000) * np.exp(-t / .0015) * .4
    return x / np.abs(x).max()
_SYN = {}
def note(prog, m, d=1.2, v=90):
    key = (prog, m, d, v)
    if key not in _SYN:
        syn = tinysoundfont.Synth(gain=0, samplerate=SR); sid = syn.sfload(SF2); syn.program_select(0, sid, 0, prog)
        syn.noteon(0, m, v); a = np.frombuffer(syn.generate(int(d * SR)), np.float32).reshape(-1, 2).copy()
        syn.noteoff(0, m); b = np.frombuffer(syn.generate(int(1.2 * SR)), np.float32).reshape(-1, 2)
        _SYN[key] = np.concatenate([a, b]).astype(np.float64)
    return _SYN[key]
mar = lambda t, m, g=.5, pan=0.0, d=1.0: S.place(out, note(12, m, d), t, g, pan)
kal = lambda t, m, g=.5, pan=0.0, d=1.0: S.place(out, note(108, m, d), t, g, pan)
def counter(t0, t1, n=12, f0=900, f1=1500, g=.07, land=None, land_g=.5, pan=.2):
    u = np.linspace(0, 1, 2000); p = eio(u)
    for k in range(1, n):
        i = np.searchsorted(p, k / n); t = t0 + u[min(i, 1999)] * (t1 - t0)
        S.place(out, knock(f0 + (f1 - f0) * k / n, .05), t, g * (.6 + .4 * k / n), pan * np.sin(k * 1.7))
    if land: mar(t1, land, land_g)
def coins(t0, t1, n, g=.035, partial=False):
    u = np.linspace(0, 1, 2000); p = eio(u)
    for k in range(n):
        i = np.searchsorted(p, (k + .5) / n); t = t0 + u[min(i, 1999)] * (t1 - t0)
        S.place(out, clink(rng.uniform(2600, 3400)), t + rng.uniform(-.01, .01), g * rng.uniform(.75, 1), rng.uniform(-.4, .4))
    if partial: S.place(out, clink(2200, .25), t1 + .08, g * .45, .1)
LOG = []
def cue(name, t): LOG.append((round(t, 2), name)); return t

# ---------- scene cuts: a dry-leaf rustle crossing the cut (no whooshes) ----------
for i, (v0, v1) in enumerate(SCENES):
    if i == 0: continue
    d = rng.uniform(.68, .82); leaves(cue(f'cut {i}->{i + 1}', v0), d, .085, .58, rate=rng.uniform(700, 1000), pan0=(-.6 if i % 2 else .6), pan1=(.5 if i % 2 else -.5))

# ---------- 1 hook: stalk grows, kernel rows stack like vertebrae, husks open, seedlings sprout ----------
ta = cue('stalk grows', Wd(0, 'agriculture')); leaves(ta + .55, 1.0, .06, .6, rate=500, bright=.8, pan0=0, pan1=0)
tb = cue('backbone: kernel rows', Wd(0, 'backbone'))
for r in range(12): S.place(out, knock(820 + 55 * r, .05), tb - .15 + r * .06 + .16, .055, -.15 + .025 * r)
leaves(cue('husks open', tb + .2), .7, .07, .45, rate=1100, pan0=-.5, pan1=.5)
kal(tb + .75, 86, .22, .2)
for k in range(8): S.place(out, rustle(.12, .3, rate=1500, curve=.8), tb + .3 + k * .16 + rng.uniform(0, .05), .022, rng.uniform(-.8, .8))   # seedlings

# ---------- 2 three tests ----------
leaves(cue('title', L(1) - .05), .4, .04, .35, rate=700)
for i in range(3): S.place(out, knock(700 + 120 * i, .06), cue(f'row {i + 1}', Wd(1, 'Three') + i * .18 + .12) if i == 0 else Wd(1, 'Three') + i * .18 + .12, .07, -.2 + .2 * i)

# ---------- 3 jobs ----------
th = cue('grid of 100 people', Wd(3, 'hundred') - .2); leaves(th + .4, .7, .045, .5, rate=900)
t37 = cue('counter to 37', Wd(3, 'thirty-seven') - .1); counter(t37, t37 + 1.0, 14, 850, 1450, .06, 79, .38)
for k in range(10): S.place(out, rustle(.1, .3, rate=1500, curve=.8), t37 + k * .1 + rng.uniform(0, .04), .018, rng.uniform(-.8, .8))   # seedlings
kal(cue('5 million chip', Wd(4, 'five') - .05), 74, .25, -.3)
tbk = cue('A backbone chip', L(5) - .05); mar(tbk, 74, .32, .3); mar(tbk + .12, 79, .32, .3)

# ---------- 4 output ----------
th = cue('grid of 100 coins', Wd(7, 'hundred') - .2); leaves(th + .4, .6, .04, .5, rate=800)
t23 = cue('coins to 23', Wd(7, 'twenty-three') - .1); coins(t23, t23 + .9, 12, .03); counter(t23, t23 + .9, 10, 900, 1400, .035, 76, .34)
for k in range(8): S.place(out, rustle(.1, .3, rate=1500, curve=.8), t23 + k * .11 + rng.uniform(0, .04), .016, rng.uniform(-.8, .8))
tbk = cue('Still a backbone chip', L(8) - .05); mar(tbk, 74, .32, .3); mar(tbk + .12, 79, .32, .3)

# ---------- 5 bank loans ----------
th = cue('grid of 100 coins', Wd(10, 'hundred') - .2); leaves(th + .4, .6, .04, .5, rate=800)
t4 = cue('4.3 coins', Wd(10, 'four') - .15)
for k in range(4): S.place(out, clink(rng.uniform(2700, 3200)), t4 + .12 + k * .16, .045, -.3 + .15 * k)
S.place(out, clink(2300, .25), t4 + .12 + 4 * .16, .02, .3)
cue('"Four." (score: single low note)', L(11))

# ---------- 6 shrinking? It isn't ----------
leaves(cue('title', Wd(12, "that's") - .1), .4, .035, .35, rate=600)
ts = cue('plant shrinks', Wd(12, 'shrinking') - .1); leaves(ts + .45, .8, .055, .55, rate=650, bright=.65, pan0=.2, pan1=-.2)
S.place(out, S.noise_sweep(.7, 1400, 500, .8, lambda q: np.sin(np.pi * q) * .8, False), ts, .015)
ti = cue('IT ISN\'T stamp', L(13) + .12); S.place(out, S.tom(72, .28), ti, .1); crunch(ti, .1)
leaves(cue('plant shoots up', L(13) + .3), .7, .08, .4, rate=1200, bright=1.1, pan0=-.2, pan1=.3); kal(L(13) + .3, 79, .2); kal(L(13) + .42, 83, .18)

# ---------- 7 growth in 2025 ----------
leaves(cue('title', Wd(14, 'agriculture') - .3), .4, .035, .35, rate=600)
def roll(t0, d, ms, g=.22, pan=0.0):
    for k, m in enumerate(ms): mar(t0 + d * k / len(ms), m, g * (.7 + .3 * k / len(ms)), pan, .4)
ta = cue('agriculture bar to 6.8%', Wd(14, 'six') - .2); roll(ta, .85, [67, 71, 74, 76, 79, 83], .2, -.2)
tt = cue('seedling on the bar tip', Wd(14, 'six') + .6); S.place(out, rustle(.18, .3, rate=1600, curve=.8), tt, .04, .3); kal(tt + .05, 88, .16, .3)
kal(cue('Faster chip', Wd(14, 'faster') - .05), 81, .2, .35)
te = cue('economy bar to 6.0%', Wd(14, "economy's")); roll(te, .95, [62, 67, 69, 71, 74], .17, .2)

# ---------- 8 loans went up, all loans faster ----------
leaves(cue('title', L(15) - .05), .4, .035, .35, rate=600)
tu = cue('agriculture loans +6%', Wd(16, 'up') - .3); roll(tu, .5, [67, 71, 74], .18, -.2)
to = cue('all loans +16%', Wd(17, 'overall')); tf = Wd(17, 'faster'); roll(to, max(.6, tf + .25 - to), [62, 67, 69, 71, 74, 76, 79], .17, .2)
coins(to + .1, tf + .3, 6, .018)

# ---------- 9 share fell ----------
t1 = cue('4.7%', Wd(18, 'four') - .1); kal(t1, 76, .2, -.2)
t2 = cue('4.3%: fifth coin drains', Wd(18, 'four', 2) - .1); kal(t2, 74, .2, .2); kal(t2 + .45, 71, .18, .2)
S.place(out, rustle(.9, .3, rate=260, bright=.7, body=.1, pan0=.2, pan1=.2, curve=1.0), t2, .03)

# ---------- 10 what this counts ----------
leaves(cue('title', L(19) - .05), .4, .035, .35, rate=600)
leaves(cue('counted card', Wd(19, 'bank') - .1), .4, .045, .35, rate=750, pan0=-.4, pan1=-.1)
leaves(cue('not counted card', Wd(19, 'not') - .1), .4, .045, .35, rate=750, pan0=.1, pan1=.4)
for i in range(3): S.place(out, knock(1100 + 90 * i, .05), cue('chip', Wd(19, 'source') + .05 + i * .15) if i == 0 else Wd(19, 'source') + .05 + i * .15, .04, -.3 + .3 * i)

# ---------- 11 scorecard ----------
leaves(cue('question', L(20) - .05), .45, .04, .35, rate=650)
for i in range(3): S.place(out, knock(700 + 120 * i, .06), L(20) + .3 + i * .12, .055, -.2 + .2 * i)
for li in (21, 22):
    ty = cue(f'Yes (row {li - 20})', Wd(li, 'Yes') - .1); mar(ty, 74, .32, .25); mar(ty + .12, 79, .34, .25)
mar(cue('loans row outlined', Wd(23, 'loans') - .15), 55, .3, 0, 1.6)
t4 = cue('4 in 100 + coins', Wd(24, 'four') - .1)
for k in range(4): S.place(out, clink(rng.uniform(2700, 3200)), t4 + .05 + k * .1, .035, -.2 + .12 * k)
S.place(out, clink(2300, .25), t4 + .45, .016, .3)
leaves(cue('footer chip', L(25) - .05), .45, .035, .35, rate=600)

# ---------- 12 sign-off ----------
leaves(cue('GilB', Wd(26, 'Gil') - .1), 1.1, .06, .35, rate=700, pan0=-.6, pan1=.6)

# ---------- field-wind bed: faint, up in the open moments (hook, "shrinking?", the bank-loans note, sign-off) ----------
n = N; t = np.arange(n) / SR
wind = np.stack([S.bp(rng.standard_normal(n), 180, 900), S.bp(rng.standard_normal(n), 180, 900)], 1)
lfo = .55 + .45 * np.sin(2 * np.pi * t / 7.3) * np.sin(2 * np.pi * t / 3.1 + 1)
far = np.stack([S.bp(_grains(n, 35 * lfo, .0012), 2500, 7000), S.bp(_grains(n, 35 * lfo, .0012), 2500, 7000)], 1)
bed = wind / np.abs(wind).max() * .5 + far / np.abs(far).max() * .5
lvl = np.full(n, .25)
for a, b in [(0, SCENES[1][0] + .3), (L(12) - .3, L(14)), (L(19) - .3, L(20)), (L(26) - .5, TOTAL)]:
    lvl[int(a * SR):int(b * SR)] = 1.0
k = int(1.2 * SR); lvl = np.convolve(np.pad(lvl, (k, k), mode='edge'), np.ones(k) / k, 'same')[k:-k]
amb = bed * (lvl * lfo)[:, None]
amb *= np.clip(t / 1.0, 0, 1)[:, None] * np.clip((TOTAL - t) / 2.0, 0, 1)[:, None]

out = S.reverb(out, S.make_ir(1.1, .01, 7500, 300, 1.0, 66), .18)
pk = np.abs(out).max(); out *= .9 / pk if pk > .9 else 1
sf.write("/home/claude/gilb006_audio/sfx_bus.wav", out.astype(np.float32), SR, subtype="FLOAT")
sf.write("/home/claude/gilb006_audio/amb_bus.wav", (amb / (np.abs(amb).max() + 1e-9) * .5).astype(np.float32), SR, subtype="FLOAT")
json.dump(sorted(LOG), open('/home/claude/gilb006_audio/sfx_cues.json', 'w'), indent=0)
print("sfx peak", round(20 * np.log10(np.abs(out).max() + 1e-9), 1), "dBFS;", len(LOG), "named cues")
