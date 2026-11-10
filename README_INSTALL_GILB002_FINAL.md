# GILB-002 Final Master — GitHub Production Completion Update

**Scope:** Only GILB-002 production completion. No change to GILB-001, existing research/audit history, evidence approvals, or publishing records.

## Files included
- `stories/GILB-002/production/final/GILB002_v4_Score_B_Cinematic_Pulse_v2_Lower_Bed.mp4`: exact approved original, not re-encoded or substituted with earlier review cut.
- `stories/GILB-002/production/final/GILB002_FINAL_VIDEO_SHA256.txt`: expected fingerprint.
- `stories/GILB-002/production/final/PRODUCTION_COMPLETION_RECORD.md`: completion decision and technical specifications.
- `stories/GILB-002/production/final/RELEASE_QA_CHECKLIST.md`: items still needed before posting.
- `stories/GILB-002/production/final/.gitignore`: explicitly permits only this MP4 under a repo-wide `*.mp4` ignore.
- `tools/mark_gilb002_production_complete.py`: safe, repeatable registry updater.

## Install on Windows
1. In GitHub Desktop, select **gilb-story-lab**, click **Fetch origin** and **Pull origin** if relevant. Check your current **Changes** panel and preserve existing work.
2. Download/extract the ZIP, then copy its **contents** (`stories`, `tools`, README) into the **root** of your local `gilb-story-lab` repository. Choose merge folders; don't overwrite unrelated files.
3. In File Explorer, go to your repository's root. Click the path/address bar, type `powershell`, and press Enter.
4. Run:

```powershell
py -3 tools/mark_gilb002_production_complete.py
py -3 tools/registry.py validate
py -3 -m unittest discover -s tests -v
py -3 tools/registry.py build
```

5. Open `exports/index.html`. GILB-002 should display **Review** with a next action starting **Production complete**; this does not mean production is unfinished.
6. Check `exports/PRODUCTION.csv` for the exact approved final MP4 and `Completed — owner approved` milestone. Check the master file appears in GitHub Desktop **Changes**. If your version of Git ignores it despite the nested .gitignore, run `git add -f stories/GILB-002/production/final/GILB002_v4_Score_B_Cinematic_Pulse_v2_Lower_Bed.mp4` from PowerShell, then review it.
7. In GitHub Desktop, **select only** the GILB-002 final video, its closeout documents, updated `stories/GILB-002/record.json`, `registry/events.jsonl`, and generated exports plus the updater. Leave unrelated uncommitted changes unchecked.
8. Commit: `milestone: complete GILB-002 video production`; click **Push origin**. In GitHub Actions, verify the registry workflow passes.

## Important
- The file is ~7.4 MB, so committing this selected master is feasible. For future much larger media, use external immutable storage or Git LFS instead of ordinary Git history.
- GitHub is a project archive here, **not** evidence that the video was posted on TikTok/Instagram.
- Production completion approval has been given. Factual public-release and third-party rights checks are still separate; do not mark published or approve claims using this updater.
- A second run of the updater makes no duplicate assets or completion events.
- Neither this ZIP nor these instructions edit your GitHub repository until you apply and commit them locally.
