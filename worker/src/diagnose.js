// Diagnose: wat gebeurt er écht op een wedstrijdpagina?
//
// De reden dat dit bestaat: deze code is geschreven in een omgeving die de
// echte wedstrijdsites niet mag bereiken, dus getest tegen een zelfgemaakte
// testsite. Die zegt niets over de werkelijkheid. Deze pagina haalt de feiten
// op waar het er wél toe doet — vanuit de Worker zelf — en verstuurt niets.
//
// Te bereiken via <geheim pad>/diagnose, of /diagnose?url=<één wedstrijd>.
import { haal, stripHtml } from "./bronnen.js";
import { bevatCaptcha, kiesFormulier, leesFormulieren, bouwPayload, zoekDoorklik } from "./deelnemen.js";

function ontsnap(t) {
  return String(t ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export async function onderzoek(url, deelnemer, context = "") {
  const bevinding = { url, stappen: [] };

  let html;
  try {
    html = await haal(url);
  } catch (fout) {
    bevinding.uitkomst = "pagina niet op te halen";
    bevinding.detail = fout.message;
    return bevinding;
  }

  bevinding.stappen.push(`pagina opgehaald (${Math.round(html.length / 1024)} kB)`);

  if (bevatCaptcha(html)) bevinding.stappen.push("captcha aanwezig");
  if (/<script/i.test(html)) {
    const scripts = (html.match(/<script/gi) || []).length;
    bevinding.stappen.push(`${scripts} scripts (formulier kan door JavaScript gebouwd zijn)`);
  }

  let { formulieren, labels } = leesFormulieren(html);
  bevinding.stappen.push(`${formulieren.length} formulier(en) in de HTML`);
  let formulier = kiesFormulier(formulieren);
  let bron = url;

  // Overzichtssites linken door naar de echte wedstrijd. Zonder die stap
  // zoeken we een formulier op een pagina die er nooit één had.
  if (!formulier) {
    const door = zoekDoorklik(html, url);
    if (door) {
      bevinding.stappen.push(`doorklik gevonden: ${door}`);
      try {
        const tweede = await haal(door);
        ({ formulieren, labels } = leesFormulieren(tweede));
        formulier = kiesFormulier(formulieren);
        bron = door;
        bevinding.stappen.push(`doorklik opgehaald, ${formulieren.length} formulier(en)`);
        if (bevatCaptcha(tweede)) bevinding.stappen.push("captcha op de doorklikpagina");
      } catch (fout) {
        bevinding.stappen.push(`doorklik mislukt: ${fout.message}`);
      }
    } else {
      bevinding.stappen.push("geen doorklik naar een wedstrijd gevonden");
    }
  }

  if (!formulier) {
    bevinding.uitkomst = "geen bruikbaar formulier";
    return bevinding;
  }

  const zichtbaar = formulier.velden.filter(
    (v) => !["hidden", "submit", "button", "image"].includes(v.type));
  bevinding.stappen.push(
    `formulier op ${bron === url ? "de pagina zelf" : "de doorklik"}: ` +
    `${zichtbaar.length} zichtbare velden (${zichtbaar.map((v) => v.name || v.id || v.type).slice(0, 8).join(", ")})`);

  const { payload, onbekend, uitleg } = bouwPayload(formulier, labels, deelnemer, {
    pagina: stripHtml(html),
    context,
  });
  for (const regel of uitleg) bevinding.stappen.push(regel);

  if (onbekend.length) {
    bevinding.uitkomst = "niet in te vullen";
    bevinding.detail = onbekend.join("; ");
  } else {
    bevinding.uitkomst = `zou versturen: ${[...payload.keys()].join(", ")}`;
  }
  return bevinding;
}

export function bouwDiagnosePagina(bevindingen, samenvatting) {
  const rijen = bevindingen.map((b) => `<div class="k">
  <a href="${ontsnap(b.url)}">${ontsnap(b.url)}</a>
  <div class="u">${ontsnap(b.uitkomst)}${b.detail ? " — " + ontsnap(b.detail) : ""}</div>
  <ol>${b.stappen.map((s) => `<li>${ontsnap(s)}</li>`).join("")}</ol>
</div>`).join("");

  return `<!doctype html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Diagnose</title><style>
:root{color-scheme:light dark}
body{margin:0;padding:24px;background:#f6f7f9;color:#111827;font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
.wrap{max-width:860px;margin:0 auto}
h1{font:600 20px system-ui;margin:0 0 6px}
.s{font:14px system-ui;color:#6b7280;margin:0 0 20px}
.k{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:12px 14px;margin-bottom:10px}
.k a{color:#0b62c4;text-decoration:none;word-break:break-all}
.u{font-weight:600;margin:6px 0}
ol{margin:6px 0 0;padding-left:20px;color:#4b5563}
li{margin:2px 0}
@media (prefers-color-scheme:dark){
 body{background:#0f1115;color:#e5e7eb}.k{background:#171a21;border-color:#262b36}
 ol{color:#9ca3af}.k a{color:#60a5fa}}
</style></head><body><div class="wrap">
<h1>Diagnose — er is niets verstuurd</h1>
<p class="s">${ontsnap(samenvatting)}</p>
${rijen || '<p class="s">Geen wedstrijden om te onderzoeken.</p>'}
</div></body></html>`;
}
