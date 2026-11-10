#!/usr/bin/env python3
from __future__ import annotations

import re
import sys

from common import (
    HEX_COLOR,
    ROOT,
    contrast_ratio,
    iter_hex_colors,
    load_palettes,
)

README = ROOT / "README.md"

EXPECTED_LIGHT_COLORS = {
    "background": "#f9f5d7",
    "surface": "#fbf1c7",
    "surfaceHover": "#f2e5bc",
    "selection": "#ebdbb2",
    "foreground": "#3c3836",
    "foregroundSecondary": "#504945",
    "foregroundInactive": "#665c54",
    "foregroundBright": "#282828",
    "accent": "#8a5200",
    "danger": "#9d0006",
    "success": "#6b6700",
    "info": "#076678",
    "magenta": "#8f3f71",
    "cyan": "#356b4d",
    "ansiBrightBlack": "#665c54",
}

EXPECTED_LIGHT_ROLES = {
    "canvas": "{colors.background}",
    "textPrimary": "{colors.foreground}",
    "textSecondary": "{colors.foregroundSecondary}",
    "textInactive": "{colors.foregroundInactive}",
    "focus": "{colors.accent}",
    "cursor": "{colors.accent}",
    "cursorText": "{colors.background}",
    "selection": "{colors.selection}",
    "selectionText": "{colors.foreground}",
    "error": "{colors.danger}",
    "warning": "{colors.accent}",
    "success": "{colors.success}",
    "information": "{colors.info}",
    "textOnFocus": "{colors.background}",
    "textOnError": "{colors.background}",
    "textOnSuccess": "{colors.background}",
    "textOnInformation": "{colors.background}",
}

EXPECTED_TERMINAL = {
    "dark": {
        "ansi": ["#1d2021", "#fb4934", "#b8bb26", "#fabd2f", "#83a598", "#d3869b", "#8ec07c", "#d5c4a1"],
        "bright": ["#665c54", "#fb4934", "#b8bb26", "#fabd2f", "#83a598", "#d3869b", "#8ec07c", "#fbf1c7"],
    },
    "light": {
        "ansi": ["#3c3836", "#9d0006", "#6b6700", "#8a5200", "#076678", "#8f3f71", "#356b4d", "#504945"],
        "bright": ["#665c54", "#9d0006", "#6b6700", "#8a5200", "#076678", "#8f3f71", "#356b4d", "#282828"],
    },
}


def check_palette() -> None:
    palettes = load_palettes()
    expected_identity = {
        "dark": ("apollo", "Apollo"),
        "light": ("apollo-light", "Apollo Light"),
    }
    if {palette["id"] for palette in palettes.values()} != {"apollo", "apollo-light"}:
        raise ValueError("Apollo palette IDs must be unique and canonical")
    for variant, palette in palettes.items():
        terminal = palette["terminal"]
        colors = palette["colors"]
        expected_id, expected_name = expected_identity[variant]
        if palette.get("schemaVersion") != 1 or palette.get("colorSpace") != "srgb":
            raise ValueError(f"{variant}: unsupported palette schema")
        if (palette["id"], palette["name"], palette["appearance"]) != (expected_id, expected_name, variant):
            raise ValueError(f"{variant}: palette identity mismatch")
        if variant == "light" and colors != EXPECTED_LIGHT_COLORS:
            raise ValueError("light: canonical colors changed unexpectedly")
        if variant == "light" and palette["roles"] != EXPECTED_LIGHT_ROLES:
            raise ValueError("light: canonical semantic roles changed unexpectedly")
        if terminal["ansi"] != EXPECTED_TERMINAL[variant]["ansi"]:
            raise ValueError(f"{variant}: canonical ANSI slots changed unexpectedly")
        if terminal["bright"] != EXPECTED_TERMINAL[variant]["bright"]:
            raise ValueError(f"{variant}: canonical bright slots changed unexpectedly")
        if terminal["foreground"] != colors["foreground"] or terminal["background"] != colors["background"]:
            raise ValueError(f"{variant}: terminal foreground/background role mismatch")
        cursor_text_key = palette["roles"]["cursorText"][8:-1]
        if terminal["cursor"] != colors["accent"] or terminal["cursorText"] != colors[cursor_text_key]:
            raise ValueError(f"{variant}: terminal cursor roles mismatch")
        selection = terminal["selection"]
        expected_alpha = 0.5 if variant == "dark" else 1.0
        if selection != {"color": colors["selection"], "alpha": expected_alpha, "foregroundMode": "preserve"}:
            raise ValueError(f"{variant}: selection contract mismatch")
        invalid = sorted({color for color in iter_hex_colors(palette) if not HEX_COLOR.fullmatch(color)})
        if invalid:
            raise ValueError(f"{variant}: invalid lowercase six-digit colors: {', '.join(invalid)}")
        for role, reference in palette["roles"].items():
            match = re.fullmatch(r"\{colors\.([A-Za-z][A-Za-z0-9]*)\}", reference)
            if not match or match.group(1) not in colors:
                raise ValueError(f"{variant}: invalid role reference for {role}: {reference}")
        minimum = palette["constraints"]["minimumTextContrast"]
        semantic_text_roles = ("textPrimary", "textSecondary", "textInactive", "focus", "error", "warning", "success", "information")
        direct_text_colors = ("foregroundBright", "magenta", "cyan")
        surfaces = ("background",) if variant == "dark" else ("background", "surface", "surfaceHover")
        for role in semantic_text_roles:
            color_key = palette["roles"][role][8:-1]
            for surface in surfaces:
                ratio = contrast_ratio(colors[color_key], colors[surface])
                if ratio < minimum:
                    raise ValueError(f"{variant}: {role} on {surface} is {ratio:.2f}, below {minimum:.2f}")
        for color_key in direct_text_colors:
            for surface in surfaces:
                ratio = contrast_ratio(colors[color_key], colors[surface])
                if ratio < minimum:
                    raise ValueError(f"{variant}: {color_key} on {surface} is {ratio:.2f}, below {minimum:.2f}")
        selection_text_key = palette["roles"].get("selectionText", "{colors.foreground}")[8:-1]
        if contrast_ratio(colors[selection_text_key], colors["selection"]) < minimum:
            raise ValueError(f"{variant}: selected text contrast is below {minimum:.2f}")
        if contrast_ratio(colors[cursor_text_key], colors["accent"]) < minimum:
            raise ValueError(f"{variant}: cursor text contrast is below {minimum:.2f}")
        if variant == "light":
            for role, fill in (("textOnFocus", "accent"), ("textOnError", "danger"), ("textOnSuccess", "success"), ("textOnInformation", "info")):
                color_key = palette["roles"][role][8:-1]
                ratio = contrast_ratio(colors[color_key], colors[fill])
                if ratio < minimum:
                    raise ValueError(f"light: {role} contrast is {ratio:.2f}, below {minimum:.2f}")
            provenance = palette["provenance"]
            if provenance["sourceCommit"] != "5d15b2765f59754d7ac263c88a0f6e3e58124951" or provenance["sourceSha256"] != "55116926ba2b625837d9ae89349a5688d60d0b32acdbd8887e1c0d225f079c3d":
                raise ValueError("light: Gruvbox source provenance changed unexpectedly")
        for restricted in palette["constraints"]["restrictedColors"]:
            if restricted not in colors.values() and restricted not in terminal["ansi"] + terminal["bright"]:
                raise ValueError(f"{variant}: restricted color is not part of the palette: {restricted}")
        if variant == "dark" and contrast_ratio(colors["ansiBrightBlack"], colors["background"]) >= minimum:
            raise ValueError("dark: restricted bright black no longer needs its usage constraint")


