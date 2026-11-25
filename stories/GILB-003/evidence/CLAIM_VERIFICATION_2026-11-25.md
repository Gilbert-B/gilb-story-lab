# GILB-003 — Claim verification, 25 Nov 2026

Checked by Claude (independent source check) at GilB's request, against the owner-approved script (`scripts/narration_v3_final_owner_approved.md`). **Owner approval of each claim is still required before the story can move to Ready to publish.**

## Sources

- Bank of Ghana, *Summary of Macroeconomic and Financial Data*, September 2026. Table 11, "Payment Systems Data", and footnote 15. https://www.bog.gov.gh/wp-content/uploads/2026/09/Summary-of-Economic-and-Financial-Data-September-2026.pdf. The copy is in `sources/` (SHA-256 `d51e173c…e9c`). The PDF text was re-extracted, and every value in `data/raw/GILB-003_BoG_Table11_2025-08_to_2026-08.csv` matches it.
- Ghana Statistical Service homepage, "Ghana at a Glance": "Projected Population 34,378,768, 2026". https://statsghana.gov.gh/

## Results

| Claim | Evidence | Result |
|---|---|---|
| Ghana has about 34 million people | GSS projected population, 2026: 34,378,768 | **Verified** (a GSS projection, not a census count) |
| 85.8 million registered mobile money accounts, Aug 2026 | BoG Table 11 | **Verified** |
| More than twice the population | 85.8 / 34.38 = 2.5 | **Verified** |
| Over one billion transactions in Aug 2026 | BoG Table 11: 1,046 million | **Verified** |
| Nearly 400 transactions a second | 1,046m / (31 × 86,400 s) = 390.5 | **Verified** (arithmetic) |
| 26.4 million active, Aug 2026 | BoG Table 11 | **Verified** |
| Fewer than one in three | 26.4 / 85.8 = 30.8% | **Verified** |
| The other 59.4 million | 85.8 − 26.4 | **Verified** |
| Active means at least one transaction in the previous 90 days | BoG footnote 15: "accounts which transacted at least once in the 90 days prior to reporting" | **Verified** |
| Registered accounts +8.1 million, Aug 2025 to Aug 2026 | 77.7 → 85.8 | **Verified** |
| Active accounts +1.3 million | 25.1 → 26.4 | **Verified** |
| The gap widened by almost 7 million | 52.6 → 59.4 = +6.8 million | **Verified** |
| Accounts are not people; owning an account isn't using it | Framing | **Verified** (framing) |

Limitation: the figures are BoG-rounded values from one release and may be revised.
