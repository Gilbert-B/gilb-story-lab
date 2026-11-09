# GILB-002 — Analysis & Verification Report v2.0

**Date:** 8 November 2026  
**Reporting status:** Source-table audit completed; external reviewer sign-off and publication approval pending.  
**Coverage:** 31 month-end observations (January 2024–July 2026), MTN / Telecel / AT, 93 operator-month records.  
**Research question:** How did Ghana's mobile internet subscriptions and market shares change, and what story does the complete historical trend support?

## Executive conclusion

Mobile-network internet subscriptions rose from **23,247,115** in January 2024 to **30,800,194** in July 2026 (**7,553,079, or 32.49%**). MTN gained **5,673,061** subscriptions but its share changed from **81.61%** to **80.02%** (**-1.60 percentage points**). Telecel gained **1,895,937** and grew **61.88%** in count. An endpoint-to-endpoint share decline does **not** imply a steady fall: MTN's share troughed in **June 2025** at **77.75%**, then recovered.

This is a story about relative growth rates, **not** a proven transfer of customers from one network to another.

## Step-by-step method

1. **Define scope:** Monthly active mobile-network data subscriptions, not fixed-line subscriptions, mobile voice, revenue, usage volumes, or unique individuals. Population is the 3 MNOs reported by the NCA.
2. **Find primary data:** Locate the NCA 2024 monthly table [S1], 2025 monthly table [S2] and 2026 January–July table [S3] on the NCA mobile-data page. Accessed 8 Nov 2026. Original PDF URLs are recorded; source PDFs have not been locally archived in this delivered package.
3. **Transcribe:** Read the MNO operator-count row for each month, not the all-market (mobile + fixed + BWA) total; 31 months × 3 operators = 93 observations. Normalise operator aliases (Scancom→MTN; Ghana Telecommunications Company→Telecel; Airtel Ghana/AirtelTigo→AT).
4. **Clean:** Produce long-form CSV columns `story_id, month, operator, subscriptions, market_share, market_segment, source_url, source_table, data_status`. Normalise month dates and parse integers; calculate monthly market shares from counts.
5. **Validate:** Compare all 93 cleaned values to a fresh transcription of [S1–S3] after viewing the NCA source tables; result **93/93 matched, 0 discrepancies**. Check 31 monthly operator sums against official MNO total rows; result **31/31 reconciled**. Save row-level evidence to `GILB002_Source_to_Clean_Comparison_93_Rows_v2.csv`.
6. **Analyse:** Compute operator net counts, growth percentages, market shares, share differences in percentage points, month-to-month movements, and alternative start/end windows. Preserve all 31 months in graphics to prevent selective comparisons.
7. **Interpret with restraint:** Explain the mathematical share paradox, flag unusual movements, and separate correlation from causation. The 2 July 2025 data-bundle directive [S5] is a documented event, **not an established cause** of the recorded subscription changes.
8. **Editorial review:** Rank candidate story angles; require separate human claim sign-off before narration, animation and publication are approved.

## Formulas (reproducible)

- Total subscriptions in month *t*: `MTN_t + Telecel_t + AT_t`.
- Operator share: `operator subscriptions in t / total MNO subscriptions in t × 100`.
- Net count change: `ending subscriptions − starting subscriptions`.
- Relative count growth (%): `(ending / starting − 1) × 100`.
- Market-share change (percentage points): `ending share (%) − starting share (%)`.
- Operator contribution to industry **net stock change**: `(operator net change / industry net change) × 100`. **Not** a share of new people.

### Worked example: MTN

- Count change: `24,646,152 − 18,973,091 = 5,673,061`.
- Share at start: `18,973,091 / 23,247,115 × 100 = 81.61%`.
- Share at end: `24,646,152 / 30,800,194 × 100 = 80.02%`.
- Share difference: `80.02% − 81.61% = -1.60 percentage points` (unrounded values used in calculation).

## Findings ledger

