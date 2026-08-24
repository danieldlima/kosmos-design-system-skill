# Kunumi Brand Foundations

Authority: **Brandbook Kunumi Final (2025)**. Read this file for any Kunumi artifact, then load
only the chapter files the task needs.

Colors, typography, and logo rules here were read from the brandbook's own Figma variables and
pages. Machine-readable values live in `tokens.json`. Original assets and channel templates remain
authoritative when their rules are narrower.

## Identity Router

| Identity | Audience | Typical work |
| --- | --- | --- |
| **Kunumi** (core) | Internal; occasionally the bank's board | Company-wide comms, collaborator events, câmbio, welcome kit |
| **Kunumi Unlimited** | External: Bradesco. Internal: Bradesco matters | Bradesco presentations, actions, events, stationery, dashboards, reports |
| **Instituto Kunumi** | External; internal Instituto initiatives | Academic events, research and content materials |

**Kunumi Colab** is a valid brand *name* with no documented mark or system. See
`visual-behavior.md` before touching anything Colab-branded.

Do not mix lockups or expressive systems unless the user explicitly requests co-branding.

## Color

### Institutional palette — PALETA PRINCIPAL

> "A identidade visual da Kunumi Unlimited possui uma paleta de cores utilizada nos layouts e em
> aplicações sobre suportes diversos. Esses tons devem ser usados de forma sólida em textos,
> fundos e recursos gráficos básicos."

| Token | Hex | RGB | CMYK | Pantone C | Pantone U | Role |
| --- | --- | --- | --- | --- | --- | --- |
| **Urucum** | `#F04E44` | 240 78 68 | 0 85 76 0 | 2034 C | 2034 U | Accent, emphasis, CTAs, Unlimited positive lockup |
| **Chumbo** | `#1C2127` | 28 33 39 | 78 69 59 70 | 426 C | BLACK 6 U | Main text, dark ground, positive marks |
| **Grafite** | `#5E5E5E` | 94 94 94 | 62 53 53 25 | COOL GRAY 9 C | COOL GRAY 9 U | Secondary text |
| **Concreto** | `#B4ADA4` | 180 173 164 | 31 27 33 0 | WARM GRAY 4 C | WARM GRAY 4 U | Rules, grids, inactive structure |
| **Gelo** | `#F0F0F0` | 240 240 240 | 4 3 3 0 | 30% COOL GRAY 1 C + 70% WHITE | 30% COOL GRAY 1 U + 70% WHITE | Main light ground, negative marks |

### Black and white are prohibited

> "As cores chumbo (#1C2127) e gelo (#F0F0F0) substituem o preto e o branco, que não devem ser
> utilizados."

Chumbo replaces black. Gelo replaces white. This applies to page grounds, body and display text,
graphic resources, rules, and chart ink.

**Two documented exceptions, and only two:**

- **White** — the brandbook's own card components sit a white surface on a Gelo ground. White is
  available *only* as an elevated surface on Gelo. Token: `--kunumi-surface-raised`.
- **Black** — `#000000` is the terminus of the Instituto signature gradient
  (`brandbook/instituto/cor`, slide 05). Token: `--kunumi-instituto-black`.

Neither is ever a page ground, a text color, or a brand color. `validate-skills.py` enforces both:
each may appear exactly once in `kunumi-tokens.css`, and only alongside its named token.

### Chart palette — PALETA PARA GRÁFICOS

> "Esta paleta foi desenvolvida exclusivamente para a representação de dados e utilização em
> gráficos e deve ser utilizada apenas nesse contexto. Ela abrange novas cores que funcionam como
> uma extensão controlada da identidade cromática da marca."

| `#4392D2` | `#2FB7CF` | `#62CCA3` | `#A0C068` | `#F0D449` |
| --- | --- | --- | --- | --- |
| blue | cyan | green | olive | yellow |

Data only. Never a UI accent, never a background, never a brand color. The brandbook prints only
the hex for these five — no name, RGB, CMYK, or Pantone exists, so do not invent one. Its own
example chart plots blue, cyan, yellow, green top-to-bottom, but does not state that as a rule.

This **supersedes** the older ten-step chart palette extracted from the 2026 decks. That set is
kept in `tokens.json` under `supersededChart` only for reading existing template charts.

