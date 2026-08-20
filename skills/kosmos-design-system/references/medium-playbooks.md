# Kunumi Medium Playbooks

Use this file after choosing the identity in `brand-foundations.md`. Query assets, slide layouts, and `visual-patterns.md` instead of opening the complete source libraries.

## Contents

- [Universal Recipe](#universal-recipe)
- [Slides](#slides)
- [Charts and Data Visualization](#charts-and-data-visualization)
- [Documents and Reports](#documents-and-reports)
- [Web, Apps, and UI](#web-apps-and-ui)
- [Images and Social Assets](#images-and-social-assets)
- [Motion, GIF, and Video](#motion-gif-and-video)
- [Delivery Gate](#delivery-gate)

For any copy inside these artifacts — headings, labels, captions, empty states, error
messages — follow `brand-voice.md`.

## Universal Recipe

1. Select core Kunumi, Kunumi Unlimited, or Instituto Kunumi.
2. Set the type system from `typography.md` — display face uppercase for titles, Figtree for body — on a Gelo canvas with Chumbo text and Urucum emphasis, unless a supplied asset or source layout establishes another mode.
3. Query approved assets with `python scripts/kunumi_lookup.py assets ...`.
4. Query a Ksequence-derived composition when an expressive treatment helps: `python scripts/kunumi_lookup.py patterns ...`.
5. Build on the two-by-two grid: two major horizontal blocks, two vertical blocks, then subdivisions.
6. Use one dominant message, one clear reading order, and only the visual structure the content needs.
7. Render at final size and inspect the real output.

Avoid invented gradients, pseudo-logos, generic neon AI styling, excessive cards, pill decoration, crowded dashboards, arbitrary rounded containers, and unapproved colors.

## Slides

Ask the user for the approved PPTX source deck and follow `slide-layouts.md`.

1. Query by narrative job:

   ```bash
   python scripts/kunumi_lookup.py slides --search "title cover"
   python scripts/kunumi_lookup.py slides --tag chart
   python scripts/kunumi_lookup.py slides --tag photo --mode dark
   ```

2. Duplicate the closest source slide and preserve master, layout, typography, grid, footer, and contrast mode.
3. Replace content inside inherited placeholders and image frames.
4. Apply `visual-patterns.md` as narrative, diagram, and motion guidance inside the inherited composition; do not rebuild the template around a reference pattern.
5. Use one composition per slide. Keep titles short and move detail into body copy, notes, or another slide.
6. Prefer source slide 42 for an imported chart and slide 43 for a simple native chart.
7. Render every slide. Inspect text fit, image crops, chart labels, repeated spacing, and empty placeholders.

## Charts and Data Visualization

### Default visual grammar

- Background: Gelo `#F0F0F0`. Not white — Gelo replaces white.
- Text and axes: Chumbo `#1C2127`.
- Grid, rules, and inactive values: Concreto `#B4ADA4`.
- Primary series or key finding: Urucum `#F04E44`.
- Series colors: the brandbook chart palette, **data only** — `#4392D2` blue, `#2FB7CF` cyan,
  `#62CCA3` green, `#A0C068` olive, `#F0D449` yellow. This supersedes the older ten-step
  extended palette, which now exists only to read legacy template charts.
- Type: Figtree for labels, axes, and notes. A chart title in the display face is uppercase.

### Construction

1. State the finding in the title, not only the metric name.
2. Remove non-informative borders, legends, minor ticks, 3D effects, shadows, and chart chrome.
3. Use consistent scales and honest baselines. Make units, dates, definitions, and uncertainty explicit.
4. Highlight one comparison with Urucum; mute context in Chumbo, Grafite, or Concreto.
5. Put labels close to the data. Use a legend only when direct labels would collide.
6. Add a compact source note for external data or non-trivial claims.
7. For categorical sets, use the five chart colors in order and stop there. The brandbook defines
   no sequential or diverging ramp — do not invent intermediate steps. If five categories are not
   enough, group the tail or change the chart form.
8. Verify color contrast and ensure meaning is not encoded by color alone.

Use flat lines and fills by default. Instituto artwork may frame a chart, but do not place essential labels over a busy gradient, wave, pixel, kaleidoscope, or gamma-map region.

## Documents and Reports

- Use Gelo/White pages, Urucum headings, Chumbo body text, Grafite secondary text, and Concreto rules.
- Build a clear title → summary → sections → action or conclusion hierarchy.
- Use restrained callouts and tables; avoid turning every paragraph into a box.
- Use exact supplied art for a branded cover or divider. Do not recreate its gradient.
- Keep running headers, footers, page numbers, captions, and source notes consistent.
- Treat the Slack guide only as a visual reference; do not copy its operational policies.
- Render and inspect every page after editing. Check page breaks, orphaned headings, table splits, crops, links, and accessibility text.

## Web, Apps, and UI

- Titles in the display face, uppercase, tracked +3%. Body in Figtree at 140-175% line height,
  tracking 0. Arial is a body fallback only, never display. See `typography.md`.
- Default to a Gelo ground with Chumbo text and selective Urucum actions or emphasis. White is
  available only as an elevated card surface on Gelo.
- Prefer the semantic tokens in `assets/web/kunumi-tokens.css` (`--kunumi-ground`,
  `--kunumi-ink`, `--kunumi-ink-muted`, `--kunumi-border`, `--kunumi-accent`) over literal hexes.
- Use the two-by-two grid as a page-composition principle, not as four mandatory cards.
- Keep navigation and operational interfaces dense, legible, and scannable.
- Use rounded corners, elevation, and animation only when they clarify hierarchy or state. When a
  card is warranted, the brandbook radius is **10 px** (`--kunumi-radius-card`); hairline rules
  and precise edge alignment remain the default language.
- For technical storytelling, selectively use the dark Ksequence-derived canvas, orbital systems, claim/demo splits, and expressive Urucum-orange-violet ramp from `visual-patterns.md`.
- Pair color with text, icon, shape, or position. Meet the product's required contrast and accessibility standards.
- Use supplied Instituto motion as a hero or transition layer, with a calm text-safe region and a static fallback.
- Preserve SVG marks and responsive aspect ratios. Never approximate a logo with text or CSS.

## Images and Social Assets

1. Confirm target channel, dimensions, identity, language, and whether the asset is static or animated.
2. Choose a supplied background or a restrained Gelo/White composition.
3. Establish one focal image, one headline, and one brand signature.
4. Keep essential copy away from crops, busy artwork, and platform safe-zone edges.
5. Use the 1584×396 LinkedIn header template as supplied for that channel.
6. For portraits or avatars, use `profile-photo-system.md` and its exact color combinations.
7. Export at the requested pixel dimensions and inspect at 100% plus a typical feed/profile size.

Core Kunumi and Unlimited work should stay restrained. Instituto may use the expressive supplied gradients, waves, pixels, bars, kaleidoscope, gamma map, or motion when the institutional/scientific context supports it.

## Motion, GIF, and Video

Query before choosing:

```bash
python scripts/kunumi_lookup.py assets --identity instituto --motion
python scripts/kunumi_lookup.py assets --identity instituto --motion --tag gamma-wave
```

- GIF: simple embedded loops and channels that require GIF.
- MP4: efficient playback in presentations, web, and video.
- MOV: preserve when alpha or editing quality is required.
- Keep source duration, proportions, frame rate, transparency, and loop behavior unless the output specification requires conversion.
- Use the Ksequence-derived motion grammar for staged diagrams and interaction; use supplied motion files when an exact background is needed.
- Place text in a region that remains calm and high-contrast for the complete loop.
- Use restrained motion: one branded background or transition is usually enough.
- Provide a poster or approved static-family fallback when autoplay or animation is unavailable.
- Do not turn a random frame into a new canonical asset or rebuild motion from sampled colors.

Preview the full loop, not only its opening frame. Check flashes, seams, crop changes, compression, file size, text legibility, and reduced-motion behavior.

## Delivery Gate

Verify identity, exact asset, logo variant and clear space, color values, type hierarchy (family,
case, tracking, line height), two-by-two grid, contrast, text fit, output dimensions, source notes, accessibility, and placeholder removal. For motion, inspect every phase of the loop; for multi-page or multi-slide work, inspect every page or slide.
