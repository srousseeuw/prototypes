from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

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

    rating_block = ""
    if rating:
        rating_block = f'''<div class="rating">
            <span class="stars">★★★★★</span>
            <span class="rating-text">{rating} / 5 — {rating_count or ""} beoordelingen</span>
        </div>'''

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
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--brass-bright); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name} <span>·</span></div>
    <a class="top-cta" href="tel:{phone}">Bel het café</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      {rating_block}
      <a class="hero-cta" href="#info">{cta}</a>
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

<section class="info" id="info">
  <div class="wrap">
    <div>
      <h2>Openingsuren</h2>
      {hours_html}
    </div>
    <div class="contact-block">
      <h2>Kom langs</h2>
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
