#!/usr/bin/env python3
"""Render the README role and contrast tables from the canonical palettes."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import ROOT, contrast_ratio, load_palettes

README = ROOT / "README.md"
BLOCKS = ("roles", "contrast")
VARIANTS = (("dark", "Dark"), ("light", "Light"))
TEXT_ROLES = ("foreground", "foregroundSecondary", "foregroundInactive", "accent", "danger", "success", "info")
BACKGROUNDS = ("background", "surface", "selection")


def _color_key(reference: str) -> str:
    return reference[len("{colors.") : -1]


def _role_cell(palette: dict, role: str) -> str:
    if role not in palette["roles"]:
        return "—"
    key = _color_key(palette["roles"][role])
    return f"`{palette['colors'][key]}` ({key})"


def render(palettes: dict[str, dict]) -> dict[str, str]:
    roles = sorted(set(palettes["dark"]["roles"]) | set(palettes["light"]["roles"]))
    role_lines = ["| Role | Apollo Dark | Apollo Light |", "| --- | --- | --- |"]
    role_lines += [f"| `{role}` | {_role_cell(palettes['dark'], role)} | {_role_cell(palettes['light'], role)} |" for role in roles]

    contrast_lines = [
        "| Variant | Color | Hex | On background | On surface | On selection |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for variant, label in VARIANTS:
        colors = palettes[variant]["colors"]
        for key in TEXT_ROLES:
            ratios = " | ".join(f"{contrast_ratio(colors[key], colors[bg]):.2f}" for bg in BACKGROUNDS)
            contrast_lines.append(f"| {label} | `{key}` | `{colors[key]}` | {ratios} |")
    return {"roles": "\n".join(role_lines), "contrast": "\n".join(contrast_lines)}


def _pattern(name: str) -> re.Pattern:
    return re.compile(rf"(<!-- tables:{name}:start -->\n)(.*?)(\n<!-- tables:{name}:end -->)", re.S)


def replace_between(text: str, name: str, body: str) -> str:
    pattern = _pattern(name)
    if not pattern.search(text):
        raise ValueError(f"missing tables:{name} markers")
    return pattern.sub(lambda m: m.group(1) + body + m.group(3), text, count=1)


def stale(text: str) -> list[str]:
    rendered = render(load_palettes())
    out = []
    for name in BLOCKS:
        match = _pattern(name).search(text)
        if not match:
            raise ValueError(f"missing tables:{name} markers")
        if match.group(2).strip() != rendered[name]:
            out.append(name)
    return out


def check(path: Path = README) -> list[str]:
    if not path.exists():
        return list(BLOCKS)
    try:
        return stale(path.read_text(encoding="utf-8"))
    except ValueError:
        return list(BLOCKS)


def write(path: Path = README) -> None:
    text = path.read_text(encoding="utf-8")
    for name, body in render(load_palettes()).items():
        text = replace_between(text, name, body)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="rewrite the README table blocks")
    mode.add_argument("--check", action="store_true", help="exit 1 if any README table block is missing or stale")
    args = parser.parse_args()
    if args.write:
        write()
        print("README tables written.")
        return 0
    names = check()
    for name in names:
        print(f"stale: tables:{name}", file=sys.stderr)
    return 1 if names else 0


if __name__ == "__main__":
    sys.exit(main())
