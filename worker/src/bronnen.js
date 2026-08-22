// Overzichtssites ophalen: feed als het kan, anders de links van de pagina.
// Bewust geen HTMLRewriter: zo draait dezelfde code ook gewoon onder node,
// en kan de logica lokaal getest worden zonder workerd.

import { budget } from "./budget.js";

export const UA = "ocior-wedstrijdbot/1.0 (+https://ocior.be; persoonlijk gebruik)";

const FEED_PADEN = ["/feed/", "/rss", "/rss.xml", "/feed.xml", "/atom.xml"];

const ROMMEL = /^(home|contact|privacy|cookie|inloggen|registreren|aanmelden|meer|lees meer|volgende|vorige|algemene voorwaarden|over ons|nieuwsbrief|deel|delen|facebook|twitter|instagram)\b/i;

export function stripHtml(rauw) {
  return ontsnap((rauw || "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
}

export function ontsnap(tekst) {
  return (tekst || "")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
    .replace(/&#0?39;|&apos;/g, "'").replace(/&nbsp;/g, " ")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)))
    .replace(/&amp;/g, "&");
}

export async function haal(url, timeoutMs = 20000) {
  budget.neem();
  const stop = AbortSignal.timeout(timeoutMs);
  const antwoord = await fetch(url, {
    signal: stop,
    headers: {
      "User-Agent": UA,
      Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "nl-BE,nl;q=0.9",
    },
  });
  if (!antwoord.ok) throw new Error(`HTTP ${antwoord.status} op ${url}`);
  return await antwoord.text();
}

export function isFeed(tekst) {
  const kop = tekst.trimStart().slice(0, 400).toLowerCase();
  return kop.includes("<rss") || kop.includes("<feed") || kop.includes("<rdf:rdf");
}

function tussen(blok, tag) {
  const treffer = blok.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)</${tag}>`, "i"));
  if (treffer) {
    return ontsnap(treffer[1].replace(/^<!\[CDATA\[|\]\]>$/g, "")).trim();
  }
  const zelfsluitend = blok.match(new RegExp(`<${tag}[^>]*href=["']([^"']+)["']`, "i"));
  return zelfsluitend ? zelfsluitend[1] : "";
}

export function parseFeed(xml, bron) {
  const items = [];
  const blokken = xml.match(/<(item|entry)\b[\s\S]*?<\/\1>/gi) || [];
  for (const blok of blokken) {
    const titel = stripHtml(tussen(blok, "title"));
    const url = tussen(blok, "link");
    if (!titel || !url) continue;
    items.push({
      titel,
      url: url.trim(),
      bron,
      samenvatting: stripHtml(tussen(blok, "description") || tussen(blok, "summary")).slice(0, 600),
      datum: tussen(blok, "pubDate") || tussen(blok, "published") || tussen(blok, "updated"),
    });
  }
  return items;
}

export function parseHtmlLijst(html, basisUrl, bron) {
  const items = [];
  const gezien = new Set();
  const links = html.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi);
  for (const [, href, binnenkant] of links) {
    const tekst = stripHtml(binnenkant);
    if (tekst.length < 15 || tekst.split(/\s+/).length < 3 || ROMMEL.test(tekst)) continue;
    let url;
    try {
      url = new URL(ontsnap(href), basisUrl).toString().split("#")[0];
    } catch {
      continue;
    }
    if (!/^https?:/.test(url) || gezien.has(url)) continue;
    gezien.add(url);
    items.push({ titel: tekst.slice(0, 200), url, bron, samenvatting: "", datum: "" });
  }
  return items;
}

function feedKandidaten(html, basisUrl) {
  const gevonden = [];
  for (const [tag] of html.matchAll(/<link\b[^>]*>/gi)) {
    if (!/rel=["']?alternate/i.test(tag) || !/(rss|atom)\+xml/i.test(tag)) continue;
    const href = tag.match(/href=["']([^"']+)["']/i);
    if (href) gevonden.push(new URL(ontsnap(href[1]), basisUrl).toString());
  }
  const basis = new URL(basisUrl);
  // Alleen gokken als de pagina zelf geen feed aangeeft — en dan hooguit één.
  if (!gevonden.length) gevonden.push(`${basis.origin}${FEED_PADEN[0]}`);
  return [...new Set(gevonden)].slice(0, 2);
}

export async function haalBron(bron, geheugen = null) {
  const { url, naam = url, type = "auto" } = bron;

  if (type === "rss") return { items: parseFeed(await haal(url), naam), methode: `feed ${url}` };

  // Wat we vorige keer ontdekten, hoeven we niet opnieuw uit te zoeken.
  const onthouden = geheugen ? await geheugen.get(url) : null;
  if (onthouden && onthouden !== "html") {
    try {
      const inhoud = await haal(onthouden);
      if (isFeed(inhoud)) {
        const items = parseFeed(inhoud, naam);
        if (items.length) return { items, methode: `feed ${onthouden} (onthouden)` };
      }
    } catch (fout) {
      if (fout.name === "BudgetOp") throw fout;
    }
  }

  const inhoud = await haal(url);
  if (isFeed(inhoud)) return { items: parseFeed(inhoud, naam), methode: `feed ${url}` };

  if (type !== "html" && onthouden !== "html") {
    for (const kandidaat of feedKandidaten(inhoud, url)) {
      try {
        const mogelijk = await haal(kandidaat);
        if (!isFeed(mogelijk)) continue;
        const items = parseFeed(mogelijk, naam);
        if (items.length) {
          if (geheugen) await geheugen.put(url, kandidaat);
          return { items, methode: `feed ${kandidaat}` };
        }
      } catch (fout) {
        if (fout.name === "BudgetOp") throw fout;
        // Feed bestaat niet op dit pad; gewoon verder proberen.
      }
    }
  }

  if (geheugen) await geheugen.put(url, "html");
  return { items: parseHtmlLijst(inhoud, url, naam), methode: `html ${url}` };
}

export async function verzamel(bronnen, log = () => {}, geheugen = null, reserve = 0) {
  const items = [];
  const fouten = [];
  for (const bron of bronnen) {
    if (bron.actief === false) continue;
    // Genoeg overhouden om ook nog te kunnen inschrijven.
    if (budget.over() <= reserve) {
      log(`— ${bron.naam} en volgende overgeslagen: budget bewaard voor deelnames`);
      break;
    }
    try {
      const { items: gevonden, methode } = await haalBron(bron, geheugen);
      log(`✓ ${bron.naam}: ${gevonden.length} items via ${methode}`);
      items.push(...gevonden);
    } catch (fout) {
      fouten.push(`${bron.naam}: ${fout.message}`);
      log(`✗ ${bron.naam}: ${fout.message}`);
    }
  }
  return { items, fouten };
}
