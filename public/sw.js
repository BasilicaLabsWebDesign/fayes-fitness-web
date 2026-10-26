// Service worker: makes the site installable and keeps a working shell offline.
// Bump VERSION with every release so installed copies fetch the new files.
const VERSION = "2.0";
const CACHE = `fit-${VERSION}`;

const CORE = [
  "/",
  "/offline",
  "/manifest.webmanifest",
  "/favicon.svg",
  "/assets/css/tokens.css",
  "/assets/css/site.css",
  "/assets/css/home.css",
  "/assets/css/pages.css",
  "/assets/js/app.js",
  "/assets/fonts/montserrat-400.woff2",
  "/assets/fonts/montserrat-500.woff2",
  "/assets/fonts/montserrat-700.woff2",
  "/assets/fonts/montserrat-900.woff2",
  "/assets/img/logo/fit-logo-white.svg",
  "/assets/img/particles-1280.webp",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  // Only same-origin GETs; the API, payments and sign-in always go to the network.
  if (req.method !== "GET" || url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;

  if (req.mode === "navigate") {
    // Pages: freshest copy first, the cached copy if offline, then the offline page.
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          if (res.ok) caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match("/offline"))),
    );
    return;
  }

  // Everything else: answer from cache straight away, refresh it in the background.
  event.respondWith(
    caches.match(req).then((hit) => {
      const fresh = fetch(req)
        .then((res) => {
          if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
          return res;
        })
        .catch(() => hit || Response.error());
      return hit || fresh;
    }),
  );
});
