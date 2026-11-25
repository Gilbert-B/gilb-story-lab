"""Original score for GILB-006 "Four Cedis in a Hundred" — "Field & Ledger".
Warm, light acoustic in G major at ~98 BPM with a highlife lilt: kalimba motif, nylon-guitar picking, round acoustic bass,
hand drums (congas, shaker, claves, cabasa) and a soft pad. Bar 42 lands on "Unpacked".
Story map: hook (kalimba + pad) / the test (percussion enters) / tests 1-2 (groove) / test 3 (thinner) / "Four." (everything stops,
one low note) / "shrinking?" (pad only) / "It isn't" -> growth and loans (groove returns) / share fell (thin) / bank-loans-only note (pad) /
scorecard (motif returns, light) / loans row (held chord, no drums) / "Even in a year" (gentle return) / sign-off."""
import sys, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/scripts"); sys.path.insert(0, "/home/claude/gilb006_audio")
import synth as S
from cues import Wd, WdE, L, LE, TOTAL
import tinysoundfont
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, PeakFilter, HighShelfFilter, Compressor
import pyloudnorm as pyln
SR = S.SR; N = int(TOTAL * SR)
SF2 = "/home/claude/work/sf/gu/package/GeneralUser.sf2"
BAR = Wd(26, 'Unpacked') / 42; BEAT = BAR / 4; SIX = BEAT / 4
def T(bar, beat=0.0): return bar * BAR + beat * BEAT
CH = {  # bass root, pad voicing, guitar/kalimba tones (low->high)
    "G":    (43, [55, 59, 62, 69], [55, 59, 62, 67, 71]),
    "C":    (36, [52, 55, 60, 62], [55, 60, 64, 67, 72]),
    "D":    (38, [54, 57, 62, 64], [57, 62, 66, 69, 74]),
    "Em":   (40, [52, 55, 59, 62], [52, 55, 59, 64, 67]),
    "Am7":  (45, [52, 55, 57, 60], [57, 60, 64, 67, 69]),
    "Cmaj7": (36, [52, 55, 59, 60], [55, 59, 60, 64, 67]),
    "Dsus": (38, [55, 57, 62, 64], [57, 62, 64, 67, 69]),
}
A = ["G", "C", "G", "D"]
SECTIONS = [  # (bar0, bar1, chord loop, flags)
    (0, 2, ["G", "C"], dict(pad=1, kal=1)),                                                         # hook
    (2, 4, ["Em", "D"], dict(pad=1, kal=.6, bass=0, shaker=.5, clave=.6)),                           # the test, three numbers
    (4, 14, A + A + ["Em", "D"], dict(pad=1, gtr=1, bass=2, conga=1, shaker=1, clave=1, kick=.8, cab=1)),  # tests 1 and 2
    (14, 19, ["Em", "C", "Em", "C", "D"], dict(pad=1, bass=0, shaker=.5, conga=.5, kal=.4, cut=1.75)),     # test 3 -> stop before "Four."
    (20, 22, ["Am7", "Cmaj7"], dict(pad=.8, q=1)),                                                    # shrinking?
    (22, 29, A + ["Em", "C", "D"], dict(pad=1, gtr=1, bass=2, conga=1, shaker=1, clave=1, kick=.9, cab=1)),  # It isn't -> growth, loans
    (29, 32, ["Em", "C", "Dsus"], dict(pad=1, bass=0, kal=.5, desc=1, shaker=.35)),                  # share fell
    (32, 34, ["C", "Dsus"], dict(pad=.8)),                                                            # bank loans only
    (34, 38, A, dict(pad=1, kal=.8, bass=1, conga=.5, shaker=.6, clave=.5)),                          # scorecard
    (38, 40, ["Em", "Em"], dict(pad=1, hold=1, bass=0)),                                              # the loans row
    (40, 42, ["C", "D"], dict(pad=1, gtr=.6, bass=1, shaker=.6, kal=.5)),                             # even in a year
    (42, 45, ["G", "G", "G"], dict(pad=1, final=1)),                                                  # sign-off
]
ENERGY = {0: -3.0, 2: -3.5, 4: -3.0, 9: -2.5, 14: -4.0, 19: -5.0, 20: -5.5, 22: -2.5, 26: -2.0, 29: -4.0, 32: -5.5, 34: -3.5, 38: -4.0, 40: -3.0, 42: -2.5}
notes = {k: [] for k in ["pad", "kal", "gtr", "bass", "str", "mar"]}
perc = []        # (t, midi drum note, velocity)
drum = {"kick": []}
def add(stem, t, d, m, v):
    if t < TOTAL: notes[stem].append((t, d, m, int(np.clip(v, 1, 127))))