| Claim ID | Verified numerical finding | Interpretation | Status |
|---|---|---|---|
| F01 | Industry +7,553,079 (32.49%) | Net subscription stock rose | NCA tables checked; sign-off pending |
| F02 | MTN +5,673,061; share -1.60 pp | Gaining subscriptions can coincide with a declining share | NCA tables checked; sign-off pending |
| F03 | Telecel +1,895,937 (61.88%) | Faster proportional count growth than MTN | NCA tables checked; sign-off pending |
| F04 | AT -15,919 (-1.32%) | Modest net decline end-to-end | NCA tables checked; sign-off pending |
| F05 | MTN low of 77.75% in June 2025 | Share recovered later; not monotonic decline | NCA tables checked; sign-off pending |

## Sensitivity to date choices

| Comparison period | MTN market share start → end | Meaning |
|---|---|---|
| January 2024 → July 2026 | 81.61% → 80.02% | Long-window endpoint share decline |
| June 2025 → July 2026 | 77.75% → 80.02% | Recovery since low |
| December 2025 → July 2026 | 79.68% → 80.02% | Mild recent gain |

## Unusual monthly movements and open explanations

- Telecel, June 2025: +385,538 (+9.52% month-on-month). [S2]
- Telecel, August 2025: −279,842 (−6.20%); September 2025 +283,016 (+6.68%). [S2]
- AT, December 2025: −173,037 (−11.73%). [S2]
- MTN, January 2026: −527,881 (−2.31%). [S3]

These changes **are in the NCA primary tables**. They are not explained by those tables. Possible price, policy, reporting or competition causes are **hypotheses only**. Confirm independently before attaching causes in a GilB video.

## Limits and verification gaps

- One subscription is not necessarily one person; multiple SIMs and changes in activity criteria can alter counts.
- Shares are MNO mobile internet subscription shares; do not call them internet traffic or revenue shares.
- Changes in a stock of subscriptions are **net changes**, not gross new accounts or customer switching.
- Primary report tables were compared through NCA's published PDF views; original source PDF binaries are not bundled locally and must be archived separately for a complete external reproduction package.
- Source comparison was conducted with AI assistance; it is a **source-table audit**, not an independent human peer review. Claims are not marked publication-approved.
- Historical 2023 source is excluded because the link from the source portal appeared inconsistent; no values were inferred.

## External reproduction / reviewer checklist

1. Download [S1], [S2], [S3] from NCA and retain the date and file hashes.
2. Compare every MNO monthly count to `GILB002_Source_to_Clean_Comparison_93_Rows_v2.csv` (31 × 3 rows).
3. Confirm monthly `MTN+Telecel+AT` against NCA official `TOTAL MOBILE` rows.
4. Independently recompute the formulas above from `GILB002_mobile_internet_operator_monthly_2024_2026-07.csv`.
5. Inspect the full 31-month shares before endorsing any endpoint headline.
6. Confirm the exact published wording and animation scale before approving for release.

## Source register

- **[S1] NCA 2024 monthly MNO subscriptions.** 2024-01 to 2024-12; 12 months. https://nca.org.gh/wp-content/uploads/2025/06/Market-Data-2024.pdf
- **[S2] NCA 2025 monthly MNO subscriptions.** 2025-01 to 2025-12; 12 months. https://nca.org.gh/wp-content/uploads/2026/02/Data-Subscription-December-2025.pdf
- **[S3] NCA 2026 monthly MNO subscriptions.** 2026-01 to 2026-07; 7 months. https://nca.org.gh/wp-content/uploads/2026/10/Monthly-Industry-Data_July_2026-.pdf
- **[S4] NCA quarterly industry statistical dashboard.** Secondary aggregated trend cross-check; Q2 2026. https://statisticaldashboard.nca.org.gh/
- **[S5] NCA policy update on revised data bundles, 2 July 2025.** Timeline/context only; not causal proof. https://nca.org.gh/2025/07/02/update-2-mnos-begin-implementation-of-directives-on-improved-data-bundle-allocations/

## Editorial recommendation (not an approved narration)

**Working angle:** *MTN added 5.7 million mobile internet subscriptions. So why did its market share edge down?* The answer is that other operators, notably Telecel, grew faster in relative terms during the selected window. Show the mid-2025 low and the later recovery to prevent a misleading steady-decline impression.

**Next gate:** Verify source PDF archive, obtain any necessary operator explanations without invented causation, receive explicit human sign-off of final claim wording, then draft and approve the script and storyboard.
