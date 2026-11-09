# GILB-002 — Primary-source verification and documentation update (v2.0)

This package extends the existing GILB-002 analysis with a publication-quality, *externally reviewable* methods report, source comparison ledger, and updated registry audit trail. It is safe to apply whether you have already installed the GILB-002 v1 analysis or still need to do so. No story is approved for publication by this package.

## Install on Windows using GitHub Desktop

1. In GitHub Desktop open `gilb-story-lab`; Fetch and Pull origin. Ensure no unrelated uncommitted changes.
2. Extract this ZIP and copy the **contents** into the top level of the local `gilb-story-lab` folder. Keep the existing `record.json` intact. Inspect any overwrite prompts: this ZIP adds new files plus the prior GILB-002 analysis package, and must not overwrite user edits without comparison.
3. In File Explorer, open your repository folder; type `powershell` in the address bar, press Enter.
4. Run each command (the analysis registration is safe to repeat):

```powershell
py -3 tools/check_gilb002_data.py
py -3 tools/register_gilb002_analysis.py
py -3 tools/verify_gilb002_nca_v2.py
py -3 tools/register_gilb002_verification_v2.py
py -3 tools/registry.py validate
py -3 -m unittest discover -s tests -v
py -3 tools/registry.py build
```

5. Open `exports/index.html`. GILB-002 should be in Analysis. Open `exports/ANALYSIS_LOG.csv` and `exports/PRODUCTION.csv` (if present); verify source-check report links in the story's `record.json`, and the issue `GILB002-HUMAN-SIGNOFF` remains open. The old `GILB002-ROW-QA` row should be marked resolved if it existed.
6. Commit in GitHub Desktop with `research: verify and document GILB-002 analysis v2` and Push origin. Verify GitHub Actions succeeds.
7. Keep the NCA original PDFs in your archive when downloaded, and request human peer review of all eventual video claims. **Do not mark evidence safe to publish just because this report has 93 source-table matches.**

## New reporting standard

`docs/GilB_Analysis_and_Verification_Reporting_Standard_v1.md` defines what every GilB research stage must produce. Create a new versioned report after each material analysis; attach it to the registry as a research asset.

## Source-preservation note

This ZIP includes NCA source URLs and independent published-table transcription, but **not the original NCA PDF files** (external source retrieval did not provide downloadable local PDF binaries here). The report documents that remaining archive requirement explicitly. Source counts were checked through the original PDF tables in the NCA publication views on 2026-11-08.