MOTIF = [(0, 74), (.5, 71), (1, 67), (2, 69), (2.5, 71), (3, 74), (4, 76), (4.5, 74), (5, 71), (6, 69), (7, 67)]
GTR = [(0, 0, 1.0), (3, 2, .7), (4, 1, .85), (6, 3, .7), (8, 2, .95), (11, 4, .7), (12, 3, .85), (14, 1, .7)]   # 16th, tone, vel
for (b0, b1, loop, f) in SECTIONS:
    for bi in range(b0, b1):
        name = loop[(bi - b0) % len(loop)]; root, pad, tones = CH[name]; t0 = T(bi)
        last = bi == b1 - 1; cut = f.get("cut") if last else None          # stop point (beats) inside the last bar
        ok = lambda beat: cut is None or beat < cut
        if f.get("pad"):
            d = BAR + .25 if ok(4) else cut * BEAT + .1
            for m in pad: add("pad", t0, d, m, int((54 if not f.get("hold") else 60) * f["pad"]))
        if f.get("hold"):
            for m in (71, 79): add("str", t0, BAR + .2, m, 44)
        if f.get("kal"):
            ph = (bi - b0) % 2
            for (b, m) in MOTIF:
                if ph * 4 <= b < ph * 4 + 4 and ok(b - ph * 4): add("kal", t0 + (b - ph * 4) * BEAT, BEAT * 1.6, m, int(72 * f["kal"]))
        if f.get("q"):            # tentative two-note questions
            add("kal", t0 + 2 * BEAT, BEAT * 1.5, tones[3], 50); add("kal", t0 + 3 * BEAT, BEAT * 2, tones[4], 44)
        if f.get("desc"):
            for k, b in enumerate((0, 1, 2, 3)): add("kal", t0 + b * BEAT, BEAT * 1.4, tones[4 - k], 56 - 4 * k)
        if f.get("gtr"):
            for (s, ti, v) in GTR:
                if ok(s / 4): add("gtr", t0 + s * SIX, SIX * 2.2, tones[ti], int(66 * v * f["gtr"]))
        if f.get("bass") == 0:
            add("bass", t0, (BAR if ok(4) else cut * BEAT) * .97, root, 80)
        elif f.get("bass") == 1:
            for off, d, dm in ((0, 1.8, 0), (2.5, .4, 0), (3, .9, 7)): add("bass", t0 + off * BEAT, d * BEAT, root + dm, 92 if off == 0 else 76)
        elif f.get("bass") == 2:
            for off, d, dm in ((0, .7, 0), (.75, .22, 0), (1.5, .45, 7), (2, .7, 0), (3, .45, 7), (3.5, .4, 12)):
                if ok(off): add("bass", t0 + off * BEAT, d * BEAT, root + dm, 96 if off in (0, 2) else 78)
        if f.get("kick"):
            for b in (0, 2):
                if ok(b): drum["kick"].append((t0 + b * BEAT, f["kick"]))
        if f.get("shaker"):
            for s in range(16):
                if not ok(s / 4): continue
                if f["shaker"] < 1 and s % 2: continue
                perc.append((t0 + s * SIX, 70, (68 if s % 4 == 2 else 46 if s % 2 == 0 else 34) * min(1, f["shaker"] + .2)))
        if f.get("clave"):
            for s in ((0, 3, 6) if bi % 2 == 0 else (4, 8)):          # 3-2 son clave across two bars
                if ok(s / 4): perc.append((t0 + s * SIX, 75, 46 * f["clave"]))
        if f.get("cab"):
            for s in (2, 6, 10, 14):
                if ok(s / 4): perc.append((t0 + s * SIX, 69, 40))
        if f.get("conga"):
            for s, m, v in ((0, 64, 70), (2, 62, 48), (6, 63, 72), (7, 63, 50), (8, 64, 60), (10, 62, 48), (11, 64, 56), (14, 63, 74)):
                if ok(s / 4): perc.append((t0 + s * SIX, m, v * f["conga"]))
        if f.get("final") and bi == b0:
            for k, m in enumerate([67, 71, 74, 79, 83, 86]): add("kal", t0 + k * .11, 3.6, m, 80 - 4 * k)
            for (b, m) in MOTIF[:6]: add("mar", t0 + BAR + b * BEAT, BEAT * 1.4, m - 12, 50)
# "Four.": a single low note in the silence
t4 = L(11) - .02
add("mar", t4, 2.2, 43, 92); add("bass", t4, 2.0, 31, 70); add("pad", t4 + .1, 1.6, 55, 30)
# the kalimba motif returns on "Unpacked" (already in final), and once on the scorecard question
def render_sf(prog, nl, bank=0, drums=False):
    syn = tinysoundfont.Synth(gain=0, samplerate=SR); sfid = syn.sfload(SF2); syn.program_select(0, sfid, bank, prog, drums)
    ev = sorted([(t, 1, m, v) for (t, d, m, v) in nl] + [(t + d, 0, m, 0) for (t, d, m, v) in nl], key=lambda e: (e[0], e[1]))
    out = np.zeros((N, 2), np.float32); pos = 0
    for (t, on, m, v) in ev:
        i = min(int(t * SR), N)
        if i > pos: out[pos:i] = np.frombuffer(syn.generate(i - pos), np.float32).reshape(-1, 2); pos = i
        if on: syn.noteon(0, m, v)
        else: syn.noteoff(0, m)
    if pos < N: out[pos:] = np.frombuffer(syn.generate(N - pos), np.float32).reshape(-1, 2)
    return out.astype(np.float64)
