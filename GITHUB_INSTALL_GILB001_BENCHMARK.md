# GilB benchmark v1.1 — correction to original master status

This package updates **GILB-001**. It works whether the earlier benchmark package has already been added or this is your first benchmark installation.

**Change:** Re-export issue closed. GilB has already confirmed the original video is high-resolution; the 512 × 910 copy is a chat-compressed review file. Only archival inspection of the existing original master remains outstanding.

## Steps (Windows + GitHub Desktop)

1. Open `gilb-story-lab` in **GitHub Desktop**. Select **Fetch origin** and **Pull origin** if available. Review and save any unrelated local changes before proceeding.
2. **Download and extract** this ZIP.
3. Select **Repository → Show in Explorer**. Copy the **contents** of the extracted folder into the repository root, merging folders and replacing only the previous benchmark package's files. **Do not replace any personally edited research records.**
4. In the repository File Explorer address bar, type `powershell` and press Enter.
5. Run these commands **one at a time**:

   ```powershell
   py -3 tools/register_gilb001_benchmark.py
   py -3 tools/registry.py validate
   py -3 -m unittest discover -s tests -v
   py -3 tools/registry.py build
   ```

6. Open `exports/index.html` and `exports/ISSUES_AND_DECISIONS.csv`. The old `BENCHMARK-RC1-EXPORT` issue, if it already exists, should be **Closed**. `GILB-001` remains **Review**, not Published.
7. Commit in GitHub Desktop with `fix: record GILB-001 original master resolution confirmation`, then **Push origin**. Check the GitHub Actions run.
8. OPTIONAL BUT RECOMMENDED: Find the **original high-resolution video file**, not the compressed copy from ChatGPT. If it is small enough for GitHub, copy it to:

   `stories/GILB-001/production/benchmark_rc1/GILB001_Hearts_of_Oak_Original_Master.mp4`

   Then run `py -3 tools/register_gilb001_benchmark.py` again. It will calculate its SHA-256, record its path, and inspect dimensions using `ffprobe` if that utility is installed. **Do not re-export merely to satisfy this step.**

   If the original is over GitHub's 100 MB single-file limit, keep it in private cloud storage instead and record its secure link in the archive notes. The automated script will not upload an external video or create a cloud link.

## Expected registry state

- Creative benchmark: **Approved**.
- Original full-resolution export: **Owner confirmed; no re-export needed**.
- Original master file archive/independent metadata check: **Pending until supplied**.
- Claude editable project: **Still to archive**.
- Evidence, captions, audio licensing, final release sign-off: **Still pending**.
- Stage: **Review**; publishing remains unchanged.

This package includes the compressed chat review copy to keep the earlier archive reference intact. It should not replace your original high-resolution file.
