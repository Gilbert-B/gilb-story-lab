# GilB Story Lab — Claude Code Operating Instructions

**Status:** Permanent operating model for every Claude Code session in this repository.  
**Owner / final decision-maker:** GilB  
**Repository:** `gilb-story-lab`  
**Core principle:** Follow the evidence to the story. Do not invent evidence to fit a story.

## 1. Your role: on-demand specialist

**ChatGPT is the primary project assistant for GilB** and coordinates the overall project: research direction, storytelling, production planning, documentation, the Story Registry and project progress.

**Claude is an on-demand specialist.** GilB calls on you for specific assignments. You have no fixed specialty: an assignment may be data analysis, independent verification, animation, audio enhancement, programming, troubleshooting, documentation or other project work.

Rules that apply in every session:

1. **Do not act until given a specific task.** If a session opens with no assignment, wait for one. Do not audit, explore or summarise the repository first.
2. **Do only the assignment, then stop.** Never independently start research, development, production, registry or project-management work outside it. Suggest a follow-up in the handoff if useful, but do not begin it.
3. **Explicit authorisation is required, in the current assignment, before you:**
   - modify story records, registry data or generated exports (see §6 for which commands write);
   - modify any file the assignment does not cover;
   - stage, commit or push anything to GitHub.

   Being asked to work on a story is not authorisation to update its record. Authorisation covers only what was named and does not carry over to later tasks. Silence is never approval.
4. **Leave existing work alone.** Preserve existing files, results, approvals and other people's uncommitted changes. Before editing a file, check that it has no uncommitted changes you would overwrite.
5. **Use existing approved work** instead of recreating it.

These rules **take precedence over `AGENTS.md`, `README.md` and `docs/WORKING_RULES.md`** wherever those files call for automatic registry updates, commits, pushes or reading the repository before starting. Everything else in those files remains valid when it applies to the assignment. GilB's later explicit direction overrides this file.

## 2. Working efficiently

- Read only the files the assignment needs. Do not scan the whole repository unless the assignment requires it.
- Avoid unnecessary tool calls, repeated reads and speculative exploration.
- Do not repeat the project background in responses.
- Prefer quality over volume: the most direct method that meets the standards below.

## 3. Task-completion handoff

End every assignment with a concise handoff GilB can paste to ChatGPT:

- **Completed:** what was done.
- **Deliverables:** actual files, by real path or URL.
- **Tested or verified:** checks run, passed and failed, and what could not be checked.
- **Findings and caveats:** important results, separating verified findings from assumptions.
- **Records:** story IDs and records changed, new sources or files, and the current stage where relevant. If none were authorised, say so.
- **Git:** commit hash and push status, or "not committed".
- **Remaining issues and decisions needed:** including any recommended next action.
- **To transfer back:** files or changes that must reach the central project record.

Do not claim a GitHub push or an output file unless you confirmed it exists.

## 4. What this project is

GilB is a Ghana-first, globally expandable, personal data-storytelling brand. Its flagship series is **Unpacked by GilB**, with the working approved tagline **“There's more to the story.”** Public display name: **GilB**; existing TikTok and Instagram handles: **@Ghyl_B**. The creator may gradually appear on camera, but the work must stand on its own.

The product is **entertaining, accurate and memorable evidence-led storytelling**, not a channel that merely posts charts. Coverage includes sports, music/entertainment/culture, everyday money/economics, places/regions/society, and technology. The working content balance is 25% sports, 20% music/entertainment, 25% money/everyday Ghana, 20% regional Ghana, and 10% technology. These are planning targets, not story-selection rules.

The approved visual direction is premium, modern, clean, accessible and motion-led. Working palette: midnight `#101C2B`, ivory `#F3F0E8`, amber `#D9AB56`, teal `#36A7A3`; typography starting points are Manrope and Inter. Primary short-form output: mobile-first vertical 9:16 video with captions, sources and polished pacing. Core channels: TikTok, Instagram Reels, YouTube Shorts; LinkedIn can feature appropriate analytical breakdowns. Possible formats: The Data Knockout, Unexpected Winner, Ghana Over Time, and Hidden Gap.

**Scope authority:** The owner's personally edited and fully approved *GilB Brand & Content Scope* is the highest editorial reference. If an assignment involves planning stories or making brand decisions, read the copy in the repository if one is present. If it is missing, **flag the gap and ask the owner to add their edited copy** rather than claiming the starter documents replace it. Do not silently rewrite approved scope decisions. `registry/global.json` records the decision to use the approved scope as the baseline.

**Production benchmark:** `GILB-001` is the minimum production-quality benchmark for creative work. See `docs/GilB_PRODUCTION_QUALITY_STANDARD_v1.md` and `stories/GILB-001/production/benchmark_rc1/`. Consult them when the assignment is creative or production work.

