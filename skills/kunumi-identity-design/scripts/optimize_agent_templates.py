#!/usr/bin/env python3
"""Resolution-optimize the approved closing-wave motion in agent templates."""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image


HEAVY_MEMBER = "ppt/media/image4.gif"
EXPECTED_HEAVY_SHA256 = (
    "f5d1bc390fc5a14f6766547d6850554a37211146663bd0adc18888967c25092e"
)
EXPECTED_HEAVY_SIGNATURE = ((1920, 1080), 38, 3040)
EXPECTED_OPTIMIZED_SIGNATURE = ((960, 540), 38, 3040)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def gif_signature(data: bytes) -> tuple[tuple[int, int], int, int]:
    with Image.open(BytesIO(data)) as image:
        frames = getattr(image, "n_frames", 1)
        duration = 0
        for index in range(frames):
            image.seek(index)
            duration += int(image.info.get("duration", 0))
        return image.size, frames, duration


def cloned_info(info: ZipInfo) -> ZipInfo:
    clone = ZipInfo(info.filename, date_time=info.date_time)
    clone.compress_type = info.compress_type
    clone.comment = info.comment
    clone.extra = info.extra
    clone.create_system = info.create_system
    clone.create_version = info.create_version
    clone.extract_version = info.extract_version
    clone.flag_bits = info.flag_bits
    clone.internal_attr = info.internal_attr
    clone.external_attr = info.external_attr
    return clone


def optimize_gif(source: bytes) -> bytes:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required to optimize the template animation.")

    with TemporaryDirectory(prefix="kunumi-template-motion-") as temporary:
        temporary_path = Path(temporary)
        source_path = temporary_path / "source.gif"
        output_path = temporary_path / "optimized.gif"
        source_path.write_bytes(source)
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source_path),
                "-filter_complex",
                (
                    "[0:v]scale=960:540:flags=lanczos,split[a][b];"
                    "[a]palettegen=max_colors=256:stats_mode=diff[p];"
                    "[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle"
                ),
                "-loop",
                "0",
                str(output_path),
            ],
            check=True,
        )
        optimized = output_path.read_bytes()
    if gif_signature(optimized) != EXPECTED_OPTIMIZED_SIGNATURE:
        raise SystemExit(
            f"Unexpected optimized animation signature: {gif_signature(optimized)}"
        )
    return optimized


def optimize_template(source: Path, destination: Path) -> tuple[int, int]:
    with ZipFile(source) as archive:
        if HEAVY_MEMBER not in archive.namelist():
            raise SystemExit(f"Missing expected template media: {HEAVY_MEMBER}")
        heavy = archive.read(HEAVY_MEMBER)
        if sha256(heavy) != EXPECTED_HEAVY_SHA256:
            raise SystemExit(
                f"Unexpected {HEAVY_MEMBER} hash in {source}; refusing replacement."
            )
        if gif_signature(heavy) != EXPECTED_HEAVY_SIGNATURE:
            raise SystemExit(f"Unexpected heavy animation signature in {source}")
        replacement = optimize_gif(heavy)

        destination.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=9) as output:
            for info in archive.infolist():
                data = replacement if info.filename == HEAVY_MEMBER else archive.read(info)
                output.writestr(cloned_info(info), data)

    return source.stat().st_size, destination.stat().st_size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Downscale and palette-optimize the approved closing-wave GIF in "
            "an agent template while preserving its frames and duration."
        )
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    if source == destination:
        raise SystemExit("Write to a separate destination and verify before replacing.")
    before, after = optimize_template(source, destination)
    saved = before - after
    print(f"{source.name}: {before / 1024 / 1024:.1f} -> {after / 1024 / 1024:.1f} MiB")
    print(f"saved={saved / 1024 / 1024:.1f} MiB output={destination}")


if __name__ == "__main__":
    main()
