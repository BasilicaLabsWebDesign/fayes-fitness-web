# CLAUDE.md

Standing policy for this repository. Read it before making any change here.

## What this repo is

The website and booking app for **F.I.T — Faye's Intentional Training**, the business of
Faye Edwards (Faye's Intentional Training Ltd). It replaces her Fibodo storefront and her
Linktree with one site she owns: customer purchases, customer accounts, and notifications to
customers and to Faye.

It is version 2 — a ground-up rebuild of version 1 (a one-page site, v1.0–v1.12). v2.0 put the
rebuilt public site on `main`; the remaining phases ship as v2.x releases. **Work happens on
the working branch `claude/repo-to-website-0442wi`** (Cloudflare builds it to a private
preview URL), and every verified batch is released by fast-forwarding `main` onto it.

## Architecture

```
Phone / browser (installable app: manifest + service worker)
  │   pages: plain static files in public/, served by Cloudflare
  ├── sign in ─────────────► Firebase Auth                      (phase 2)
  ├── read own data ───────► Firestore — browsers never write money-related data
  └── /api/* ──► Cloudflare Worker (worker/index.js)
                    ├──► Stripe: checkout, memberships, card portal   (phase 4)
                    ├──► Firestore: orders, bookings — only the Worker writes these
                    ├──► Email to customers and to Faye              (phase 5)
                    └──► Push notifications; cron for reminders and digests
```

The Worker runs only for `/api/*` (`run_worker_first` in `wrangler.jsonc`); every other
request is served straight from `public/` by Cloudflare's asset handler.

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Foundations: repo layout, design system, installable shell, Worker skeleton, locked database rules | done |
| 1 | Public site: home, about, services (app, presenting, consulting, speaking), academy, experiences, book (timetable, memberships, vouchers — on Fibodo until phase 4), Work with Faye, contact | done |
| 2 | Accounts: Firebase sign-up/in (email, Google, Apple), profile, settings, delete account | next — needs Firebase project |
| 3 | Faye's admin: services, timetable, capacity | |
| 4 | Purchases: Stripe test mode, memberships, vouchers, retreat deposits + instalments, QR check-in | needs Stripe |
| 5 | Notifications: emails, in-app messages, reminders, push, Faye's digest | needs email provider + DNS |
| 6 | Go live: legal pages from a data audit, Stripe live, domain, Fibodo cutover | |

## Repository layout

```
public/                 everything served (no build step — these files are the site)
  index.html 404.html offline.html
  about services app presenting consulting speaking academy experiences
  work-with-faye book contact .html   (served without .html: /about, /book …)
  manifest.webmanifest  sw.js  favicon.svg  apple-touch-icon.png  icons/
  _headers              security headers (incl. CSP) + caching
  _redirects            v1 addresses (/why, /retreats/zanzibar …) → their v2 pages; never remove
  assets/css/           tokens.css (brand) → site.css (components) → home.css | pages.css
  assets/js/app.js      menu + service-worker registration
  assets/js/video.js    YouTube facades: nothing loads from YouTube until play is pressed
  assets/js/enquiry.js  enquiry form → pre-filled email to Faye (→ /api/enquiry in phase 5)
  assets/fonts/         Montserrat, self-hosted (OFL.txt beside it)
  assets/img/           web-sized WebP from tools/optimise-images.py; logo/ = traced SVGs
worker/index.js         the API (Cloudflare Worker)
firestore.rules         database rules (closed until phase 2) — firebase.json points at it
brand/                  full-size originals: logos, photos, backgrounds — NOT deployed
tools/                  authoring tools; their output is committed
  partials/             shared header.html + footer.html
  sync-partials.py      stamps partials into every page
  optimise-images.py    brand/ originals → public/assets/img/*.webp
prompt text/            the archive for the version in service (see below)
```

## Working rules

- **No build step for the site.** `public/` is served as-is. Tools in `tools/` produce files
  that are committed; Cloudflare never runs them.
- **Header and footer are partials.** Edit `tools/partials/*.html`, then
  `python3 tools/sync-partials.py`. `--check` fails if any page is stale. A new page writes
  `{{HEADER}}` / `{{FOOTER}}` and the first run fills them in.
- **Images:** add the original to `brand/`, a line to `IMAGES` in `tools/optimise-images.py`,
  run it (needs Pillow), commit the WebP. Image URLs are cached as immutable — a changed
  picture gets a new file name, never an in-place edit.
- **CSP is strict** (`public/_headers`): no inline `<script>`, no inline `style=""`, no
  third-party origins. When a phase adds a third party (Firebase, Stripe, YouTube embeds),
  add exactly its origins to the right directive in the same commit. So far:
  `frame-src https://www.youtube-nocookie.com` (phase 1, video facades).
- **Service worker:** bump `VERSION` in `public/sw.js` with every release, and add new core
  files to `CORE`. The API is never cached.
- **Fonts are self-hosted** so no visitor data goes to Google; keep it that way.
- **Database:** nothing money-related (orders, bookings, memberships, vouchers, payments)
  is ever writable from a browser. Only the Worker writes those, with server credentials.
- **Accessibility is part of the brand** (the guide's personas run from 28 to 55): body text
  ≥ 17px, contrast AA, tap targets ≥ 48px, visible focus, reduced-motion respected.

## Brand rules (F.I.T 2025 Brand Guide — `prompt text/1/F.I.T_2025_Brand_Guide.pdf`)

- **Colours:** primary (backgrounds) Honey Flower `#421769`, Blue Violet `#8A2BE2`,
  Hot Purple `#BF00FF`, Black `#000000`; supporting (text, accents) Ocean `#036FA5`,
  Cobalt `#0047AB`, Persian Rose `#F715AB`, Off White `#FDFDFD`. Tokens in `tokens.css`.
- **Contrast:** text on hot purple or persian rose is black, never white. Never set text in
  hot purple on honey flower, cobalt on hot purple, rose on cobalt, or honey flower on hot
  purple (all under 3:1) — those pairings are decoration only.
- **Concept colours:** Jam = rose, Flow = ocean, Combat = black, Stretch = violet,
  Strength = cobalt, Bands = hot purple. Use them to colour-code classes.
- **Type:** Montserrat — Black for titles (uppercase, wide tracking), Bold for headings,
  Medium for subheadings, Regular for body. Blandit is for the logo only: the logo is
  artwork (`assets/img/logo/*.svg`, traced from the guide), never typed text.
- **Logo:** purple on light backgrounds, white (with purple tagline) on dark; the F.I.T mark
  without tagline is an approved additional mark (used in the header).
- **Look:** black canvas, particle/smoke backgrounds, thin rule lines framing titles,
  tilted black-framed photos.
- **Voice:** uplifting, friendly, enthusiastic. About how people *feel*, never aesthetics or
  physical goals. Talk like a close friend. Tagline: "Focus on the feeling."
- **Audiences:** Move with Faye (participants — Mandy, Grace), Grow with Faye (instructors —
  Paul, Penny), Work with Faye (brands and event organisers, from Faye's deck).
- **Family logos — always use them:** F.I.T (`fit-logo-*.svg`), F.I.T Academy (the winged F/A,
  `fit-academy-*.svg`, traced from the deck), MindFit Retreats (`mindfit-retreats-*`), and the
  six concept logos (`fit-jam` … `fit-bands`). Originals live in `brand/logo/`.

## Source of truth for content

**Faye's deck (`prompt text/1/FAYEs_DECK.pdf`, June 2026) is the latest information** and
wins over older sources (the Fibodo export, the v1 site, Flodesk emails). From it:
email `faye@fayesintentionaltraining.com`, phone 07539 734633, Instagram @fayes_fitness,
TikTok @fayesfitness, Facebook @fayesfitness, LinkedIn @fayeedwards, YouTube @fayeedwards;
her bio, mission, the F.I.T ecosystem, services and clients.

## Local development

```bash
npm install
npm run dev                 # wrangler dev — site + API on http://127.0.0.1:8787
curl http://127.0.0.1:8787/api/health
```

## Verification — before every push

1. `python3 tools/sync-partials.py --check`
2. `npx wrangler deploy --dry-run`
3. Run `wrangler dev` and drive it with headless Chromium at phone (390px) and desktop
   (1440px) widths: no console errors, no CSP violations, fonts loaded, menu works,
   service worker controls the page, offline fallback works. **Look at the screenshots.**
4. `/api/health` answers `{"ok":true}`; unknown API paths answer JSON 404.

Never leave pushed work unverified or half-finished. Work in small, complete batches:
implement, verify, commit, push.

## Git and release workflow

- Before committing: `git config user.name "Fid" && git config user.email "fid_kk@proton.me"`,
  and after the first commit confirm with `git log -1 --format='%an <%ae>'`.
- Develop on the working branch and push there first. Release verified work by
  fast-forwarding `main` onto it and pushing `main`.
- Every push to `main` is a release. Versions are an ascending `vMAJOR.MINOR` sequence; every
  push bumps the minor regardless of size; a major bump is reserved for a ground-up overhaul
  (v2.0 is one).
- With every push to `main`, provide release-tag text in the reply, in exactly this shape.
  The owner creates the GitHub release manually — **never push tags**:

  ```
  Tag: v<next>  —  Title: <five to nine words, plain and evocative>
  Description: <one to three sentences of editorial prose describing what changed
  from the owner's point of view — outcomes, not implementation. No bullet lists,
  no jargon, no file names.>
  ```

- Append the release line to the ledger below as part of the same push.
- Commit messages: descriptive imperative first line (what the change does, not
  "update X"), then a short prose body; dash bullets are fine there. One commit per coherent
  piece of work; several may share a push, but each push gets exactly one version entry.
- Never include model names, AI attribution trailers, session links, or other tooling
  identifiers in commit messages, titles, release text or code.

## Prompt archive

`prompt text/` holds the records for the version currently in service - nothing else.
Shipping version N replaces the folder's contents wholesale, in the same push that releases
the version: remove the previous version's folder(s) and add `prompt text/N/` containing
`input.txt` (the prompt, byte for byte), `output.txt` (the reply that shipped it, byte for
byte), `ai model.txt` (three lines: Anthropic / Claude / Fable 5 Max unless the owner directs
otherwise, or the model that truly did the work) and every input image and file the owner
provided, each under its own name. The files are owner-supplied records: never edit,
reformat, trim or regenerate them.

`prompt text/1/` shipped with v2.0: every owner message from the start of the rebuild to that
release, the brand guide, the deck and the old site's zip. The next release that ships new
owner words starts `prompt text/2/`.

## Go-live checklist (phase 6)

- [ ] Domain fayesintentionaltraining.com (the deck's) attached in Cloudflare
- [ ] Every social link clicked through: the deck's handles were built into URLs without
      being opened (this environment cannot reach those sites)
- [ ] Absolute `og:image` / `og:url` / canonical tags, sitemap.xml and the robots Sitemap line
- [ ] App Store and Google Play links on /app opened and confirmed
- [ ] Retreat dates, venues and availability on /experiences confirmed with Faye
- [ ] Book page's interim Fibodo links (timetable, memberships, vouchers) replaced by
      the site's own booking (phase 4)
- [ ] Company registration number in the footer (UK companies must show it on their website)
- [ ] Privacy, terms, cookie and account-deletion pages from a data audit (app-legal-admin)
- [ ] Firestore rules published; Firebase authorised domains include the live domain
- [ ] Stripe in live mode; webhook endpoint registered for the live domain
- [ ] Email sending domain verified (SPF/DKIM)
- [ ] `sw.js` VERSION and the `RELEASE` var in `wrangler.jsonc` match the release (every release)

## Owner inputs still needed

- Firebase project, Stripe account (in the Ltd's name), email provider + DNS access
- Offerings, prices, timetable, membership plans, voucher amounts, cancellation/refund policy
- Full-size originals of the pool and beach photos
- Whether to show partner logos (permission) or names only

## Release ledger

Releases v1.0–v1.12 are version 1 (the one-page site), recorded from the release notes
handed back with each push. v2.0 onwards is the rebuild.

| Version | Title | Description |
| --- | --- | --- |
| v1.0 | The F.I.T site goes live | Faye's site now exists as a real, deployable page — the full F.I.T one-pager with the camp countdown, retreats, app, book and video, ready to serve from Cloudflare. Wrong turns land on a proper branded page instead of a blank error, and content edits like dates or prices go live the moment they're pushed. |
| v1.1 | The portrait in her real colours | Faye's hero photo now appears exactly as it was taken, instead of being drained to grayscale and washed with the brand pink. The picture reads as a photograph again while the wordmark across it stays perfectly legible. |
| v1.2 | Her name no longer hides behind the photo | The hero portrait was sitting high enough to swallow the bottom of "Faye", leaving the name hard to read on every screen size. The photo now rests just beneath the name, so it reads cleanly while keeping the layered look that carries the page. |
| v1.3 | Every link now lands on her own site | Everything Faye points people to — the camp, both trips, the academy, the community, the app, the webinar, the book and the video — now has a proper page on her own domain, styled to match, with a single links page gathering them all. Visitors arrive somewhere that looks like hers instead of being handed straight to someone else's platform. The new pages carry only the details the site already published, so the deeper content still needs writing. |
| v1.4 | The pages now speak with her voice | Every inner page has been rebuilt from what Faye's own materials actually say — the camp's real programme, the Zanzibar retreat's sold-out history at Zen Boutique Resort, the app's true class list with app-store links, the book's publisher description. The site now keeps visitors on Faye's own pages until the moment they book or sign up, and all booking goes to her current Bookwhen page. |
| v1.5 | The trips get their postcard views | The Zanzibar and Bulgaria pages now open with their destination artwork — the sunset over the Indian Ocean and the steaming mountain pool — instead of going straight to text. Arriving on a trip page now feels like the place before you've read a word. |
| v1.6 | Her pages stop passing visitors along | The trip, academy and community pages no longer send anyone back to the old hosted pages — reserving a retreat spot or joining now happens right there, by email to Faye with the subject already filled in. The only links that still leave the site are the true points of purchase: booking a class, getting the app, buying the book. |
| v1.7 | The brochures live on her site now | The Zanzibar and Bulgaria pages now hold everything the email brochures said — the full descriptions, the three retreat pillars, complete what's-included lists, real prices, deposits and instalment plans — presented in the site's own style. Bulgaria gets a booking grid with a button for every room type and payment option, ready for the real payment links to be dropped in. |
| v1.8 | Zanzibar sells itself in pictures now | The Zanzibar page now leads with the retreat's real photographs — the class in full flow and a grid of moments from the trip — while the writing gets out of the way: shorter, punchier, with "September sold out, six rooms left" as the first thing a visitor reads. Bulgaria gets the same tightening while it waits for its own photo. |
| v1.9 | Real moments replace the drawings | Both trip pages now open on photography instead of illustration — Zanzibar greets visitors with the class mid-session, and Bulgaria's page is ready to do the same the moment the crew photo is added, falling back gracefully to its artwork until then. |
| v1.10 | The site now argues its own case | A new "Why this site" page tells the story of the upgrade — from a bio link that scattered people across six other platforms to one home where every offer is pitched in Faye's own brand. It ends on the reassurance that every page address is permanent, so even a return to the old link-list way would break nothing. |
| v1.11 | The Book button steps out of the shadows | The booking button in the top bar was being painted over by the styling of the tilted book cover further down the page — near-invisible on two of the five styles, and slightly askew on all of them. It now shows its true colours everywhere. The Zanzibar page also gains proper payment options to match Bulgaria: pay in full, instalments, or a deposit to secure the room. |
| v1.12 | The Why tab earns its place up top | The page that sells the whole concept was hiding in the footer where nobody would find it. It now has a proper tab in the top bar of every page, so the story of the site — one place instead of a list of links — is one tap away from anywhere. |
| v2.0 | Faye's whole world in one rebuilt site | The one-page site gives way to a full site built from Faye's 2025 brand and her latest deck, with pages for her classes and app, presenting, consulting, speaking, the Academy, retreats and working with brands, and enquiries that arrive as a ready-written email to Faye. It installs on a phone like an app and still opens offline, and every old address now lands on the page that covers it. |

Next release: **v2.1**.
