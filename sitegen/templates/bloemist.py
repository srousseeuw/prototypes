from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def _build_offerings(items):
    lis = [f'<li class="offer">{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Neem contact op"))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="✿")
    offerings_html = _build_offerings(brief.get("offerings", []))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Manrope:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #262a24;
    --leafgreen: #2f5233;
    --leafgreen-deep: #1f3a24;
    --bloom: #d5487a;
    --bloom-soft: #f4dae4;
    --paper: #ffffff;
    --mist: #f7f8f4;
    --line: #e4e6dd;
    --ink-soft: #5b6058;
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
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 22px 0;
    border-bottom: 1px solid var(--line);
  }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-style: italic;
    font-size: 1.5rem;
    color: var(--leafgreen-deep);
  }}
  .top-cta {{
    font-weight: 600;
    font-size: 0.85rem;
    background: var(--bloom);
    color: #fff;
    padding: 10px 20px;
    border-radius: 999px;
    text-decoration: none;
  }}

  .hero {{
    padding: 80px 0 64px;
    background: linear-gradient(135deg, var(--mist) 0%, var(--bloom-soft) 130%);
  }}
  .hero .wrap {{ max-width: 640px; text-align: center; margin: 0 auto; }}
  .eyebrow {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--bloom);
    font-weight: 600;
    margin-bottom: 18px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-weight: 600;
    font-style: italic;
    font-size: clamp(2.4rem, 6vw, 3.8rem);
    line-height: 1.1;
    color: var(--leafgreen-deep);
    margin-bottom: 20px;
  }}
  .tagline {{
    font-size: 1.1rem;
    color: var(--ink-soft);
    margin-bottom: 32px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--leafgreen-deep);
    color: #fff;
    font-weight: 600;
    padding: 14px 32px;
    border-radius: 999px;
    text-decoration: none;
    font-size: 0.98rem;
  }}

  section {{ padding: 60px 0; }}

  .offerings {{ border-bottom: 1px solid var(--line); }}
  .offerings h2 {{ text-align: center; margin-bottom: 32px; }}
  .offer-grid {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }}
  .offer {{
    text-align: center;
    padding: 26px 12px;
    border: 1px solid var(--line);
    border-radius: 10px;
    font-family: var(--font-display);
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--leafgreen-deep);
    background: var(--mist);
  }}

  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--leafgreen-deep);
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.03rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 12px;
    padding: 11px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--bloom); font-weight: 700; }}

  .info {{ background: var(--leafgreen-deep); color: #fff; }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--bloom-soft); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--bloom); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(255,255,255,0.85); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--bloom-soft);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{
    padding: 28px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--ink-soft);
  }}

  @media (max-width: 760px) {{
    .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .offer-grid {{ grid-template-columns: 1fr 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--bloom); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel de winkel</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="eyebrow">{category}</div>
    <h1>{tagline}</h1>
    <p class="tagline">{about}</p>
    <a class="hero-cta" href="#info">{cta}</a>
  </div>
</section>

<section class="offerings">
  <div class="wrap">
    <h2>Wat we bieden</h2>
    <ul class="offer-grid">
      {offerings_html}
    </ul>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Ons verhaal</h2>
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
