# GILB-001 | Interactive Visual Storyboard v1.0

**Status:** Design prototype for owner review. Not approved for production or publication.  
**Story:** Hearts of Oak / 2025–26 Ghana Premier League.  
**Brand:** GilB · Unpacked by GilB · “There’s more to the story.”  
**Video aspect:** 9:16 vertical (planned master 1080×1920).  
**Runtime:** approximately 1:44 in this **estimated** prototype timeline; final timing must be set against a real narration recording.

## Open the prototype

1. Unzip the package on your computer.
2. Double-click `index.html` to open it in Chrome or Edge. Internet access is **not** required.
3. Use **Play / Pause**, left/right arrows, the timeline slider, or the scene list.
4. The right panel contains narration excerpts, visual intent, and proposed motion for the selected scene.
5. Open `shotlist.csv` in Excel to see all scene timings and design notes.

**Controls:** Space = play/pause; left/right arrow keys = previous/next scene. On mobile, swipe the scene strip horizontally and tap a scene. There is no audio or rendered MP4 yet.

## Editorial principles

- Uses the approved GILB-001 script without changing its story structure.
- Visualizes clean sheets as 34 **nonchronological, outcome-grouped** tiles. 24 show clean sheets; 13 of those become 0–0 results.
- 18 scoreless matches include those 13 0–0s, with 5 other scoreless matches.
- Shows 0.74 Hearts versus 1.02 goals per **team** per match with a common zero baseline.
- Compares Hearts and Medeama (wins 13/17; draws 15/11; losses 6/6; points 54/62).
- Does not use fake club crests, stock stadium photography, player likenesses, licensed music, or invented match ordering.
- Figures follow GILB-001 project research; **all claims still require publication-level owner approval** before final video production.

## Contents

- `index.html` — self-contained HTML/CSS/JavaScript working storyboard; no external libraries.
- `shotlist.csv` — scenes, narration excerpts, visual intent, transitions, proposed duration.
- `approved_narration_v1.md` — exact locked script from the prior approved storyboard package.
- `assets/design_review_montage.jpg` — design review stills from selected frames.

## Suggested GitHub location

`stories/GILB-001/storyboards/interactive/`

This package is designed to be copied into that folder. The live GitHub repository has **not** been changed by this prototype.

## Limits and future work

This is an **interactive design proof**, not a voice-synced production animation. It uses simple CSS transitions to demonstrate visual language, numeric emphasis, and scene order. The definitive animation still needs voice recording, scene-level timing, audio design, subtitles, export rendering, accessibility checks, and formal source/claim sign-off. Some motion transitions are represented by storyboard beats rather than full continuous object morphing. The playable stage is rendered at browser preview resolution and scales to the device; the 1080×1920 output is a future production specification.
