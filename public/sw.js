// Service worker: makes the site installable and keeps a working shell offline.
// Bump VERSION with every release so installed copies fetch the new files.
const VERSION = "2.6";
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

function fetchAndKeep(req) {
  return fetch(req).then((res) => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
    return res;
  });
}

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  // Only same-origin GETs; the API, payments and sign-in always go to the network.
  if (req.method !== "GET" || url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;

  // Pictures and fonts never change in place (a new picture gets a new name), so the cached
  // copy is always right: answer from cache, fetch only what isn't there yet.
  if (url.pathname.startsWith("/assets/img/") || url.pathname.startsWith("/assets/fonts/")) {
    event.respondWith(caches.match(req).then((hit) => hit || fetchAndKeep(req)));
    return;
  }

  // Pages, styles and scripts: freshest copy first, so a page and its styles always come from
  // the same release; the cached copy when offline, and the offline page for pages never seen.
  event.respondWith(
    fetchAndKeep(req).catch(() =>
      // ignoreSearch: pages ask for /assets/css/site.css?v=…, the shell cached it without
      caches.match(req, { ignoreSearch: true }).then((hit) => hit || (req.mode === "navigate" ? caches.match("/offline") : Response.error())),
    ),
  );
});
