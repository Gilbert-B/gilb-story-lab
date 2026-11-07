# GilB Story Registry — Automation Starter

**Brand:** GilB · **Flagship:** Unpacked by GilB · **Tagline:** There's more to the story.  
**Scope:** Ghana-first, globally expandable, balanced entertainment and serious evidence-led stories.  
**Owner:** GilB · Instagram/TikTok: `@Ghyl_B`

## What this actually does

- Preserves the **6 ideas and all the research placeholders** from the existing GilB Story Registry v1. The figures and story ideas are **not treated as verified**.
- Keeps one editable, human-readable `record.json` per story in `stories/GILB-###/`.
- Automatically creates a stable ID for new stories and for datasets, analyses, evidence, assets, posts and issues.
- On every change, rebuilds **7 Excel-friendly CSV register tabs, a searchable HTML dashboard, a JSON summary and a Markdown snapshot**.
- Includes tests and publication safeguards. A story cannot be set to Ready to publish / Published with unapproved claims. A Published story needs a published post URL and date.
- Works offline with **Python standard library**—no database or subscription required.
- Once placed in a GitHub repository, GitHub Actions validates and refreshes views **when record changes are pushed to `main`**.

> **Important:** The CSV exports and HTML dashboard are automatically refreshed. The enclosed formatted Excel `.xlsx` is an **initial reference snapshot**, not a continuously synced live workbook. Excel can open each exported CSV directly. A live, multi-sheet spreadsheet sync can be added later after choosing/connecting a spreadsheet provider. Do not edit the generated views; edit story records.

## Windows — first setup (GitHub Desktop, easiest)

1. Create a **private** GitHub repository named `gilb-story-lab`. Use a private repository initially because raw datasets may have reuse limitations.
2. Install/open GitHub Desktop, clone the new repository to your computer.
3. Extract this ZIP and copy its **contents** (including `.github`, `stories`, `tools`, `registry`, `exports`) into the cloned repository directory.
4. In GitHub Desktop, commit as `Initialize GilB story automation`, then **Push origin**.
5. In GitHub, go to **Actions** and confirm `Update GilB story registry` has run. If Actions are disabled, enable them for the repository. It needs `contents: write` to commit exports; see GitHub's workflow-permissions settings if it fails.
6. Open `exports/index.html` locally to view the searchable dashboard, or open any `exports/*.csv` in Excel.
7. For changes made in Claude Code or by editing a story JSON, **commit and push**: the GitHub Action automatically regenerates the views. The dashboard in GitHub is a generated file, not a hosted public web page.

No GitHub account is connected to ChatGPT yet, so **this package does not itself create or push a live repository**.

## Try it locally first

From the extracted folder on Windows PowerShell:

```powershell
py -3 tools/registry.py list
py -3 tools/registry.py validate
py -3 tools/registry.py build
py -3 -m unittest discover -s tests -v
```

On macOS/Linux, use `python3` instead of `py -3`.

## Useful commands

**Create a new story** (the next permanent ID is assigned automatically):

```powershell
py -3 tools/registry.py new-story "Which club improved most away from home?" --pillar "Sports & competition" --next-action "Find complete match results"
```

**Update an existing story:**

```powershell
py -3 tools/registry.py set-story GILB-001 --field "stage=Research underway" --field "next_action=Obtain and reconcile match-level results"
```

**Record a source lead for a story** (it is *not* marked as downloaded):

```powershell
py -3 tools/registry.py add-record GILB-001 dataset --field "name=Season match results" --field "publisher=Ghana FA" --field "source_url=https://www.ghanafa.org/" --field "acquisition_status=Not downloaded"
```

**Add an analysis task** (not a completed finding):

```powershell
py -3 tools/registry.py add-record GILB-001 analysis --field "question=Recalculate clean sheets" --field "approach=Count matches with zero goals conceded" --field "status=Not started" --field "input_dataset_ids=DATA-001"
```

The command updates the right `record.json`, appends to `registry/events.jsonl`, checks the data, and regenerates the exports. **Don't run example add-record commands blindly:** they create real records; the six stories already contain source leads and planned tasks.

## Your workflow with Claude Code / ChatGPT

Ask your coding assistant: 

> Open the GilB story-lab repository, read `AGENTS.md` and `docs/WORKING_RULES.md`, then work on GILB-001. Track every source found, dataset downloaded, cleaning step, analytical result, verification status and creative asset in its record.json. Run `python tools/registry.py validate` and `python tools/registry.py build` before committing. Never mark claims Verified or publishable without my explicit approval.

Claude Code can run the Python tool and commit/push changes in your local clone with the appropriate permissions. For ChatGPT to directly edit the repository, **you would need to connect GitHub and grant the relevant access**. A chat by itself cannot silently update a file on your computer or GitHub.

## How each story is stored

```text
stories/GILB-001/
  record.json                 # master structured story record
  data/raw/                   # collected originals, if reuse is permitted
  data/clean/                 # cleaned datasets and data dictionaries
  analysis/                   # reproducible scripts/notebooks and results
  evidence/                   # source screenshots, calculation proofs
  scripts/                    # narration scripts
  storyboards/                # scene plans
  animations/                 # source for animations (not large video exports)
```

Video masters and large assets should stay in a private Drive folder or other storage, with exact shareable links recorded under `assets` and `posts`. Keep protected or non-public datasets out of the repo unless appropriately licensed and authorised.

## Project map

- `stories/` — **the authoritative source records**
- `registry/global.json` — project-wide decisions (including approved scope)
- `registry/events.jsonl` — audit log of changes made using commands (Git history also captures direct JSON edits)
- `tools/registry.py` — create, update, validate and export records
- `exports/*.csv` — automatically generated Excel-friendly registers
- `exports/index.html` — searchable offline dashboard
- `exports/dashboard.json` — machine-readable summary
- `.github/workflows/` — GitHub Actions validation and regeneration
- `tests/` — integration tests with isolated sample stories
- `docs/WORKING_RULES.md` — research-to-publication operating rules

## How publication approval works

1. Record the actual source (exact document, page, table or URL), reproducible proof, and finding.
2. Check every claim independently, document limitations and obtain the user's explicit approval.
3. Only then set an evidence record to `verification_status=Verified`, `safe_to_publish=Yes`, with `checked_by`, `checked_on`, `approved_by`, and `approval_date` (plus a source or proof).
4. Only mark a story `Ready to publish` when **all** its evidence records are approved.
5. A `Published` story also requires a post with `publish_status=Published`, `post_url` and `actual_date`.

All six imported story ideas start without a verified claim. `GILB-001`'s clean-sheet number is explicitly a **research lead**, not a cleared claim.

## Current starting point

| Indicator | Value |
|---|---:|
| Candidate stories | 6 |
| Datasets downloaded | 0 |
| Verified and approved claims | 0 |
| Published stories | 0 |
| Open research issues | 1 |

**Next step after uploading:** perform one real test on `GILB-001`: save a verified source link or file, run the cleaning/analysis, attach the analysis output, and check that the data-source and analysis registers update. This is not permission to publish the findings.
