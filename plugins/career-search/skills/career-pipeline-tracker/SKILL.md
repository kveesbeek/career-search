---
name: career-pipeline-tracker
description: Updates the candidate's application pipeline page whenever a job-search status changes — a new research brief, a CV finalized or sent, an interview scheduled, a rejection, a role ruled out, a new contact, or a score to set or revise — and keeps its setup page current (steps, requirements, updates) and processes answers to the narrative questions. Use whenever such a change becomes known, also when the candidate does not ask for it, and at the start of any career task to process answered questions.
---

# Career pipeline tracker

The pipeline lives as a published artifact page, not a file. Its URL is `tools.pipeline_artifact` in `00 Sources/profile.yaml`. The page renders everything from its own database (schema in `references/pipeline-schema.md`); all content is written with the artifact database tools against that URL. Never hand-edit the page's HTML to add data, and never keep a separate spreadsheet or markdown tracker. This page is the single source of truth.

**Push, not pull.** Update the page in the same turn a change becomes known, whether the candidate reports it or the work in this conversation produces it (a new brief, a finalized CV or letter). Don't wait to be asked.

## Before writing

1. Read `00 Sources/profile.yaml`: pipeline URL, `languages.conversation` (language of all entries), `pipeline_notes` (the candidate's own wishes for layout and wording; follow them).
2. Before scoring, read the scoring model (`files.scoring_model` in `00 Sources/`) and `00 Sources/search_criteria.md`. The ladders get revised; a score set from memory drifts from the ones already on the board.

## Scoring

Every role carries six component scores (0–5): `senScore`, `domScore`, `locScore` (Fit) and `evScore`, `lvlScore`, `rteScore` (Winnability). The page computes Fit, Winnability, Priority and band. Never store derived numbers.

- **A new role card is not finished without the six scores.** A card without them drops out of the priority ordering.
- **Show the reasoning in chat**, one line per component, no half points, so the candidate can contradict one score instead of the total. Say when a special rule in the model fires.
- Report Fit, Winnability, Priority and band, and where the role lands against the current pipeline. Let the band drive the "how to apply" advice.
- **Re-score when inputs change**: a contact replying moves the route; a confirmed reporting line moves seniority; a clarified on-site policy moves location.
- **When the candidate corrects a ladder** rather than one score: change the scoring model first (bump version and date, record that it was their call), then re-apply it to every affected role in one batch. Query for the old value instead of fixing only the role in front of you. Then write the new model text to `meta/scoring`, so the page's own assistant scores with it too.

## How to update

1. **Existing role or contact changes state**: read the document to get its version, then update only the changed fields, pinned to that version. Update `stage`, `pillLabel`, `dateStamp` and the matching date field together. Keep `nextStep` and `nextStepDate` together, add a log entry under `roles/<id>/log` for every piece of news, and put durable context in `dossier` (full text, keeping what was there). Check whether the change also moves a score. For a contact, always update `lastAction` and `lastActionDate` together.
2. **New company enters the pipeline** (a brief or CV is created): create a document with a fresh slug, `stage: explore`, the six scores and whatever is known. Add `briefUrl` only when `tools.file_links` allows it and the brief's link was actually looked up; never guess a link.
3. **New contact**: same pattern in `contacts`, always with `type` and `lastActionDate`.
4. **Priorities shift**: update `meta/board.nextActions` deliberately; it is hand-picked, not derived.
5. **Applied means sent.** Only set `cvSubmitted` or move a role to `applied` once the candidate confirms the application was actually sent, not drafted.
6. Write in the conversation language, short and dense, matching the style already in the data.
7. Bump `meta/board.lastCompiled` on every change.
8. If a write is rejected because the document changed, re-read, merge and retry. Other sessions write to the same board; a stale version is routine. Never force.
9. Batch writes when more than a couple of documents change.
10. Never republish the page's HTML for a data change. Change the page's code only when the candidate asks, and keep the layout choices recorded in `pipeline_notes`.

## Questions inbox

The candidate answers questions on the pipeline's setup page; the page can't write files, so answers wait in the `questions` collection with `status: answered`. At the start of every career task (any skill of this plugin), check for them:

1. Query `questions` where `status == answered`.
2. Put each answer into the narrative, under "Confirmed by <name>, <date> (via questions)", in the candidate's words, tidied but not embellished. An answer of "(niet van toepassing)" / "not applicable" closes the question without a narrative change.
3. If an answer changes a CV line, propose the change to the base (cv-tailoring skill, "Changing the base"); don't change approved lines silently.
4. Set the question to `status: processed`, `processedAt`, and add one `updates` entry ("3 answers processed into the narrative").
5. Mention it in one line in chat, then continue with the task.

New questions come from the other skills whenever they find a gap; format in the career-setup skill ("Questions").

## Setup page

`meta/setup` holds the step list, requirements and links shown on the "Opzet" tab (schema in `references/pipeline-schema.md`). When a task completes a setup step or tests a requirement, update it. Every change to a source file (narrative, CV base, standing rules, criteria, scoring model, design) gets one `updates` entry: `at`, `text` (one sentence, what changed and why), `kind` (`source`, `setup` or `plugin`).

## Closing a role

When a process ends (rejected, ruled out, declined), update the card and move the company's folder from `03 Companies/` to `99 Archive/Companies/`, if no other role at that company is still open.
