from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Kom langs"))
    accent = brief.get("accent", "#e07a1f")
    rating = brief.get("rating")
    rating_count = brief.get("rating_count")
    hours = brief.get("hours", [])
    hours_html = build_hours_rows(hours) if hours else ""
    highlights_html = build_highlights(brief.get("highlights", []), mark="🍟")
    maps_q = _maps_query(address) if address else ""

    rating_block = ""
    if rating:
        rating_block = f'''<div class="rating">
            <span class="stars">★★★★★</span>
            <span class="rating-text">{rating} / 5{f" — {rating_count} beoordelingen" if rating_count else ""}</span>
        </div>'''

    hours_section = ""
    if hours_html:
        hours_section = f'''<div>
      <h2>Openingsuren</h2>
      {hours_html}
    </div>'''
    else:
        hours_section = '''<div>
      <h2>Openingsuren</h2>
      <p class="hours-note">Bel even voor de actuele uren.</p>
    </div>'''

    contact_lines = f'<p>{address}</p>' if address else ""
    contact_lines += f'<p>{phone}</p>' if phone else ""
    map_link = ""
    if maps_q:
        map_link = f'<a class="map-link" href="https://www.google.com/maps/search/?api=1&query={maps_q}" target="_blank" rel="noopener">Bekijk op kaart →</a>'

    top_cta = f'<a class="top-cta" href="tel:{phone}">Bel de frituur</a>' if phone else ""

    online_order_note = esc(brief.get("online_order_teaser", ""))
    online_order_block = ""
    if online_order_note:
        online_order_block = f'''<a class="hero-cta hero-cta-outline" href="#info">
        <span class="soon-badge">Binnenkort</span> Bestel online
      </a>'''

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --fry: {accent};
    --paper-bag: #f6ead4;
    --paper-bag-deep: #ecdcb8;
    --grease: #2c231a;
    --cone: #1f2a1f;
    --cone-line: rgba(246,234,212,0.14);
    --sauce: #c23b22;
    --ink-soft: #5c5142;
    --font-display: 'Fredoka', sans-serif;
    --font-body: 'Work Sans', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper-bag);
    color: var(--grease);
    line-height: 1.5;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 18px 0;
    border-bottom: 3px dashed var(--paper-bag-deep);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--grease);
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--fry);
    color: #fff;
    padding: 10px 20px;
    border-radius: 999px;
    text-decoration: none;
  }}

  .hero {{
    padding: 60px 0 56px;
    background:
      repeating-linear-gradient(90deg, var(--paper-bag-deep) 0 3px, transparent 3px 26px),
      var(--paper-bag);
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
    letter-spacing: 0.1em;
    color: var(--sauce);
    font-weight: 600;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.3rem, 5vw, 3.4rem);
    font-weight: 700;
    line-height: 1.08;
    margin-bottom: 18px;
    color: var(--grease);
  }}
  .tagline {{
    font-size: 1.1rem;
    color: var(--ink-soft);
    max-width: 42ch;
    margin-bottom: 26px;
  }}
  .rating {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 26px;
    font-size: 0.92rem;
  }}
  .stars {{ color: var(--fry); letter-spacing: 2px; }}
  .rating-text {{ color: var(--ink-soft); }}
  .hero-cta {{
    display: inline-block;
    background: var(--sauce);
    color: #fff;
    font-family: var(--font-display);
    font-weight: 600;
    padding: 14px 30px;
    border-radius: 999px;
    text-decoration: none;
    font-size: 1rem;
  }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 10px; }}
  .hero-cta-outline {{
    background: transparent;
    color: var(--grease);
    border: 2px solid var(--grease);
    padding: 12px 24px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }}
  .soon-badge {{
    background: var(--fry);
    color: #fff;
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 9px;
    border-radius: 999px;
  }}
  .online-order-note {{ font-size: 0.88rem; color: var(--ink-soft); margin-bottom: 26px; }}

  .cone {{
    justify-self: end;
    width: 200px;
    height: 240px;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
  }}
  .cone::before {{
    content: "";
    position: absolute;
    bottom: 0;
    width: 0;
    height: 0;
    border-left: 90px solid transparent;
    border-right: 90px solid transparent;
    border-bottom: 190px solid var(--paper-bag-deep);
    filter: drop-shadow(0 6px 10px rgba(44,35,26,0.18));
  }}
  .cone .fries {{
    position: relative;
    z-index: 1;
    margin-bottom: 150px;
    display: flex;
    gap: 5px;
  }}
  .cone .fry-stick {{
    width: 10px;
    background: var(--fry);
    border-radius: 3px 3px 0 0;
  }}
  .cone .fry-stick:nth-child(1) {{ height: 90px; transform: rotate(-8deg); }}
  .cone .fry-stick:nth-child(2) {{ height: 110px; transform: rotate(-2deg); }}
  .cone .fry-stick:nth-child(3) {{ height: 100px; transform: rotate(4deg); }}
  .cone .fry-stick:nth-child(4) {{ height: 80px; transform: rotate(10deg); }}
  .cone .label {{
    position: absolute;
    bottom: 20px;
    z-index: 2;
    font-family: var(--font-display);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--grease);
    font-weight: 600;
    background: rgba(255,255,255,0.55);
    padding: 4px 10px;
    border-radius: 999px;
  }}

  section {{ padding: 52px 0; }}
  .about {{ border-top: 3px dashed var(--paper-bag-deep); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--grease);
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px; align-items: baseline;
    padding: 10px 0;
    border-bottom: 1px solid var(--paper-bag-deep);
    font-size: 0.98rem;
  }}
  .mark {{ font-weight: 700; }}

  .info {{ background: var(--cone); color: var(--paper-bag); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--paper-bag); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--cone-line);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--fry); }}
  .hours-note {{ color: rgba(246,234,212,0.75); font-size: 0.94rem; }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(246,234,212,0.85); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--fry);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{
    padding: 26px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--ink-soft);
  }}

  @media (max-width: 760px) {{
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .cone {{ justify-self: start; margin-top: 12px; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--sauce); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
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
        {online_order_block}
      </div>
      {f'<p class="online-order-note">{online_order_note}</p>' if online_order_note else ""}
    </div>
    <div class="cone">
      <div class="label">Vers gebakken</div>
      <div class="fries">
        <div class="fry-stick"></div>
        <div class="fry-stick"></div>
        <div class="fry-stick"></div>
        <div class="fry-stick"></div>
      </div>
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
      <h2>Wat je vindt</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

<section class="info" id="info">
  <div class="wrap">
    {hours_section}
    <div class="contact-block">
      <h2>Kom langs</h2>
      {contact_lines}
      {map_link}
    </div>
  </div>
</section>

<footer>
  Prototype gebouwd voor {name} · <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
</footer>

</body>
</html>
"""
