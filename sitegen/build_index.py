#!/usr/bin/env python3
"""
Bouwt de overzichtspagina sites/index.html uit alle briefs in sitegen/briefs/.
Gebruik: python3 sitegen/build_index.py

Draai dit na elk nieuw of verwijderd prototype — dan kan het overzicht nooit
uit sync lopen met de briefs. Bewerk sites/index.html niet met de hand.

OUTREACH BIJHOUDEN
Zet in de brief van een bedrijf een "outreach" veld; het overzicht toont dan
de status en laat erop filteren. Zonder dat veld staat een prototype op
"nog niet benaderd".

  "outreach": {
    "status": "gecontacteerd",      # zie STATUSSEN hieronder
    "date": "2026-08-13",           # optioneel, dag van de mail
    "note": "via contactformulier"  # optioneel, kort
  }
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent

# Leesbare sectorlabels; onbekende sectoren vallen terug op de sectornaam zelf.
SECTOR_LABELS = {
    "accountant": "Accountancy & fiscaliteit",
    "bakery": "Bakkerij",
    "bloemist": "Bloemen",
    "broodboetiek": "Bakkerij",
    "brouwerij": "Brouwerij",
    "cafe": "Café",
    "dierenarts": "Dierenzorg",
    "fietsenwinkel": "Fietsen",
    "frituur": "Frituur",
    "garage": "Garage",
    "hoevewinkel": "Hoeve & streekproducten",
    "hondentrimsalon": "Trimsalon",
    "hovenier": "Tuinaanleg",
    "juwelier": "Juwelier",
    "kapper": "Kapsalon",
    "keukenstudio": "Interieur & keukens",
    "kinderopvang": "Kinderopvang",
    "kringloopwinkel": "Kringloop",
    "opticien": "Optiek",
    "pedicure": "Pedicure & voetverzorging",
    "pizzeria": "Pizzeria & Italiaans",
    "app": "App",
    "boekhouding": "Boekhouding",
    "metaal": "Metaal & bouw",
    "schrijnwerk": "Schrijnwerk",
    "sportdirectory": "Sport & directory",
    "sushi": "Sushi & Aziatisch",
    "verhuur": "Verhuur",
    "vrijetijd": "Vrije tijd & opvang",
    "zorg": "Zorg & welzijn",
    "politiek": "Politiek",
    "schilder": "Schilderwerken",
    "restaurant": "Restaurant",
    "slager": "Slagerij",
    "sportclub": "Sport & vereniging",
    "tuincentrum": "Tuincentrum",
    "veehouderij": "Veeteelt",
}

# Volgorde bepaalt ook de volgorde van de filterknoppen.
STATUSSEN = [
    ("nieuw", "Nog niet benaderd", "#6b7280"),
    ("gepland", "Klaar om te mailen", "#b45309"),
    ("gecontacteerd", "Gecontacteerd", "#2f5fd0"),
    ("gereageerd", "Heeft gereageerd", "#7c3aed"),
    ("klant", "Klant", "#15803d"),
    ("geen-vervolg", "Geen vervolg", "#8a8f98"),
]
STATUS_LABEL = {k: label for k, label, _ in STATUSSEN}
STATUS_KLEUR = {k: kleur for k, _, kleur in STATUSSEN}

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

TELEFOON_LABEL = "Enkel telefonisch"
TELEFOON_KLEUR = "#0f766e"

def enkel_telefonisch(brief):
    """Kanaal, los van de funnelstatus: is mailen hier geen optie?"""
    return bool((brief.get("outreach") or {}).get("only_phone"))

def outreach_of(brief):
    """Geeft (status, label, detailtekst) voor een brief."""
    info = brief.get("outreach") or {}
    status = info.get("status", "nieuw")
    if status not in STATUS_LABEL:
        status = "nieuw"
    bits = [b for b in (info.get("date"), info.get("note")) if b]
    return status, STATUS_LABEL[status], " · ".join(bits)

def load_briefs():
    """Laadt de briefs waarvoor ook echt een site gegenereerd is.

    Een brief kan al bestaan terwijl het sjabloon nog in de maak is; die
    overslaan voorkomt een dode link op het overzicht.
    """
    briefs, zonder_site = [], []
    sites = ROOT.parent / "sites"
    for path in sorted((ROOT / "briefs").glob("*.json")):
        brief = json.loads(path.read_text(encoding="utf-8"))
        if (sites / brief["slug"] / "index.html").exists():
            briefs.append(brief)
        else:
            zonder_site.append(brief["slug"])
    for slug in zonder_site:
        print(f"  overgeslagen (nog geen sites/{slug}/index.html): {slug}")
    return briefs

def render(briefs) -> str:
    total = len(briefs)
    sectors = {b.get("sector", "bakery") for b in briefs}
    ordered = sorted(briefs, key=lambda b: b["business_name"].lower())

    tally = {key: 0 for key, _, _ in STATUSSEN}
    tel_aantal = [0]
    cards = []
    for brief in ordered:
        sector = brief.get("sector", "bakery")
        label = esc(SECTOR_LABELS.get(sector, sector.capitalize()))
        status, status_label, detail = outreach_of(brief)
        tally[status] += 1
        tel = enkel_telefonisch(brief)
        if tel:
            tel_aantal[0] += 1
        tel_badge = f'<span class="badge badge-telefonisch">{TELEFOON_LABEL}</span>' if tel else ""
        detail_html = f'<span class="card-detail">{esc(detail)}</span>' if detail else ""
        cards.append(f"""      <a class="card" href="/{esc(brief['slug'])}/" data-status="{status}" data-phone="{'1' if tel else '0'}">
        <span class="card-top">
          <span class="card-sector">{label}</span>
          <span class="badges">
            <span class="badge badge-{status}">{esc(status_label)}</span>
            {tel_badge}
          </span>
        </span>
        <span class="card-name">{esc(brief['business_name'])}</span>
        <span class="card-cat">{esc(brief.get('category', ''))}</span>
        {detail_html}
      </a>""")

    filters = ['      <button class="filter is-active" type="button" data-filter="alles">'
               f'Alles <span class="filter-n">{total}</span></button>']
    for key, label, _ in STATUSSEN:
        if tally[key]:
            filters.append(
                f'      <button class="filter" type="button" data-filter="{key}">'
                f'{esc(label)} <span class="filter-n">{tally[key]}</span></button>'
            )
    if tel_aantal[0]:
        filters.append(
            f'      <button class="filter filter-kanaal" type="button" data-filter="telefonisch">'
            f'{TELEFOON_LABEL} <span class="filter-n">{tel_aantal[0]}</span></button>'
        )
    badge_css = "\n".join(
        f"  .badge-{key} {{ color: {kleur}; border-color: {kleur}33; background: {kleur}14; }}"
        for key, _, kleur in STATUSSEN
    ) + f"\n  .badge-telefonisch {{ color: {TELEFOON_KLEUR}; border-color: {TELEFOON_KLEUR}33; background: {TELEFOON_KLEUR}14; }}"

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prototypes — ocior.be</title>
<meta name="description" content="Site-prototypes voor lokale ondernemers in en rond Essen.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #14171c;
    --ink-soft: #5b6472;
    --paper: #ffffff;
    --panel: #f5f6f8;
    --line: #e2e5ea;
    --accent: #2f5fd0;
    --font-body: 'Inter', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 940px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 72px 0 40px;
    border-bottom: 1px solid var(--line);
  }}
  .kicker {{
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 14px;
  }}
  h1 {{
    font-size: clamp(1.9rem, 4vw, 2.6rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 14px;
  }}
  .sub {{
    color: var(--ink-soft);
    font-size: 1.05rem;
    max-width: 60ch;
  }}
  .count {{
    display: inline-block;
    margin-top: 22px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--ink-soft);
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 5px 14px;
  }}

  .filters {{
    display: flex; flex-wrap: wrap; gap: 8px;
    padding: 26px 0 4px;
  }}
  .filter {{
    font-family: var(--font-body);
    font-size: 0.86rem; font-weight: 500;
    color: var(--ink-soft);
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 7px 15px;
    cursor: pointer;
    transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
  }}
  .filter:hover {{ border-color: var(--ink-soft); color: var(--ink); }}
  .filter.is-active {{
    background: var(--ink); border-color: var(--ink); color: #fff;
  }}
  .filter-n {{ font-family: var(--font-mono); font-size: 0.76rem; opacity: 0.65; margin-left: 3px; }}
  /* Kanaalfilter staat los van de funnelstatus. */
  .filter-kanaal {{ border-style: dashed; }}
  .filter-kanaal.is-active {{ border-style: solid; }}

  main {{ padding: 20px 0 72px; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(268px, 1fr));
    gap: 12px;
  }}
  .card {{
    display: flex;
    flex-direction: column;
    gap: 3px;
    padding: 18px 20px;
    border: 1px solid var(--line);
    border-radius: 10px;
    text-decoration: none;
    color: inherit;
    background: var(--paper);
    transition: border-color 0.15s ease, background 0.15s ease, transform 0.15s ease;
  }}
  .card:hover {{
    border-color: var(--accent);
    background: var(--panel);
    transform: translateY(-1px);
  }}
  .card.is-hidden {{ display: none; }}
  .card-top {{
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 10px; margin-bottom: 6px;
  }}
  .badges {{ display: flex; flex-wrap: wrap; gap: 5px; justify-content: flex-end; }}
  .card-sector {{
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
  }}
  .badge {{
    font-size: 0.7rem;
    font-weight: 600;
    white-space: nowrap;
    border: 1px solid;
    border-radius: 999px;
    padding: 2px 9px;
  }}
{badge_css}
  .card-name {{ font-weight: 600; font-size: 1rem; letter-spacing: -0.01em; }}
  .card-cat {{ color: var(--ink-soft); font-size: 0.86rem; }}
  .card-detail {{
    font-family: var(--font-mono);
    font-size: 0.74rem;
    color: var(--ink-soft);
    margin-top: 6px;
  }}
  .empty {{ color: var(--ink-soft); font-size: 0.94rem; padding: 30px 0; }}

  footer {{
    border-top: 1px solid var(--line);
    padding: 28px 0 56px;
    font-size: 0.86rem;
    color: var(--ink-soft);
  }}
  footer a {{ color: var(--accent); text-decoration: none; font-weight: 500; }}
  footer a:hover {{ text-decoration: underline; }}

  a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="kicker">ocior.be</div>
    <h1>Prototypes</h1>
    <p class="sub">Site-prototypes voor lokale ondernemers in en rond Essen. Elke sector krijgt een eigen vormgeving — geen sjabloon dat overal hetzelfde oogt.</p>
    <span class="count">{total} prototypes · {len(sectors)} sectoren</span>
  </div>
</header>

<main>
  <div class="wrap">
    <div class="filters" id="filters">
{chr(10).join(filters)}
    </div>
    <div class="grid" id="grid">
{chr(10).join(cards)}
    </div>
    <p class="empty" id="empty" hidden>Niets in deze status.</p>
  </div>
</main>

<footer>
  <div class="wrap">
    Gemaakt door <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
  </div>
</footer>

<script>
  const knoppen = document.querySelectorAll('.filter');
  const kaarten = document.querySelectorAll('.card');
  const leeg = document.getElementById('empty');

  knoppen.forEach((knop) => {{
    knop.addEventListener('click', () => {{
      const filter = knop.dataset.filter;
      knoppen.forEach((k) => k.classList.toggle('is-active', k === knop));
      let zichtbaar = 0;
      kaarten.forEach((kaart) => {{
        // "telefonisch" is een kanaal, geen status: een kaart kan dus in
        // twee filters tegelijk zitten.
        const toon = filter === 'alles'
          || (filter === 'telefonisch' ? kaart.dataset.phone === '1'
                                       : kaart.dataset.status === filter);
        kaart.classList.toggle('is-hidden', !toon);
        if (toon) zichtbaar++;
      }});
      leeg.hidden = zichtbaar > 0;
    }});
  }});
</script>

</body>
</html>
"""

def main():
    briefs = load_briefs()
    out = ROOT.parent / "sites" / "index.html"
    out.write_text(render(briefs), encoding="utf-8")
    print(f"✓ Overzicht bijgewerkt: {out} ({len(briefs)} prototypes)")

if __name__ == "__main__":
    main()
