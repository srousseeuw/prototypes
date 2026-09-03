#!/usr/bin/env python3
"""
Bedieningspaneel in je browser.

    python3 wedstrijden/serve.py
    → open http://localhost:8900

Vier knoppen: zoeken, diagnose, proefdraai en echt deelnemen. Je ziet de log
live meelopen, met daaronder het logboek van alles waar je ooit aan deelnam en
de schermafbeeldingen die de browser onderweg maakte.

Draait alleen op je eigen machine (localhost) — niets hiervan staat op het
internet, en er zit bewust geen wachtwoord op omdat er ook niets van buiten bij
kan.
"""
import json
import sys
import threading
import traceback
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

HIER = Path(__file__).parent
sys.path.insert(0, str(HIER))

import browser as browser_mod        # noqa: E402
import bronnen as bronnen_mod        # noqa: E402
import deelnemen as deelnemen_mod    # noqa: E402
import selectie as selectie_mod      # noqa: E402
from opslag import Opslag            # noqa: E402
from wedstrijden import laad_config  # noqa: E402

POORT = 8900
SCHERMEN = HIER / "data" / "schermafbeeldingen"

TAKEN = {
    "zoek":      "Alleen zoeken (verstuurt niets)",
    "diagnose":  "Diagnose met browser (verstuurt niets)",
    "proef":     "Proefdraai (vult in, verstuurt niet)",
    "echt":      "Echt deelnemen",
}


class Loop:
    """Houdt de log en de status van de lopende taak bij."""

    def __init__(self):
        self.regels: list[str] = []
        self.bezig = False
        self.taak = ""
        self.slot = threading.Lock()

    def schrijf(self, regel: str = ""):
        with self.slot:
            self.regels.append(str(regel))

    def start(self, taak: str, doel):
        if self.bezig:
            return False
        self.bezig, self.taak = True, taak
        with self.slot:
            self.regels = [f"── {TAKEN.get(taak, taak)} · {datetime.now():%H:%M:%S} ──"]

        def draai():
            try:
                doel()
            except Exception:
                self.schrijf("FOUT:")
                for regel in traceback.format_exc().splitlines()[-8:]:
                    self.schrijf("  " + regel)
            finally:
                self.schrijf(f"── klaar · {datetime.now():%H:%M:%S} ──")
                self.bezig = False

        threading.Thread(target=draai, daemon=True).start()
        return True


loop = Loop()


# --------------------------------------------------------------------------- taken

def _config_en_opslag():
    config = laad_config(HIER / "config.json")
    return config, Opslag(HIER / "data")


def _verzamel(config, opslag):
    rauw, fouten = bronnen_mod.verzamel(config, log=loop.schrijf)
    loop.schrijf(f"  {len(rauw)} items opgehaald")
    keuzes = selectie_mod.kies(rauw, config.get("selectie", {}))
    nieuw = [i for i in keuzes if not opslag.is_bekend(i["url"])]
    for item in nieuw:
        opslag.onthoud(item, "nieuw")
    opslag.bewaar()
    loop.schrijf(f"  {len(keuzes)} passen bij het gezin, waarvan {len(nieuw)} nieuw")
    return keuzes, fouten


def taak_zoek():
    config, opslag = _config_en_opslag()
    keuzes, _ = _verzamel(config, opslag)
    loop.schrijf("")
    for item in keuzes[:25]:
        loop.schrijf(f"  {item['score']:>3}  {item['titel'][:75]}")
        loop.schrijf(f"       {item['url']}")


def _te_doen(opslag, keuzes):
    return [i for i in keuzes if not opslag.al_gedaan(i["url"])]


def taak_browser(dry_run: bool, alleen_diagnose: bool = False):
    config, opslag = _config_en_opslag()
    config.setdefault("deelname", {})["dry_run"] = dry_run
    if alleen_diagnose:
        config["deelname"]["max_per_nacht"] = min(
            6, int(config["deelname"].get("max_per_nacht", 6)))

    keuzes, _ = _verzamel(config, opslag)
    te_doen = _te_doen(opslag, keuzes)
    if not te_doen:
        loop.schrijf("  niets te doen — alles is al eens geprobeerd")
        return

    loop.schrijf("")
    loop.schrijf(f"  browser start ({'proefdraai' if dry_run else 'ECHT VERSTUREN'})…")
    browser_mod.doe_mee_met_browser(te_doen, config, opslag, log=loop.schrijf)
    opslag.bewaar()


STARTERS = {
    "zoek": taak_zoek,
    "diagnose": lambda: taak_browser(True, alleen_diagnose=True),
    "proef": lambda: taak_browser(True),
    "echt": lambda: taak_browser(False),
}


# --------------------------------------------------------------------------- pagina

