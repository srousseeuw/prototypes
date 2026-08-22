// De digest: één pagina met wat er vannacht gebeurd is.
// Wordt zowel als webpagina geserveerd (geheim pad) als gemaild.

const LABELS = {
  gedaan: ["Ingeschreven", "#1a7f37"],
  proefdraai: ["Proefdraai (niets verstuurd)", "#8a6d00"],
  handmatig: ["Zelf doen", "#0b62c4"],
  mislukt: ["Mislukt", "#b42318"],
  overgeslagen: ["Overgeslagen", "#6b7280"],
};

function ontsnap(tekst) {
  return String(tekst ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function kaart(item) {
  const [label, kleur] = LABELS[item.status] || ["", "#6b7280"];
  const categorieen = (item.categorieen || [])
    .map((c) => `<span class="badge">${ontsnap(c)}</span>`).join(" ");
  return `<div class="kaart">
  <span class="score">score ${ontsnap(item.score ?? 0)}</span>
  <a href="${ontsnap(item.url)}">${ontsnap(item.titel || "(zonder titel)")}</a>
  <div class="meta"><span class="badge" style="color:${kleur}">${ontsnap(label)}</span>
    ${categorieen} ${ontsnap(item.bron || "")}
    ${item.opmerking ? "· " + ontsnap(item.opmerking) : ""}</div>
</div>`;
}

function sectie(titel, items, leeg) {
  if (!items.length) return `<h2>${ontsnap(titel)}</h2><p class="leeg">${ontsnap(leeg)}</p>`;
  return `<h2>${ontsnap(titel)} (${items.length})</h2>` + items.map(kaart).join("");
}

export function bouwDigest(digest) {
  const perStatus = {};
  for (const item of digest.resultaten || []) {
    (perStatus[item.status] ||= []).push(item);
  }

  const datum = new Date(digest.tijd || Date.now()).toLocaleDateString("nl-BE", {
    day: "2-digit", month: "2-digit", year: "numeric", timeZone: "Europe/Brussels",
  });

  const stukken = [
    digest.fatale_fout
      ? `<div class="kaart fout">De ronde is afgebroken: ${ontsnap(digest.fatale_fout)}</div>`
      : "",
    digest.dryRun ? `<p class="sub">Proefdraai — er is niets verstuurd (zet DRY_RUN op "false").</p>` : "",
    digest.eersteNacht ? `<p class="sub">Eerste ronde: inhaalbeweging op alles wat nu online staat.</p>` : "",
    sectie("Ingeschreven", perStatus.gedaan || [], "Vannacht geen inschrijvingen."),
    sectie("Zelf afwerken", perStatus.handmatig || [], "Niets dat jouw handen nodig heeft."),
    sectie("Proefdraai", perStatus.proefdraai || [], "Geen proefdraai."),
    sectie("Mislukt", perStatus.mislukt || [], "Niets mislukt."),
    (perStatus.overgeslagen || []).length
      ? `<h2>Wacht op een volgende nacht (${perStatus.overgeslagen.length})</h2>` +
        perStatus.overgeslagen.map(kaart).join("")
      : "",
    (digest.fouten || []).length
      ? `<h2>Bronnen met problemen (${digest.fouten.length})</h2>` +
        digest.fouten.map((f) => `<div class="kaart fout">${ontsnap(f)}</div>`).join("")
      : "",
  ];

  return `<!doctype html><html lang="nl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Wedstrijden — ${datum}</title>
<style>
:root{color-scheme:light dark}
body{margin:0;padding:28px 20px;background:#f6f7f9;color:#111827;
     font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:760px;margin:0 auto}
h1{font-size:22px;margin:0 0 4px}
.sub{color:#6b7280;font-size:14px;margin:0 0 20px}
h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:#6b7280;
   margin:32px 0 12px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}
.kaart{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 16px;margin-bottom:10px}
.kaart a{color:#111827;text-decoration:none;font-weight:600}
.meta{font-size:13px;color:#6b7280;margin-top:6px}
.badge{display:inline-block;font-size:12px;font-weight:600;padding:2px 8px;border-radius:999px;
       background:#eef2f7;margin-right:6px}
.score{float:right;font-size:13px;color:#6b7280}
.leeg{color:#6b7280;font-style:italic}
.fout{background:#fff5f5;border-color:#fecdca}
@media (prefers-color-scheme:dark){
  body{background:#0f1115;color:#e5e7eb}
  .kaart{background:#171a21;border-color:#262b36}
  .kaart a{color:#e5e7eb}
  .badge{background:#232833;color:#cbd5e1}
  .fout{background:#241618;border-color:#5b2326}
}
</style></head><body><div class="wrap">
<h1>Wedstrijden van ${datum}</h1>
<p class="sub">${ontsnap(digest.opgehaald ?? 0)} gevonden · ${ontsnap(digest.gekozen ?? 0)} geselecteerd ·
${(digest.resultaten || []).length} behandeld</p>
${stukken.join("")}
</div></body></html>`;
}
