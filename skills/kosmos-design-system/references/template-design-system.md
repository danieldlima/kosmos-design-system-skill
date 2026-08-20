# Template Design System

The 2026 Kunumi and Instituto source decks were inspected slide by slide. They are parallel 16:9 systems built on Figtree, a two-by-two spatial grid, inherited brand furniture, and disciplined light/dark modes.

## Shared Essence

- Use **Figtree** throughout. Keep titles short, left aligned, and structurally dominant.
- Compose on a **two-by-two grid** with generous breathing space. Alignment and empty space carry more identity than decoration.
- Use **Gelo** as the default paper field and **Chumbo** for dark chapters. Urucum is the reading accent, not a fill-everything color.
- Keep the identity mark small in page furniture. Allow the symbol to become large only on covers, identity stories, and resource slides.
- Prefer one clear narrative job per slide: title, evidence, comparison, process, media story, or transition.
- Reuse the source element geometry. When content does not fit, shorten it or select a different layout before shrinking typography.
- Use hairline rules, restrained page markers, and precise edge alignment instead of rounded-card UI language.

## Core Kunumi Mode

Core Kunumi is quiet, direct, and editorial:

- Minimal Gelo covers pair a large shared symbol with a concise title and small wordmark.
- Body slides use black/Chumbo type, Urucum emphasis, thin rules, and strong column alignment.
- Dark mode is reserved for chapter rhythm, image-led stories, dense matrices, and high-contrast metrics.
- Photographs and charts occupy defined frames; they do not float as decorative stickers.

## Instituto Mode

Instituto shares the grid but adds an expressive spectrum:

- Approved gradients, gamma waves, stepped pixels, bars, kaleidoscope, and maps may create cover or chapter atmosphere.
- Use the supplied assets intact. Do not approximate their colors, redraw their wave forms, or synthesize replacement motion.
- Keep essential copy away from high-frequency areas and preserve strong contrast.
- Motion is slow and atmospheric: background drift, wave movement, or a single symbol loop. Text and page furniture remain stable.
- The Instituto wordmark/lockup identifies the system; do not substitute the core Kunumi wordmark.

## Source Decks

| System | Canonical deck | Source layout coverage |
| --- | --- | --- |
| Kunumi | 76 slides | cover, agenda, gradient/pixel transitions, text, photo, bars, media grid, metrics, chart, timeline, table, dark variants, closing, marks, icons, static assets |
| Instituto | 75 slides | Instituto cover, minimal/gradient/pixel covers, agenda, text, photo, bars, media grid, metrics, chart, timeline, table, dark variants, closing, marks, graphic resources, static assets |

Neither deck is bundled. Ask the user for the approved source deck, and use `slide-layouts.md` to
identify the exact layout to duplicate.

## Web Motion Translation

- Use a 480–700 ms ease-out for slide entry and content rise.
- Stagger only elements that have a reading order; 80–180 ms is enough.
- Keep background drift between 6–12 seconds and under roughly 6% scale/position change.
- A progress rail may draw once on entry. Do not loop attention effects on controls or essential copy.
- Honor `prefers-reduced-motion` by reducing transitions and disabling loops.
- In responsive layouts, preserve the 16:9 stage when presenting slide replicas; for production sites, translate the hierarchy rather than forcing slide dimensions.

## CSS Contract

`assets/web/kunumi-tokens.css` is the reusable implementation:

- institutional and support color tokens;
- chart-only extended colors;
- local Figtree variable font faces;
- typography weights, spacing, timing, and reduced-motion behavior.

Use these tokens as a foundation, then follow the target medium’s composition rules. CSS tokens do not authorize recoloring supplied logos or Instituto art.