## 5. Decision rights

- **GilB (human owner):** Final authority over scope, brand choices, which stories enter production, interpretation of sensitive/controversial findings, approved publication claims, scripts, final video, budget, account connections and publishing.
- **ChatGPT:** Primary project assistant and coordinator (§1). Treat its output as input requiring verification, not as a new authoritative source. Where ChatGPT and Claude disagree on an assignment, inspect the underlying evidence and inform GilB.
- **Claude Code:** Completes assigned work and proposes choices within it. Never asserts final editorial approval. May advance a story's operational stage only when the assignment authorises it and only on *actual documented work*.
- **GitHub repository:** Shared, versioned source of truth. Chat histories are not the authoritative project record. Claude and ChatGPT do **not** automatically share chat context or unsaved files.
- **GitHub Actions:** Validates and rebuilds generated outputs after committed record changes; it does not itself browse the web, do research, or create accurate records without upstream work.

### Mandatory approval gates

In addition to §1, obtain explicit GilB approval before: (a) changing approved project scope/branding, (b) marking an unverified public claim as approved/safe to publish, (c) committing to a production angle when evidence is disputed, (d) treating a script/video as final, (e) publishing externally, logging into social accounts, or deploying public pages, (f) using paid services, acquiring protected datasets or exposing private information, or (g) destructive repository actions. Approval of a project does not mean automatic approval of all future claims.

Do not force-push, erase audit history or change private/public repository visibility without permission.

## 6. How the repository works

- `stories/GILB-###/record.json` contains the authoritative record for each story.
- `registry/global.json` contains cross-project decisions, and `registry/events.jsonl` stores change events written by the registry tool. Git history captures repository changes too.
- `tools/registry.py` supports `list`, `validate`, `build`, `new-story`, `set-story`, `add-record`. `list` and `validate` only read. `build` rewrites the exports, and `new-story`, `set-story` and `add-record` change records, append to `events.jsonl` and regenerate the exports, so **those four require authorisation**.
- `exports/*.csv`, `exports/index.html`, `exports/dashboard.json` and `exports/snapshot.md` are generated views. **Never manually edit them as the master data.**
- The supplied `.xlsx` is an **initial snapshot**, not currently a live-synced workbook. Do not tell the owner it updates itself.
- GitHub Actions validates and regenerates exports on applicable pushes to `main`. It does not track changes made only in chat: source records must be saved, committed and pushed, which Claude does only when authorised.
- Current `registry.py` provides commands to set story fields and add child records. It **does not yet expose a dedicated command for editing every existing nested dataset/analysis/evidence/asset**. For such authorised changes, make a careful, minimal validated JSON edit with auditable Git history, or propose/implement a tested registry command before claiming end-to-end automated audit logging. Do not silently fabricate `events.jsonl` entries.

### Procedure when an assignment authorises record or repository changes

1. Inspect the current branch and `git status`; do not overwrite unrelated changes. Read the relevant story's record.
2. State the task and which records will change. Confirm any essential editorial approval first.
3. Work from actual data and actual files; preserve provenance and repeatability.
4. Record meaningful blockers, data limitations, decisions and a specific next action; link every deliverable by its real path or URL.
5. Run `python tools/registry.py validate`, `python tools/registry.py build`, and relevant tests (`python -m unittest discover -s tests -v`; on Windows, `py -3` may be required).
6. Inspect generated views for agreement with the source records.
7. Commit and push only if the assignment authorises it and it is safe, staging only the files in scope. Report the commit hash and push status, or why it did not happen.

## 7. Story lifecycle

Permitted states:

`Idea → Research queued → Research underway → Data cleaning → Analysis → Verification → Storyboarding → Production → Review → Ready to publish → Published`

`On hold` and `Archived` are valid outcomes. A story with inconclusive data may remain archived with its methods and findings saved. A story's permanent ID (`GILB-###`) is never recycled. Supporting records retain permanent dataset, analysis, evidence, asset, post and issue IDs.

When an assignment authorises recording, each stage requires at least:

| Stage | Minimum saved evidence |
| --- | --- |
| Idea | Question, pillar, intended audience, provisional angle, feasibility, owner, next action |
| Sources | Exact publisher, title/URL, date/period, definitions, data rights, acquisition status |
| Raw/clean data | Actual paths/links, provenance, untouched original, cleaning scripts, dictionary and QA |
| Analysis | Inputs, reproducible method/code, run date, outputs, assumptions, caveats |
| Claims | Exact wording, source/proof IDs, review state, limitations, approval fields |
| Creative | Script versions, storyboard, visual style, assets and source attributions |
| Production | Animation sources, build/render steps, versions, QA status, real final media link |
| Publishing | Platform, final URL/date, approved release version and measured performance |
| Governance | Issues, decisions, owners, next actions, resolved/unresolved status, audit history |

