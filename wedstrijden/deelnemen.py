#!/usr/bin/env python3
"""
Deelnemen: het formulier van een wedstrijd invullen en versturen.

Twee manieren:
  http        → formulier uit de HTML halen en zelf posten (snel, geen browser,
                werkt bij eenvoudige formulieren)
  playwright  → een echte browser laten klikken (voor JavaScript-formulieren;
                enkel als playwright geïnstalleerd is)

En drie uitkomsten:
  gedaan      → verstuurd en de pagina bevestigt het
  proefdraai  → dry_run stond aan; we tonen wat we zouden versturen
  handmatig   → captcha, login, bestand nodig, of geen formulier gevonden;
                de wedstrijd komt in de digest zodat jij kan beslissen

Bewust ingebouwde remmen:
  * dry_run staat standaard aan (config.deelname.dry_run)
  * max_per_nacht en pauze_seconden tussen twee deelnames
  * captcha of een verplicht vinkje dat we niet begrijpen → nooit gokken,
    maar doorschuiven naar "handmatig"
  * per wedstrijd maar één keer (zie opslag.py) — dat is meestal ook de regel
"""
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from bronnen import UA, BronFout, haal, strip_html

CAPTCHA_SPOREN = ("recaptcha", "g-recaptcha", "hcaptcha", "h-captcha", "cf-turnstile",
                  "turnstile", "friendlycaptcha", "captcha")

# Formulieren die géén deelnameformulier zijn. Zonder deze filter kiest de bot
# op elke WordPress-site het reactieformulier (dat heeft ook een e-mailveld) en
# plaatst hij je naam en adres publiek onder een blogartikel.
GEEN_DEELNAME_ACTIE = re.compile(
    r"wp-comments-post|/comment|#comment|/search|/zoek|list-manage\.com|"
    r"mailchimp|newsletter|nieuwsbrief|/login|/inloggen|/account", re.I)

GEEN_DEELNAME_VELDEN = (
    {"comment", "author"},        # WordPress-reacties
    {"comment", "email"},
    {"bericht", "naam"},          # contactformulier
)

ZOEKVELDEN = ({"s"}, {"q"}, {"search"}, {"zoek"}, {"s", "submit"}, {"q", "submit"})

GELUKT_STANDAARD = ("bedankt", "je deelname", "uw deelname", "deelname geregistreerd",
                    "succesvol", "gelukt", "bevestigingsmail", "thank you", "veel succes")

# Hoe we een invoerveld herkennen aan zijn name/id/label.
VELDPATRONEN = [
    (r"voornaam|firstname|first_name|fname|given", "voornaam"),
    (r"achternaam|lastname|last_name|lname|surname|familienaam", "achternaam"),
    (r"\bnaam\b|fullname|full_name|\bname\b", "volledige_naam"),
    (r"e.?mail", "email"),
    (r"telefoon|gsm|mobiel|phone|tel\b", "telefoon"),
    (r"straat|street|adres|address(?!.*mail)", "straat"),
    (r"huisnummer|nummer|house.?number|streetnumber", "huisnummer"),
    (r"postcode|zip|postal", "postcode"),
    (r"gemeente|woonplaats|stad|city|plaats", "gemeente"),
    (r"land|country", "land"),
    (r"geboorte|birth|dob", "geboortedatum"),
]


