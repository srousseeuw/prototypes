// Wedstrijdbot als Cloudflare Worker.
//
//   cron   → zoekt de bronnen af, kiest wat nuttig is voor het gezin en
//            schrijft in. Wat al gedaan is, staat in KV en gebeurt geen
//            tweede keer.
//   fetch  → de digest op een geheim pad (/<DIGEST_PAD>), zodat je 's ochtends
//            kan nakijken wat er gebeurd is. Al de rest geeft 404.
//   email  → als je wedstrijden@ocior.be via Cloudflare Email Routing hierheen
//            stuurt: bevestigingslinks aanklikken en de rest doorsturen naar je
//            gewone mailbox.
import { verzamel } from "./bronnen.js";
import { kies } from "./selectie.js";
import { deelnemen } from "./deelnemen.js";
import { BRONNEN, INSTELLINGEN } from "./config.js";
import { bouwDigest } from "./digest.js";
import { budget } from "./budget.js";
import { bouwDiagnosePagina, onderzoek } from "./diagnose.js";

const wacht = (ms) => new Promise((klaar) => setTimeout(klaar, ms));

function sleutel(url) {
  return "gezien:" + url.split("#")[0].replace(/\/+$/, "").toLowerCase();
}

function deelnemerUit(env) {
  let rauw = {};
  try {
    rauw = JSON.parse(env.DEELNEMER || "{}");
  } catch {
    throw new Error("DEELNEMER is geen geldige JSON — zie README");
  }
  return {
    ...rauw,
    volledigeNaam: [rauw.voornaam, rauw.achternaam].filter(Boolean).join(" "),
    nieuwsbriefToestaan: rauw.nieuwsbriefToestaan === true,
  };
}

async function ronde(env, { dryRun }) {
  const log = [];
  const noteer = (regel) => log.push(regel);

  // Elke fetch telt mee tegen de subrequest-limiet van het Cloudflare-plan
  // (50 gratis, 1000 betaald). Loopt die vol, dan mislukt alles wat daarna
  // komt — vandaar dat we zelf tellen en op tijd stoppen.
  budget.reset(Number(env.MAX_SUBREQUESTS || INSTELLINGEN.maxSubrequests));

  // Onthouden waar de feed van een bron zit, zodat we dat niet elke nacht
  // opnieuw moeten uitzoeken (scheelt een paar fetches per bron).
  const feedGeheugen = {
    get: (url) => env.WEDSTRIJDEN.get(`feed:${url}`),
    put: (url, waarde) => env.WEDSTRIJDEN.put(`feed:${url}`, waarde, { expirationTtl: 30 * 86400 }),
  };

  const deelnemer = deelnemerUit(env);
  const { items, fouten } = await verzamel(BRONNEN, noteer, feedGeheugen, INSTELLINGEN.reserveVoorDeelnames);
  const keuzes = kies(items);

  // Niets in KV betekent: eerste nacht. Dan halen we in.
  const eerder = await env.WEDSTRIJDEN.list({ prefix: "gezien:", limit: 1 });
  const eersteNacht = eerder.keys.length === 0;
  const plafond = eersteNacht ? INSTELLINGEN.maxEersteNacht : INSTELLINGEN.maxPerNacht;
  if (eersteNacht) noteer(`eerste ronde: inhaalbeweging, tot ${plafond} deelnames`);

  const resultaten = [];
  let gedaan = 0;

  for (const item of keuzes) {
    const kvSleutel = sleutel(item.url);
    const bekend = await env.WEDSTRIJDEN.get(kvSleutel, "json");

    if (bekend && ["gedaan", "overgeslagen"].includes(bekend.status)) continue;
    if (bekend && (bekend.pogingen || 0) >= INSTELLINGEN.maxPogingen) continue;

    if (gedaan >= plafond) {
      resultaten.push({ ...item, status: "overgeslagen", opmerking: "plafond voor vannacht bereikt" });
      continue;
    }

    const { status, opmerking } = await deelnemen(item.url, deelnemer, {
      dryRun,
      // Overzichtssites zetten het juiste antwoord vaak in de samenvatting.
      context: `${item.titel} ${item.samenvatting || ""}`,
    });

    // Budget op: de rest bewaren we voor de volgende ronde in plaats van
    // een reeks valse "mislukt"-regels te produceren.
    if (status === "later") {
      noteer(`— gestopt: ${opmerking}; de rest volgt een volgende ronde`);
      resultaten.push({ ...item, status: "overgeslagen", opmerking: "budget op, volgende ronde" });
      break;
    }

    gedaan += 1;
    noteer(`[${status}] ${item.titel.slice(0, 70)} — ${opmerking}`);
    resultaten.push({ ...item, status, opmerking });

    await env.WEDSTRIJDEN.put(
      kvSleutel,
      JSON.stringify({
        titel: item.titel,
        url: item.url,
        bron: item.bron,
        score: item.score,
        status,
        opmerking,
        pogingen: (bekend?.pogingen || 0) + 1,
        tijd: new Date().toISOString(),
      }),
      { expirationTtl: INSTELLINGEN.bewaarDagen * 86400 }
    );

    // Bijhouden in één lopende lijst, zodat de overzichtspagina met één
    // KV-leesbeurt kan tonen waar je overal aan deelgenomen hebt.
    if (status !== "overgeslagen") {
      const lijst = (await env.WEDSTRIJDEN.get("index:deelnames", "json")) || [];
      lijst.unshift({
        titel: item.titel, url: item.url, bron: item.bron, score: item.score,
        categorieen: item.categorieen, status, opmerking,
        tijd: new Date().toISOString(),
      });
      await env.WEDSTRIJDEN.put("index:deelnames", JSON.stringify(lijst.slice(0, 500)));
    }

    // Het domein onthouden: alleen daar mag de e-mailkant later op klikken.
    if (status === "gedaan") {
      const domein = new URL(item.url).hostname.replace(/^www\./, "");
      await env.WEDSTRIJDEN.put(`domein:${domein}`, "1", { expirationTtl: 14 * 86400 });
    }

    if (gedaan < plafond) await wacht(INSTELLINGEN.pauzeMs);
  }

  const digest = {
    tijd: new Date().toISOString(),
    dryRun,
    subrequests: `${budget.gebruikt}/${budget.limiet}`,
    eersteNacht,
    opgehaald: items.length,
    gekozen: keuzes.length,
    resultaten,
    fouten,
    log,
  };
  await env.WEDSTRIJDEN.put("digest:laatste", JSON.stringify(digest), { expirationTtl: 30 * 86400 });
  return digest;
}

