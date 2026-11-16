# Lake Volta episode — Phase A proofs: sources, assets, method

Status: **Final cut approved by GilB on 2026-11-16** (`out/GILB_LakeVolta_Episode_v2_music.mp4`, sha256 `bf17dae3…de0f9`). GilB confirmed everything was checked and approved: the script, on-screen statements, narration wording, music and effects mix, Akosombo position and sources. Not published, and not yet in the Story Registry.
Story ID: pending. `GILB-006` in the repo is currently the youth-employment idea, so GilB needs to decide the ID.

## Figures used (approved script V1.2)

| Figure | Value | Used in |
|---|---|---|
| Lake Volta surface area | 8,502 km² (shown as "8,500") | P1 |
| Lake Volta capacity | 148 km³ = 148 trillion L | P2, P3 |
| Lake Kariba capacity | 181 km³ | P3 (bar/volume ratio 148:181) |
| Mean depths | Volta 18.8 m, Kariba 29.2 m (≈1.5×) | P3 gauges |
| Tanks | 148×10¹² L ÷ 5,000 L = 29.6×10⁹ | P2 |

Reference publishers: Volta River Authority (VRA), Zambezi River Authority (ZRA), ILEC World Lake Database.
The exact pages and retrieval dates must be captured in the story's source records before publication.
These proofs did not download those publishers' pages.

## Data consistency warning

The published mean depths and capacities do not reconcile with the surface areas.

| Lake | Area × published mean depth | Published capacity | Capacity ÷ area |
|---|---|---|---|
| Volta | ≈160 km³ | 148 km³ | 17.4 m |
| Kariba | ≈163 km³ | 181 km³ | 32.4 m |

The cause is likely different water levels or survey dates between sources.

For that reason:

- the visuals never show area × depth = volume;
- the depth gauges are labelled "PUBLISHED MEAN DEPTHS · NOT SURVEYED LAKE PROFILES";
- the containers are labelled "ILLUSTRATION".

## Geometry

| Item | Source | Licence | Measured area |
|---|---|---|---|
| Lake Volta outline | Natural Earth 1:10m lakes v5 | Public domain | 7,994 km² (94% of 8,502) |
| Lake Kariba outline | OpenStreetMap relation 318675 (via Nominatim) | ODbL 1.0, "© OpenStreetMap contributors" | 5,371 km² (96% of 5,580) |
| Countries and rivers | Natural Earth 1:10m admin-0 and rivers | Public domain | — |

Why this pair:

- OSM Volta was rejected because it measures only 6,692 km².
- Natural Earth Kariba was rejected because it measures only 4,724 km².
- The chosen pair has a measured area ratio of 1.49, against a published ratio of 1.52.

Method details:

- **Projection:** Lambert azimuthal equal-area (d3-geo). Areas on screen are proportional to true areas, so side-by-side lakes at the same scale are a fair comparison.
- **Scale squares:** the 1,000 km² squares in P1 are drawn at the true projected scale.
- **Raw files:** kept untouched in `../_geo_raw/`.
- **Reproducible prep:** `python -I scripts/prep_geo.py ../_geo_raw src/geo` simplifies the outlines with Douglas–Peucker and preserves area within 0.1% for Volta and 1.1% for Kariba.
- **Dam markers:** the Akosombo coordinate (0.0569 E, 6.2994 N) is approximate. Verify it against VRA before the final cut.

## Illustrative assets (original, made in code)

- 5,000 L water tank: an original generic vector drawing. It is not a brand logo or a product photo.
- Isometric containers: illustrative only. Their footprint ratio is exaggerated (2.4) for legibility. Their volumes are drawn in true 148:181 proportion.
- Font: Inter (SIL Open Font License) via `@remotion/google-fonts`.
- No AI-generated images, stock footage, music or third-party artwork are used.

## Tooling

- Remotion 4.0.543 is free for individuals and companies of up to 3 people. Larger teams need a company licence.
- d3-geo 3.1.1 (ISC licence).

## Phase B — full episode (draft for GilB review, 2026-11-16)

Draft status: not approved, not final, not published.

**Narration**
- `public/narration_v1.wav` is GilB's approved master, used unmodified.
  - Original upload: `GILB006_Lake_Volta_Premium_Narration_V1.wav`.
  - Format: 119.34 s, 48 kHz, 24-bit mono, −16.1 LUFS integrated, −1.5 dBTP.
  - sha256: `00e66b3b19cce10a02cd4d332ecc049b0b4f04c6863a08773d4f5b26ae9e334e`.

**Timing**
- Word timestamps come from `timing/transcribe.py`: faster-whisper "small", run locally on CPU. Output is in `timing/words.json`.
- Scene cues and the per-proof TimeWarp anchors are in `src/Episode.tsx`.
- The three approved proofs keep their animation. They are re-timed piecewise-linearly so beats land on spoken words.

**Structure:** 11 timeline blocks, 18 story beats.

