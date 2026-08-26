// Het deelnameformulier lezen, invullen en versturen.
// Zelfde regels als deelnemen.py: nooit gokken bij twijfel, geen lege verplichte
// velden versturen, en bij een captcha stoppen we — dan komt het op de digest.
import { UA, haal, ontsnap, stripHtml } from "./bronnen.js";
import { budget } from "./budget.js";
import { schatSchifting, soortVraag, zoekAntwoord } from "./antwoord.js";

const CAPTCHA_SPOREN = ["recaptcha", "g-recaptcha", "hcaptcha", "h-captcha",
                        "cf-turnstile", "turnstile", "friendlycaptcha", "captcha"];
const LOGIN_SPOREN = ["wachtwoord", "password", "inloggen om deel te nemen", "log in om"];
const GELUKT = ["bedankt", "je deelname", "uw deelname", "deelname geregistreerd",
                "succesvol", "gelukt", "bevestigingsmail", "thank you", "veel succes"];

const VELDPATRONEN = [
  [/voornaam|firstname|first_name|fname|given/, "voornaam"],
  [/achternaam|lastname|last_name|lname|surname|familienaam/, "achternaam"],
  [/\bnaam\b|fullname|full_name|\bname\b/, "volledigeNaam"],
  [/e.?mail/, "email"],
  [/telefoon|gsm|mobiel|phone|tel\b/, "telefoon"],
  [/straat|street|adres|address(?!.*mail)/, "straat"],
  [/huisnummer|nummer|house.?number|streetnumber/, "huisnummer"],
  [/postcode|zip|postal/, "postcode"],
  [/gemeente|woonplaats|stad|city|plaats/, "gemeente"],
  [/land|country/, "land"],
  [/geboorte|birth|dob/, "geboortedatum"],
];

// Overzichtssites tonen een detailpagina met een knop naar de echte wedstrijd.
// Die hop misten we: we zochten een formulier op een pagina die er geen heeft.
const DOORKLIK = /deelnem|meedoen|doe\s*mee|naar de (wedstrijd|actie)|win nu|inschrijv|naar de site|bezoek/i;

export function zoekDoorklik(html, basisUrl) {
  const huidig = new URL(basisUrl);
  const eigen = huidig.hostname.replace(/^www\./, "");
  const kandidaten = [];

  for (const [, href, binnenkant] of html.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)) {
    const tekst = stripHtml(binnenkant);
    if (!DOORKLIK.test(tekst)) continue;

    let doel;
    try {
      doel = new URL(ontsnap(href), basisUrl);
    } catch {
      continue;
    }
    if (!/^https?:$/.test(doel.protocol)) continue;
    if (doel.toString().split("#")[0] === basisUrl.split("#")[0]) continue;

    const extern = doel.hostname.replace(/^www\./, "") !== eigen;
    // Een link terug naar de homepage van de overzichtssite is geen wedstrijd.
    if (!extern && doel.pathname.replace(/\/+$/, "") === "") continue;

    kandidaten.push({ url: doel.toString(), extern });
  }

  // Extern heeft voorrang (dat is meestal het merk zelf), maar een doorklik
  // binnen dezelfde site telt ook: sommige overzichtssites hosten het
  // formulier gewoon zelf.
  const gekozen = kandidaten.find((k) => k.extern) || kandidaten[0];
  return gekozen ? gekozen.url : null;
}

export function bevatCaptcha(html) {
  const laag = html.toLowerCase();
  return CAPTCHA_SPOREN.some((spoor) => laag.includes(spoor));
}

function kenmerken(tag) {
  const uit = {};
  for (const [, naam, waarde] of tag.matchAll(/([a-zA-Z-]+)(?:=["']([^"']*)["'])?/g)) {
    uit[naam.toLowerCase()] = waarde ?? "";
  }
  return uit;
}

