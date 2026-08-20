"""Sjabloon voor een accountants-/fiscaal kantoor.

Eigen identiteit: koel indigo-navy met een teal accent, IBM Plex Sans/Mono
(tabulaire cijfers) en als signature-element een "grootboek"-kaart met
gelinieerde rijen — het ritme van het fiscale jaar. Bewust géén openingsuren:
een accountant werkt op afspraak, niet met winkeluren.

Verwachte velden in de brief (alles behalve business_name is optioneel; lege
velden laten hun blok gewoon weg, zodat er nooit een leeg kader overblijft):

  business_name, category, tagline, intro, about, address, email, phone,
  contact_person, contact_role, availability, cta_text,
  stats:     [{"value": "2017", "label": "kantoor opgericht"}]
  ledger:    [{"label": "Btw-aangifte", "freq": "per kwartaal"}]
  ledger_title, ledger_note
  services:  [{"title": ..., "text": ..., "items": [...]}]
  audiences: [{"title": ..., "text": ...}]
  steps:     [{"title": ..., "text": ...}]
  legal_line
"""
from .common import esc, maps_query as _maps_query


def _tel_href(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit() or ch == "+")


def _services(items):
    out = []
    for i, svc in enumerate(items, start=1):
        bullets = "".join(
            f"<li>{esc(b)}</li>" for b in svc.get("items", [])
        )
        bullets_html = f'<ul class="svc-list">{bullets}</ul>' if bullets else ""
        text = f'<p>{esc(svc.get("text", ""))}</p>' if svc.get("text") else ""
        out.append(f"""      <article class="svc">
        <span class="svc-n">{i:02d}</span>
        <h3>{esc(svc.get("title", ""))}</h3>
        {text}
        {bullets_html}
      </article>""")
    return "\n".join(out)


def _audiences(items):
    out = []
    for a in items:
        text = f'<p>{esc(a.get("text", ""))}</p>' if a.get("text") else ""
        out.append(f"""      <li class="aud">
        <h3>{esc(a.get("title", ""))}</h3>
        {text}
      </li>""")
    return "\n".join(out)


def _steps(items):
    out = []
    for i, s in enumerate(items, start=1):
        text = f'<p>{esc(s.get("text", ""))}</p>' if s.get("text") else ""
        out.append(f"""      <li class="step">
        <span class="step-n">{i}</span>
        <div>
          <h3>{esc(s.get("title", ""))}</h3>
          {text}
        </div>
      </li>""")
    return "\n".join(out)


def _ledger(rows):
    out = []
    for r in rows:
        out.append(
            '<div class="led-row">'
            f'<span class="led-label">{esc(r.get("label", ""))}</span>'
            f'<span class="led-freq">{esc(r.get("freq", ""))}</span>'
            "</div>"
        )
    return "\n".join(out)