class FormulierParser(HTMLParser):
    """Haalt de formulieren met hun velden en labels uit een pagina."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.formulieren: list[dict] = []
        self._huidig: dict | None = None
        self._label_voor: str | None = None
        self._label_tekst: list[str] = []
        self.labels: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        kenmerken = {k.lower(): (v or "") for k, v in attrs}
        if tag == "form":
            self._huidig = {"action": kenmerken.get("action", ""),
                            "method": (kenmerken.get("method") or "get").lower(),
                            "velden": []}
        elif tag in ("input", "select", "textarea") and self._huidig is not None:
            self._huidig["velden"].append({
                "tag": tag,
                "type": (kenmerken.get("type") or ("select" if tag == "select" else "text")).lower(),
                "name": kenmerken.get("name", ""),
                "id": kenmerken.get("id", ""),
                "value": kenmerken.get("value", ""),
                "placeholder": kenmerken.get("placeholder", ""),
                "required": "required" in kenmerken,
                "checked": "checked" in kenmerken,
            })
        elif tag == "label":
            self._label_voor = kenmerken.get("for", "")
            self._label_tekst = []

    def handle_data(self, data):
        if self._label_voor is not None:
            self._label_tekst.append(data)

    def handle_endtag(self, tag):
        if tag == "form" and self._huidig is not None:
            self.formulieren.append(self._huidig)
            self._huidig = None
        elif tag == "label" and self._label_voor is not None:
            if self._label_voor:
                self.labels[self._label_voor] = " ".join("".join(self._label_tekst).split())
            self._label_voor, self._label_tekst = None, []


# --------------------------------------------------------------------------- recepten

def laad_recepten(map_pad: Path) -> list[dict]:
    """Recepten zijn handmatige uitzonderingen per site; zie recepten/_voorbeeld.json."""
    recepten = []
    for pad in sorted(Path(map_pad).glob("*.json")):
        if pad.name.startswith("_"):
            continue
        try:
            recepten.append(json.loads(pad.read_text(encoding="utf-8")))
        except json.JSONDecodeError as fout:
            print(f"  ! recept {pad.name} is geen geldige JSON: {fout}")
    return recepten


def zoek_recept(url: str, recepten: list[dict]) -> dict | None:
    domein = urllib.parse.urlsplit(url).netloc.lower().removeprefix("www.")
    for recept in recepten:
        if recept.get("url_patroon") and re.search(recept["url_patroon"], url, re.I):
            return recept
        if recept.get("domein", "").lower().removeprefix("www.") == domein:
            return recept
    return None


# --------------------------------------------------------------------------- invullen

def waarden(deelnemer: dict) -> dict:
    """De gegevens die in een formulier terechtkomen."""
    gegevens = dict(deelnemer)
    gegevens["volledige_naam"] = f"{deelnemer.get('voornaam','')} {deelnemer.get('achternaam','')}".strip()
    return gegevens


def vul_sjabloon(sjabloon: str, gegevens: dict) -> str:
    """Vervangt {{voornaam}} en co. in een receptwaarde."""
    def vervang(treffer):
        return str(gegevens.get(treffer.group(1).strip(), ""))
    return re.sub(r"\{\{([^}]+)\}\}", vervang, sjabloon)


def raad_veld(veld: dict, labels: dict) -> str | None:
    """Welk gegeven hoort in dit invoerveld? None = onbekend."""
    if veld["type"] == "email":
        return "email"
    if veld["type"] == "tel":
        return "telefoon"
    aanwijzing = " ".join([veld.get("name", ""), veld.get("id", ""),
                           veld.get("placeholder", ""), labels.get(veld.get("id", ""), "")]).lower()
    for patroon, sleutel in VELDPATRONEN:
        if re.search(patroon, aanwijzing):
            return sleutel
    return None


def is_deelnameformulier(formulier: dict) -> bool:
    """Zeef reactie-, zoek-, nieuwsbrief- en loginformulieren eruit."""
    if GEEN_DEELNAME_ACTIE.search(formulier.get("action", "")):
        return False

    namen = {(v.get("name") or "").lower() for v in formulier["velden"] if v.get("name")}
    if any(kern <= namen for kern in GEEN_DEELNAME_VELDEN):
        return False
    if any(namen == zoek for zoek in ZOEKVELDEN):
        return False

    invulbaar = [v for v in formulier["velden"]
                 if v["type"] not in ("hidden", "submit", "button", "image")]
    # Eén enkel e-mailveld is een nieuwsbriefinschrijving, geen wedstrijd.
    if len(invulbaar) <= 1:
        return False
    return True


def kies_formulier(formulieren: list[dict]) -> dict | None:
    """Het deelnameformulier: heeft een e-mailveld, en is er ook echt één."""
    kandidaten = []
    for formulier in formulieren:
        velden = formulier["velden"]
        heeft_email = any(v["type"] == "email" or re.search(r"e.?mail", v.get("name", ""), re.I) for v in velden)
        zichtbaar = [v for v in velden if v["type"] not in ("hidden", "submit", "button", "image")]
        if heeft_email and zichtbaar and is_deelnameformulier(formulier):
            kandidaten.append((len(zichtbaar), formulier))
    if not kandidaten:
        return None
    return max(kandidaten, key=lambda p: p[0])[1]


def bouw_payload(formulier: dict, labels: dict, gegevens: dict,
                 recept: dict | None) -> tuple[dict, list[str]]:
    """Bouwt de POST-gegevens. Tweede return: velden die we niet begrepen."""
    payload: dict[str, str] = {}
    onbekend: list[str] = []
    vaste_velden = (recept or {}).get("velden", {})

    for veld in formulier["velden"]:
        naam = veld.get("name")
        if not naam or veld["type"] in ("submit", "button", "image", "file", "password"):
            if veld["type"] in ("file", "password"):
                onbekend.append(f"{veld['type']}-veld ({naam or veld.get('id')})")
            continue

        if naam in vaste_velden:
            payload[naam] = vul_sjabloon(str(vaste_velden[naam]), gegevens)
            continue

        if veld["type"] == "hidden":
            payload[naam] = veld.get("value", "")
            continue

        if veld["type"] == "checkbox":
            label = (labels.get(veld.get("id", ""), "") + " " + naam).lower()
            # Voorwaarden en leeftijdsbevestiging aanvinken; reclame enkel als het mag.
            if re.search(r"voorwaard|reglement|akkoord|privacy|18|leeftijd|terms", label):
                payload[naam] = veld.get("value") or "on"
            elif re.search(r"nieuwsbrief|newsletter|aanbieding|partner|marketing|mailing", label):
                if gegevens.get("nieuwsbrief_toestaan"):
                    payload[naam] = veld.get("value") or "on"
            elif veld["required"]:
                onbekend.append(f"verplicht vinkje ({naam})")
            continue

        if veld["type"] == "radio":
            if veld.get("checked"):
                payload[naam] = veld.get("value", "on")
            elif veld["required"] and naam not in payload:
                onbekend.append(f"verplichte keuze ({naam})")
            continue

        sleutel = raad_veld(veld, labels)
        if sleutel:
            waarde = str(gegevens.get(sleutel, "") or "").strip()
            if waarde:
                payload[naam] = waarde
            elif veld["required"]:
                # Liever niets versturen dan een leeg verplicht veld: dan weet je
                # meteen welk gegeven nog in config.json ontbreekt.
                onbekend.append(f"{sleutel} staat niet in config.json ({naam})")
        elif veld["required"]:
            onbekend.append(f"verplicht veld ({naam})")

    return payload, onbekend


def bevat_captcha(html: str) -> bool:
    lage = html.lower()
    return any(spoor in lage for spoor in CAPTCHA_SPOREN)


def gelukt(html: str, recept: dict | None) -> bool:
    tekst = strip_html(html).lower()
    markeringen = (recept or {}).get("gelukt_indien") or GELUKT_STANDAARD
    return any(m.lower() in tekst for m in markeringen)


# --------------------------------------------------------------------------- uitvoeren

def deelnemen_http(url: str, gegevens: dict, recept: dict | None,
                   dry_run: bool, timeout: int) -> tuple[str, str]:
    """Geeft (status, opmerking) terug."""
    try:
        html = haal(url, timeout)
    except BronFout as fout:
        return "mislukt", f"pagina niet op te halen: {fout}"

    if bevat_captcha(html):
        return "handmatig", "captcha op de pagina"

    parser = FormulierParser()
    parser.feed(html)
    formulier = kies_formulier(parser.formulieren)
    if formulier is None:
        return "handmatig", "geen deelnameformulier gevonden op de pagina"

    # Login herkennen we aan een wachtwoordveld ín dit formulier. Op het hele
    # document zoeken sloeg aan op de inlogknop in elke sitenavigatie.
    if any(v["type"] == "password" for v in formulier["velden"]):
        return "handmatig", "het formulier vraagt een account (wachtwoordveld)"

    payload, onbekend = bouw_payload(formulier, parser.labels, gegevens, recept)
    if onbekend:
        return "handmatig", "niet begrepen: " + "; ".join(onbekend[:4])
    if not any(re.search(r"e.?mail", naam, re.I) for naam in payload):
        return "handmatig", "geen e-mailveld herkend"

    doel = urllib.parse.urljoin(url, formulier["action"] or url)
    if dry_run:
        kort = {k: v for k, v in payload.items() if v}
        return "proefdraai", f"zou POST'en naar {doel} met {len(kort)} velden: {', '.join(sorted(kort)[:8])}"

    data = urllib.parse.urlencode(payload).encode("utf-8")
    verzoek = urllib.request.Request(doel, data=data, headers={
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": url,
        "Accept-Language": "nl-BE,nl;q=0.9",
    })
    try:
        with urllib.request.urlopen(verzoek, timeout=timeout) as antwoord:
            resultaat = antwoord.read().decode("utf-8", errors="replace")
    except Exception as fout:  # netwerk, HTTP-fout, time-out
        return "mislukt", f"versturen mislukt: {fout}"

    if gelukt(resultaat, recept):
        return "gedaan", f"verstuurd naar {doel}"
    return "handmatig", "verstuurd, maar geen bevestiging herkend — zelf nakijken"


def deelnemen_playwright(url: str, gegevens: dict, recept: dict | None,
                         dry_run: bool, config: dict) -> tuple[str, str]:
    """Formulieren die JavaScript nodig hebben. Vereist `pip install playwright`."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "handmatig", "playwright niet geïnstalleerd (pip install playwright)"

    velden = (recept or {}).get("velden", {})
    if not velden:
        return "handmatig", "playwright-modus vraagt een recept met selectors"

    timeout = int(config.get("timeout_seconden", 30)) * 1000
    chromium_pad = config.get("chromium_pad") or None

    with sync_playwright() as pw:
        starter = pw.chromium.launch(headless=True, executable_path=chromium_pad)
        pagina = starter.new_page(locale="nl-BE")
        try:
            pagina.goto(url, timeout=timeout, wait_until="domcontentloaded")
            if bevat_captcha(pagina.content()):
                return "handmatig", "captcha op de pagina"
            for selector, sjabloon in velden.items():
                pagina.fill(selector, vul_sjabloon(str(sjabloon), gegevens), timeout=timeout)
            for selector in (recept or {}).get("aanvinken", []):
                pagina.check(selector, timeout=timeout)
            if dry_run:
                return "proefdraai", f"formulier ingevuld, niet verstuurd ({len(velden)} velden)"
            pagina.click(recept["verzend"], timeout=timeout)
            pagina.wait_for_timeout(3000)
            if gelukt(pagina.content(), recept):
                return "gedaan", "verstuurd via browser"
            return "handmatig", "verstuurd, maar geen bevestiging herkend — zelf nakijken"
        except Exception as fout:
            return "mislukt", f"browser: {type(fout).__name__}: {fout}"
        finally:
            starter.close()


