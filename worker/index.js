// F.I.T API — runs only for /api/* (see run_worker_first in wrangler.jsonc).
// Every other request is served straight from public/ by Cloudflare's asset handler.
// Later phases add routes here: checkout, Stripe webhooks, bookings, notifications.

const SECURITY_HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "no-store",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
};

export function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), { status, headers: { ...SECURITY_HEADERS, ...extra } });
}

const routes = {
  "GET /api/health": (_req, env) =>
    json({ ok: true, service: "fit-api", release: env.RELEASE ?? "dev", time: new Date().toISOString() }),
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);

    const handler = routes[`${request.method} ${url.pathname}`];
    if (handler) {
      try {
        return await handler(request, env, url);
      } catch (err) {
        console.error("api error", url.pathname, err);
        return json({ ok: false, error: "server_error" }, 500);
      }
    }
    const known = Object.keys(routes).some((r) => r.endsWith(` ${url.pathname}`));
    return known
      ? json({ ok: false, error: "method_not_allowed" }, 405)
      : json({ ok: false, error: "not_found" }, 404);
  },
};