export function leesFormulieren(html) {
  const labels = {};
  const labelTags = html.matchAll(/<label[^>]*for=["']([^"']+)["'][^>]*>([\s\S]*?)<\/label>/gi);
  for (const [, voor, tekst] of labelTags) labels[voor] = stripHtml(tekst);

  const formulieren = [];
  for (const [blok, opening] of html.matchAll(/(<form\b[^>]*>)[\s\S]*?<\/form>/gi)) {
    const kop = kenmerken(opening);
    const velden = [];
    // Keuzes per veldnaam: nodig om een wedstrijdvraag te kunnen beantwoorden.
    const keuzes = {};

    // <select name="antwoord"><option value="a">Brussel</option>...
    for (const [blokje, selectTag] of blok.matchAll(/(<select\b[^>]*>[\s\S]*?<\/select>)/gi)) {
      const naam = kenmerken(selectTag).name;
      if (!naam) continue;
      for (const [, waarde, tekst] of blokje.matchAll(/<option[^>]*value=["']([^"']*)["'][^>]*>([\s\S]*?)<\/option>/gi)) {
        if (!waarde) continue;
        (keuzes[naam] ||= []).push({ value: waarde, tekst: stripHtml(tekst) });
      }
    }
    for (const [, soort, rest] of blok.matchAll(/<(input|select|textarea)\b([^>]*)>/gi)) {
      const k = kenmerken(rest);
      velden.push({
        type: (k.type || (soort.toLowerCase() === "input" ? "text" : soort.toLowerCase())).toLowerCase(),
        name: k.name || "",
        id: k.id || "",
        value: ontsnap(k.value || ""),
        placeholder: k.placeholder || "",
        required: "required" in k,
        checked: "checked" in k,
      });
    }
    // Radiokeuzes: de tekst staat in het <label for="...">.
    for (const veld of velden) {
      if (veld.type !== "radio" || !veld.name) continue;
      (keuzes[veld.name] ||= []).push({
        value: veld.value || "on",
        tekst: labels[veld.id] || veld.value || "",
      });
    }

    formulieren.push({
      action: ontsnap(kop.action || ""),
      method: (kop.method || "get").toLowerCase(),
      velden,
      keuzes,
    });
  }
  return { formulieren, labels };
}

export function kiesFormulier(formulieren) {
  let beste = null;
  for (const formulier of formulieren) {
    const heeftEmail = formulier.velden.some((v) => v.type === "email" || /e.?mail/i.test(v.name));
    const zichtbaar = formulier.velden.filter(
      (v) => !["hidden", "submit", "button", "image"].includes(v.type));
    if (!heeftEmail || !zichtbaar.length) continue;
    if (!beste || zichtbaar.length > beste.aantal) beste = { formulier, aantal: zichtbaar.length };
  }
  return beste ? beste.formulier : null;
}

function raadVeld(veld, labels) {
  if (veld.type === "email") return "email";
  if (veld.type === "tel") return "telefoon";
  const aanwijzing = [veld.name, veld.id, veld.placeholder, labels[veld.id] || ""]
    .join(" ").toLowerCase();
  for (const [patroon, sleutel] of VELDPATRONEN) if (patroon.test(aanwijzing)) return sleutel;
  return null;
}

export function bouwPayload(formulier, labels, deelnemer, context = {}) {
  const payload = new URLSearchParams();
  const onbekend = [];
  const uitleg = [];
  const keuzes = formulier.keuzes || {};

  // Een wedstrijd- of schiftingsvraag invullen op basis van wat er op de
  // pagina staat. Lukt dat niet overtuigend, dan blijft het veld onbekend en
  // gaat de wedstrijd naar "zelf doen" — liever dat dan een gok die je
  // deelname toch ongeldig maakt.
  const probeerVraag = (veld, aanwijzing) => {
    const soort = soortVraag(aanwijzing);
    if (!soort) return false;
    const gevonden = soort === "schifting"
      ? schatSchifting(aanwijzing, context.pagina || "", context.context || "")
      : zoekAntwoord(aanwijzing, keuzes[veld.name] || [], context.pagina || "", context.context || "");
    if (!gevonden) return false;
    payload.set(veld.name, gevonden.waarde);
    uitleg.push(`${soort === "schifting" ? "schifting" : "wedstrijdvraag"}: ` +
                `"${gevonden.waarde}" — ${gevonden.reden}`);
    return true;
  };

  for (const veld of formulier.velden) {
    const naam = veld.name;

    if (["file", "password"].includes(veld.type)) {
      onbekend.push(`${veld.type}-veld (${naam || veld.id})`);
      continue;
    }
    if (!naam || ["submit", "button", "image"].includes(veld.type)) continue;

    if (veld.type === "hidden") {
      payload.set(naam, veld.value);
      continue;
    }

    if (veld.type === "checkbox") {
      const label = `${labels[veld.id] || ""} ${naam}`.toLowerCase();
      if (/voorwaard|reglement|akkoord|privacy|18|leeftijd|terms/.test(label)) {
        payload.set(naam, veld.value || "on");
      } else if (/nieuwsbrief|newsletter|aanbieding|partner|marketing|mailing/.test(label)) {
        if (deelnemer.nieuwsbriefToestaan) payload.set(naam, veld.value || "on");
      } else if (veld.required) {
        onbekend.push(`verplicht vinkje (${naam})`);
      }
      continue;
    }

    if (veld.type === "radio") {
      if (veld.checked) payload.set(naam, veld.value || "on");
      else if (payload.has(naam)) continue;
      else if (probeerVraag(veld, `${labels[veld.id] || ""} ${naam} ${vraagTekstBij(labels, naam)}`)) continue;
      else if (veld.required) onbekend.push(`verplichte keuze (${naam})`);
      continue;
    }

    const aanwijzing = [veld.name, veld.id, veld.placeholder, labels[veld.id] || ""].join(" ");
    if (probeerVraag(veld, aanwijzing)) continue;

    const sleutel = raadVeld(veld, labels);
    if (sleutel) {
      const waarde = String(deelnemer[sleutel] ?? "").trim();
      // Liever niets versturen dan een leeg verplicht veld: dan weet je meteen
      // welk gegeven nog als secret ontbreekt.
      if (waarde) payload.set(naam, waarde);
      else if (veld.required) onbekend.push(`${sleutel} ontbreekt in de secrets (${naam})`);
    } else if (veld.required) {
      onbekend.push(`verplicht veld (${naam})`);
    }
  }

  return { payload, onbekend, uitleg };
}

