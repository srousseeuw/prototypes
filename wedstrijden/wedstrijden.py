#!/usr/bin/env python3
"""
Wedstrijdbot — zoekt 's nachts gratis wedstrijden die nuttig zijn voor het gezin.

  python3 wedstrijden/wedstrijden.py nacht           # alles: zoeken, deelnemen, bevestigen, digest
  python3 wedstrijden/wedstrijden.py zoek            # enkel zoeken en tonen, niets versturen
  python3 wedstrijden/wedstrijden.py zoek --alles    # ook wat de filter afwees (om te ijken)
  python3 wedstrijden/wedstrijden.py deelnemen       # deelnemen aan wat al gevonden is
  python3 wedstrijden/wedstrijden.py bevestig        # bevestigingsmails aanklikken
  python3 wedstrijden/wedstrijden.py digest          # digest opnieuw opbouwen uit de log
  python3 wedstrijden/wedstrijden.py bronnen-check   # welke bronnen doen het nog?

Standaard staat dry_run aan: er wordt niets echt verstuurd. Zet dat pas af in
config.json als je de proefdraai-uitvoer hebt nagekeken (--echt forceert het
voor één keer, --proef zet het net weer aan).
"""
import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).parent
sys.path.insert(0, str(HIER))

import bevestig as bevestig_mod          # noqa: E402
import bronnen as bronnen_mod            # noqa: E402
import deelnemen as deelnemen_mod        # noqa: E402
import digest as digest_mod              # noqa: E402
import selectie as selectie_mod          # noqa: E402
from opslag import Opslag                # noqa: E402


def laad_config(pad: Path) -> dict:
    if not pad.exists():
        voorbeeld = HIER / "config.example.json"
        print(f"Geen {pad.name} gevonden.\nKopieer eerst het voorbeeld:\n"
              f"  cp {voorbeeld} {pad}\nen vul je gegevens aan.")
        sys.exit(1)
    config = json.loads(pad.read_text(encoding="utf-8"))
    # De woordenlijsten staan apart, want de Cloudflare Worker leest dezelfde.
    # Wie lokaal wil afwijken, zet een eigen "selectie"-blok in config.json.
    if "selectie" not in config:
        config["selectie"] = json.loads((HIER / "selectie.json").read_text(encoding="utf-8"))
    return config


def _zoek(config: dict, opslag: Opslag, toon_alles: bool = False):
    """Haalt alle bronnen op. Geeft (nieuw, gekozen, fouten, aantal_opgehaald)."""
    print("Bronnen ophalen…")
    rauw, fouten = bronnen_mod.verzamel(config)
    print(f"  {len(rauw)} items opgehaald")

    gekozen = selectie_mod.kies(rauw, config.get("selectie", {}))
    nieuw = [item for item in gekozen if not opslag.is_bekend(item["url"])]
    for item in nieuw:
        opslag.onthoud(item, "nieuw")

    print(f"  {len(gekozen)} passen bij het gezin, waarvan {len(nieuw)} nieuw")

    if toon_alles:
        beoordeeld = [selectie_mod.beoordeel(i, config.get("selectie", {})) for i in rauw]
        beoordeeld.sort(key=lambda i: -i["score"])
        print("\nAlle items met score (om de filter te ijken):")
        for item in beoordeeld[:60]:
            merk = "×" if item["uitgesloten"] else " "
            print(f"  {merk} {item['score']:>3}  {item['titel'][:80]}")
            if item["redenen"]:
                print(f"        {' | '.join(item['redenen'][:3])}")

    return nieuw, gekozen, fouten, len(rauw)


def _te_doen(opslag: Opslag, keuzes: list[dict]) -> list[dict]:
    """Wat nog een poging verdient: nieuw gevonden plus eerder blijven steken."""
    te_doen = [item for item in keuzes if not opslag.al_gedaan(item["url"])]
    bekend = {item["url"].rstrip("/").lower() for item in te_doen}
    for sleutel, vermelding in opslag.gezien.items():
        if vermelding.get("status") == "nieuw" and sleutel not in bekend and vermelding.get("url"):
            te_doen.append({"titel": vermelding.get("titel", ""), "url": vermelding["url"],
                            "bron": vermelding.get("bron", ""), "score": vermelding.get("score", 0),
                            "categorieen": vermelding.get("categorieen", []), "samenvatting": ""})
    te_doen.sort(key=lambda i: -i.get("score", 0))
    return te_doen


def opdracht_zoek(config, opslag, args):
    nieuw, _, _, _ = _zoek(config, opslag, args.alles)
    opslag.bewaar()
    if nieuw:
        print("\nNieuw gevonden:")
        for item in nieuw:
            print(f"  {item['score']:>3}  {item['titel'][:80]}\n       {item['url']}")
    return 0


