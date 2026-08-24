<img src="assets/kunumi-icon-urucum.png" alt="Kunumi" width="200">

# Kosmos Design System

Claude Code plugin that ships a single skill, [`kosmos-design-system`](skills/kosmos-design-system/SKILL.md),
for designing and reviewing artifacts in the approved Kunumi, Instituto Kunumi, and Kunumi
Unlimited visual **and verbal** systems — web and UI, slides, charts, social assets, and copy.

Authority is the **Brandbook Kunumi Final (2025)**; colors and type were read from that file's own
design variables. Local-first: every approved asset the skill uses is bundled in the repository, so
it works with no network and no Figma access.

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
      tokens.json             # single source of truth for color and type
      brand-foundations.md    # always read; identity, color, composition
      typography.md           # the two-family type system
      logo-governance.md      # clear space, minimum size, co-branding, misuse
      brand-voice.md          # messages, tone axes, DOs/DON'Ts, naming
      visual-behavior.md      # brand architecture, formats, Versus symbol
    scripts/                  # kunumi_lookup.py and the index builder
    assets/local/             # marks, Figtree, Space Grotesk, Instituto artwork
    assets/web/               # CSS tokens and animated template preview
scripts/
  validate-skills.py          # frontmatter, reference links, token consistency
  build_bundle.py             # self-contained bundle for publishing
```

`skills/` at the plugin root is auto-discovered by Claude Code — the manifest carries no skill path.

## What Works Offline

- approved marks;
- Figtree (body) and Space Grotesk (display);
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

**PP Neue Machina Inktrap**, the brandbook's first-choice display face, is commercial software from
Pangram Pangram and is not redistributed here. Space Grotesk — the alternate the brandbook itself
names — is bundled under the SIL OFL and is the offline default. If PP Neue Machina is licensed and
installed locally, the CSS display stack picks it up automatically.

Two chapters of the brandbook, the Instituto and Colab deep dives, were not reachable through the
Figma MCP page enumeration and are therefore not extracted. **Kunumi Colab** consequently has a
documented name but no documented mark; the skill asks rather than inventing one.

## Install

Pick one of the two routes below — installing both leaves two copies of the same skill competing
to trigger.

### Local development

Symlink the **skill package**, not the repository root, so the personal skill directory contains
`SKILL.md` directly:

```bash
ln -s "$PWD/skills/kosmos-design-system" ~/.claude/skills/kosmos-design-system
```

The link points at the working tree, so edits take effect in the next session with no reinstall.
Verify the link resolves:

```bash
ls -l ~/.claude/skills/kosmos-design-system/SKILL.md
```

### Shareable install

```bash
claude plugin marketplace add .
claude plugin install kosmos-design-system@kosmos-design-system
```

This route copies the plugin into `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, so
it captures a snapshot: later edits to the repository do not appear until the version is bumped and
the plugin reinstalled. Prefer the symlink while developing the skill. Verify with:

```bash
claude plugin details kosmos-design-system
```

`claude plugin details` only knows about plugins — it reports "not found" for a symlinked personal
skill even when that skill is installed and working.

Start a new session after either route so the skill is discovered.

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

The primary brand accent is Urucum `#F04E44`. Chumbo `#1C2127` and Gelo `#F0F0F0` replace black
and white, which the brandbook prohibits as brand colors. Titles are set in the display face,
**always uppercase**, tracked **+3%**; body is Figtree at 140–175% line height.

`references/tokens.json` is the single source of truth. `assets/web/kunumi-tokens.css` mirrors it
for web work, and `validate-skills.py` fails the build if the two drift.

## Standalone Bundle

Build a self-contained copy outside the repository when publishing or sharing:

```bash
python scripts/build_bundle.py --bundle-dir /tmp/kosmos-design-system-plugin
```

Repository metadata is excluded.

## Development Workflow

- Keep `SKILL.md` short and procedural; put standards, schemas, and examples in `references/`.
- Edit `references/tokens.json` first when a token changes, then mirror it into
  `assets/web/kunumi-tokens.css` and `references/brand-foundations.md`.
- Run `python scripts/validate-skills.py` before opening or merging a branch. It checks frontmatter,
  that every `references/` path named in `SKILL.md` exists, and that the token layer is consistent
  and free of prohibited colors.
- Use short-lived branches, Conventional Commits in English, and squash merges into `main`.
