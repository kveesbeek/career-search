# Config template

```yaml
# <Company> · <Role> · <location> · reports to <X>
# Posting: <url>
base: cv_base.md            # or the base for another language (profile.yaml: languages.cv_bases)
label: <Company> (<Role>)   # output: "<Name> - CV - <label>.pdf"
lang: en                    # matches the base
layout: compact             # compact (2 p.) | comfortable (3 p., only on request)
variant: B
variant_why: "..."
ai_option: 2                # 1 = one line under Education · 2 = featured block
insider_reader: false       # false = insider terms (profile.yaml) may not appear in headline/profile
highlight_tags: 4           # first N tags in accent colour
tags: [TAG-07, TAG-12, "Literal New Tag", TAG-04]   # max 8; IDs or literal text, in order
tags_why: "..."
omit:
  R1-02: "reason"
override:
  R1-01:
    text: "full new text, **bold** allowed"
    why: "reason"
insert_after:
  - {after: R1-03, id: X-01, text: "...", why: "..."}
order: []                   # preferred ID order within a role, and within the featured block
headline: ""                # optional custom headline (+ headline_why)
profile: ""                 # optional custom profile (+ profile_why)
keywords: [roadmap, discovery, ...]
```

- Every omit, override and insert needs a reason; the Check flags missing ones with ⚠️.
- An omit or override on an ID that is not in the base stops the renderer.
- `layout_overrides: {side, top, bottom, scale}` only when used, with the reason beside it.
- `banking_reader` is accepted as an older name for `insider_reader`.
- `output_dir:` puts the outputs in another folder, relative to the config.
