# GILB-002 Independent Data Audit

**Auditor:** Claude Code, on GilB's assignment. AI-assisted, not a human peer review.
**Date:** 9 November 2026
**Scope:** MTN, Telecel and AT mobile data subscriptions, January 2024 to July 2026.
**Publication status:** Nothing here approves a claim. GilB holds claim approval.

## 1. Verdict

**The data and arithmetic are reliable. The current headline framing is not ready for publication.**

- All 93 operator-month values match the NCA's latest published tables. All 31 totals reconcile. No transcription, cleaning or calculation error was found.
- "MTN's share fell from 81.61% to 80.02%" is correct but depends heavily on the start month. January 2024 is MTN's highest share in the window and coincides with a 17.42% one-month fall at AT, which reversed in February. Start one month earlier or later and the change is -0.45 or -0.33 points.
- The NCA has published very different MTN figures for the same months. Its February 2026 release put December 2025 MTN 2.42 million higher, which moves MTN's share by 1.59 points. That is the same size as the headline change. Later NCA files use the lower figures, but I found no published explanation.

The more defensible story is that **MTN stayed at about 80% while Telecel rose by about 3 points and AT fell**.

## 2. Sources obtained

| File | Role | Result | SHA-256 starts |
|---|---|---|---|
| `Market-Data-2024.pdf` | GilB S1 | Downloaded, parsed | `ce841e32ff051d57` |
| `Data-Subscription-December-2025.pdf` | GilB S2 | Downloaded, parsed | `e41291aaafa45fb5` |
| `Monthly-Industry-Data_July_2026-.pdf` | GilB S3 | Downloaded, parsed | `cc92911a3544960b` |
| `Market-Data-2023.pdf` | New: December 2023 baseline | Downloaded, parsed | `00059f5bdbc78e84` |
| `Market-Data-2025.pdf` (Jan to Apr) | Earlier release | Compared | `d875b1b7381abf39` |
| `Data-Subscription-July-2025-1.pdf` | Earlier release | Jan to Apr columns compared only | `5ceb0e21cfb00d40` |
| `Data-Subscription-February-2026.pdf` | Earlier release | Compared | `ec448bbef4972cf1` |
| `Monthly-Industry-Data_May_2026-2.pdf` | Earlier release | Compared | `0e4a64065c6180c9` |
| Q1 2024, Q2 2025, Q3 2025, Q4 2025 and Q1 2026 Statistical Bulletins | Definitions and quarter-end check | Downloaded, read in part | n/a |

All files came from `nca.org.gh/wp-content/uploads/` on 9 November 2026. Full URLs and the four main hashes are in `audit_checks.json`.

**Not obtained or checked:** other interim monthly releases, the May to July 2025 columns of the July 2025 release, the statistical dashboard [S4], and any explanation from the NCA or operators for the revisions.

## 3. Source verification

| Test | Result |
|---|---|
| Values read by page position from the PDFs, with no GilB input | 93 of 93 extracted |
| Same values found by a second PDF text engine | No value missing |
| Rendered tables viewed as images | No difference seen |
| MTN + Telecel + AT against the NCA's printed TOTAL MOBILE | 31 of 31 in scope (43 of 43 with 2023) |
| Recomputed shares against the NCA's printed shares | 132 of 132 |
| Recomputed operator growth against printed growth | 128 of 129 |
| Recomputed total growth against printed growth | 41 of 42 |
| December 2025 column in S2 against S3 | Identical |
| Clean CSV, raw transcription and 93-row ledger against this extraction | 0 mismatches |
| Duplicates or missing values in the clean CSV | None |
| Panel, window file, verified metrics and HHI recomputed | 0 mismatches |

**Operator names:** consistent entities with changed labels. Airtel Ghana Limited appears as AirtelTigo in 2024 and AT from 2025. Telecel is "Formerly Vodafone Ghana" in 2024 and Ghana Telecommunications Company Limited from 2025. Scancom PLC is MTN throughout.

**Definition:** The NCA's Q1 2026 bulletin defines mobile data subscriptions as active subscriptions that generated internet traffic within the last 90 days. This supports the word "active", but the monthly PDFs GilB cites do not say it, so the bulletin should be added to the source register.

