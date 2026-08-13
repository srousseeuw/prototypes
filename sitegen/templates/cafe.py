from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query
from . import zaal as _zaal

_MAANDEN = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]

def _theme(brief):
    accent = brief.get("accent", "#b5793a")
    return {
        "bg": "#241712",
        "bg_deep": "#17100c",
        "accent": accent,
        "accent_bright": "#d9a94f",
        "paper": "#efe3cd",
        "ink": "#241712",
        "font_display": "'Bitter', serif",
        "font_body": "'Karla', sans-serif",
        "fonts_href": "https://fonts.googleapis.com/css2?family=Bitter:wght@500;600;700;800&family=Karla:wght@400;500;600;700&display=swap",
    }

def render_extra_pages(brief: dict) -> dict:
    if not brief.get("room_booking"):
        return {}
    return {"zaal/index.html": _zaal.render(brief, _theme(brief))}

def _build_events(events):
    """Bouwt de agendaregels. Datum verwacht 'DD/MM' of 'DD/MM/JJJJ'."""
    rijen = []
    for ev in events:
        datum = str(ev.get("date", ""))
        dag, maand = "", ""
        delen = datum.split("/")
        if len(delen) >= 2 and delen[0].isdigit() and delen[1].isdigit():
            dag = str(int(delen[0]))
            m = int(delen[1])
            maand = _MAANDEN[m - 1] if 1 <= m <= 12 else ""
        tijd = esc(ev.get("time", ""))
        tijd_html = f'<span class="ev-time">{tijd}</span>' if tijd else ""
        desc = esc(ev.get("desc", ""))
        desc_html = f'<span class="ev-desc">{desc}</span>' if desc else ""
        soort = esc(ev.get("kind", ""))
        soort_html = f'<span class="ev-kind">{soort}</span>' if soort else "<span></span>"
        rijen.append(f"""        <li>
          <span class="ev-date">
            <span class="ev-day">{esc(dag)}</span>
            <span class="ev-month">{esc(maand)}</span>
            {tijd_html}
          </span>
          <span>
            <span class="ev-title">{esc(ev.get('title', ''))}</span>
            {desc_html}
          </span>
          {soort_html}
        </li>""")
    return "\n".join(rijen)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Kom gezellig langs"))
    accent = esc(brief.get("accent", "#b5793a"))
    signature = esc(brief.get("signature_word", "Proost"))
    rating = brief.get("rating")
    rating_count = brief.get("rating_count")
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="🍺")
    maps_q = _maps_query(address)

    # Zonder telefoonnummer geen dode tel:-knop en geen lege regel tonen.
    top_cta = f'<a class="top-cta" href="tel:{phone}">Bel het café</a>' if phone else ""
    phone_line = f'<p>{phone}</p>' if phone else ""

    rating_block = ""
    if rating:
        rating_block = f'''<div class="rating">
            <span class="stars">★★★★★</span>
            <span class="rating-text">{rating} / 5 — {rating_count or ""} beoordelingen</span>
        </div>'''

    # Agenda en zaalverhuur zijn optioneel: alleen tonen als de brief ze bevat.
    agenda_section = ""
    events = brief.get("agenda_events", [])
    if events:
        agenda_note = ""
        if not brief.get("agenda_verified", True):
            agenda_note = ('<p class="agenda-note">Voorbeeldagenda — hier komen de echte data en namen '
                           'zodra het café ze doorgeeft.</p>')
        agenda_lead = esc(brief.get("agenda_lead", "Wat er de komende weken op het programma staat."))
        agenda_section = f"""<section class="agenda" id="agenda">
  <div class="wrap">
    <h2>Op het programma</h2>
    <p class="lead">{agenda_lead}</p>
    {agenda_note}
    <ul class="events">
{_build_events(events)}
    </ul>
  </div>
</section>"""

    zaal_link = ""
    if brief.get("room_booking"):
        zaal_link = f'<a class="hero-cta ghost" href="/{esc(brief["slug"])}/zaal/">Zaal reserveren</a>'

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;600;700;800&family=Karla:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --oak: #241712;
    --oak-deep: #17100c;
    --stout: #3a271c;
    --foam: #f4ead9;
    --paper: #efe3cd;
    --brass: {accent};
    --brass-bright: #d9a94f;
    --line: rgba(244,234,217,0.14);
    --line-dark: rgba(36,23,18,0.14);
    --ink-soft: #5a4a3c;
    --font-display: 'Bitter', serif;
    --font-body: 'Karla', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--oak);
    line-height: 1.55;
    background-image:
      repeating-linear-gradient(90deg, rgba(36,23,18,0.025) 0 2px, transparent 2px 26px);
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 18px 0;
    background: var(--oak);
    border-bottom: 3px solid var(--brass);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 1.3rem;
    letter-spacing: 0.01em;
    color: var(--foam);
  }}
  .brand span {{ color: var(--brass-bright); }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 700;
    font-size: 0.88rem;
    background: var(--brass);
    color: var(--oak-deep);
    padding: 10px 20px;
    border-radius: 2px;
    text-decoration: none;
    letter-spacing: 0.02em;
  }}

  .hero {{
    padding: 68px 0 60px;
    background:
      radial-gradient(ellipse at 80% 0%, rgba(217,169,79,0.10), transparent 55%),
      linear-gradient(180deg, var(--oak) 0%, var(--stout) 100%);
    color: var(--foam);
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--brass-bright);
    font-weight: 700;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.3rem, 5vw, 3.4rem);
    font-weight: 700;
    line-height: 1.08;
    letter-spacing: -0.01em;
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.1rem;
    color: rgba(244,234,217,0.82);
    max-width: 42ch;
    margin-bottom: 26px;
  }}
  .rating {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 26px;
    font-size: 0.92rem;
  }}
  .stars {{ color: var(--brass-bright); letter-spacing: 2px; }}
  .rating-text {{ color: rgba(244,234,217,0.7); }}
  .hero-cta {{
    display: inline-block;
    background: var(--brass);
    color: var(--oak-deep);
    font-weight: 700;
    padding: 14px 30px;
    border-radius: 2px;
    text-decoration: none;
    font-size: 0.98rem;
    letter-spacing: 0.02em;
  }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; }}
  .hero-cta.ghost {{
    background: transparent;
    color: var(--foam);
    border: 2px solid rgba(244,234,217,0.45);
    padding: 12px 26px;
  }}
  .hero-cta.ghost:hover {{ border-color: var(--foam); background: rgba(244,234,217,0.1); }}

  .tap {{
    justify-self: end;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, var(--stout), var(--oak-deep) 70%);
    border: 3px solid var(--brass);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    font-family: var(--font-display);
    padding: 18px;
    box-shadow: inset 0 0 0 6px rgba(217,169,79,0.08);
  }}
  .tap .small {{ font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--brass-bright); font-weight: 700; margin-bottom: 8px; }}
  .tap .big {{ font-size: 1.5rem; font-weight: 700; line-height: 1.15; color: var(--foam); }}

  section {{ padding: 56px 0; }}
  .about {{ border-top: 1px solid var(--line-dark); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 700;
    margin-bottom: 16px;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 12px; align-items: baseline;
    padding: 10px 0;
    border-bottom: 1px solid var(--line-dark);
    font-size: 0.98rem;
  }}
  .mark {{ font-weight: 700; }}

  /* Agenda — alleen zichtbaar als de brief evenementen bevat. */
  .agenda {{ background: var(--stout); color: var(--foam); }}
  .agenda h2 {{ color: var(--foam); margin-bottom: 6px; }}
  .agenda .lead {{ color: rgba(244,234,217,0.7); font-size: 0.95rem; margin-bottom: 26px; }}
  .agenda-note {{
    font-size: 0.84rem;
    color: var(--brass-bright);
    border-left: 3px solid var(--brass-bright);
    padding-left: 12px;
    margin-bottom: 24px;
  }}
  ul.events {{ list-style: none; display: grid; gap: 10px; }}
  ul.events li {{
    display: grid;
    grid-template-columns: 74px 1fr auto;
    gap: 18px;
    align-items: center;
    background: rgba(244,234,217,0.05);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px 18px;
  }}
  .ev-date {{
    text-align: center;
    font-family: var(--font-display);
    line-height: 1.05;
  }}
  .ev-day {{ display: block; font-size: 1.6rem; font-weight: 800; color: var(--brass-bright); }}
  .ev-month {{ display: block; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(244,234,217,0.7); }}
  .ev-title {{ display: block; font-weight: 700; font-size: 1.02rem; }}
  .ev-desc {{ display: block; color: rgba(244,234,217,0.72); font-size: 0.9rem; margin-top: 2px; }}
  .ev-kind {{
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--oak);
    background: var(--brass-bright);
    border-radius: 999px;
    padding: 4px 12px;
    white-space: nowrap;
  }}
  .ev-time {{ display: block; font-size: 0.82rem; color: rgba(244,234,217,0.6); margin-top: 5px; text-align: center; }}

  .info {{ background: var(--oak); color: var(--foam); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--foam); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--brass-bright); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(244,234,217,0.82); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--brass-bright);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{
    padding: 28px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--ink-soft);
    border-top: 1px solid var(--line-dark);
  }}

  @media (max-width: 760px) {{
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .tap {{ justify-self: start; margin-top: 12px; }}
    ul.events li {{ grid-template-columns: 58px 1fr; row-gap: 8px; }}
    .ev-kind {{ grid-column: 2; justify-self: start; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--brass-bright); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name} <span>·</span></div>
    {top_cta}
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      {rating_block}
      <div class="hero-actions">
        <a class="hero-cta" href="#info">{cta}</a>
        {zaal_link}
      </div>
    </div>
    <div class="tap">
      <div class="small">Op het terras</div>
      <div class="big">{signature}</div>
    </div>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Waarom {name}</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Wat je er vindt</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

{agenda_section}

<section class="info" id="info">
  <div class="wrap">
    <div>
      <h2>Openingsuren</h2>
      {hours_html}
    </div>
    <div class="contact-block">
      <h2>Kom langs</h2>
      <p>{address}</p>
      {phone_line}
      <a class="map-link" href="https://www.google.com/maps/search/?api=1&query={maps_q}" target="_blank" rel="noopener">Bekijk op kaart →</a>
    </div>
  </div>
</section>

<footer>
  Prototype gebouwd voor {name} · <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
</footer>

</body>
</html>
"""
