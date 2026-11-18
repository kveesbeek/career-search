---
name: cv-tailoring
description: Tailors the candidate's CV to a specific vacancy with the cv_base + config system — proposes changes per line ID against an approved base, renders an ATS-safe HTML and PDF, validates it and delivers a Check file. Use when the candidate wants a CV for a vacancy, asks to change or re-render the generic CV, or approves a CV proposal.
---

# CV tailoring (cv_base + config)

The goal: the candidate never re-reads a full CV. They review a change list against an approved base, and only the Check file after rendering.

## Read first, every time

From `00 Sources/` (see the career-setup skill for the folder layout and how to reach it):

| File | Role |
|---|---|
| `profile.yaml` | Name, languages, which base per CV language, writing-style skill, insider terms. |
| `standing_rules.md` | The candidate's accuracy rules (what may and may not be claimed), wording rules per reader type, variants, featured-block options, first cut candidates. Overrides anything general in this skill. |
| narrative (`files.narrative`) | Source of truth for facts. Never state anything that isn't there or confirmed in chat. New confirmed facts go into it, dated. |
| `cv_base.md` (+ one per language) | The only place CV wording lives. One line per ID: `- **[R1-03]** ✅ text`. Headline variants in a table, profiles as `PRO-A`, `PRO-B` ... ✅ approved, ⏳ open. |
| `cv_config - Base.yaml` (+ per language) | Generic CVs; output to `00 Sources/Generic CV/`. |

Per vacancy: `03 Companies/<Company>/cv_config - <Company> (<Role>).yaml`, with the HTML, PDF and Check written next to it. `Sent/` holds frozen copies of what was sent: never edit or regenerate them.

Re-read the base and the config every time before proposing or rendering, even within one session. The candidate edits them between turns.

Before proposing changes, process answered questions ("Questions inbox" in the career-pipeline-tracker skill): new facts may give a bullet its missing number. A bullet that would be stronger with a fact the narrative lacks becomes a question on the setup page, not an invented figure. After changing the base or rendering the generic CV, add an `updates` entry.

## Outgoing text versus internal fields

- **Outgoing text** (`text:`, `profile:`, `headline:`, anything in the PDF) is written as the candidate: implicit first person, verb first, never their name or "he/she/his/her/him". Apply the writing-style skill named in `profile.yaml`.
- **Internal fields** (`why:`, `variant_why:`, `tags_why:`, `profile_why:`, comments, the Check) are notes to the candidate, so the third person is fine there.

## Workflow per vacancy

1. **Read the posting in full** (fetch it if only a link is given; for a LinkedIn link, follow the browser preflight in the vacancy-analysis skill), the research brief in `03 Companies/<Company>/` if one exists, and any lessons from earlier rejections the candidate has recorded.
2. **Fit assessment** with the vacancy-analysis skill, if not done yet in this conversation.
3. **Change proposal in chat, before rendering**:
   - Variant + one-line reason. The headline level matches the posted title.
   - Featured-block option (`ai_option` 1 or 2), as `standing_rules.md` describes.
   - `insider_reader` true or false, as `standing_rules.md` describes.
   - Per changed ID: the full line with `~~removed~~` and `**added**` inline, then one or two sentences of reason.
   - Omitted IDs: full text struck through, with the reason.
   - Tags: at most 8. New order, new tags in bold, dropped tags struck through, reason.
   - 5–10 posting keywords, each mapped to the ID where it appears. Use the posting's term only for experience the candidate actually has; never copy sentences from the posting; never add a keyword without evidence.
   - Per rewording: ask whether it is for this vacancy only or should also go into the base.
4. **After approval**: write the config (template in `references/config-template.md`), render, validate, deliver the PDF and the Check.
5. **Pipeline**: update it with the career-pipeline-tracker skill in the same turn. A finalized CV is not an application.
6. **When the candidate confirms it was sent**: copy the PDF (and config, Check, HTML) to `Sent/YYYY-MM-DD Company - CV.pdf` etc., add a row to `Sent/Sent - Index.md`, update the pipeline.

## Rendering

The renderer ships with this skill: `scripts/render_cv.py`, with a default `cv_template.html` and `cv_fonts.css`. A `cv_template.html` in the candidate's `01 System/` folder overrides the default design. Render in the cloud workspace, which has Playwright and Chromium:

