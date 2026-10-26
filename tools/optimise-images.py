#!/usr/bin/env python3
"""Make web-sized WebP copies of the brand library for the site.

    python3 tools/optimise-images.py

Reads full-size originals from brand/ and writes public/assets/img/<name>-<width>.webp.
Add a line to IMAGES when a page needs a new picture, run this, and commit the output:
public/ stays plain files with no build step. Needs Pillow (pip install pillow).
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "brand"
OUT = ROOT / "public" / "assets" / "img"

# source (relative to brand/), output name, widths, quality
IMAGES = [
    ("photos/faye-laughing-cutout.png", "faye-laughing", (640, 1100), 82),
    ("backgrounds/particles.jpg", "particles", (1280, 2400), 62),
    ("photos/faye-stage-jam.jpg", "faye-stage-jam", (636,), 80),
    ("photos/faye-coaching-group.jpg", "faye-coaching-group", (720, 1200), 78),
    ("photos/ladies-who-launch.jpg", "ladies-who-launch", (720, 1200), 78),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src, name, widths, quality in IMAGES:
        im = Image.open(SRC / src)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        for w in widths:
            w = min(w, im.width)
            h = round(im.height * w / im.width)
            out = OUT / f"{name}-{w}.webp"
            im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=quality, method=6)
            print(f"{out.relative_to(ROOT)}  {w}x{h}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