def doe_mee(items: list[dict], config: dict, opslag, log=print) -> list[dict]:
    """Loopt de gekozen wedstrijden af en probeert er aan deel te nemen."""
    instellingen = config.get("deelname", {})
    dry_run = bool(instellingen.get("dry_run", True))
    maximum = int(instellingen.get("max_per_nacht", 8))
    pauze = int(instellingen.get("pauze_seconden", 25))
    timeout = int(instellingen.get("timeout_seconden", 30))
    alleen_met_recept = bool(instellingen.get("alleen_met_recept", True))
    max_pogingen = int(instellingen.get("max_pogingen", 3))

    recepten = laad_recepten(Path(__file__).parent / "recepten")
    gegevens = waarden(config.get("deelnemer", {}))
    resultaten: list[dict] = []
    gedaan = 0

    for item in items:
        if gedaan >= maximum:
            opslag.zet_status(item["url"], "nieuw", "wachtrij vol voor vannacht")
            resultaten.append({**item, "status": "overgeslagen", "opmerking": "max_per_nacht bereikt"})
            continue
        if opslag.al_gedaan(item["url"]):
            continue
        if opslag.pogingen(item["url"]) >= max_pogingen:
            opslag.zet_status(item["url"], "overgeslagen",
                              f"na {max_pogingen} pogingen opgegeven")
            continue

        recept = zoek_recept(item["url"], recepten)
        geprobeerd = True
        if recept is None and alleen_met_recept:
            status, opmerking = "handmatig", "geen recept voor deze site"
            geprobeerd = False  # niets opgehaald: telt niet mee voor max_per_nacht
        elif recept and recept.get("modus") == "playwright":
            status, opmerking = deelnemen_playwright(item["url"], gegevens, recept, dry_run, instellingen)
        else:
            status, opmerking = deelnemen_http(item["url"], gegevens, recept, dry_run, timeout)

        log(f"  [{status}] {item['titel'][:70]} — {opmerking}")
        if geprobeerd:
            opslag.tel_poging(item["url"])
        opslag.zet_status(item["url"], status, opmerking)
        opslag.noteer(item, status, opmerking)
        resultaten.append({**item, "status": status, "opmerking": opmerking})

        if geprobeerd:
            gedaan += 1
            if pauze and gedaan < maximum:
                time.sleep(pauze)

    return resultaten
