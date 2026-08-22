// Draait de Worker-logica onder gewone node, tegen een lokale testsite.
// Geen workerd nodig: KV wordt nagebootst met een Map.
//   node test/lokaal.mjs [basis-url]      (standaard http://127.0.0.1:8765/)
import worker from "../src/index.js";
import { BRONNEN } from "../src/config.js";

const BASIS = process.argv[2] || "http://127.0.0.1:8765/";

// Nep-KV met net genoeg gedrag: get/put/list met prefix.
function nepKV() {
  const opslag = new Map();
  return {
    opslag,
    async get(sleutel, soort) {
      const waarde = opslag.get(sleutel);
      if (waarde === undefined) return null;
      return soort === "json" ? JSON.parse(waarde) : waarde;
    },
    async put(sleutel, waarde) {
      opslag.set(sleutel, waarde);
    },
    async list({ prefix = "", limit = 1000 } = {}) {
      const keys = [...opslag.keys()].filter((k) => k.startsWith(prefix)).slice(0, limit);
      return { keys: keys.map((name) => ({ name })), list_complete: true };
    },
  };
}

function omgeving(kv, extra = {}) {
  return {
    WEDSTRIJDEN: kv,
    DIGEST_PAD: "geheim-pad",
    DEELNEMER: JSON.stringify({
      voornaam: "Sebastiaan",
      achternaam: "Rousseeuw",
      email: "sebastiaan.rousseeuw+wedstrijden@gmail.com",
      telefoon: "0470 12 34 56",
      straat: "Teststraat",
      huisnummer: "7",
      postcode: "2910",
      gemeente: "Essen",
      land: "België",
      geboortedatum: "1985-04-12",
      nieuwsbriefToestaan: false,
    }),
    ...extra,
  };
}

// De echte bronnenlijst vervangen door de testsite.
BRONNEN.length = 0;
BRONNEN.push({ naam: "Testsite", url: BASIS, type: "html", actief: true });

const taken = [];
const ctx = { waitUntil: (belofte) => taken.push(belofte) };

async function ronde(env, naam) {
  console.log(`\n── ${naam} ──`);
  taken.length = 0;
  await worker.scheduled({}, env, ctx);
  await Promise.all(taken);
  const digest = await env.WEDSTRIJDEN.get("digest:laatste", "json");
  for (const regel of digest.log) console.log("  " + regel);
  return digest;
}

const kv = nepKV();

// 1. Proefdraai
await ronde(omgeving(kv, { DRY_RUN: "true" }), "proefdraai (DRY_RUN=true)");

// 2. Echt inschrijven — eerste ronde, dus inhaalbeweging
const kv2 = nepKV();
const echt = await ronde(omgeving(kv2, { DRY_RUN: "false" }), "echt inschrijven, eerste ronde");
console.log("  inhaalbeweging herkend:", echt.eersteNacht);

// 3. Nog eens: wat gedaan is, mag niet opnieuw
const herhaling = await ronde(omgeving(kv2, { DRY_RUN: "false" }), "tweede ronde (mag niets herhalen)");
const opnieuw = herhaling.resultaten.filter((r) => r.status === "gedaan");
console.log("  opnieuw ingeschreven:", opnieuw.length, opnieuw.length === 0 ? "✓" : "✗ FOUT");

// 4. Digestpagina op het geheime pad, en 404 daarbuiten
const env = omgeving(kv2, { DRY_RUN: "false" });
const goed = await worker.fetch(new Request("https://bot.example/geheim-pad"), env);
const fout = await worker.fetch(new Request("https://bot.example/"), env);
console.log(`\n── digestpagina ──`);
console.log("  /geheim-pad →", goed.status, (await goed.text()).includes("Wedstrijden van") ? "✓ digest" : "✗");
console.log("  /           →", fout.status, fout.status === 404 ? "✓ verborgen" : "✗");

// 5. E-mailkant: bevestigingslink van een domein waar we inschreven → aanklikken
console.log(`\n── bevestigingsmail ──`);
const host = new URL(BASIS).hostname.replace(/^www\./, "");
await kv2.put(`domein:${host}`, "1");
const mail = [
  "From: wedstrijd@voorbeeld.be",
  "Subject: Bevestig je deelname",
  "",
  `Klik hier om te bevestigen: ${new URL("/bevestig?token=abc", BASIS)}`,
].join("\r\n");
let doorgestuurd = null;
await worker.email(
  { raw: new Blob([mail]).stream(), forward: async (naar) => { doorgestuurd = naar; } },
  omgeving(kv2, { DIGEST_NAAR: "sebastiaan.rousseeuw@gmail.com" }),
  ctx
);
const bevestigingen = (await kv2.list({ prefix: "bevestigd:" })).keys;
console.log("  link aangeklikt:", bevestigingen.length ? "✓" : "✗");
console.log("  mail doorgestuurd:", doorgestuurd ?? "nee (klopt: bevestiging afgehandeld)");
