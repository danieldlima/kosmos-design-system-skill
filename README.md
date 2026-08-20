<img src="assets/kunumi-icon.png" alt="Kunumi" width="72">

# Kosmos Design System

Claude Code plugin that ships a single skill, [`kosmos-design-system`](skills/kosmos-design-system/SKILL.md),
for creating and reviewing artifacts in the approved Kunumi, Instituto Kunumi, and Kunumi Unlimited
visual systems. Local-first: every approved asset the skill uses is bundled in the repository.

## Layout

```text
.claude-plugin/
  plugin.json                 # plugin manifest
  marketplace.json            # single-plugin marketplace, source "./"
assets/                       # plugin icons
skills/
  kosmos-design-system/
    SKILL.md                  # routing instructions (required)
    references/               # brand standards, loaded only when relevant
    scripts/                  # kunumi_lookup.py and the index builder
    assets/local/             # marks, Figtree, Instituto artwork
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
- CSS tokens and the animated HTML template preview;
- the extracted slide-layout, visual-pattern, and design-token references;
- semantic source lookup.

## Sources Not Bundled

Slide decks are not bundled. A Kunumi or Instituto source deck, heavy motion or video, a channel
guide, portraits, historical/client material, and the annual report are all outside the bundle.
When a task needs one, the skill asks for the approved file instead of substituting or
reconstructing it. `references/slide-layouts.md` still carries the full extracted layout system,
so the skill can specify slide work precisely before a deck is supplied.

## Install

Local development — symlink the repository into the skills directory so it auto-loads as
`kosmos-design-system@skills-dir`:

```bash
ln -s "$PWD" ~/.claude/skills/kosmos-design-system
```

Shareable install through the bundled marketplace:

```bash
claude plugin marketplace add .
claude plugin install kosmos-design-system@kosmos-design-system
```

Start a new session after installing so the skill is discovered. Verify with:

```bash
claude plugin details kosmos-design-system
```

## Use

Prompts that route to the skill:

- Create this artifact in the correct Kunumi identity using local assets first.
- Build a presentation from a supplied Kunumi or Instituto source deck.
- Find the approved logo, background, or channel template for this task.

Query the bundled indexes instead of reading them wholesale — run from the skill directory:

```bash
python scripts/kunumi_lookup.py tokens
python scripts/kunumi_lookup.py resolve "Instituto gradient"
python scripts/kunumi_lookup.py sources --identity instituto
python scripts/kunumi_lookup.py slides --tag chart
python scripts/kunumi_lookup.py patterns --medium slides --tag data-viz
```

The primary brand accent is Urucum `#F04E44`. Full tokens live in
`skills/kosmos-design-system/assets/web/kunumi-tokens.css` and
`references/brand-foundations.md`.

## Standalone Bundle

Build a self-contained copy outside the repository when publishing or sharing:

```bash
python scripts/build_bundle.py --bundle-dir /tmp/kosmos-design-system-plugin
```

Repository metadata is excluded.

## Development Workflow

- Keep `SKILL.md` short and procedural; put standards, schemas, and examples in `references/`.
- Run `python scripts/validate-skills.py` before opening or merging a branch.
- Use short-lived branches, Conventional Commits in English, and squash merges into `main`.
