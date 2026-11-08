// POST /api/enquiry: adds someone who ticked "Add me to Faye's mailing list" on an enquiry
// form to Faye's Flodesk list, in the segment for their type of enquiry (v2.41).
//
// The Flodesk API key is the Worker secret FLODESK_API_KEY (Cloudflare dashboard → this
// Worker → Settings → Variables and Secrets), never in this repository. Without it the
// route answers 503 not_configured and the form still opens the email to Faye as before.
// Segments are found by name, and created the first time they are needed, so they must
// keep these names in Flodesk (rename one here and in Flodesk together).

import { json } from "./http.js";

const FLODESK = "https://api.flodesk.com/v1";
const ALL = "Website enquiries";
// the forms' "What's it about?" values → the segment each one joins
export const SEGMENTS = {
  classes: "Enquiry: Classes & booking",
  app: "Enquiry: The F.I.T App",
  academy: "Enquiry: F.I.T Academy",
  retreats: "Enquiry: Retreats & experiences",
  presenting: "Enquiry: Fitness presenting",
  speaking: "Enquiry: Speaking & hosting",
  consulting: "Enquiry: Coaching & consulting",
  other: "Enquiry: Something else",
};
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/;

// segment name → id, kept for the life of this Worker instance
let segmentIds = null;

function flodesk(env) {
  const base = env.FLODESK_API_BASE || FLODESK; // overridden only by local tests
  const headers = {
    Authorization: `Basic ${btoa(`${env.FLODESK_API_KEY}:`)}`,
    "Content-Type": "application/json",
    "User-Agent": "FIT website (fayesintentionaltraining.com)",
  };
  return async (method, path, body) => {
    const res = await fetch(base + path, { method, headers, body: body && JSON.stringify(body) });
    if (!res.ok) throw new Error(`flodesk ${method} ${path} → ${res.status}`);
    return res.status === 204 ? null : res.json();
  };
}

async function segmentId(api, name) {
  if (!segmentIds) {
    segmentIds = new Map();
    for (let page = 1; page <= 10; page++) {
      const r = await api("GET", `/segments?page=${page}&per_page=100`);
      for (const s of r?.data ?? []) segmentIds.set(s.name, s.id);
      if ((r?.data ?? []).length < 100) break;
    }
  }
  if (!segmentIds.has(name)) {
    const s = await api("POST", "/segments", { name, color: "#8A2BE2" });
    segmentIds.set(name, s.id ?? s.data?.id);
  }
  return segmentIds.get(name);
}

export async function enquiry(request, env, url) {
  // only this site's own pages may post here
  const origin = request.headers.get("Origin");
  if (origin && origin !== url.origin) return json({ ok: false, error: "forbidden" }, 403);
  if (!(request.headers.get("Content-Type") || "").includes("application/json")) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const raw = await request.text();
  if (raw.length > 4000) return json({ ok: false, error: "too_large" }, 413);
  let d;
  try { d = JSON.parse(raw); } catch { return json({ ok: false, error: "bad_request" }, 400); }

  const name = String(d.name ?? "").trim().slice(0, 120);
  const email = String(d.email ?? "").trim().toLowerCase();
  const segment = SEGMENTS[d.topic];
  // the hidden "website" field is left empty by people and filled in by spam bots
  if (d.website) return json({ ok: true });
  if (d.optin !== true || !name || !EMAIL.test(email) || email.length > 254 || !segment) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  if (!env.FLODESK_API_KEY) return json({ ok: false, error: "not_configured" }, 503);

  const api = flodesk(env);
  const [first, ...rest] = name.split(/\s+/);
  try {
    const ids = [await segmentId(api, ALL), await segmentId(api, segment)];
    await api("POST", "/subscribers", {
      email, first_name: first, last_name: rest.join(" "),
      double_optin: env.FLODESK_DOUBLE_OPTIN === "true",
    });
    await api("POST", `/subscribers/${encodeURIComponent(email)}/segments`, { segment_ids: ids });
  } catch (err) {
    segmentIds = null; // look the segments up afresh next time
    console.error("flodesk", String(err)); // never log the visitor's details
    return json({ ok: false, error: "mailing_list_unavailable" }, 502);
  }
  return json({ ok: true });
}
