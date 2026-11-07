# GilB — Research and Production Operating Rules

## Editorial scope and authority

The user's personally edited and approved **GilB Brand & Content Scope v0.1** is the authoritative brand document. This starter has not replaced it. The core identity is GilB; series **Unpacked by GilB**; tagline **There's more to the story**; handle **@Ghyl_B**; Ghana-first but internationally extensible; balanced sports, entertainment, money, regions, society, and technology. Do not make editorial decisions contrary to the scope.

## The registry is maintained *as we work*

Every substantial action should leave a trace in the relevant story folder and `record.json`. At minimum:

1. **New idea:** permanent ID, topic, pillar, question, intended audience, decision, next action.
2. **Source located:** `dataset` record, source name, URL, period, intended granularity, download status, reuse terms, limitations.
3. **Source downloaded:** raw-file path/link, acquisition date, provenance, original untouched copy.
4. **Data cleaned:** clean-file link, transformation script, data dictionary, missing-value and outlier decisions.
5. **Analysis conducted:** hypothesis/question, input dataset IDs, reproducible method/script, result, date, limitations, review state.
6. **Factual claim proposed:** exact evidence source, calculation/proof, status **Needs verification** until checked.
7. **Claim checked:** record who checked it, when, what was checked, and the owner's explicit approval before publishing.
8. **Creative asset created:** script/storyboard/animation/video version, exact saved path, review status.
9. **Published:** platform, real post URL, date and video version; add analytics only after measured.
10. **Issue/decision:** blocker, owner, next action, resolution and date; preserve abandoned ideas.

No manufactured numbers, source pages, downloads, results, approvals, video files, follower counts or URLs. A source lead is NOT a downloaded dataset. An attractive exploratory finding is NOT publishable evidence.

## Clear status terminology

Story stages: Idea → Research queued → Research underway → Data cleaning → Analysis → Verification → Storyboarding → Production → Review → Ready to publish → Published. `On hold` and `Archived` remain available.

The record may contain planned analyses, storyboards, or asset placeholders at any stage, but they are **not completed deliverables** until an actual file or reproducible output exists.

## Files, links and naming

- Story ID `GILB-001`, `GILB-002`, etc.; IDs never reused.
- One JSON per story is the source of truth; generated CSV and HTML views are not edited manually.
- IDs: `DATA-001`, `AN-001`, `EV-001`, `AS-001`, `POST-001`, `ISS-001`.
- Prefer relative paths within the repository for small research outputs, direct source URLs for public data, and secured shareable links for large media.
- No credentials, private customer data, unauthorised datasets or licensing-restricted source files in commits. Handle copyright for music, sports images, and videos separately.
- Whenever a source changes, re-run analyses and re-check dependent claims before publication.
- Never quietly overwrite a corrected source or a prior published video; make a new revision and record the change.

## Working with multiple assistants

Claude Code and ChatGPT should inspect the **current repository and records** before modifying anything. Git commits and PRs are the collaboration history; avoid editing the same story branch simultaneously without resolving conflicts. The tools do not automatically share chat memory or see unsaved changes in the other environment.

The AI's job is to minimize paperwork, not remove judgement. The owner chooses which topics to pursue, approves factual claims, creative interpretation, and publication.

## Before declaring a task complete

- `python tools/registry.py validate` must pass.
- `python tools/registry.py build` must pass.
- Every real dataset/analysis/asset created must be linked by ID or path.
- The status shown in the dashboard must agree with reality.
- If using GitHub, commit and push the work so the scheduled workflow can refresh the shared exports.