REQUIRED_SECTIONS = ("Lineage", "Roles", "Contrast rules", "Why Apollo Light darkens semantic colors", "ANSI slot order", "Choosing colors for a new app")


def sections(text):
    out, name = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            name = line[3:].strip()
            out[name] = []
        elif name:
            out[name].append(line)
    return out


def prose_words(lines):
    keep, fence = [], False
    for l in lines:
        if l.startswith("```"):
            fence = not fence
            continue
        if fence or l.lstrip().startswith(("|", "<!--")):
            continue
        keep.append(l)
    return len(re.findall(r"[A-Za-z][\w'-]*", " ".join(keep)))


def check_readme(text, palettes):
    errs, secs = [], sections(text)
    for s in REQUIRED_SECTIONS:
        if s not in secs:
            errs.append(f"missing section {s}")
        elif prose_words(secs[s]) < 80:
            errs.append(f"{s}: under 80 words of prose")
    for variant in ("dark", "light"):
        m = re.search(rf"<!-- example:{variant} -->(.*?)<!-- /example:{variant} -->", text, re.S)
        if not m:
            errs.append(f"missing worked example {variant}")
            continue
        known = set(iter_hex_colors(palettes[variant]))
        rows = [r for r in m.group(1).strip().splitlines()[2:] if r.startswith("|")]
        if not rows:
            errs.append(f"{variant}: worked example has no rows")
        for row in rows:
            role, fg, bg, ratio, _ = [c.strip() for c in row.strip("|").split("|")]
            for h in (fg, bg):
                if h not in known:
                    errs.append(f"{variant} {role}: {h} not in {variant} palette")
            if f"{contrast_ratio(fg, bg):.2f}" != ratio:
                errs.append(f"{variant} {role}: ratio {ratio} != {contrast_ratio(fg, bg):.2f}")
    return errs


REQUIRED_KEYS = ("schemaVersion", "id", "name", "appearance", "provenance", "colors", "roles", "terminal", "constraints")
TEXT_ROLES = ("foreground", "foregroundSecondary", "foregroundInactive", "accent", "danger", "success", "info")


def check_schema(p):
    return [f"{v}: missing key {k}" for v, d in p.items() for k in REQUIRED_KEYS if k not in d] + [f"{v}: bad hex {h}" for v, d in p.items() for h in iter_hex_colors(d) if not HEX_COLOR.match(h)]


def check_slots(p):
    return [f"{v}: terminal.{k} slot order differs" for v in p for k in ("ansi", "bright") if p[v]["terminal"][k] != EXPECTED_TERMINAL[v][k]]


def check_contrast(p):
    return [f"{v} {r}: {contrast_ratio(d['colors'][r], d['colors']['background']):.2f} < 4.5" for v, d in p.items() for r in TEXT_ROLES if contrast_ratio(d["colors"][r], d["colors"]["background"]) < 4.5]


def main() -> int:
    import tables

    errors = []
    try:
        check_palette()
    except (KeyError, ValueError) as error:
        errors.append(str(error))
    palettes = load_palettes()
    errors += check_schema(palettes) + check_slots(palettes) + check_contrast(palettes)
    errors += [f"README tables:{name} block is stale; run scripts/tables.py --write" for name in tables.check()]
    errors += check_readme(README.read_text(encoding="utf-8") if README.exists() else "", palettes)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if not errors:
        print("Apollo palette checks passed.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
