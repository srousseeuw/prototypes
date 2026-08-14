"""Sjabloon voor een ambachtelijke brood- en banketbakkerij met familiegeschiedenis.

Visuele identiteit: de geglazuurde winkelpuitegel van de klassieke Vlaamse
buurtbakkerij — diep tealgroen, tarwegoud en warm haverwit. Signature element
is de generatietijdlijn: een bakkerij die al decennia in dezelfde familie zit
verkoopt vooral continuïteit, dus die krijgt een eigen sectie.

Velden in de brief:
  business_name, category, tagline, address, phone, email, about, cta_text
  founded            (str, bv. "1947") -> tegel-badge in de hero
  highlights         (list[str])
  assortment         (list[{title, desc}])   -> productkaarten
  timeline           (list[{year, title, text}]) -> generatietijdlijn
  order_note         (str)  -> bestelblok
  order_lead         (str)  -> korte regel boven het bestelblok
  route              (str)  -> wegbeschrijving onder het adres
  hours              (list[[dag, uren]])
"""
from .common import esc, build_hours_rows, maps_query as _maps_query


def _tel(phone):
    return "".join(c for c in str(phone) if c.isdigit() or c == "+")


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    tel = _tel(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    about = esc(brief.get("about", ""))
    intro = esc(brief.get("intro", "")) or about
    founded = esc(brief.get("founded", ""))
    cta = esc(brief.get("cta_text", "Kom langs in de winkel"))
    route = esc(brief.get("route", ""))
    order_lead = esc(brief.get("order_lead", ""))
    order_note = esc(brief.get("order_note", ""))
    hours_html = build_hours_rows(brief.get("hours", []))
    maps_q = _maps_query(brief.get("address", ""))

    # --- hero badge -------------------------------------------------------
    badge = ""
    if founded:
        badge = f'''<div class="seal" aria-hidden="true">
        <span class="seal-top">Bakkersfamilie sinds</span>
        <span class="seal-year">{founded}</span>
        <span class="seal-bot">Essen · Heikant</span>
      </div>'''

    # --- assortiment ------------------------------------------------------
    assortment = brief.get("assortment", [])
    assortment_section = ""
    if assortment:
        cards = "\n".join(
            f'''<article class="card">
          <h3>{esc(a.get("title", ""))}</h3>
          <p>{esc(a.get("desc", ""))}</p>
        </article>'''
            for a in assortment
        )
        assortment_section = f'''<section class="assortiment" id="assortiment">
  <div class="wrap">
    <p class="eyebrow">In de toog</p>
    <h2>Wat er elke dag klaarstaat</h2>
    <div class="cards">
      {cards}
    </div>
  </div>
</section>'''

    # --- highlights -------------------------------------------------------
    highlights = brief.get("highlights", [])
    highlights_html = ""
    if highlights:
        items = "\n".join(f"<li>{esc(h)}</li>" for h in highlights)
        highlights_html = f'<ul class="ticks">{items}</ul>'

    # --- tijdlijn ---------------------------------------------------------
    timeline = brief.get("timeline", [])
    timeline_section = ""
    if timeline:
        steps = "\n".join(
            f'''<li class="step">
          <span class="year">{esc(t.get("year", ""))}</span>
          <h3>{esc(t.get("title", ""))}</h3>
          <p>{esc(t.get("text", ""))}</p>
        </li>'''
            for t in timeline
        )
        timeline_section = f'''<section class="verhaal" id="verhaal">
  <div class="wrap">
    <p class="eyebrow light">Het verhaal</p>
    <h2>Van bakkersgast tot derde generatie</h2>
    <ol class="timeline">
      {steps}
    </ol>
  </div>
</section>'''

    # --- bestellen --------------------------------------------------------
    order_section = ""
    if order_note or email:
        mail_btn = (
            f'<a class="btn btn-solid" href="mailto:{email}">Mail je bestelling</a>'
            if email else ""
        )
        note_p = f"<p>{order_note}</p>" if order_note else ""
        lead_p = f'<p class="lead">{order_lead}</p>' if order_lead else ""
        order_section = f'''<section class="bestellen" id="bestellen">
  <div class="wrap">
    <div class="order-panel">
      <div>
        <p class="eyebrow">Op bestelling</p>
        <h2>Taart, broodjes of een ontbijtmand?</h2>
        {lead_p}
        {note_p}
      </div>
      <div class="order-actions">
        {mail_btn}
        <a class="btn btn-ghost" href="tel:{tel}">Bel {phone}</a>
      </div>
    </div>
  </div>
</section>'''

    # --- about kolom ------------------------------------------------------
    about_section = ""
    if about or highlights_html:
        about_section = f'''<section class="over" id="over">
  <div class="wrap over-grid">
    <div>
      <p class="eyebrow">Over de bakkerij</p>
      <h2>Alles vers uit eigen werkhuis</h2>
      <p class="body-lg">{about}</p>
    </div>
    <div class="over-side">
      {highlights_html}
    </div>
  </div>
</section>'''

    # --- contact ----------------------------------------------------------
    route_p = f'<p class="route">{route}</p>' if route else ""
    email_p = (
        f'<p><a class="plain" href="mailto:{email}">{email}</a></p>' if email else ""
    )

    nav_items = [("#assortiment", "Assortiment", bool(assortment)),
                 ("#verhaal", "Verhaal", bool(timeline)),
                 ("#bestellen", "Bestellen", bool(order_section)),
                 ("#bezoek", "Openingsuren", True)]
    nav_html = "\n".join(
        f'<a href="{href}">{label}</a>' for href, label, show in nav_items if show
    )

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}. {phone}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --tile:      #1d4d47;
    --tile-deep: #14332f;
    --tile-soft: #2f6b63;
    --oat:       #f2eee4;
    --oat-warm:  #e8e2d4;
    --wheat:     #c08a1e;
    --ink:       #1a221f;
    --ink-soft:  #55625d;
    --line:      #d8d2c3;
    --display: 'Newsreader', Georgia, serif;
    --body: 'Karla', system-ui, sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: var(--body);
    background: var(--oat);
    color: var(--ink);
    line-height: 1.6;
    -webkit-text-size-adjust: 100%;
    overflow-x: hidden;
  }}
  img {{ max-width: 100%; }}
  a {{ color: inherit; }}
  .wrap {{ width: 100%; max-width: 1060px; margin: 0 auto; padding: 0 22px; }}

  h1, h2, h3 {{ font-family: var(--display); font-weight: 600; letter-spacing: -0.015em; line-height: 1.12; }}
  h2 {{ font-size: clamp(1.6rem, 3.4vw, 2.3rem); margin-bottom: 14px; }}
  h3 {{ font-size: 1.12rem; margin-bottom: 6px; }}

  .eyebrow {{
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.18em;
    font-weight: 700; color: var(--tile-soft); margin-bottom: 10px;
  }}
  .eyebrow.light {{ color: var(--wheat); }}

  /* ---------- header ---------- */
  header.top {{
    position: sticky; top: 0; z-index: 40;
    background: var(--tile);
    color: var(--oat);
  }}
  header.top .wrap {{
    display: flex; align-items: center; gap: 16px;
    min-height: 60px; flex-wrap: wrap;
  }}
  .brand {{
    font-family: var(--display); font-size: 1.15rem; font-weight: 600;
    margin-right: auto; white-space: nowrap;
  }}
  nav.main {{ display: flex; gap: 4px; flex-wrap: wrap; }}
  nav.main a {{
    display: inline-flex; align-items: center; min-height: 44px;
    padding: 0 12px; text-decoration: none;
    font-size: 0.88rem; font-weight: 500;
    color: rgba(242,238,228,0.82); border-radius: 8px;
  }}
  nav.main a:hover {{ color: #fff; background: rgba(255,255,255,0.10); }}

  /* ---------- hero ---------- */
  .hero {{
    background: var(--tile);
    color: var(--oat);
    position: relative;
    padding: 56px 0 72px;
  }}
  .hero::before {{
    content: ""; position: absolute; inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,0.055) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.055) 1px, transparent 1px);
    background-size: 64px 64px;
    pointer-events: none;
  }}
  .hero .wrap {{ position: relative; display: grid; grid-template-columns: 1.35fr 0.65fr; gap: 40px; align-items: center; }}
  .hero .kicker {{
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.2em;
    font-weight: 700; color: var(--wheat); margin-bottom: 16px;
  }}
  .hero h1 {{
    font-size: clamp(2.15rem, 5.6vw, 3.5rem);
    font-weight: 500; margin-bottom: 18px; max-width: 16ch;
  }}
  .hero h1 em {{ font-style: italic; color: #f2d79a; }}
  .hero p.sub {{
    font-size: 1.05rem; color: rgba(242,238,228,0.85);
    max-width: 46ch; margin-bottom: 28px;
  }}
  .hero-btns {{ display: flex; gap: 12px; flex-wrap: wrap; }}

  .btn {{
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 48px; padding: 0 22px;
    border-radius: 4px; text-decoration: none;
    font-weight: 700; font-size: 0.94rem; letter-spacing: 0.01em;
    border: 2px solid transparent;
  }}
  .btn-solid {{ background: var(--wheat); color: #211703; }}
  .btn-solid:hover {{ background: #d69c2b; }}
  .btn-ghost {{ border-color: currentColor; }}
  .btn-ghost:hover {{ background: rgba(255,255,255,0.10); }}
  .bestellen .btn-ghost {{ color: var(--tile); }}
  .bestellen .btn-ghost:hover {{ background: rgba(29,77,71,0.08); }}

  .seal {{
    justify-self: end;
    width: 176px; height: 176px; flex: none;
    border: 2px solid var(--wheat);
    border-radius: 6px;
    transform: rotate(-4deg);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 16px; gap: 4px;
    background: rgba(0,0,0,0.14);
  }}
  .seal-top, .seal-bot {{
    font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.16em;
    font-weight: 700; color: var(--wheat);
  }}
  .seal-year {{ font-family: var(--display); font-size: 2.9rem; line-height: 1; color: var(--oat); }}

  /* ---------- secties ---------- */
  section {{ padding: 60px 0; }}
  .body-lg {{ font-size: 1.04rem; color: var(--ink-soft); }}

  .over {{ background: var(--oat); }}
  .over-grid {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 44px; align-items: start; }}
  ul.ticks {{ list-style: none; }}
  ul.ticks li {{
    position: relative; padding: 12px 0 12px 30px;
    border-bottom: 1px solid var(--line);
    font-size: 0.97rem;
  }}
  ul.ticks li:first-child {{ border-top: 1px solid var(--line); }}
  ul.ticks li::before {{
    content: ""; position: absolute; left: 4px; top: 20px;
    width: 9px; height: 9px; border-radius: 2px;
    background: var(--wheat);
  }}

  .assortiment {{ background: var(--oat-warm); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 18px; margin-top: 26px; }}
  .card {{
    background: var(--oat);
    border: 1px solid var(--line);
    border-top: 4px solid var(--tile-soft);
    border-radius: 4px;
    padding: 22px 20px;
  }}
  .card h3 {{ color: var(--tile); }}
  .card p {{ font-size: 0.94rem; color: var(--ink-soft); }}

  /* ---------- tijdlijn ---------- */
  .verhaal {{ background: var(--tile-deep); color: var(--oat); }}
  .verhaal h2 {{ color: var(--oat); }}
  ol.timeline {{
    list-style: none;
    display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 0; margin-top: 34px;
  }}
  .step {{
    position: relative;
    padding: 34px 20px 4px 0;
    border-top: 2px solid rgba(192,138,30,0.45);
  }}
  .step::before {{
    content: ""; position: absolute; top: -8px; left: 0;
    width: 14px; height: 14px; border-radius: 50%;
    background: var(--wheat);
    border: 3px solid var(--tile-deep);
  }}
  .step .year {{
    display: block; font-family: var(--display); font-size: 1.5rem;
    color: var(--wheat); line-height: 1; margin-bottom: 8px;
  }}
  .step h3 {{ color: var(--oat); font-size: 1rem; }}
  .step p {{ font-size: 0.92rem; color: rgba(242,238,228,0.74); padding-bottom: 20px; }}

  /* ---------- bestellen ---------- */
  .bestellen {{ background: var(--oat); }}
  .order-panel {{
    background: var(--oat-warm);
    border: 1px solid var(--line);
    border-left: 5px solid var(--wheat);
    border-radius: 4px;
    padding: 32px 28px;
    display: grid; grid-template-columns: 1.4fr 0.6fr; gap: 32px; align-items: center;
  }}
  .order-panel p {{ color: var(--ink-soft); font-size: 0.98rem; }}
  .order-panel p.lead {{ color: var(--ink); font-size: 1.04rem; margin-bottom: 8px; }}
  .order-actions {{ display: flex; flex-direction: column; gap: 12px; }}
  .order-actions .btn {{ width: 100%; }}

  /* ---------- bezoek ---------- */
  .bezoek {{ background: var(--tile); color: var(--oat); }}
  .bezoek h2 {{ color: var(--oat); }}
  .bezoek .wrap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 44px; }}
  .hours-row {{
    display: flex; justify-content: space-between; gap: 12px;
    padding: 11px 0;
    border-bottom: 1px solid rgba(242,238,228,0.16);
    font-size: 0.95rem;
  }}
  .hours-row:first-child {{ border-top: 1px solid rgba(242,238,228,0.16); }}
  .hours-row.closed span:last-child {{ color: var(--wheat); font-weight: 700; }}
  .bezoek p {{ color: rgba(242,238,228,0.85); margin-bottom: 8px; }}
  .bezoek .route {{ font-size: 0.9rem; color: rgba(242,238,228,0.62); margin-top: 12px; }}
  a.plain {{ color: var(--wheat); text-decoration: underline; text-underline-offset: 3px; }}
  a.map-link {{
    display: inline-flex; align-items: center; min-height: 44px;
    margin-top: 8px; font-weight: 700; font-size: 0.92rem;
    color: var(--wheat); text-decoration: none;
  }}
  a.map-link:hover {{ text-decoration: underline; }}

  footer {{
    background: var(--tile-deep); color: rgba(242,238,228,0.6);
    padding: 26px 0; text-align: center; font-size: 0.82rem;
  }}
  footer a {{ color: var(--wheat); }}

  a:focus-visible, .btn:focus-visible {{ outline: 3px solid var(--wheat); outline-offset: 3px; border-radius: 4px; }}

  @media (max-width: 860px) {{
    .hero .wrap, .over-grid, .bezoek .wrap, .order-panel {{ grid-template-columns: 1fr; }}
    .seal {{ justify-self: start; width: 150px; height: 150px; }}
    .seal-year {{ font-size: 2.4rem; }}
    .order-actions {{ flex-direction: row; flex-wrap: wrap; }}
    .order-actions .btn {{ flex: 1 1 200px; width: auto; }}
  }}
  @media (max-width: 620px) {{
    header.top .wrap {{ padding-top: 8px; padding-bottom: 8px; }}
    .brand {{ width: 100%; margin-right: 0; }}
    nav.main {{ width: 100%; }}
    nav.main a {{ padding: 0 10px; font-size: 0.84rem; }}
    section {{ padding: 46px 0; }}
    .hero {{ padding: 40px 0 52px; }}
    .hero-btns .btn {{ flex: 1 1 100%; }}
    .step {{ padding-top: 30px; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <span class="brand">{name}</span>
    <nav class="main" aria-label="Hoofdnavigatie">
      {nav_html}
    </nav>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <p class="kicker">{category}</p>
      <h1>{tagline}</h1>
      <p class="sub">{intro}</p>
      <div class="hero-btns">
        <a class="btn btn-solid" href="#bezoek">{cta}</a>
        <a class="btn btn-ghost" href="tel:{tel}">Bel {phone}</a>
      </div>
    </div>
    {badge}
  </div>
</section>

{about_section}

{assortment_section}

{timeline_section}

{order_section}

<section class="bezoek" id="bezoek">
  <div class="wrap">
    <div>
      <p class="eyebrow light">Openingsuren</p>
      <h2>Wanneer we open zijn</h2>
      {hours_html}
    </div>
    <div>
      <p class="eyebrow light">Kom langs</p>
      <h2>Waar je ons vindt</h2>
      <p>{address}</p>
      <p><a class="plain" href="tel:{tel}">{phone}</a></p>
      {email_p}
      {route_p}
      <a class="map-link" href="https://www.google.com/maps/search/?api=1&amp;query={maps_q}" target="_blank" rel="noopener">Route op Google Maps &rarr;</a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    Websiteprototype voor {name} · gemaakt door <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
  </div>
</footer>

</body>
</html>
"""