CSS = """
:root{color-scheme:light dark}
body{margin:0;padding:24px;background:#f6f7f9;color:#111827;
     font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:900px;margin:0 auto}
h1{font-size:21px;margin:0 0 4px}
.sub{color:#6b7280;font-size:14px;margin:0 0 20px}
.knoppen{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
button{font:600 14px system-ui;padding:9px 14px;border-radius:8px;border:1px solid #cbd5e1;
       background:#fff;color:#111827;cursor:pointer}
button:hover{border-color:#94a3b8}
button.echt{background:#b42318;border-color:#b42318;color:#fff}
button:disabled{opacity:.45;cursor:not-allowed}
pre{background:#0f1115;color:#e5e7eb;padding:14px;border-radius:10px;overflow:auto;
    max-height:52vh;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap}
h2{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:#6b7280;
   margin:28px 0 10px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}
table{width:100%;border-collapse:collapse;font-size:14px}
td{padding:7px 6px;border-bottom:1px solid #e5e7eb;vertical-align:top}
td a{color:#111827;font-weight:600;text-decoration:none}
.dag{color:#6b7280;white-space:nowrap;width:70px}
.st{white-space:nowrap;font-weight:600}
.gedaan{color:#1a7f37}.handmatig{color:#0b62c4}.mislukt{color:#b42318}.proefdraai{color:#8a6d00}
.schermen{display:flex;gap:10px;flex-wrap:wrap}
.schermen a{display:block;width:180px;font-size:12px;color:#6b7280;text-decoration:none}
.schermen img{width:180px;border:1px solid #e5e7eb;border-radius:6px;display:block}
@media (prefers-color-scheme:dark){
  body{background:#0f1115;color:#e5e7eb}
  button{background:#171a21;border-color:#262b36;color:#e5e7eb}
  td{border-color:#262b36} td a{color:#e5e7eb}
  .schermen img{border-color:#262b36}}
"""

SCRIPT = """
async function start(taak){
  document.querySelectorAll('button').forEach(b => b.disabled = true);
  await fetch('/start?taak=' + taak, {method:'POST'});
  volg();
}
async function volg(){
  const r = await fetch('/log');
  const d = await r.json();
  document.getElementById('log').textContent = d.regels.join('\\n');
  document.getElementById('log').scrollTop = 1e6;
  document.querySelectorAll('button').forEach(b => b.disabled = d.bezig);
  if (d.bezig) setTimeout(volg, 1000);
  else if (d.regels.length > 1) setTimeout(() => location.reload(), 1200);
}
volg();
"""


def _logboek_html() -> str:
    opslag = Opslag(HIER / "data")
    regels = opslag.recent(60)
    if not regels:
        return '<p class="sub">Nog niets geprobeerd.</p>'
    rijen = []
    for regel in regels:
        status = escape(regel.get("status", ""))
        rijen.append(
            f'<tr><td class="dag">{escape(regel.get("tijd", "")[:16])}</td>'
            f'<td><a href="{escape(regel.get("url", ""))}">{escape(regel.get("titel", ""))}</a>'
            f'<br><span class="sub">{escape(regel.get("opmerking", ""))[:120]}</span></td>'
            f'<td class="st {status}">{status}</td></tr>')
    return f"<table>{''.join(rijen)}</table>"


def _schermen_html() -> str:
    if not SCHERMEN.exists():
        return '<p class="sub">Nog geen schermafbeeldingen.</p>'
    plaatjes = sorted(SCHERMEN.glob("*.png"), key=lambda p: -p.stat().st_mtime)[:12]
    if not plaatjes:
        return '<p class="sub">Nog geen schermafbeeldingen.</p>'
    return '<div class="schermen">' + "".join(
        f'<a href="/scherm/{escape(p.name)}" target="_blank">'
        f'<img src="/scherm/{escape(p.name)}" loading="lazy">{escape(p.name[:40])}</a>'
        for p in plaatjes) + "</div>"


def pagina_html() -> str:
    knoppen = "".join(
        f'<button class="{"echt" if taak == "echt" else ""}" '
        f'onclick="start(\'{taak}\')">{escape(tekst)}</button>'
        for taak, tekst in TAKEN.items())
    return f"""<!doctype html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wedstrijdbot</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Wedstrijdbot</h1>
<p class="sub">Draait op deze Mac. "Echt deelnemen" verstuurt met je echte naam en adres.</p>
<div class="knoppen">{knoppen}</div>
<pre id="log">…</pre>
<h2>Waar je aan deelnam</h2>
{_logboek_html()}
<h2>Wat de browser zag</h2>
{_schermen_html()}
</div><script>{SCRIPT}</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _stuur(self, inhoud: bytes, soort="text/html; charset=utf-8", code=200):
        self.send_response(code)
        self.send_header("Content-Type", soort)
        self.send_header("Content-Length", str(len(inhoud)))
        self.end_headers()
        self.wfile.write(inhoud)

    def do_GET(self):
        pad = urlsplit(self.path).path
        if pad == "/":
            self._stuur(pagina_html().encode("utf-8"))
        elif pad == "/log":
            with loop.slot:
                data = {"regels": list(loop.regels), "bezig": loop.bezig}
            self._stuur(json.dumps(data).encode("utf-8"), "application/json")
        elif pad.startswith("/scherm/"):
            plaatje = SCHERMEN / Path(pad).name
            if plaatje.exists() and plaatje.parent == SCHERMEN:
                self._stuur(plaatje.read_bytes(), "image/png")
            else:
                self._stuur(b"niet gevonden", "text/plain", 404)
        else:
            self._stuur(b"niet gevonden", "text/plain", 404)

    def do_POST(self):
        taak = parse_qs(urlsplit(self.path).query).get("taak", [""])[0]
        starter = STARTERS.get(taak)
        if starter is None:
            self._stuur(b'{"ok":false}', "application/json", 400)
            return
        loop.start(taak, starter)
        self._stuur(b'{"ok":true}', "application/json")

    def log_message(self, *args):
        pass          # de server hoeft niet mee te praten in je terminal


def main():
    if not (HIER / "config.json").exists():
        print("Geen config.json — draai eerst ./wedstrijden/installeer.sh")
        return 1
    print(f"Wedstrijdbot draait op http://localhost:{POORT}")
    print("Stoppen: Ctrl-C")
    try:
        HTTPServer(("127.0.0.1", POORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nGestopt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
