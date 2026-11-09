# Updating the GilB GitHub registry

1. Download and extract `GilB001_Full_Animation_Draft_v2.zip`.
2. Open your `gilb-story-lab` project folder (GitHub Desktop > Repository > Show in Explorer). Fetch/pull first.
3. Copy the **contents** of the ZIP into the *root* of the repository. This adds:
   - `stories/GILB-001/production/full_animation_v2/` (video + renderer + data)
   - `tools/register_gilb001_animation_v2.py` (one-time registry update)
   Keep `full_animation_v1` intact. Review any file conflicts instead of replacing unrelated work.
4. Open PowerShell in the repository root and run:

   ```powershell
   py -3 tools/register_gilb001_animation_v2.py
   py -3 tools/registry.py validate
   py -3 tools/registry.py build
   ```

5. Open `exports/index.html`: GILB-001 should remain in **Production**, and its production records should include the v2 animation as **Draft — owner review pending**.
6. Commit using GitHub Desktop: `production: add GILB-001 full animation v2 draft` then **Push origin**; check Actions is green.

The updater does **not** mark any claim approved or video published. Running it again will not create a duplicate production record. If the registry validation fails, stop and share the error rather than altering live evidence records.
