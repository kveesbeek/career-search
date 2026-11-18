# Folder layout

Every skill in this plugin works on one folder, named in `profile.yaml` (`folder.name`). The layout is fixed so skills and the renderer can find things without asking.

| Folder | Contents | Rule |
|---|---|---|
| `00 Sources/` | `profile.yaml`, the career narrative, `cv_base.md` (+ one per CV language), `cv_config - Base.yaml` (+ per language), `standing_rules.md`, `search_criteria.md`, `scoring_model.md`. Subfolders `Generic CV/` (rendered generic CVs) and `Knowledge/` (reusable background). | The only place facts, rules and settings live. |
| `01 System/` | Optional: `fonts/` with the woff2 files named in `cv.design.font_files`; or the candidate's own `cv_template.html` for structural changes. | An own template replaces the default one, and then the `cv.design` keys no longer apply. |
| `02 Screening/` | `LinkedIn Ranking.md` (last four weeks) and `Archive/LinkedIn Ranking - YYYY-MM.md`. | Deduplication checks both. |
| `03 Companies/<Company>/` | Research brief, call prep, CV config, rendered CV, Check, cover letter drafts for an active process. | One folder per company. |
| `Sent/` | Exact copies of what was sent, as `YYYY-MM-DD Company - CV.pdf` etc., plus `Sent - Index.md`. | Frozen: never edit or regenerate. |
| `99 Archive/` | `Companies/` (closed processes), `Old versions/`, `Scratch/`. | A company folder moves here when its process closes. |

## Reaching the folder

- **Device bridge** (Claude desktop app with the folder connected): use the device tools on `folder.device_path`. Prefer this; it can overwrite files.
- **Drive connector**: the folder at `folder.drive_path`. The connector cannot overwrite existing files: deliver changes to source files as text for the candidate to apply, and never create duplicates.
- **Neither**: ask the candidate to connect the folder or attach the files.

## Editing rules

- Re-read a source file every time before using it; the candidate edits them between turns.
- When writing back a file that existed before this turn, guard against overwriting a newer version (on the device bridge: re-stage and pass `expectedMtimeMs`; never force).
- Never delete files. Move superseded ones to `99 Archive/`.
