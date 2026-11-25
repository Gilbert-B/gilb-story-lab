# GILB-006 · Four Cedis in a Hundred · Audio V1

- `stems/GILB006_final_audio.wav`: the finished soundtrack (voice + music + effects + field bed), 48 kHz / 24-bit, −14 LUFS integrated, −1.2 dBTP, 1:49.6, starts 0.5 s before the first word (matches the picture).
- `stems/GILB006_music_bus.wav`, `GILB006_sfx_bus.wav`, `GILB006_amb_bus.wav`: the separate layers before ducking and mixing, for re-balancing in an editor.
- `sfx_cues.json`: every named effect and its time in the video.

**Music, "Field & Ledger":** original, ~98 BPM in G major with a light highlife lilt: kalimba motif, nylon-guitar picking, acoustic bass, congas / shaker / claves / cabasa, soft pad. It stops dead before "Four." (one low marimba note in the silence), sits on the pad for "shrinking?" and the bank-loans note, holds one chord under "But of the loans…", and lands bar 42 on "Unpacked".

**Effects:** dry-leaf rustles on every scene change and reveal instead of whooshes and swishes; wooden seed knocks for the maize kernels, score rows and counters; soft coin clinks for the cedi grids (four and a half clinks for 4.3); marimba / kalimba notes in the score's key for the checks and growth bars; a stamp thud with a leaf crunch on "It isn't"; a faint field-wind bed that comes up in the open moments.

**Mix:** music −9.5 dB with 6 dB ducking under the voice, effects +7 dB (3 dB ducking), wind bed −15 dB. Voice sits about 16 dB above the music during speech.

`scripts/`: `score6.py` (music), `sfx6.py` (effects), `mix6.py` (mix: `python3 mix6.py <music dB> <duck dB> <sfx dB> <wind dB>`), `cues.py` (word-anchored cue times from the storyboard's timing.json).