PROG = {"pad": 89, "kal": 108, "gtr": 24, "bass": 32, "str": 49, "mar": 12}
stems = {k: render_sf(PROG[k], nl) for k, nl in notes.items() if nl}
stems["perc"] = render_sf(0, [(t, .12, m, int(v)) for (t, m, v) in perc], bank=128, drums=True)
print({k: len(v) for k, v in notes.items()}, "perc", len(perc), "kick", len(drum["kick"]))
K = S.kick(tone=52, punch=95, dec=.28, click=.03)
kick_bus = np.zeros((N, 2)); kenv = np.zeros(N)
for (t, v) in drum["kick"]:
    S.place(kick_bus, K, t, .55 * v); i = int(t * SR); kenv[i:i + int(.16 * SR)] = np.maximum(kenv[i:i + int(.16 * SR)], v)
def pb(x, fx): return Pedalboard(fx)(x.T.astype(np.float32), SR).T.astype(np.float64)
IR = S.make_ir(2.2, .018, 6500, 180, 1.0, 61); IR_R = S.make_ir(.7, .006, 8000, 220, .9, 62)
ke = np.convolve(kenv, np.hanning(int(.03 * SR)) / (.015 * SR), "same"); pump = (1 - .15 * np.clip(ke, 0, 1))[:, None]
P = {}
P["pad"] = S.reverb(pb(stems["pad"], [HighpassFilter(150), LowpassFilter(5500), PeakFilter(2600, -3, .7)]), IR, .3) * pump
P["str"] = S.reverb(pb(stems["str"], [HighpassFilter(200), LowpassFilter(6000)]), IR, .4)
P["kal"] = S.reverb(pb(stems["kal"], [HighpassFilter(300), PeakFilter(3000, -2, .8), HighShelfFilter(9000, -1.5, .7)]), IR, .32)
P["gtr"] = S.reverb(pb(stems["gtr"], [HighpassFilter(180), PeakFilter(2800, -2.5, .8), LowpassFilter(8000)]), IR_R, .22) * pump
P["bass"] = pb(stems["bass"], [HighpassFilter(35), LowpassFilter(900)]) * pump
P["mar"] = S.reverb(pb(stems["mar"], [HighpassFilter(60)]), IR, .38)
P["perc"] = S.reverb(pb(stems["perc"], [HighpassFilter(90), PeakFilter(3200, -2, .8), LowpassFilter(11000)]), IR_R, .18)
P["kick"] = pb(kick_bus, [HighpassFilter(35), LowpassFilter(4000)])
GAIN = {"pad": .55, "str": .35, "kal": .62, "gtr": .55, "bass": .7, "mar": .7, "perc": .55, "kick": .6}
mus = sum(P[k] * GAIN[k] for k in P)
gdb = np.zeros(N); starts = sorted(ENERGY)
for i, b in enumerate(starts):
    i0 = int(T(b) * SR); i1 = int(T(starts[i + 1]) * SR) if i + 1 < len(starts) else N
    gdb[i0:i1] = ENERGY[b]
k = int(.5 * SR); gdb = np.convolve(np.pad(gdb, (k, k), mode="edge"), np.ones(k) / k, "same")[k:-k]
t = np.arange(N) / SR
mus *= (10 ** (gdb / 20))[:, None]
# the drop before "Four.": whatever still rings is pulled down quickly, then the single note speaks
td0, td1 = T(19, 1.75), L(11) - .05
g = np.ones(N); i0, i1 = int(td0 * SR), int(td1 * SR); g[i0:i1] = np.linspace(1, .12, i1 - i0); g[i1:int((L(11) + 2.5) * SR)] = .12
low = P["mar"] * GAIN["mar"] * (10 ** (gdb / 20))[:, None]          # keep the "Four." marimba note itself at full level
mus = (mus - low) * g[:, None] + low
mus *= np.clip(t / .5, 0, 1)[:, None]
mus *= np.clip((TOTAL - t) / 2.8, 0, 1)[:, None] ** 1.3
mus = pb(mus, [PeakFilter(2800, -2.5, .6), Compressor(threshold_db=-18, ratio=2.0, attack_ms=25, release_ms=220)])
m = pyln.Meter(SR); Lm = m.integrated_loudness(mus[:int((TOTAL - 4) * SR)]); mus *= 10 ** ((-16 - Lm) / 20)
pk = np.abs(mus).max()
if pk > .95: mus *= .95 / pk
sf.write("/home/claude/gilb006_audio/music_bus.wav", mus.astype(np.float32), SR, subtype="FLOAT")
print(f"music LUFS {m.integrated_loudness(mus[:int((TOTAL - 4) * SR)]):.1f}, BPM {240 / BAR:.2f}, bar {BAR:.3f}s, TOTAL {TOTAL}")
for name, b in [('test', 2), ('tests 1-2 groove', 4), ('test 3', 14), ('stop', 19.44), ('shrinking?', 20), ('groove returns', 22), ('share fell', 29), ('bank loans only', 32), ('scorecard', 34), ('loans row hold', 38), ('even in a year', 40), ('Unpacked', 42)]:
    print(f'  bar {b:>5}: {T(b):6.2f}s  {name}')
