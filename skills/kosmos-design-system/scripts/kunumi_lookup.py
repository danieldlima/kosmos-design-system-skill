#!/usr/bin/env python3
"""Resolve Kunumi sources, design tokens, slide layouts, and approved assets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
REFERENCES_DIR = SKILL_DIR / "references"

TOKENS = {
    "primary": {
        "urucum": "#F04E44",
        "chumbo": "#1C2127",
        "grafite": "#5E5E5E",
        "concreto": "#B4ADA4",
        "gelo": "#F0F0F0",
    },
    "support": {
        "amarelo": "#FF931E",
        "laranja": "#F26638",
        "magenta": "#D73E5F",
        "violeta": "#9355A0",
        "indigo": "#5A61B6",
        "preto": "#000000",
    },
    "extended_chart_only": {
        "amarelo": ["#481F00", "#7D470A", "#FFDFC1"],
        "indigo": ["#1A2052", "#3A2FDF", "#D6E0FF"],
        "verde": ["#103C1F", "#246A3C", "#43F085", "#ADF3BE"],
    },
    "typography": {
        "family": "Figtree",
        "fallback": "Arial",
        "weights": ["ExtraBold", "SemiBold", "Medium", "Regular", "Light"],
    },
}


def load(name: str) -> dict[str, Any]:
    return json.loads((REFERENCES_DIR / name).read_text(encoding="utf-8"))


def text_matches(entry: dict[str, Any], query: str | None) -> bool:
    if not query:
        return True
    haystack = json.dumps(entry, ensure_ascii=False).lower()
    return all(term in haystack for term in query.lower().split())


def contains_tag(entry: dict[str, Any], tags: list[str]) -> bool:
    available = {tag.lower() for tag in entry.get("tags", [])}
    return all(tag.lower() in available for tag in tags)


def select_assets(args: argparse.Namespace) -> list[dict[str, Any]]:
    entries = []
    for source in load("semantic-index.json")["featuredSources"]:
        tags = source.get("tags", [])
        path = source["localPath"]
        entries.append(
            {
                **source,
                "path": path,
                "format": Path(path).suffix.lower().lstrip(".") or "native",
                "variant": (
                    "positive"
                    if "positive" in tags
                    else "negative"
                    if "negative" in tags
                    else "none"
                ),
            }
        )
    result = []
    for entry in entries:
        if args.identity and entry.get("identity") != args.identity:
            continue
        if args.kind and entry.get("kind") != args.kind:
            continue
        if args.format and entry.get("format") != args.format:
            continue
        if args.variant and entry.get("variant") != args.variant:
            continue
        if args.motion and not (
            "motion" in entry.get("tags", [])
            or entry.get("kind") in {"motion", "video"}
        ):
            continue
        if not contains_tag(entry, args.tag):
            continue
        if not text_matches(entry, args.search):
            continue
        result.append(entry)
    return result


def select_slides(args: argparse.Namespace) -> list[dict[str, Any]]:
    entries = load("slide-index.json")["slides"]
    result = []
    for entry in entries:
        if args.mode and entry.get("mode") != args.mode:
            continue
        if args.role and entry.get("role") != args.role:
            continue
        if not contains_tag(entry, args.tag):
            continue
        if not text_matches(entry, args.search):
            continue
        result.append(entry)
    return result


def select_patterns(args: argparse.Namespace) -> list[dict[str, Any]]:
    entries = load("visual-pattern-index.json")["patterns"]
    result = []
    for entry in entries:
        if args.mode and entry.get("mode") != args.mode:
            continue
        if args.medium and args.medium not in entry.get("mediums", []):
            continue
        if not contains_tag(entry, args.tag):
            continue
        if not text_matches(entry, args.search):
            continue
        result.append(entry)
    return result


def select_sources(args: argparse.Namespace) -> list[dict[str, Any]]:
    entries = load("semantic-index.json")["featuredSources"]
    result = []
    for entry in entries:
        if getattr(args, "identity", None) and entry.get("identity") != args.identity:
            continue
        if getattr(args, "kind", None) and entry.get("kind") != args.kind:
            continue
        if not contains_tag(entry, getattr(args, "tag", [])):
            continue
        if not text_matches(entry, getattr(args, "search", None)):
            continue
        result.append(entry)
    return result


def print_assets(entries: list[dict[str, Any]], limit: int) -> None:
    for entry in entries[:limit]:
        geometry = ""
        if entry.get("width") and entry.get("height"):
            geometry = f" · {entry['width']}×{entry['height']}"
        if entry.get("durationSeconds") is not None:
            geometry += f" · {entry['durationSeconds']}s"
        print(
            f"{entry['kind']} · {entry['identity']} · {entry['variant']}"
            f"{geometry}\n  {entry['path']}\n  {entry['use']}"
        )
    print(f"matches={len(entries)} shown={min(len(entries), limit)}")


def print_slides(entries: list[dict[str, Any]], limit: int) -> None:
    for entry in entries[:limit]:
        print(
            f"slide {entry['slide']:02} · {entry['role']} · {entry['mode']}\n"
            f"  {entry['use']}\n"
            f"  slots: {', '.join(entry['slots'])}"
        )
    print(f"matches={len(entries)} shown={min(len(entries), limit)}")


def print_patterns(entries: list[dict[str, Any]], limit: int) -> None:
    for entry in entries[:limit]:
        print(
            f"{entry['id']} · {entry['mode']} · slides "
            f"{','.join(str(number) for number in entry['sourceSlides'])}\n"
            f"  {entry['purpose']}\n"
            f"  recipe: {entry['recipe']}\n"
            f"  motion: {entry['motion']}"
        )
    print(f"matches={len(entries)} shown={min(len(entries), limit)}")


def resolved_source(entry: dict[str, Any]) -> dict[str, Any]:
    result = dict(entry)
    local_path = entry.get("localPath")
    if local_path:
        result["localExists"] = (SKILL_DIR / local_path).exists()
        result["absoluteLocalPath"] = str(SKILL_DIR / local_path)
    return result


def print_sources(entries: list[dict[str, Any]], limit: int) -> None:
    for source in (resolved_source(entry) for entry in entries[:limit]):
        print(
            f"{source['key']} · {source['identity']} · {source['kind']}\n"
            f"  {source['use']}"
        )
        if source.get("localPath"):
            availability = "ready" if source.get("localExists") else "missing"
            print(f"  local ({availability}): {source['absoluteLocalPath']}")
    print(f"matches={len(entries)} shown={min(len(entries), limit)}")


def add_common_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--search", help="Require every term anywhere in the entry.")
    parser.add_argument("--tag", action="append", default=[], help="Require a tag; repeatable.")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Print matching JSON.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    tokens_parser = subparsers.add_parser("tokens", help="Print exact color and type tokens.")
    tokens_parser.add_argument("--json", action="store_true")

    assets_parser = subparsers.add_parser("assets", help="Find approved source assets.")
    assets_parser.add_argument("--identity")
    assets_parser.add_argument("--kind")
    assets_parser.add_argument("--format")
    assets_parser.add_argument("--variant")
    assets_parser.add_argument("--motion", action="store_true")
    add_common_filters(assets_parser)

    slides_parser = subparsers.add_parser("slides", help="Find source-slide layouts.")
    slides_parser.add_argument("--mode")
    slides_parser.add_argument("--role")
    add_common_filters(slides_parser)

    patterns_parser = subparsers.add_parser(
        "patterns", help="Find globally reusable visual patterns."
    )
    patterns_parser.add_argument("--mode")
    patterns_parser.add_argument("--medium")
    add_common_filters(patterns_parser)

    sources_parser = subparsers.add_parser(
        "sources", help="Find approved bundled sources."
    )
    sources_parser.add_argument("--identity")
    sources_parser.add_argument("--kind")
    add_common_filters(sources_parser)

    resolve_parser = subparsers.add_parser(
        "resolve", help="Resolve a plain-language need to the best source."
    )
    resolve_parser.add_argument("query", help='For example: "Instituto gradient".')
    resolve_parser.add_argument("--limit", type=int, default=8)
    resolve_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "tokens":
        print(json.dumps(TOKENS, indent=2))
        return
    if args.command == "assets":
        entries = select_assets(args)
        if args.json:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
        else:
            print_assets(entries, args.limit)
        return
    if args.command == "slides":
        entries = select_slides(args)
        if args.json:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
        else:
            print_slides(entries, args.limit)
        return
    if args.command == "patterns":
        entries = select_patterns(args)
        if args.json:
            print(json.dumps(entries, ensure_ascii=False, indent=2))
        else:
            print_patterns(entries, args.limit)
        return
    if args.command == "sources":
        entries = select_sources(args)
        if args.json:
            print(
                json.dumps(
                    [resolved_source(entry) for entry in entries],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print_sources(entries, args.limit)
        return
    if args.command == "resolve":
        args.search = args.query
        args.tag = []
        args.identity = None
        args.kind = None
        entries = sorted(select_sources(args), key=lambda entry: entry["key"])
        if args.json:
            print(
                json.dumps(
                    [resolved_source(entry) for entry in entries[: args.limit]],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print_sources(entries, args.limit)
        return
    parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
