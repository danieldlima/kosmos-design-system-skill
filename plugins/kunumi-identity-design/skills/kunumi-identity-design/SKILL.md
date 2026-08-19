---
name: kunumi-identity-design
description: Apply approved Kunumi, Instituto Kunumi, and Kunumi Unlimited identity guidance to documents, slides, sites, apps, UI mockups, social assets, profile images, templates, and written materials. Use when work must select or place Kunumi logos, use Kunumi colors or Figtree typography, reuse branded backgrounds or motion assets, follow LinkedIn or profile-photo templates, or review an artifact for Kunumi brand fidelity.
---

# Kunumi Identity Design

Create the artifact from the smallest relevant context set. The original templates and assets remain the source of truth.

## Route

1. Identify core Kunumi, Kunumi Unlimited, or Instituto Kunumi. Do not mix their lockups or expressive systems unless the user explicitly requests co-branding.
2. Always read `references/brand-foundations.md`.
3. Then read only what the task needs:

| Task | Read |
| --- | --- |
| Slides or presentations | `references/slide-layouts.md` + `references/medium-playbooks.md` + `references/visual-patterns.md` |
| Charts, documents, reports, web, apps, UI, images, social, GIF, video | `references/medium-playbooks.md` + `references/visual-patterns.md` |
| Logo, background, motion, template, or Drive source selection | `references/content-map.md` + `references/asset-catalog.md` |
| Kunumi/Instituto slide or web-system fidelity | `references/template-design-system.md` |
| Profile photo, portrait, or avatar | `references/profile-photo-system.md` |

Do not load index JSON files wholesale. Query their compact views:

```bash
python scripts/kunumi_lookup.py tokens
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py resolve "Kunumi slide template"
python scripts/kunumi_lookup.py folders --search "profile portrait"
python scripts/kunumi_lookup.py sources --access drive --kind motion
python scripts/kunumi_lookup.py slides --tag chart
python scripts/kunumi_lookup.py patterns --medium slides --tag data-viz
```

## Source Order

1. Source or version named by the user.
2. Matching approved local file in `assets/local/`.
3. Exact canonical Drive object recorded in `references/semantic-index.json`.
4. Extracted rules in `references/`.

If sources conflict, use the highest applicable source. Do not average rules or invent a compromise.

Use the local agent-ready Kunumi/Instituto decks by default. Connect to Google Drive only for a canonical full deck, an unrepresented source slide, heavy motion/video, a channel guide, portraits, historical/client material, or the annual report. Fetch Drive sources by recorded ID and cache them outside the repository.

## Nonnegotiables

- Reuse the approved files. Do not redraw, trace, recolor, distort, crop, animate, or typeset a substitute for an available mark.
- Use Instituto gradients, waves, pixels, bars, kaleidoscope, gamma maps, and motion as supplied.
- Prefer supplied SVG for vector work and transparent PNG for raster work.
- Use Figtree; if unavailable, use Arial or a neutral system sans. Do not download or synthesize a font without authorization.
- Prefer `assets/web/kunumi-tokens.css` for web work and honor its reduced-motion behavior.
- Do not invent legal names, slogans, claims, relationships, policy, governance, colors, or assets.
- When a required source is missing, ask for it if identity fidelity is central. Otherwise use a neutral text-only treatment and state the limitation.
- Render the final artifact and inspect every page, slide, frame, loop, breakpoint, or export at delivery size.
