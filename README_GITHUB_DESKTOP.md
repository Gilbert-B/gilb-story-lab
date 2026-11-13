# GilB — register final video archives for GILB-003 and GILB-005

This package is a **small incremental update to your existing `gilb-story-lab` repo**, not a replacement. It preserves GILB-001, GILB-002, GILB-004, and GILB-006. The two final videos are copied byte-for-byte from the ZIPs you supplied.

## 1. Prepare GitHub Desktop

1. Open GitHub Desktop and select **Gilbert-B/gilb-story-lab** (`main`).
2. Click **Fetch origin** and then **Pull origin** if shown.
3. Ensure the **Changes** tab is clean. If it isn't, back up or commit your existing edits before applying this update.
4. Click **Repository > Show in Explorer** to open your live local repository folder.

## 2. Merge the update files

1. Extract `GILB_003_005_Registry_Update.zip` somewhere OUTSIDE your live repository.
2. Open the extracted `GILB_003_005_Registry_Update` folder and copy **its contents** (`stories/`, `tools/`, and this README) into your existing local `gilb-story-lab` folder.
3. Allow Windows to **merge folders**. Do **not** overwrite existing `record.json` files or replace the whole repository with this ZIP. This package does **not** contain existing `record.json` files; the updater merges with them.
4. Confirm the two final videos now exist at:
   - `stories/GILB-003/production/final/GILB003_Ghanas_Sleeping_Wallets_Final.mp4`
   - `stories/GILB-005/production/final/GILB005_Accra_Growing_Shrinking_Final.mp4`

## 3. Run the original Story Registry updater

In File Explorer, while inside your live `gilb-story-lab` folder, click the location/address bar, type `powershell` and press Enter. Run these commands **one at a time**:

```powershell
py -3 tools/register_gilb003_005_final_videos.py
py -3 tools/registry.py validate
py -3 -m unittest discover -s tests -v
py -3 tools/registry.py build
```

Expected: `PASS` for both story records, six stories validated, tests pass, and exports rebuilt. The custom updater checks the SHA-256 fingerprint and size of each final MP4. It registers the masters as production artifacts, moves both stories to the `Review` stage, and does not mark them Published.

## 4. Check before committing

1. Double-click `exports/index.html`. GILB-003 should show `Ghana's Sleeping Wallets` at `Review`; GILB-005 should show `Accra Is Growing. Accra Is Shrinking.` at `Review`.
2. Open `exports/PRODUCTION.csv` in Excel. Both final masters should appear as asset records.
3. Verify GILB-004 is unchanged and still deferred.
4. In GitHub Desktop inspect **Changes**. Confirm your two MP4s are listed: the updater adds targeted exceptions to `.gitignore` (all other MP4s remain ignored).
5. Confirm the only source records changed are GILB-003 and GILB-005, along with a new updater, final-asset documentation, audit events, and regenerated dashboard/exports.

## 5. Commit and push manually

In GitHub Desktop, write commit summary:

`milestone: archive GILB-003 and GILB-005 final videos`

Click **Commit to main** and then **Push origin**. Open GitHub > Actions and verify `Update GilB story registry` succeeded. If the action makes another export-only commit, run **Fetch origin** and **Pull origin** again in GitHub Desktop.

## Important notes

- The original GILB-005 music-chart backlog idea and `DATA-005` are preserved as historical material and flagged as unrelated to the Accra video, rather than silently deleted.
- GILB-003's original `DATA-003` census-source lead also predates its reassignment and remains retained for provenance. It is **not** evidence of the mobile money story.
- **Review** means production is complete/delivered, with factual release QA outstanding. **Published** is reserved for a real dated post URL.
- GILB-005's 2010–2021 geographic equivalence remains a verification limitation; don't claim exact matched boundaries without additional evidence.
- The package does not contain your Git history, credentials, or the rest of your project. Do not upload the whole backup ZIP as a new GitHub repo.
- The updater can safely be run again. It will report `NO CHANGES` after successful registration, without duplicate assets/events.