### Instituto signature gradient — brandbook, not deck

`brandbook/instituto/cor` slide 05 defines the Instituto gradient as seven stops, measured as bands
of a 1918 px bar:

| Stop | Hex | Band | Centre |
| --- | --- | --- | --- |
| 1 | `#FF9516` | 200 | 5.2% |
| 2 | `#FF6330` | 200 | 15.6% |
| 3 | **`#F04E44`** | **542** | 35.0% |
| 4 | `#D73E5F` | 244 | 55.5% |
| 5 | `#9355A0` | 244 | 68.2% |
| 6 | `#5A61B6` | 244 | 80.9% |
| 7 | `#000000` | 244 | 93.6% |

The ramp is **urucum-dominant** — Urucum alone is 28% of the bar, nearly triple any other stop. It
is not seven equal steps, and it is **not a general-purpose accent palette**: it belongs to Instituto
Kunumi, and core Kunumi and Unlimited stay restrained. Ready-made as
`--kunumi-gradient-gamma-ray`.

Five of these hexes were previously filed as deck-derived. They are brandbook. `#FF931E` (amarelo)
and `#F26638` (laranja) really are deck-only and remain so.

### Deck-derived colors

The deck support palette — `#FF931E` (amarelo) and `#F26638` (laranja) — comes from the 2026
templates, **not** the brandbook. Use it only for fidelity inside template-based work, and never in
place of the institutional palette.

Near-Urucum values such as `#FF4A3D` and `#FF4B3E` belong to specific exported files. Preserve
them in place; never replace `#F04E44` globally. Instituto artwork carries its own gradients —
keep those inside the supplied artwork rather than rebuilding them.

## Typography — summary

Two families, two jobs. **PP Neue Machina Inktrap** or **Space Grotesk** for titles, **always
uppercase**, tracked **+3%**. **Figtree** for body and subtitles, tracking **0**, line height
**140–175%**.

PP Neue Machina is commercial and not bundled; Space Grotesk and Figtree are bundled. Full specs,
the exact variable table, the scale ratios, and the fallback order are in **`typography.md`** —
read it for any typographic decision.

## Logo — summary

Positive marks in Chumbo on light grounds; the Unlimited lockup positive is **Urucum**; negative
marks in Gelo on dark. Clear space is **1X**, where X is the symbol's square module. Minimum size
is **28 px / 10 mm** of lockup height. Reuse the supplied file — never redraw, recolor, restretch,
rearrange, or add to a mark.

Full governance, the co-branding rule, photo application, and the seven prohibitions are in
**`logo-governance.md`**.

## Composition

- Strong left-aligned hierarchy on a Gelo ground with generous empty space.
- Two-by-two grid: two major horizontal blocks, two major vertical blocks, then subdivide.
- Hairline rules and precise edge alignment over rounded-card UI chrome. When a card is genuinely
  warranted, the brandbook radius is **10 px**.
- One narrative job, one dominant message, one reading order per page, slide, or view.
- Urucum selectively as a reading accent, not an all-over fill.
- Client-facing work concise and polished; operational work dense but scannable; internal work
  warm and direct.

Avoid: invented gradients, pseudo-logos, generic neon "AI" styling, dashboards of pills and cards,
arbitrary rounded containers, unapproved colors.

## Copy and Claims

Voice, messages, tone axes, DOs and DON'Ts, gender-neutral language, and the exact brand-name
forms are in **`brand-voice.md`**. The essentials:

- Spell the organization `Kunumi`. Write **Kunumi Unlimited**, never "Kunumi Unltd".
- First person plural, active voice, casual but never irreverent.
- Do not invent a legal name, tagline, slogan, certification, customer or performance claim,
  product promise, or a relationship between the identities.
- Do not carry Slack policy, support channels, or dated product references into unrelated work.

## Final Gate

Verify identity choice, source asset, contrast variant, proportions, clear space, minimum size,
typography (family, case, tracking, line height), grid, spacing, text fit, image resolution,
motion-loop legibility, links, alt text, and placeholder removal.

Render the artifact and inspect **every** page, slide, frame, loop, breakpoint, or export at
delivery size before calling it done.