def opdracht_deelnemen(config, opslag, args, keuzes=None, fouten=None):
    keuzes = keuzes if keuzes is not None else _zoek(config, opslag)[1]
    te_doen = _te_doen(opslag, keuzes)
    if not te_doen:
        print("Niets om aan deel te nemen.")
        return []
    modus = "PROEFDRAAI" if config["deelname"].get("dry_run", True) else "ECHT VERSTUREN"
    met_browser = bool(config["deelname"].get("browser", False))
    print(f"\nDeelnemen ({modus}{' · browser' if met_browser else ''}, "
          f"max {config['deelname'].get('max_per_nacht', 8)}):")

    # Met browser: de enige manier om voorbij de JavaScript-doorklik van de
    # overzichtssites te raken. Zonder: de snelle HTTP-modus.
    if met_browser:
        import browser as browser_mod
        try:
            resultaten = browser_mod.doe_mee_met_browser(te_doen, config, opslag)
        except browser_mod.GeenBrowser as fout:
            print(f"  ! {fout}")
            resultaten = []
    else:
        resultaten = deelnemen_mod.doe_mee(te_doen, config, opslag)
    opslag.bewaar()
    return resultaten


def opdracht_bevestig(config, opslag, args):
    print("Bevestigingsmails nakijken…")
    bevestigd = bevestig_mod.bevestig(config, opslag)
    opslag.bewaar()
    return bevestigd


def opdracht_digest(config, opslag, args, resultaten=None, bevestigd=None, fouten=None, stats=None):
    resultaten = resultaten if resultaten is not None else opslag.recent(60)
    html = digest_mod.bouw_html(resultaten, bevestigd or [], fouten or [], stats or {})
    pad = digest_mod.schrijf(html, HIER / config["digest"].get("bestand", "data/digest.html"))
    print(f"\n✓ Digest: {pad}")
    digest_mod.mail(html, config)
    return pad


def opdracht_bronnen_check(config, opslag, args):
    print("Bronnen testen (geen deelnames):\n")
    stuk = 0
    for bron in config.get("bronnen", []):
        naam = bron.get("naam", bron["url"])
        if not bron.get("actief", True):
            print(f"  – {naam}: uitgeschakeld")
            continue
        try:
            items, methode = bronnen_mod.haal_bron(bron)
        except bronnen_mod.BronFout as fout:
            print(f"  ✗ {naam}: {fout}")
            stuk += 1
            continue
        voorbeeld = items[0]["titel"][:60] if items else "(geen items herkend)"
        vlag = "✓" if items else "!"
        if not items:
            stuk += 1
        print(f"  {vlag} {naam}: {len(items)} items via {methode}\n      bv. {voorbeeld}")
    if stuk:
        print(f"\n{stuk} bron(nen) leveren niets op — pas de URL aan of zet 'actief': false.")
    return 0


def opdracht_nacht(config, opslag, args):
    nieuw, keuzes, fouten, opgehaald = _zoek(config, opslag)
    resultaten = opdracht_deelnemen(config, opslag, args, keuzes=keuzes)
    bevestigd = opdracht_bevestig(config, opslag, args)
    stats = {"opgehaald": opgehaald, "nieuw": len(nieuw), "gekozen": len(keuzes)}
    opdracht_digest(config, opslag, args, resultaten=resultaten, bevestigd=bevestigd,
                    fouten=fouten, stats=stats)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Wedstrijdbot voor het gezin")
    parser.add_argument("opdracht", choices=["nacht", "zoek", "deelnemen", "bevestig",
                                             "digest", "bronnen-check"])
    parser.add_argument("--config", default=str(HIER / "config.json"))
    parser.add_argument("--alles", action="store_true", help="bij 'zoek': ook afgewezen items tonen")
    parser.add_argument("--echt", action="store_true", help="dry_run uitzetten voor deze run")
    parser.add_argument("--proef", action="store_true", help="dry_run aanzetten voor deze run")
    args = parser.parse_args()

    config = laad_config(Path(args.config))
    config.setdefault("deelname", {})
    if args.echt and args.proef:
        print("Kies --echt of --proef, niet allebei.")
        return 1
    if args.echt:
        config["deelname"]["dry_run"] = False
    if args.proef:
        config["deelname"]["dry_run"] = True

    opslag = Opslag(HIER / "data")

    opdrachten = {
        "nacht": opdracht_nacht,
        "zoek": opdracht_zoek,
        "deelnemen": opdracht_deelnemen,
        "bevestig": opdracht_bevestig,
        "digest": opdracht_digest,
        "bronnen-check": opdracht_bronnen_check,
    }
    opdrachten[args.opdracht](config, opslag, args)
    opslag.bewaar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
