# Apollo Palette

Apollo Palette is the source of truth for the two Apollo color schemes, Apollo Dark and Apollo Light. It holds the two palette files, `palette/apollo.json` (Dark, also known by the compatibility name Apollo) and `palette/apollo-light.json` (Light). It also explains how each color was chosen and how to map the palette onto an application that does not have an Apollo theme yet. Every ratio in this document is a WCAG 2.x contrast ratio computed by `scripts/common.py`. The generated tables are refreshed by `scripts/tables.py --write`, and `scripts/check.py` fails if any of them drift. The finished themes live in [apollo-theme/apollo-theme](https://github.com/apollo-theme/apollo-theme), and you can see rendered previews of every app at [apollo-theme.github.io](https://apollo-theme.github.io/).

## Lineage

Both variants adapt Gruvbox, created by Pavel Pertsev and released under the MIT License ([morhetz/gruvbox](https://github.com/morhetz/gruvbox)). They take different routes from it.

Apollo Dark comes from the Modified Gruvbox Dark Hard theme that ships with [SonicTerm](https://github.com/D0n9X1n/SonicTerm). Its `provenance` block pins `assets/themes/wezterm.toml` at SonicTerm commit `81917dc8fe736f18b4a531fd47a0f36fd89eaf8f`, with SHA-256 `0ed79939b82134b14ea3e339ebabee1f22ee5d12bb80915b0a407b5affb5f5ac`. SonicTerm contributed the near-black canvas, the softened primary text, and the terminal mapping. That mapping uses Gruvbox's bright accents in both the normal and bright ANSI banks.

Apollo Light is pinned directly to Gruvbox Light Hard in `colors/gruvbox.vim` at Gruvbox commit `5d15b2765f59754d7ac263c88a0f6e3e58124951`, with SHA-256 `55116926ba2b625837d9ae89349a5688d60d0b32acdbd8887e1c0d225f079c3d`. Light keeps Gruvbox's paper backgrounds and dark neutrals. It replaces only the semantic colors that fail text contrast, as explained below.

`NOTICE` records this attribution, and `LICENSE` covers this repository. Despite the shared name, this palette is unrelated to the 46-color pixel-art palette called Apollo.

## Roles

Each palette file has three layers. `colors` is a flat set of named hex values. `roles` gives those colors a meaning: every role is a reference such as `{colors.accent}`, never a raw hex value. A theme should therefore ask for "the error color" or "the canvas", not for a hue that happens to look red or dark. `terminal` holds the ordered ANSI slots and the cursor and selection contract.

Dark builds its surfaces from the near-black canvas `#141617`, which is darker than Gruvbox's own hard background `#1d2021`. That Gruvbox value becomes the raised `surface` and ANSI slot 0, at 1.11:1 against the canvas: just enough to separate a panel without drawing a border. Primary text `#cfbc97` is SonicTerm's softer cream. It reaches 9.76:1, where Gruvbox's usual `#ebdbb2` reaches 13.23:1, which reduces glare on the very dark canvas. `foregroundSecondary` (`#d5c4a1`) names a role, not a brightness. In Dark it is ANSI white and is slightly brighter than primary text. `foregroundInactive` is Gruvbox gray `#928374`. The accents are Gruvbox's bright series: accent/warning `#fabd2f`, danger `#fb4934`, success `#b8bb26`, information `#83a598`, magenta `#d3869b` and cyan `#8ec07c`.

Light uses Gruvbox's paper tones: canvas `#f9f5d7`, surface `#fbf1c7`, hover `#f2e5bc` and opaque selection `#ebdbb2`. Text runs from `#282828` (brightest emphasis) through primary `#3c3836` and secondary `#504945` to inactive `#665c54`. Light also defines `selectionText` and four `textOn*` roles for text placed on a filled semantic color. Those roles are explicit because an adapter must not guess inverse colors from whether the theme is dark or light.

<!-- tables:roles:start -->
| Role | Apollo Dark | Apollo Light |
| --- | --- | --- |
| `canvas` | `#141617` (background) | `#f9f5d7` (background) |
| `cursor` | `#fabd2f` (accent) | `#8a5200` (accent) |
| `cursorText` | `#141617` (background) | `#f9f5d7` (background) |
| `error` | `#fb4934` (danger) | `#9d0006` (danger) |
| `focus` | `#fabd2f` (accent) | `#8a5200` (accent) |
| `information` | `#83a598` (info) | `#076678` (info) |
| `selection` | `#3c3836` (selection) | `#ebdbb2` (selection) |
| `selectionText` | — | `#3c3836` (foreground) |
| `success` | `#b8bb26` (success) | `#6b6700` (success) |
| `textInactive` | `#928374` (foregroundInactive) | `#665c54` (foregroundInactive) |
| `textOnError` | — | `#f9f5d7` (background) |
| `textOnFocus` | — | `#f9f5d7` (background) |
| `textOnInformation` | — | `#f9f5d7` (background) |
| `textOnSuccess` | — | `#f9f5d7` (background) |
| `textPrimary` | `#cfbc97` (foreground) | `#3c3836` (foreground) |
| `textSecondary` | `#d5c4a1` (foregroundSecondary) | `#504945` (foregroundSecondary) |
| `warning` | `#fabd2f` (accent) | `#8a5200` (accent) |
<!-- tables:roles:end -->

## Contrast rules

The floor is `minimumTextContrast` 4.5:1 (WCAG AA) for normal and small text. `minimumLargeTextContrast` is 3:1, and that lower value is also the practical target for non-text indicators such as focus borders. The table below is generated from the palettes. It covers every text role against the canvas (`background`), the raised `surface` and the `selection` color.

Read it as a set of permissions. In Light, every text role clears 4.5:1 on canvas, surface and hover. The weakest pairing is success `#6b6700` on hover `#f2e5bc` at 4.69:1. In Dark, the guarantee covers the canvas only. Inactive gray `#928374` reaches 4.95:1 on `#141617` but only 4.47:1 on surface `#1d2021`, so text on a surface-filled area must use `foregroundSecondary` or primary text.

The selection column is a worst case for Dark, because the table treats its 50% `#3c3836` overlay as opaque. Composited over the canvas, primary text actually reaches about 8.02:1. Selection uses `foregroundMode` `preserve`: the selected text keeps its color. Only the primary and selection-text roles are guaranteed legible on selection, because some accents fall below 4.5:1 there.

`#665c54` is restricted in Dark. It reaches only 2.79:1 on the canvas, so it is reserved for ANSI bright black and must never be used for interface text. In Light, the same value is the inactive text color and reaches 5.92:1.

Inverse pairs are checked separately. Cursor text uses the canvas color on the accent: 10.71:1 in Dark and 5.80:1 in Light. Light's `textOn*` roles put canvas-colored text on danger, success and information fills at 7.83:1, 5.35:1 and 6.00:1.

<!-- tables:contrast:start -->
| Variant | Color | Hex | On background | On surface | On selection |
| --- | --- | --- | ---: | ---: | ---: |
| Dark | `foreground` | `#cfbc97` | 9.76 | 8.82 | 6.24 |
| Dark | `foregroundSecondary` | `#d5c4a1` | 10.58 | 9.56 | 6.76 |
| Dark | `foregroundInactive` | `#928374` | 4.95 | 4.47 | 3.16 |
| Dark | `accent` | `#fabd2f` | 10.71 | 9.67 | 6.84 |
| Dark | `danger` | `#fb4934` | 5.28 | 4.77 | 3.37 |
| Dark | `success` | `#b8bb26` | 8.79 | 7.94 | 5.62 |
| Dark | `info` | `#83a598` | 6.74 | 6.09 | 4.31 |
| Light | `foreground` | `#3c3836` | 10.53 | 10.22 | 8.45 |
| Light | `foregroundSecondary` | `#504945` | 8.01 | 7.78 | 6.43 |
| Light | `foregroundInactive` | `#665c54` | 5.92 | 5.74 | 4.75 |
| Light | `accent` | `#8a5200` | 5.80 | 5.63 | 4.66 |
| Light | `danger` | `#9d0006` | 7.83 | 7.60 | 6.28 |
| Light | `success` | `#6b6700` | 5.35 | 5.19 | 4.29 |
| Light | `info` | `#076678` | 6.00 | 5.82 | 4.81 |
<!-- tables:contrast:end -->

## Why Apollo Light darkens semantic colors

For text, Gruvbox Light uses its "faded" series. Three of those colors already pass on every Apollo Light background, so Apollo keeps them unchanged:

- red `#9d0006`: 7.83:1 on canvas, 6.86:1 on hover
- blue `#076678`: 6.00:1 on canvas, 5.25:1 on hover
- purple `#8f3f71`: 6.12:1 on canvas, 5.36:1 on hover

The others fail somewhere, and the binding background is hover `#f2e5bc`, the darkest of the three paper tones:

| Gruvbox original | On `#f9f5d7` | On `#f2e5bc` | Apollo Light | On `#f9f5d7` | On `#f2e5bc` |
| --- | ---: | ---: | --- | ---: | ---: |
| yellow `#b57614` | 3.43 | 3.00 | accent `#8a5200` | 5.80 | 5.08 |
| green `#79740e` | 4.42 | 3.87 | success `#6b6700` | 5.35 | 4.69 |
| aqua `#427b58` | 4.53 | 3.97 | cyan `#356b4d` | 5.67 | 4.97 |
| gray `#928374` | 3.33 | 2.92 | inactive `#665c54` | 5.92 | 5.18 |

Each replacement keeps the original hue and lowers only the lightness:

- yellow moves from hue 37° to 36°
- green moves from 57° to 58°
- aqua moves from 143° to 147°

Yellow becomes a deep amber, which is why the Light accent reads as brown-gold rather than yellow. A paler yellow cannot carry text on cream paper. The inactive gray becomes Gruvbox's own `#665c54`, its dark3 neutral, rather than a new color.

The terminal shows the same problem in a stronger form. In the pinned `gruvbox.vim`, the Light terminal's normal slots 1–6 use the neutral series, and on the Apollo canvas these are weak:

- red `#cc241d`: 4.97:1
- blue `#458588` and purple `#b16286`: 3.84:1
- aqua `#689d6a`: 2.88:1
- green `#98971a`: 2.81:1
- yellow `#d79921`: 2.25:1

Apollo Light drops them and uses the hardened semantic colors in both banks. That way, colored program output is as readable as interface text.

## ANSI slot order

`terminal.ansi` and `terminal.bright` are ordered arrays, not color sets. The index is the contract. Slot 0 is black, then red, green, yellow, blue, magenta, cyan and white, and `bright` repeats that order for slots 8–15. Programs ask for "red" or "bright black" by number. Moving a color to another index changes what every terminal program draws, even if the array still contains the same colors. For that reason, `check.py` compares both arrays element by element against the expected order.

| Slot | Name | Dark | Light | | Slot | Name | Dark | Light |
| ---: | --- | --- | --- | --- | ---: | --- | --- | --- |
| 0 | black | `#1d2021` | `#3c3836` | | 8 | bright black | `#665c54` | `#665c54` |
| 1 | red | `#fb4934` | `#9d0006` | | 9 | bright red | `#fb4934` | `#9d0006` |
| 2 | green | `#b8bb26` | `#6b6700` | | 10 | bright green | `#b8bb26` | `#6b6700` |
| 3 | yellow | `#fabd2f` | `#8a5200` | | 11 | bright yellow | `#fabd2f` | `#8a5200` |
| 4 | blue | `#83a598` | `#076678` | | 12 | bright blue | `#83a598` | `#076678` |
| 5 | magenta | `#d3869b` | `#8f3f71` | | 13 | bright magenta | `#d3869b` | `#8f3f71` |
| 6 | cyan | `#8ec07c` | `#356b4d` | | 14 | bright cyan | `#8ec07c` | `#356b4d` |
| 7 | white | `#d5c4a1` | `#504945` | | 15 | bright white | `#fbf1c7` | `#282828` |

In Dark, both banks use Gruvbox's bright accents. The normal-bank alternatives are too dim on `#141617`: neutral red `#cc241d` reaches only 3.32:1, and neutral blue and purple reach 4.29:1. The slots stay ordered by name, not by lightness. In Light, slot 0 "black" is the dark text color `#3c3836`, not the canvas, and "white" slots 7 and 15 are dark grays.

This is deliberate. Programs print "white" or "black" text expecting it to stand out from the background, so in Light those slots hold the high-contrast ends. Gruvbox Light instead puts the canvas in slot 0, which makes black text invisible. Slot 8 is the one place where Dark's restricted `#665c54` is allowed. Shells use it for dim hints that the user may ignore.

## Choosing colors for a new app

Start from roles, not hues. List every visible element in the target app, and give each one a role:

- canvas, surface, hover or selection for fills
- primary, secondary or inactive for text
- focus, error, warning, success or information for state

Then pick the matching `roles` entry for each variant. Do not derive Light by inverting Dark. Check every foreground and background pair with `scripts/common.contrast_ratio` against the contrast rules above.

Text needs 4.5:1. Focus indicators need 3:1. Purely decorative separators may go lower, as long as they carry no meaning that is not shown some other way. If the target cannot draw alpha, replace Dark's 50% selection with an opaque color and test it. If an element sits on the surface in Dark, do not use the inactive gray there.

The worked example below maps tmux and matches the published tmux theme:

- The status bar is filled with the canvas, so it merges into the terminal. Its legibility comes from the status text, which is why that row reads 1.00.
- The active pane border uses the accent. The inactive border uses the selection tone, a quiet divider at 1.57:1 in Dark and 1.25:1 in Light. That is acceptable only because the active border alone carries the focus state.
- Messages and copy-mode selection are short-lived states that must catch the eye. They use a filled accent with canvas-colored text, the same inverse pair as the cursor.

Either selection role would also work for copy mode: primary text on the opaque selection reaches 6.24:1 in Dark and 8.45:1 in Light.

<!-- example:dark -->
| Role | Hex | Background | Ratio | Reason |
| --- | --- | --- | --- | --- |
| Status text | #cfbc97 | #141617 | 9.76 | textPrimary on canvas |
| Status background | #141617 | #141617 | 1.00 | canvas fill; bar merges with panes and status text carries legibility |
| Active border | #fabd2f | #141617 | 10.71 | focus accent; well above the 3:1 indicator floor |
| Inactive border | #3c3836 | #141617 | 1.57 | selection tone as a quiet divider; focus is shown by the active border |
| Message | #141617 | #fabd2f | 10.71 | inverse cursor pair; canvas text on accent fill |
| Mode selection | #141617 | #fabd2f | 10.71 | copy mode uses the same inverse accent pair |
<!-- /example:dark -->

<!-- example:light -->
| Role | Hex | Background | Ratio | Reason |
| --- | --- | --- | --- | --- |
| Status text | #3c3836 | #f9f5d7 | 10.53 | textPrimary on canvas |
| Status background | #f9f5d7 | #f9f5d7 | 1.00 | canvas fill; bar merges with panes and status text carries legibility |
| Active border | #8a5200 | #f9f5d7 | 5.80 | darkened focus accent; above the 3:1 indicator floor |
| Inactive border | #ebdbb2 | #f9f5d7 | 1.25 | opaque selection tone as a quiet divider; focus is shown by the active border |
| Message | #f9f5d7 | #8a5200 | 5.80 | explicit textOnFocus on accent fill |
| Mode selection | #f9f5d7 | #8a5200 | 5.80 | copy mode uses the same inverse accent pair |
<!-- /example:light -->