def _stats(items):
    out = []
    for s in items:
        out.append(
            '<div class="stat">'
            f'<span class="stat-v">{esc(s.get("value", ""))}</span>'
            f'<span class="stat-l">{esc(s.get("label", ""))}</span>'
            "</div>"
        )
    return "\n".join(out)


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    intro = esc(brief.get("intro", ""))
    about = esc(brief.get("about", ""))
    address = esc(brief.get("address", ""))
    email = esc(brief.get("email", ""))
    phone = brief.get("phone", "")
    person = esc(brief.get("contact_person", ""))
    role = esc(brief.get("contact_role", ""))
    availability = esc(brief.get("availability", ""))
    cta = esc(brief.get("cta_text", "Plan een kennismaking"))
    legal_line = esc(brief.get("legal_line", ""))
    ledger_title = esc(brief.get("ledger_title", "Het ritme van het jaar"))
    ledger_note = esc(brief.get("ledger_note", ""))

    services_html = _services(brief.get("services", []))
    audiences_html = _audiences(brief.get("audiences", []))
    steps_html = _steps(brief.get("steps", []))
    ledger_html = _ledger(brief.get("ledger", []))
    stats_html = _stats(brief.get("stats", []))
    maps_q = _maps_query(brief.get("address", ""))

    # Primaire actie: mailen als er een adres is, anders bellen, anders naar
    # het contactblok scrollen. Zo staat er nooit een dode link op de pagina.
    if email:
        primary_href = f"mailto:{email}"
    elif phone:
        primary_href = f"tel:{_tel_href(phone)}"
    else:
        primary_href = "#contact"

    # De kopbalk blijft op een telefoon één regel hoog: daar valt de lange
    # CTA-tekst weg en blijft een kort label over.
    cta_short = esc(brief.get("cta_short", "Contact"))
    if email or phone:
        header_action = (
            f'<a class="top-cta" href="{primary_href}">'
            f'<span class="cta-long">{cta}</span>'
            f'<span class="cta-short">{cta_short}</span></a>'
        )
    else:
        header_action = f'<a class="top-cta" href="#contact">{cta_short}</a>'

    intro_html = f'<p class="lede">{intro}</p>' if intro else ""
    stats_block = f'<div class="stats">\n{stats_html}\n</div>' if stats_html else ""
    ledger_note_html = f'<p class="led-note">{ledger_note}</p>' if ledger_note else ""
    ledger_block = f"""    <aside class="ledger" aria-label="{ledger_title}">
      <div class="led-head">
        <span class="led-title">{ledger_title}</span>
        <span class="led-mark" aria-hidden="true"></span>
      </div>
{ledger_html}
      {ledger_note_html}
    </aside>""" if ledger_html else ""

    about_block = f"""<section class="about" id="over">
  <div class="wrap about-grid">
    <div class="about-head">
      <span class="eyebrow">Over het kantoor</span>
      <h2>Eén aanspreekpunt dat uw dossier kent</h2>
    </div>
    <div class="about-body">
      <p>{about}</p>
      {f'<p class="signature"><strong>{person}</strong><span>{role}</span></p>' if person else ""}
    </div>
  </div>
</section>""" if about else ""

    services_block = f"""<section class="services" id="diensten">
  <div class="wrap">
    <span class="eyebrow">Diensten</span>
    <h2>Wat we voor u opnemen</h2>
    <div class="svc-grid">
{services_html}
    </div>
  </div>
</section>""" if services_html else ""

    audiences_block = f"""<section class="audiences">
  <div class="wrap">
    <span class="eyebrow">Voor wie</span>
    <h2>Ondernemers in en rond Essen</h2>
    <ul class="aud-grid">
{audiences_html}
    </ul>
  </div>
</section>""" if audiences_html else ""

    steps_block = f"""<section class="approach" id="aanpak">
  <div class="wrap">
    <span class="eyebrow">Aanpak</span>
    <h2>Van eerste gesprek tot lopend dossier</h2>
    <ol class="steps">
{steps_html}
    </ol>
  </div>
</section>""" if steps_html else ""

    contact_rows = []
    if email:
        contact_rows.append(
            f'<a class="big-link" href="mailto:{email}">{email}</a>'
        )
    if phone:
        contact_rows.append(
            f'<a class="big-link" href="tel:{_tel_href(phone)}">{esc(phone)}</a>'
        )
    contact_links = "\n      ".join(contact_rows)

    address_block = ""
    if address:
        address_block = f"""<div class="contact-col">
        <span class="contact-k">Kantoor</span>
        <p class="contact-v">{address}</p>
        <a class="map-link" href="https://www.google.com/maps/search/?api=1&amp;query={maps_q}" target="_blank" rel="noopener">Bekijk op kaart <span aria-hidden="true">&rarr;</span></a>
      </div>"""

    availability_block = f"""<div class="contact-col">
        <span class="contact-k">Afspraken</span>
        <p class="contact-v">{availability}</p>
      </div>""" if availability else ""

    person_block = f"""<div class="contact-col">
        <span class="contact-k">Aanspreekpunt</span>
        <p class="contact-v">{person}{f'<br><span class="contact-role">{role}</span>' if role else ""}</p>
      </div>""" if person else ""

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline or intro}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #101A2E;
    --ink-2: #1B2942;
    --ink-soft: #5C6B85;
    --paper: #ffffff;
    --mist: #F1F4F9;
    --mist-2: #E7EDF5;
    --rule: #D8E1EC;
    --accent: #0E8F80;
    --accent-dk: #0A6E63;
    --accent-tint: #E2F2EF;
    --font-body: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, monospace;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }}
  img {{ max-width: 100%; height: auto; }}
  a {{ color: inherit; }}
  .wrap {{ width: 100%; max-width: 1060px; margin: 0 auto; padding: 0 24px; }}

  .eyebrow {{
    display: block;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent-dk);
    margin-bottom: 12px;
  }}
  h2 {{
    font-size: clamp(1.5rem, 3vw, 2.05rem);
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 34px;
  }}
  h3 {{
    font-size: 1.02rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 8px;
  }}
  section {{ padding: 76px 0; }}

  /* ---------- kop ---------- */
  header.top {{
    position: sticky; top: 0; z-index: 20;
    background: rgba(255,255,255,0.94);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--rule);
  }}
  header.top .wrap {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; min-height: 68px; flex-wrap: wrap;
  }}
  .brand {{
    display: inline-flex; align-items: center; gap: 11px;
    font-weight: 600; font-size: 1.08rem; letter-spacing: -0.01em;
    padding: 12px 0;
    text-decoration: none;
  }}
  .brand-mark {{
    width: 26px; height: 26px; flex: none;
    border: 1.5px solid var(--ink);
    border-radius: 5px;
    position: relative; overflow: hidden;
    background: var(--paper);
  }}
  .brand-mark::before, .brand-mark::after {{
    content: ""; position: absolute; left: 4px; right: 4px; height: 1.5px;
    background: var(--rule);
  }}
  .brand-mark::before {{ top: 8px; }}
  .brand-mark::after {{ top: 13px; background: var(--accent); right: 10px; }}
  .top-cta {{
    display: inline-flex; align-items: center;
    min-height: 44px; padding: 11px 22px;
    background: var(--ink); color: #fff;
    font-size: 0.88rem; font-weight: 500;
    border-radius: 6px; text-decoration: none;
  }}
  .top-cta:hover {{ background: var(--ink-2); }}
  .cta-short {{ display: none; }}

  /* ---------- hero ---------- */
  .hero {{
    background: var(--mist);
    border-bottom: 1px solid var(--rule);
    position: relative; overflow: hidden;
    padding: 78px 0 82px;
  }}
  /* gelinieerd 'rekenpapier' als achtergrondtextuur */
  .hero::before {{
    content: ""; position: absolute; inset: 0;
    background-image: repeating-linear-gradient(
      to bottom, transparent 0 31px, var(--rule) 31px 32px);
    opacity: 0.5; pointer-events: none;
  }}
  .hero .wrap {{ position: relative; }}
  .hero-grid {{
    display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
    gap: 56px; align-items: start;
  }}
  h1 {{
    font-size: clamp(2rem, 4.6vw, 3.1rem);
    font-weight: 600;
    line-height: 1.1;
    letter-spacing: -0.032em;
    margin-bottom: 20px;
    max-width: 16ch;
  }}
  .hero .lede {{
    font-size: 1.06rem;
    color: var(--ink-soft);
    max-width: 46ch;
    margin-bottom: 30px;
  }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; }}
  .btn {{
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 48px; padding: 13px 26px;
    border-radius: 6px; text-decoration: none;
    font-size: 0.94rem; font-weight: 500;
  }}
  .btn-primary {{ background: var(--accent); color: #fff; }}
  .btn-primary:hover {{ background: var(--accent-dk); }}
  .btn-ghost {{ border: 1px solid var(--rule); background: var(--paper); color: var(--ink); }}
  .btn-ghost:hover {{ border-color: var(--ink-soft); }}

  .stats {{
    display: flex; flex-wrap: wrap; gap: 32px;
    margin-top: 40px; padding-top: 26px;
    border-top: 1px solid var(--rule);
  }}
  .stat {{ display: flex; flex-direction: column; gap: 2px; }}
  .stat-v {{
    font-family: var(--font-mono); font-variant-numeric: tabular-nums;
    font-size: 1.35rem; font-weight: 500; color: var(--ink);
  }}
  .stat-l {{ font-size: 0.8rem; color: var(--ink-soft); }}

  /* ---------- signature: grootboekkaart ---------- */
  .ledger {{
    background: var(--paper);
    border: 1px solid var(--rule);
    border-radius: 10px;
    padding: 8px 22px 20px;
    box-shadow: 0 18px 40px -28px rgba(16,26,46,0.5);
  }}
  .led-head {{
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 16px 0 12px;
    border-bottom: 2px solid var(--ink);
  }}
  .led-title {{
    font-size: 0.9rem; font-weight: 600; letter-spacing: -0.01em;
  }}
  .led-mark {{
    width: 34px; height: 8px; flex: none; border-radius: 999px;
    background: linear-gradient(to right, var(--accent) 0 60%, var(--mist-2) 60% 100%);
  }}
  .led-row {{
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 4px 14px; padding: 13px 0;
    border-bottom: 1px solid var(--rule);
    flex-wrap: wrap;
  }}
  .led-label {{ font-size: 0.93rem; min-width: 0; }}
  .led-freq {{
    font-family: var(--font-mono); font-variant-numeric: tabular-nums;
    font-size: 0.78rem; color: var(--accent-dk);
    background: var(--accent-tint);
    padding: 3px 9px; border-radius: 4px;
    white-space: nowrap;
  }}
  .led-note {{
    font-size: 0.79rem; color: var(--ink-soft);
    margin-top: 16px; line-height: 1.5;
  }}

  /* ---------- over ---------- */
  .about {{ border-bottom: 1px solid var(--rule); }}
  .about-grid {{
    display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
    gap: 48px;
  }}
  .about h2 {{ margin-bottom: 0; }}
  .about-body p {{ font-size: 1.04rem; color: var(--ink-soft); }}
  .signature {{
    margin-top: 26px; padding-top: 18px;
    border-top: 1px solid var(--rule);
    display: flex; flex-direction: column;
  }}
  .signature strong {{ font-weight: 600; color: var(--ink); }}
  .signature span {{
    font-family: var(--font-mono); font-size: 0.78rem; color: var(--ink-soft);
  }}

  /* ---------- diensten ---------- */
  .services {{ background: var(--mist); border-bottom: 1px solid var(--rule); }}
  .svc-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
    gap: 1px; background: var(--rule);
    border: 1px solid var(--rule); border-radius: 10px; overflow: hidden;
  }}
  .svc {{ background: var(--paper); padding: 28px 26px 30px; }}
  .svc-n {{
    display: block;
    font-family: var(--font-mono); font-variant-numeric: tabular-nums;
    font-size: 0.75rem; color: var(--accent-dk); margin-bottom: 14px;
  }}
  .svc p {{ font-size: 0.93rem; color: var(--ink-soft); }}
  .svc-list {{ list-style: none; margin-top: 14px; }}
  .svc-list li {{
    position: relative; padding-left: 18px; margin-top: 7px;
    font-size: 0.87rem; color: var(--ink-soft);
  }}
  .svc-list li::before {{
    content: ""; position: absolute; left: 0; top: 0.62em;
    width: 8px; height: 1.5px; background: var(--accent);
  }}

  /* ---------- voor wie ---------- */
  .aud-grid {{
    list-style: none;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 26px;
  }}
  .aud {{ padding-top: 18px; border-top: 2px solid var(--ink); }}
  .aud p {{ font-size: 0.9rem; color: var(--ink-soft); }}

  /* ---------- aanpak ---------- */
  .approach {{ background: var(--ink); color: #fff; }}
  .approach .eyebrow {{ color: #6FD3C6; }}
  .approach h2 {{ color: #fff; }}
  .steps {{ list-style: none; display: grid; gap: 1px; background: rgba(255,255,255,0.14); }}
  .step {{
    background: var(--ink);
    display: flex; gap: 20px; align-items: flex-start;
    padding: 24px 4px;
  }}
  .step-n {{
    flex: none;
    width: 34px; height: 34px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    border: 1px solid rgba(255,255,255,0.35);
    font-family: var(--font-mono); font-size: 0.82rem;
    color: #6FD3C6;
  }}
  .step h3 {{ color: #fff; }}
  .step p {{ color: rgba(255,255,255,0.72); font-size: 0.94rem; max-width: 62ch; }}

  /* ---------- contact ---------- */
  .contact {{ background: var(--mist-2); }}
  .contact h2 {{ margin-bottom: 26px; }}
  .big-link {{
    display: inline-block;
    font-size: clamp(1.2rem, 3vw, 1.75rem);
    font-weight: 600; letter-spacing: -0.02em;
    color: var(--accent-dk); text-decoration: none;
    padding: 8px 0; min-height: 44px;
    overflow-wrap: anywhere;
  }}
  .big-link:hover {{ text-decoration: underline; }}
  .contact-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 28px;
    margin-top: 34px; padding-top: 28px;
    border-top: 1px solid var(--rule);
  }}
  .contact-k {{
    display: block;
    font-family: var(--font-mono); font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--ink-soft); margin-bottom: 8px;
  }}
  .contact-v {{ font-size: 0.98rem; }}
  .contact-role {{ font-family: var(--font-mono); font-size: 0.78rem; color: var(--ink-soft); }}
  .map-link {{
    display: inline-block; margin-top: 10px;
    min-height: 44px; padding: 10px 0;
    font-size: 0.88rem; font-weight: 500;
    color: var(--accent-dk); text-decoration: none;
  }}
  .map-link:hover {{ text-decoration: underline; }}

  footer {{
    padding: 30px 0 38px;
    border-top: 1px solid var(--rule);
    font-size: 0.79rem; color: var(--ink-soft);
  }}
  footer .wrap {{ display: flex; flex-wrap: wrap; gap: 10px 26px; justify-content: space-between; }}
  /* negatieve marge houdt de regel visueel gelijk, maar geeft de link een
     tapdoel van 44px hoog op een telefoon */
  footer a {{
    color: var(--accent-dk);
    display: inline-block;
    padding: 14px 4px; margin: -14px -4px;
  }}

  a:focus-visible, .btn:focus-visible, .top-cta:focus-visible {{
    outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 4px;
  }}

  @media (max-width: 900px) {{
    /* minmax(0,1fr) en niet 1fr: anders rekt een brede kaart de kolom
       voorbij de schermbreedte op en valt de rechterrand weg */
    .hero-grid, .about-grid {{ grid-template-columns: minmax(0, 1fr); gap: 40px; }}
    h1 {{ max-width: 20ch; }}
  }}
  @media (max-width: 620px) {{
    section {{ padding: 56px 0; }}
    .wrap {{ padding: 0 18px; }}
    header.top .wrap {{ flex-wrap: nowrap; min-height: 60px; }}
    .brand {{
      font-size: 0.98rem; min-width: 0;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .top-cta {{ padding: 11px 16px; white-space: nowrap; }}
    .cta-long {{ display: none; }}
    .cta-short {{ display: inline; }}
    .eyebrow {{ font-size: 0.68rem; letter-spacing: 0.1em; }}
    .hero {{ padding: 52px 0 58px; }}
    .stats {{ gap: 22px 26px; }}
    .hero-actions .btn {{ flex: 1 1 100%; }}
    .step {{ gap: 14px; padding: 20px 0; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    html {{ scroll-behavior: auto; }}
  }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <a class="brand" href="#top"><span class="brand-mark" aria-hidden="true"></span>{name}</a>
    {header_action}
  </div>
</header>

<main id="top">

<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">{category}</span>
      <h1>{tagline}</h1>
      {intro_html}
      <div class="hero-actions">
        <a class="btn btn-primary" href="{primary_href}">{cta}</a>
        <a class="btn btn-ghost" href="#diensten">Wat we doen</a>
      </div>
      {stats_block}
    </div>
{ledger_block}
  </div>
</section>

{about_block}

{services_block}

{audiences_block}

{steps_block}

<section class="contact" id="contact">
  <div class="wrap">
    <span class="eyebrow">Contact</span>
    <h2>{cta}</h2>
    <div class="contact-links">
      {contact_links}
    </div>
    <div class="contact-grid">
      {person_block}
      {address_block}
      {availability_block}
    </div>
  </div>
</section>

</main>

<footer>
  <div class="wrap">
    <span>{legal_line}</span>
    <span>Prototype gebouwd voor {name} · <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a></span>
  </div>
</footer>

</body>
</html>
"""
