"""
GILB Lake Volta episode: original music bed + sound effects, synthesised from scratch in code
(no samples, loops, presets or third-party audio). Deterministic (fixed random seeds).

Outputs (48 kHz, float32 stereo WAV):
  public/music_bed_v1.wav   music, already ducked under the narration
  public/sfx_v1.wav         sound effects, placed on the episode's animation events
Mixing with the untouched narration is done by audio/mix.sh (ffmpeg).

Run:  python audio/make_audio.py
"""
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
FPS = 30
DUR = 3581 / FPS  # episode length, s
N = int(round(DUR * SR))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(20261116)


# ---------------------------------------------------------------- helpers
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def tv_lowpass(x, fc):
    """one-pole low-pass with a per-sample cutoff (Hz)"""
    a = np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def reverb_ir(seconds, decay, seed):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    env = np.exp(-tt(n) * (6.9 / decay))
    ir = np.stack([r.standard_normal(n), r.standard_normal(n)], 1) * env[:, None]
    ir[:, 0] = lp(ir[:, 0], 6000)
    ir[:, 1] = lp(ir[:, 1], 6000)
    return ir / np.sqrt((ir ** 2).sum(0))


def add(buf, sig, t0, pan=0.0, gain=1.0):
    """add mono (or stereo) sig into stereo buf at time t0 (s), equal-power pan -1..1"""
    i0 = int(round(t0 * SR))
    if sig.ndim == 1:
        th = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(th), sig * np.sin(th)], 1) * np.sqrt(2)
    if i0 < 0:
        sig, i0 = sig[-i0:], 0
    n = min(len(sig), len(buf) - i0)
    if n > 0:
        buf[i0:i0 + n] += sig[:n] * gain


def auto(points, n=N):
    """automation curve from [(t, value), ...]"""
    p = np.array(points, float)
    return np.interp(tt(n), p[:, 0], p[:, 1])


# ---------------------------------------------------------------- music
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT  # 2.5 s
# i–VI–III–VII in D minor, one chord per bar (voicings, MIDI)
CHORDS = [
    [50, 53, 57, 60, 64],  # Dm9
    [46, 50, 53, 57, 62],  # Bbmaj7(add9)
    [48, 53, 57, 60, 64],  # Fmaj7/C
    [48, 52, 55, 62, 67],  # Cadd9
]
ROOTS = [38, 34, 41, 36]
OUTRO_T = 115.40  # "Unpacked by GilB"

# section levels (0..1) for each layer — follows the story's arc
PAD = auto([(0, 0), (1.2, 0.8), (14.3, 0.8), (14.3, 1), (26.9, 1), (27.15, 0.15), (28.6, 0.15), (29.2, 1),
            (105.7, 1), (112.6, 0.5), (112.95, 0.9), (OUTRO_T, 0.9), (DUR, 0.9)])
SUB = auto([(0, 0), (7.4, 0), (8.6, 0.8), (26.9, 0.8), (27.12, 0), (28.7, 0), (29.0, 1), (105.6, 1),
            (106.4, 0.6), (112.6, 0.6), (112.95, 0), (DUR, 0)])
ARP = auto([(0, 0.55), (14.3, 0.55), (26.9, 0.7), (27.12, 0), (28.7, 0), (29.2, 0.7), (59.0, 0.7),
            (60.0, 0.9), (90.9, 0.9), (105.6, 0.8), (106.2, 0), (DUR, 0)])
KICK = auto([(0, 0), (14.2, 0), (14.4, 0.7), (26.9, 0.7), (27.0, 0), (28.75, 0), (28.8, 1), (59.0, 1),
             (59.2, 0.45), (90.8, 0.45), (90.9, 1), (105.6, 1), (105.7, 0), (DUR, 0)])
HAT = auto([(0, 0), (14.2, 0), (14.4, 0.6), (26.9, 0.6), (27.0, 0), (28.75, 0), (28.8, 1), (90.9, 1),
            (91.0, 1.15), (105.6, 1.15), (105.7, 0), (DUR, 0)])
BRIGHT = auto([(0, 900), (14.3, 1300), (28.8, 1800), (59.0, 1500), (90.9, 2600), (105.7, 1100),
               (112.9, 2400), (DUR, 1600)])


