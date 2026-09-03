#!/usr/bin/env python3
"""
Deelnemen met een echte browser (Playwright).

Waarom dit bestaat: de overzichtssites laden hun "ga naar de wedstrijd"-knop met
JavaScript in. Een gewone HTTP-fetch ziet die knop niet en vindt dus nooit een
deelnameformulier — gemeten op 12 van de 12 echte wedstrijden. Een browser voert
dat JavaScript wél uit en kan doorklikken naar de site van het merk, waar het
formulier staat.

Wat er per wedstrijd gebeurt:
  1. pagina openen en een schermafbeelding maken (zodat je achteraf ziet wat de
     bot zag)
  2. captcha? → stoppen, dat lossen we niet op
  3. staat er een deelnameformulier? zo niet: de doorklikknop zoeken en volgen
  4. het formulier invullen met de logica uit deelnemen.py — inclusief
     wedstrijd- en schiftingsvragen
  5. proefdraai → hier stoppen en tonen wat er ingevuld zou worden
     echt        → versturen en kijken of de pagina bevestigt

Installeren (eenmalig, op de Mac):
    pip3 install playwright && python3 -m playwright install chromium
"""
from __future__ import annotations

import re
from pathlib import Path

import antwoord  # noqa: F401  (gedeeld met deelnemen.py)
from bronnen import strip_html
import deelnemen as deelnemen_mod
from deelnemen import (bevat_captcha, bouw_payload, gelukt, kies_formulier,
                       FormulierParser, waarden)

DOORKLIK = re.compile(
    r"deelnem|meedoen|doe\s*mee|ga naar|naar de (actie|wedstrijd|site)|win nu|"
    r"aanvragen|vraag aan|claim|profiteer|bekijk (de )?(actie|aanbieding)", re.I)

ROMMEL_LINK = re.compile(
    r"facebook|twitter|x\.com|instagram|pinterest|whatsapp|linkedin|"
    r"privacy|voorwaarden|cookie|/tag/|/category/", re.I)


class GeenBrowser(RuntimeError):
    """Playwright is niet geïnstalleerd."""


def _speler():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as fout:
        raise GeenBrowser(
            "playwright is niet geïnstalleerd. Op de Mac:\n"
            "  pip3 install playwright && python3 -m playwright install chromium") from fout
    return sync_playwright


def zoek_doorklik(pagina, basis_url: str, html: str) -> str | None:
    """De knop die naar de echte wedstrijd leidt.

    Eerst dezelfde logica als de HTTP-modus op de gerenderde HTML — die is tegen
    echte sites getest. Levert dat niets op, dan nog eens via de DOM: daar staan
    ook links die pas door JavaScript zijn toegevoegd.
    """
    gevonden = deelnemen_mod.zoek_doorklik(html, basis_url)
    if gevonden:
        return gevonden

    eigen = re.sub(r"^www\.", "", basis_url.split("/")[2]) if "//" in basis_url else ""
    try:
        links = pagina.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => ({tekst: (e.innerText||'').trim().slice(0,60), href: e.href}))")
    except Exception:
        return None

    extern, intern = [], []
    for link in links:
        href, tekst = link.get("href", ""), link.get("tekst", "")
        if not href.startswith("http") or ROMMEL_LINK.search(href):
            continue
        if not DOORKLIK.search(tekst):
            continue
        (intern if eigen and eigen in href else extern).append(href)
    return (extern or intern or [None])[0]


TWEEDE_KLIK = re.compile(
    r"deelnem|doe mee|meedoen|ik doe mee|inschrijv|start|vraag (het |je )?aan|"
    r"claim|win|verzilver|activeer", re.I)


def _formulier_in_frames(pagina):
    """Zoekt het deelnameformulier in de pagina én in alle iframes.

    Wedstrijdformulieren zitten vaak in een iframe van een externe partij
    (Typeform, Formstack, een campagnetool). page.content() toont die niet.
    """
    for frame in pagina.frames:
        try:
            html = frame.content()
        except Exception:
            continue
        parser = FormulierParser()
        parser.feed(html)
        formulier = kies_formulier(parser.formulieren)
        if formulier is not None:
            return formulier, parser, html, frame
    return None, None, "", None


def _probeer_tweede_klik(pagina, timeout: int) -> bool:
    """Klikt op een 'Doe mee'-knop op de bestemming; sommige sites tonen het
    formulier pas daarna. True als er iets aangeklikt is."""
    for selector in ("a", "button"):
        try:
            elementen = pagina.query_selector_all(selector)
        except Exception:
            continue
        for element in elementen[:60]:
            try:
                tekst = (element.inner_text() or "").strip()
            except Exception:
                continue
            if not tekst or len(tekst) > 40 or not TWEEDE_KLIK.search(tekst):
                continue
            try:
                element.click(timeout=5000)
                pagina.wait_for_timeout(3000)
                return True
            except Exception:
                continue
    return False


