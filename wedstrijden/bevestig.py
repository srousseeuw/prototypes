#!/usr/bin/env python3
"""
Dubbele opt-in afhandelen: bevestigingsmails aanklikken.

Veel wedstrijden sturen na deelname een mail met "bevestig je deelname". Zonder
die klik telt de inzending niet. Dit leest de mailbox via IMAP (alleen lezen —
BODY.PEEK, dus mails blijven ongelezen) en opent enkel bevestigingslinks van
domeinen waar we de voorbije dagen zelf aan deelnamen. Alles daarbuiten blijft
onaangeroerd; een bevestigingsknop in een willekeurige mail wordt dus niet
zomaar aangeklikt.

Staat standaard uit (config.bevestiging.actief). Aanzetten vraagt een
app-wachtwoord van Google in een omgevingsvariabele — nooit in config.json.
"""
from __future__ import annotations

import email
import imaplib
import os
import re
import urllib.parse
from datetime import datetime, timedelta
from email.header import decode_header, make_header

from bronnen import BronFout, haal

BEVESTIG_WOORDEN = re.compile(
    r"bevestig|confirm|verifieer|verify|activeer|activate|valideer|opt.?in|double.?opt", re.I)

UITSLUITEN_LINKS = re.compile(
    r"uitschrijv|unsubscribe|afmeld|privacy|voorwaarden|cookie|facebook\.com|instagram\.com|"
    r"twitter\.com|x\.com|linkedin\.com|whatsapp", re.I)


def _kop(rauw: str) -> str:
    try:
        return str(make_header(decode_header(rauw or "")))
    except Exception:
        return rauw or ""


def _tekstdelen(bericht) -> list[str]:
    delen = []
    for deel in bericht.walk():
        if deel.get_content_type() not in ("text/plain", "text/html"):
            continue
        try:
            inhoud = deel.get_payload(decode=True) or b""
            delen.append(inhoud.decode(deel.get_content_charset() or "utf-8", errors="replace"))
        except Exception:
            continue
    return delen


def _links(tekst: str) -> list[tuple[str, str]]:
    """(url, omringende tekst) uit zowel HTML-links als kale URL's."""
    gevonden = []
    for treffer in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', tekst, re.I | re.S):
        gevonden.append((treffer.group(1), re.sub(r"<[^>]+>", " ", treffer.group(2))))
    for treffer in re.finditer(r'(?<!["\'=])(https?://[^\s<>"\']{10,})', tekst):
        gevonden.append((treffer.group(1), ""))
    return gevonden


def _domein(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower().removeprefix("www.")


def bevestig(config: dict, opslag, log=print) -> list[dict]:
    """Zoekt bevestigingsmails en opent de links. Geeft de gedane bevestigingen terug."""
    instellingen = config.get("bevestiging", {})
    if not instellingen.get("actief"):
        log("  bevestiging staat uit (config.bevestiging.actief)")
        return []

    wachtwoord = os.environ.get(instellingen.get("wachtwoord_env", "GMAIL_APP_WACHTWOORD"), "")
    if not wachtwoord:
        log(f"  ! geen wachtwoord in ${instellingen.get('wachtwoord_env')} — bevestiging overgeslagen")
        return []

    uren = int(instellingen.get("max_uren", 72))
    eigen_domeinen = {_domein(regel["url"]) for regel in opslag.wachtend_op_bevestiging(uren) if regel.get("url")}
    if not eigen_domeinen:
        log("  geen recente deelnames om te bevestigen")
        return []

    sinds = (datetime.now() - timedelta(hours=uren + 24)).strftime("%d-%b-%Y")
    bevestigd: list[dict] = []

    try:
        verbinding = imaplib.IMAP4_SSL(instellingen.get("imap_server", "imap.gmail.com"),
                                       timeout=30)  # cron mag nooit blijven hangen
        verbinding.login(instellingen["gebruiker"], wachtwoord)
        verbinding.select(instellingen.get("map", "INBOX"), readonly=True)
        _, nummers = verbinding.search(None, f'(SINCE {sinds})')
    except Exception as fout:
        log(f"  ! mailbox niet bereikbaar: {fout}")
        return []

    try:
        for nummer in (nummers[0].split() if nummers and nummers[0] else [])[-200:]:
            _, brokken = verbinding.fetch(nummer, "(BODY.PEEK[])")
            if not brokken or not isinstance(brokken[0], tuple):
                continue
            bericht = email.message_from_bytes(brokken[0][1])
            afzender = _kop(bericht.get("From", ""))
            onderwerp = _kop(bericht.get("Subject", ""))
            afzender_domein = _domein("http://" + afzender.split("@")[-1].strip(" >")) if "@" in afzender else ""

            if not BEVESTIG_WOORDEN.search(onderwerp) and not any(
                    d in afzender_domein or afzender_domein in d for d in eigen_domeinen if d):
                continue

            for tekst in _tekstdelen(bericht):
                for url, linktekst in _links(tekst):
                    if UITSLUITEN_LINKS.search(url) or UITSLUITEN_LINKS.search(linktekst):
                        continue
                    if not (BEVESTIG_WOORDEN.search(url) or BEVESTIG_WOORDEN.search(linktekst)):
                        continue
                    doel = _domein(url)
                    if not any(doel.endswith(d) or d.endswith(doel) for d in eigen_domeinen if d):
                        continue
                    try:
                        haal(url, timeout=20)
                    except BronFout as fout:
                        log(f"  ! bevestiging mislukt ({onderwerp[:50]}): {fout}")
                        continue
                    log(f"  ✓ bevestigd: {onderwerp[:60]}")
                    bevestigd.append({"onderwerp": onderwerp, "afzender": afzender, "url": url})
                    break
                else:
                    continue
                break
    finally:
        try:
            verbinding.close()
            verbinding.logout()
        except Exception:
            pass

    return bevestigd
