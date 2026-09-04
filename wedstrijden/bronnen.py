#!/usr/bin/env python3
"""
Bronnen ophalen: van een overzichtssite naar een lijst wedstrijden.

Per bron proberen we in deze volgorde:
  1. een RSS/Atom-feed (opgegeven, of gevonden via <link rel="alternate">,
     of via de gebruikelijke paden /feed/, /rss, /feed.xml, ...)
  2. de HTML-pagina zelf, waaruit we de links met een deftige titel plukken.

Een feed is altijd te verkiezen: minder verkeer, propere titels en datums.
Alles hier is stdlib — geen dependencies, zoals de rest van deze repo.
"""
from __future__ import annotations

import gzip
import re
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser

UA = "ocior-wedstrijdbot/1.0 (+https://ocior.be; persoonlijk gebruik)"

FEED_PADEN = ["/feed/", "/feed", "/rss", "/rss.xml", "/feed.xml", "/atom.xml", "/index.xml"]

_robots_cache: dict[str, urllib.robotparser.RobotFileParser | None] = {}


class BronFout(Exception):
    """Een bron kon niet opgehaald of begrepen worden."""


# --------------------------------------------------------------------------- http

def haal(url: str, timeout: int = 25) -> str:
    """Haalt een URL op als tekst. Gooit BronFout bij netwerk- of HTTP-fouten."""
    verzoek = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "nl-BE,nl;q=0.9",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(verzoek, timeout=timeout) as antwoord:
            rauw = antwoord.read()
            if antwoord.headers.get("Content-Encoding") == "gzip":
                rauw = gzip.decompress(rauw)
            charset = antwoord.headers.get_content_charset() or "utf-8"
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as fout:
        raise BronFout(f"{url}: {fout}") from fout
    return rauw.decode(charset, errors="replace")


def mag_ophalen(url: str) -> bool:
    """Respecteert robots.txt van de overzichtssite. Onbereikbaar = wel toegestaan."""
    stuk = urllib.parse.urlsplit(url)
    basis = f"{stuk.scheme}://{stuk.netloc}"
    if basis not in _robots_cache:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(basis + "/robots.txt")
        try:
            parser.read()
        except Exception:
            _robots_cache[basis] = None
        else:
            _robots_cache[basis] = parser
    parser = _robots_cache[basis]
    if parser is None:
        return True
    return parser.can_fetch(UA, url)


# --------------------------------------------------------------------------- feeds

def feed_kandidaten(html: str, basis_url: str) -> list[str]:
    """Feed-URL's uit de <head> van een pagina, plus de gebruikelijke paden."""
    gevonden: list[str] = []
    for tag in re.findall(r"<link\b[^>]*>", html, flags=re.I):
        if not re.search(r'rel=["\']?alternate', tag, flags=re.I):
            continue
        if not re.search(r"(rss|atom)\+xml", tag, flags=re.I):
            continue
        href = re.search(r'href=["\']([^"\']+)["\']', tag, flags=re.I)
        if href:
            gevonden.append(urllib.parse.urljoin(basis_url, unescape(href.group(1))))
    stuk = urllib.parse.urlsplit(basis_url)
    for pad in FEED_PADEN:
        gevonden.append(f"{stuk.scheme}://{stuk.netloc}{pad}")
        if stuk.path not in ("", "/"):
            gevonden.append(urllib.parse.urljoin(basis_url.rstrip("/") + "/", pad.lstrip("/")))
    uniek: list[str] = []
    for url in gevonden:
        if url not in uniek:
            uniek.append(url)
    return uniek


def is_feed(tekst: str) -> bool:
    kop = tekst.lstrip()[:400].lower()
    return "<rss" in kop or "<feed" in kop or "<rdf:rdf" in kop


def _tekst(element, *namen) -> str:
    """Eerste niet-lege waarde van de gevraagde tags, namespace-onafhankelijk."""
    for naam in namen:
        for kind in element.iter():
            tag = kind.tag.split("}")[-1].lower()
            if tag != naam:
                continue
            if kind.text and kind.text.strip():
                return unescape(kind.text.strip())
            href = kind.get("href")
            if href:
                return href
    return ""


def parse_feed(xml_tekst: str, bron_naam: str) -> list[dict]:
    """RSS 2.0, RDF en Atom naar een uniforme itemlijst."""
    try:
        wortel = ET.fromstring(xml_tekst.encode("utf-8", errors="replace"))
    except ET.ParseError as fout:
        raise BronFout(f"onleesbare feed: {fout}") from fout

    items = []
    for element in wortel.iter():
        if element.tag.split("}")[-1].lower() not in ("item", "entry"):
            continue
        titel = _tekst(element, "title")
        link = _tekst(element, "link")
        if not titel or not link:
            continue
        items.append({
            "titel": strip_html(titel),
            "url": link.strip(),
            "bron": bron_naam,
            "samenvatting": strip_html(_tekst(element, "description", "summary", "content"))[:600],
            "datum": normaliseer_datum(_tekst(element, "pubdate", "published", "updated", "date")),
        })
    return items