def pad_voice(m, n, seed):
    r = np.random.default_rng(seed)
    t = tt(n)
    out = np.zeros(n)
    for det in (-7, 0, 6):  # cents
        f = mtof(m) * 2 ** (det / 1200)
        ph = r.uniform(0, 2 * np.pi)
        # soft saw from 7 harmonics
        for h in range(1, 8):
            out += np.sin(2 * np.pi * f * h * t + ph * h) / h ** 1.3
    return out / 3


def build_music():
    L = np.zeros(N)
    R = np.zeros(N)
    pad = np.zeros((N, 2))
    nbars = int(np.ceil(DUR / BAR)) + 1
    att, rel = 0.9, 1.4
    for b in range(nbars):
        t0 = b * BAR
        if t0 >= OUTRO_T:
            break
        chord = CHORDS[b % 4]
        end = min(t0 + BAR, OUTRO_T) if t0 + BAR > OUTRO_T else t0 + BAR
        n = int((end - t0 + rel) * SR)
        env = np.minimum(1, tt(n) / att) * np.clip((end - t0 + rel - tt(n)) / rel, 0, 1)
        for j, m in enumerate(chord):
            v = pad_voice(m, n, b * 10 + j) * env * 0.11
            add(pad, v, t0 - 0.25, pan=(-0.55 + 0.275 * j))
    # outro: resolve on a held Dm(add9), long tail
    n = int((DUR - OUTRO_T + 0.5) * SR)
    env = np.minimum(1, tt(n) / 0.4) * np.clip((DUR - OUTRO_T - tt(n)) / 2.6, 0, 1) ** 1.5
    for j, m in enumerate([38, 50, 57, 64, 65, 69]):
        add(pad, pad_voice(m, n, 900 + j) * env * 0.11, OUTRO_T - 0.1, pan=(-0.6 + 0.24 * j))
    for c in range(2):
        pad[:, c] = tv_lowpass(pad[:, c], BRIGHT)
    pad *= PAD[:, None]

    # sub bass: root per bar, sine + touch of 2nd harmonic
    sub = np.zeros(N)
    for b in range(nbars):
        t0 = b * BAR
        if t0 >= DUR:
            break
        f = mtof(ROOTS[b % 4])
        n = int(BAR * SR)
        t = tt(n)
        env = np.minimum(1, t / 0.08) * np.exp(-t / 2.2)
        v = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * env * 0.32
        i0 = int(t0 * SR)
        k = min(n, N - i0)
        sub[i0:i0 + k] += v[:k]
    sub *= SUB

    # arpeggio: 8th-note pluck through chord tones (+1 oct), ping-pong
    arp = np.zeros((N, 2))
    step = BEAT / 2
    pattern = [0, 2, 4, 1, 3, 2, 4, 1]
    for s in range(int(DUR / step)):
        t0 = s * step
        if t0 >= OUTRO_T - 0.3:
            break
        chord = CHORDS[int(t0 // BAR) % 4]
        m = chord[pattern[s % 8]] + 12
        n = int(0.6 * SR)
        t = tt(n)
        f = mtof(m)
        v = (np.sin(2 * np.pi * f * t) + 0.18 * np.sin(6 * np.pi * f * t)) * np.exp(-t / 0.16) * np.minimum(1, t / 0.004)
        vel = 0.75 + 0.25 * (s % 2 == 0)
        add(arp, v * 0.07 * vel, t0, pan=(0.45 if s % 2 else -0.45))
    arp *= ARP[:, None]

    # kick (soft, no click) on beats 1 & 3; closed hat on off-beats
    drums = np.zeros((N, 2))
    nk = int(0.45 * SR)
    t = tt(nk)
    fk = 46 + 70 * np.exp(-t / 0.03)
    kick = np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-t / 0.16) * 0.42
    nh = int(0.08 * SR)
    hat_src = hp(rng.standard_normal(nh), 7500, 4) * np.exp(-tt(nh) / 0.018) * 0.05
    for bt in range(int(DUR / BEAT)):
        t0 = bt * BEAT
        if bt % 2 == 0:
            add(drums, kick * KICK[min(int(t0 * SR), N - 1)], t0)
        th = t0 + BEAT / 2
        if th < DUR:
            add(drums, hat_src * HAT[min(int(th * SR), N - 1)] * (1.0 if bt % 2 else 0.7), th, pan=0.25)

    mus = pad + arp + drums
    mus[:, 0] += sub
    mus[:, 1] += sub
    # shared room
    ir = reverb_ir(2.6, 2.2, 7)
    wet = np.stack([fftconvolve(pad[:, 0] + arp[:, 0], ir[:, 0])[:N], fftconvolve(pad[:, 1] + arp[:, 1], ir[:, 1])[:N]], 1)
    mus = mus + 0.35 * wet
    mus[:, 0] = hp(mus[:, 0], 30)
    mus[:, 1] = hp(mus[:, 1], 30)
    return mus


# ---------------------------------------------------------------- ducking under narration
def duck_gain(narr, depth_db=9.0):
    hop = int(0.01 * SR)
    frames = len(narr) // hop
    rms = np.sqrt(np.mean(narr[: frames * hop].reshape(frames, hop) ** 2, 1) + 1e-12)
    db = 20 * np.log10(rms)
    target = -depth_db * np.clip((db + 48) / 14, 0, 1)  # full duck once speech is clearly present
    g = np.zeros(frames)
    s = 0.0
    a_att, a_rel = np.exp(-1 / 4), np.exp(-1 / 40)  # 40 ms attack, 400 ms release (in 10 ms frames)
    # look-ahead 60 ms so the duck starts just before each phrase
    target = np.concatenate([target[6:], np.zeros(6)])
    for i in range(frames):
        a = a_att if target[i] < s else a_rel
        s = a * s + (1 - a) * target[i]
        g[i] = s
    gl = np.interp(np.arange(N) / hop, np.arange(frames), g)
    return 10 ** (gl / 20)


# ---------------------------------------------------------------- sound effects
def s_whoosh(d=0.55, peak=0.6, lo=300, hi=5000, gain=0.12):
    n = int(d * SR)
    x = rng.standard_normal(n)
    u = tt(n) / d
    env = np.where(u < peak, (u / peak) ** 2, ((1 - u) / (1 - peak)) ** 1.6)
    fc = lo + (hi - lo) * np.where(u < peak, u / peak, (1 - u) / (1 - peak))
    return hp(tv_lowpass(x, fc), 120) * env * gain


def s_tick(pitch=2400, gain=0.05):
    n = int(0.03 * SR)
    t = tt(n)
    return (np.sin(2 * np.pi * pitch * t) * np.exp(-t / 0.006) + 0.3 * rng.standard_normal(n) * np.exp(-t / 0.002)) * gain


def s_pop(f0=980, f1=520, gain=0.12):
    n = int(0.16 * SR)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.025)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.045) * np.minimum(1, t / 0.002) * gain