| Time (s) | Beat |
|---|---|
| 0–14.3 | Opening (proof 1) |
| 14.3–23.3 | Kariba flight and area squares |
| 23.3–28.6 | More area = more water? / Not quite |
| 28.6–46.2 | Polytank (proof 2) |
| 46.2–52.9 | Kariba 181 km³ |
| 52.9–59.0 | +33 km³ / less area |
| 59.0–90.9 | Containers and lakes (proof 3) |
| 90.9–100.9 | Verdict |
| 100.9–105.7 | Both enormous |
| 105.7–115.4 | Callback / Largest by what? |
| 114.9–end | Approved GILB-001 outro |

**Output**
- Video: `out/GILB_LakeVolta_Episode_v1.mp4`.
  - 1080×1920, 30 fps, 3,581 frames, H.264.
  - AAC 48 kHz stereo; the mono narration is duplicated to both channels.
  - sha256: `49876cde468b27901dc05a398026d6afd83004c86350148c789597c4eb0b00ba`.
- Captions: `out/GILB_LakeVolta_Episode_v1.en.srt` is a sidecar file using the approved script wording. It is not burned into the video.

**Audio check against the master:** sync offset 0 ms, correlation 1.0. True peak is −1.4 dBTP. Measured loudness is −13.1 LUFS, which is the master's −16.1 plus 3 dB from dual-mono stereo.

**Not included (v1 only)**
- v1 has no music or sound effects. v2 below adds them.

**Additional on-screen statements** (beyond the narration, for GilB to approve)
- "= 181 TRILLION LITRES."
- "+33 KM³" and "181 − 148 = 33"
- "SMALLER THAN LAKE VOLTA"
- "WIDER" / "DEEPER" tags
- "THE VERDICT"
- Rounded labels 8,500 / 5,600, with exact values in the sources.

**Wording to check by ear**
- Line 20: the transcript heard "the deeper one holds more water"; the script says "can hold".
- Last line: the transcript heard "There is more to the story"; the tagline says "There's".
- The SRT uses the script wording.

## Phase B v2 — music and sound effects (mix approved by GilB on 2026-11-16)

The mix approval covers the music and sound-effects mix only. The script, on-screen claims and final video are not yet approved.

GilB asked for music and effects and left the choice to Claude.

**Rights:** all music and effects are original and synthesised from scratch in code by `audio/make_audio.py`.
- No samples, loops, presets, stock audio or AI music service are used.
- No third-party licence applies.
- The GILB-001 music was not reused, because its rights review is still open in that benchmark's FINAL_RELEASE_QA.md.

**Music bed** (`public/music_bed_v1.wav`)
- 96 BPM in D minor, progression Dm9 – Bbmaj7 – Fmaj7/C – Cadd9.
- Layers: soft pad, sub bass, 8th-note pluck arpeggio, soft kick and hat.
- Follows the story: sparse opening, groove from the Kariba flight, a near-silent drop on "Not quite.", a lighter section for the containers, a lift for the verdict, stripped back for the callback, a riser into "Largest by what?", then a resolved D-minor chord under the outro.
- Ducked automatically under the narration: up to 9 dB, with 60 ms look-ahead, 40 ms attack and 400 ms release.

**Sound effects** (`public/sfx_v1.wav`)
- Placed on the animation events computed from the scene cues and TimeWarp anchors.
- Effects used: soft whooshes on scene changes, square pops, counter ticks, chimes when counts land, water swells when lakes, tanks and containers fill, low impacts on "Not quite.", the 181 figure and each verdict row, a sparkle on each asterisk, and a riser and hit on "Largest by what?". The outro has a sting.
- Ducked up to 5 dB under speech.

**Mix** (`audio/mix.sh`, ffmpeg)
- Narration is untouched and dual-mono at unity. Music −9 dB, effects −4 dB, master −1 dB.
- Limiter at −1.5 dBFS, applied at 4× oversampling.
- Result `public/mix_v1.wav`: −14.2 LUFS integrated, −1.6 dBFS peak, LRA 3.2 LU.

**Output:** `out/GILB_LakeVolta_Episode_v2_music.mp4`
- 1080×1920, 30 fps, 3,581 frames, AAC 48 kHz stereo.
- −14.2 LUFS, −1.7 dBTP.
- Narration sync against the master: 1 ms offset from the limiter look-ahead, correlation 0.98 with music present.
- sha256: `bf17dae3c42b56df52f0220429bd53a3d9b05cc233f8f1771fb7e037c81de0f9`.
- The picture is identical to v1.

**Speech clarity (measured, before the −2 dB music trim):** music sat a median 14.5 dB under the voice during speech.
Not yet checked by ear on a phone speaker or headphones (GILB quality standard §4).

**Regenerate:** `python audio/make_audio.py && sh audio/mix.sh`, then render. Use `MUSIC_DB` / `SFX_DB` to change levels.

## Final approval (2026-11-16)

GilB stated that "everything has been checked and approved". That covers:

- the v2 cut;
- the additional on-screen statements;
- the two narration wordings;
- the earlier open checks, namely the Akosombo coordinate and the source pages.

Those checks were done by GilB and are not documented in this folder. The exact source URLs and retrieval dates should still be added to the story's source records when it enters the Registry.

Still open: the story ID (`GILB-006` is taken by youth employment), publication, and the Registry entry.
