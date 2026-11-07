#!/usr/bin/env python3
"""Give every YouTube video on the site its own thumbnail, stored on the site.

    python3 tools/fetch-thumbnails.py          # fetch what's missing, update the pages
    python3 tools/fetch-thumbnails.py --check  # fail if any video has no thumbnail

Every video is a click-to-play cover (<button data-youtube="ID">, assets/js/video.js). This
finds each one in public/*.html, downloads that video's thumbnail from YouTube's image server
once, and keeps it as an original in brand/thumbs/ (never overwritten; delete one to fetch it
again). From it the tool writes web copies to public/assets/img/thumbs/ and points the cover's
<img> at them: a wide copy (16:9) for wide players and a tall copy (9:16) for the tall ones.
A Short shown in a wide player gets its upright frame centred on a blurred copy of itself.
Visitors are served these copies from the site itself, so nothing is requested from YouTube
until someone presses play. Making copies needs Pillow and network access to i.ytimg.com;
--check needs neither, and runs before every push.

Thumbnail sizes YouTube may have, best first: maxresdefault and hq720 (1280x720), then
sddefault (640x480) and hqdefault (480x360), which carry black bars above and below a 16:9
picture; those bars are trimmed. Shorts also have a tall frame (oar2), used for tall players.
"""
import re
import sys
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
ORIG = ROOT / "brand" / "thumbs"
OUT = PUBLIC / "assets" / "img" / "thumbs"
WIDE = ("maxresdefault", "hq720", "sddefault", "hqdefault")
TALL = ("oar2",)
WIDE_W, TALL_W = 640, 360

# a cover: the player's div (its class says wide or tall), the button with the video's id,
# then the poster <img> the tool owns
COVER = re.compile(
    r'(<div class="(?P<cls>video[^"]*)">\s*<button type="button" data-youtube="(?P<id>[^"]+)"[^>]*>\s*)'
    r'<img [^>]*>')


def fetch(vid: str, names) -> bytes | None:
    from PIL import Image
    for name in names:
        try:
            with urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/{name}.jpg", timeout=30) as r:
                data = r.read()
        except urllib.error.HTTPError:
            continue
        # YouTube answers a missing size with a small grey placeholder
        if Image.open(BytesIO(data)).width > 120:
            return data
    return None


def trim_bars(im):
    """Cut the black bars YouTube pads 4:3 thumbnails with."""
    g = im.convert("L")
    w, h = g.size
    def dark(y):
        row = g.crop((0, y, w, y + 1)).getdata()
        return sum(row) / w < 18
    top, bottom = 0, h
    while top < h // 4 and dark(top):
        top += 1
    while bottom > h - h // 4 and dark(bottom - 1):
        bottom -= 1
    return im.crop((0, top, w, bottom))


def cover_crop(im, ratio: float):
    """Centre-crop to width/height = ratio."""
    w, h = im.size
    if w / h > ratio:
        nw = round(h * ratio)
        return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = round(w / ratio)
    return im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def framed_short(tall, w: int, h: int):
    """A Short in a wide player: its upright frame, whole, centred on a blurred, darkened
    copy of itself, the way YouTube shows Shorts sideways."""
    from PIL import Image, ImageEnhance, ImageFilter
    bg = cover_crop(tall, w / h).resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(.45)
    fw = round(h * tall.width / tall.height)
    bg.paste(tall.resize((fw, h), Image.LANCZOS), ((w - fw) // 2, 0))
    return bg


def originals(vid: str) -> tuple[Path, Path | None]:
    """Download (once) the wide thumbnail and, where there is one, the tall frame."""
    ORIG.mkdir(parents=True, exist_ok=True)
    wide, tall = ORIG / f"{vid}.jpg", ORIG / f"{vid}-tall.jpg"
    if not wide.exists():
        data = fetch(vid, WIDE)
        if data is None:
            sys.exit(f"no thumbnail on YouTube for {vid}")
        wide.write_bytes(data)
        print(f"fetched {wide.relative_to(ROOT)}")
    if not tall.exists() and not (ORIG / f"{vid}-tall.none").exists():
        data = fetch(vid, TALL)
        if data:
            tall.write_bytes(data)
            print(f"fetched {tall.relative_to(ROOT)}")
        else:
            (ORIG / f"{vid}-tall.none").write_text("YouTube has no tall frame for this video\n")
    return wide, (tall if tall.exists() else None)


def web_copy(vid: str, shape: str) -> tuple[str, int, int]:
    """Write (once) the web copy for a wide or tall player; return its URL and size."""
    OUT.mkdir(parents=True, exist_ok=True)
    w = WIDE_W if shape == "wide" else TALL_W
    h = round(w * 9 / 16) if shape == "wide" else round(w * 16 / 9)
    out = OUT / f"{vid}-{shape}.webp"
    if not out.exists():
        from PIL import Image  # only needed to make copies; --check runs without it
        wide, tall = originals(vid)
        if shape == "tall" and tall:
            im = cover_crop(Image.open(tall).convert("RGB"), w / h).resize((w, h), Image.LANCZOS)
        elif shape == "wide" and tall:
            im = framed_short(Image.open(tall).convert("RGB"), w, h)
        else:
            im = cover_crop(trim_bars(Image.open(wide).convert("RGB")), w / h).resize((w, h), Image.LANCZOS)
        im.save(out, "WEBP", quality=80, method=6)
        print(f"wrote {out.relative_to(ROOT)}  {w}x{h}")
    return f"/assets/img/thumbs/{vid}-{shape}.webp", w, h


def main() -> None:
    check = "--check" in sys.argv
    problems = []
    for page in sorted(PUBLIC.glob("*.html")):
        html = page.read_text()

        def poster(m):
            vid, shape = m["id"], ("wide" if "wide" in m["cls"].split() else "tall")
            if check:
                url = f"/assets/img/thumbs/{vid}-{shape}.webp"
                if not (PUBLIC / url.lstrip("/")).exists() or url not in m.group(0):
                    problems.append(f"{page.name}: {vid} has no thumbnail")
                return m.group(0)
            url, w, h = web_copy(vid, shape)
            return f'{m.group(1)}<img src="{url}" width="{w}" height="{h}" loading="lazy" alt="">'

        new = COVER.sub(poster, html)
        found = len(COVER.findall(html))
        if found != html.count("data-youtube="):
            problems.append(f"{page.name}: a video cover isn't in the usual shape")
        if new != html:
            page.write_text(new)
            print(f"updated {page.relative_to(ROOT)}")
    if problems:
        sys.exit("\n".join(problems))
    if check:
        print("every video has its thumbnail")


if __name__ == "__main__":
    main()