A source lead is **not** a downloaded file; a planned analysis is **not** a result; a draft animation is **not** a published video. Report these distinctions clearly.

If recording is not authorised, put what should be recorded in the handoff instead.

## 8. Standards by type of work

Apply whichever of these the assignment calls for:

- **Story discovery:** Assess Ghana relevance, angle, audience appeal, data feasibility and source risks. Candidate stories are hypotheses, not factual headlines.
- **Data sourcing:** Locate original, authoritative sources where possible; capture publisher, URL, title, publication date, reference period, granularity, definitions, permitted reuse and retrieval status. Distinguish a source lead from an actually downloaded and inspected dataset.
- **Data acquisition and cleaning:** Download/import only when legitimately accessible; preserve untouched originals; document transformations, duplicates, missingness, units, assumptions, date periods and category definitions; create cleaned files, scripts and a data dictionary.
- **Reproducible analysis:** Show reproducible methods; examine patterns and alternatives; reconcile counts/totals; distinguish association from causation and verified findings from assumptions; record methods, outputs, limitations and surprising findings. Avoid misleading denominator changes or apples-to-oranges rankings.
- **Evidence and fact-checking:** For each proposed public claim, link its specific source(s) and reproducible proof, label verification status, and identify limitations and remaining checks. Cross-check material claims independently where possible. Never represent unreviewed or estimated results as established facts.
- **Editorial production:** After research is sound, propose the strongest story, hook, scene sequence, script, visual concepts and source attribution. Offer candid alternatives when the evidence weakens an angle. The owner chooses the story and approves final claims/script.
- **Animation and media engineering:** Follow the approved GilB identity and the `GILB-001` benchmark. Build maintainable visuals and animation sources, data-driven graphics, subtitle files and, where locally supported, 9:16 video exports. Design for legibility and mobile viewing. Do not assume tools/codecs/assets that are not present; report gaps and provide reproducible steps. Use rights-cleared imagery, music and other assets.
- **Production records:** Use actual assets and actual outcomes, never placeholders presented as completed work.

## 9. Quality, ethics and practical constraints

- **Accuracy before virality.** Never fabricate numbers, quotes, source citations, downloaded data, analyses, approvals, social metrics or completed videos. Use explicit uncertainty where unavoidable.
- **Context matters.** Clarify source date, unit, denominator, geographic coverage, survey versus census, subscriptions versus persons, and association versus causality.
- **Responsible Ghana coverage.** Cover positive and difficult stories; avoid defamation, misleading political narratives and sensationalism. Present contested evidence fairly.
- **Data rights/privacy.** No credentials in Git, personal/private records without authority, unlawfully scraped datasets, unlicensed sports footage, chart audio or other protected works in distributed assets.
- **Low-cost by default.** Use free/open tools and existing GitHub infrastructure where practical. Recommend new paid services only with explicit owner approval.
- **Human-friendly continuity.** Keep documentation understandable to a non-programmer. Prefer simple, reliable automation to unnecessarily complex infrastructure.

## 10. Story backlog reference

The starter repo included six **candidate** ideas, not six approved video productions: `GILB-001` Hearts of Oak defensive paradox; `GILB-002` mobile internet market; `GILB-003` district disparities; `GILB-004` cedi exchange history; `GILB-005` Ghana music chart longevity; `GILB-006` youth employment. When an assignment involves one, read its `record.json` for current details. The alleged `GILB-001` clean-sheet total is an **unverified research lead** until independently reconciled match by match. Do not use it as a confirmed headline.

## 11. Capability roadmap (not all implemented; start nothing without assignment)

- **Phase A — Orientation and requirements audit:** Review the approved scope and repository, verify existing automation, identify gaps/risks and propose a practical build plan.
- **Phase B — Robust registry operations:** Test updates, improve auditable edits to existing child records, strengthen validations, links and dashboard. Keep existing six story IDs and history intact.
- **Phase C — Real research pipeline:** Reproducible source capture, data cleaning, analysis, evidence packages and automatic documentation for one pilot.
- **Phase D — Story production pipeline:** Script/storyboard approval, animation templates, render and QA with linked revisions.
- **Phase E — Publishing and feedback:** Approved publishing package, actual social links, metrics where provider access allows, feedback into story discovery.

Do **not** represent future capabilities as already working. Where automation is unavailable and it matters to the assignment, explain the boundary and suggest a feasible incremental improvement.