def s_chime(m=74, gain=0.09, d=1.6):
    n = int(d * SR)
    t = tt(n)
    f = mtof(m)
    x = np.zeros(n)
    for ratio, amp, dec in [(1, 1, 0.9), (2.0, 0.35, 0.5), (2.76, 0.25, 0.35), (5.4, 0.1, 0.15)]:
        x += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t / dec)
    return x * np.minimum(1, t / 0.003) * gain


def s_impact(gain=0.32, d=1.4):
    n = int(d * SR)
    t = tt(n)
    f = 34 + 60 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    noise = lp(rng.standard_normal(n), 900) * np.exp(-t / 0.08) * 0.5
    return (body + noise) * np.minimum(1, t / 0.002) * gain


def s_water(d, gain=0.05, seed=1):
    r = np.random.default_rng(seed)
    n = int(d * SR)
    t = tt(n)
    u = t / d
    base = bp(np.cumsum(r.standard_normal(n)) * 0.02, 180, 1400)
    env = np.sin(np.pi * np.clip(u, 0, 1)) ** 0.7
    x = base * env * 4
    # gentle bubbles: short rising sine chirps
    for _ in range(int(d * 9)):
        bt = r.uniform(0, d - 0.06)
        bn = int(r.uniform(0.02, 0.05) * SR)
        bt_ = tt(bn)
        f = r.uniform(380, 900) * (1 + 1.5 * bt_ / (bn / SR))
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * bt_ / (bn / SR)) * r.uniform(0.15, 0.4)
        i0 = int(bt * SR)
        x[i0:i0 + bn] += b * env[i0:i0 + bn].mean()
    return x * gain


