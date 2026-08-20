# Kunumi Source Map

This is the human routing view of the approved Kunumi material bundled with the skill. Query
`semantic-index.json` through `scripts/kunumi_lookup.py`; do not load the JSON wholesale.

## Access Model

- **Local by default:** approved marks, Figtree, Instituto static backgrounds, three lightweight
  GIFs, LinkedIn/profile support files, and the CSS/HTML preview. All of it runs without
  authentication.
- **Ask when missing:** slide decks, heavy GIF/video, detailed channel guides, named-person
  portraits, historical/client templates, and the 2025 report are not bundled. Ask the user for
  the approved file instead of substituting or reconstructing it.
- Keep user-supplied working files in a temporary or user-designated cache. Do not add them to
  Git by default.

Resolve a source in one command:

```bash
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py sources --identity instituto
python scripts/kunumi_lookup.py sources --kind wordmark
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
└── channels/
    ├── linkedin/
    └── profile/

assets/web/
├── kunumi-tokens.css
├── template-preview.html
├── template-preview.png
└── template-preview-instituto.png
```

No slide deck is bundled. Ask the user for the approved Kunumi or Instituto source deck before
building slides, and use `references/slide-layouts.md` to identify the exact source layout to
duplicate.

## Resolution Procedure

1. Resolve the exact source with `kunumi_lookup.py`.
2. Use the returned `localPath`.
3. If nothing resolves, state which source is missing and ask the user to provide that file. Do
   not redraw, recolor, or synthesize a replacement.
4. Never search portraits broadly when the task names a person; ask for the named portrait only.
