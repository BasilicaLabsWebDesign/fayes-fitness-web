# F.I.T — Faye's Intentional Training

The website and booking app for Faye Edwards: classes, retreats, coaching and events, with
customer accounts, purchases and notifications, in the F.I.T brand. It runs on Cloudflare
Workers: plain static pages in `public/` plus a small API Worker in `worker/`.

> **Status:** version 2 is being built on the working branch and previewed on Cloudflare.
> `main` still serves version 1 until v2.0 launches. See `CLAUDE.md` for the build phases.

## Run it locally

```bash
npm install
npm run dev          # http://127.0.0.1:8787 — the site and the API together
```

`GET /api/health` answers `{"ok":true,...}` when the API is up.

## Where things live

| Path | What it is |
| --- | --- |
| `public/` | The site, served as-is — no build step |
| `public/assets/css/tokens.css` | The brand: colours, fonts, sizes from the 2025 Brand Guide |
| `public/assets/css/site.css` | Shared components: header, buttons, cards, footer |
| `public/sw.js`, `public/manifest.webmanifest` | Make the site installable and work offline |
| `public/_headers` | Security headers (including a strict Content Security Policy) and caching |
| `worker/index.js` | The API |
| `firestore.rules` | Database rules — fully closed until accounts arrive |
| `brand/` | Full-size logos and photos (not deployed) |
| `tools/` | Header/footer sync and image optimisation; their output is committed |

## Common edits

- **Header or footer:** edit `tools/partials/header.html` or `footer.html`, then run
  `python3 tools/sync-partials.py`.
- **A new photo:** put the original in `brand/photos/`, add a line to `tools/optimise-images.py`,
  run it (`pip install pillow` first), and use the `.webp` it writes.
- **Colours or type:** `public/assets/css/tokens.css` only.

## Deploying

Cloudflare Workers Builds deploys `main` to production and builds other branches to preview
URLs. Check the configuration before pushing:

```bash
npx wrangler deploy --dry-run
```

## Credits

Montserrat is © The Montserrat Project Authors, used under the SIL Open Font License
(`public/assets/fonts/OFL.txt`). Logos and photography © Faye's Intentional Training Ltd.
