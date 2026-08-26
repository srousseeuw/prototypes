// Wedstrijdvragen en schiftingsvragen invullen.
//
// Twee heel verschillende dingen:
//
//   Wedstrijdvraag  — heeft één juist antwoord ("In welk jaar werd X opgericht?").
//                     Dat antwoord staat vaak gewoon op de pagina zelf, of in de
//                     samenvatting van de overzichtssite (veel van die sites
//                     publiceren "de wedstrijd mét antwoord").
//
//   Schiftingsvraag — heeft géén juist antwoord ("Hoeveel mensen zullen
//                     deelnemen?"). Wie er het dichtst bij zit, wint. Een lege
//                     of belachelijke waarde kost je de wedstrijd, dus schatten
//                     we zo goed als het kan en zeggen we er eerlijk bij dat het
//                     een schatting is.
//
// Alles wat hier gebeurt, komt in de opmerking op de digest terecht, zodat je
// achteraf kan zien wat er ingevuld werd en waarom.

export const SCHIFTING = /schifting|tiebreak|schattings?vraag|hoeveel\s+(mensen|deelnemers|personen|inzendingen)|aantal\s+(deelnemers|inzendingen)/i;
export const WEDSTRIJDVRAAG = /wedstrijdvraag|vraag|question|antwoord|answer|quiz/i;

const GETAL = /(\d[\d .,]{0,12}\d|\d)/g;

