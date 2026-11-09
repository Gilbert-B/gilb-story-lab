# Apply the GILB-001 creative benchmark update to your GitHub repository

**This is a non-destructive, additive package.** It does **not** replace the existing registry or change the status of GILB-002 through GILB-006. Use your existing private `gilb-story-lab` repository.

## Windows + GitHub Desktop instructions

1. In GitHub Desktop, select `gilb-story-lab` and **Fetch origin**, then **Pull origin** if GitHub has new commits.
2. Make sure you have no unrelated changes awaiting commit; back them up first if you do.
3. Download and **Extract All** this ZIP to a temporary folder.
4. Open your local repository via **Repository → Show in Explorer**.
5. Copy the **contents** of the extracted ZIP folder (not its outer folder) into the repository root. Merge folders; do not overwrite personally modified files without checking. These files have new paths to avoid collisions.
6. In the repository's Explorer address bar, type `powershell` and press Enter.
7. Run:

   ```powershell
   py -3 tools/register_gilb001_benchmark.py
   py -3 tools/registry.py validate
   py -3 -m unittest discover -s tests -v
   py -3 tools/registry.py build
   ```

   If `py -3` is unavailable, use `python` or `python3` with your installed Python 3 interpreter.

8. Open `exports/index.html`. GILB-001 should show **Review** (not Published), and its `PRODUCTION.csv` should include the new benchmark file and quality documents. Approved claims should remain unchanged.
9. **Open GitHub Desktop → Changes.** The MP4 **should appear** because `stories/GILB-001/production/benchmark_rc1/.gitignore` specifically permits this file even though the parent repo ignores other MP4s. Verify it appears; if not, run `git check-ignore -v stories/GILB-001/production/benchmark_rc1/GILB001_Hearts_of_Oak_Creative_Benchmark_RC1.mp4` to diagnose, and only if needed use `git add -f` for this *one* known video.
10. Commit with: `milestone: archive GILB-001 creative benchmark RC1` and click **Push origin**.
11. On GitHub, open **Actions** and confirm that **Update GilB story registry** succeeds. Pull any automation commits back into GitHub Desktop afterward.

## Verification

- No other story should be altered.
- The source `stories/GILB-001/record.json` remains the registry authority; CSV/HTML are generated.
- Run the register command a second time if desired: it should report **NO CHANGES**.
- Confirm the video size/resolution: use `ffprobe` if available; source RC1 is **512 × 910**.
- The video source you uploaded is not Claude's editable animation project. To preserve full reproducibility, obtain the project's original source and all referenced assets separately.

## Important release status

GilB's owner approved the **creative benchmark**, not a final publication release. The update therefore sets the story to **Review**, retains all evidence approvals as-is, and leaves every post unpublished. The `FINAL_RELEASE_QA.md` file lists what still needs to happen.
