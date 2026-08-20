---
name: kosmos-design-system
description: Design and review work in the Kunumi visual and verbal identity, covering Kunumi, Kunumi Unlimited, Instituto Kunumi, and Kunumi Colab. Use when work must apply Kunumi colors, place a Kunumi logo, set Kunumi typography, build a Kunumi web page, app, UI, slide, chart, or social asset, write or review Kunumi copy and tone of voice, choose an approved Kunumi asset, or check an artifact for Kunumi brand fidelity.
---

# Kosmos Design System

Design in the Kunumi system, from the smallest relevant context set. The **Brandbook Kunumi Final
(2025)** is the authority; the original templates and approved asset files remain the source of
truth for artwork.

## Route

1. Pick the identity: **Kunumi**, **Kunumi Unlimited**, **Instituto Kunumi**. Do not mix their
   lockups or expressive systems unless the user explicitly asks for co-branding.
2. Always read `references/brand-foundations.md`.
3. Then read only what the task needs:

| Task | Read |
| --- | --- |
| Typography, titles, type scale, emphasis | `references/typography.md` |
| Logo placement, clear space, minimum size, co-branding, misuse | `references/logo-governance.md` |
| Copy, microcopy, naming, tone, verbal review | `references/brand-voice.md` |
| Brand architecture, formats, margins, Versus symbol, hatching | `references/visual-behavior.md` |
| Web, app, or UI | `references/medium-playbooks.md` + `references/typography.md` |
| Slides or presentations | `references/slide-layouts.md` + `references/medium-playbooks.md` + `references/visual-patterns.md` |
| Charts and data visualization | `references/medium-playbooks.md` |
| Images, social, GIF, video | `references/medium-playbooks.md` + `references/visual-patterns.md` |
| Asset, background, or motion selection | `references/content-map.md` + `references/asset-catalog.md` |
| Kunumi/Instituto slide or web-system fidelity | `references/template-design-system.md` |
| Profile photo, portrait, or avatar | `references/profile-photo-system.md` |

Do not load index JSON files wholesale. Query their compact views:

```bash
python scripts/kunumi_lookup.py tokens
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py sources --identity instituto
python scripts/kunumi_lookup.py slides --tag chart
python scripts/kunumi_lookup.py patterns --medium slides --tag data-viz
```

## Source Order

1. Source or version named by the user.
2. Matching approved local file in `assets/local/`, resolved through `references/semantic-index.json`.
3. Extracted rules in `references/`.

If sources conflict, use the highest applicable source. Do not average rules or invent a
compromise. Where the older deck-derived references disagree with the 2025 brandbook, the
brandbook wins.

No slide deck is bundled. When a task needs a source deck, heavy motion/video, a channel guide,
portraits, or historical/client material, ask the user to supply the approved file and cache it
outside the repository. Use `references/slide-layouts.md` to identify the exact source layout to
duplicate once a deck is supplied.

## Nonnegotiables

- **Two type families, two jobs.** PP Neue Machina Inktrap or Space Grotesk for titles, **always
  uppercase**, tracked **+3%**. Figtree for body and subtitles at **0** tracking. Never set a
  title in lowercase, never set body in the display face, never use Arial for display.
- **Chumbo replaces black; Gelo replaces white.** Pure black and white are not brand colors. White
  is allowed only as an elevated card surface on Gelo.
- **The chart palette is for data only** — `#4392D2`, `#2FB7CF`, `#62CCA3`, `#A0C068`, `#F0D449`.
  Never a UI accent or a background.
- **Logo:** 1X clear space where X is the symbol's square module; minimum 28 px / 10 mm of lockup
  height. Reuse the approved file — do not redraw, trace, recolor, distort, crop, rotate, animate,
  or typeset a substitute for an available mark.
- Use Instituto gradients, waves, pixels, bars, kaleidoscope, gamma maps, and motion as supplied.
- Prefer supplied SVG for vector work and transparent PNG for raster work.
- Prefer `assets/web/kunumi-tokens.css` for web work and honor its reduced-motion behavior.
- Write **Kunumi Unlimited**, never "Kunumi Unltd". Only `unltd` in filenames is fine.
- Do not invent legal names, slogans, claims, relationships, policy, governance, colors, or
  assets. **Kunumi Colab** has a name but no documented mark — ask before designing for it.
- When a required source is missing, ask for it if identity fidelity is central. Otherwise use a
  neutral text-only treatment and state the limitation.
- Render the final artifact and inspect every page, slide, frame, loop, breakpoint, or export at
  delivery size.
