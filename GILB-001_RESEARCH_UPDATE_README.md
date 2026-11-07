# GilB-001 research update — 7 November 2026

This update does **not** require Claude Code, an API key or a database. It uses the existing Python registry automation.

## What it contains

- 34 Hearts of Oak 2025/26 league match scores, transcribed from RSSSF with attribution and source details.
- Reproducible calculation script and comparison with champions Medeama.
- Generated cleaned match metrics, research findings and calculation JSON.
- `tools/import_gilb001.py`, a repeatable importer that **merges into your existing `GILB-001` record** rather than replacing the whole registry.
- Source links and limitations for publication review.

## Installation via GitHub Desktop on Windows

1. In GitHub Desktop select your `gilb-story-lab` repository and **Fetch/Pull** first.
2. Open **Repository → Show in Explorer**.
3. Unzip this research update and copy its CONTENTS into that repository folder. You should see this README at the root and `tools/import_gilb001.py` under `tools/`.
4. Open PowerShell in the repository folder (type `powershell` in File Explorer's address bar).
5. Run:

```powershell
py -3 tools/import_gilb001.py
py -3 tools/registry.py validate
py -3 -m unittest discover -s tests -v
```

6. Check `exports/index.html`, story `GILB-001`, and `registry/events.jsonl`.
7. In GitHub Desktop review changes; commit as `research: reconcile GILB-001 season match results`; then **Push origin**.

**Do not copy a new `record.json` or overwrite the existing registry:** the importer updates it safely, preserves other stories and generates current views. This package has no replacement `record.json` or `events.jsonl`.

## Expected analysis (check before committing)

Hearts (2025/26): 34 games, 13 W, 15 D, 6 L, 25 GF, 15 GA, 54 points, 24 clean sheets, 13 goalless draws. Medeama: 62 points, 17 W, 11 D, 6 L. No evidence is automatically marked safe to publish.

## Important limitation

These findings come from an initial 34-row manual score transcription validated against final standings and Ghana FA's reported 24 clean sheets. Before publishing, the owner should spot-check the rows and explicitly approve the claims. No official raw match data feed was downloaded in this update.
