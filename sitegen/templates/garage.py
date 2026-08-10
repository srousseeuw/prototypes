from .common import esc, build_hours_rows, build_highlights, build_list, maps_query as _maps_query

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Maak een afspraak"))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="▸")
    services_html = build_list(brief.get("services", []), item_class="service")
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --steel: #2a2e33;
    --steel-deep: #1a1d20;
    --iron: #40454c;
    --signal: #f5a300;
    --paper: #f2f2f0;
    --line: rgba(255,255,255,0.12);
    --line-dark: #3a3f45;
    --ink-soft: #6b7178;
    --font-display: 'Oswald', sans-serif;
    --font-body: 'Inter', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--steel-deep);
    line-height: 1.5;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 18px 0;
    background: var(--steel-deep);
    border-bottom: 3px solid var(--signal);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.3rem;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: #fff;
  }}
  .top-cta {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    background: var(--signal);
    color: var(--steel-deep);
    padding: 10px 18px;
    text-decoration: none;
  }}

  .hero {{
    padding: 72px 0 64px;
    background:
      repeating-linear-gradient(135deg, rgba(245,163,0,0.06) 0 3px, transparent 3px 40px),
      linear-gradient(160deg, var(--steel) 0%, var(--steel-deep) 100%);
    color: #fff;
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-family: var(--font-display);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--signal);
    font-weight: 600;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    font-weight: 700;
    text-transform: uppercase;
    line-height: 1.05;
    letter-spacing: 0.005em;
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.1rem;
    color: rgba(255,255,255,0.78);
    max-width: 42ch;
    margin-bottom: 28px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--signal);
    color: var(--steel-deep);
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    padding: 14px 28px;
    text-decoration: none;
    font-size: 0.95rem;
  }}

  .plate {{
    justify-self: end;
    background: #fff;
    color: var(--steel-deep);
    border-radius: 6px;
    padding: 22px 26px;
    width: 100%;
    max-width: 260px;
    border: 3px solid var(--steel-deep);
    box-shadow: 6px 6px 0 var(--signal);
  }}
  .plate .label {{
    font-family: var(--font-display);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--ink-soft);
    font-weight: 600;
    margin-bottom: 8px;
  }}
  .plate .big {{
    font-family: var(--font-display);
    font-size: 1.9rem;
    font-weight: 700;
    text-transform: uppercase;
    line-height: 1.15;
  }}

  section {{ padding: 56px 0; }}
  .about {{ border-top: 1px solid var(--line-dark); background: var(--paper); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.01em;
    margin-bottom: 16px;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid #ddd;
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--signal); font-weight: 700; }}

  .services {{ background: var(--steel); color: #fff; }}
  .services h2 {{ color: #fff; }}
  ul.service-list {{ list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  ul.service-list li.service {{
    font-weight: 500;
    font-size: 0.98rem;
    padding: 14px 16px;
    background: var(--steel-deep);
    border-left: 4px solid var(--signal);
  }}

  .info {{ background: var(--steel-deep); color: #fff; }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: #fff; }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--signal); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(255,255,255,0.8); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--signal);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{
    padding: 28px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--ink-soft);
    background: var(--paper);
  }}

  @media (max-width: 760px) {{
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .plate {{ justify-self: start; margin-top: 12px; max-width: none; }}
    ul.service-list {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--signal); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel de garage</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      <a class="hero-cta" href="#info">{cta}</a>
    </div>
    <div class="plate">
      <div class="label">Werkplaats</div>
      <div class="big">Vakwerk<br>op maat</div>
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
      <h2>Waarom {name}</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

<section class="services">
  <div class="wrap">
    <h2>Onze diensten</h2>
    <ul class="service-list">
      {services_html}
    </ul>
  </div>
</section>

<section class="info" id="info">
  <div class="wrap">
    <div>
      <h2>Openingsuren</h2>
      {hours_html}
    </div>
    <div class="contact-block">
      <h2>Bezoek ons</h2>
      <p>{address}</p>
      <p>{phone}</p>
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
