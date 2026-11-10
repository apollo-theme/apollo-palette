from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATHS = {
    "dark": ROOT / "palette" / "apollo.json",
    "light": ROOT / "palette" / "apollo-light.json",
}
PALETTE_PATH = PALETTE_PATHS["dark"]
HEX_COLOR = re.compile(r"^#[0-9a-f]{6}$")


def palette_path(variant: str | Path = "dark") -> Path:
    if isinstance(variant, Path):
        return variant
    try:
        return PALETTE_PATHS[variant]
    except KeyError as error:
        raise ValueError(f"unknown Apollo variant: {variant}") from error


def load_palette(variant: str | Path = "dark") -> dict:
    return json.loads(palette_path(variant).read_text(encoding="utf-8"))


def load_palettes() -> dict[str, dict]:
    return {variant: load_palette(variant) for variant in PALETTE_PATHS}


def palette_sha256(variant: str | Path = "dark") -> str:
    return hashlib.sha256(palette_path(variant).read_bytes()).hexdigest()


def iter_hex_colors(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from iter_hex_colors(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_hex_colors(nested)
    elif isinstance(value, str) and value.startswith("#"):
        yield value


def relative_luminance(color: str) -> float:
    channels = []
    for offset in (1, 3, 5):
        channel = int(color[offset : offset + 2], 16) / 255
        channels.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: str, second: str) -> float:
    high, low = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)
