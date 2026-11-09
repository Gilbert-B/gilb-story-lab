# GilB — Mark GILB-001 production complete

This is a **small incremental update**, not a replacement of your existing GitHub project or benchmark. It only updates `GILB-001` and adds production-closeout documentation. It does not change claim approvals or publish the video.

## Installation (Windows with GitHub Desktop)

1. Open GitHub Desktop, select `gilb-story-lab`, **Fetch origin** and **Pull origin** if needed. Make sure unrelated local changes are safely committed or backed up.
2. Download and extract the ZIP. Open the extracted folder.
3. In GitHub Desktop select **Repository → Show in Explorer** to open your local repository.
4. Copy **contents** of the extracted update folder (the `tools/` and `stories/` folders and this README) into your repository root. Merge folders; do not replace `record.json` or your original video. Do not put the extracted folder inside the repository as an extra nested level.
5. In the repository File Explorer window, click the address bar, type `powershell`, press Enter.
6. Run:

```powershell
py -3 tools/mark_gilb001_production_complete.py
py -3 tools/registry.py validate
py -3 -m unittest discover -s tests -v
py -3 tools/registry.py build
```

7. Open `exports/index.html`: the GILB-001 **Stage** should read **Review** (the video production is complete; release QA is separate). The **Next action** should begin `Production complete`.
8. Open `exports/PRODUCTION.csv` and search `GILB-001 — Production Complete (Owner Approved)`. The milestone **Status** should be `Completed — owner approved`.
9. Open `stories/GILB-001/production/production_closeout_v1/PRODUCTION_COMPLETION_RECORD.md` to see the closeout decision and remaining release gates.
10. In GitHub Desktop inspect changes, commit with `milestone: complete GILB-001 video production`, then click **Push origin**. Check GitHub Actions is green.

## Important

- No claim is automatically marked `safe_to_publish` by this updater.
- No post is automatically created or marked `Published`.
- The user-confirmed original full-quality master stays the true source video; don't replace it with the chat-compressed copy.
- You can run the updater again safely: it will report `NO CHANGES` and will not create duplicate records.
- This package doesn't connect to GitHub by itself. The changes appear in the live repository only after you copy, run, commit and push them.
