#!/usr/bin/env python3
"""Build a self-contained plugin bundle outside the repository."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "kosmos-design-system"


def build_standalone_bundle(destination: Path) -> None:
    """Materialize a self-contained plugin outside the tracked source tree."""
    destination = destination.resolve()
    if destination.exists():
        raise SystemExit(f"Bundle destination already exists: {destination}")
    if ROOT in destination.parents or destination == ROOT:
        raise SystemExit("Build the standalone bundle outside the repository directory.")

    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            ".github",
            "Ativos de Marca",
            "Canais e Redes Sociais",
            "Templates",
            "*.inspect.ndjson",
            "*.manifest.json",
            ".DS_Store",
            "__pycache__",
            "*.pyc",
        ),
    )
    print(f"Built standalone plugin: {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Materialize a self-contained plugin at this new path.",
    )
    return parser.parse_args()


def main() -> None:
    if not (SKILL_DIR / "SKILL.md").is_file():
        raise SystemExit(f"Missing skill: {SKILL_DIR}")
    args = parse_args()
    build_standalone_bundle(args.bundle_dir)


if __name__ == "__main__":
    main()
