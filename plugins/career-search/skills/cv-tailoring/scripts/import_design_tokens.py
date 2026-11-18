#!/usr/bin/env python3
"""Turn a design system's tokens.json into the `cv.design` block of profile.yaml.

Usage:
    python3 import_design_tokens.py <tokens.json> [--fonts-dir <dir>] [--theme light]

Reads two layouts:
- a Claude Design System artifact (`color.tokens: [{name, value: {light, dark}}]`,
  `type.families`, `type.groups`, `radius.tokens`);
- a flat or nested token file (W3C/DTCG style: `{"color": {"ink": {"$value": "#123"}}}`).

Prints a YAML block to paste under `cv:` in profile.yaml, plus notes on what it
could not map. It only proposes values: the CV keeps its ATS-safe structure
(one column, real text, embedded fonts), and the candidate reviews the result.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROLES = {
    "ink": ["ink", "text", "foreground", "fg", "text-primary", "heading"],
    "body": ["ink-body", "body", "text-body", "text-default", "ink"],
    "muted": ["ink-muted", "muted", "text-muted", "text-secondary", "secondary-text", "subtle"],
    "rule": ["rule", "border", "divider", "line", "outline"],
    "accent": ["accent", "primary", "brand", "brand-primary"],
    "accent_wash": ["accent-wash", "accent-soft", "primary-wash", "primary-soft", "brand-soft", "accent-subtle"],
    "accent_wash_rule": ["accent-wash-rule", "accent-border", "primary-border"],
}


def flatten(node, prefix=""):
    """Nested token files → {"color-ink": "#123", ...}."""
    out = {}
    if isinstance(node, dict):
        if "$value" in node or ("value" in node and not isinstance(node["value"], dict) and "name" not in node):
            return {prefix: node.get("$value", node.get("value"))}
        for k, v in node.items():
            if k.startswith("$"):
                continue
            out.update(flatten(v, f"{prefix}-{k}" if prefix else k))
    return out


def colours(data, theme):
    found = {}
    tokens = (data.get("color") or {}).get("tokens")
    if isinstance(tokens, list):
        for t in tokens:
            v = t.get("value")
            if isinstance(v, dict):
                v = v.get(theme) or next(iter(v.values()))
            found[t["name"].lower()] = v
    else:
        for k, v in flatten(data.get("color") or data.get("colors") or {}).items():
            found[k.lower()] = v
    # resolve {alias} references
    for k, v in list(found.items()):
        if isinstance(v, str) and v.startswith("{") and v.endswith("}"):
            found[k] = found.get(v[1:-1].lower(), v)
    return found


def pick(found, names):
    for n in names:
        for key in (n, f"color-{n}", f"colors-{n}"):
            if key in found and isinstance(found[key], str) and found[key].startswith(("#", "rgb")):
                return found[key]
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    theme = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "light"
    found = colours(data, theme)
    design, notes = {}, []
    for role, names in ROLES.items():
        v = pick(found, names)
        if v:
            design[role] = v
        else:
            notes.append(f"no token found for {role}; the plugin default stays")

    typ = data.get("type") or data.get("typography") or {}
    fam = (typ.get("families") or {}).get("sans") or (typ.get("fontFamily") or {}).get("sans")
    if isinstance(fam, dict):
        fam = fam.get("$value") or fam.get("value")
    if fam:
        first = fam.split(",")[0].strip().strip("'\"")
        design["font_family"] = first
        design["font_fallback"] = ",".join(fam.split(",")[1:]).strip() or "sans-serif"

    styles = [s for g in typ.get("groups") or [] for s in g.get("styles") or []]
    by_name = {s.get("name"): s for s in styles}
    # Name in the header is ~32px: take the heaviest heading style between 24 and 36px.
    heads = [s for s in styles if 24 <= float(str(s.get("fontSize", "0")).rstrip("px") or 0) <= 36]
    if heads:
        h = max(heads, key=lambda s: int(s.get("fontWeight", 400)))
        design["name_weight"] = int(h.get("fontWeight", 700))
        if h.get("letterSpacing"):
            design["name_tracking"] = h["letterSpacing"]
    eyebrow = by_name.get("eyebrow") or by_name.get("overline") or by_name.get("label")
    if eyebrow:
        usage = (eyebrow.get("usage") or "").lower()
        if "never uppercase" in usage or "sentence case" in usage:
            design["label_case"] = "none"
            design["label_size"] = "1"   # sentence case reads smaller than capitals
            design["label_tracking"] = "0"
            design["sub_tracking"] = "0"
        if "in accent" in usage:
            design["label_color"] = "var(--accent)"
        if re.search(r"\brule\b", usage):
            design["label_rule"] = True
            m = re.search(r"(\d+)\s*[×x]\s*2px", usage)
            if m:
                design["label_rule_width"] = f"{round(int(m.group(1)) * 0.75)}px"
        if eyebrow.get("fontWeight"):
            design["label_weight"] = int(eyebrow["fontWeight"])

    radii = {t["name"]: t["value"] for t in (data.get("radius") or {}).get("tokens") or []}
    if "radius-pill" in radii:
        design["tag_radius"] = radii["radius-pill"]

    if "--fonts-dir" in sys.argv:
        d = Path(sys.argv[sys.argv.index("--fonts-dir") + 1])
        files = []
        for f in sorted(d.glob("*.woff2")):
            m = re.search(r"(\d{3})", f.name)
            if m:
                files.append({"file": f"fonts/{f.name}", "weight": int(m.group(1))})
        design["font_files"] = files
        notes.append(f"copy the {len(files)} font files into '01 System/fonts/'")
    elif "font_family" in design:
        notes.append(f"add font_files for '{design['font_family']}' (woff2 per weight in '01 System/fonts/'), "
                     "or the PDF falls back to the next font in the stack")

    print(yaml.safe_dump({"design": design}, sort_keys=False, allow_unicode=True))
    for n in notes:
        print("# note:", n)


if __name__ == "__main__":
    main()
