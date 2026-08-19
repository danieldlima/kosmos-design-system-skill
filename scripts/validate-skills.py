#!/usr/bin/env python3
"""Lightweight validation for the Kunumi skills repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("---\n"):
        return {}, ["missing opening YAML frontmatter marker"]

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, ["missing closing YAML frontmatter marker"]

    frontmatter: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line!r}")
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.exists():
        return [f"{skill_dir}: missing SKILL.md"]

    metadata, metadata_errors = parse_frontmatter(skill_file)
    errors.extend(f"{skill_file}: {error}" for error in metadata_errors)

    name = metadata.get("name", "")
    description = metadata.get("description", "")

    if not name:
        errors.append(f"{skill_file}: missing frontmatter name")
    elif name != skill_dir.name:
        errors.append(f"{skill_file}: name {name!r} does not match folder {skill_dir.name!r}")
    elif not NAME_RE.fullmatch(name):
        errors.append(f"{skill_file}: name must be lowercase letters, digits, and hyphens only")

    if not description:
        errors.append(f"{skill_file}: missing frontmatter description")
    elif "TODO" in description or "[" in description:
        errors.append(f"{skill_file}: description still looks like a template placeholder")

    text = skill_file.read_text(encoding="utf-8")
    if "TODO" in text:
        errors.append(f"{skill_file}: contains TODO placeholder text")

    agent_file = skill_dir / "agents" / "openai.yaml"
    if agent_file.exists():
        agent_text = agent_file.read_text(encoding="utf-8")
        if "default_prompt:" in agent_text and f"${name}" not in agent_text:
            errors.append(f"{agent_file}: default_prompt should mention ${name}")

    return errors


def main() -> int:
    if not SKILLS_DIR.exists():
        print("skills directory does not exist", file=sys.stderr)
        return 1

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        print("skills directory is empty", file=sys.stderr)
        return 1

    errors: list[str] = []
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