### Reporting changes and anomalies

| Month | Issue | Effect |
|---|---|---|
| Dec 2025 to Feb 2026 | February 2026 release shows MTN at 25,292,341, 25,537,818 and 25,806,338. May and July 2026 files show 22,867,689, 22,339,808 and 23,103,208. | MTN share would be 81.27%, not 79.68%, for December. Unexplained. |
| Jan 2026 | MTN's -527,881 drop exists only in the later figures. The February 2026 release showed +245,477. | Do not narrate as a real loss without confirmation. |
| Feb 2025 | MTN first published as 20,613,654, later 20,480,694 (-132,960). | Superseded. GilB uses the later value. |
| Nov 2025 | S3 prints December 2025 growth of 2.48% (MTN) and 1.78% (total). S2's counts give 2.34% and 1.67%. This implies a November MTN figure near 22.31 million against 22,344,100 published. | Possible unpublished revision of about 30,000. No finding depends on it. |
| Jan 2024 | AT falls 17.42% (-255,272), then rises 20.52% in February (+248,368). | Distorts the baseline. |
| 2023 | AT swings between -27.79% and +20.22% in single months. | AT's series is volatile, so its figures need care. |
| Jun to Oct 2025 | Telecel moves +9.52%, +1.80%, -6.20%, +6.68%, -3.34%. | Unexplained saw-tooth, and it creates MTN's low. |
| Mar 2026 | Bulletin shows AT at 1,291,580, monthly table 1,291,576. | Immaterial. |

## 4. Reproduced calculations

| Measure | Jan 2024 to Jul 2026 | Dec 2025 to Jul 2026 | Jul 2025 to Jul 2026 |
|---|---:|---:|---:|
| Industry change | +7,553,079 (+32.49%) | +2,101,804 (+7.32%) | +3,278,021 (+11.91%) |
| MTN change | +5,673,061 (+29.90%) | +1,778,463 (+7.78%) | +3,245,647 (+15.17%) |
| MTN share | 81.61 → 80.02 (-1.60 pp) | 79.68 → 80.02 (+0.34 pp) | 77.76 → 80.02 (+2.26 pp) |
| MTN net contribution | 75.11% | 84.62% | 99.01% |
| Telecel change | +1,895,937 (+61.88%) | +430,898 (+9.51%) | +445,346 (+9.86%) |
| Telecel share | 13.18 → 16.10 (+2.92 pp) | 15.78 → 16.10 (+0.32 pp) | 16.40 → 16.10 (-0.30 pp) |
| Telecel net contribution | 25.10% | 20.50% | 13.59% |
| AT change | -15,919 (-1.32%) | -107,557 (-8.26%) | -412,972 (-25.69%) |
| AT share | 5.21 → 3.88 (-1.33 pp) | 4.54 → 3.88 (-0.66 pp) | 5.84 → 3.88 (-1.96 pp) |
| AT net contribution | -0.21% | -5.12% | -12.60% |

Denominators are correct: shares use the three-operator total, contributions use industry net change, and percentage changes and percentage points are kept separate. Monthly and year-on-year figures for all 31 months are in `audit_monthly_calculations.csv`. Year-on-year figures for 2024 use the 2023 file.

**Turning points in MTN's share (reversals of at least 0.5 points):** 81.61% in January 2024, 77.75% in June 2025, 79.68% in December 2025, 78.98% in January 2026, then 80.02% in July 2026. It peaked at 80.32% in April 2026, then fell for three straight months.

**Start-month test for MTN's share, ending July 2026:**

| Start | MTN share change |
|---|---:|
| January 2023 (outside study) | +4.67 pp |
| December 2023 (outside study) | -0.45 pp |
| **January 2024 (current)** | **-1.60 pp** |
| February 2024 | -0.33 pp |
| May 2024 | -0.60 pp |
| Three-month pooled, Jan to Mar 2024 vs May to Jul 2026 | -0.72 pp |

Of 30 possible start months in the study, the share is down from 11 and up from 19. MTN's median monthly move is 0.30 points. Had AT held its December 2023 count, January 2024 MTN share would have been 80.73%.

