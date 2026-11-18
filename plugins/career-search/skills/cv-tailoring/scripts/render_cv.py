#!/usr/bin/env python3
"""Render a candidate's CV from cv_base.md + a per-vacancy config (YAML).

Usage:
    python3 render_cv.py <config.yaml> [--no-pdf] [--sources <dir>]

Outputs (next to the config file, or in `output_dir` from the config):
    <Name> - CV[ - <label>].html
    <Name> - CV[ - <label>].pdf        (needs Playwright + Chromium)
    <Name> - CV[ - <label>] - Check.md (validation report + change list vs base)

The name comes from HDR-01 in the base. Personal settings (Check language,
banned words, insider-only terms) come from `profile.yaml` in the sources
folder ("00 Sources"), found by walking up from the config or given with
--sources. A `cv_template.html` / `cv_fonts.css` in the "01 System" folder
next to "00 Sources" overrides the default design shipped here.

The base file is the single source of truth for wording. The config only
selects a variant and lists changes by ID, so a review only has to cover
those changes.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

HERE = Path(__file__).resolve().parent
SOURCES_DIR = "00 Sources"
SYSTEM_DIR = "01 System"

# Check-file wording per language (profile.yaml: notes_language).
TEXT = {
    "en": {"why": "Why", "no_why": "⚠️ no reason given in the config", "changed": "changed",
           "omitted": "omitted", "new_after": "new (after {after})", "company_name": "Company name",
           "new_order": "New order", "dropped": "Dropped",
           "max_pages": "Max {n} pages ({layout})", "pages": "{n} pages",
           "no_empty_last": "No empty last page", "chars_per_page": "characters per page: {v}",
           "ats_titles": "ATS: section titles readable", "missing": "missing", "all_titles": "all titles found",
           "ats_contact": "ATS: contact '{f}'", "no_banned": "No banned words",
           "no_dashes": "No em dashes in profile/bullets", "found": "{n} found",
           "no_insider": "No {terms} in headline/profile ({reader})",
           "kw": "Posting keyword coverage", "kw_found": "{a}/{b} found", "kw_missing": "; missing: {m}",
           "featured": "Featured-block option", "variant_why": "Why this variant",
           "changes": "Changes against the base",
           "legend": "*~~struck~~ = removed · **bold** = new · everything else as in the base*",
           "none": "None: base unchanged.", "validation": "Validation"},
    "nl": {"why": "Waarom", "no_why": "⚠️ geen reden opgegeven in de config", "changed": "gewijzigd",
           "omitted": "weggelaten", "new_after": "nieuw (na {after})", "company_name": "Bedrijfsnaam",
           "new_order": "Nieuwe volgorde", "dropped": "Weggelaten",
           "max_pages": "Max {n} pagina's ({layout})", "pages": "{n} pagina's",
           "no_empty_last": "Geen lege laatste pagina", "chars_per_page": "tekens per pagina: {v}",
           "ats_titles": "ATS: sectietitels leesbaar", "missing": "ontbreekt", "all_titles": "alle titels gevonden",
           "ats_contact": "ATS: contact '{f}'", "no_banned": "Geen verboden woorden",
           "no_dashes": "Geen em dashes in profiel/bullets", "found": "{n} gevonden",
           "no_insider": "Geen {terms} in headline/profiel ({reader})",
           "kw": "Keyword-dekking vacature", "kw_found": "{a}/{b} gevonden", "kw_missing": "; ontbreekt: {m}",
           "featured": "AI-optie", "variant_why": "Waarom deze variant",
           "changes": "Wijzigingen t.o.v. de base",
           "legend": "*~~doorstreept~~ = verdwijnt · **vet** = nieuw · de rest blijft zoals in de base*",
           "none": "Geen: base ongewijzigd.", "validation": "Validatie"},
}
DEFAULT_BANNED = [r"\bHonestly\b", r"\bFrankly\b", r"That said", r"That being said", r"not just\b",
                  r"\bleverag", r"\bspearhead", r"\bcatalys", r"end-to-end", r"0-to-1", r"fast-paced",
                  r"ever-evolving", r"\bnon-negotiable\b", r"\bsynerg", r"\brobust\b", r"\bseamless"]
PROFILE = {}

# CV design. The defaults reproduce the plugin's standard look (Inter, green
# accent). profile.yaml `cv.design` overrides any key; `import_design_tokens.py`
# fills it from a design-system tokens.json. Every value stays inside what an
# ATS can read: one column, real text, embedded fonts, no text in images.
DEFAULT_DESIGN = {
    "font_family": "Inter", "font_fallback": "sans-serif", "font_files": [],
    "ink": "#0F172A", "body": "#334155", "muted": "#64748B", "rule": "#E2E8F0",
    "accent": "#2E5A4C", "accent_wash": "#EDF3F0", "accent_wash_rule": "#C6D8D0",
    "name_weight": 700, "name_tracking": "-.8px",
    "label_case": "uppercase", "label_color": "var(--ink)", "label_weight": 700,
    "label_size": ".87", "label_tracking": ".03em", "sub_tracking": ".02em",
    "label_rule": False, "label_rule_width": "14px",
    "tag_radius": "999px",
}
T = TEXT["en"]


def find_sources(start: Path) -> Path:
    """The candidate's "00 Sources" folder: --sources, or the first one found walking up."""
    if "--sources" in sys.argv:
        return Path(sys.argv[sys.argv.index("--sources") + 1]).resolve()
    for d in [start, *start.parents]:
        if d.name == SOURCES_DIR:
            return d
        if (d / SOURCES_DIR).is_dir():
            return d / SOURCES_DIR
    return start


