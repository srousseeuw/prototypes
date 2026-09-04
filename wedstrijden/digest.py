#!/usr/bin/env python3
"""
Digest: één pagina met wat het script vannacht gedaan heeft.

Schrijft altijd een HTML-bestand (config.digest.bestand). Mailen naar jezelf is
optioneel en staat standaard uit; het wachtwoord komt uit een omgevingsvariabele,
nooit uit config.json.

De volgorde is bewust: eerst wat jij nog moet doen, dan wat het script zelf deed.
"""
from __future__ import annotations

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from html import escape
from pathlib import Path

STATUS_LABELS = {
    "gedaan": ("Deelgenomen", "#1a7f37"),
    "proefdraai": ("Proefdraai (niets verstuurd)", "#8a6d00"),
    "handmatig": ("Zelf doen", "#0b62c4"),
    "mislukt": ("Mislukt", "#b42318"),
    "overgeslagen": ("Overgeslagen", "#6b7280"),
}

CSS = """
:root{color-scheme:light dark}
body{margin:0;padding:28px 20px;background:#f6f7f9;color:#111827;
     font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:760px;margin:0 auto}
h1{font-size:22px;margin:0 0 4px}
.sub{color:#6b7280;font-size:14px;margin:0 0 28px}
h2{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:#6b7280;
   margin:32px 0 12px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}
.kaart{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:14px 16px;margin-bottom:10px}
.kaart a{color:#111827;text-decoration:none;font-weight:600}
.kaart a:hover{text-decoration:underline}
.meta{font-size:13px;color:#6b7280;margin-top:6px}
.badge{display:inline-block;font-size:12px;font-weight:600;padding:2px 8px;border-radius:999px;
       background:#eef2f7;margin-right:6px}
.score{float:right;font-size:13px;color:#6b7280}
.leeg{color:#6b7280;font-style:italic}
.fout{background:#fff5f5;border-color:#fecdca}
@media (prefers-color-scheme:dark){
  body{background:#0f1115;color:#e5e7eb}
  .kaart{background:#171a21;border-color:#262b36}
  .kaart a{color:#e5e7eb}
  .badge{background:#232833;color:#cbd5e1}
  .fout{background:#241618;border-color:#5b2326}
}
"""


def _kaart(item: dict) -> str:
    label, kleur = STATUS_LABELS.get(item.get("status", ""), ("", "#6b7280"))
    badge = f'<span class="badge" style="color:{kleur}">{escape(label)}</span>' if label else ""
    categorieen = " ".join(f'<span class="badge">{escape(c)}</span>' for c in item.get("categorieen", []))
    opmerking = escape(item.get("opmerking", ""))
    return f"""    <div class="kaart">
      <span class="score">score {item.get('score', 0)}</span>
      <a href="{escape(item.get('url',''))}">{escape(item.get('titel','(zonder titel)'))}</a>
      <div class="meta">{badge}{categorieen}
        {escape(item.get('bron',''))}{' · ' + opmerking if opmerking else ''}</div>
    </div>"""


def _sectie(titel: str, items: list[dict], leeg: str) -> str:
    if not items:
        return f"<h2>{escape(titel)}</h2>\n    <p class=\"leeg\">{escape(leeg)}</p>"
    return f"<h2>{escape(titel)} ({len(items)})</h2>\n" + "\n".join(_kaart(i) for i in items)


def bouw_html(resultaten: list[dict], bevestigd: list[dict], fouten: list[str],
              stats: dict) -> str:
    per_status: dict[str, list[dict]] = {}
    for item in resultaten:
        per_status.setdefault(item.get("status", "overgeslagen"), []).append(item)

    stukken = [
        _sectie("Zelf afwerken", per_status.get("handmatig", []),
                "Niets dat jouw handen nodig heeft."),
        _sectie("Deelgenomen", per_status.get("gedaan", []), "Vannacht geen deelnames."),
        _sectie("Proefdraai", per_status.get("proefdraai", []),
                "Geen proefdraai (dry_run staat uit)."),
        _sectie("Mislukt", per_status.get("mislukt", []), "Niets mislukt."),
    ]

    if bevestigd:
        regels = "\n".join(
            f'    <div class="kaart"><a href="{escape(b["url"])}">{escape(b["onderwerp"])}</a>'
            f'<div class="meta">{escape(b["afzender"])}</div></div>' for b in bevestigd)
        stukken.append(f"<h2>Bevestigingsmails geopend ({len(bevestigd)})</h2>\n{regels}")

    if fouten:
        regels = "\n".join(f'    <div class="kaart fout">{escape(f)}</div>' for f in fouten)
        stukken.append(f"<h2>Bronnen met problemen ({len(fouten)})</h2>\n{regels}")

    samenvatting = (f"{stats.get('opgehaald', 0)} gevonden · {stats.get('nieuw', 0)} nieuw · "
                    f"{stats.get('gekozen', 0)} geselecteerd · {len(resultaten)} behandeld")

    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Wedstrijden — {datetime.now().strftime('%d/%m/%Y')}</title>
<style>{CSS}</style>
</head>
<body>
  <div class="wrap">
    <h1>Wedstrijden van {datetime.now().strftime('%d/%m/%Y')}</h1>
    <p class="sub">{escape(samenvatting)}</p>
    {"".join(stukken)}
  </div>
</body>
</html>
"""


def schrijf(html: str, pad: Path) -> Path:
    pad = Path(pad)
    pad.parent.mkdir(parents=True, exist_ok=True)
    pad.write_text(html, encoding="utf-8")
    return pad


def mail(html: str, config: dict, log=print) -> bool:
    """Stuurt de digest naar jezelf. Standaard uit — zie config.digest.mailen."""
    instellingen = config.get("digest", {})
    if not instellingen.get("mailen"):
        return False
    wachtwoord = os.environ.get(instellingen.get("smtp_wachtwoord_env", "GMAIL_APP_WACHTWOORD"), "")
    if not wachtwoord:
        log(f"  ! geen wachtwoord in ${instellingen.get('smtp_wachtwoord_env')} — digest niet gemaild")
        return False

    bericht = EmailMessage()
    bericht["Subject"] = f"Wedstrijden {datetime.now().strftime('%d/%m')}"
    bericht["From"] = instellingen["smtp_gebruiker"]
    bericht["To"] = instellingen.get("naar", instellingen["smtp_gebruiker"])
    bericht.set_content("Deze samenvatting is in HTML opgemaakt.")
    bericht.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(instellingen.get("smtp_server", "smtp.gmail.com"),
                          int(instellingen.get("smtp_poort", 587)), timeout=30) as server:
            server.starttls()
            server.login(instellingen["smtp_gebruiker"], wachtwoord)
            server.send_message(bericht)
    except Exception as fout:
        log(f"  ! digest mailen mislukt: {fout}")
        return False
    log(f"  ✓ digest gemaild naar {bericht['To']}")
    return True
