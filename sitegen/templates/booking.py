"""
Herbruikbare online-afspraakpagina, in eerste instantie voor kapsalons.

Een sjabloon roept render(brief, theme) aan; theme bepaalt de kleuren zodat de
boekingspagina bij de hoofdsite van dat prototype past. De behandelingen komen
uit het "booking_services" veld van de brief:

  "booking_services": [
    {"category": "Knippen", "items": [
        {"name": "Dames knippen", "desc": "...", "duration": 45, "price": 32}
    ]}
  ]

Prijzen zijn vaak niet publiek te vinden. Zet dan "booking_prices_verified":
false in de brief — de pagina toont bovenaan een duidelijke waarschuwing, zodat
een demo nooit voor een echte tarievenlijst kan doorgaan.
"""
from .common import esc

DEFAULT_THEME = {
    "bg": "#2a2724",
    "bg_deep": "#1c1a18",
    "accent": "#9c6b4f",
    "paper": "#faf8f5",
    "ink": "#1c1a18",
    "font_display": "'Cormorant Garamond', serif",
    "font_body": "'Manrope', sans-serif",
    "fonts_href": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400&family=Manrope:wght@400;500;600;700&display=swap",
}

def _money(value):
    return f"{float(value):.2f}".replace(".", ",")

# JS getDay(): zondag = 0
_DAG_INDEX = {
    "zondag": 0, "maandag": 1, "dinsdag": 2, "woensdag": 3,
    "donderdag": 4, "vrijdag": 5, "zaterdag": 6,
}

def _dagvensters(hours):
    """Leidt uit de openingsuren af op welke dagen er geboekt kan worden.

    Geeft {dagIndex: [startMinuut, eindMinuut]}. Dagen die ontbreken of
    'gesloten' zijn, komen er niet in. Zonder tijdsaanduiding (bv. 'Enkel op
    afspraak') geldt een standaardvenster.
    """
    vensters = {}
    for dag, tijd in hours or []:
        idx = _DAG_INDEX.get(str(dag).strip().lower())
        if idx is None:
            continue
        t = str(tijd)
        if "esloten" in t or "losed" in t:
            continue
        start, eind = 9 * 60, 17 * 60
        for scheider in ("–", "-", "—"):
            if scheider in t:
                links, rechts = t.split(scheider, 1)
                try:
                    su, sm = [int(x) for x in links.strip().split(":")]
                    eu, em = [int(x) for x in rechts.strip().split(":")]
                    start, eind = su * 60 + sm, eu * 60 + em
                except ValueError:
                    pass
                break
        vensters[idx] = [start, eind]
    return vensters

