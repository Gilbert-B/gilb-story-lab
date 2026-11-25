# GILB-002 — Claim verification, 25 Nov 2026

Checked by Claude (independent source check) at GilB's request. **Owner approval of each claim is still required before the story can move to Ready to publish.**

## What the final video says

No narration script was saved in the repository, so the claims below were taken from the final master (`production/final/GILB002_v4_Score_B_Cinematic_Pulse_v2_Lower_Bed.mp4`) using automatic speech recognition (faster-whisper "small"). Key lines are below, lightly cleaned: the recogniser heard "on MTN" as "un-emptying" and "Telecel" as "TELISEL". A listen-through by the owner should confirm the wording.

> In Ghana, about 8 out of every 10 mobile data subscriptions were on MTN at the end of March 2026 … In the first three months of 2026, for every 100 gigabytes of mobile data used, about 87 gigabytes were used on MTN's network … MTN had 80% of subscriptions, but its network carried 87% of the data. Telecel and AT together had 20% of subscriptions, but carried only about 13% of the data. Just a year earlier, the difference was much smaller. In early 2025, MTN had about 79% of subscriptions and 82% of the data, a gap of just over 3 percentage points. By early 2026, that gap had more than doubled to over 7 points. Most of the widening had already happened by mid-2025. Remember, a subscription isn't necessarily a person … these numbers don't tell us why this difference exists.

## Sources (copies in `sources/`)

NCA Quarterly Statistical Bulletins on Communications in Ghana:

- Q1 2025: https://nca.org.gh/wp-content/uploads/2025/07/Q1-2025-Statistical-Bulletin.pdf (Tables 13 and 16)
- Q2 2025: https://nca.org.gh/wp-content/uploads/2025/12/Q2-2025-Statistical-Bulletin.pdf (Tables 15 and 18)
- Q3 2025: https://nca.org.gh/wp-content/uploads/2026/01/Q3-2025-Statistical-Bulletin.pdf (Tables 15 and 18)
- Q1 2026: https://nca.org.gh/wp-content/uploads/2026/06/Q1_2026_Statistical_Bulletin.pdf (Tables 15 and 18)

## MTN shares, from the NCA tables

| Quarter | Data subscriptions (quarter end) | Data traffic (quarter) | Gap (pp) |
|---|---:|---:|---:|
| Q1 2025 | 79.05% | 82.30% | 3.25 |
| Q2 2025 | 77.75% | 84.74% | 6.99 |
| Q3 2025 | 78.33% | 85.93% | 7.60 |
| Q4 2025 | 79.68% | 86.69% | 7.01 |
| Q1 2026 | 80.12% | 87.31% | 7.19 |

## Results

| Claim | Result |
|---|---|
| About 8 in 10 data subscriptions on MTN, end-March 2026 | **Verified**: 80.12% |
| About 87 of every 100 GB on MTN, Q1 2026 | **Verified**: 1,091,499 / 1,250,099 TB = 87.31% |
| Telecel and AT: 20% of subscriptions, about 13% of data | **Verified**: 15.53 + 4.34 = 19.87%; 11.49 + 1.19 = 12.68% |
| Early 2025: MTN about 79% of subscriptions, 82% of data, gap just over 3 points | **Verified**: 79.05%, 82.30%, 3.25 pp |
| By early 2026 the gap had more than doubled to over 7 points | **Verified**: 7.19 pp, 2.2× |
| Most of the widening had happened by mid-2025 | **Verified**: by Q2 2025 the gap had widened by 3.74 of the 3.94 points (95%). Part of that Q2 jump came from a dip in MTN's subscription share (79.05% to 77.75%), not only from traffic. |
| A subscription isn't necessarily a person; no cause claimed | **Verified** (framing) |

All the subscription and traffic figures are printed identically in more than one bulletin (each bulletin repeats the previous quarters). The disputed December 2025 MTN count (ISS-008 / clean-scope v3) is not used in any claim.
