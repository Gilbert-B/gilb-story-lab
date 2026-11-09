# GILB-001 — Sources and provenance

Research date: 2026-11-07. Editorial status: **findings calculated, not approved for publication**.

## Match-by-match score dataset

- **RSSSF — Ghana 2025/26:** https://www.rsssf.org/tablesg/gha2026.html
- Page authors: Hans Schöggl and Karel Stokkermans; site states last updated 22 October 2026.
- Rows in `data/raw/hearts_2025-26_results_transcribed.csv` were **manually transcribed** from the 34 round-by-round results shown on that webpage. It is not a downloaded original data file or an API export.
- Attribution: RSSSF and its authors. Their webpage states it may be copied in whole or part provided proper acknowledgement is given; verify applicable terms before wider republishing.
- `round` indicates nominal matchweek, **not necessarily actual chronological order**: RSSSF explicitly notes round 30 was played after round 31.
- The Hearts score is normalized to `hearts_goals` whether the club was home or away; `venue` preserves which club hosted.
- The script checks match counts, totals and season-end results against a second source. This reconciliation reduces—but does not eliminate—the risk of transcription mistakes.

## Independent checks

1. **Ghana Football Association — final table**: https://www.ghanafa.org/official-ghana-premier-league-table-after-the-end-of-the-2025-26-season
   - Confirms Medeama champion (62 points), Hearts third (54 points).
2. **Ghana Football Association — 2025/26 season statistics**: https://ghanafa.org/ghana-premier-league-2025-26-statistics?amp=1
   - Explicitly reports Hearts of Oak's 24 team clean sheets across 34 matches.
3. **2025/26 GPL results listing**: https://preview.gpl.com.gh/matches?season=2025-26
   - Cross-check source for selected individual results (rounds 20, 27, 32, 34).
4. **RSSSF final standings and round results**: https://www.rsssf.org/tablesg/gha2026.html
   - Final table: Hearts 34 P, 13 W, 15 D, 6 L, 25 GF, 15 GA, 54 pts; Medeama 34 P, 17 W, 11 D, 6 L, 52 GF, 28 GA, 62 pts.

## Scope and limitations

- Team clean sheets are **not** the same as an individual goalkeeper's credited clean sheets.
- We do not have shot counts, xG, injuries, tactical data or other causal evidence here. It would be unjustified to say **why** Hearts failed to score beyond the observable match results.
- The arithmetic comparison 'four draws versus four wins explains the eight-point difference' is descriptive; it is **not** a simulation claiming identical outcomes under changed tactics.
- The analysis needs owner review and explicit approval of proposed publication claims. All evidence must remain `safe_to_publish=No` until then.
