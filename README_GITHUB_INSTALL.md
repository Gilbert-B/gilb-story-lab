# GILB-002 v3 — clean-evidence scope update (9 November 2026)

This is a **cumulative editorial decision**, not a replacement for earlier research data. Prior NCA discrepancies remain archived but are excluded from public-story work. The new narrowed candidate uses Q1 2026 subscription shares versus Q1 traffic shares.

## Files
- `stories/GILB-002/analysis/clean_scope_v3/GILB002_Clean_Evidence_Scope_And_Verification_v3.docx` — external-review report.
- Same report in `.md`.
- `GILB002_Q1_2026_Crosschecked_Shares_v3.csv` — share-only working table.
- `GILB002_Source_Exceptions_v3.csv` — discrepancies excluded from active scope.
- `reproduce_gilb002_clean_scope_v3.py` — arithmetic checks.
- `tools/register_gilb002_clean_scope_v3.py` — optional idempotent Story Registry update, leaving publication approvals as No.

## GitHub steps (Windows)
1. Open GitHub Desktop and fetch/pull the `gilb-story-lab` repository. Review unrelated uncommitted changes first; do not overwrite them.
2. Extract this ZIP and copy its **contents** into the repository root, merging folders.
3. In PowerShell from the repository root:

```powershell
py -3 stories/GILB-002/analysis/clean_scope_v3/reproduce_gilb002_clean_scope_v3.py
py -3 tools/register_gilb002_clean_scope_v3.py
py -3 tools/registry.py validate
py -3 -m unittest discover -s tests -v
py -3 tools/registry.py build
```

4. Inspect `stories/GILB-002/record.json` and `exports/index.html`.
5. Commit and push **only the reviewed related changes** with message `research: restrict GILB-002 to consistent evidence v3`.

## Safeguards
- Never delete source discrepancies from the audit archive.
- Never treat the share gap as an individual customer usage statistic.
- Story remains Analysis; no publication approvals or production assets are marked ready.
- Existing Claude audit and previous reports are preserved.
- Your live GitHub repository is not changed until you apply the package.

Sources:
- https://nca.org.gh/wp-content/uploads/2026/06/Q1_2026_Statistical_Bulletin.pdf
- https://nca.org.gh/wp-content/uploads/2026/10/Monthly-Industry-Data_July_2026-.pdf
- https://nca.org.gh/wp-content/uploads/2026/04/Data-Subscription-February-2026.pdf
