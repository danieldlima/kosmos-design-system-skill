#!/usr/bin/env python3
"""Rebuild compact, queryable indexes from the bundled Kunumi sources."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from PIL import Image


SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_DIR / "assets"
REFERENCES_DIR = SKILL_DIR / "references"
PPTX_PATH = ASSETS_DIR / "Kunumi - Template de Slides.pptx"

SLIDE_ROWS = """
1|instruction|light|Template cover and date|title,subtitle,date,brand-symbol|cover,instruction
2|instruction|light|Template usage and editing instructions|title,body|instruction
3|brand-architecture|light|Compare core Kunumi, Unlimited, and Instituto identities|intro,three identity columns|identity,comparison
4|instruction|light|Explain the available layout system|title,two text columns,layout preview|instruction,layouts
5|instruction|light|Explain the two-by-two grid and breathing space|title,two text columns,grid overlay|instruction,grid
6|color-system|light|Show primary, support, and chart-only extended palettes|palette groups,swatches,notes|colors,reference
7|title-cover|light|Minimal presentation title cover|title,subtitle,date,large brand symbol|cover,title
8|agenda|light|List chapters or sections|chapter list,accent rule|agenda,section
9|title-cover|gradient|High-impact Instituto title cover with gamma wave|title,date,large brand symbol|cover,instituto,gradient
10|title-cover|dark|High-impact title cover with stepped pixels|title,date,large brand symbol|cover,dark,pixels
11|section-progress|light|Show chapter progress or a three-step section path|progress rule,three labels|section,progress
12|keyword-body|light|Pair a keyword with explanatory copy|keyword,body|text,two-column
13|title-body|light|Balance a short title with two body columns|title,two body columns|text,two-column
14|headline-columns|light|Lead with a takeaway and three evidence columns|headline,deck,three columns|text,three-column
15|identity-story|light|Explain Instituto or identity content around a central symbol|symbol,title,body|identity,visual
16|text-photo|light|Place text left and a square image right|title,body,square image|photo,two-column
17|photo-text|light|Place a large image left and text right|large image,eyebrow,title,body|photo,two-column
18|photo-text|light|Place a large image left with a shorter text block right|large image,title,body|photo,two-column
19|gradient-text|split|Pair an Instituto gradient panel left with text right|gradient panel,title,body|instituto,gradient,two-column
20|dark-text|split|Pair a black panel left with text right|black panel,title,body|dark,two-column
21|texture-text|light|Pair a light texture left with text right|texture panel,title,body|photo,texture,two-column
22|text-bars|light|Pair text left with a horizontal palette-bars panel right|title,body,bars panel|graphic,two-column
23|text-pixels|light|Pair text left with a pixel-gradient panel right|title,body,pixel panel|graphic,pixels,two-column
24|text-texture|light|Pair text left with a light texture right|title,body,texture panel|photo,texture,two-column
25|text-horizontal-photo|light|Pair text left with a wide image right|title,body,wide image|photo,two-column
26|mosaic-text|light|Pair narrative text with one large and two small images|title,subtitle,body,three images|photo,mosaic
27|mosaic-captioned|light|Pair text with a captioned hero and two thumbnails|title,subtitle,body,three captioned images|photo,mosaic,captions
28|media-grid|light|Show a two-by-three image grid with captions|six images,six captions|photo,mosaic,grid
29|media-grid|light|Show a second two-by-three image grid with captions|six images,six captions|photo,mosaic,grid
30|visual-comparison|light|Compare four visual or media examples|four visuals,four labels,four descriptions|comparison,media
31|full-bleed-texture|light|Use a full-slide light texture with a small text block|background image,body|photo,full-bleed
32|full-bleed-photo|dark|Use a full-slide photo with concise overlay copy|background photo,short copy,arrow|photo,full-bleed
33|quote|light|Present a centered quotation and attribution|quote,attribution,quote marks|quote
34|quote|gradient|Present a centered quote over an Instituto gradient|gradient background,quote,attribution|quote,instituto,gradient
35|big-numbers|light|Present three large metrics with short explanations|three metrics,three descriptions|data,kpi
36|big-numbers|light|Present two large metrics with narrative emphasis|two metrics,two descriptions,highlight|data,kpi
37|regional-map|light|Pair a Brazil map right with narrative text left|title,eyebrow,body,map|map,data
38|regional-map-media|light|Pair a Brazil map with a two-item media rail|map,two visuals,two captions|map,media
39|regional-map|light|Pair a South America map right with narrative text left|title,eyebrow,body,map|map,data
40|regional-map-media|light|Pair a South America map with a two-item media rail|map,two visuals,two captions|map,media
41|world-map|light|Use a world map with a highlighted region and small text|map,highlight,body|map,data
42|external-chart|light|Pair explanatory text left with an imported chart right|title,body,external chart,source note|chart,data
43|internal-chart|light|Pair explanatory text left with a native donut chart|title,body,donut chart,labels|chart,data
44|phase-timeline|light|Show a two-phase horizontal timeline|two phases,dates,milestones|timeline,process
45|calendar-timeline|light|Show a month-by-month roadmap|months,descriptions,active month|timeline,roadmap
46|process-columns|light|Show a multi-stage process with dark headers|stages,cards,connectors|process,diagram
47|process-flow|light|Show a branching node-and-connector flow|nodes,connectors,title|process,diagram
48|gantt|light|Show a multiyear Gantt plan|time axis,workstreams,bars,legend|timeline,gantt,data
49|comparison-table|light|Show a structured comparison or requirements matrix|title,group headers,table|table,comparison
50|numeric-table|light|Show a numeric table with confidence and status icons|headers,numeric rows,status icons|table,data
51|content-matrix|light|Show a dense light content matrix|five columns,multiple rows|table,matrix
52|content-matrix|light|Show a dense light matrix with highlighted rows|five columns,multiple rows,highlights|table,matrix
53|agenda|dark|List chapters or sections on Chumbo|chapter list,accent rule|agenda,section,dark
54|section-progress|dark|Show chapter progress on Chumbo|progress rule,three labels|section,progress,dark
55|keyword-body|dark|Pair a keyword with explanatory copy on Chumbo|keyword,body|text,two-column,dark
56|title-body|dark|Balance a short title with two body columns on Chumbo|title,two body columns|text,two-column,dark
57|headline-columns|dark|Lead with a takeaway and three evidence columns on Chumbo|headline,deck,three columns|text,three-column,dark
58|identity-story|dark|Explain Instituto or identity content around a central symbol|symbol,title,body|identity,visual,dark
59|text-photo|dark|Place text left and a square image right on Chumbo|title,body,square image|photo,two-column,dark
60|photo-text|dark|Place a large image left and text right on Chumbo|large image,eyebrow,title,body|photo,two-column,dark
61|photo-text|dark|Place a large image left with shorter copy right on Chumbo|large image,title,body|photo,two-column,dark
62|full-bleed-story|dark|Use a dark image-led story with centered copy and regional art|background image,body,regional visual|photo,full-bleed,dark
63|big-numbers|dark|Present three large metrics on Chumbo|three metrics,three descriptions|data,kpi,dark
64|big-numbers|dark|Present two large metrics with emphasis on Chumbo|two metrics,two descriptions,highlight|data,kpi,dark
65|content-matrix|dark|Show a dense dark content matrix|five columns,multiple rows|table,matrix,dark
66|content-matrix|dark|Show a denser dark matrix with grouped rows|five columns,group labels,multiple rows|table,matrix,dark
67|closing|gradient|Close with a centered message over an Instituto gamma wave|closing message,gradient background|closing,instituto,gradient
68|logo-reference|light|Reference positive complete and icon signatures|complete mark,icon,gradient icon,labels|resource,logo
69|logo-reference|dark|Reference negative complete and icon signatures|complete mark,icon,gradient icon,labels|resource,logo,dark
70|symbol-reference|light|Compare approved brand-symbol variants on light|five symbols|resource,symbol
71|symbol-reference|dark|Compare approved brand-symbol variants on dark|five symbols|resource,symbol,dark
72|icon-reference|mixed|Reference status and navigation icons on light and dark|two icon sets,status color keys|resource,icons
73|brand-artwork|dark|Show the full Kunumi graphic composition|full-bleed brand artwork|resource,artwork
74|static-background-reference|light|Preview three static Instituto gradient backgrounds|three background previews|resource,instituto,static
75|motion-reference|light|Preview three gamma-wave GIF families|three GIF previews|resource,instituto,motion
76|motion-reference|light|Preview bars, black, stripes, and kaleidoscope GIFs|four GIF previews|resource,instituto,motion
""".strip()

KSEQUENCE_PATTERN_ROWS = """
dark-hero-orbit|dark|1,2|Open with one large claim and one luminous focal object|slides,web,social|cover,hero,orbit,gradient|Use a 55/45 split, oversized left-aligned Figtree, restrained grid, peripheral red-violet glow, and thin orbital rings.|Float only the focal object on a slow loop; keep copy and chrome still.
dual-pillar|dark|3|Contrast two foundations, principles, or strategic pillars|slides,web|comparison,pillars,diagram|Use two equal dark fields with a thin accent rail, one micro-diagram, and no more than one paragraph per field.|Build diagrams in 400-700 ms with a short stagger; loop only a simple signal.
typed-interlude|light|4|Create a brief narrative reset before a new chapter|slides,web,motion|interlude,typewriter,terminal|Place one short monospaced message inside a generous light window over a faint grid.|Type at a readable pace, pause after the opening phrase, then use a single high-impact transition.
lineage-branching|dark|6|Show one origin becoming several connected initiatives|slides,web,diagram|lineage,branching,team,process|Place the origin left, a division core near center, and ordered descendants right; use gradient connectors and aligned portraits or icons.|Draw connectors first, migrate markers second, reveal destinations last.
people-orbit|light|7,8,10,18,20|Introduce a team or person through an orbital portrait system|slides,social,web|people,portrait,orbit,chapter|Use a quiet light field, circular portraits, thin orbital rules, and one small red plus one violet marker.|Use only slow 4-5 second portrait drift and a much slower orbit rotation.
cinematic-photo-chapter|dark|11,12,13,15,16,22|Build an immersive image-led chapter with concise copy|slides,social,video|photo,cinematic,chapter,overlay|Use one full-bleed photograph, a directional black overlay, an eyebrow, a large claim, and minimal metadata.|Allow gentle image drift or grain; never animate essential copy.
editorial-gallery|mixed|9,14,21|Tell a human story through one collage or structured gallery|slides,social,documents|gallery,collage,photo,editorial|Choose either a composed editorial collage or a clean asymmetric image grid; keep crops and borders consistent.|Use entry reveals only when order matters; otherwise keep the gallery static.
light-operating-system|light|23,24,25,26|Explain practices, channels, systems, or operating principles|slides,documents,web|workflow,rows,diagram,editorial|Use warm Gelo paper, Chumbo type, hairline rules, disciplined rows, and compact diagrams instead of decorative cards.|Reveal rows or connectors in reading order with 80-150 ms staggers.
story-wall|light|27|Present a set of anecdotes, decisions, or cases as an editorial wall|slides,web,social|stories,cards,editorial|Use varied paper fields with very small rotations, tape details, one dominant story, and clear author markers.|Use subtle hover or opening motion only; preserve legibility over playfulness.
cosmic-scale-map|dark|29|Compare a family of objects whose scale is meaningful|slides,web,data-viz|scale,universe,orbit,interactive,data-viz|Map area to quantity, separate families by hue, provide a scale rail, and let labels stay outside the objects.|Stagger object arrival, pulse the core gently, and make filters settle in under 600 ms.
parallel-sequences|dark|30|Explain an analogy by aligning two step-by-step sequences|slides,documents,web|sequence,comparison,explainer|Stack two parallel rails with matching grammar, highlight the predicted output, and place the shared logic between them.|Reveal tokens in order, draw the connector, then reveal the outcome.
claim-demo-split|dark|31|Pair a strong claim with several views of one reusable context|slides,web,data-viz|demo,tabs,metrics,scenario,data-viz|Keep the claim in the left third and the interactive or scenario panel in the right two-thirds; reuse the same frame for every scenario.|Switch scenarios with a 350-500 ms lateral or opacity transition; animate only the changed measure.
before-after-system|dark|32|Contrast a fragmented current state with a connected future state|slides,web,diagram|before-after,transformation,system|Use symmetric outer fields, a small transformation engine at center, muted current-state nodes, and a clearer future-state system.|Let one data point traverse the center; keep ambient orbits slow.
results-comparison|light|33|Present model or option results with an explicit takeaway|slides,documents,data-viz|results,table,bubbles,comparison,data-viz|Lead with the conclusion, use one or two disciplined tables, bold the winner, and add a short directional note such as higher or lower is better.|Use a quick panel change only when tabs expose alternate result families.
process-orbit|dark|34|Show an iterative cycle plus version or maturity progression|slides,web,diagram|process,orbit,timeline,iteration|Combine a few top milestones, one large loop with labeled stages, and a separate version rail.|Move one runner around the loop slowly; reveal nodes once and keep sparks sparse.
capability-triptych|dark|35|Summarize three capabilities and connect them to a wider ecosystem|slides,web,documents|capabilities,triptych,integration,diagram|Use three equal capability scenes with cropped diagram-atlas art, then a full-width integration band underneath.|Float decorative atlas art 3-7 px over 6-8 seconds; keep labels still.
case-board|dark|36|Turn a sequence, investigation, or decision into an evidence-based case|slides,web,interactive|case,timeline,choices,evidence|Pair a narrative claim with an evidence timeline, bounded options, and a response area; distinguish known facts from hypotheses.|Reveal evidence before choices and use a restrained selected state rather than celebration effects.
""".strip()


def parse_slide_rows() -> list[dict[str, Any]]:
    slides: list[dict[str, Any]] = []
    for row in SLIDE_ROWS.splitlines():
        number, role, mode, use, slots, tags = row.split("|")
        slides.append(
            {
                "slide": int(number),
                "role": role,
                "mode": mode,
                "use": use,
                "slots": [item.strip() for item in slots.split(",")],
                "tags": [item.strip() for item in tags.split(",")],
            }
        )
    expected = list(range(1, 77))
    actual = [entry["slide"] for entry in slides]
    if actual != expected:
        raise ValueError(f"Slide registry must cover 1-76 exactly; got {actual}")
    return slides


def parse_ksequence_patterns() -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for row in KSEQUENCE_PATTERN_ROWS.splitlines():
        (
            pattern_id,
            mode,
            source_slides,
            purpose,
            mediums,
            tags,
            recipe,
            motion,
        ) = row.split("|")
        patterns.append(
            {
                "id": pattern_id,
                "mode": mode,
                "sourceSlides": [int(number) for number in source_slides.split(",")],
                "purpose": purpose,
                "mediums": [item.strip() for item in mediums.split(",")],
                "tags": [item.strip() for item in tags.split(",")],
                "recipe": recipe,
                "motion": motion,
            }
        )
    return patterns


def ratio_label(width: int, height: int) -> str:
    if not width or not height:
        return "unknown"
    from math import gcd

    factor = gcd(width, height)
    return f"{width // factor}:{height // factor}"


def classify_asset(relative_path: str) -> tuple[str, str, str, list[str]]:
    normalized = relative_path.replace("\\", "/")
    name = Path(normalized).name.lower()
    suffix = Path(normalized).suffix.lower().lstrip(".")
    tags: list[str] = []
    is_global_pattern = "/Global Visual Patterns/" in normalized

    if is_global_pattern:
        identity = "multi-identity"
        tags.extend(["deck-extracted", "global", "ksequence"])
    elif "/Instituto/" in normalized:
        identity = "instituto"
    elif "/Unlimited/" in normalized or "unltd" in name:
        identity = "unlimited"
    elif "/Ícone/" in normalized or "/Ícone/" in normalized:
        identity = "shared-icon"
    elif "/Kunumi/" in normalized:
        identity = "core"
    elif "Template de Slides" in normalized:
        identity = "multi-identity"
    else:
        identity = "core-channel"

    variant = "negative" if "negativo" in name else "positive" if "positivo" in name else "none"
    if variant == "positive":
        tags.extend(["positive", "light-background"])
    elif variant == "negative":
        tags.extend(["negative", "dark-background"])

    if name in {"habits-background-art.png", "capability-background-art.png"}:
        kind = "visual-pattern-atlas"
        tags.extend(["atlas", "diagram", "transparent"])
        tags.append("habits" if name.startswith("habits") else "capabilities")
    elif suffix == "pptx":
        kind = "slide-template"
    elif suffix == "docx":
        kind = "guide"
    elif "linkedin" in name:
        kind = "channel-template"
        tags.extend(["linkedin", "wide"])
    elif name == "marca.png":
        kind = "profile-mark"
        tags.extend(["profile-photo", "specialized"])
    elif "/Estáticos/" in normalized or "/Estáticos/" in normalized:
        kind = "static-background"
        tags.append("static")
    elif suffix == "gif":
        kind = "motion-background"
        tags.extend(["motion", "gif"])
    elif suffix in {"mp4", "mov"}:
        kind = "motion-background"
        tags.extend(["motion", "video"])
    elif "/Instituto - Marca/" in normalized or "logotipo" in name or "unltd" in name:
        kind = "wordmark"
    elif "ícone/" in normalized.lower() or "ícone/" in normalized.lower() or "icone" in name:
        kind = "icon"
    else:
        kind = "image"

    for token, tag in [
        ("gradiente", "gradient"),
        ("ondas", "gamma-wave"),
        ("barras", "bars"),
        ("pixels", "pixels"),
        ("kaleido", "kaleidoscope"),
        ("mapa_gama", "gamma-map"),
        ("marca_", "brand-symbol"),
    ]:
        if token in name:
            tags.append(tag)

    if name.startswith("g-_shared-drives"):
        tags.extend(["image-bank", "portrait", "photographic"])

    return identity, kind, variant, sorted(set(tags))


def asset_use(kind: str, identity: str, variant: str, name: str, tags: list[str]) -> str:
    if kind in {"wordmark", "icon"}:
        ground = "dark" if variant == "negative" else "light"
        return f"Place the approved {identity} {kind} on a {ground} background."
    if kind == "profile-mark":
        return "Use only in the Kunumi IA profile-photo workflow."
    if kind == "channel-template":
        return "Use as the approved Kunumi LinkedIn header."
    if kind == "visual-pattern-atlas":
        subject = "operating-principle" if "habits" in tags else "capability"
        return f"Crop one quadrant as supplied for a dark {subject} diagram; do not treat the full atlas as one composition."
    if kind == "slide-template":
        return "Duplicate source slides and edit inherited elements for Kunumi presentations."
    if kind == "guide":
        if "Slack" in name:
            return "Use as a channel-specific document-design reference; do not reuse its policy copy."
        return "Use as the authoritative Kunumi IA profile-photo workflow."
    if kind == "static-background":
        family = next(
            (
                tag
                for tag in ["gamma-wave", "bars", "pixels", "kaleidoscope", "gamma-map", "gradient"]
                if tag in tags
            ),
            "graphic",
        )
        return f"Use as supplied for Instituto {family} backgrounds, covers, or section moments."
    if kind == "motion-background":
        if "global" in tags:
            return "Use as a restrained dark Kunumi transition or ambient background with a static fallback."
        if "image-bank" in tags:
            return "Use only when the portrait photographic subject fits the Instituto story."
        if "brand-symbol" in tags:
            return "Use as supplied for a square animated Instituto brand-symbol moment."
        return "Use as supplied for an animated Instituto background or transition."
    return "Use only for the channel or identity indicated by its source path."


def inspect_image(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
        result: dict[str, Any] = {
            "width": width,
            "height": height,
            "aspectRatio": ratio_label(width, height),
            "colorMode": image.mode,
            "hasAlpha": "A" in image.mode or "transparency" in image.info,
        }
        frames = getattr(image, "n_frames", 1)
        if frames > 1:
            duration_ms = 0
            for frame in range(frames):
                image.seek(frame)
                duration_ms += int(image.info.get("duration", 0))
            result["frames"] = frames
            result["durationSeconds"] = round(duration_ms / 1000, 3)
            if duration_ms:
                result["averageFps"] = round(frames / (duration_ms / 1000), 3)
        return result


def inspect_svg(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    width = root.get("width")
    height = root.get("height")
    view_box = root.get("viewBox")
    colors = sorted(
        {
            match.upper()
            for match in re.findall(r"#[0-9a-fA-F]{6}", path.read_text(encoding="utf-8"))
        }
    )
    result: dict[str, Any] = {"width": width, "height": height, "viewBox": view_box}
    if colors:
        result["colors"] = colors
    return result


def inspect_video(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return {"inspectionNote": "ffprobe unavailable"}
    process = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,pix_fmt,width,height,r_frame_rate,duration",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(process.stdout)
    stream = payload.get("streams", [{}])[0]
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    frame_rate = stream.get("r_frame_rate", "0/1")
    fps = float(Fraction(frame_rate)) if frame_rate != "0/0" else 0
    duration = stream.get("duration") or payload.get("format", {}).get("duration")
    return {
        "width": width,
        "height": height,
        "aspectRatio": ratio_label(width, height),
        "codec": stream.get("codec_name"),
        "pixelFormat": stream.get("pix_fmt"),
        "hasAlpha": "a" in str(stream.get("pix_fmt", "")).lower(),
        "fps": round(fps, 3),
        "durationSeconds": round(float(duration), 3) if duration else None,
    }


def inspect_package(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if suffix == ".pptx":
            presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
            ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
            size = presentation.find("p:sldSz", ns)
            fonts: set[str] = set()
            for name in names:
                if name.startswith("ppt/") and name.endswith(".xml"):
                    text = archive.read(name).decode("utf-8", "ignore")
                    fonts.update(re.findall(r'typeface="([^"]+)"', text))
            return {
                "slides": sum(
                    bool(re.fullmatch(r"ppt/slides/slide\d+\.xml", name)) for name in names
                ),
                "layouts": sum(
                    bool(re.fullmatch(r"ppt/slideLayouts/slideLayout\d+\.xml", name))
                    for name in names
                ),
                "masters": sum(
                    bool(re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name))
                    for name in names
                ),
                "embeddedMedia": sum(name.startswith("ppt/media/") for name in names),
                "widthEmu": int(size.get("cx", 0)) if size is not None else None,
                "heightEmu": int(size.get("cy", 0)) if size is not None else None,
                "aspectRatio": "16:9",
                "sourceFonts": sorted(font for font in fonts if font and not font.startswith("+")),
            }
        app_path = "docProps/app.xml"
        pages = None
        if app_path in names:
            app = ET.fromstring(archive.read(app_path))
            for child in app:
                if child.tag.endswith("Pages") and child.text:
                    pages = int(child.text)
                    break
        document = archive.read("word/document.xml").decode("utf-8", "ignore")
        return {
            "pages": pages,
            "paragraphs": document.count("<w:p"),
            "tables": document.count("<w:tbl>"),
            "inlineDrawings": document.count("<w:drawing>"),
        }


def add_geometry_tags(entry: dict[str, Any]) -> None:
    width = entry.get("width")
    height = entry.get("height")
    if not isinstance(width, int) or not isinstance(height, int):
        return
    if width == height:
        entry["tags"].append("square")
    elif width / height >= 1.5:
        entry["tags"].append("wide")
    elif height / width >= 1.5:
        entry["tags"].append("portrait")
    if entry.get("hasAlpha"):
        entry["tags"].append("transparent")
    entry["tags"] = sorted(set(entry["tags"]))


def build_asset_index() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in sorted(ASSETS_DIR.rglob("*")):
        if not path.is_file() or path.name in {".DS_Store", ".gitkeep"}:
            continue
        relative = path.relative_to(SKILL_DIR).as_posix()
        identity, kind, variant, tags = classify_asset(relative)
        entry: dict[str, Any] = {
            "path": relative,
            "name": path.name,
            "format": path.suffix.lower().lstrip("."),
            "bytes": path.stat().st_size,
            "identity": identity,
            "kind": kind,
            "variant": variant,
            "tags": tags,
            "use": asset_use(kind, identity, variant, path.name, tags),
        }
        if "deck-extracted" in tags:
            entry["provenance"] = (
                "Copied unchanged from presentation-ksequence-cambio for global visual use."
            )
        suffix = path.suffix.lower()
        try:
            if suffix in {".png", ".gif", ".jpg", ".jpeg", ".webp"}:
                entry.update(inspect_image(path))
            elif suffix == ".svg":
                entry.update(inspect_svg(path))
            elif suffix in {".mp4", ".mov"}:
                entry.update(inspect_video(path))
            elif suffix in {".pptx", ".docx"}:
                entry.update(inspect_package(path))
        except Exception as error:  # Keep the index useful if one optional inspector fails.
            entry["inspectionError"] = str(error)
        add_geometry_tags(entry)
        entries.append(entry)
    return {
        "schema": "kunumi.asset-index/v1",
        "assetCount": len(entries),
        "totalBytes": sum(entry["bytes"] for entry in entries),
        "entries": entries,
    }


def slide_layout_relationships(path: Path) -> dict[int, str]:
    relationships: dict[int, str] = {}
    ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            match = re.fullmatch(r"ppt/slides/_rels/slide(\d+)\.xml\.rels", name)
            if not match:
                continue
            root = ET.fromstring(archive.read(name))
            for relationship in root.findall("r:Relationship", ns):
                if relationship.get("Type", "").endswith("/slideLayout"):
                    relationships[int(match.group(1))] = Path(
                        relationship.get("Target", "")
                    ).name
                    break
    return relationships


def build_slide_index() -> dict[str, Any]:
    slides = parse_slide_rows()
    relationships = slide_layout_relationships(PPTX_PATH)
    package = inspect_package(PPTX_PATH)
    if package.get("slides") != 76:
        raise ValueError(f"Expected 76 slides, found {package.get('slides')}")
    for entry in slides:
        entry["source"] = "assets/Kunumi - Template de Slides.pptx"
        entry["layoutXml"] = relationships.get(entry["slide"])
    return {
        "schema": "kunumi.slide-index/v1",
        "template": {
            "path": "assets/Kunumi - Template de Slides.pptx",
            "slides": 76,
            "canvas": {"width": 1920, "height": 1080, "aspectRatio": "16:9"},
            "dominantBackgrounds": ["#F0F0F0", "#1C2127", "Instituto supplied artwork"],
            "sourceFonts": [
                "Figtree ExtraBold",
                "Figtree SemiBold",
                "Figtree Medium",
                "Figtree",
                "Figtree Light",
                "Arial",
            ],
            "package": package,
        },
        "slides": slides,
    }


def build_visual_pattern_index() -> dict[str, Any]:
    patterns = parse_ksequence_patterns()
    return {
        "schema": "kunumi.visual-pattern-index/v1",
        "source": {
            "name": "presentation-ksequence-cambio",
            "slidesReviewed": 36,
            "status": "Extracted visual reference; not a replacement for approved brand foundations.",
        },
        "patternCount": len(patterns),
        "patterns": patterns,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when regenerated indexes differ instead of overwriting them.",
    )
    args = parser.parse_args()
    outputs = {
        REFERENCES_DIR / "asset-index.json": build_asset_index(),
        REFERENCES_DIR / "slide-index.json": build_slide_index(),
        REFERENCES_DIR / "visual-pattern-index.json": build_visual_pattern_index(),
    }
    changed: list[str] = []
    for path, payload in outputs.items():
        rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != rendered:
            changed.append(path.name)
            if not args.check:
                path.write_text(rendered, encoding="utf-8")
    if args.check and changed:
        raise SystemExit("Stale indexes: " + ", ".join(changed))
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
