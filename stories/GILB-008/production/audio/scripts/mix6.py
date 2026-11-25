"""GILB-006 final mix: voice master (untouched, +0.5 s) + ducked music bed + SFX + faint field-wind bed -> -14 LUFS, -1.2 dBTP."""
import sys, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/scripts")
from dsp import limiter, true_peak_db
import numba
from pedalboard import Pedalboard, Compressor, HighShelfFilter, HighpassFilter
import pyloudnorm as pyln
SR = 48000; DUR = 109.6; N = int(round(DUR * SR)); PRE = 0.5
MUSIC_DB = float(sys.argv[1]) if len(sys.argv) > 1 else -9.0
DUCK_DB = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
SFX_DB = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
AMB_DB = float(sys.argv[4]) if len(sys.argv) > 4 else -14.0
def load(p):
    x, sr = sf.read(p); assert sr == SR, (p, sr)
    if x.ndim == 1: x = np.stack([x, x], 1)
    x = np.concatenate([x, np.zeros((max(0, N - len(x)), 2))])[:N]; return x
v = sf.read("/mnt/user-data/uploads/4134b559-GILB007_Four_Cedis_Voice_Master_V1.wav")[0]
if v.ndim > 1: v = v.mean(1)
v = Pedalboard([HighpassFilter(60)])(v.astype(np.float32)[None, :], SR)[0].astype(np.float64)
voice = np.zeros((N, 2)); i0 = int(PRE * SR); n = min(len(v), N - i0)
voice[i0:i0 + n, 0] = v[:n]; voice[i0:i0 + n, 1] = v[:n]
music = load("music_bus.wav"); sfx = load("sfx_bus.wav"); amb = load("amb_bus.wav")
@numba.njit
def follower(s, a, r):
    e = np.zeros_like(s); x = 0.0
    for i in range(len(s)):
        c = a if s[i] > x else r; x = c * x + (1 - c) * s[i]; e[i] = x
    return e
e = follower(np.abs(voice[:, 0]), np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.45 * SR)))
act = np.clip((20 * np.log10(e + 1e-9) + 45) / 15, 0, 1)
la = int(0.06 * SR); act = np.concatenate([act[la:], np.zeros(la)])
k = int(0.05 * SR); act = np.convolve(act, np.ones(k) / k, "same")
duck = 10 ** ((MUSIC_DB - DUCK_DB * act) / 20); sduck = 10 ** ((SFX_DB - 3.0 * act) / 20)
aduck = 10 ** ((AMB_DB - 4.0 * act) / 20)
mix = voice + music * duck[:, None] + sfx * sduck[:, None] + amb * aduck[:, None]
mix = Pedalboard([Compressor(threshold_db=-16, ratio=1.5, attack_ms=30, release_ms=250), HighShelfFilter(12000, 0.6, 0.7)])(mix.T.astype(np.float32), SR).T.astype(np.float64)
m = pyln.Meter(SR); L = m.integrated_loudness(mix); mix *= 10 ** ((-14.0 - L) / 20)
mix, g = limiter(mix, SR, ceiling_db=-1.2, lookahead_ms=2.0, release_ms=80)
t = np.arange(N) / SR; mix *= np.clip((DUR - t) / 0.6, 0, 1)[:, None] ** 1.5
L2 = m.integrated_loudness(mix)
sp = act > 0.8; mb = music * duck[:, None]; sb = sfx * sduck[:, None]
print(f"music {MUSIC_DB} duck {DUCK_DB} sfx {SFX_DB} amb {AMB_DB} -> {L2:.2f} LUFS, TP {true_peak_db(mix):.2f} dBTP, limiter GR>1dB {np.mean(g < .891) * 100:.2f}%")
vr = np.mean(voice[sp] ** 2)
print(f"voice vs bed during speech: {10 * np.log10(vr / np.mean(mb[sp] ** 2)):.1f} dB; bed in pauses {10 * np.log10(np.mean(mb[act < .1] ** 2) / vr):.1f} dB re speech; sfx peak re voice peak {20 * np.log10(np.abs(sb).max() / np.abs(voice).max()):.1f} dB")
sf.write("/home/claude/gilb006_audio/final_audio.wav", mix.astype(np.float32), SR, subtype="FLOAT")
ab = amb * aduck[:, None]
print(f"wind bed in pauses {10 * np.log10(np.mean(ab[act < .1] ** 2) / vr):.1f} dB re speech; music bed peak-to-voice in pauses {20*np.log10(np.abs(mb[act<.1]).max()/np.abs(voice).max()):.1f} dB")
