---
name: career-setup
description: Onboards a candidate to the career-search plugin and keeps their setup current — a quick start from just a CV to a first tailored result, then step-by-step deepening (variants, standing rules, search criteria, scoring, screening, house style), tracked on the setup page of their pipeline. Use when the candidate starts with the plugin, uploads a CV to get going, asks what is left to set up, or wants to add a target role, CV language, variant or criteria later.
---

# Career setup

Every other skill in this plugin holds only method. This skill creates and maintains the candidate's own sources, which hold everything personal. Folder layout and how to reach the folder: `references/folder-layout.md`. Templates for every source file: `references/templates/`.

Setup is split so the candidate gets a result fast and deepens later:

| Phase | Steps (`meta/setup` step ids) | Goal |
|---|---|---|
| **Quick start** | `qs-folder`, `qs-cv`, `qs-narrative`, `qs-cv-base`, `qs-pipeline`, `qs-first` | From one uploaded CV to a rendered CV and a first vacancy analysis, in about a quarter of an hour. |
| **Deepening** | `dp-questions`, `dp-variants`, `dp-rules`, `dp-criteria`, `dp-scoring` | One step per session, at the candidate's pace. |
| **Optional** | `op-screening`, `op-style`, `op-languages`, `op-writing-style` | When the candidate wants it. |

The setup page of the pipeline (the "Opzet" tab) shows this list with statuses, the requirements, links, updates and the open questions. Keep it current: it is how the candidate sees where they stand.

## Start: new or returning?

- **Returning** (the folder has `00 Sources/profile.yaml`): read `meta/setup` from the pipeline, say in two lines what is done and suggest the next open step. On a re-run, extend files and never overwrite them without showing the change.
- **New**: if the candidate hasn't uploaded a CV yet, ask for one (any format; a LinkedIn PDF export helps too) and explain in three lines what happens next. Don't ask anything else up front.

Show progress in chat with the task list (one item per quick-start step) while you work.

## Quick start

Only the folder is a hard requirement here. Ask the rest later, at the step that needs it.

1. **`qs-folder`**: check that a folder is connected (Claude desktop app). If not, explain how to connect one; fall back to the Google Drive connector only if the candidate prefers. Create the layout with empty `02 Screening/`, `03 Companies/`, `Sent/` (with `Sent - Index.md`: Date · Company / role · CV sent · Cover letter) and `99 Archive/`.
2. **`qs-cv`**: read the CV (and LinkedIn export). Fill a minimal `profile.yaml`: name, conversation language, folder paths, `target_level` and `previous_employer` from the CV. Leave the rest at template defaults.
3. **`qs-narrative`**: draft the career narrative from the CV, following the template. Write only what the CV says; mark the narrative "draft from CV" at the top. Every gap you notice becomes a **question** (see below), not a guess: team sizes, reporting lines, results without numbers, reasons for moves. Ask at most 8 questions now, the ones that change the CV most.
4. **`qs-cv-base`**: write `cv_base.md` with one variant (A), matching the level of the candidate's most recent role. Every line ⏳. Follow the template's structure rules exactly; the renderer depends on them. Render the generic CV with the cv-tailoring skill (default design) and send the PDF. Ask the candidate to mark anything wrong; corrections go into the narrative and the base.
5. **`qs-pipeline`**: create the pipeline page from `assets/pipeline-board.html` in the career-pipeline-tracker skill, following "Creating the page" in its `references/pipeline-schema.md`. Write `meta/setup` with all steps (statuses so far), the requirements (folder ✅, browser and scheduled tasks "unknown" until tested), links (the generic CV, the README), and the questions from step 3. Tell the candidate they can answer the questions on the page, any time, also from their phone.
6. **`qs-first`**: ask for one vacancy. Run the vacancy-analysis skill; offer the tailored CV with the cv-tailoring skill. This is the first real result. If the vacancy is a LinkedIn link, the browser preflight runs here: record its result as the browser requirement on the setup page. Mark the step done when the analysis is delivered.

Close the quick start with three lines: what exists now, the open questions on the setup page, and the next deepening step.

## Deepening (one per session)

- **`dp-questions`**: done when the first round of questions is answered and processed. Process answers as described in the career-pipeline-tracker skill ("Questions inbox"). Then ask the follow-up questions the answers raise.
- **`dp-variants`**: ask which kinds of roles they will apply for (two to four). Each becomes a CV variant with its own headline and profile, and a route in the search criteria. Walk through the base section by section; mark approved lines ✅.
- **`dp-rules`**: build `standing_rules.md` from every correction so far, plus: what may never be claimed, which domain terms outsiders don't understand (also into `cv.insider_terms`), which figures look odd to small companies, which lines to cut first.
- **`dp-criteria`**: fill `search_criteria.md` (exclusions, location and on-site limits, routes with title keywords, sectors to avoid, seniority bar), and help create the matching LinkedIn job alerts.
- **`dp-scoring`**: fill the scoring-model ladders from the criteria and the narrative. Write the model to the pipeline's `meta/scoring` too.

## Optional

- **`op-screening`**: test the browser with the browser preflight in the linkedin-job-screening skill (update the requirement on the setup page with the result and the fix), then offer a scheduled task that runs that skill. It needs the candidate's computer and signed-in browser. Record whether scheduled tasks are available.
- **`op-style`**: align the CV with their house style ("Design" section of the cv-tailoring skill).
- **`op-languages`**: a CV base per extra language, same IDs.
- **`op-writing-style`**: a personal writing-style skill (`setup-writing-style` if available); put its name in `writing_style_skill`.

## Questions: filling the narrative over time

Questions are how the narrative grows without long interviews. Write each one as a document in the pipeline's `questions` collection:

- `question`: one concrete question, answerable in a few sentences.
- `why`: what it improves (which CV line, variant or decision), in one sentence.
- `source`: where it came from ("quick start", "vacancy <company>", "rejection <company>").
- `status: open`, `askedAt`, `order`.

Ask about facts that change a CV or a decision: scope, numbers, results, ownership, reasons. Never ask for what the narrative already states. Keep at most about ten open questions; drop or merge stale ones.

## After every setup step

Update `meta/setup`: the step's status (`todo`, `active`, `done`), notes, and the requirements you tested. Add an entry to `updates` (`at`, `text`, `kind: setup`). Bump `meta/board.lastCompiled`.

## Rules

- Never invent experience, numbers or dates. Ask, through a question.
- Personal content goes into the candidate's files, never into a skill.
- Corrections are the system's fuel: whenever the candidate corrects something, the other skills put it into the narrative, `standing_rules.md` or `search_criteria.md`.