def load_profile(sources: Path) -> dict:
    f = sources / "profile.yaml"
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


def font_css(design: dict, sources: Path) -> str:
    """@font-face rules with the font files embedded, so the PDF never falls back."""
    import base64
    rules = []
    for f in design.get("font_files") or []:
        path = Path(f["file"])
        if not path.is_absolute():
            path = sources.parent / SYSTEM_DIR / path
        data = base64.b64encode(path.read_bytes()).decode()
        rules.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;"
                     "src:url(data:font/woff2;base64,%s) format('woff2')}"
                     % (design["font_family"], f.get("weight", 400), data))
    return "".join(rules)


def design_dir(sources: Path) -> Path:
    """The candidate's own "01 System" folder if it holds a template, else the default here."""
    own = sources.parent / SYSTEM_DIR
    return own if (own / "cv_template.html").exists() else HERE

# Page layout presets. `compact` is the default: two pages, 15mm margins.
# type, the proportions of a normal printed business document, over 3 pages.
# `compact` fits the same content on 2 pages at 9.6pt, for markets and
# portals where the two-page rule is strict (France, most ATS uploads).
# side/top/bottom are the printed margins; `left` is 1.6mm smaller because the
# .page box carries 6px of left padding to keep the role timeline dot on paper.
LAYOUTS = {
    "comfortable": {"side": 20, "top": 20, "bottom": 22, "scale": 13.3, "max_pages": 3},
    "compact": {"side": 16, "top": 14, "bottom": 16, "scale": 12.6, "max_pages": 2},
}
EXPERIENCE_H2 = {"experience", "expérience", "ervaring"}
ID_LINE = re.compile(r"^- \*\*\[([A-Za-z0-9-]+)\]\*\*\s*(?:[✅⏳]\s*)?(.*)$")
HEADLINE_ROW = re.compile(r"^\|\s*\*\*([A-Z])\*\*\s*\|[^|]*\|\s*(?:[✅⏳]\s*)?(.*?)\s*\|\s*$")
TRAILING_NOTE = re.compile(r"\s*\*\([^)]*\)\*\s*$")
LEADING_NOTE = re.compile(r"^\*\([^)]*\)\*\s*")


def clean(text: str) -> str:
    text = TRAILING_NOTE.sub("", text.strip())
    text = LEADING_NOTE.sub("", text)
    return text.strip()


def md_inline(text: str) -> Markup:
    """Escape HTML, then turn **bold** into <strong>."""
    esc = html.escape(text, quote=False)
    esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
    return Markup(esc)


