# Kunumi Agent Skills

Reusable agent skills created for Kunumi workflows live in this repository.

## Layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
    assets/
scripts/
  validate-skills.py
```

Each skill is a self-contained package. `SKILL.md` is required and must include YAML frontmatter with `name` and `description`. Resource folders are optional:

- `references/`: detailed domain guidance that should be loaded only when relevant.
- `scripts/`: deterministic utilities that can be run by an agent.
- `assets/`: templates, brand files, icons, fonts, or other files used in outputs.
- `agents/`: product-specific metadata such as Codex UI labels.

For a skill shipped inside a self-contained plugin, `skills/<skill-name>` may be a relative
symlink to the plugin-owned skill tree. This keeps the standard repository entrypoint without
committing large assets twice.

## Current Skills

- `build-databricks-job-yaml`: Databricks job YAML authoring and validation with LEAP and bank-llm governance checks.
- `kunumi-identity-design`: applying approved Kunumi identity and design guidance to artifacts.

## Adding A Skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Use lowercase hyphenated names, and make the folder name match the frontmatter `name`.
3. Keep `SKILL.md` concise. Move long standards, examples, and schemas into files under `references/`.
4. Add `scripts/` only for utilities worth reusing and testing.
5. Add `assets/` only for files that should be reused in final artifacts.
6. Run `python scripts/validate-skills.py`.

## Development Workflow

- Use short-lived branches for changes; do not develop directly on `main` after the initial repository bootstrap.
- Use Conventional Commits for branch commits and squash-merge commit titles, for example `feat: add databricks cluster guidance`.
- Squash merge branches into `main` so each merged change has one clean Conventional Commit on the default branch.
- Run `python scripts/validate-skills.py` before opening or merging a branch.