def s_riser(d=3.2, gain=0.11):
    n = int(d * SR)
    t = tt(n)
    u = t / d
    noise = tv_lowpass(rng.standard_normal(n), 200 + 6000 * u ** 2)
    tone = np.sin(2 * np.pi * np.cumsum(110 + 330 * u ** 2) / SR) * 0.25
    return hp(noise + tone, 150) * u ** 2.2 * gain


def s_sparkle(base=86, gain=0.05):
    out = np.zeros(int(0.9 * SR))
    for k, m in enumerate([base, base + 3, base + 7, base + 12]):
        c = s_chime(m, gain, d=0.6)
        i0 = int(k * 0.055 * SR)
        out[i0:i0 + len(c)] += c[: len(out) - i0]
    return out


# ---------------------------------------------------------------- event timeline
# scene starts (episode frames) and proof time-warp anchors — mirror src/Episode.tsx
SC = dict(open=0, kariba=430, question=699, poly=858, kcap=1386, gap=1588, avd=1770, verdict=2727,
          both=3027, callback=3170, outro=3448)
WARP = {
    "open": [[0, 0], [125, 104], [263, 212], [318, 300], [378, 400], [438, 420]],
    "poly": [[0, 0], [125, 60], [216, 112], [272, 134], [320, 186], [437, 392], [470, 440], [536, 480]],
    "avd": [[0, 0], [73, 10], [133, 105], [182, 135], [231, 195], [278, 222], [332, 300], [376, 326], [470, 386],
            [530, 440], [600, 500], [625, 505], [738, 560], [766, 562], [828, 590], [840, 600], [885, 650], [890, 660],
            [910, 676], [965, 720]],
}


def T(scene, local):
    """episode seconds for a scene-local (proof) frame"""
    if scene in WARP:
        a = np.array(WARP[scene], float)
        local = np.interp(local, a[:, 1], a[:, 0])
    return (SC[scene] + local) / FPS


def ticks(buf, scene, f0, f1, count, p0=1900, p1=2900, gain=0.045):
    for i in range(count):
        u = i / max(1, count - 1)
        add(buf, s_tick(p0 + (p1 - p0) * u, gain), T(scene, f0 + (f1 - f0) * u), pan=0.15)