def _waarom_geen_formulier(pagina, html: str) -> str:
    """Korte diagnose voor in de log: wat stond er dan wél op die pagina?"""
    parser = FormulierParser()
    parser.feed(html)
    aantal = len(parser.formulieren)
    try:
        frames = len(pagina.frames) - 1
    except Exception:
        frames = 0
    knoppen = []
    try:
        for element in (pagina.query_selector_all("a, button") or [])[:80]:
            tekst = (element.inner_text() or "").strip()
            if tekst and len(tekst) <= 30 and TWEEDE_KLIK.search(tekst):
                knoppen.append(tekst)
    except Exception:
        pass
    delen = [f"{aantal} formulier(en)", f"{frames} iframe(s)"]
    if knoppen:
        delen.append("knoppen: " + ", ".join(dict.fromkeys(knoppen))[:60])
    if "inloggen" in html.lower() or "aanmelden" in html.lower():
        delen.append("pagina noemt inloggen")
    return " · ".join(delen)


def _vul_formulier(pagina, formulier, payload) -> None:
    """Zet de gevonden waarden in de echte velden van de pagina."""
    for naam, waarde in payload.items():
        veld = next((v for v in formulier["velden"] if v.get("name") == naam), None)
        if veld is None or veld["type"] == "hidden":
            continue
        kiezer = f'[name="{naam}"]'
        try:
            if veld["type"] == "checkbox":
                pagina.check(kiezer, timeout=5000)
            elif veld["type"] == "radio":
                pagina.check(f'{kiezer}[value="{waarde}"]', timeout=5000)
            elif veld["type"] == "select":
                pagina.select_option(kiezer, waarde, timeout=5000)
            else:
                pagina.fill(kiezer, waarde, timeout=5000)
        except Exception:
            # Eén onwillig veld mag de rest niet blokkeren; of het formulier
            # daardoor onvolledig is, blijkt uit het antwoord van de site.
            continue


