from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query
from . import booking as _booking

def render_extra_pages(brief: dict) -> dict:
    if not brief.get("booking_services"):
        return {}
    accent = brief.get("accent", "#9c6b4f")
    theme = {
        "bg": "#2a2724",
        "bg_deep": "#1c1a18",
        "accent": accent,
        "paper": "#faf8f5",
        "ink": "#1c1a18",
        "font_display": "'Cormorant Garamond', serif",
        "font_body": "'Manrope', sans-serif",
        "fonts_href": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400&family=Manrope:wght@400;500;600;700&display=swap",
    }
    return {"afspraak/index.html": _booking.render(brief, theme)}

def _initial(name: str) -> str:
    for ch in name:
        if ch.isalpha():
            return ch.upper()
    return "?"

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    phone_href = esc(brief.get("phone", "").replace(" ", "").replace("/", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Maak een afspraak"))
    appointment_note = esc(brief.get("appointment_note", "Enkel op afspraak"))
    accent = esc(brief.get("accent", "#9c6b4f"))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="✂")
    maps_q = _maps_query(address)
    monogram = esc(_initial(brief["business_name"]))

    # Met behandelingen in de brief wordt online boeken de hoofdactie.
    boekbaar = bool(brief.get("booking_services"))
    boek_href = f'/{esc(brief["slug"])}/afspraak/'
    if boekbaar:
        top_cta = f'<a class="top-cta" href="{boek_href}">Afspraak maken</a>'
        hero_ctas = (
            f'<a class="hero-cta" href="{boek_href}">Boek online</a>\n'
            f'        <a class="hero-cta ghost" href="tel:{phone_href}">Of bel ons</a>'
        )
    else:
        top_cta = f'<a class="top-cta" href="tel:{phone_href}">Bel voor afspraak</a>'
        hero_ctas = (
            f'<a class="hero-cta" href="tel:{phone_href}">{cta}</a>\n'
            f'        <a class="hero-cta ghost" href="#info">Openingsuren &amp; adres</a>'
        )

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #161513;
    --ink-soft: #8a857c;
    --paper: #f6f4f0;
    --panel: #201f1c;
    --line: rgba(22,21,19,0.12);
    --line-dark: rgba(246,244,240,0.14);
    --accent: {accent};
    --font-display: 'Cormorant Garamond', serif;
    --font-body: 'Manrope', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.55;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1060px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 22px 0;
    border-bottom: 1px solid var(--line);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    display: flex; align-items: center; gap: 12px;
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.3rem;
    letter-spacing: 0.01em;
  }}
  .brand .mono {{
    width: 34px; height: 34px;
    border: 1px solid var(--ink);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
    color: var(--accent);
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    border: 1px solid var(--ink);
    color: var(--ink);
    padding: 10px 20px;
    border-radius: 2px;
    text-decoration: none;
    transition: background 0.15s ease, color 0.15s ease;
  }}
  .top-cta:hover {{ background: var(--ink); color: var(--paper); }}

  .hero {{
    padding: 96px 0 88px;
    position: relative;
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.05fr 0.95fr;
    gap: 56px;
    align-items: center;
  }}
  .eyebrow {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.24em;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 20px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.8rem, 5.6vw, 4.4rem);
    font-weight: 600;
    font-style: italic;
    line-height: 1.04;
    letter-spacing: 0;
    margin-bottom: 22px;
  }}
  .tagline {{
    font-size: 1.08rem;
    color: var(--ink-soft);
    max-width: 40ch;
    margin-bottom: 30px;
  }}
  .appointment-note {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 30px;
  }}
  .appointment-note::before {{
    content: "";
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
  }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 14px; }}
  .hero-cta {{
    display: inline-block;
    background: var(--ink);
    color: var(--paper);
    font-weight: 600;
    padding: 15px 30px;
    border-radius: 2px;
    text-decoration: none;
    font-size: 0.92rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }}
  .hero-cta.ghost {{
    background: transparent;
    color: var(--ink);
    border: 1px solid var(--ink);
  }}

  .signature {{
    justify-self: end;
    width: 260px;
    aspect-ratio: 1;
    border-radius: 50%;
    border: 1px solid var(--line);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }}
  .signature::before {{
    content: "";
    position: absolute;
    inset: 22px;
    border: 1px solid var(--accent);
    border-radius: 50%;
  }}
  .signature .letter {{
    font-family: var(--font-display);
    font-style: italic;
    font-size: 6.5rem;
    font-weight: 600;
    color: var(--ink);
  }}

  section {{ padding: 64px 0; }}
  .about {{ border-top: 1px solid var(--line); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 56px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 600;
    font-style: italic;
    margin-bottom: 18px;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.03rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--accent); font-weight: 700; }}

  .info {{ background: var(--panel); color: var(--paper); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 56px;
  }}
  .info h2 {{ color: var(--paper); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid var(--line-dark);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--accent); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(246,244,240,0.82); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 16px;
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
    font-size: 0.9rem;
    letter-spacing: 0.02em;
  }}
  .contact-block .phone-link {{
    font-family: var(--font-display);
    font-style: italic;
    font-size: 1.5rem;
    color: var(--paper);
    text-decoration: none;
    display: inline-block;
    margin-bottom: 6px;
  }}

  footer {{
    padding: 30px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--ink-soft);
  }}

  @media (max-width: 760px) {{
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .signature {{ justify-self: start; margin-top: 8px; width: 190px; }}
    .signature .letter {{ font-size: 4.6rem; }}
  }}

  a:focus-visible, .hero-cta:focus-visible, .top-cta:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand"><span class="mono">{monogram}</span>{name}</div>
    {top_cta}
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      <div class="appointment-note">{appointment_note}</div>
      <div class="hero-actions">
        {hero_ctas}
      </div>
    </div>
    <div class="signature">
      <span class="letter">{monogram}</span>
    </div>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Over {name}</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Wat we bieden</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

<section class="info" id="info">
  <div class="wrap">
    <div>
      <h2>Openingsuren</h2>
      {hours_html}
    </div>
    <div class="contact-block">
      <h2>Maak een afspraak</h2>
      <a class="phone-link" href="tel:{phone_href}">{phone}</a>
      <p>{address}</p>
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
