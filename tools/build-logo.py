#!/usr/bin/env python3
"""Draw the F.I.T logo as clean vector artwork, in every colourway the site uses.

    python3 tools/build-logo.py

The brand guide only holds the logo as a 1147 x 726 picture, and a trace of it has wobbly
edges when shown large. This rebuilds it exactly instead: the F.I.T letters, dots and name
bar are rounded rectangles measured from that picture (to a tenth of a pixel), and the name
is set in Montserrat Bold - the face it was set in - turned into outlines, so the SVGs need
no font and stay sharp at any size. Needs fontTools + brotli (pip install fonttools brotli).

Writes public/assets/img/logo/fit-logo-{purple,white,black}-hd.svg and fit-mark-hd.svg.
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "assets" / "img" / "logo"
FONT = ROOT / "public" / "assets" / "fonts" / "montserrat-700.woff2"

W, H = 1147, 726
PURPLE, WHITE, BLACK = "#421769", "#FDFDFD", "#000000"

# Letters, measured from the guide's logo: (x, y, width, height). Every stroke is 84.6 wide
# and every bar 82.8 tall; outer corners are rounded at 10 (8 on the dots). Where a bar meets
# a stem the shapes overlap, so the joins stay square.
LETTER_R, DOT_R = 10, 8
LETTERS = [
    (58.3, 0.15, 84.6, 580.0),     # F stem
    (58.3, 0.15, 224.2, 82.8),     # F top bar
    (58.3, 207.25, 224.1, 82.95),  # F middle bar
    (523.75, 0.15, 84.7, 580.0),   # I
    (849.75, 0.15, 261.7, 82.8),   # T top bar
    (849.75, 112.8, 261.7, 82.85), # T second bar
    (938.3, 150.0, 84.6, 430.15),  # T stem (starts inside the second bar)
]
DOTS = [(344.6, 520.55, 70.75, 62.25), (714.1, 520.55, 70.65, 62.25)]
BAR = (0.25, 616.65, 1146.7, 109.2)  # the name bar, rounded at 43
BAR_R = 43

NAME = "FAYE’S INTENTIONAL TRAINING"
NAME_SIZE = 42.93        # px: capitals 30.05 tall (Montserrat's cap height is 700/1000)
NAME_TRACKING = 13.59    # px added after every character
NAME_X, NAME_BASELINE = 38.73, 683.0
# Per-letter nudges (px) that put each letter exactly where the guide's logo has it: all
# within about a pixel, except the opening F and A, which sit a little further right.
NAME_NUDGE = [3.1, 2.2, 0.1, -0.4, -0.45, 0.05, 0,
              -0.2, 0.2, 0, -0.15, 0.35, 0.4, 0.15, 0.15, 0.5, 0.75, 0.25, 0,
              0.6, 0.7, 0.95, 0.65, 1.15, 0.7, 1.2, 1.05]


def rounded_rect(x, y, w, h, r):
    """One closed subpath, drawn clockwise so overlapping shapes fill as one (nonzero)."""
    return (f"M{x + r:.2f} {y:.2f}H{x + w - r:.2f}A{r} {r} 0 0 1 {x + w:.2f} {y + r:.2f}"
            f"V{y + h - r:.2f}A{r} {r} 0 0 1 {x + w - r:.2f} {y + h:.2f}"
            f"H{x + r:.2f}A{r} {r} 0 0 1 {x:.2f} {y + h - r:.2f}"
            f"V{y + r:.2f}A{r} {r} 0 0 1 {x + r:.2f} {y:.2f}Z")


def mark_path() -> str:
    return "".join([rounded_rect(*l, LETTER_R) for l in LETTERS]
                   + [rounded_rect(*d, DOT_R) for d in DOTS])


def name_path() -> str:
    font = TTFont(FONT)
    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    k = NAME_SIZE / font["head"].unitsPerEm
    pen_x, out = NAME_X, []
    for ch, nudge in zip(NAME, NAME_NUDGE, strict=True):
        name = cmap[ord(ch)]
        svg = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        # font units are y-up; flip onto the baseline and scale to size
        glyphs[name].draw(TransformPen(svg, (k, 0, 0, -k, pen_x + nudge, NAME_BASELINE)))
        out.append(svg.getCommands())
        pen_x += hmtx[name][0] * k + NAME_TRACKING
    return "".join(out)


def logo_svg(ink: str, name_ink: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{title}"><title>{title}</title>'
            f'<path fill="{ink}" d="{mark_path()}{rounded_rect(*BAR, BAR_R)}"/>'
            f'<path fill="{name_ink}" d="{name_path()}"/></svg>\n')


def main() -> None:
    title = "F.I.T — Faye’s Intentional Training"
    files = {
        "fit-logo-purple-hd.svg": logo_svg(PURPLE, WHITE, title),  # for light backgrounds
        "fit-logo-white-hd.svg": logo_svg(WHITE, PURPLE, title),   # for dark backgrounds
        "fit-logo-black-hd.svg": logo_svg(BLACK, WHITE, title),
        "fit-mark-hd.svg": (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 583" '
                            f'role="img" aria-label="F.I.T"><title>F.I.T</title>'
                            f'<path fill="currentColor" d="{mark_path()}"/></svg>\n'),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg)
        print(f"{name}  {len(svg) // 1024 + 1} KB")


if __name__ == "__main__":
    main()
