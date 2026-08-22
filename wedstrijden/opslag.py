#!/usr/bin/env python3
"""
Opslag: onthouden wat we al gezien hebben en waaraan we al deelnamen.

Twee JSON-bestanden in data/ (niet in git — ze bevatten deelnamegegevens):
  gezien.json    → url → {eerst_gezien, titel, score, status}
  deelnames.json → chronologische log van elke poging

Zonder dit zou het script elke nacht opnieuw aan dezelfde wedstrijd deelnemen.
Dat is meteen ook de belangrijkste regel van de meeste wedstrijdreglementen:
één deelname per persoon.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

STATUSSEN = ("nieuw", "gedaan", "handmatig", "mislukt", "overgeslagen", "proefdraai")


def _nu() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def sleutel(url: str) -> str:
    return url.split("#")[0].rstrip("/").lower()


class Opslag:
    def __init__(self, map_pad: Path):
        self.map = Path(map_pad)
        self.map.mkdir(parents=True, exist_ok=True)
        self.gezien_pad = self.map / "gezien.json"
        self.log_pad = self.map / "deelnames.json"
        self.gezien = self._laad(self.gezien_pad, {})
        self.log = self._laad(self.log_pad, [])

    @staticmethod
    def _laad(pad: Path, standaard):
        if not pad.exists():
            return standaard
        try:
            return json.loads(pad.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return standaard

    def bewaar(self) -> None:
        self.gezien_pad.write_text(json.dumps(self.gezien, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log_pad.write_text(json.dumps(self.log[-2000:], ensure_ascii=False, indent=2), encoding="utf-8")

    # -- gezien ------------------------------------------------------------

    def is_bekend(self, url: str) -> bool:
        return sleutel(url) in self.gezien

    def status(self, url: str) -> str:
        return self.gezien.get(sleutel(url), {}).get("status", "nieuw")

    def al_gedaan(self, url: str) -> bool:
        """Deelname geslaagd of bewust overgeslagen: niet nog eens proberen."""
        return self.status(url) in ("gedaan", "overgeslagen")

    def onthoud(self, item: dict, status: str = "nieuw") -> None:
        sl = sleutel(item["url"])
        bestaand = self.gezien.get(sl, {})
        self.gezien[sl] = {
            "titel": item.get("titel", bestaand.get("titel", "")),
            "url": item["url"],
            "bron": item.get("bron", bestaand.get("bron", "")),
            "score": item.get("score", bestaand.get("score", 0)),
            "categorieen": item.get("categorieen", bestaand.get("categorieen", [])),
            "eerst_gezien": bestaand.get("eerst_gezien", _nu()),
            "laatst_gezien": _nu(),
            "status": status,
        }

    def zet_status(self, url: str, status: str, opmerking: str = "") -> None:
        sl = sleutel(url)
        vermelding = self.gezien.setdefault(sl, {"url": url, "eerst_gezien": _nu()})
        vermelding["status"] = status
        vermelding["laatst_gezien"] = _nu()
        if opmerking:
            vermelding["opmerking"] = opmerking

    def pogingen(self, url: str) -> int:
        return int(self.gezien.get(sleutel(url), {}).get("pogingen", 0))

    def tel_poging(self, url: str) -> int:
        """Een wedstrijd die blijft haperen mag niet elke nacht opnieuw geprobeerd worden."""
        sl = sleutel(url)
        vermelding = self.gezien.setdefault(sl, {"url": url, "eerst_gezien": _nu()})
        vermelding["pogingen"] = int(vermelding.get("pogingen", 0)) + 1
        return vermelding["pogingen"]

    # -- log ---------------------------------------------------------------

    def noteer(self, item: dict, status: str, opmerking: str = "") -> None:
        self.log.append({
            "tijd": _nu(),
            "titel": item.get("titel", ""),
            "url": item.get("url", ""),
            "bron": item.get("bron", ""),
            "score": item.get("score", 0),
            "status": status,
            "opmerking": opmerking,
        })

    def recent(self, aantal: int = 50) -> list[dict]:
        return list(reversed(self.log[-aantal:]))

    def wachtend_op_bevestiging(self, uren: int) -> list[dict]:
        """Deelnames van de laatste N uur — daar horen de bevestigingsmails bij."""
        grens = datetime.now(timezone.utc).timestamp() - uren * 3600
        wachtend = []
        for regel in self.log:
            if regel.get("status") != "gedaan":
                continue
            try:
                tijd = datetime.strptime(regel["tijd"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            except (KeyError, ValueError):
                continue
            if tijd.timestamp() >= grens:
                wachtend.append(regel)
        return wachtend
