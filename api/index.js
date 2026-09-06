// Kleine API voor de U7-trainingsplanner (sites/training/).
//
// Dit is de Worker-kant van het "prototypes"-project (zie ../wrangler.toml).
// Alle statische bestanden in sites/ worden nog altijd rechtstreeks als assets
// geserveerd; enkel /api/* komt hier terecht (run_worker_first).
//
// Opslag: één KV-namespace (binding TRAINING) met deze keys:
//   t:<id>      → één training (JSON, met "version"), metadata = korte samenvatting
//   library     → eigen oefeningen + trainersnamen (JSON, met "version")
//
// Geen login: iedereen met de link mag lezen en schrijven. Om elkaars werk niet
// stilletjes te overschrijven stuurt de client bij elke PUT de versie mee die
// hij las (baseVersion); klopt die niet meer, dan antwoordt de API 409 met de
// huidige inhoud en laadt de client die opnieuw.

const PREFIX = "/api/training";
const MAX_BODY = 512 * 1024; // 512 KB is ruim voldoende voor één training

const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extra,
    },
  });

const newId = () =>
  Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

async function readBody(request) {
  const text = await request.text();
  if (text.length > MAX_BODY) throw new Error("body te groot");
  return text ? JSON.parse(text) : {};
}

function summary(doc) {
  return {
    title: String(doc.title || "").slice(0, 120),
    date: String(doc.date || "").slice(0, 20),
    time: String(doc.time || "").slice(0, 10),
    updatedAt: doc.updatedAt || null,
    minutes: Array.isArray(doc.blocks)
      ? doc.blocks.reduce((s, b) => s + (Number(b.duration) || 0), 0)
      : 0,
    blocks: Array.isArray(doc.blocks) ? doc.blocks.length : 0,
  };
}

// Schrijft een document met optimistic locking. Geeft {ok, doc} of {conflict, doc}.
async function putVersioned(kv, key, incoming, baseVersion, meta) {
  const current = await kv.get(key, "json");
  const currentVersion = current ? current.version || 0 : 0;
  if (current && baseVersion !== undefined && baseVersion !== currentVersion) {
    return { conflict: true, doc: current };
  }
  const doc = { ...incoming, version: currentVersion + 1, updatedAt: new Date().toISOString() };
  await kv.put(key, JSON.stringify(doc), meta ? { metadata: meta(doc) } : undefined);
  return { ok: true, doc };
}

async function handleApi(request, env) {
  const kv = env.TRAINING;
  if (!kv) return json({ error: "KV-binding TRAINING ontbreekt" }, 500);

  const url = new URL(request.url);
  const path = url.pathname.slice(PREFIX.length).replace(/\/+$/, "") || "/";
  const method = request.method.toUpperCase();

  // --- Oefeningenbibliotheek + trainers -------------------------------------
  if (path === "/library") {
    if (method === "GET") {
      const doc = (await kv.get("library", "json")) || { version: 0, exercises: [], trainers: [] };
      return json(doc);
    }
    if (method === "PUT") {
      const body = await readBody(request);
      const incoming = {
        exercises: Array.isArray(body.exercises) ? body.exercises : [],
        trainers: Array.isArray(body.trainers) ? body.trainers : [],
        settings: body.settings && typeof body.settings === "object" ? body.settings : {},
      };
      const r = await putVersioned(kv, "library", incoming, body.baseVersion);
      return r.conflict ? json({ conflict: true, current: r.doc }, 409) : json(r.doc);
    }
    return json({ error: "method not allowed" }, 405);
  }

  // --- Trainingen -------------------------------------------------------------
  if (path === "/trainings") {
    if (method === "GET") {
      const items = [];
      let cursor;
      do {
        const page = await kv.list({ prefix: "t:", cursor });
        for (const k of page.keys) items.push({ id: k.name.slice(2), ...(k.metadata || {}) });
        cursor = page.list_complete ? undefined : page.cursor;
      } while (cursor);
      items.sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")) || String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")));
      return json({ trainings: items });
    }
    if (method === "POST") {
      const body = await readBody(request);
      const id = newId();
      const r = await putVersioned(kv, "t:" + id, body.doc || {}, undefined, summary);
      return json({ id, ...r.doc }, 201);
    }
    return json({ error: "method not allowed" }, 405);
  }

  const m = path.match(/^\/trainings\/([a-z0-9]+)$/);
  if (m) {
    const key = "t:" + m[1];
    if (method === "GET") {
      const doc = await kv.get(key, "json");
      return doc ? json({ id: m[1], ...doc }) : json({ error: "niet gevonden" }, 404);
    }
    if (method === "PUT") {
      const body = await readBody(request);
      const r = await putVersioned(kv, key, body.doc || {}, body.baseVersion, summary);
      return r.conflict
        ? json({ conflict: true, current: { id: m[1], ...r.doc } }, 409)
        : json({ id: m[1], ...r.doc });
    }
    if (method === "DELETE") {
      await kv.delete(key);
      return json({ ok: true });
    }
    return json({ error: "method not allowed" }, 405);
  }

  return json({ error: "onbekende route" }, 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith(PREFIX)) {
      try {
        return await handleApi(request, env);
      } catch (err) {
        return json({ error: String(err && err.message || err) }, 400);
      }
    }
    // Alles wat geen asset was, komt hier terecht: gewoon de 404 van de assets.
    if (env.ASSETS) return env.ASSETS.fetch(request);
    return new Response("Not found", { status: 404 });
  },
};