def normaliseer_datum(rauw: str) -> str:
    if not rauw:
        return ""
    try:
        return parsedate_to_datetime(rauw).astimezone(timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        pass
    for patroon in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(rauw.strip(), patroon).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


# --------------------------------------------------------------------------- html

def verzamel_links(html: str, basis_url: str) -> list[tuple[str, str]]:
    """Alle links met hun zichtbare tekst, als (absolute url, tekst).

    Via de HTML-parser en niet met een regex: veel sites serveren geminificeerde
    HTML waarin attributen geen aanhalingstekens hebben (<a href=https://... >).
    Een regex die quotes verwacht, mist precies de doorklik naar de wedstrijd.
    """
    verzamelaar = _LinkVerzamelaar()
    try:
        verzamelaar.feed(html)
    except Exception:
        pass
    links = []
    for href, tekst in verzamelaar.links:
        try:
            url = urllib.parse.urljoin(basis_url, unescape(href)).split("#")[0]
        except ValueError:
            continue
        if url.startswith(("http://", "https://")):
            links.append((url, tekst))
    return links


class _LinkVerzamelaar(HTMLParser):
    """Verzamelt <a href> met hun zichtbare tekst."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._tekst: list[str] = []
        self._diepte = 0

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        if self._href is not None:
            self._diepte += 1
            return
        href = dict(attrs).get("href")
        if href:
            self._href = href
            self._tekst = []

    def handle_data(self, data):
        if self._href is not None:
            self._tekst.append(data)

    def handle_endtag(self, tag):
        if tag != "a" or self._href is None:
            return
        if self._diepte:
            self._diepte -= 1
            return
        tekst = " ".join("".join(self._tekst).split())
        self.links.append((self._href, tekst))
        self._href, self._tekst = None, []


def strip_html(rauw: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", rauw or "")).split())


ROMMEL = re.compile(
    r"^(home|contact|privacy|cookie|inloggen|registreren|aanmelden|meer|lees meer|volgende|vorige|"
    r"algemene voorwaarden|over ons|nieuwsbrief|deel|delen|facebook|twitter|instagram)\b", re.I)


def parse_html_lijst(html: str, basis_url: str, bron_naam: str) -> list[dict]:
    """Plukt kandidaat-wedstrijden uit een overzichtspagina.

    Een linktekst van minstens 15 tekens met meer dan twee woorden is doorgaans
    een wedstrijdtitel; navigatie is korter of staat in de ROMMEL-lijst.
    """
    verzamelaar = _LinkVerzamelaar()
    verzamelaar.feed(html)

    items, gezien = [], set()
    for href, tekst in verzamelaar.links:
        if not tekst or len(tekst) < 15 or len(tekst.split()) < 3 or ROMMEL.match(tekst):
            continue
        url = urllib.parse.urljoin(basis_url, href)
        if not url.startswith(("http://", "https://")) or "#" == href[:1]:
            continue
        url = url.split("#")[0]
        if url in gezien:
            continue
        gezien.add(url)
        items.append({"titel": tekst[:200], "url": url, "bron": bron_naam,
                      "samenvatting": "", "datum": ""})
    return items


# --------------------------------------------------------------------------- publiek

def haal_bron(bron: dict, timeout: int = 25) -> tuple[list[dict], str]:
    """Haalt één bron op. Geeft (items, gebruikte methode) terug."""
    url, naam = bron["url"], bron.get("naam", bron["url"])
    soort = bron.get("type", "auto")

    if not mag_ophalen(url):
        raise BronFout(f"{naam}: robots.txt verbiedt ophalen van {url}")

    if soort == "rss":
        return parse_feed(haal(url, timeout), naam), f"feed {url}"

    inhoud = haal(url, timeout)

    if is_feed(inhoud):
        return parse_feed(inhoud, naam), f"feed {url}"

    if soort != "html":
        for kandidaat in feed_kandidaten(inhoud, url)[:6]:
            if not mag_ophalen(kandidaat):
                continue
            try:
                mogelijk = haal(kandidaat, timeout)
            except BronFout:
                continue
            if is_feed(mogelijk):
                try:
                    items = parse_feed(mogelijk, naam)
                except BronFout:
                    continue
                if items:
                    return items, f"feed {kandidaat}"

    return parse_html_lijst(inhoud, url, naam), f"html {url}"


def verzamel(config: dict, log=print) -> tuple[list[dict], list[str]]:
    """Alle actieve bronnen ophalen. Geeft (items, foutmeldingen) terug."""
    items, fouten = [], []
    timeout = config.get("deelname", {}).get("timeout_seconden", 25)
    for bron in config.get("bronnen", []):
        if not bron.get("actief", True):
            continue
        try:
            gevonden, methode = haal_bron(bron, timeout)
        except BronFout as fout:
            fouten.append(str(fout))
            log(f"  ✗ {bron.get('naam', bron['url'])}: {fout}")
            continue
        log(f"  ✓ {bron.get('naam')}: {len(gevonden)} items via {methode}")
        items.extend(gevonden)
    return items, fouten
