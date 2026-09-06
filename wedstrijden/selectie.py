#!/usr/bin/env python3
"""
Selectie: welke wedstrijd is nuttig voor het gezin, en welke laten we links liggen.

Score = som van de gewichten van de categorieën waarvan een woord voorkomt in
titel + samenvatting + URL, plus een bonus voor "gratis"-signalen. Eén woord uit
de uitsluitlijst duwt de score onder nul, zodat gokken, tabak en sms-spelletjes
er sowieso uit vallen. Alle woorden en gewichten staan in config.json.
"""
from __future__ import annotations

import re
import unicodedata


def normaliseer(tekst: str) -> str:
    """Kleine letters, accenten weg — zo matcht 'wélness' ook op 'wellness'."""
    ontleed = unicodedata.normalize("NFKD", tekst or "")
    zonder_accent = "".join(teken for teken in ontleed if not unicodedata.combining(teken))
    return re.sub(r"[^a-z0-9]+", " ", zonder_accent.lower()).strip()


def bevat(hooiberg: str, naald: str) -> bool:
    """Match aan het begin van een woord, samenstellingen inbegrepen.

    Het Nederlands plakt aan elkaar: 'gezin' moet 'gezinsticket' vangen, 'kind'
    ook 'kinderfiets', 'plopsa' ook 'Plopsaland'. Vandaar enkel een grens links.
    Rechts vrijlaten kan niet: zonder linkergrens zou 'bon' aanslaan op
    'abonnement' en 'gok' op elk woord dat die letters toevallig bevat.
    """
    naald = normaliseer(naald)
    if not naald:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(naald)}", hooiberg) is not None


def beoordeel(item: dict, selectie: dict) -> dict:
    """Geeft het item terug met score, categorieën en de redenen erbij."""
    tekst = normaliseer(" ".join([
        item.get("titel", ""),
        item.get("samenvatting", ""),
        item.get("url", "").replace("-", " ").replace("/", " "),
    ]))

    score = 0
    categorieen: list[str] = []
    redenen: list[str] = []

    for naam, blok in (selectie.get("categorieen") or {}).items():
        treffers = [woord for woord in blok.get("woorden", []) if bevat(tekst, woord)]
        if not treffers:
            continue
        gewicht = int(blok.get("gewicht", 1))
        score += gewicht
        categorieen.append(naam)
        redenen.append(f"{naam} (+{gewicht}): {', '.join(treffers[:3])}")

    gratis_treffers = [woord for woord in selectie.get("gratis_woorden", []) if bevat(tekst, woord)]
    if gratis_treffers:
        bonus = int(selectie.get("gratis_bonus", 0))
        score += bonus
        redenen.append(f"gratis (+{bonus}): {', '.join(gratis_treffers[:2])}")

    uitgesloten = [woord for woord in selectie.get("uitsluiten", []) if bevat(tekst, woord)]
    if uitgesloten:
        straf = int(selectie.get("uitsluiten_gewicht", -20))
        score += straf
        redenen.append(f"uitgesloten ({straf}): {', '.join(uitgesloten[:3])}")

    resultaat = dict(item)
    resultaat["score"] = score
    resultaat["categorieen"] = categorieen
    resultaat["redenen"] = redenen
    resultaat["uitgesloten"] = bool(uitgesloten)
    return resultaat


def kies(items: list[dict], selectie: dict) -> list[dict]:
    """Beoordeelt alles, gooit dubbels eruit en houdt de bruikbare over."""
    drempel = int(selectie.get("min_score", 4))
    maximum = int(selectie.get("max_per_nacht", 25))

    beste: dict[str, dict] = {}
    for item in items:
        beoordeeld = beoordeel(item, selectie)
        sleutel = beoordeeld["url"].rstrip("/").lower()
        vorig = beste.get(sleutel)
        if vorig is None or beoordeeld["score"] > vorig["score"]:
            beste[sleutel] = beoordeeld

    bruikbaar = [i for i in beste.values() if not i["uitgesloten"] and i["score"] >= drempel]
    bruikbaar.sort(key=lambda i: (-i["score"], i["titel"]))
    return bruikbaar[:maximum]
