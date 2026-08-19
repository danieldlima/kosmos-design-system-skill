# Kunumi Source Map

This is the human routing view of the `Kunumi - Id.espensa` Drive snapshot from 2026-07-29. Query `semantic-index.json` through `scripts/kunumi_lookup.py`; do not load the JSON wholesale.

## Access Model

- **Local by default:** approved marks, Figtree, Instituto static backgrounds, three lightweight GIFs, LinkedIn/profile support files, CSS/HTML preview, and compact Kunumi/Instituto slide editions.
- **Drive when needed:** canonical full decks, heavy GIF/video, detailed channel guides, named-person portraits, historical/client templates, and the 2025 report.
- The local files are execution-ready copies. The Drive object with the recorded ID remains canonical.
- Download Drive-only working files into a temporary or user-designated cache. Do not add them to Git by default.

Resolve a source in one command:

```bash
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py resolve "Kunumi slide template"
python scripts/kunumi_lookup.py sources --access drive --kind motion
python scripts/kunumi_lookup.py folders --search "profile portrait"
```

## Drive Roots

| Root | What belongs there | Snapshot |
| --- | --- | --- |
| `Ativos de Marca/` | Approved marks and the Instituto expressive system | 44 files · 376.3 MB |
| `Fonte/` | Figtree variable/static fonts, license, and readme; semantically part of Ativos de Marca | 19 files · 0.8 MB |
| `Templates/` | Canonical Kunumi, Instituto, Unlimited, Metamáquina, Keynote, and client-environment decks | 19 files · 787.5 MB |
| `Canais e Redes Sociais/` | Profile system, approved portraits, Slack guide, and LinkedIn assets | 29 files · 54.1 MB |
| `Relatório Kunumi 2025/` | Canonical 2025 annual-report PDF | 1 file · 32.8 MB |

## Folder Semantics

```text
Ativos de Marca/
├── Versus/                         shared icon signatures
├── Kunumi/                         core positive/negative wordmarks
├── Unlimited/                      Unlimited positive/negative marks
└── Instituto/
    ├── Instituto - Marca/
    │   ├── completa/               complete raster signatures
    │   │   └── svg/                complete vector signatures
    │   └── logotipo/               Instituto wordmarks
    └── Instituto - Imagens e Fundos/
        ├── Estáticos/              gradients, waves, pixels, bars, kaleidoscope, gamma map
        ├── GIFS/                   approved animated backgrounds and symbols
        └── Vídeos/                 high-resolution motion masters

Fonte/
└── Figtree/
    └── static/                     individual Figtree weights and italics

Templates/
├── Kunumi/                         canonical 76-slide deck, Metamáquina, Keynote
├── Instituto/                      canonical 75-slide Instituto deck
└── Unlimited/
    └── Ambiente Bradesco/          client-specific, not the general master

Canais e Redes Sociais/
├── Foto de Perfil Kunumi IA/
│   └── Kunumis Notáveis/           named-person portraits; fetch narrowly
└── LinkedIn/                       channel header/source files

Relatório Kunumi 2025/
└── Relatório Kunumi 2025.pdf
```

## Local Bundle

```text
assets/local/
├── brand-marks/
│   ├── core/
│   ├── instituto/
│   ├── unlimited/
│   └── shared/
├── fonts/Figtree/
├── instituto/
│   ├── static/
│   └── motion-lightweight/
├── channels/
│   ├── linkedin/
│   └── profile/
└── templates/
    ├── Kunumi-Agent-Template.pptx       20 representative source slides
    └── Instituto-Agent-Template.pptx    20 representative source slides

assets/web/
├── kunumi-tokens.css
├── template-preview.html
├── template-preview.png
└── template-preview-instituto.png
```

The agent editions preserve the supplied decks' inherited layouts and representative source
slides. Their approved animated closing-wave background is resolution-optimized for the local
bundle; fetch the canonical Drive deck when full-resolution source motion or an unrepresented
slide is required.

## Connection Procedure

1. Resolve the exact source with `kunumi_lookup.py`.
2. Use `localPath` if returned and the task does not require canonical full-deck fidelity.
3. If the result is Drive-only, use the Google Drive connector and fetch by the exact recorded `driveId`.
4. If Google Drive is unavailable, continue with the local fallback when one exists. Otherwise state which source is missing and ask the user to connect Drive or provide that file.
5. Never search portraits broadly when the task names a person; resolve the named folder/file only.