## 5. Challenge to the findings

| Finding | Mathematically correct? | Supported by NCA data? | Interpretation reasonable? | Could it mislead? |
|---|---|---|---|---|
| **A.** MTN gained about 5.7 million | Yes: 5,673,061 | Yes | Yes, as a net change | Low to moderate. It is a net change in active subscriptions, not new customers or people. From December 2023 it is 5.97 million. |
| **B.** MTN share 81.61% to 80.02% | Yes: -1.595 pp | Yes, printed by the NCA | **Only as a two-date comparison** | **High.** The start month is the window's peak and is distorted by AT. The drop is 0.33 to 0.72 points on nearby baselines. |
| **C.** Telecel grew proportionally faster, helping explain the change | Yes: 61.88% vs 29.90% | Yes | Yes as arithmetic. Had Telecel grown at MTN's rate, MTN would end at 82.65%. | Moderate. It reverses in the last 12 months (9.86% vs 15.17%), its share peaked in July 2025, and it does not show customers switching. |
| **D.** No continuous decline, recovered after about June 2025 | Yes: share rose in 13 months and fell in 17 | Yes | Yes, with limits | Moderate. June and July 2025 are almost tied (77.751% vs 77.757%). The low follows Telecel's unexplained jump. Of the +2.27 point recovery, AT's fall accounts for 2.10 and Telecel's for 0.17, and the share has slipped since April 2026. |
| **E.** AT's share declined | Yes: -1.33 pp | Yes | Yes | Moderate. It rose to 6.81% by May 2024, then fell to 3.88%. The -1.32% count change understates the decline: -18.51% from December 2023 and -29.41% from the May 2024 peak. |
| **F.** MTN's contribution varies by period | Yes: 69.35% to 99.01% across all start months | Yes | Yes | Moderate. "99% of growth" hides Telecel's +445,346, offset by AT's -412,972. MTN's share of gross gains in that period is 87.93%. |

## 6. Issues in the existing materials

1. **The 93-row ledger is not independent proof.** `tools/verify_gilb002_nca_v2.py` compares the clean file with values typed into the script. The values were right, but ISS-007's "independently re-read" overstates the method.
2. **The 2023 exclusion is out of date.** The NCA index links to the voice file, but `Market-Data-2023.pdf` is available at the matching official address and changes the interpretation.
3. **The report lists no NCA revisions.** The vintage differences in section 3 should be recorded.
4. **On-screen rounding.** 81.61 minus 80.02 appears to be 1.59, but the true change rounds to 1.60. Use "about 1.6 points" and avoid showing the subtraction.
5. **F04's "modest net decline" for AT** is an artifact of the January 2024 baseline.
6. **"Month-end" is not stated** in the monthly tables. Bulletins support quarter-end only.

## 7. Suggested wording for GilB's review

Not approved claims.

- **Safer:** "From January 2024 to July 2026, MTN added about 5.7 million active mobile data subscriptions, yet its share stayed close to 80%."
- **Safer:** "Telecel's share rose about 3 points, from 13.2% to 16.1%, while AT's fell from a peak of 6.8% in May 2024 to 3.9%."
- **Avoid:** "MTN is losing the market", "customers left MTN for Telecel", and any cause for the month-to-month jumps.
- **On screen:** "Subscriptions active in the last 90 days, not people. Source: NCA, July 2026 release."

## 8. Open before publication

1. Ask the NCA why MTN's December 2025 to February 2026 figures changed, and whether the July 2026 file is final.
2. GilB to decide whether to keep January 2024 as the start, or use a pooled or December 2023 baseline.
3. Check NCA data reuse terms and archive the source PDFs.
4. Unverified leads on AT, from search results only and not read in full: Bloomberg's October 2025 report of a plan for Telecel to absorb AT subscribers, and a September 2025 report of AT site disconnections. These need checking before any causal claim.

## 9. Reproduce

```bash
python gilb002_independent_audit.py --pdf-dir <folder with the four PDFs> --repo <repo root> --out <output folder>
python gilb002_release_comparison.py <folder containing nca_raw and nca_vint>
```

Requires PyMuPDF, pandas and openpyxl.
