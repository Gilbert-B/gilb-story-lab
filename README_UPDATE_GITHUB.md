# GilB GILB-001 — Add the production blueprint to GitHub

**Package:** cumulative GILB-001 research + approved narration + approved interactive visual storyboard + draft production blueprint v1.0.

**Purpose:** Update the existing `gilb-story-lab` repository **without deleting its other five stories**. This also works if you have not applied the earlier research and storyboard ZIP updates yet.

## Step 1 — Back up and prepare

1. Open **GitHub Desktop** and select `gilb-story-lab`.
2. Click **Fetch origin**, then **Pull origin** if available.
3. Confirm **Changes** has no unrelated uncommitted edits. If it does, commit or safely stash those before the update.
4. Use **Repository → Show in Explorer** to open your local repo. Keep this window open.

## Step 2 — Copy the package

1. Extract `GilB001_Production_Blueprint_and_Registry_Update_v1.zip` to a folder in **Downloads**.
2. Inside the extracted folder, look for `stories/`, `tools/`, and `README_UPDATE_GITHUB.md`.
3. Select the **contents** of that extracted folder and copy them into your local `gilb-story-lab` directory.
4. Allow Windows to **merge folders**. Some files from earlier packages may have the same filename. If you have modified those files yourself, compare them first and keep your edits; do not blindly overwrite your work.
5. Verify these paths now exist directly under the repository:
   - `stories/GILB-001/production/blueprint_v1.md`
   - `stories/GILB-001/production/scenes_v1.csv`
   - `stories/GILB-001/storyboards/interactive/index.html`
   - `tools/sync_gilb001_production.py`

**Common mistake:** Do not paste an extra `GilB001_Production_Blueprint_v1/` parent folder inside your repository. GitHub Actions expects the above exact paths.

## Step 3 — Run the one-command update

1. In the local repository folder, click the Windows Explorer address bar, type `powershell`, press Enter.
2. Run:

```powershell
py -3 tools/sync_gilb001_production.py
```

If Windows does not recognise `py`, try:

```powershell
python tools/sync_gilb001_production.py
```

This script detects whether prior research/storyboard updates are already logged, imports them only if absent, and then registers the owner-approved interactive design and the **draft** production blueprint. It never approves claims or marks the video published.

3. Run validation and rebuild:

```powershell
py -3 -m unittest discover -s tests -v
py -3 tools/registry.py validate
py -3 tools/registry.py build
```

(Replace `py -3` with `python` if needed.)

4. Open `exports/index.html` by double-clicking it. Locate `GILB-001`. The **stage should be Production** (pre-production / animation preparation; no video has been generated). The next action should mention reviewing the blueprint and building a 24→13 motion proof.

5. Open `exports/PRODUCTION.csv` in Excel. Confirm GILB-001 has two new assets:
   - Interactive storyboard v1.0 — visual design approved; facts pending.
   - Production blueprint v1.0 — awaiting owner approval.

6. Open `registry/events.jsonl` and inspect the last event. It should describe the new draft and visual approval. **All claim `safe_to_publish` flags must remain unchanged** (usually `No`).

## Step 4 — Commit and push

1. In GitHub Desktop, review the **Changes** list. Make sure no personal secrets, large raw videos, or unrelated edits are included.
2. Enter summary: `docs: register GILB-001 production blueprint v1`.
3. Click **Commit to main**.
4. Click **Push origin**.
5. On GitHub, go to **Actions → Update GilB story registry** and check for a **green success mark**. If the registry script already generated the files locally, the action may report "Registry already up to date"; that is normal.
6. Click **Fetch origin** and then **Pull origin** in GitHub Desktop if Actions created a new commit.

## Step 5 — What it means and what happens next

The registry records **approval of the interactive storyboard**, but keeps the new production blueprint as **Draft**, because you have not reviewed it yet. No video and no final fact approval has been recorded.

After your blueprint review, the next deliverable is a **short motion proof** of the 34 match tiles → 24 clean sheets → 13 goalless draws, using the approved design. We'll then record the voiceover and retime the full sequence before rendering all 14 scenes.

## Troubleshooting

- **`ModuleNotFoundError: registry`**: run `tools/sync_gilb001_production.py` as written from the repository folder; `tools/registry.py` must exist.
- **`Missing ...`**: you likely copied the outer folder rather than its contents. Move the `stories` and `tools` directories to the repository root.
- **`Unexpected story status` or `Published`**: stop; the script intentionally refuses to downgrade previously completed stories.
- **`Merge conflict`**: preserve the existing GitHub version and compare differences before rerunning. Don't force overwrite the official story record.
- **`Python not found`**: install Python 3.11 or newer or use the existing Python used in your earlier GitHub setup.
- **GitHub Actions failed**: open its failed step and share the error; do not mark the video ready for publication.

**Source of truth:** `stories/GILB-001/record.json`. The `exports/` CSV and HTML dashboard are regenerated outputs, not manually maintained spreadsheets.
