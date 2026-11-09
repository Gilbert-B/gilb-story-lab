# GILB-002 — Clean Evidence Scope & Verification Note (v3.0)

**Decision date:** 9 November 2026  
**Story:** GILB-002 — Ghana's mobile internet market  
**Decision:** No regulator outreach. Remove disputed or potentially misleading numbers from the **active editorial scope**; retain prior datasets and analyses as historical, excluded evidence.  
**Status:** Source selection complete for a new candidate; no script, publication or claim approval.

## 1. Why we revised the scope
Claude's independent audit found a material conflict in the NCA's published MTN counts for December 2025: 22,867,689 in the December 2025 release and later quarterly statistics versus 25,292,341 in the February 2026 release. Even when a calculation is correct within a selected source series, this uncertainty makes the original “MTN gained millions but lost share” headline unsuitable under GilB's stricter editorial rule.

We will not request clarification from the NCA. We **will not delete** old data, calculations, or audit documents; we will mark the original time-series headline as **EXCLUDED FROM PUBLIC STORY**.

## 2. New narrow, cross-checked candidate
**Working question:** Why does MTN account for about four-fifths of mobile data subscriptions but nearly nine-tenths of network traffic?

Source: NCA Quarterly Statistical Bulletin on Communications in Ghana, Q1 2026, **printed page 30 / Table 15** and **printed page 32 / Table 18**.

| Operator | Subscription share (31 March 2026) | Traffic share (Jan–Mar 2026) | Gap, pp |
|---|---:|---:|---:|
| MTN | 80.12% | 87.31% | +7.19 |
| Telecel | 15.53% | 11.49% | −4.04 |
| AT | 4.34% | 1.19% | −3.15 |

These are **two different metrics**: subscriptions are a March-end stock (active mobile data subscriptions), while traffic is the share of total data volume over the quarter. Their difference does **not** establish individual customer usage rates, subscriber quality, pricing, network performance, or causal explanations.

The same MTN and Telecel **March counts** in Table 15 match the later July 2026 monthly report (23,818,235 MTN; 4,617,656 Telecel), as do the market shares printed to two decimal places. The MTN traffic share is computed from the Q1 bulletin's **1,091,499 TB / 1,250,099 TB** and rounds to 87.31%; traffic components total exactly 1,250,099 TB in that report.

## 3. Source exceptions we exclude, not erase
- **December 2025 MTN count:** 22,867,689 (December release and Q1 Bulletin) versus **25,292,341** in February 2026 release; a 2,424,652-count discrepancy. The origin/cause is unresolved. Do not use affected month-to-month comparisons, the original 5.7m/market-share paradox hook, or an asserted reason for the discrepancy in a video.
- **March 2026 AT count:** Q1 2026 Bulletin 1,291,580 vs later July monthly report 1,291,576, a **four-subscription** discrepancy. Consequently the precise total also differs: 29,727,471 vs 29,727,467. Exclude these exact values from narration and animation. All reported March operator share **percentages** match at the displayed two-decimal precision.
- **Unverified causes:** Do not attribute movements to mergers, service quality, customer switching, regulation, data-price changes or outage events without separately sourced evidence.

## 4. Reproduction steps (external reviewer)
1. Open the **Q1 2026 Statistical Bulletin**, printed p.30 Table 15, and transcribe the March-end share of mobile data subscriptions for each operator.
2. Open printed p.32 Table 18 for operator quarterly traffic (TB) and reported traffic shares.
3. Confirm traffic total: 1,091,499 + 143,696 + 14,904 = 1,250,099 TB. Compute MTN share as 1,091,499 / 1,250,099 × 100 = **87.31%** after rounding.
4. Compute **87.31 − 80.12 = 7.19 percentage points**. Do not call this 7.19% relative growth.
5. Cross-check the March 2026 subscription figures/shares against the July 2026 monthly report. Observe and record the AT exact-count exception; do not silently “correct” either official source.
6. Check the large December 2025 MTN exception using the February 2026 bulletin; this is why the former headline is out of scope.
7. Run `python reproduce_gilb002_clean_scope_v3.py` beside the CSV for the cross-check assertions.

## 5. Editorial status and next work
**Working angle, not approved:** “Four in five mobile subscriptions—but nearly nine in ten megabytes of traffic: what the NCA figures show about concentration.” Prefer “mobile data traffic by volume” to “actual internet use by customers.” No causal or user-level behaviour claims from these aggregated data.

**Allowed for next editorial review:** The shares in the table, the 7.19pp difference, the NCA reporting period, and the fact that MTN remains largest by both measures.  
**Not approved yet:** Narration, animation, publication, individual customer behaviour, causation, usage-per-subscriber comparisons.

## 6. Primary references
- Q1 2026 NCA Statistical Bulletin: https://nca.org.gh/wp-content/uploads/2026/06/Q1_2026_Statistical_Bulletin.pdf
- NCA July 2026 mobile data monthly release: https://nca.org.gh/wp-content/uploads/2026/10/Monthly-Industry-Data_July_2026-.pdf
- NCA February 2026 mobile data release (discrepancy archive): https://nca.org.gh/wp-content/uploads/2026/04/Data-Subscription-February-2026.pdf

**Verification level:** Source-authentic regulatory tables, internal arithmetic cross-checks, published March share cross-check across two releases. This is not a guarantee that all underlying operator reports are error-free or independently audited. The original February inconsistency remains unresolved but excluded from the active public storyline.
