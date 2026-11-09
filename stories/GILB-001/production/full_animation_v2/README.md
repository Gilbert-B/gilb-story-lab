# GilB — GILB-001 Full Animation Draft v2

**Status:** Silent animation v2, for creator review. **Not approved for publication.**

## Files
- `GILB001_Full_Animation_Silent_Draft_v2.mp4` — 14-scene, 1:44 video, 1080×1920, 24fps, H.264, no audio.
- `source/render.py` — complete, editable Python + Pillow + FFmpeg renderer.
- `data/hearts_2025-26_chronological_matches.csv` — all 34 matches, actual dates, matchweek, opponent, score, and flags used by the tile animation.
- `previews/scene_montage.jpg` and `previews/scene_XX.png` — stills of each scene.
- `approved_narration_v1.md` and `voiceover_scene_timing.csv` — original approved voiceover and provisional timings, unchanged.

## What changed from v1
1. Each tile denotes a match **in actual date played order** (01–34). Clean-sheet tiles are highlighted in their real places, not grouped at the start.
2. The 13 goalless draws change from amber to teal **in the same match positions**. Match numbers persist; 0–0 appears on the relevant tile.
3. The 18 scoreless matches are shown as 13 teal 0–0 draws plus five coral scoreless defeats, each at its own match position. The other 11 clean sheets remain amber.
4. The league average (1.02 goals per team per game, rounded) is the full 100% reference bar. Hearts (0.74, rounded) covers 71.77% using unrounded data. No unexplained blank end on the reference bar.
5. Medeama's 17 wins and Hearts' 13 wins are each scaled against **34 matches**, with numerical `17/34` and `13/34` labels. The follow-up comparison displays all 34 outcomes (wins, draws, defeats) for both teams, and 62 vs 54 points.

## Data integrity and chronology
- Match results and match dates sourced from RSSSF, Ghana 2025/26: https://www.rsssf.org/tablesg/gha2026.html (last updated October 22, 2026, as noted in our prior source register).
- Round 31 (Hearts 1–0 Nations; May 3, 2026) was played **before** Round 30 (Hearts 0–0 Karela; May 6, 2026). The CSV and video use played-order positions 30 = round 31 and 31 = round 30.
- Match data reconciles to 34 played, 13 W, 15 D, 6 L, 25 GF, 15 GA, 54 points; 24 clean sheets, 13 goalless draws, 5 other scoreless games and 18 failed-to-score matches.
- The league benchmark uses **627 total goals across 306 league matches**, equivalent to `627 / (306×2) = 1.0245 goals per team per match`, displayed as **1.02**. This is consistent with the sum of all 18 clubs' final goals-for columns (627) and published Ghana FA season statistics. A few external providers state 626, so the source definition is documented here; the displayed figure is 1.02 under either total.
- 24 team clean sheets is also corroborated by the Ghana Football Association's season statistics.

## Creative / ownership
- Original GilB editorial colours, uncluttered layout, same approved narration.
- `@Ghyl_B` remains subtly visible throughout and prominent in the outro.
- No on-screen internal tracking identifiers. Match numbers are **data identifiers** representing the order played, not internal story IDs.

## Usage
Required: Python 3, Pillow, and FFmpeg.

From the package's root:
```
python source/render.py --output GILB001_Full_Animation_Silent_Draft_v2.mp4 --scale 1080 --preview-dir previews
```
System font files are used where available. None are distributed.

## Next production steps
1. Review revised draft visually and mark approved or changes requested.
2. Record narrator's own voice, clean and master it, then retime scenes to the narration.
3. Complete claim-by-claim editorial sign-off and music/sound checks before publishing.

**GitHub:** Put the package inside `stories/GILB-001/production/full_animation_v2/`; keep the v1 folder for revision history. Do not mark this as published or final/approved until personally reviewed. No live repo changes were performed by this package.
