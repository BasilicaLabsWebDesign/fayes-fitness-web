#!/usr/bin/env python3
"""Stamp the shared header and footer into every page in public/.

    python3 tools/sync-partials.py          # update pages
    python3 tools/sync-partials.py --check  # exit 1 if any page is out of date

Edit tools/partials/<name>.html, run this, commit the result. Pages hold the
stamped markup between <!-- partial:name --> and <!-- /partial:name --> comments,
so public/ stays plain HTML that Cloudflare serves with no build step. A new page
can say {{HEADER}} / {{FOOTER}} and the first run fills it in.

It also stamps the release (VERSION in public/sw.js) onto every stylesheet and script
link, e.g. /assets/css/site.css?v=2.4, so a new release's pages can never be paired with
an older release's styles from any cache. Bump VERSION, run this, and every page follows.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
PARTIALS = ROOT / "tools" / "partials"
MARK = ROOT / "public" / "assets" / "img" / "logo" / "fit-mark.svg"
SW = ROOT / "public" / "sw.js"
ASSET_LINK = re.compile(r'((?:href|src)="/assets/(?:css|js)/[^"?]+)(?:\?v=[^"]*)?"')


def release() -> str:
    return re.search(r'const VERSION = "([^"]+)"', SW.read_text()).group(1)


def load_partials() -> dict:
    mark_path = re.search(r' d="([^"]+)"', MARK.read_text()).group(1)
    parts = {}
    for f in sorted(PARTIALS.glob("*.html")):
        parts[f.stem] = f.read_text().strip().replace("{{MARK_PATH}}", mark_path)
    return parts


def page_path(page: Path) -> str:
    """The URL a page is served at: about.html -> /about, index.html -> /."""
    rel = page.relative_to(PUBLIC).with_suffix("")
    return "/" if rel.name == "index" else "/" + rel.as_posix()


def mark_current(body: str, path: str) -> str:
    """Flag the link to this page so the menu shows, and screen readers say, where you are."""
    if path == "/":
        return body
    return body.replace(f'href="{path}"', f'href="{path}" aria-current="page"')


def stamp(html: str, parts: dict, path: str = "", version: str = "") -> str:
    for name, body in parts.items():
        body = mark_current(body, path)
        block = f"<!-- partial:{name} -->\n{body}\n<!-- /partial:{name} -->"
        token = "{{" + name.upper() + "}}"
        if token in html:
            html = html.replace(token, block)
        else:
            html = re.sub(rf"<!-- partial:{name} -->.*?<!-- /partial:{name} -->",
                          lambda _m: block, html, flags=re.S)
    if version:
        html = ASSET_LINK.sub(rf'\1?v={version}"', html)
    return html


def main() -> int:
    check = "--check" in sys.argv
    parts = load_partials()
    version = release()
    stale = []
    for page in sorted(PUBLIC.rglob("*.html")):
        old = page.read_text()
        new = stamp(old, parts, page_path(page), version)
        if new != old:
            stale.append(page.relative_to(ROOT))
            if not check:
                page.write_text(new)
    for p in stale:
        print(("out of date: " if check else "updated: ") + str(p))
    if check and stale:
        return 1
    if not stale:
        print("all pages up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
