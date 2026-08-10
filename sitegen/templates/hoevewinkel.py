from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def _build_products(items):
    lis = [f'<li class="crate">{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Kom langs"))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="✚")
    products_html = _build_products(brief.get("products", []))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --field: #566b3e;
    --field-deep: #3d4d2b;
    --straw: #e8c877;
    --hay: #f3ead4;
    --barn-red: #9a4530;
    --soil: #2e2418;
    --ink-soft: #5a5040;
    --line: #d9cba3;
    --font-hand: 'Caveat', cursive;
    --font-display: 'Fraunces', serif;
    --font-body: 'Nunito Sans', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--hay);
    color: var(--soil);
    line-height: 1.55;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 18px 0;
    background: var(--field-deep);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--hay);
    letter-spacing: -0.01em;
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 700;
    font-size: 0.88rem;
    background: var(--straw);
    color: var(--soil);
    padding: 9px 18px;
    border-radius: 6px;
    text-decoration: none;
  }}

  .hero {{
    padding: 60px 0 48px;
    background:
      radial-gradient(ellipse at 85% -10%, rgba(232,200,119,0.35), transparent 55%),
      var(--field);
    color: var(--hay);
    border-bottom: 8px solid var(--soil);
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 40px;
    align-items: center;
  }}
  .eyebrow {{
    display: inline-block;
    font-family: var(--font-hand);
    font-size: 1.6rem;
    color: var(--straw);
    transform: rotate(-2deg);
    margin-bottom: 6px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 4.6vw, 3.3rem);
    font-weight: 700;
    line-height: 1.08;
    letter-spacing: -0.01em;
    margin-bottom: 16px;
  }}
  .tagline {{
    font-size: 1.08rem;
    color: rgba(243,234,212,0.9);
    max-width: 44ch;
    margin-bottom: 26px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--barn-red);
    color: var(--hay);
    font-weight: 700;
    padding: 13px 26px;
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.98rem;
    border: 2px solid var(--soil);
  }}
  .open-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 22px;
    font-size: 0.9rem;
    background: rgba(46,36,24,0.35);
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px dashed rgba(243,234,212,0.5);
  }}
  .open-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--straw); }}

  .board {{
    background: var(--soil);
    color: var(--hay);
    border-radius: 10px;
    padding: 26px 24px;
    transform: rotate(1.5deg);
    box-shadow: 0 14px 0 rgba(0,0,0,0.15);
    border: 6px solid #4a3a26;
  }}
  .board .board-title {{
    font-family: var(--font-hand);
    font-size: 1.7rem;
    color: var(--straw);
    margin-bottom: 10px;
    transform: rotate(-1deg);
  }}
  ul.crates {{ list-style: none; }}
  .crate {{
    font-family: var(--font-hand);
    font-size: 1.3rem;
    padding: 4px 0;
    border-bottom: 1px dashed rgba(243,234,212,0.25);
  }}
  .crate:last-child {{ border-bottom: none; }}

  section {{ padding: 52px 0; }}
  .about {{ border-bottom: 1px solid var(--line); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 44px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 700;
    margin-bottom: 14px;
    color: var(--field-deep);
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--barn-red); font-weight: 700; }}

  .info {{ background: var(--field-deep); color: var(--hay); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 44px;
  }}
  .info h2 {{ color: var(--straw); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(243,234,212,0.15);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--straw); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(243,234,212,0.88); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--straw);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{
    padding: 26px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--ink-soft);
    background: var(--hay);
  }}

  @media (max-width: 760px) {{
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .board {{ transform: none; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--straw); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel de hoeve</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <div class="open-badge"><span class="open-dot"></span> Elke dag open van 7 tot 22 uur</div>
      <p class="tagline">{about}</p>
      <a class="hero-cta" href="#info">{cta}</a>
    </div>
    <div class="board">
      <div class="board-title">Vandaag in de winkel</div>
      <ul class="crates">
        {products_html}
      </ul>
    </div>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Recht van bij de boer</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Wat je hier vindt</h2>
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
      <h2>Bezoek de hoeve</h2>
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
