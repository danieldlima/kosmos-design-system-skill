# Repository Instructions

This repo stores reusable agent skills for Kunumi. Keep each skill package focused on instructions and resources an agent needs at execution time.

- Put all skill packages under `skills/<skill-name>/`.
- Require `SKILL.md` in every skill folder.
- Keep frontmatter to `name` and `description`; the description must say when the skill should trigger.
- Keep `SKILL.md` short and procedural. Put detailed standards, schemas, examples, and brand rules in one-level-deep `references/` files.
- Put reusable deterministic utilities in `scripts/` and executable output resources in `assets/`.
- Do not invent Kunumi governance values, brand assets, policy IDs, ACLs, or legal names. Ask for approved source material when it is missing.
- Run `python scripts/validate-skills.py` after adding or changing skills.
- Use Conventional Commits, branch-based development, and squash merges into `main` for repository changes.
