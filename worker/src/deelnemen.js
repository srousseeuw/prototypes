// Het deelnameformulier lezen, invullen en versturen.
// Zelfde regels als deelnemen.py: nooit gokken bij twijfel, geen lege verplichte
// velden versturen, en bij een captcha stoppen we — dan komt het op de digest.
import { UA, haal, ontsnap, stripHtml } from "./bronnen.js";

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
    formulieren.push({
      action: ontsnap(kop.action || ""),
      method: (kop.method || "get").toLowerCase(),
      velden,
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

export function bouwPayload(formulier, labels, deelnemer) {
  const payload = new URLSearchParams();
  const onbekend = [];

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
      else if (veld.required && !payload.has(naam)) onbekend.push(`verplichte keuze (${naam})`);
      continue;
    }

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

  return { payload, onbekend };
}

export async function deelnemen(url, deelnemer, opties = {}) {
  const { dryRun = true } = opties;

  let html;
  try {
    html = await haal(url);
  } catch (fout) {
    return { status: "mislukt", opmerking: `pagina niet op te halen: ${fout.message}` };
  }

  if (bevatCaptcha(html)) return { status: "handmatig", opmerking: "captcha op de pagina" };
  const laag = html.toLowerCase();
  if (LOGIN_SPOREN.some((spoor) => laag.includes(spoor))) {
    return { status: "handmatig", opmerking: "lijkt een account of login te vragen" };
  }

  const { formulieren, labels } = leesFormulieren(html);
  const formulier = kiesFormulier(formulieren);
  if (!formulier) return { status: "handmatig", opmerking: "geen deelnameformulier gevonden" };

  const { payload, onbekend } = bouwPayload(formulier, labels, deelnemer);
  if (onbekend.length) {
    return { status: "handmatig", opmerking: `niet begrepen: ${onbekend.slice(0, 4).join("; ")}` };
  }
  if (![...payload.keys()].some((naam) => /e.?mail/i.test(naam))) {
    return { status: "handmatig", opmerking: "geen e-mailveld herkend" };
  }

  const doel = new URL(formulier.action || url, url).toString();
  if (dryRun) {
    return {
      status: "proefdraai",
      opmerking: `zou versturen naar ${doel} met ${[...payload.keys()].length} velden`,
    };
  }

  let antwoord;
  try {
    antwoord = await fetch(doel, {
      method: "POST",
      body: payload,
      signal: AbortSignal.timeout(25000),
      headers: {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        Referer: url,
        "Accept-Language": "nl-BE,nl;q=0.9",
      },
    });
  } catch (fout) {
    return { status: "mislukt", opmerking: `versturen mislukt: ${fout.message}` };
  }

  const resultaat = stripHtml(await antwoord.text()).toLowerCase();
  if (GELUKT.some((markering) => resultaat.includes(markering))) {
    return { status: "gedaan", opmerking: `verstuurd naar ${doel}` };
  }
  return { status: "handmatig", opmerking: "verstuurd, maar geen bevestiging herkend — zelf nakijken" };
}
