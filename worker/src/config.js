// Welke overzichtssites afgelopen worden, en hoe voorzichtig de Worker doet.
// De woordenlijsten (wat nuttig is, wat we links laten liggen) staan in
// ../../wedstrijden/selectie.json — gedeeld met het Python-script.

export const BRONNEN = [
  // België
  { naam: "Wedstrijden.be", url: "https://www.wedstrijden.be/wedstrijden", type: "auto", actief: true },
  { naam: "WinPrijzen.be", url: "https://winprijzen.be/", type: "auto", actief: true },
  { naam: "DeWedstrijden.be", url: "https://www.dewedstrijden.be/", type: "auto", actief: true },
  { naam: "GoGratis.be", url: "https://www.gogratis.be/cat/wedstrijden/", type: "auto", actief: true },
  { naam: "Gratis.be", url: "https://gratis.be/alle/gratis-wedstrijden/", type: "auto", actief: true },
  { naam: "Prijzen-winnen.com", url: "https://www.prijzen-winnen.com/", type: "auto", actief: true },
  { naam: "Tegen de crisis", url: "https://www.tegendecrisis.be/category/wedstrijden-belgie/", type: "auto", actief: true },
  // Nederland — Essen ligt tegen de grens, maar let op: veel NL-acties leveren
  // enkel binnen Nederland en vragen een NL-adres of postcode.
  { naam: "Prijzenpakker.nl", url: "https://www.prijzenpakker.nl/", type: "auto", actief: true },
  { naam: "Winactie.nl", url: "https://www.winactie.nl/", type: "auto", actief: true },
  { naam: "Gratis.nl", url: "https://www.gratis.nl/winacties", type: "auto", actief: true },
];

export const INSTELLINGEN = {
  // Eerste nacht: er staat nog niets in KV, dus alles wat nu online staat is
  // "nieuw". Dan mag hij meer doen dan op een gewone nacht — de inhaalbeweging.
  maxPerNacht: 10,
  maxEersteNacht: 15,
  // Gratis plan: 50 subrequests per uitvoering. We houden wat marge.
  // Zit je op Workers Paid, zet dan MAX_SUBREQUESTS als var op bv. 900.
  maxSubrequests: 45,
  // Zoveel fetches houden we opzij voor het inschrijven zelf, zodat het
  // ophalen van bronnen nooit het hele budget opsoupeert.
  reserveVoorDeelnames: 25,
  maxPogingen: 3,
  pauzeMs: 2500,
  bewaarDagen: 180,
};
