# GilB Analysis & Verification Reporting Standard v1.0

**Applies to every new GilB story analysis and every significant reanalysis.** The report is a required deliverable, not optional documentation. Preserve the approved scope and use the permanent GILB-### ID.

## Required outputs
1. An editable **Analysis & Verification Report (.docx)**, with a readable Markdown companion in the repository.
2. Raw-source links/files, date accessed and publisher; retain originals wherever access or licensing allows.
3. Cleaned/analysis-ready data and a data dictionary; document exclusions and every material transformation.
4. Reproducible calculation steps, formulas, units, benchmark choices, and an executable verification/check script where practical.
5. Row-level source-check ledger showing how each publication-critical number was verified, discrepancy count and remediation status.
6. Findings ledger separating **observation**, **interpretation**, **possible explanation**, and **verified causal explanation**.
7. A list of limitations, unusual movements, counterexamples and sensitivity to selected time windows.
8. Proposed editorial angles only after findings; an explicit claims sign-off gate before narration/animation is treated as approved.
9. Registry links to all documents, data and the next action; no duplicate record IDs, no retrospective approval.

## Standard report outline
- Metadata: story ID, report version, author/reviewer, analysis date, data coverage, status.
- Executive summary and central research question.
- Source register (primary URL, publisher, report period, accessed date, local file, license).
- Scope/definitions, population, time grain, units, exclusions.
- Data acquisition, raw preservation, cleaning and transformation steps.
- Quality assurance: completeness, uniqueness, reconciliation, primary-source cross-check, exception ledger.
- Analysis methodology and exact formulas/examples.
- Results with tables/charts and citations to underlying file and source.
- Sensitivity checks and competing interpretations.
- Claims ledger: status, evidence, caveats, human sign-off required.
- Open issues, limitations and reproducibility instructions.
- Archive links and next review date/version history.

## Publication control
A calculation verified against a primary-source table is **not automatically publication approved**. Keep evidence `safe_to_publish=No` until a responsible human reviewer has approved the exact phrasing, numbers and visual encoding. Do not state or imply reasons for trends without independent evidence. Never treat telecom subscriptions as unique individuals.

## Reproducibility control
Keep source data immutable (or store a new version), derive all shares from counts, show the period behind all comparison claims, and never hide contradictory dates or inconvenient movements. Preserve an earlier approved version when changes are made.

## GitHub file convention
`stories/GILB-###/analysis/GILB###_Analysis_and_Verification_Report_vN.docx` and `...md`; `.../Source_to_Clean_Comparison_*.csv`; `tools/verify_gilb###_*.py`. Record assets in the story registry and commit with the corresponding analysis version.