def plain(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


def word_diff(old: str, new: str) -> str:
    """Inline diff for the Check file: ~~removed~~ and **added**, unchanged words as is."""
    import difflib
    a, b = plain(old).split(), plain(new).split()
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    # Merge changes separated by 1-2 unchanged words, so a rephrased clause reads as one block.
    merged = []
    for op in ops:
        tag, i1, i2, j1, j2 = op
        if (merged and tag != "equal" and len(merged) >= 2 and merged[-1][0] == "equal"
                and merged[-1][2] - merged[-1][1] <= 2 and merged[-2][0] != "equal"):
            eq = merged.pop()
            prev = merged.pop()
            merged.append(("replace", prev[1], i2, prev[3], j2))
            continue
        merged.append(op)
    out = []
    for tag, i1, i2, j1, j2 in merged:
        if tag == "equal":
            out.append(" ".join(a[i1:i2]))
            continue
        if i2 > i1:
            out.append("~~" + " ".join(a[i1:i2]) + "~~")
        if j2 > j1:
            out.append("**" + " ".join(b[j1:j2]) + "**")
    return " ".join(out)


def split_why(value):
    """Config values may be plain text or {text: ..., why: ...}."""
    if isinstance(value, dict):
        return value.get("text", ""), value.get("why", "")
    return value, ""


def change_block(title: str, body: str, why: str) -> str:
    lines = [f"### {title}", "", body, ""]
    lines.append(f"*{T['why']}:* {why}" if why else f"*{T['why']}:* {T['no_why']}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- parse base
def parse_base(path: Path) -> dict:
    items, order, headlines = {}, [], {}
    companies, sections, subsections = [], {}, {}
    h2 = None
    subgroup = None
    company = role = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = HEADLINE_ROW.match(line)
        if m:
            headlines[m.group(1)] = clean(m.group(2))
            continue
        if line.startswith("## "):
            h2 = clean(line[3:])
            sections.setdefault(h2, [])
            subsections.setdefault(h2, [])
            company = role = None
            subgroup = None
            continue
        if line.startswith("### ") and h2 and h2.split(" ·")[0].lower() not in EXPERIENCE_H2:
            # sub-heading inside a plain section (e.g. Certifications / Degrees)
            subgroup = {"label": clean(line[4:]), "ids": []}
            subsections[h2].append(subgroup)
            continue
        if line.startswith("### ") and h2 and h2.split(" ·")[0].lower() in EXPERIENCE_H2:
            name, _, dates = clean(line[4:]).rpartition(" · ")
            company = {"name": name, "dates": dates, "note_id": None, "roles": []}
            companies.append(company)
            role = None
            continue
        if line.startswith("#### ") and company is not None:
            title, sep, dates = clean(line[5:]).rpartition(" · ")
            if not sep:
                title, dates = clean(line[5:]), ""
            role = {"title": title, "dates": dates, "ids": []}
            company["roles"].append(role)
            continue
        m = ID_LINE.match(line)
        if not m:
            continue
        iid, text = m.group(1), clean(m.group(2))
        items[iid] = text
        order.append(iid)
        if company is not None:
            if role is None:
                company["note_id"] = iid
            else:
                role["ids"].append(iid)
        elif h2:
            sections[h2].append(iid)
            if subgroup is not None:
                subgroup["ids"].append(iid)
    labels = {"EXP": next((h for h in sections if h.split(" ·")[0].lower() in EXPERIENCE_H2), "Experience")}
    for name, ids in sections.items():
        if ids:
            labels.setdefault(ids[0].split("-")[0], name)
    return {"items": items, "order": order, "headlines": headlines,
            "companies": companies, "sections": sections,
            "subsections": subsections, "labels": labels}


def section_ids(base, prefix):
    """Section whose first ID starts with `prefix` (TAG, EDU, AI, LNG, TEC)."""
    for name, ids in base["sections"].items():
        if ids and ids[0].split("-")[0] == prefix:
            return name, ids
    return None, []


# ------------------------------------------------------------ build context
def build(base: dict, cfg: dict):
    items = dict(base["items"])
    changes = []
    raw_omit = cfg.get("omit") or []
    omit_why = raw_omit if isinstance(raw_omit, dict) else {i: "" for i in raw_omit}
    omit = set(omit_why)
    for iid, value in (cfg.get("override") or {}).items():
        if iid not in items:
            sys.exit(f"override: unknown ID {iid}")
        text, why = split_why(value)
        changes.append(change_block(f"{iid} · {T['changed']}", word_diff(items[iid], text), why))
        items[iid] = text
    for iid, why in omit_why.items():
        if iid not in items:
            sys.exit(f"omit: unknown ID {iid}")
        changes.append(change_block(f"{iid} · {T['omitted']}", f"~~{plain(items[iid])}~~", why))
    inserts = {}
    for ins in cfg.get("insert_after") or []:
        inserts.setdefault(ins["after"], []).append(ins)
        items[ins["id"]] = ins["text"]
        changes.append(change_block(f"{ins['id']} · " + T['new_after'].format(after=ins['after']), f"**{plain(ins['text'])}**", ins.get("why", "")))

    def expand(ids):
        out = []
        for i in ids:
            out.append(i)
            out.extend(x["id"] for x in inserts.get(i, []))
        return out

    def reorder(ids):
        pref = cfg.get("order") or []
        if not pref:
            return ids
        rank = {i: n for n, i in enumerate(pref)}
        return sorted(ids, key=lambda i: (rank.get(i, 10_000), ids.index(i)))

    variant = cfg.get("variant", "A")
    headline = cfg.get("headline") or base["headlines"][variant]
    profile_id = f"PRO-{variant}"
    # `profile:` and `headline:` may be free text or the ID of a base line
    # (e.g. PRO-B-SU), so alternative approved wordings live in the base
    # instead of being copied into every config.
    cfg_profile = cfg.get("profile")
    if cfg_profile and cfg_profile in items:
        cfg_profile = items[cfg_profile]
    if headline and headline in items:
        headline = items[headline]
    profile = cfg_profile or items[profile_id]
    if cfg.get("headline"):
        changes.insert(0, change_block(f"Headline · {T['changed']}", word_diff(base["headlines"][variant], headline), cfg.get("headline_why", "")))
    if cfg.get("profile"):
        changes.insert(0, change_block(f"{profile_id} · {T['changed']}", word_diff(items[profile_id], cfg_profile), cfg.get("profile_why", "")))

    companies = []
    for c in base["companies"]:
        roles = []
        for r in c["roles"]:
            ids = [i for i in reorder(expand(r["ids"])) if i not in omit]
            ctx = next((i for i in ids if i.endswith("-00b")), None)
            stack = next((i for i in ids if items[i].startswith("Stack ·")), None)
            bullets = [md_inline(items[i]) for i in ids if i not in (ctx, stack)]
            if not bullets and not ctx:
                continue
            roles.append({"title": r["title"], "dates": r["dates"],
                          "context": md_inline(items[ctx]) if ctx else None,
                          "stack": md_inline(items[stack]) if stack else None,
                          "bullets": bullets})
        if roles:
            note = c["note_id"]
            # `company_names:` in the config renames a company header for one
            # vacancy, e.g. dropping a parent group from the title, without
            # touching the base. Key = the name as the base spells it.
            cname = cfg.get("company_names", {}).get(c["name"], c["name"])
            if cname != c["name"]:
                changes.append(change_block(f"{T['company_name']} · {T['changed']}",
                                            word_diff(c["name"], cname),
                                            cfg.get("company_names_why", "")))
            companies.append({"name": cname, "dates": c["dates"], "roles": roles,
                              "note": md_inline(items[note]) if note and note not in omit else None})

    _, tag_ids = section_ids(base, "TAG")
    if cfg.get("tags"):
        shown = []
        for t in cfg["tags"]:
            shown.append(plain(items[t]) if t in items else f"**{t}**")
        dropped = [f"~~{plain(items[t])}~~" for t in tag_ids if t not in cfg["tags"]]
        body = f"{T['new_order']}: " + " · ".join(shown)
        if dropped:
            body += f"\n\n{T['dropped']}: " + " · ".join(dropped)
        changes.append(change_block(f"Tags · {T['changed']}", body, cfg.get("tags_why", "")))
    tags = [md_inline(items.get(t, t)) for t in (cfg.get("tags") or tag_ids) if t not in omit]

    edu_section, edu_ids = section_ids(base, "EDU")
    education, edu_note = [], None

    def edu_entry(iid):
        parts = items[iid].split(" · ")
        if len(parts) >= 3:
            # Degree · School · Year [· Distinction]: the year goes right, the rest left.
            return {"degree": parts[0], "school": parts[1], "year": parts[2],
                    "extra": " · ".join(parts[3:])}
        return None

    for i in edu_ids:
        if i in omit:
            continue
        if edu_entry(i) is None:
            edu_note = md_inline(items[i])

    edu_groups = []
    for g in base.get("subsections", {}).get(edu_section, []):
        entries = [e for i in g["ids"] if i not in omit for e in [edu_entry(i)] if e]
        if entries:
            edu_groups.append({"label": g["label"], "entries": entries})
    if not edu_groups:
        entries = [e for i in edu_ids if i not in omit for e in [edu_entry(i)] if e]
        if entries:
            edu_groups.append({"label": None, "entries": entries})
    education = [e for g in edu_groups for e in g["entries"]]

    ai_name, ai_ids = section_ids(base, "AI")
    ai_items = [md_inline(items[i]) for i in reorder(expand(ai_ids)) if i not in omit]

    _, lng_ids = section_ids(base, "LNG")
    _, tec_ids = section_ids(base, "TEC")
    tech = [t for i in tec_ids for t in items[i].split(" · ")]
    tech = cfg.get("tech") or tech

    layout = cfg.get("layout", "compact")
    if layout not in LAYOUTS:
        sys.exit(f"layout: unknown value {layout!r} (use one of {', '.join(LAYOUTS)})")
    page = dict(LAYOUTS[layout])
    # A config may nudge one key of the preset, e.g. {side: 15, scale: 12.4} for a
    # vacancy that carries extra content and would otherwise run onto a third page.
    for key, value in (cfg.get("layout_overrides") or {}).items():
        if key not in page:
            sys.exit(f"layout_overrides: unknown key {key!r} (use one of {', '.join(page)})")
        page[key] = value
    page["left"] = round(page["side"] - 1.6, 1)

    ctx = {
        "layout": layout, "page": page,
        "doc_title": cfg.get("doc_title") or headline.split(" · ")[0],
        "name": items["HDR-01"], "email": items["HDR-02"],
        "phone_loc": items["HDR-03"], "linkedin": items["HDR-05"],
        "headline": headline, "profile": md_inline(profile),
        "tags": tags, "highlight_tags": cfg.get("highlight_tags", 4),
        "companies": companies,
        "ai_option": cfg.get("ai_option", 2), "ai_title": ai_name, "ai_items": ai_items,
        "education": education, "edu_groups": edu_groups, "edu_note": edu_note,
        "languages": [dict(zip(("name", "level"), (items[i].split(" — ") + [""])[:2]))
                      for i in lng_ids if i not in omit],
        "tech": tech,
        "lang": cfg.get("lang", "en"),
        "labels": base["labels"],
    }
    return ctx, changes


# ------------------------------------------------------------------ outputs
def render_pdf(html_path: Path, pdf_path: Path, name: str):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri())
        page.wait_for_load_state("networkidle")
        footer = (
            '<div style="width:100%;font-family:Helvetica,Arial,sans-serif;font-size:7pt;'
            'color:#94A3B8;padding:0 15mm;text-align:right;">'
            + html.escape(name) + ' · <span class="pageNumber"></span>/<span class="totalPages"></span>'
            "</div>"
        )
        page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True,
                 display_header_footer=True, header_template="<span></span>",
                 footer_template=footer)
        browser.close()




