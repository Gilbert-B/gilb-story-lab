# GILB-001 — Claim verification, 25 Nov 2026

Checked by Claude (independent source check) at GilB's request, against the approved narration (`scripts/narration_v1_approved.md`) and the claim list (`production/claims_to_verify_v1.csv`). **Owner approval of each claim is still required before the story can move to Ready to publish.**

## Method

1. Recomputed every figure from the 34-match transcription (`data/raw/hearts_2025-26_results_transcribed.csv`).
2. Re-read the RSSSF page independently (https://www.rsssf.org/tablesg/gha2026.html, 25 Nov 2026). Its 34 Hearts results give the same totals, the same 24 clean sheets and the same 13 goalless draws.
3. Re-read the Ghana FA season statistics (https://ghanafa.org/ghana-premier-league-2025-26-statistics?amp=1) and the final-table article (https://www.ghanafa.org/official-ghana-premier-league-table-after-the-end-of-the-2025-26-season).

## Results

| ID | Claim | Evidence | Result |
|---|---|---|---|
| CL-001 | 24 clean sheets in 34 matches | Transcription: 24. RSSSF: 24. GFA: "Hearts of Oak set a new Ghana Premier League record by keeping 24 clean sheets in 34 matches." | **Verified** (team clean sheets) |
| CL-002 | Conceded just 15 goals | Transcription 15; RSSSF table 25-15 | **Verified** |
| CL-003 | 13 of the clean sheets were 0–0 draws | Transcription 13; RSSSF results 13 | **Verified** |
| CL-004 | 25 goals in 34 matches | Transcription 25; RSSSF 25-15 | **Verified** |
| CL-005 | 0.74 goals per game | 25 / 34 = 0.735 | **Verified** (arithmetic) |
| CL-006 | League average 1.02 | GFA: "Across the 306 matches played, a total of 627 goals were scored"; RSSSF goals-for column also sums to 627. 627 / (306 × 2) = 1.02 per team per match | **Verified, with a note:** 627 includes 21 goals from seven matches awarded 3–0 after Hohoe United withdrew. Played matches only: 606 / 598 = 1.01. The comparison with 0.74 holds either way. |
| CL-007 | Failed to score in 18 matches | Transcription: 18 matches with 0 goals for | **Verified** |
| CL-008 | Both clubs lost exactly six | RSSSF: Hearts 13-15-6, Medeama 17-11-6 | **Verified** |
| CL-009 | Medeama won 17, Hearts 13 | RSSSF table | **Verified** |
| CL-010 | Hearts eight points behind the champions | RSSSF and GFA: Medeama 62 (champions), Hearts 54 (third) | **Verified** |
| — | Hearts finished third | GFA: "Hearts of Oak secured third place with 54 points"; RSSSF position 3 | **Verified** |

No discrepancies were found between the transcription, RSSSF and the Ghana FA.

## Still open (not factual claims)

- ISS-003, ISS-004, ISS-005: rights, captions, editable source and master archive (production QA).