// De paginatekst loopt na "Antwoord: 1964" gewoon door, dus knippen we streng
// af: een getal, of hooguit drie woorden. Loopt er toch vraagtekst in mee, dan
// is de vondst besmet en gebruiken we ze niet.
function kortAntwoord(rauw) {
  const schoon = (rauw || "").trim().replace(/^["'\s]+|["'.,;\s]+$/g, "");
  const getal = schoon.match(/^\d[\d .,]*/);
  if (getal) return getal[0].trim().replace(/[.,]$/, "");
  const woorden = schoon.split(/\s+/).slice(0, 3).join(" ");
  if (/vraag|question|e-?mail|voornaam|achternaam|formulier/i.test(woorden)) return null;
  return woorden.length >= 1 && woorden.length <= 40 ? woorden : null;
}

function alleGetallen(tekst) {
  return [...(tekst || "").matchAll(GETAL)]
    .map((t) => Number(t[1].replace(/[ .]/g, "").replace(",", ".")))
    .filter((n) => Number.isFinite(n));
}

// --------------------------------------------------------------- wedstrijdvraag

/**
 * Zoekt het juiste antwoord in de tekst die we hebben.
 * @param {string} vraag      de vraagtekst zoals ze bij het veld staat
 * @param {Array}  keuzes     [{value, tekst}] bij meerkeuze, anders leeg
 * @param {string} pagina     de tekst van de wedstrijdpagina
 * @param {string} context    titel + samenvatting van de overzichtssite
 */
export function zoekAntwoord(vraag, keuzes, pagina, context = "") {
  const alles = `${context}\n${pagina}`;

  // 1. Sites die het antwoord er zelf bij zetten: "Antwoord: B" of
  //    "Het juiste antwoord is Brussel".
  const gemeld = alles.match(
    /(?:juiste\s+)?antwoord(?:\s+is)?\s*[:=]?\s*([A-Za-zÀ-ÿ0-9][^.\n<]{0,60})/i);
  if (gemeld) {
    const gevonden = kortAntwoord(gemeld[1]);
    if (gevonden && keuzes.length) {
      const keuze = keuzes.find(
        (k) => k.tekst.toLowerCase() === gevonden.toLowerCase() ||
               k.value.toLowerCase() === gevonden.toLowerCase() ||
               (gevonden.length <= 2 && k.value.toLowerCase() === gevonden.toLowerCase()));
      if (keuze) return { waarde: keuze.value, reden: `antwoord stond op de pagina (${gevonden})` };
    } else if (gevonden) {
      return { waarde: gevonden, reden: `antwoord stond op de pagina ("${gevonden}")` };
    }
  }

  // 2. Meerkeuze zonder gemeld antwoord: het juiste antwoord staat meestal ook
  //    in de wervende tekst erboven ("... in ons filiaal in Brussel ..."), de
  //    afleiders niet. Tel dus hoe vaak elke keuze elders op de pagina staat.
  if (keuzes.length) {
    const zonderKeuzes = pagina.replace(/\s+/g, " ");
    const geteld = keuzes.map((keuze) => {
      const naald = keuze.tekst.trim();
      if (naald.length < 2) return { keuze, aantal: 0 };
      const patroon = new RegExp(naald.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      return { keuze, aantal: (zonderKeuzes.match(patroon) || []).length };
    });
    geteld.sort((a, b) => b.aantal - a.aantal);
    // Alleen als er één duidelijk bovenuit steekt; anders is het gokken en dat
    // doen we niet — dan gaat de wedstrijd naar "zelf doen".
    if (geteld[0].aantal >= 2 && geteld[0].aantal > (geteld[1]?.aantal ?? 0)) {
      return {
        waarde: geteld[0].keuze.value,
        reden: `meerkeuze: "${geteld[0].keuze.tekst}" komt ${geteld[0].aantal}× voor in de tekst`,
      };
    }
  }

  // 3. Jaartal- of getalvraag waarvan het antwoord letterlijk in de tekst staat.
  if (/in welk jaar|sinds wanneer|opgericht/i.test(vraag)) {
    const jaren = alleGetallen(alles).filter((n) => n > 1800 && n <= new Date().getFullYear());
    if (jaren.length) {
      const vaakste = jaren.sort(
        (a, b) => jaren.filter((j) => j === b).length - jaren.filter((j) => j === a).length)[0];
      return { waarde: String(vaakste), reden: `jaartal uit de paginatekst (${vaakste})` };
    }
  }

  return null;
}

// -------------------------------------------------------------- schiftingsvraag

/**
 * Schat een schiftingsvraag. Nooit 0, nooit een rond getal: bij gelijke stand
 * wint wie het dichtst zit, en ronde getallen kiest iedereen.
 */
export function schatSchifting(vraag, pagina, context = "") {
  const alles = `${context}\n${pagina}`;

  // Staat er een aantal in de vraag zelf ("hoeveel van de 500 ballen..."),
  // dan is dat het beste anker dat we hebben.
  const inVraag = alleGetallen(vraag).filter((n) => n >= 10 && n <= 1_000_000);
  if (inVraag.length) {
    const anker = Math.max(...inVraag);
    const schatting = Math.round(anker * 0.62) + 3;   // iets onder het midden
    return { waarde: String(schatting), reden: `schatting op basis van ${anker} uit de vraag` };
  }

  // Gaat het over het aantal deelnemers, dan hangt dat vooral aan de waarde van
  // de prijs: hoe groter de prijs, hoe meer volk. Ruwe vuistregel, maar veel
  // beter dan niets invullen — en beter dan een rond getal.
  if (/deelnem|inzending|mensen|personen/i.test(vraag)) {
    const prijzen = [...alles.matchAll(/(?:€|eur)\s*(\d[\d .,]*)|(\d[\d .,]*)\s*euro/gi)]
      .map((t) => Number((t[1] || t[2]).replace(/[ .]/g, "").replace(",", ".")))
      .filter((n) => Number.isFinite(n) && n > 0 && n < 100000);
    const waarde = prijzen.length ? Math.max(...prijzen) : 100;
    const schatting = Math.min(25000, Math.max(800, Math.round(500 + waarde * 12)));
    return {
      waarde: String(schatting + 7),  // net niet rond
      reden: prijzen.length
        ? `schatting deelnemers op basis van prijs €${waarde}`
        : "schatting deelnemers (geen prijswaarde gevonden)",
    };
  }

  // Andere schiftingsvraag ("hoeveel snoepjes in de bokaal"): getallen op de
  // pagina als anker, anders geven we het op — dan is raden zinloos.
  const ankers = alleGetallen(alles).filter((n) => n >= 50 && n <= 100_000);
  if (ankers.length) {
    const gemiddeld = Math.round(ankers.reduce((a, b) => a + b, 0) / ankers.length);
    return { waarde: String(gemiddeld + 3), reden: `schatting op basis van getallen op de pagina` };
  }

  return null;
}

/** Is dit veld een wedstrijd- of schiftingsvraag? */
export function soortVraag(aanwijzing) {
  if (SCHIFTING.test(aanwijzing)) return "schifting";
  if (WEDSTRIJDVRAAG.test(aanwijzing)) return "vraag";
  return null;
}
