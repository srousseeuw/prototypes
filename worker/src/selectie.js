// Scoren: welke wedstrijd is nuttig voor het gezin?
// De woordenlijsten komen uit wedstrijden/selectie.json — hetzelfde bestand dat
// het Python-script gebruikt, zodat er maar één lijst te onderhouden is.
// src/lijsten.js wordt daaruit gegenereerd met `npm run lijsten`.
import lijsten from "./lijsten.js";

export function normaliseer(tekst) {
  return (tekst || "")
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")   // accenten weg
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

// Match aan het begin van een woord: 'gezin' vangt ook 'gezinsticket',
// maar 'bon' slaat niet aan op 'abonnement'. Zelfde regel als in selectie.py.
function bevat(hooiberg, naald) {
  const woord = normaliseer(naald);
  if (!woord) return false;
  const patroon = new RegExp(`(^| )${woord.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`);
  return patroon.test(hooiberg);
}

export function beoordeel(item) {
  const tekst = normaliseer(
    [item.titel, item.samenvatting, (item.url || "").replace(/[-/]/g, " ")].join(" ")
  );

  let score = 0;
  const categorieen = [];
  const redenen = [];

  for (const [naam, blok] of Object.entries(lijsten.categorieen || {})) {
    const treffers = (blok.woorden || []).filter((w) => bevat(tekst, w));
    if (!treffers.length) continue;
    const gewicht = Number(blok.gewicht || 1);
    score += gewicht;
    categorieen.push(naam);
    redenen.push(`${naam} (+${gewicht}): ${treffers.slice(0, 3).join(", ")}`);
  }

  const gratis = (lijsten.gratis_woorden || []).filter((w) => bevat(tekst, w));
  if (gratis.length) {
    score += Number(lijsten.gratis_bonus || 0);
    redenen.push(`gratis (+${lijsten.gratis_bonus || 0})`);
  }

  const uitgesloten = (lijsten.uitsluiten || []).filter((w) => bevat(tekst, w));
  if (uitgesloten.length) {
    score += Number(lijsten.uitsluiten_gewicht ?? -20);
    redenen.push(`uitgesloten: ${uitgesloten.slice(0, 3).join(", ")}`);
  }

  return { ...item, score, categorieen, redenen, uitgesloten: uitgesloten.length > 0 };
}

export function kies(items, { minScore, maximum } = {}) {
  const drempel = minScore ?? Number(lijsten.min_score ?? 4);
  const plafond = maximum ?? Number(lijsten.max_per_nacht ?? 25);

  const beste = new Map();
  for (const item of items) {
    const beoordeeld = beoordeel(item);
    const sleutel = (beoordeeld.url || "").replace(/\/+$/, "").toLowerCase();
    const vorig = beste.get(sleutel);
    if (!vorig || beoordeeld.score > vorig.score) beste.set(sleutel, beoordeeld);
  }

  return [...beste.values()]
    .filter((i) => !i.uitgesloten && i.score >= drempel)
    .sort((a, b) => b.score - a.score || a.titel.localeCompare(b.titel))
    .slice(0, plafond);
}