// De vraagtekst staat niet altijd in het label van de radio zelf, maar in het
// label van de groep of in een kop erboven; we plakken alles wat we hebben aan
// elkaar zodat de herkenning kans maakt.
function vraagTekstBij(labels, naam) {
  return Object.entries(labels)
    .filter(([id]) => id.toLowerCase().includes(naam.toLowerCase()))
    .map(([, tekst]) => tekst)
    .join(" ");
}

export async function deelnemen(url, deelnemer, opties = {}) {
  const { dryRun = true, context = "" } = opties;

  let html;
  try {
    html = await haal(url);
  } catch (fout) {
    if (fout.name === "BudgetOp") return { status: "later", opmerking: fout.message };
    return { status: "mislukt", opmerking: `pagina niet op te halen: ${fout.message}` };
  }

  if (bevatCaptcha(html)) return { status: "handmatig", opmerking: "captcha op de pagina" };
  const laag = html.toLowerCase();
  if (LOGIN_SPOREN.some((spoor) => laag.includes(spoor))) {
    return { status: "handmatig", opmerking: "lijkt een account of login te vragen" };
  }

  let { formulieren, labels } = leesFormulieren(html);
  let formulier = kiesFormulier(formulieren);
  let doelPagina = url;

  // Geen formulier? Dan staan we waarschijnlijk op de detailpagina van een
  // overzichtssite. Volg de knop naar de echte wedstrijd — één keer.
  if (!formulier) {
    const door = zoekDoorklik(html, url);
    if (!door) return { status: "handmatig", opmerking: "geen deelnameformulier en geen doorklik gevonden" };
    let tweede;
    try {
      tweede = await haal(door);
    } catch (fout) {
      if (fout.name === "BudgetOp") return { status: "later", opmerking: fout.message };
      return { status: "mislukt", opmerking: `doorklik ${door} niet op te halen: ${fout.message}` };
    }
    if (bevatCaptcha(tweede)) {
      return { status: "handmatig", opmerking: `captcha op ${new URL(door).hostname}` };
    }
    ({ formulieren, labels } = leesFormulieren(tweede));
    formulier = kiesFormulier(formulieren);
    doelPagina = door;
    html = tweede;
    if (!formulier) {
      return { status: "handmatig", opmerking: `geen formulier op ${new URL(door).hostname} (waarschijnlijk JavaScript)` };
    }
  }

  const { payload, onbekend, uitleg } = bouwPayload(formulier, labels, deelnemer, {
    pagina: stripHtml(html),
    context,
  });
  const extra = uitleg.length ? ` · ${uitleg.join(" · ")}` : "";
  if (onbekend.length) {
    return { status: "handmatig", opmerking: `niet begrepen: ${onbekend.slice(0, 4).join("; ")}` };
  }
  if (![...payload.keys()].some((naam) => /e.?mail/i.test(naam))) {
    return { status: "handmatig", opmerking: "geen e-mailveld herkend" };
  }

  const doel = new URL(formulier.action || doelPagina, doelPagina).toString();
  if (dryRun) {
    return {
      status: "proefdraai",
      opmerking: `zou versturen naar ${doel} met ${[...payload.keys()].length} velden${extra}`,
    };
  }

  let antwoord;
  try {
    budget.neem();
    antwoord = await fetch(doel, {
      method: "POST",
      body: payload,
      signal: AbortSignal.timeout(25000),
      headers: {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        Referer: doelPagina,
        "Accept-Language": "nl-BE,nl;q=0.9",
      },
    });
  } catch (fout) {
    if (fout.name === "BudgetOp") return { status: "later", opmerking: fout.message };
    return { status: "mislukt", opmerking: `versturen mislukt: ${fout.message}` };
  }

  const resultaat = stripHtml(await antwoord.text()).toLowerCase();
  if (GELUKT.some((markering) => resultaat.includes(markering))) {
    return { status: "gedaan", opmerking: `verstuurd naar ${doel}${extra}` };
  }
  return { status: "handmatig", opmerking: "verstuurd, maar geen bevestiging herkend — zelf nakijken" };
}
