# Repository Instructions

This repository is a single-purpose Claude Code plugin holding one skill,
`skills/kosmos-design-system/`. Keep the skill package focused on instructions and resources an
agent needs at execution time.

The authority for Kunumi brand rules is the **Brandbook Kunumi Final (2025)**. Where the older
deck-derived references disagree with it, the brandbook wins, and the older material must be
labelled deck-derived rather than silently kept as a rule.

- Keep the skill at `skills/kosmos-design-system/` and keep `SKILL.md` present and authoritative.
- Keep frontmatter to `name` and `description`; the description must say when the skill should trigger.
- Keep `SKILL.md` short and procedural. Put detailed standards, schemas, examples, and brand rules in one-level-deep `references/` files.
- Put reusable deterministic utilities in `scripts/` and executable output resources in `assets/`.
- Do not invent Kunumi governance values, brand assets, policy IDs, ACLs, or legal names. Ask for approved source material when it is missing. `Kunumi Colab` is a documented name with no documented mark — do not design a mark or system for it.
- `references/tokens.json` is the single source of truth for color and typography. Change it first, then mirror into `assets/web/kunumi-tokens.css` and `references/brand-foundations.md`.
- Do not add PP Neue Machina to the repository. It is commercial software from Pangram Pangram; only OFL faces (Figtree, Space Grotesk) may be bundled.
- Treat the original templates and approved asset files as the source of truth; do not redraw, recolor, or substitute a mark.
- Run `python scripts/validate-skills.py` after changing the skill. It also verifies that every `references/` path named in `SKILL.md` exists and that the token layer stays consistent and free of prohibited colors.
- Run `python skills/kosmos-design-system/scripts/build_indices.py --check` after touching the slide or pattern indexes.
- Use Conventional Commits in English, branch-based development, and squash merges into `main`.
