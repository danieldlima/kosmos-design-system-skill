<img src="assets/kunumi-icon.png" alt="Kunumi" width="72">

# Kunumi Identity Design

Claude Code plugin that ships a single skill, [`kunumi-identity-design`](skills/kunumi-identity-design/SKILL.md),
for creating and reviewing artifacts in the approved Kunumi, Instituto Kunumi, and Kunumi Unlimited
visual systems. Local-first: approved assets are bundled, and Google Drive is optional.

## Layout

```text
.claude-plugin/
  plugin.json                 # plugin manifest
  marketplace.json            # single-plugin marketplace, source "./"
assets/                       # plugin icons
skills/
  kunumi-identity-design/
    SKILL.md                  # routing instructions (required)
    references/               # brand standards, loaded only when relevant
    scripts/                  # kunumi_lookup.py and index/template utilities
    assets/local/             # marks, Figtree, Instituto artwork, source decks
    assets/web/               # CSS tokens and animated template preview
scripts/
  validate-skills.py          # frontmatter and naming checks
  build_bundle.py             # self-contained bundle for publishing
```

`skills/` at the plugin root is auto-discovered by Claude Code — the manifest carries no skill path.

## What Works Offline

- approved marks;
- Figtree;
- Instituto static artwork and lightweight motion;
- compact 20-slide Kunumi and Instituto source decks;
- CSS tokens and the animated HTML template preview;
- semantic source lookup.

The two source decks under `skills/kunumi-identity-design/assets/local/templates/` are stored with
Git LFS. A clone without LFS leaves them as 133-byte pointer files:

```bash
git lfs install && git lfs pull
```

## Google Drive (Optional)

Drive is only needed for a canonical full deck, an unrepresented source slide, heavy motion or
video, a channel guide, portraits, historical/client material, or the annual report. The skill
records the exact Drive object IDs in `references/semantic-index.json`; fetch by ID and cache
outside the repository.

The Kunumi workspace Drive connector used for these sources is
`connector_5f3c8c41a1e54ad7a76272c89e2554fa`.

## Install

Local development — symlink the repository into the skills directory so it auto-loads as
`kunumi-identity-design@skills-dir`:

```bash
ln -s "$PWD" ~/.claude/skills/kunumi-identity-design
```

Shareable install through the bundled marketplace:

```bash
claude plugin marketplace add .
claude plugin install kunumi-identity-design@kunumi-identity-design
```

Start a new session after installing so the skill is discovered. Verify with:

```bash
claude plugin details kunumi-identity-design
```

## Use

Prompts that route to the skill:

- Create this artifact in the correct Kunumi identity using local assets first.
- Build a presentation from the Kunumi or Instituto source templates.
- Find the approved logo, background, or channel template for this task.

Query the bundled indexes instead of reading them wholesale — run from the skill directory:

```bash
python scripts/kunumi_lookup.py tokens
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py folders --search "profile portrait"
python scripts/kunumi_lookup.py sources --access drive --kind motion
python scripts/kunumi_lookup.py slides --tag chart
python scripts/kunumi_lookup.py patterns --medium slides --tag data-viz
```

The primary brand accent is Urucum `#F04E44`. Full tokens live in
`skills/kunumi-identity-design/assets/web/kunumi-tokens.css` and
`references/brand-foundations.md`.

## Standalone Bundle

Build a self-contained copy outside the repository when publishing or sharing:

```bash
python scripts/build_bundle.py --bundle-dir /tmp/kunumi-identity-design-plugin
```

Raw Drive exports, inspection artifacts, and repository metadata are excluded.

## Development Workflow

- Keep `SKILL.md` short and procedural; put standards, schemas, and examples in `references/`.
- Run `python scripts/validate-skills.py` before opening or merging a branch.
- Use short-lived branches, Conventional Commits in English, and squash merges into `main`.
