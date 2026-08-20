# Kunumi and Instituto Slide Layouts

The canonical Kunumi deck contains 76 slides and the canonical Instituto deck contains 75 slides, both at 1920×1080 (16:9). Use either as a source deck: duplicate the closest source slide and edit inherited elements. Do not rebuild layouts from screenshots or approximate their brand furniture.

No source deck is bundled. Ask the user for the approved Kunumi or Instituto deck before building slides, then duplicate the closest source slide from it.

This reference catalogs every source layout, so use it to identify the exact slide you need and to specify the work before a deck is supplied. Do not rebuild a missing layout from this description alone.

## Contents

- [Fast Selection](#fast-selection)
- [Source-Slide Catalog](#source-slide-catalog)
- [Build Contract](#build-contract)
- [Slide QA](#slide-qa)

## Fast Selection

Query the semantic registry instead of opening all 76 slides:

```bash
python scripts/kunumi_lookup.py slides --search "title cover"
python scripts/kunumi_lookup.py slides --tag chart
python scripts/kunumi_lookup.py slides --tag photo --mode dark
python scripts/kunumi_lookup.py slides --role content-matrix
python scripts/kunumi_lookup.py slides --search "timeline roadmap"
```

The compact result returns source slide, mode, purpose, and content slots. `slide-index.json` catalogs the 76-slide Kunumi deck; the Instituto deck follows the same core sequence but begins with its dedicated gradient template cover and ends at slide 75. Use `template-design-system.md` for cross-system differences.

Selection order:

1. Match the narrative job.
2. Match the content slots and density.
3. Match light, dark, split, or supplied-gradient mode.
4. Prefer the simplest fitting layout.
5. Shorten copy or choose another source slide before shrinking type.

Slides 1–6 are template instructions and extracted design references. In the canonical Kunumi deck, slides 68–76 are brand/resource references; in the Instituto deck they run 68–75. Preserve them unless the deliverable explicitly needs a reference appendix.

## Source-Slide Catalog

### Setup, covers, and navigation

| Slides | Pattern |
| --- | --- |
| 1–2 | Template cover and editing instructions |
| 3 | Three-identity architecture comparison |
| 4–5 | Layout and two-by-two grid guidance |
| 6 | Complete color system |
| 7 | Minimal light title cover |
| 8 | Light agenda |
| 9 | Instituto gamma-wave title cover |
| 10 | Dark stepped-pixel title cover |
| 11 / 54 | Light / dark section progress |
| 53 | Dark agenda |
| 67 | Instituto gradient closing |

### Text and editorial stories

| Light | Dark | Pattern |
| --- | --- | --- |
| 12 | 55 | Keyword plus body |
| 13 | 56 | Short title plus two body columns |
| 14 | 57 | Headline plus three evidence columns |
| 15 | 58 | Identity story around a central symbol |
| 16 | 59 | Text left, square image right |
| 17–18 | 60–61 | Large image left, text right |
| 19 | — | Instituto gradient panel left, text right |
| 20 | — | Black panel left, text right |
| 21 / 24 | — | Light texture plus text, mirrored |
| 22 | — | Text plus palette bars |
| 23 | — | Text plus pixels |
| 25 | — | Text plus wide horizontal image |
| 31 | — | Full-slide light texture with small copy |
| 32 | — | Full-slide photo with overlay copy |
| 33 | 34 | Light / gradient centered quote |
| — | 62 | Dark image-led institutional story |

### Media and comparisons

| Slides | Pattern |
| --- | --- |
| 26 | Narrative plus one hero and two supporting images |
| 27 | Captioned hero and two thumbnails |
| 28–29 | Two-by-three media grids with captions |
| 30 | Four-up visual comparison |
| 37 / 39 | Brazil / South America map plus narrative |
| 38 / 40 | Regional map plus a two-item media rail |
| 41 | World map with a highlighted region |

### Data, process, and tables

| Slides | Pattern |
| --- | --- |
| 35 / 63 | Three big numbers, light / dark |
| 36 / 64 | Two big numbers with emphasis, light / dark |
| 42 | Imported chart with explanatory text and source note |
| 43 | Native donut chart with labels |
| 44 | Two-phase timeline |
| 45 | Month-by-month roadmap |
| 46 | Multi-stage process columns |
| 47 | Branching node-and-connector flow |
| 48 | Multiyear Gantt |
| 49 | Comparison or requirements matrix |
| 50 | Numeric table with confidence and status |
| 51–52 | Light content matrices; slide 52 adds highlighted rows |
| 65–66 | Dark content matrices; slide 66 supports grouped dense rows |

### Brand and asset references

| Slides | Reference |
| --- | --- |
| 68–69 | Positive/negative complete mark and icon signatures |
| 70–71 | Brand-symbol variants on light/dark |
| 72 | Status and navigation icon sets |
| 73 | Full Kunumi graphic composition |
| 74 | Static Instituto background previews |
| 75–76 | Instituto GIF families |

## Build Contract

1. Use the presentation skill’s template-following workflow.
2. Inspect the chosen source slide at full size.
3. Duplicate the source slide; preserve master → layout → slide inheritance.
4. Edit identified inherited placeholders and media frames. Do not add an unrelated overlay composition.
5. Keep the source element's font family, size, weight, line spacing, text insets, alignment, and vertical anchoring. Do not restyle inherited type to the newer display face mid-deck.
6. Preserve header/footer brand furniture, page markers, grid, asset proportions, and source-slide contrast mode.
7. Use source slide 42 for external raster/vector charts and source slide 43 for native simple charts. Apply `medium-playbooks.md` chart rules.
8. Use exact supplied Instituto backgrounds and motion assets. Do not rebuild them from sampled colors.
9. Use `visual-patterns.md` for narrative logic, diagrams, and motion inside suitable inherited slots; it does not authorize replacing the source layout or brand furniture.
10. Add source notes for external visuals and non-trivial claims.

## Slide QA

- Render and inspect every output slide, not only a montage.
- Check title hierarchy, text fit, image crop, chart labels, table density, contrast, margins, and repeated spacing.
- Confirm no empty inherited placeholders or default prompts remain.
- Confirm required logos and footer elements survived export.
- Confirm adjacent slides vary appropriately without mixing unrelated visual systems.
- Check essential copy across every frame of animated backgrounds.
