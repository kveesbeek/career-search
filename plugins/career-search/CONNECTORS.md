# Connectors and tools

The skills don't hard-code tools. `00 Sources/profile.yaml` says which ones the candidate uses.

| Need | Used by | Options | Set in profile.yaml |
|---|---|---|---|
| Access to the career folder | all skills | The Claude desktop app with the folder connected (preferred; can overwrite files) · Google Drive connector (cannot overwrite existing files) | `folder.device_path`, `folder.drive_path` |
| A browser signed in to LinkedIn | linkedin-job-screening | Claude in Chrome (your own Chrome) · the built-in browser of the desktop app | `tools.linkedin_browser` |
| Pipeline page | career-pipeline-tracker | A Claude artifact with a database (created by career-setup) | `tools.pipeline_artifact` |
| Links from the pipeline to briefs | career-pipeline-tracker | Google Drive connector, to look up file links · none | `tools.file_links` |
| Scheduled screening | linkedin-job-screening | Claude scheduled tasks | — |
| Writing style | cv-tailoring, vacancy-analysis, company-brief | The candidate's own writing-style skill (e.g. from setup-writing-style) | `writing_style_skill` |
