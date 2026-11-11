# GILB-003 — Research stage and safe registry update

1. Review `stories/GILB-003/analysis/GILB-003_Analysis_and_Verification_v1.docx`.
2. Copy the `stories/` and `tools/` folders into your current `gilb-story-lab` repository *after pulling changes*. Merge only; do not delete any existing story files.
3. Inspect the file `stories/GILB-003/record.json` if it exists. The updater will refuse an unexpected story state and should not overwrite existing music research.
4. Run `py -3 stories/GILB-003/analysis/reproduce_gilb003.py`
5. Run `py -3 tools/register_gilb003_research.py` (works against existing `tools/registry.py`; updates the status only after validating; may stop if schema differs).
6. Run `py -3 tools/registry.py validate`, `py -3 -m unittest discover -s tests -v`, and `py -3 tools/registry.py build`.
7. Check `exports/index.html`: GILB-003 Sleeping Wallets at Analysis; GILB-004 music at Idea/deferred; GILB-001/002 unchanged.
8. Inspect all GitHub Desktop changes before committing. Suggested message: `research: register GILB-003 sleeping wallets analysis`

This package DOES NOT include your live registry, cannot modify GitHub remotely, and does not change publication or evidence approval status. If the updater blocks, do not force a rename; share the error and the current `record.json` structure.

Main source: https://www.bog.gov.gh/wp-content/uploads/2026/09/Summary-of-Economic-and-Financial-Data-September-2026.pdf
