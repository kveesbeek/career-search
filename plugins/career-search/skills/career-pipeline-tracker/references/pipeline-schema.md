# Pipeline schema

The pipeline page is a published artifact that reads everything from its own database and holds no data in its HTML. Three collections.

## `roles`

One document per company/role. Doc id: a lowercase-hyphenated company slug (`acme`, `wrike-klaxoon`).

| Field | Type | Meaning |
|---|---|---|
| `company` | string | |
| `role` | string | Role title plus location / hybrid note. |
| `stage` | `interview` \| `applied` \| `explore` \| `declined` \| `rejected` \| `noreply` \| `ruledout` | Drives the board column. `explore` covers both "researching" and "on the radar, not applied". `rejected` only for an explicit no; `noreply` for silence or a posting that closed without an answer; `declined` when the candidate got an offer and said no; `ruledout` when the candidate passed before any offer. |
| `senScore`, `domScore`, `locScore`, `evScore`, `lvlScore`, `rteScore` | number 0–5 | The six components from the scoring model. Never store Fit, Winnability, Priority or band. |
| `pillLabel` | string | Short status label on the card ("waiting for reply", "rejected"). |
| `detail` | string | 1–3 sentences: why this stage, what the read is, flags. |
| `nextStep` | string | Optional; empty string if none. |
| `nextStepDate` | ISO date or "" | The day the candidate must act or follow up; fills the "next actions" list. Always set it together with `nextStep`; empty it when the card closes. |
| `nextStepWhen` | string | Optional short timing ("Wed 7 Oct 14:30", "follow up if silent"). |
| `dossier` | string | Durable context per role: contacts, decisions, salary ask, CV choices, open questions. Always written as the full new text, keeping what was there. |
| `dateStamp` | string | Short footer line ("applied 11 Sep · rejected 15 Sep"). |
| `dateOnRadar`, `cvSubmitted`, `rejectionDate` | ISO date or "" | |
| `motivationLetter` | `yes` \| `no` \| `unknown` | |
| `applicationType` | `easy_apply` \| `extended` \| `unknown` | |
| `interviewDates` | string | An exact date or a window. |
| `vacancyUrl`, `applyUrl` | string | Optional. |
| `order` | number | Sort position within its column; new cards get max + 1 in their stage. |
| `briefUrl` | string | Optional link to the company's research brief. Only when the file exists and its link was looked up (e.g. Drive search); never guessed. |

Each role has a subcollection `roles/<id>/log`: one document per event (`at`: ISO date-time, `text`: one or two sentences), newest first. Add a log entry for every piece of news.

## `contacts`

One document per network or recruiter contact. Doc id: a lowercase-hyphenated name slug.

| Field | Type | Meaning |
|---|---|---|
| `name`, `org`, `status` | string | |
| `type` | `executive_search` \| `consultancy` \| `other` | Headhunters and search agencies · people at consultancies relevant to a consultancy route · everyone else (hiring managers, founders, in-house recruiters, friends). |
| `lastAction` | string | Short label ("5 Oct · reply sent"). |
| `lastActionDate` | ISO date or "" | The table sorts on this. Update together with `lastAction`, always. |
| `closed` | boolean | Optional; closed contacts move to a collapsed table. |
| `order` | number | Tie-breaker only. |

## `meta`

- `meta/board`: `title`, `subtitle`, `lastCompiled` (ISO date, bump on every change), `footerTopFunnel`, `footerNote`.
- `meta/scoring`: `text`, the full text of the candidate's scoring model. The page's built-in "new card" assistant scores from it, so write it at setup and again whenever the model changes.

## Setup page collections

- `meta/setup`: `pluginVersion`; `steps` (array of `{id, phase: quickstart|deepen|optional, label, status: todo|active|done, note, prompt}`; `prompt` is the sentence the candidate copies into a new task); `requirements` (array of `{label, status: ok|missing|unknown, fix, checkedAt}`); `links` (array of `{label, url, note}`; only real http(s) URLs become links).
- `questions`: one document per question: `question`, `why`, `source`, `status: open|answered|processed`, `answer`, `askedAt`, `answeredAt`, `processedAt`, `order`. The page writes only `answer`, `status: answered` and `answeredAt`.
- `updates`: one document per change: `at` (ISO date), `text`, `kind: source|setup|plugin`. The page shows the latest eight.

## Creating the page (setup only)

The page ships with this skill as `assets/pipeline-board.html`: a kanban board with status cells, Fit / Winnability / Priority computed in the page, a next-actions list, per-card drawer with dossier, log and a chat that updates the card, a "new card" assistant that scores from `meta/scoring`, analytics, a contacts table and a demo mode with invented data. It holds no data and is styled in the plugin author's house style (Hanken Grotesk, blue accent, bright status colours).

1. Copy the file and replace the placeholders: `{{FULL_NAME}}`, `{{FIRST_NAME}}`, `{{INITIAL}}` (favicon letter) and `{{CANDIDATE_CONTEXT}}` (one line in the page's language: current or last role, where they live, which roles they look for). The page's labels and assistant prompts are in Dutch; for another conversation language, translate the visible labels and the prompt texts, and nothing else.
2. Publish it as a new artifact titled with `tools.pipeline_title`, and declare the capabilities `db` and `sample` (the database and the in-page Claude calls).
3. Write `meta/board` (title, subtitle, lastCompiled) and `meta/scoring` (the scoring model text).
4. Put the artifact URL in `tools.pipeline_artifact` in profile.yaml.

To restyle the page in the candidate's own house style, change only the CSS custom properties at the top (`--paper`, `--surface`, `--ink`, `--accent`, the status colours) and the font link; the rest of the page reads from them.
