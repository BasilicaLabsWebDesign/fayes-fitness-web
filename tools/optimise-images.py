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

# source (relative to brand/), output name, widths, quality[, tint]
# tint recolours every visible pixel (keeping transparency): e.g. a white logo for dark pages.
IMAGES = [
    ("photos/faye-laughing-cutout.png", "faye-laughing", (640, 1100), 82),
    ("backgrounds/particles.jpg", "particles", (1280, 2400), 62),
    ("photos/faye-stage-jam.jpg", "faye-stage-jam", (636,), 80),
    ("photos/faye-coaching-group.jpg", "faye-coaching-group", (720, 1200), 78),
    ("photos/ladies-who-launch.jpg", "ladies-who-launch", (720, 1200), 78),
    # phase 1 pages
    ("photos/faye-mission-portrait.jpg", "faye-mission-portrait", (640, 1000), 80),
    ("photos/faye-wall-bars.jpg", "faye-wall-bars", (600, 1000), 80),
    ("photos/faye-neon-kick.jpg", "faye-neon-kick", (640, 1000), 80),
    ("photos/faye-flex.png", "faye-flex", (749,), 82),
    ("photos/faye-portrait-white.png", "faye-portrait-white", (640,), 82),
    ("photos/faye-coaching-conversation.png", "faye-coaching-conversation", (720, 1200), 80),
    ("photos/faye-consulting.jpg", "faye-consulting", (600, 805), 80),
    ("photos/faye-hackney-moves-stage.png", "faye-hackney-moves", (720, 1400), 78),
    ("photos/faye-athena-effect-speaking.jpg", "faye-athena-effect", (600, 1000), 80),
    ("photos/faye-panel-discussion.jpg", "faye-panel", (600, 1000), 80),
    ("photos/ladies-who-launch-crowd.jpg", "lwl-crowd", (720, 1400), 78),
    ("photos/retreat-pool-overhead.jpg", "retreat-pool", (640,), 80),
    ("photos/faye-beach-kick.jpg", "faye-beach-kick", (661,), 80),
    ("photos/davina-fit-jam.jpg", "davina-fit-jam", (668,), 80),
    ("backgrounds/purple-smoke.png", "purple-smoke", (1600,), 70),
    # sub-brand and concept logos (transparent)
    ("logo/mindfit-retreats-blue.png", "logo/mindfit-retreats-white", (520,), 90, "#FDFDFD"),
    ("logo/concepts/fit-jam.png", "logo/fit-jam", (420,), 90),
    ("logo/concepts/fit-flow.png", "logo/fit-flow", (420,), 90),
    ("logo/concepts/fit-combat.png", "logo/fit-combat", (420,), 90),
    ("logo/concepts/fit-stretch.png", "logo/fit-stretch", (420,), 90),
    ("logo/concepts/fit-strength.png", "logo/fit-strength", (420,), 90),
    ("logo/concepts/fit-bands.png", "logo/fit-bands", (420,), 90),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src, name, widths, quality, *tint in IMAGES:
        im = Image.open(SRC / src)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        if tint:
            solid = Image.new("RGBA", im.size, tint[0])
            solid.putalpha(im.getchannel("A"))
            im = solid
        if name.startswith("logo/") and im.mode == "RGBA":
            # logos: drop empty transparent margins so they size to their artwork
            im = im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())
        for w in widths:
            w = min(w, im.width)
            h = round(im.height * w / im.width)
            out = OUT / f"{name}-{w}.webp"
            out.parent.mkdir(parents=True, exist_ok=True)
            im.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=quality, method=6)
            print(f"{out.relative_to(ROOT)}  {w}x{h}  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