1. Copy the candidate's `00 Sources/` (profile, base, configs), their `01 System/` if it exists, and the vacancy config into one working folder that mirrors the layout. On the device bridge, stage the files; otherwise download them via the Drive connector.
2. Install `jinja2`, `pyyaml`, `markupsafe`, `playwright` if missing (`pip install --break-system-packages`).
3. From the working folder: `python3 <this skill>/scripts/render_cv.py "03 Companies/<Company>/cv_config - <...>.yaml"`. The renderer finds `00 Sources/` by walking up from the config. Outputs: `.html`, `.pdf`, `- Check.md` next to the config.
4. Look at the PDF pages as images: orphaned role headers, a lone Stack line at the top of a page, empty gaps, wrapped tags, the timeline dot clipping at the left edge.
5. Read the PDF back as text (`pdftotext`, without `-layout`): Education, Languages and Tools must extract one record per line.
6. Write the outputs back into `03 Companies/<Company>/`, guarding against overwriting newer versions. Send the PDF and the Check to the chat.

## Design: aligning the CV with a house style

The default design is a classic, text-first single column: centred header, section labels with a hairline, inline skills, Source Sans 3 with a dark slate-blue accent. The look comes from `cv.design` in `profile.yaml`: font family and embedded font files, ink/body/muted/rule colours, accent and its wash, the name's weight and tracking, section-label style (case, colour, weight, size) and tag radius. Missing keys keep the default.

A candidate who wants a layout of their own puts a `cv_template.html` in `01 System/`. It replaces the default template for that candidate only; the `cv.design` keys still apply to the extent the template uses them (`d.ink`, `d.accent`, `d.font_stack` ...). Start from the default template in `scripts/`, keep its variables and its ATS rules, and change the layout. Never edit the plugin's default for one candidate.

When the candidate has a design system or style sheet:
1. Get its tokens file (for a Design System artifact: `project/tokens.json`) and run `scripts/import_design_tokens.py <tokens.json> [--fonts-dir <dir>]`. It prints a `design:` block and notes on what it could not map.
2. Get the brand font as woff2 files per weight (400–800) into `01 System/fonts/`. Open-licence fonts are on npm as `@fontsource/<family>`. If the font cannot be obtained, use the design system's fallback stack and say so.
3. Put the block under `cv:` in profile.yaml, render the generic CV(s), and show page images next to the previous version.
4. Keep what an ATS needs, whatever the style sheet says: one column, real selectable text, embedded fonts, section titles as plain words (sentence case is fine), contact details as text, no text in images, no icons replacing words, colour contrast for body text of at least 4.5:1. Section labels may follow the design's eyebrow style.
5. A different font changes line breaks. Check every generic CV and open vacancy config against the page limit; fix overruns by cutting content (first cut candidates), not by shrinking the type, and let the candidate choose the cut.

## Validation (all green before delivery)

The Check file tests: page count against the layout maximum, no near-empty last page, section titles readable by ATS extraction, contact details extractable, no banned patterns (from `profile.yaml`, or the default list), no em dashes in profile and bullets, no insider terms in headline or profile for outside readers, keyword coverage.

Also check by hand:
- **Third person**: grep the extracted PDF text for the candidate's first name and third-person pronouns. Only the header and the page footer may name them.
- **Money figures against the reader's scale**, as `standing_rules.md` describes.

## Fitting the page limit

Layout and content are separate: never fix an overrun by editing the template.

| `layout:` | Margins | Body type | Pages |
|---|---|---|---|
| `compact` (default) | 16 mm | 9.45 pt | max 2 |
| `comfortable` | 20 mm | 10 pt | max 3, only on request |

Cut content, not the page: omit the lowest-relevance IDs for this posting, starting with the first cut candidates in `standing_rules.md`, or tighten wording. `layout_overrides: {side, top, bottom, scale}` is a last resort when nothing is left worth cutting; state the reason in a comment. Keep `letter-spacing` at or below 0.03em on uppercase text, or PDF extraction breaks words.

## Cover letters and application answers

Write them with the candidate's writing-style skill, from the narrative and the research brief, within `standing_rules.md`. Start with the substantive hook, not with "I am writing about the role". Save drafts in `03 Companies/<Company>/`; the version that was sent goes to `Sent/` with the CV.

## Changing the base

When the candidate approves a wording as permanent, update the base (and the same ID in the other language bases), keep IDs stable, mark the line ✅, and re-render the generic CVs. New lines get a new ID in the same prefix family. Never renumber IDs: configs refer to them. When an ID is retired, remove its references from working configs in the same step (never from `Sent/`). Record standing choices about the base in `standing_rules.md`.
