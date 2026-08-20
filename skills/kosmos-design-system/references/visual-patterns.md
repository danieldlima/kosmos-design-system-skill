# Kunumi Global Visual Patterns

These patterns were extracted from all 36 rendered slides, transitions, and key interactive states in `presentation-ksequence-cambio`. They extend the visual vocabulary; they do not replace `brand-foundations.md` or authorize Ksequence product claims, personal imagery, third-party motifs, or new logos.

**This is a deck-derived expressive layer, subordinate to the 2025 brandbook.** Its dark canvases
and expressive ramp are product-storytelling devices, not brand colors, and none of them are in
`tokens.json`. Where this file and the brandbook disagree, the brandbook wins.

## Contents

- [Find a Pattern](#find-a-pattern)
- [Global Visual Layer](#global-visual-layer)
- [Pattern Families](#pattern-families)
- [Reusable Assets](#reusable-assets)
- [Motion Grammar](#motion-grammar)
- [What Stays Local](#what-stays-local)
- [Review Gate](#review-gate)

## Find a Pattern

Query the compact registry instead of loading the reference deck:

```bash
python scripts/kunumi_lookup.py patterns --medium slides
python scripts/kunumi_lookup.py patterns --tag data-viz
python scripts/kunumi_lookup.py patterns --mode dark --tag process
python scripts/kunumi_lookup.py patterns --search "team portrait"
```

Results provide the original slide numbers, narrative purpose, construction recipe, and motion behavior. Load `visual-pattern-index.json` only when machine-readable output is required.

## Global Visual Layer

Use these Ksequence-derived values as an expressive layer, not as replacements for the canonical brand palette.

| Role | Exact value | Use |
| --- | --- | --- |
| Deep canvas | `#050609` | Cinematic dark backgrounds |
| Dark slide | `#090A0D` | Default expressive dark page |
| Dark panel | `#111216` | Bounded diagrams, demos, and data fields |
| Dark border | `#2A2B31` | Hairlines and panel separation |
| Warm light canvas | `#F3F2EE` | Editorial light pages |
| Light ink | `#101115` | Text on warm light pages |
| Dark text | `#F7F6F2` | Main text on dark pages |
| Dark muted | `#A8A9B1` | Supporting copy and metadata |
| Expressive orange | `#FF6A3D` | Middle of the technology/storytelling ramp |
| Expressive violet | `#7765DF` | Secondary technology/storytelling accent |

Preferred expressive ramp:

```text
#F04E44 → #FF6A3D → #7765DF
```

Use the ramp for thin progress rails, connectors, one highlighted word, data-flow paths, and restrained peripheral glows. Do not apply it to every object or redefine primary brand colors.

Useful gradient recipes:

- Accent rail: `linear-gradient(90deg, #F04E44, #FF6A3D, #7765DF)`.
- Technology title: `linear-gradient(90deg, #FF5D4D, #FF875D 58%, #9C84FF)`.
- Dark ambient glow: Urucum at the lower or outer edge, violet farther inward, then transparent.
- Photo shade: near-black at the text edge, falling to 20–35% opacity across the image.
- Subtle dark grid: 1 px white at 3.5% opacity every 44–68 px; mask it toward the focal area.
- Subtle light grid: 1 px Chumbo at 2.5–4% opacity every 32–44 px.

Typography follows `typography.md`, not this file: the display face uppercase for titles, Figtree
for body. This deck predates the 2025 brandbook and sets its own titles in Figtree — do not copy
that as a rule.

The deck also uses **DM Mono** as a technical secondary voice for eyebrows, slide numbers, units,
source notes, navigation, and terminal moments. DM Mono is **deck-local and not bundled**, and the
brandbook does not name it. Use it only when already available and only inside Ksequence-style
work; otherwise use a neutral monospace fallback without downloading a font.

## Pattern Families

### Narrative and identity

- `dark-hero-orbit`: oversized claim left, luminous object right, thin orbital lines, peripheral glow.
- `typed-interlude`: one short monospaced sentence in a generous light terminal window; use as a chapter reset.
- `people-orbit`: circular portraits around a central mark or one large portrait inside orbit lines.
- `cinematic-photo-chapter`: full-bleed photo, directional dark overlay, short claim, small metadata.
- `editorial-gallery`: either one composed collage or a clean asymmetric gallery; never both at once.
- `story-wall`: a small set of paper fragments with restrained rotation and one clear primary story.

### Systems and explanations

- `dual-pillar`: two equal dark fields with accent rails and one simple diagram per field.
- `lineage-branching`: one origin left, division core center, aligned destinations right.
- `light-operating-system`: warm light canvas, rows, hairlines, compact diagrams, and direct labels.
- `parallel-sequences`: two aligned rails that share visual grammar and converge on an outcome.
- `before-after-system`: fragmented current state, small transformation engine, coherent future state.
- `case-board`: known evidence in sequence, bounded choices, and a separate response or hypothesis area.

### Data and capability

- `cosmic-scale-map`: area encodes magnitude; color encodes family; a visible scale explains the mapping.
- `claim-demo-split`: claim in the left third, reusable scenario frame in the right two-thirds.
- `results-comparison`: conclusion-first title, disciplined table or bubble matrix, winner highlighted once.
- `process-orbit`: milestones above, one large iterative loop, separate maturity/version rail below.
- `capability-triptych`: three equal capability scenes, then one full-width integration band.

Do not combine more than two major pattern families on one page or slide.

## Reusable Assets

**None of these files are bundled.** They exist only in the source deck. Ask the user to supply
the approved file and cache it outside the repository; do not recreate the artwork.

| Asset (not bundled) | Use |
| --- | --- |
| `habits-background-art.png` | Transparent 2×2 atlas for collaboration, organic evolution, multidimensional work, and hub-and-spoke principles |
| `capability-background-art.png` | Transparent 2×2 atlas for speed, zero-shot/reuse, sequence, and integration capability scenes |
| `kunumi-dark-gradient.gif` | 1280×800, 12-frame, 1.2-second dark Urucum-violet ambient loop |

For either atlas, crop one quadrant using a 2×2 background grid; do not display all four quadrants as one graphic unless creating a deliberate four-principle overview. On dark surfaces, use screen-like blending or increased brightness only when the exact medium supports it and labels remain legible.

Use the gradient GIF behind concise light copy or as a transition. Provide a static fallback, keep text away from the most active color boundary, and do not treat a random frame as a new canonical asset.

## Motion Grammar

- Default page entry: 550 ms, small right-to-left travel, ease-out.
- Micro-reveal: 400–700 ms with 70–150 ms stagger in reading order.
- Token or process sequence: reveal nodes first, draw connectors second, show result last.
- Ambient object float: 4–7 seconds, movement under 14 px, no essential meaning.
- Large orbit: 9–16 seconds for an active runner; 24–46 seconds for background rings.
- Scenario change: 350–500 ms; animate only the content that changed.
- Typewriter interlude: 42 ms per character with a deliberate pause after the opening phrase.
- High-impact chapter transition: use at most once in a short narrative section and always provide a reduced-motion fade.

Every continuous animation must tolerate `prefers-reduced-motion`: stop loops, resolve entry states immediately, and replace cinematic transitions with a short fade.

## What Stays Local

Do not globalize:

- the Ksequence cube, model names, credit examples, metrics, or product claims;
- personal photos, names, biographies, family galleries, or travel media;
- Orkut, Matrix/terminal-cinema, Backrooms, fandom, or scrapbook treatments as default Kunumi styling;
- third-party logos, screenshots, community imagery, or event-specific QR codes;
- green terminal palettes, beige evidence-board palettes, or other story-specific colors as brand tokens.

These may still be used when a new artifact explicitly calls for that narrative world and the underlying assets and rights are available.

## Review Gate

Confirm the pattern serves the content, the canonical brand tokens still lead, the expressive ramp is selective, essential information is static and legible, scale encodings are explained, copied assets are uncropped safely, interaction has a non-interactive equivalent, and reduced-motion behavior is present. Inspect the complete animation and every interactive state used in the deliverable.
