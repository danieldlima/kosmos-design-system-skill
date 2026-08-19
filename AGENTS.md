# Repository Instructions

This repository is a single-purpose Claude Code plugin holding one skill,
`skills/kunumi-identity-design/`. Keep the skill package focused on instructions and resources an
agent needs at execution time.

- Keep the skill at `skills/kunumi-identity-design/` and keep `SKILL.md` present and authoritative.
- Keep frontmatter to `name` and `description`; the description must say when the skill should trigger.
- Keep `SKILL.md` short and procedural. Put detailed standards, schemas, examples, and brand rules in one-level-deep `references/` files.
- Put reusable deterministic utilities in `scripts/` and executable output resources in `assets/`.
- Do not invent Kunumi governance values, brand assets, policy IDs, ACLs, or legal names. Ask for approved source material when it is missing.
- Treat the original templates and approved asset files as the source of truth; do not redraw, recolor, or substitute a mark.
- Run `python scripts/validate-skills.py` after changing the skill.
- Use Conventional Commits in English, branch-based development, and squash merges into `main`.
