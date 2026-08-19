# Kunumi Identity Design Plugin

Local-first Codex plugin for the Kunumi, Instituto Kunumi, and Kunumi Unlimited visual systems.

## What Works Offline

- approved marks;
- Figtree;
- Instituto static artwork and lightweight motion;
- compact 20-slide Kunumi and Instituto source decks;
- CSS tokens and the animated HTML template preview;
- semantic source lookup.

Google Drive is an optional app connection for canonical full decks, heavy media, channel guides, portraits, historical/client material, and the 2025 report.

## Local Install

From this repository:

```bash
codex plugin marketplace add /absolute/path/to/agent-skills
codex plugin add kunumi-identity-design@personal
```

Start a new Codex task after installation so the skill and optional app are discovered.

## Development Link

The plugin-owned skill under
`plugins/kunumi-identity-design/skills/kunumi-identity-design/` is the single editable source.
The repository entry at `skills/kunumi-identity-design/` points to it with a relative symlink,
so the plugin remains self-contained without duplicating brand assets and templates.

```bash
python plugins/kunumi-identity-design/scripts/sync_from_skill.py
python /path/to/plugin-creator/scripts/update_plugin_cachebuster.py plugins/kunumi-identity-design
codex plugin add kunumi-identity-design@personal
```

The first command verifies or repairs the repository skill link. Start a new Codex task after
reinstalling so the updated skill and app declaration are discovered.

## Standalone Bundle

Build a self-contained plugin outside the repository when publishing or sharing:

```bash
python plugins/kunumi-identity-design/scripts/sync_from_skill.py \
  --bundle-dir /tmp/kunumi-identity-design-plugin
```

The standalone bundle includes only the local-first assets, web preview, instructions,
references, and runtime scripts. Raw Drive exports remain excluded.