def deelnemen_browser(item: dict, gegevens: dict, opties: dict) -> tuple[str, str, list[str]]:
    """Geeft (status, opmerking, schermafbeeldingen) terug."""
    dry_run = opties.get("dry_run", True)
    map_pad = Path(opties.get("schermafbeeldingen", "data/schermafbeeldingen"))
    map_pad.mkdir(parents=True, exist_ok=True)
    timeout = int(opties.get("timeout_seconden", 30)) * 1000
    sleutel = re.sub(r"[^a-z0-9]+", "-", item["url"].lower())[:60].strip("-")
    plaatjes: list[str] = []

    sync_playwright = _speler()
    with sync_playwright() as pw:
        starter = pw.chromium.launch(headless=bool(opties.get("headless", True)))
        context = starter.new_context(
            locale="nl-BE",
            user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"))
        pagina = context.new_page()
        try:
            try:
                pagina.goto(item["url"], wait_until="domcontentloaded", timeout=timeout)
                pagina.wait_for_timeout(2500)
            except Exception as fout:
                return "mislukt", f"pagina niet te openen: {type(fout).__name__}", plaatjes

            plaatje = map_pad / f"{sleutel}-1.png"
            try:
                pagina.screenshot(path=str(plaatje), full_page=False)
                plaatjes.append(plaatje.name)
            except Exception:
                pass

            html = pagina.content()
            if bevat_captcha(html):
                return "handmatig", "captcha op de pagina", plaatjes

            parser = FormulierParser()
            parser.feed(html)
            formulier = kies_formulier(parser.formulieren)
            bron_url = item["url"]
            doel_frame = pagina          # waar het formulier staat: pagina of iframe

            # Geen formulier: doorklikken naar de echte wedstrijd.
            if formulier is None:
                door = zoek_doorklik(pagina, item["url"], html)
                if not door:
                    return "handmatig", "geen formulier en geen doorklikknop gevonden", plaatjes
                try:
                    pagina.goto(door, wait_until="domcontentloaded", timeout=timeout)
                    pagina.wait_for_timeout(3000)
                except Exception as fout:
                    return "mislukt", f"doorklik {door} niet te openen: {type(fout).__name__}", plaatjes

                bron_url = door
                plaatje = map_pad / f"{sleutel}-2.png"
                try:
                    pagina.screenshot(path=str(plaatje), full_page=False)
                    plaatjes.append(plaatje.name)
                except Exception:
                    pass

                html = pagina.content()
                if bevat_captcha(html):
                    return "handmatig", f"captcha op {door.split('/')[2]}", plaatjes

                # Ook in iframes kijken: campagneformulieren staan er vaak in.
                formulier, parser, frame_html, doel_frame = _formulier_in_frames(pagina)
                if formulier is not None:
                    html = frame_html

                # Nog niets? Sommige sites tonen het formulier pas na een klik
                # op "Doe mee". Eén keer proberen, dan opnieuw kijken.
                if formulier is None and _probeer_tweede_klik(pagina, timeout):
                    plaatje = map_pad / f"{sleutel}-3.png"
                    try:
                        pagina.screenshot(path=str(plaatje), full_page=False)
                        plaatjes.append(plaatje.name)
                    except Exception:
                        pass
                    html = pagina.content()
                    if bevat_captcha(html):
                        return "handmatig", f"captcha na doorklik op {door.split('/')[2]}", plaatjes
                    formulier, parser, frame_html, doel_frame = _formulier_in_frames(pagina)
                    if formulier is not None:
                        html = frame_html

                if formulier is None:
                    return ("handmatig",
                            f"doorgeklikt naar {door.split('/')[2]}, geen deelnameformulier "
                            f"({_waarom_geen_formulier(pagina, html)})",
                            plaatjes)

            if any(v["type"] == "password" for v in formulier["velden"]):
                return "handmatig", "het formulier vraagt een account (wachtwoordveld)", plaatjes

            payload, onbekend, uitleg = bouw_payload(
                formulier, parser.labels, gegevens, None,
                {"pagina": strip_html(html),
                 "context": f"{item.get('titel','')} {item.get('samenvatting','')}"})
            extra = (" · " + " · ".join(uitleg)) if uitleg else ""

            if onbekend:
                return "handmatig", "niet begrepen: " + "; ".join(onbekend[:4]) + extra, plaatjes
            if not any(re.search(r"e.?mail", naam, re.I) for naam in payload):
                return "handmatig", "geen e-mailveld herkend", plaatjes

            _vul_formulier(doel_frame or pagina, formulier, payload)
            plaatje = map_pad / f"{sleutel}-ingevuld.png"
            try:
                pagina.screenshot(path=str(plaatje), full_page=False)
                plaatjes.append(plaatje.name)
            except Exception:
                pass

            if dry_run:
                return ("proefdraai",
                        f"ingevuld op {bron_url.split('/')[2]} ({len(payload)} velden), "
                        f"niet verstuurd{extra}", plaatjes)

            try:
                (doel_frame or pagina).click(
                    'button[type="submit"], input[type="submit"]', timeout=8000)
                pagina.wait_for_timeout(4000)
            except Exception:
                return "handmatig", "geen verzendknop gevonden" + extra, plaatjes

            plaatje = map_pad / f"{sleutel}-na.png"
            try:
                pagina.screenshot(path=str(plaatje), full_page=False)
                plaatjes.append(plaatje.name)
            except Exception:
                pass

            if gelukt(pagina.content(), None):
                return "gedaan", f"verstuurd op {bron_url.split('/')[2]}{extra}", plaatjes
            return ("handmatig",
                    "verstuurd, maar geen bevestiging herkend — kijk de schermafbeelding na" + extra,
                    plaatjes)
        finally:
            context.close()
            starter.close()


def doe_mee_met_browser(items: list[dict], config: dict, opslag, log=print) -> list[dict]:
    """Zelfde rol als deelnemen.doe_mee, maar met een echte browser."""
    instellingen = config.get("deelname", {})
    dry_run = bool(instellingen.get("dry_run", True))
    maximum = int(instellingen.get("max_per_nacht", 8))
    max_pogingen = int(instellingen.get("max_pogingen", 3))
    gegevens = waarden(config.get("deelnemer", {}))

    opties = {
        "dry_run": dry_run,
        "headless": instellingen.get("headless", True),
        "timeout_seconden": instellingen.get("timeout_seconden", 30),
        "schermafbeeldingen": Path(__file__).parent / "data" / "schermafbeeldingen",
    }

    resultaten: list[dict] = []
    gedaan = 0
    for item in items:
        if gedaan >= maximum:
            break
        if opslag.al_gedaan(item["url"]) or opslag.pogingen(item["url"]) >= max_pogingen:
            continue

        try:
            status, opmerking, plaatjes = deelnemen_browser(item, gegevens, opties)
        except GeenBrowser as fout:
            log(f"  ! {fout}")
            return resultaten
        except Exception as fout:                      # browser kan altijd stukgaan
            status, opmerking, plaatjes = "mislukt", f"{type(fout).__name__}: {fout}", []

        gedaan += 1
        log(f"  [{status}] {item['titel'][:70]} — {opmerking}")
        opslag.tel_poging(item["url"])
        opslag.zet_status(item["url"], status, opmerking)
        opslag.noteer(item, status, opmerking)
        resultaten.append({**item, "status": status, "opmerking": opmerking,
                           "schermafbeeldingen": plaatjes})

    return resultaten