def render(brief: dict, theme: dict = None) -> str:
    t = {**DEFAULT_THEME, **(theme or {})}
    name = esc(brief["business_name"])
    slug = esc(brief["slug"])
    phone = esc(brief.get("phone", ""))
    address = esc(brief.get("address", ""))
    phone_href = phone.replace(" ", "").replace("/", "")
    groups = brief.get("booking_services", [])
    prices_verified = brief.get("booking_prices_verified", True)
    stylists = brief.get("booking_stylists", [])
    vensters = _dagvensters(brief.get("hours", []))
    vensters_js = "{" + ",".join(f"{k}:[{v[0]},{v[1]}]" for k, v in sorted(vensters.items())) + "}"

    disclaimer = ""
    if not prices_verified:
        disclaimer = """    <div class="notice" id="notice">
      <strong>Voorbeeldtarieven.</strong> De behandelingen, duurtijden en prijzen hieronder zijn ter
      illustratie ingevuld om te tonen hoe online boeken kan werken. De echte lijst wordt overgenomen
      van het salon zelf voor dit live gaat.
    </div>"""

    service_html = []
    for g_index, group in enumerate(groups):
        rows = []
        for i_index, item in enumerate(group.get("items", [])):
            sid = f"{g_index}-{i_index}"
            item_name = esc(item.get("name", ""))
            desc = esc(item.get("desc", ""))
            duration = int(item.get("duration", 30))
            price = item.get("price")
            meta = [f"{duration} min"]
            if price is not None:
                meta.append(f"&euro;&nbsp;{_money(price)}")
            desc_html = f'<span class="svc-desc">{desc}</span>' if desc else ""
            rows.append(f"""          <li>
            <button class="svc" type="button" data-id="{sid}" data-name="{item_name}"
              data-duration="{duration}" data-price="{price if price is not None else ''}">
              <span class="svc-text">
                <span class="svc-name">{item_name}</span>
                {desc_html}
              </span>
              <span class="svc-meta">{' · '.join(meta)}</span>
            </button>
          </li>""")
        service_html.append(f"""        <div class="svc-group">
          <h3>{esc(group.get('category', ''))}</h3>
          <ul>
{chr(10).join(rows)}
          </ul>
        </div>""")

    stylist_html = ""
    if stylists:
        knoppen = "\n".join(
            f'            <button class="chip" type="button" data-stylist="{esc(s)}">{esc(s)}</button>'
            for s in stylists
        )
        stylist_html = f"""      <div class="field">
        <label>Bij wie?</label>
        <div class="chips" id="stylists">
            <button class="chip is-on" type="button" data-stylist="">Maakt niet uit</button>
{knoppen}
        </div>
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Afspraak maken — {name}</title>
<meta name="description" content="Boek online een afspraak bij {name}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{t['fonts_href']}" rel="stylesheet">
<style>
  :root {{
    --bg: {t['bg']};
    --bg-deep: {t['bg_deep']};
    --accent: {t['accent']};
    --paper: {t['paper']};
    --ink: {t['ink']};
    --ink-soft: #6d6862;
    --line: rgba(28,26,24,0.14);
    --font-display: {t['font_display']};
    --font-body: {t['font_body']};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 720px; margin: 0 auto; padding: 0 20px; }}

  header.top {{ background: var(--bg); color: #fff; padding: 16px 0; }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{ font-family: var(--font-display); font-size: 1.3rem; letter-spacing: 0.02em; }}
  .back {{ font-size: 0.88rem; color: rgba(255,255,255,0.8); text-decoration: none; }}
  .back:hover {{ color: #fff; }}

  .hero {{ padding: 30px 0 8px; }}
  .hero h1 {{ font-family: var(--font-display); font-size: clamp(1.9rem, 5vw, 2.5rem); font-weight: 600; margin-bottom: 6px; }}
  .hero p {{ color: var(--ink-soft); font-size: 0.98rem; }}

  .notice {{
    background: #fdf3e3;
    border-left: 4px solid var(--accent);
    color: #4d3a24;
    font-size: 0.9rem;
    padding: 13px 16px;
    border-radius: 6px;
    margin-top: 20px;
  }}

  /* Stappen */
  .steps {{ display: flex; gap: 8px; padding: 22px 0 6px; }}
  /* display:flex wint van het hidden-attribuut, dus expliciet verbergen. */
  .steps[hidden] {{ display: none; }}
  .step-dot {{
    flex: 1;
    font-size: 0.76rem;
    color: var(--ink-soft);
    border-top: 3px solid var(--line);
    padding-top: 8px;
  }}
  .step-dot.is-done, .step-dot.is-now {{ color: var(--ink); border-top-color: var(--accent); font-weight: 600; }}

  .panel {{ padding: 18px 0 60px; }}
  .panel[hidden] {{ display: none; }}
  h2 {{ font-family: var(--font-display); font-size: 1.5rem; font-weight: 600; margin-bottom: 14px; }}

  .svc-group {{ margin-bottom: 22px; }}
  .svc-group h3 {{
    font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.12em;
    color: var(--accent); font-weight: 700; margin-bottom: 8px;
  }}
  .svc-group ul {{ list-style: none; }}
  .svc {{
    width: 100%;
    display: flex; justify-content: space-between; align-items: center; gap: 14px;
    text-align: left;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
    font-family: inherit; font-size: 1rem; color: inherit;
    cursor: pointer;
    min-height: 56px;
    transition: border-color 0.15s ease, background 0.15s ease;
  }}
  .svc:hover {{ border-color: var(--accent); }}
  .svc.is-on {{ border-color: var(--accent); background: #fff; box-shadow: inset 0 0 0 1px var(--accent); }}
  .svc-text {{ display: flex; flex-direction: column; gap: 2px; }}
  .svc-name {{ font-weight: 600; }}
  .svc-desc {{ color: var(--ink-soft); font-size: 0.86rem; }}
  .svc-meta {{ color: var(--ink-soft); font-size: 0.86rem; white-space: nowrap; font-variant-numeric: tabular-nums; }}

  .field {{ margin-bottom: 20px; }}
  .field label {{ display: block; font-weight: 600; font-size: 0.92rem; margin-bottom: 8px; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .chip {{
    font-family: inherit; font-size: 0.92rem;
    background: #fff; color: var(--ink);
    border: 1px solid var(--line); border-radius: 999px;
    padding: 10px 16px; min-height: 44px;
    cursor: pointer;
  }}
  .chip:hover {{ border-color: var(--accent); }}
  .chip.is-on {{ background: var(--bg); border-color: var(--bg); color: #fff; }}
  .chip:disabled {{ opacity: 0.35; cursor: not-allowed; }}

  input[type=text], input[type=tel], input[type=email], textarea {{
    width: 100%;
    font-family: inherit; font-size: 1rem;
    padding: 13px 14px;
    border: 1px solid var(--line); border-radius: 10px;
    background: #fff; color: var(--ink);
    min-height: 50px;
  }}
  textarea {{ min-height: 88px; resize: vertical; }}
  input:focus, textarea:focus {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .hint {{ font-size: 0.82rem; color: var(--ink-soft); margin-top: 5px; }}
  .error {{ font-size: 0.85rem; color: #b3261e; margin-top: 6px; }}
  .error[hidden] {{ display: none; }}

  .summary {{
    background: #fff; border: 1px solid var(--line); border-radius: 12px;
    padding: 18px; margin-bottom: 20px;
  }}
  .sum-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 7px 0; font-size: 0.95rem; }}
  .sum-row + .sum-row {{ border-top: 1px solid var(--line); }}
  .sum-label {{ color: var(--ink-soft); }}
  .sum-val {{ font-weight: 600; text-align: right; }}

  .actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .btn {{
    font-family: inherit; font-size: 1rem; font-weight: 600;
    border-radius: 10px; padding: 15px 26px; min-height: 52px;
    cursor: pointer; border: none;
  }}
  .btn-main {{ background: var(--accent); color: #fff; flex: 1; min-width: 180px; }}
  .btn-main:hover {{ filter: brightness(1.07); }}
  .btn-main:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  .btn-ghost {{ background: transparent; color: var(--ink); border: 1px solid var(--line); }}
  .btn-ghost:hover {{ border-color: var(--ink-soft); }}

  .done {{ text-align: center; padding: 40px 0 70px; }}
  .done .tick {{
    width: 62px; height: 62px; border-radius: 50%;
    background: var(--accent); color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.9rem; margin: 0 auto 18px;
  }}
  .done h2 {{ margin-bottom: 10px; }}
  .done p {{ color: var(--ink-soft); margin-bottom: 10px; }}
  .done .call {{ display: inline-block; margin-top: 14px; font-weight: 600; color: var(--accent); }}

  footer {{ border-top: 1px solid var(--line); padding: 22px 0 40px; font-size: 0.84rem; color: var(--ink-soft); text-align: center; }}

  @media (max-width: 520px) {{
    .btn-main {{ width: 100%; }}
    .svc {{ align-items: flex-start; flex-direction: column; gap: 6px; }}
    .svc-meta {{ font-weight: 600; color: var(--ink); }}
  }}
  a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="back" href="/{slug}/">&larr; Terug naar de site</a>
  </div>
</header>

<div class="wrap">
  <section class="hero">
    <h1>Afspraak maken</h1>
    <p>In drie stappen geregeld — geen account nodig.</p>
  </section>
{disclaimer}

  <div class="steps" id="steps">
    <div class="step-dot is-now" data-step="1">1 · Behandeling</div>
    <div class="step-dot" data-step="2">2 · Moment</div>
    <div class="step-dot" data-step="3">3 · Gegevens</div>
  </div>

  <!-- Stap 1 -->
  <section class="panel" id="panel-1">
    <h2>Wat mogen we doen?</h2>
{chr(10).join(service_html)}
    <div class="actions">
      <button class="btn btn-main" id="naar-2" disabled>Kies een moment</button>
    </div>
  </section>

  <!-- Stap 2 -->
  <section class="panel" id="panel-2" hidden>
    <h2>Wanneer komt het uit?</h2>
{stylist_html}
    <div class="field">
      <label>Welke dag?</label>
      <div class="chips" id="dagen"></div>
    </div>
    <div class="field">
      <label>Hoe laat?</label>
      <div class="chips" id="uren"></div>
      <p class="hint">Vrije momenten worden hier getoond zodra je een dag kiest.</p>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-terug="1">Terug</button>
      <button class="btn btn-main" id="naar-3" disabled>Verder naar gegevens</button>
    </div>
  </section>

  <!-- Stap 3 -->
  <section class="panel" id="panel-3" hidden>
    <h2>Nog even je gegevens</h2>
    <div class="summary" id="samenvatting"></div>
    <div class="field">
      <label for="naam">Naam</label>
      <input type="text" id="naam" autocomplete="name" placeholder="Voor- en achternaam">
      <p class="error" id="fout-naam" hidden>Vul je naam in.</p>
    </div>
    <div class="field">
      <label for="tel">Telefoon</label>
      <input type="tel" id="tel" autocomplete="tel" inputmode="tel" placeholder="Zodat we je kunnen bereiken">
      <p class="error" id="fout-tel" hidden>Vul een geldig telefoonnummer in.</p>
    </div>
    <div class="field">
      <label for="opm">Iets dat we moeten weten? <span style="font-weight:400;color:var(--ink-soft)">(optioneel)</span></label>
      <textarea id="opm" placeholder="Bijvoorbeeld: liever niet te kort"></textarea>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-terug="2">Terug</button>
      <button class="btn btn-main" id="bevestig">Afspraak bevestigen</button>
    </div>
  </section>

  <!-- Klaar -->
  <section class="panel done" id="panel-klaar" hidden>
    <div class="tick">&check;</div>
    <h2>Zo zou het gaan</h2>
    <div class="summary" id="samenvatting-klaar"></div>
    <p>In de echte versie komt deze afspraak meteen in de agenda van het salon, met een
       bevestiging per sms.</p>
    <p>Dit is een prototype, dus er wordt nog niets vastgelegd.</p>
    <a class="call" href="tel:{phone_href}">Bel {phone} om echt te boeken</a>
  </section>
</div>

<footer>
  Prototype gebouwd voor {name} &middot; <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
</footer>

<script>
  const staat = {{ dienst: null, stylist: '', dag: null, uur: null }};

  const toon = (n) => {{
    [1, 2, 3].forEach((i) => {{
      document.getElementById('panel-' + i).hidden = (i !== n);
    }});
    document.getElementById('panel-klaar').hidden = true;
    document.querySelectorAll('.step-dot').forEach((d) => {{
      const s = Number(d.dataset.step);
      d.classList.toggle('is-now', s === n);
      d.classList.toggle('is-done', s < n);
    }});
    document.getElementById('steps').hidden = false;
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }};

  // Stap 1 — behandeling
  document.querySelectorAll('.svc').forEach((knop) => {{
    knop.addEventListener('click', () => {{
      document.querySelectorAll('.svc').forEach((k) => k.classList.remove('is-on'));
      knop.classList.add('is-on');
      staat.dienst = {{
        naam: knop.dataset.name,
        duur: Number(knop.dataset.duration),
        prijs: knop.dataset.price ? Number(knop.dataset.price) : null
      }};
      document.getElementById('naar-2').disabled = false;
    }});
  }});
  document.getElementById('naar-2').addEventListener('click', () => {{ vulDagen(); toon(2); }});

  // Stap 2 — stylist, dag, uur
  const stylistBox = document.getElementById('stylists');
  if (stylistBox) {{
    stylistBox.addEventListener('click', (e) => {{
      const chip = e.target.closest('.chip');
      if (!chip) return;
      stylistBox.querySelectorAll('.chip').forEach((c) => c.classList.remove('is-on'));
      chip.classList.add('is-on');
      staat.stylist = chip.dataset.stylist;
    }});
  }}

  const dagNamen = ['zo', 'ma', 'di', 'wo', 'do', 'vr', 'za'];
  const maandNamen = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];

  // Openingsvensters per weekdag, afgeleid uit de openingsuren van de zaak.
  const vensters = {vensters_js};

  function vulDagen() {{
    const box = document.getElementById('dagen');
    if (box.childElementCount) return;
    const vandaag = new Date();
    for (let i = 1; i <= 21 && box.childElementCount < 8; i++) {{
      const d = new Date(vandaag);
      d.setDate(vandaag.getDate() + i);
      if (!vensters[d.getDay()]) continue; // die dag is de zaak dicht
      const knop = document.createElement('button');
      knop.type = 'button';
      knop.className = 'chip';
      knop.textContent = dagNamen[d.getDay()] + ' ' + d.getDate() + ' ' + maandNamen[d.getMonth()];
      knop.dataset.dag = knop.textContent;
      knop.addEventListener('click', () => {{
        box.querySelectorAll('.chip').forEach((c) => c.classList.remove('is-on'));
        knop.classList.add('is-on');
        staat.dag = knop.dataset.dag;
        staat.uur = null;
        vulUren(d);
        controleerStap2();
      }});
      box.appendChild(knop);
    }}
  }}

  function vulUren(datum) {{
    const box = document.getElementById('uren');
    box.innerHTML = '';
    const venster = vensters[datum.getDay()] || [9 * 60, 17 * 60];
    const start = venster[0];
    // Laatste start zo kiezen dat de behandeling nog binnen de openingsuren past.
    const eind = Math.max(start, venster[1] - (staat.dienst ? staat.dienst.duur : 30));
    const stap = 30;
    // Zaterdag drukker: minder vrije momenten.
    const bezet = datum.getDay() === 6 ? 5 : 3;
    let idx = 0;
    for (let m = start; m <= eind; m += stap, idx++) {{
      const uur = String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
      const knop = document.createElement('button');
      knop.type = 'button';
      knop.className = 'chip';
      knop.textContent = uur;
      // Vast patroon i.p.v. random, zodat het niet verspringt bij herklikken.
      // Reken met de slotindex: minuten zijn altijd veelvouden van 30, waardoor
      // een modulo daarop voor elk slot dezelfde waarde zou geven.
      const vrij = ((datum.getDate() * 3 + idx * 7) % 10) >= bezet;
      knop.disabled = !vrij;
      knop.addEventListener('click', () => {{
        box.querySelectorAll('.chip').forEach((c) => c.classList.remove('is-on'));
        knop.classList.add('is-on');
        staat.uur = uur;
        controleerStap2();
      }});
      box.appendChild(knop);
    }}
  }}

  function controleerStap2() {{
    document.getElementById('naar-3').disabled = !(staat.dag && staat.uur);
  }}
  document.getElementById('naar-3').addEventListener('click', () => {{ vulSamenvatting(); toon(3); }});

  document.querySelectorAll('[data-terug]').forEach((b) => {{
    b.addEventListener('click', () => toon(Number(b.dataset.terug)));
  }});

  function rij(label, waarde) {{
    return '<div class="sum-row"><span class="sum-label">' + label +
           '</span><span class="sum-val">' + waarde + '</span></div>';
  }}

  function samenvattingHtml() {{
    let h = rij('Behandeling', staat.dienst.naam);
    h += rij('Duurt', staat.dienst.duur + ' min');
    if (staat.dienst.prijs !== null) {{
      h += rij('Prijs', '\\u20ac\\u00a0' + staat.dienst.prijs.toFixed(2).replace('.', ','));
    }}
    if (staat.stylist) h += rij('Bij', staat.stylist);
    h += rij('Wanneer', staat.dag + ' om ' + staat.uur);
    return h;
  }}

  function vulSamenvatting() {{
    document.getElementById('samenvatting').innerHTML = samenvattingHtml();
  }}

  // Stap 3 — gegevens
  document.getElementById('bevestig').addEventListener('click', () => {{
    const naam = document.getElementById('naam');
    const tel = document.getElementById('tel');
    const foutNaam = document.getElementById('fout-naam');
    const foutTel = document.getElementById('fout-tel');
    const cijfers = tel.value.replace(/\\D/g, '');
    foutNaam.hidden = naam.value.trim().length > 1;
    foutTel.hidden = cijfers.length >= 8;
    if (!foutNaam.hidden) {{ naam.focus(); return; }}
    if (!foutTel.hidden) {{ tel.focus(); return; }}

    let h = samenvattingHtml() + rij('Op naam van', naam.value.trim());
    document.getElementById('samenvatting-klaar').innerHTML = h;
    [1, 2, 3].forEach((i) => {{ document.getElementById('panel-' + i).hidden = true; }});
    document.getElementById('steps').hidden = true;
    const melding = document.getElementById('notice');
    if (melding) melding.hidden = true;
    document.getElementById('panel-klaar').hidden = false;
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }});
</script>

</body>
</html>
"""
