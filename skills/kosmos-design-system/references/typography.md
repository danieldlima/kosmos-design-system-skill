# Kunumi Typography

Authority: **Brandbook Kunumi Final (2025)**, typography chapter. Values below were read from
the brandbook's own Figma variables, not inferred. Exact tokens live in `tokens.json`.

This supersedes any earlier instruction to set Kunumi work entirely in Figtree.

## Two Families, Two Jobs

> "As tipografias PP Neue Machina ou Space Grotesk são utilizadas exclusivamente como fontes de
> título, assumindo o papel de destaque visual. Já a Figtree é aplicada como fonte de corpo de
> texto e subtítulos."

| Role | Family | Case | Tracking |
| --- | --- | --- | --- |
| Titles and display | **PP Neue Machina Inktrap**, or **Space Grotesk** | **Always uppercase** | **+3%** |
| Body, subtitles, lists | **Figtree** | Sentence case | **0%** |

Never set body copy in the display face. Never set a title in lowercase. Never typeset a
substitute logo in either family.

### Availability and fallback

PP Neue Machina is a **commercial face from Pangram Pangram** and is not bundled. Space Grotesk
(SIL OFL) is bundled at `assets/local/fonts/SpaceGrotesk/`. Figtree (SIL OFL) is bundled at
`assets/local/fonts/Figtree/`.

Resolve the display face in this order:

1. **PP Neue Machina Inktrap** — only if licensed and already present on the system, or if the
   user supplies a local path. Do not download it.
2. **Space Grotesk** — the brandbook's own stated alternate. This is the offline default.
3. **Figtree SemiBold, uppercase** — last resort. State the substitution in your delivery note.

Arial is a body fallback only. Never use Arial for display.

## Exact Type Variables

Sizes are the brandbook's own values at the 1920×1080 stage. `letterSpacing` is a **percentage**
of the font size — the brandbook stores `3` for the display face, which renders as `0.66px` at
22px, confirming percent rather than pixels.

| Variable | Family / style | Size | Line height | Tracking | Case |
| --- | --- | --- | --- | --- | --- |
| `Abertura/Título` | PP Neue Machina Inktrap Semibold | 180 | 1.1 | +3% | upper |
| `Abertura/Categoria` | PP Neue Machina Inktrap Semibold | 35 | 1.2 | +3% | upper |
| `Miolo/Título` | PP Neue Machina Inktrap Medium | 22 | 34 px | +3% | upper |
| `Cabecalho/Menu` | PP Neue Machina Inktrap Medium | 13 | 1.1 | **+10%** | upper |
| `Miolo/Texto` | Figtree Light | 20 | 1.75 | 0 | none |
| `Miolo/TextoMenorSubtitulo` | Figtree SemiBold | 21 | 1.1 | 0 | none |
| `Miolo/TextoMenor` | Figtree Regular | 18.5 | 1.6 | 0 | none |
| `Lista/Tópico` | Figtree Regular | 20 | 1.0 | 0 | none |

The canonical body block — the brandbook's `Template/Texto` component — is a **360 px** column:
`Miolo/Título` uppercase, then a **60 px** gap, then `Miolo/Texto`.

## Scale and Rhythm

The brandbook expresses scale as ratios against a grid unit rather than a fixed point list.

| Level | Ratio |
| --- | --- |
| Title | **5x – 7.5x** |
| Subtitle | **1.2x – 1.6x** |
| Lead | **1.1x** |
| Body | **x** |

A title occupies **2y** of grid height, where `y` is the grid unit.

Line-height ranges, by level:

| Level | Range |
| --- | --- |
| Display | 110% – 140% |
| Subtitle | 110% – 120% |
| Body | **140% – 175%** |

Body text is generously leaded. Do not tighten it to fit — cut copy instead.

## Emphasis Inside a Sentence

> "Para destacar conteúdos em uma frase, utilize a ferramenta de highlight na cor chumbo ou
> urucum. A cor da tipografia deve acompanhar o fundo. Seu uso deve ser dosado e pontual, evite
> marcar muitas palavras em uma mesma frase. Ele não deve ser aplicado em títulos."

- Highlight color: **Chumbo `#1C2127`** or **Urucum `#F04E44`** only.
- The text color follows the ground it now sits on, so it stays legible inside the highlight.
- Sparing and pointed. Not several words in one sentence.
- **Never on a title.**

In Figma the brandbook builds this with the underline tool, since Figma has no highlight
primitive: apply underline, then set `Thickness: 120%`, `Offset: -100%`, `Skip ink: Off`, and a
custom color with transparency. On the web, use a real background on an inline span.

## Applying This on the Web

`assets/web/kunumi-tokens.css` carries these values as custom properties:
`--kunumi-font-display`, `--kunumi-font`, the `--kunumi-text-*` size ramp, and the matching
tracking and line-height tokens. Prefer the tokens over literal values.

Because the display face is tracked **positive** and set uppercase, never carry over the tight
negative tracking common in display type. Any earlier Kunumi CSS using a negative
`letter-spacing` on a display heading is wrong against this brandbook.

## Gate

- Titles uppercase, in the display face, tracked +3%.
- Body in Figtree at 140–175% line height, tracking 0.
- No Arial in display.
- If the display face fell back past Space Grotesk, say so on delivery.
- Render and read at delivery size before shipping.