def build_sfx():
    fx = np.zeros((N, 2))
    # scene transitions: soft air
    for sc in ["kariba", "question", "poly", "kcap", "gap", "avd", "verdict", "both", "callback"]:
        add(fx, s_whoosh(), SC[sc] / FPS - 0.33, pan=0.0)
    # opening
    add(fx, s_whoosh(1.4, 0.75, 120, 1800, 0.08), 0.0)
    add(fx, s_sparkle(), T("open", 104))  # asterisk
    add(fx, s_water(T("open", 252) - T("open", 168), 0.05, 2), T("open", 168), pan=-0.1)  # lake floods
    add(fx, s_pop(700, 380, 0.08), T("open", 196))  # dam marker
    add(fx, s_pop(), T("open", 306))  # first 1,000 km² square
    add(fx, s_whoosh(0.4, 0.5, 600, 4000, 0.06), T("open", 334))
    ticks(fx, "open", 352, 400, 8)
    add(fx, s_chime(74), T("open", 400))  # 8,500
    # Kariba intro
    add(fx, s_whoosh(1.6, 0.55, 150, 3200, 0.09), SC["kariba"] / FPS)  # map flight
    add(fx, s_water((118 - 64) / FPS, 0.05, 3), T("kariba", 64), pan=0.1)
    add(fx, s_pop(700, 380, 0.08), T("kariba", 96))
    add(fx, s_pop(), T("kariba", 120))
    add(fx, s_whoosh(0.4, 0.5, 600, 4000, 0.06), T("kariba", 142))
    ticks(fx, "kariba", 160, 196, 5)
    add(fx, s_chime(69), T("kariba", 196))  # 5,600
    # question → "Not quite."
    add(fx, s_whoosh(0.35, 0.3, 1500, 7000, 0.05), T("question", 112))  # strike
    add(fx, s_impact(0.24), T("question", 116))
    # Polytank
    ticks(fx, "poly", 6, 54, 10)
    add(fx, s_chime(74), T("poly", 54))  # 148
    add(fx, s_water((176 - 134) / FPS, 0.06, 4), T("poly", 134))  # tank fills
    add(fx, s_whoosh(0.5, 0.4, 2000, 300, 0.07), T("poly", 186))  # tank shrinks
    for f, m in [(204, 79), (226, 81), (272, 83)]:
        add(fx, s_pop(1100, 600, 0.07), T("poly", f), pan=0.2)
    for f in (302, 340, 374):
        add(fx, s_whoosh(0.35, 0.6, 400, 3500, 0.05), T("poly", f))
    ticks(fx, "poly", 392, 440, 12, 1800, 3200)
    add(fx, s_chime(76, 0.1), T("poly", 440))  # 29.6 billion
    # Kariba capacity
    add(fx, s_water((124 - 40) / FPS, 0.06, 5), T("kcap", 40))
    ticks(fx, "kcap", 52, 122, 14)
    add(fx, s_impact(0.2, 1.0), T("kcap", 122))
    add(fx, s_chime(76), T("kcap", 122))  # 181
    add(fx, s_pop(), T("kcap", 150))  # 181 trillion litres
    # capacity gap
    ticks(fx, "gap", 34, 72, 9, 2200, 3200)
    add(fx, s_chime(79), T("gap", 72))  # +33
    add(fx, s_whoosh(0.5, 0.5, 400, 3000, 0.05), T("gap", 108))
    add(fx, s_pop(), T("gap", 134))  # LESS AREA
    # area vs depth
    add(fx, s_water(66 / FPS, 0.055, 6), T("avd", 300), pan=-0.3)
    add(fx, s_water(66 * 181 / 148 / FPS, 0.055, 7), T("avd", 300), pan=0.3)
    add(fx, s_chime(74), T("avd", 386))  # more water
    add(fx, s_whoosh(0.7, 0.5, 200, 2500, 0.06), T("avd", 458))
    add(fx, s_whoosh(0.5, 0.5, 300, 2500, 0.05), T("avd", 600))  # gauges
    add(fx, s_pop(), T("avd", 660))  # ≈1.5×
    # verdict
    add(fx, s_impact(0.22, 1.0), T("verdict", 8))
    add(fx, s_chime(74), T("verdict", 10))
    add(fx, s_impact(0.22, 1.0), T("verdict", 180))
    add(fx, s_chime(78), T("verdict", 182))
    # both enormous
    add(fx, s_pop(900, 500, 0.08), T("both", 80), pan=-0.25)
    add(fx, s_pop(800, 450, 0.08), T("both", 88), pan=0.25)
    # callback
    for i, f in enumerate([62, 74, 89, 104, 119]):
        add(fx, s_pop(600 + 40 * i, 320, 0.05), T("callback", f - 3))
    add(fx, s_sparkle(), T("callback", 150))
    add(fx, s_riser(3.0), T("callback", 212) - 3.0)
    add(fx, s_impact(0.34, 1.6), T("callback", 212))
    # outro sting
    add(fx, s_whoosh(0.9, 0.6, 200, 3500, 0.07), SC["outro"] / FPS - 0.5)
    add(fx, s_chime(74, 0.08, 2.4), OUTRO_T)
    add(fx, s_chime(81, 0.05, 2.4), OUTRO_T + 0.06)
    # light room on effects
    ir = reverb_ir(1.4, 1.0, 11)
    wet = np.stack([fftconvolve(fx[:, 0], ir[:, 0])[:N], fftconvolve(fx[:, 1], ir[:, 1])[:N]], 1)
    return fx + 0.2 * wet


def main():
    sr, narr = wavfile.read(os.path.join(ROOT, "public", "narration_v1.wav"))
    assert sr == SR
    narr = narr.astype(np.float64)
    narr /= np.abs(narr).max() if narr.dtype.kind == "f" else 2 ** 31
    narr = np.pad(narr if narr.ndim == 1 else narr.mean(1), (0, max(0, N - len(narr))))[:N]
    music = build_music() * duck_gain(narr)[:, None]
    sfx = build_sfx() * duck_gain(narr, 5.0)[:, None]  # effects sit back under speech too
    for name, x in [("music_bed_v1.wav", music), ("sfx_v1.wav", sfx)]:
        wavfile.write(os.path.join(ROOT, "public", name), SR, x.astype(np.float32))
        print(name, "peak", round(20 * np.log10(np.abs(x).max()), 1), "dBFS")


if __name__ == "__main__":
    main()