async function mailDigest(env, digest) {
  if (!env.RESEND_API_KEY || !env.DIGEST_NAAR || !env.DIGEST_VAN) return false;
  const nieuw = digest.resultaten.filter((r) => r.status !== "overgeslagen");
  if (!nieuw.length) return false;   // stille nacht: geen mail

  const antwoord = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: env.DIGEST_VAN,
      to: [env.DIGEST_NAAR],
      subject: `[Wedstrijden] ${nieuw.filter((r) => r.status === "gedaan").length} ingeschreven, ` +
               `${nieuw.filter((r) => r.status === "handmatig").length} zelf te doen`,
      html: bouwDigest(digest),
    }),
  });
  return antwoord.ok;
}

export default {
  async scheduled(event, env, ctx) {
    const dryRun = String(env.DRY_RUN ?? "true") !== "false";
    ctx.waitUntil(
      ronde(env, { dryRun })
        .then((digest) => mailDigest(env, digest))
        .catch(async (fout) => {
          await env.WEDSTRIJDEN.put(
            "digest:laatste",
            JSON.stringify({ tijd: new Date().toISOString(), fatale_fout: String(fout), resultaten: [], fouten: [], log: [] }),
            { expirationTtl: 30 * 86400 }
          );
        })
    );
  },

  async fetch(verzoek, env, ctx) {
    const pad = new URL(verzoek.url).pathname.replace(/^\/|\/$/g, "");
    const geheim = (env.DIGEST_PAD || "").replace(/^\/|\/$/g, "");

    if (!geheim || ![geheim, `${geheim}/nu`, `${geheim}/diagnose`].includes(pad)) {
      return new Response("Niets te zien hier.", { status: 404 });
    }

    // Diagnose: toont per wedstrijd wat er gebeurt, zonder iets te versturen.
    if (pad === `${geheim}/diagnose`) {
      budget.reset(Number(env.MAX_SUBREQUESTS || INSTELLINGEN.maxSubrequests));
      const deelnemer = deelnemerUit(env);
      const losseUrl = new URL(verzoek.url).searchParams.get("url");

      let items;
      let kop;
      if (losseUrl) {
        items = [{ url: losseUrl, titel: "", samenvatting: "" }];
        kop = `Eén wedstrijd onderzocht: ${losseUrl}`;
      } else {
        const feedGeheugen = {
          get: (u) => env.WEDSTRIJDEN.get(`feed:${u}`),
          put: (u, w) => env.WEDSTRIJDEN.put(`feed:${u}`, w, { expirationTtl: 30 * 86400 }),
        };
        const { items: rauw } = await verzamel(BRONNEN, () => {}, feedGeheugen, 20);
        items = kies(rauw).slice(0, 6);
        kop = `${rauw.length} items opgehaald, ${items.length} onderzocht (subrequests ${budget.gebruikt}/${budget.limiet})`;
      }

      const bevindingen = [];
      for (const item of items) {
        if (budget.over() < 3) break;
        bevindingen.push(await onderzoek(item.url, deelnemer, `${item.titel || ""} ${item.samenvatting || ""}`));
      }
      return new Response(bouwDiagnosePagina(bevindingen, kop), {
        headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex" },
      });
    }

    // /<pad>/nu draait meteen een ronde, zodat je niet tot 03:15 moet wachten.
    if (pad === `${geheim}/nu`) {
      // Afwachten, niet in de achtergrond: werk in waitUntil() wordt door
      // Cloudflare afgekapt zodra het antwoord verstuurd is.
      const dryRun = String(env.DRY_RUN ?? "true") !== "false";
      const digest = await ronde(env, { dryRun });
      ctx.waitUntil(mailDigest(env, digest));
      const alles = (await env.WEDSTRIJDEN.get("index:deelnames", "json")) || [];
      return new Response(bouwDigest(digest, alles, geheim), {
        headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex" },
      });
    }

    const digest = (await env.WEDSTRIJDEN.get("digest:laatste", "json")) || {
      tijd: new Date().toISOString(), resultaten: [], fouten: [], log: [],
      nogNiets: true,
    };
    const alles = (await env.WEDSTRIJDEN.get("index:deelnames", "json")) || [];
    return new Response(bouwDigest(digest, alles, geheim), {
      headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex" },
    });
  },

  // Cloudflare Email Routing stuurt binnenkomende mail hierheen.
  async email(bericht, env, ctx) {
    const doorsturen = env.DIGEST_NAAR;
    let rauw = "";
    try {
      rauw = await new Response(bericht.raw).text();
    } catch {
      if (doorsturen) await bericht.forward(doorsturen);
      return;
    }

    // Quoted-printable een beetje ontknopen, anders staan links vol =3D.
    const tekst = rauw.replace(/=\r?\n/g, "").replace(/=3D/gi, "=");
    const bevestigWoorden = /bevestig|confirm|verifieer|verify|activeer|activate|valideer|opt.?in/i;
    const rommel = /uitschrijv|unsubscribe|afmeld|privacy|voorwaarden|cookie|facebook\.com|instagram\.com|linkedin\.com/i;

    let geklikt = null;
    for (const treffer of tekst.matchAll(/https?:\/\/[^\s"'<>()]{10,}/g)) {
      const url = treffer[0];
      if (rommel.test(url) || !bevestigWoorden.test(url)) continue;
      let host;
      try {
        host = new URL(url).hostname.replace(/^www\./, "");
      } catch {
        continue;
      }
      // Alleen klikken op domeinen waar we zelf ingeschreven hebben.
      if (!(await env.WEDSTRIJDEN.get(`domein:${host}`))) continue;
      try {
        await fetch(url, { headers: { "User-Agent": "ocior-wedstrijdbot/1.0" }, signal: AbortSignal.timeout(15000) });
        geklikt = url;
        await env.WEDSTRIJDEN.put(`bevestigd:${host}:${Date.now()}`, url, { expirationTtl: 30 * 86400 });
      } catch {
        // Niet erg: de mail wordt sowieso doorgestuurd, dan klik je zelf.
      }
      break;
    }

    if (doorsturen && !geklikt) await bericht.forward(doorsturen);
  },
};
