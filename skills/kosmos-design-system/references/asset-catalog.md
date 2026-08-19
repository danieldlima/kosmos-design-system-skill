# Kunumi Asset Catalog

Use approved files from the local-first bundle or the exact Drive objects in `semantic-index.json`; keep source files unchanged. Query the indexes rather than loading them wholesale.

## Find an Asset

Run the compact query tool from the skill directory:

```bash
python scripts/kunumi_lookup.py assets --identity core --kind wordmark
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py resolve "Kunumi positive wordmark"
python scripts/kunumi_lookup.py sources --access drive --kind motion
python scripts/kunumi_lookup.py sources --search "linkedin"
```

Prefer the returned local path. Use the recorded Drive ID when the source is remote-only or canonical full fidelity is required.

## Preferred Identity Assets

| Need | Source |
| --- | --- |
| Core wordmark on light | `assets/local/brand-marks/core/kunumi_logotipo_positivo_rgb.png` |
| Core wordmark on dark | `assets/local/brand-marks/core/kunumi_logotipo_negativo_rgb.png` |
| Shared icon on light | `assets/local/brand-marks/shared/kunumi_icone_positivo_rgb.png` |
| Shared icon on dark | `assets/local/brand-marks/shared/kunumi_icone_negativo_rgb.png` |
| Unlimited lockup on light | `assets/local/brand-marks/unlimited/kunumi_unltd_positivo_rgb.png` |
| Unlimited lockup on dark | `assets/local/brand-marks/unlimited/kunumi_unltd_negativo_rgb.png` |
| Instituto full lockup on light | `assets/local/brand-marks/instituto/kunumi_inst_positivo_rgb.svg` |
| Instituto full lockup on dark | `assets/local/brand-marks/instituto/kunumi_inst_negativo_rgb.svg` |
| Instituto wordmark only | `assets/local/brand-marks/instituto/` |

`positivo` means Chumbo for core/icon/Instituto and Urucum for Unlimited. `negativo` means Gelo. Preview transparent art on the intended ground.

## Instituto Static Families

All paths are under `assets/local/instituto/static/`.

| Family | Files | Use |
| --- | --- | --- |
| Horizontal gradients | `kunuminst_assets_gradiente_01.png`, `_02.png` | Wide covers and heroes |
| Gradient fields | `kunuminst_gradiente_01.png` through `_04.png` | Full-bleed covers and atmospheric panels |
| Gamma waves | `kunuminst_assets_ondas_gama_01.png` through `_04.png` | Section openers and data/science storytelling |
| Bars | `kunuminst_assets_barras.png` | Structured stripes or transitions |
| Pixels | `kunuminst_assets_pixels.png` | Digital and computational stories |
| Kaleidoscope | `kunuminst_assets_kaleido.png` | High-energy institutional moments |
| Gamma map | `kunuminst_assets_mapa_gama.png` | Scientific or research-led stories |

Place essential text in calm, high-contrast regions. Do not reconstruct, recolor, or generalize these backgrounds.

## Motion Selector

- Use the three local lightweight GIFs for simple embedded loops.
- Fetch MP4 from Drive for efficient web, presentation, or video playback.
- Fetch the high-quality MOV source when alpha or editing quality matters.
- Fetch `kunuminst_gradiente_marca_small.gif`, `_medium.gif`, or `_large.gif` only when square symbol-led motion is required; medium and large are deliberately Drive-only.
- Use the portrait photographic GIF only when its actual subject fits the story.
- Do not capture a random motion frame as a new canonical asset. If motion is unsupported, choose the closest approved static family without claiming a frame-for-frame match.

## Channel Sources

- LinkedIn header: `assets/local/channels/linkedin/[modelo]Cabeçalho_Linkedin-kunumi.png` — use as supplied.
- Profile-photo mark: `assets/local/channels/profile/marca.png` — specialized near-Urucum export; use only with `profile-photo-system.md`.
- Slide templates: `assets/local/templates/` — preserve and duplicate source slides; resolve canonical full decks through `semantic-index.json`.
- Slack guide: use only as a document-design reference; do not copy its operational policy.
- Profile-photo guide: authoritative for the profile-photo workflow.

## Conversion Rules

- Keep SVG as SVG where supported.
- Preserve PNG transparency.
- Copy only assets required by the deliverable; do not duplicate the motion library.
- Keep raw Drive exports and canonical full decks out of Git unless the user explicitly changes the local-bundle policy.
- Never rename, recompress, convert, crop, or adapt a source unless the output medium requires it.
