---
name: vacancy-analysis
description: Gives the candidate a candid fit assessment for a job posting, advice on how to apply and interview prep, grounded in their career narrative and search criteria. Use when the candidate pastes a posting or a link, asks "is this a fit", "should I apply", or wants to prepare an application.
---

# Vacancy analysis

Read `00 Sources/profile.yaml`, the narrative (`files.narrative`), `standing_rules.md`, `search_criteria.md` and the scoring model before answering. Re-read them every time; they change. Answer in `languages.conversation`. Pitch tone and judgment at `candidate.target_level`.

The assessment is only useful if it is candid. Be honest about weak matches rather than optimistic, and flag anything ethically or factually questionable in a posting or in a request (such as exaggerating a match) instead of complying silently.

## Output

1. **Read the posting in full**: role, seniority, must-haves, nice-to-haves, industry, company stage and size, location and on-site policy. With only a link: try the web fetch tool first. A LinkedIn link usually needs the signed-in browser: run the browser preflight below, and if any check fails, give its message and ask the candidate to paste the posting text instead. If the posting falls under an exclusion in `search_criteria.md`, say so first.
2. **Fit assessment**: a clear verdict (strong / moderate / weak match), the top 3–5 strengths for this role, each tied to a named proof point from the narrative, and the top 2–3 gaps or risks a recruiter would flag.
3. **Scores**: the six component scores from the scoring model, one line of reasoning each, then Fit, Winnability, Priority and band, and where the role lands against the current pipeline.
4. **How to apply**: which angle to lead with (and which CV variant that suggests), direct application or warm route (look for contacts in the pipeline), and what to address proactively (career gap, seniority mismatch, sector pivot, location). Let the band drive this: band C means find a warm route first, band D means don't spend a CV cycle on it.
5. **Interview prep**: likely topics and competencies, questions the candidate must be ready for given the gaps, and what to read about the company and the role.
6. **Next step**: offer a research brief (company-brief skill) and a tailored CV (cv-tailoring skill).

Then add the role to the pipeline with the career-pipeline-tracker skill, `stage: explore` and the six scores, in the same turn.

Before starting, process answered questions ("Questions inbox" in the career-pipeline-tracker skill). When the analysis exposes a gap the narrative can't answer (a must-have without a proof point, a number that would change the verdict), add it as a question on the setup page (format in the career-setup skill), at most three per vacancy, and say so in one line.

## Browser preflight (before anything on LinkedIn)

LinkedIn pages need a browser where the candidate is signed in. Check this before the first LinkedIn step, and stop with a clear message instead of failing halfway or switching browsers on your own. Give the messages below in the conversation language.

1. **Which browser**: `tools.linkedin_browser` in profile.yaml (`claude-in-chrome` or `built-in-browser`). Use that one, even when another browser is the preferred browser.
2. **Is it installed and connected?** For `claude-in-chrome`, the `mcp__claude-in-chrome__*` tools must be in this session (loaded or deferred); for `built-in-browser`, the `Claude_Browser` tools. If they are missing, stop and say: *"Claude in Chrome is not installed or not connected in this session. Install the Claude in Chrome extension in Chrome and sign in with your Claude account, or set `tools.linkedin_browser: built-in-browser` in profile.yaml."* (or the equivalent for the built-in browser: open the Claude desktop app).
3. **Is it running?** Call the browser's tab-context tool. No answer, a connection error, or no connected browser means Chrome (or the desktop app) is closed or the extension is off. Stop and say: *"Chrome isn't open, or the Claude in Chrome extension isn't active. Open Chrome with the extension switched on and try again."*
4. **Signed in to LinkedIn?** Open `https://www.linkedin.com/feed/` in a new tab. A redirect to a login, "authwall" or "checkpoint" page, or a page asking to sign in or join, means the candidate is not signed in. Stop and say: *"You're not signed in to LinkedIn in that browser. Sign in there and try again."* Never type credentials, and never solve a verification challenge for the candidate.
5. Only when all four pass, continue. In an unattended run (scheduled task), put the same message in the notification and end the run.

## Rules

- Never invent experience, numbers or dates. If the assessment needs a fact that is not in the narrative, ask.
- Use the posting's terms only for experience the candidate actually has.
- When the candidate confirms a new fact during the conversation, add it to the narrative, dated.
