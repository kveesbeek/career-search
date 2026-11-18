---
name: linkedin-job-screening
description: Screens the candidate's LinkedIn job alerts and recommendation feed for new vacancies, scores each against their search criteria and appends the run to the LinkedIn Ranking file. Use for the screening scheduled task, or when the candidate asks to check LinkedIn for new jobs.
---

# LinkedIn job screening

Checks every LinkedIn job alert plus the "Jobs based on your preferences" feed, scores each new vacancy, and appends one dated section to the ranking file. This skill holds the method. What the candidate looks for and excludes lives in `00 Sources/search_criteria.md`; read it at the start of every run, because it changes.

## Files

| File | Role |
|---|---|
| `00 Sources/profile.yaml` | Folder location, conversation language (language of the ranking), browser to use. |
| `00 Sources/search_criteria.md` | Scope, exclusions, location limit, routes, seniority criteria. The only place these rules live. |
| narrative (`files.narrative` in `00 Sources/`) | The candidate's background, to judge fit. |
| `02 Screening/LinkedIn Ranking.md` | Active ranking: the last four weeks, newest on top. Write here. Create it with a one-paragraph intro on the first run. |
| `02 Screening/Archive/LinkedIn Ranking - YYYY-MM.md` | Older runs per month. Read-only, except for the monthly rollover. |

## Browser preflight (before anything on LinkedIn)

LinkedIn pages need a browser where the candidate is signed in. Check this before the first LinkedIn step, and stop with a clear message instead of failing halfway or switching browsers on your own. Give the messages below in the conversation language.

1. **Which browser**: `tools.linkedin_browser` in profile.yaml (`claude-in-chrome` or `built-in-browser`). Use that one, even when another browser is the preferred browser.
2. **Is it installed and connected?** For `claude-in-chrome`, the `mcp__claude-in-chrome__*` tools must be in this session (loaded or deferred); for `built-in-browser`, the `Claude_Browser` tools. If they are missing, stop and say: *"Claude in Chrome is not installed or not connected in this session. Install the Claude in Chrome extension in Chrome and sign in with your Claude account, or set `tools.linkedin_browser: built-in-browser` in profile.yaml."* (or the equivalent for the built-in browser: open the Claude desktop app).
3. **Is it running?** Call the browser's tab-context tool. No answer, a connection error, or no connected browser means Chrome (or the desktop app) is closed or the extension is off. Stop and say: *"Chrome isn't open, or the Claude in Chrome extension isn't active. Open Chrome with the extension switched on and try again."*
4. **Signed in to LinkedIn?** Open `https://www.linkedin.com/feed/` in a new tab. A redirect to a login, "authwall" or "checkpoint" page, or a page asking to sign in or join, means the candidate is not signed in. Stop and say: *"You're not signed in to LinkedIn in that browser. Sign in there and try again."* Never type credentials, and never solve a verification challenge for the candidate.
5. Only when all four pass, continue. In an unattended run (scheduled task), put the same message in the notification and end the run.

With Claude in Chrome, on "Cannot access a chrome-extension:// URL of different extension", retry a few times, if needed in a new tab; if it persists, ask the candidate to bring the Chrome window to the front.

## Steps

1. **Run the browser preflight** above. Then **read the alert list.** Open https://www.linkedin.com/jobs/jam/ ("Manage job alerts"), click "Show N more" until all alerts are visible, and read each alert's link (keywords + geoId), location and any "Filters:" line (a page script on `[role=dialog] a[href*="keywords"]` works). Never hard-code the alert list. Map each alert to a route from `search_criteria.md`. An alert that fits no route is a new source: score it anyway and mention it in the notification. An alert the criteria exclude: skip it and mention it, so the candidate can delete it.
2. **Set the time window.** Find the exact time of the previous run (the newest date section, its 🕐 line, or the file's modification time) and use the real difference until now plus a few hours' margin as `f_TPR=r<seconds>`. Never default to 24 hours or less. If the previous run can't be determined, use 48 hours or more. Document the window.
   - **New source, first run**: a source that appears in no earlier section of the ranking or archive gets a one-week window, flagged with 🆕. With more than 30 results, focus on the most recognisable titles and companies, and say so.
   - **Work-type filter**: LinkedIn's new search page ignores work-type filters. Open an alert with "Filters: Remote" or "Remote · Hybrid" via the classic page: `https://www.linkedin.com/jobs/search/?keywords=<keywords without the Remote suffix>&geoId=<geoId>&f_WT=<2 or 2%2C3>&f_TPR=r<seconds>`, and check that the filter is active. Alerts without a filter can be opened via their own link with the window replaced.
3. **Collect and deduplicate.** Check each card's "posted X ago"; the semantic feeds are not sorted by date. Deduplicate on function + company + location, regardless of source, against the active ranking and the archive files (search them for the company name, don't read them in full), and within the run. Word-for-word cross-postings by anonymous reposters (e.g. Jobgether) count as the same role. Skip generic contractor marketplaces (Toptal, Ethos).
4. **Apply exclusions first**, as `search_criteria.md` defines them. Excluded roles are not scored; they go in the excluded list with a short reason.
5. **Score the rest.** Open each remaining vacancy and read the full "About the job". Confirm by screenshot which vacancy actually loaded, because page-text extraction sometimes returns stale content. Give a verdict as `search_criteria.md` names them, with a short, substantive reason in the conversation language, in the style of the existing rows, and mention the route when it explains the verdict. Fill in the company type.
6. **Write the section** (layout below), then send a short notification: number of new vacancies, best verdicts, how many were excluded, and anything notable (cross-posting, first run of a source, an alert that should be removed, a method problem). With no new vacancies, say so and add no empty table.

## Never skip work for time

"Time budget" is never a reason to skip anything. When a source has a high volume and not every result is opened, state concrete numbers (total results and pages, how many were viewed) and the real reason. Any title named as potentially relevant during a partial scan is opened and scored in the same run.

## Layout

Headings and column names in the conversation language; the English names below are the reference.

- **Date section**: `## YYYY-MM-DD`, newest on top, directly under the intro and its `---`. One heading for the run's findings. Close the section with `---`.
- **Run report**: 3 to 5 lines that start with an emoji, the emoji being the bullet (no `-` or `*` before it), each on its own line with an empty line between them, one or two sentences each. 🕐 window and why · ✅ sources fully covered, with volume ("page 1 of 3, 25 of 90") · 🆕 first run of a new source · ⏭️ skipped or not reached, with the reason · ⚠️ technical or method problem. The report never repeats the table; it only covers what is not in it.
- **Table**: `| Role · Company | Location | Company type | Verdict | Reason |`
  - "Role · Company" links to the vacancy: `[Job title · Company](https://www.linkedin.com/jobs/view/<jobId>/)`.
  - Location with work type: "Paris (Hybrid)".
  - Company type, max ~6 words, as "[company type] - [sector/domain]", e.g. "Fintech - Payments", "Software - FP&A". Both the kind of company and the sector it serves.
  - Verdict underlined (`<u>Strong</u>`). Sort from the best verdict to the weakest.
- **Excluded list** under the table, as plain `- ` bullets grouped per source.
- Outside the table: company names in **bold**, job titles in *italics*, nothing else bold or italic. No other headings, no summary paragraphs above the table.
- If the existing file already uses its own heading or column names, keep them for continuity.

## Monthly rollover

The active file keeps about four weeks. When its oldest section is more than four weeks old, move that month's sections to `Archive/LinkedIn Ranking - YYYY-MM.md` (create it with a one-line header if needed, newest on top) and remove them from the active file in the same step. Edit the files in place with a script; never rewrite them from tool output, which can be truncated.