def check(pdf_path: Path, cfg: dict, ctx: dict) -> list:
    out = []
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout).group(1))
    max_pages = LAYOUTS[ctx["layout"]]["max_pages"]
    out.append((T["max_pages"].format(n=max_pages, layout=ctx['layout']), pages <= max_pages, T["pages"].format(n=pages)))
    per_page = []
    for n in range(1, pages + 1):
        t = subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), str(pdf_path), "-"],
                           capture_output=True, text=True).stdout
        per_page.append(len(t.strip()))
    out.append((T["no_empty_last"], per_page[-1] > 200, T["chars_per_page"].format(v=per_page)))
    text = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True).stdout
    lab = ctx["labels"]
    heads = [lab[k] for k in ("TAG", "EXP", "EDU", "LNG")]
    text = text.replace("\u2019", "'")
    missing = [h for h in heads if h.upper() not in text.upper()]
    out.append((T["ats_titles"], not missing, f"{T['missing']}: " + ", ".join(missing) if missing else T["all_titles"]))
    contact = [ctx["email"], ctx["phone_loc"].split(" · ")[0], ctx["linkedin"]]
    for field in (c for c in contact if c):
        out.append((T["ats_contact"].format(f=field), field in text, ""))
    banned = (PROFILE.get("cv") or {}).get("banned_patterns") or DEFAULT_BANNED
    hits = [p for p in banned if re.search(p, text, re.I)]
    out.append((T["no_banned"], not hits, ", ".join(hits)))
    bullet_text = " ".join(str(b) for c in ctx["companies"] for r in c["roles"] for b in r["bullets"])
    bullet_text += " " + str(ctx["profile"])
    dashes = bullet_text.count("—")
    out.append((T["no_dashes"], dashes == 0, T["found"].format(n=dashes)))
    insider_reader = cfg.get("insider_reader", cfg.get("banking_reader", True))
    insider = (PROFILE.get("cv") or {}).get("insider_terms") or {}
    if not insider_reader and insider.get("terms"):
        intro = str(ctx["headline"]) + str(ctx["profile"])
        found = [t for t in insider["terms"] if t in intro]
        label = T["no_insider"].format(terms=insider.get("check_label", "/".join(insider["terms"])),
                                       reader=insider.get("reader_label", "outside reader"))
        out.append((label, not found, ", ".join(found)))
    kws = cfg.get("keywords") or []
    if kws:
        low = text.lower()
        miss = [k for k in kws if k.lower() not in low]
        out.append((T["kw"], not miss,
                    T["kw_found"].format(a=len(kws) - len(miss), b=len(kws)) + (T["kw_missing"].format(m=", ".join(miss)) if miss else "")))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cfg_path = Path(sys.argv[1]).resolve()
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    root = cfg_path.parent
    sources = find_sources(root)
    global PROFILE, T
    PROFILE = load_profile(sources)
    T = TEXT.get((PROFILE.get("languages") or {}).get("notes_language", "en"), TEXT["en"])
    base_name = cfg.get("base", "cv_base.md")
    base_path = (root / base_name).resolve()
    if not base_path.exists():
        # Configs live in "03 Companies/<Company>/"; the bases live in "00 Sources/".
        base_path = (sources / Path(base_name).name).resolve()
    out_dir = (root / cfg.get("output_dir", ".")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    base = parse_base(base_path)
    ctx, changes = build(base, cfg)
    d = dict(DEFAULT_DESIGN, **((PROFILE.get("cv") or {}).get("design") or {}))
    d["font_stack"] = Markup(f"'{d['font_family']}',{d['font_fallback']}")
    ctx["d"] = d
    design = design_dir(sources)
    if d["font_files"]:
        ctx["fonts_css"] = Markup(font_css(d, sources))
    else:
        fonts = design / "cv_fonts.css" if (design / "cv_fonts.css").exists() else HERE / "cv_fonts.css"
        ctx["fonts_css"] = Markup(fonts.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(str(design)), autoescape=True)
    html_out = env.get_template("cv_template.html").render(**ctx)

    label = cfg.get("label")
    name = ctx["name"]
    stem = f"{name} - CV" + (f" - {label}" if label else "")
    html_path = out_dir / f"{stem}.html"
    html_path.write_text(html_out, encoding="utf-8")
    print("HTML:", html_path)

    variant = cfg.get("variant", "A")
    report = [f"# Check — {stem}", "",
              f"**Variant {variant}** · headline: {ctx['headline']}  ",
              f"**{T['featured']} {ctx['ai_option']}** · base: `{base_path.name}`", ""]
    if cfg.get("variant_why"):
        report += [f"*{T['variant_why']}:* {cfg['variant_why']}", ""]
    report += [f"## {T['changes']}", "", T["legend"], ""]
    report += changes or [T["none"]]
    if "--no-pdf" not in sys.argv:
        pdf_path = out_dir / f"{stem}.pdf"
        render_pdf(html_path, pdf_path, name)
        print("PDF:", pdf_path)
        report += ["", f"## {T['validation']}", "", "| Check | OK | Detail |", "|---|---|---|"]
        for name, ok, detail in check(pdf_path, cfg, ctx):
            report.append(f"| {name} | {'✅' if ok else '❌'} | {detail} |")
    (out_dir / f"{stem} - Check.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
