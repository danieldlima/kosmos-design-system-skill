#!/usr/bin/env python3
"""Link the repository skill entry or build a standalone plugin bundle."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


PLUGIN_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = PLUGIN_DIR.parents[1]
PLUGIN_SKILL = PLUGIN_DIR / "skills" / "kunumi-identity-design"
REPO_SKILL = REPO_DIR / "skills" / "kunumi-identity-design"


def ensure_development_link() -> None:
    """Expose the plugin-owned canonical skill at the repository skill path."""
    expected = Path(os.path.relpath(PLUGIN_SKILL, REPO_SKILL.parent))
    if REPO_SKILL.is_symlink():
        current = Path(os.readlink(REPO_SKILL))
        if current == expected:
            print(f"Repository skill link is current: {REPO_SKILL} -> {current}")
            return
        raise SystemExit(
            f"Unexpected skill link: {REPO_SKILL} -> {current}; expected {expected}"
        )
    if REPO_SKILL.exists():
        raise SystemExit(
            f"Refusing to replace existing repository skill copy: {REPO_SKILL}\n"
            "Remove or archive that duplicate first, then rerun this command."
        )
    REPO_SKILL.parent.mkdir(parents=True, exist_ok=True)
    REPO_SKILL.symlink_to(expected, target_is_directory=True)
    print(f"Linked {REPO_SKILL} -> {expected}")


def build_standalone_bundle(destination: Path) -> None:
    """Materialize a self-contained plugin outside the tracked source tree."""
    destination = destination.resolve()
    if destination.exists():
        raise SystemExit(f"Bundle destination already exists: {destination}")
    if PLUGIN_DIR.resolve() in destination.parents:
        raise SystemExit("Build the standalone bundle outside the plugin source directory.")

    shutil.copytree(
        PLUGIN_DIR,
        destination,
        ignore=shutil.ignore_patterns(
            "*.inspect.ndjson",
            "*.manifest.json",
            ".DS_Store",
            "__pycache__",
            "*.pyc",
        ),
    )
    print(f"Built standalone plugin: {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Link the canonical repo skill or build a standalone plugin bundle."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        help="Materialize a self-contained plugin at this new path.",
    )
    return parser.parse_args()


def main() -> None:
    if not (PLUGIN_SKILL / "SKILL.md").is_file():
        raise SystemExit(f"Missing canonical plugin skill: {PLUGIN_SKILL}")
    args = parse_args()
    if args.bundle_dir:
        build_standalone_bundle(args.bundle_dir)
    else:
        ensure_development_link()


if __name__ == "__main__":
    main()
