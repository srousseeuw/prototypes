#!/usr/bin/env python3
"""
Wedstrijdvragen en schiftingsvragen invullen.

Zelfde logica als worker/src/antwoord.js, hier voor de Mac-versie die met een
echte browser werkt.

  Wedstrijdvraag  — heeft één juist antwoord. Dat staat vaak op de pagina zelf
                    of in de samenvatting van de overzichtssite. Vinden we het
                    niet overtuigend, dan gokken we niet: een fout antwoord
                    maakt de deelname toch ongeldig.

  Schiftingsvraag — heeft geen juist antwoord; wie het dichtst zit, wint. Leeg
                    laten kost je de wedstrijd, dus schatten we — nooit 0 en
                    nooit een rond getal, want ronde getallen kiest iedereen.
"""
from __future__ import annotations

import re

SCHIFTING = re.compile(
    r"schifting|tiebreak|schattings?vraag|hoeveel\s+(mensen|deelnemers|personen|inzendingen)"
    r"|aantal\s+(deelnemers|inzendingen)", re.I)

WEDSTRIJDVRAAG = re.compile(r"wedstrijdvraag|vraag|question|antwoord|answer|quiz", re.I)

GETAL = re.compile(r"\d[\d .,]{0,12}\d|\d")


def soort_vraag(aanwijzing: str) -> str | None:
    """'schifting', 'vraag' of None."""
    if SCHIFTING.search(aanwijzing or ""):
        return "schifting"
    if WEDSTRIJDVRAAG.search(aanwijzing or ""):
        return "vraag"
    return None


def _getallen(tekst: str) -> list[float]:
    uit = []
    for treffer in GETAL.finditer(tekst or ""):
        try:
            uit.append(float(treffer.group(0).replace(" ", "").replace(".", "").replace(",", ".")))
        except ValueError:
            continue
    return uit


def _kort_antwoord(rauw: str) -> str | None:
    """De paginatekst loopt na "Antwoord: 1964" gewoon door; streng afknippen."""
    schoon = (rauw or "").strip().strip("\"' .,;")
    getal = re.match(r"\d[\d .,]*", schoon)
    if getal:
        return getal.group(0).strip().rstrip(".,")
    woorden = " ".join(schoon.split()[:3])
    if re.search(r"vraag|question|e-?mail|voornaam|achternaam|formulier", woorden, re.I):
        return None
    return woorden if 1 <= len(woorden) <= 40 else None


def zoek_antwoord(vraag: str, keuzes: list[dict], pagina: str, context: str = "") -> dict | None:
    """keuzes: [{'value': ..., 'tekst': ...}] bij meerkeuze, anders []."""
    alles = f"{context}\n{pagina}"

    # 1. Sites die het antwoord er zelf bij zetten.
    gemeld = re.search(r"(?:juiste\s+)?antwoord(?:\s+is)?\s*[:=]?\s*([A-Za-z0-9À-ÿ][^.\n<]{0,60})",
                       alles, re.I)
    if gemeld:
        gevonden = _kort_antwoord(gemeld.group(1))
        if gevonden and keuzes:
            for keuze in keuzes:
                if gevonden.lower() in (keuze["tekst"].lower(), keuze["value"].lower()):
                    return {"waarde": keuze["value"],
                            "reden": f"antwoord stond op de pagina ({gevonden})"}
        elif gevonden:
            return {"waarde": gevonden, "reden": f'antwoord stond op de pagina ("{gevonden}")'}

    # 2. Meerkeuze: het juiste antwoord staat meestal ook in de wervende tekst
    #    erboven, de afleiders niet.
    if keuzes:
        geteld = []
        vlak = " ".join((pagina or "").split())
        for keuze in keuzes:
            naald = keuze["tekst"].strip()
            aantal = len(re.findall(re.escape(naald), vlak, re.I)) if len(naald) >= 2 else 0
            geteld.append((aantal, keuze))
        geteld.sort(key=lambda p: -p[0])
        if geteld and geteld[0][0] >= 2 and (len(geteld) == 1 or geteld[0][0] > geteld[1][0]):
            aantal, keuze = geteld[0]
            return {"waarde": keuze["value"],
                    "reden": f'meerkeuze: "{keuze["tekst"]}" komt {aantal}× voor in de tekst'}

    # 3. Jaartalvraag waarvan het antwoord in de tekst staat.
    if re.search(r"in welk jaar|sinds wanneer|opgericht", vraag or "", re.I):
        from datetime import date
        jaren = [int(j) for j in _getallen(alles) if 1800 < j <= date.today().year]
        if jaren:
            vaakste = max(set(jaren), key=jaren.count)
            return {"waarde": str(vaakste), "reden": f"jaartal uit de paginatekst ({vaakste})"}

    return None


def schat_schifting(vraag: str, pagina: str, context: str = "") -> dict | None:
    alles = f"{context}\n{pagina}"

    # Staat er een aantal in de vraag zelf, dan is dat het beste anker.
    in_vraag = [n for n in _getallen(vraag or "") if 10 <= n <= 1_000_000]
    if in_vraag:
        anker = max(in_vraag)
        return {"waarde": str(round(anker * 0.62) + 3),
                "reden": f"schatting op basis van {int(anker)} uit de vraag"}

    # Aantal deelnemers schaalt vooral met de waarde van de prijs.
    if re.search(r"deelnem|inzending|mensen|personen", vraag or "", re.I):
        prijzen = []
        for treffer in re.finditer(r"(?:€|eur)\s*(\d[\d .,]*)|(\d[\d .,]*)\s*euro", alles, re.I):
            rauw = treffer.group(1) or treffer.group(2)
            try:
                waarde = float(rauw.replace(" ", "").replace(".", "").replace(",", "."))
            except ValueError:
                continue
            if 0 < waarde < 100_000:
                prijzen.append(waarde)
        waarde = max(prijzen) if prijzen else 100
        schatting = min(25_000, max(800, round(500 + waarde * 12)))
        reden = (f"schatting deelnemers op basis van prijs €{int(waarde)}" if prijzen
                 else "schatting deelnemers (geen prijswaarde gevonden)")
        return {"waarde": str(schatting + 7), "reden": reden}   # net niet rond

    # Andere schiftingsvraag: getallen op de pagina als anker.
    ankers = [n for n in _getallen(alles) if 50 <= n <= 100_000]
    if ankers:
        return {"waarde": str(round(sum(ankers) / len(ankers)) + 3),
                "reden": "schatting op basis van getallen op de pagina"}

    return None
