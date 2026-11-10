# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repository is the canonical source for the Apollo palettes. `palette/apollo.json` is Apollo Dark (compatibility name `Apollo` / `apollo`) and `palette/apollo-light.json` is Apollo Light (`Apollo Light` / `apollo-light`). `README.md` explains the lineage, roles, contrast rules, Light hardening, ANSI slot order, and how to map the palette onto a new app. `NOTICE` records Gruvbox and SonicTerm lineage. Do not substitute the unrelated 46-color pixel-art palette also named Apollo.

## Commands

```sh
python3 scripts/check.py                    # palette identity, schema, slot order, contrast, README tables and sections
python3 -m unittest discover -s tests -v    # unit tests
python3 scripts/tables.py --write           # regenerate README role/contrast tables
python3 scripts/tables.py --check           # exit 1 if a README table block is missing or stale
```

`check.py` must exit 0 before any commit. It fails when the README's generated tables are stale, when a required `##` section has under 80 words of prose, or when a worked-example row uses a hex value outside its variant's palette or a ratio that does not match `scripts/common.contrast_ratio`.

## Downstream consumers

The palette file bytes are consumed by `apollo-theme` and the `apollo-theme.github.io` site, which record the exact source they copied in `SOURCE.json`. Consumers never edit their palette snapshots by hand. After a palette change lands here, run `sync_palette.py` in each downstream repository, regenerate, and publish there; never point a consumer at an unpushed commit of this repository.

## Changing a palette

- Change one variant at a time; the other variant's bytes must not move.
- Update the `EXPECTED_*` constants in `scripts/check.py` deliberately in the same commit; they exist so accidental edits fail.
- Keep both invariants: every normal or small text role is at least 4.5:1 on its canvas (Light: canvas, surface, and hover), and Dark `#665c54` stays ANSI bright black only.
- `terminal.ansi` and `terminal.bright` are ordered slots; never reorder them.
- Run `python3 scripts/tables.py --write`, update any README prose or worked-example ratios the change affects, then run `check.py` and the tests.
