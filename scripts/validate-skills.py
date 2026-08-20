#!/usr/bin/env python3
"""Lightweight validation for the Kunumi skills repository."""

from __future__ import annotations

import json
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


def validate_tokens(skill_dir: Path) -> list[str]:
    """Check that the token source of truth agrees with everything derived from it.

    The palette used to be duplicated across `tokens.json`, `kunumi-tokens.css`, and
    `brand-foundations.md` with nothing keeping them in sync. This check fails the build when
    they drift, and when a prohibited color reappears.

    Args:
        skill_dir: Path to the skill package directory.

    Returns:
        A list of human-readable error strings; empty when the token layer is consistent.
    """
    errors: list[str] = []
    tokens_path = skill_dir / "references" / "tokens.json"
    css_path = skill_dir / "assets" / "web" / "kunumi-tokens.css"
    foundations_path = skill_dir / "references" / "brand-foundations.md"

    if not tokens_path.exists():
        return [f"{skill_dir.name}: missing references/tokens.json"]

    try:
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{skill_dir.name}: tokens.json is not valid JSON: {exc}"]

    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    foundations = (
        foundations_path.read_text(encoding="utf-8") if foundations_path.exists() else ""
    )

    color = tokens.get("color", {})
    groups = ("institutional", "chart")
    for group in groups:
        for entry in color.get(group, {}).get("entries", []):
            hex_value = entry["hex"]
            css_var = entry["cssVar"]
            if css and f"{css_var}: {hex_value.lower()}" not in css.lower():
                errors.append(
                    f"{skill_dir.name}: {css_var} missing or mismatched in kunumi-tokens.css "
                    f"(tokens.json says {hex_value})"
                )
            if foundations and hex_value.upper() not in foundations.upper():
                errors.append(
                    f"{skill_dir.name}: {hex_value} ({group}) absent from brand-foundations.md"
                )

    # Black is prohibited outright; white survives only as the documented raised surface.
    if css:
        for banned in ("#000000", "#000 ", "#000;"):
            if banned in css.lower():
                errors.append(
                    f"{skill_dir.name}: prohibited pure black {banned.strip()} in kunumi-tokens.css"
                )
        surface = "--kunumi-surface-raised"
        white_hits = css.lower().count("#ffffff")
        if white_hits and surface not in css:
            errors.append(
                f"{skill_dir.name}: white used in kunumi-tokens.css without the documented "
                f"{surface} exception"
            )
        if white_hits > 1:
            errors.append(
                f"{skill_dir.name}: white appears {white_hits} times in kunumi-tokens.css; "
                "only the raised-surface token may use it"
            )

    # The display face must never carry negative tracking.
    if css and "letter-spacing: -" in css:
        errors.append(
            f"{skill_dir.name}: negative letter-spacing in kunumi-tokens.css; the display face "
            "is tracked +3%"
        )

    return errors


def validate_reference_links(skill_dir: Path) -> list[str]:
    """Check that every `references/<file>` path named in SKILL.md exists.

    Args:
        skill_dir: Path to the skill package directory.

    Returns:
        A list of error strings for referenced files that are missing on disk.
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []

    errors: list[str] = []
    text = skill_md.read_text(encoding="utf-8")
    for name in sorted(set(re.findall(r"references/([A-Za-z0-9._-]+)", text))):
        if not (skill_dir / "references" / name).exists():
            errors.append(f"{skill_dir.name}: SKILL.md references missing references/{name}")
    return errors


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
        errors.extend(validate_reference_links(skill_dir))
        errors.extend(validate_tokens(skill_dir))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
