from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def _build_specialties(items):
    lis = [f'<li><span class="cut"></span>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Kom langs in de winkel"))
    since = esc(brief.get("since", ""))
    note = esc(brief.get("note", ""))
    rating = brief.get("rating")
    rating_count = brief.get("rating_count")
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="▸")
    specialties_html = _build_specialties(brief.get("specialties", []))
    maps_q = _maps_query(address)

    rating_block = ""
    if rating:
        rating_block = f'''<div class="rating">
            <span class="stars">★★★★★</span>
            <span class="rating-text">{rating} / 5 — {rating_count or ""} beoordelingen</span>
        </div>'''

    note_block = ""
    if note:
        note_block = f'<p class="note">{note}</p>'

    stamp_block = ""
    if since:
        stamp_block = f'''<div class="stamp">
      <span class="cleaver" aria-hidden="true">
        <svg viewBox="0 0 64 64" width="34" height="34" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 40 L44 14 C50 10 58 14 58 22 C58 28 54 32 48 34 L14 50 Z" fill="currentColor"/>
          <rect x="4" y="46" width="20" height="6" rx="2" fill="currentColor"/>
        </svg>
      </span>
      <div class="small">Vakmanschap sinds</div>
      <div class="big">{since}</div>
    </div>'''
    else:
        stamp_block = '''<div class="stamp">
      <span class="cleaver" aria-hidden="true">
        <svg viewBox="0 0 64 64" width="34" height="34" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 40 L44 14 C50 10 58 14 58 22 C58 28 54 32 48 34 L14 50 Z" fill="currentColor"/>
          <rect x="4" y="46" width="20" height="6" rx="2" fill="currentColor"/>
        </svg>
      </span>
      <div class="small">Ambachtelijke</div>
      <div class="big">Slagerij</div>
    </div>'''

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --wood: #3b271b;
    --wood-deep: #241812;
    --meat: #8a2e2e;
    --meat-deep: #6c2222;
    --cream: #f6ece0;
    --marble: #ead9c2;
    --line: #ddc9ab;
    --ink-soft: #5c4a3a;
    --font-display: 'Zilla Slab', serif;
    --font-body: 'Work Sans', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--cream);
    color: var(--wood-deep);
    line-height: 1.5;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 20px 0;
    background: var(--wood-deep);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.3rem;
    letter-spacing: -0.01em;
    color: var(--cream);
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--meat);
    color: var(--cream);
    padding: 10px 18px;
    border-radius: 3px;
    text-decoration: none;
  }}

  .hero {{
    padding: 68px 0 60px;
    background:
      linear-gradient(180deg, rgba(59,39,27,0.04) 0%, rgba(59,39,27,0) 40%),
      var(--marble);
    border-bottom: 1px solid var(--line);
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--meat);
    font-weight: 600;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.3rem, 5vw, 3.5rem);
    font-weight: 700;
    line-height: 1.06;
    letter-spacing: -0.01em;
    margin-bottom: 18px;
    color: var(--wood-deep);
  }}
  .tagline {{
    font-size: 1.12rem;
    color: var(--ink-soft);
    max-width: 44ch;
    margin-bottom: 22px;
  }}
  .note {{
    font-size: 0.92rem;
    color: var(--ink-soft);
    background: rgba(138,46,46,0.08);
    border-left: 3px solid var(--meat);
    padding: 10px 14px;
    margin-bottom: 22px;
    max-width: 44ch;
  }}
  .rating {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 26px;
    font-size: 0.92rem;
  }}
  .stars {{ color: var(--meat); letter-spacing: 2px; }}
  .rating-text {{ color: var(--ink-soft); }}
  .hero-cta {{
    display: inline-block;
    background: var(--meat);
    color: var(--cream);
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 3px;
    text-decoration: none;
    font-size: 0.98rem;
  }}

  .stamp {{
    justify-self: end;
    width: 190px; height: 190px;
    background: var(--wood-deep);
    color: var(--cream);
    border: 2px solid var(--meat);
    border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    transform: rotate(4deg);
    font-family: var(--font-display);
    padding: 18px;
  }}
  .stamp .cleaver {{ color: var(--meat); margin-bottom: 8px; }}
  .stamp .small {{ font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--marble); font-weight: 600; margin-bottom: 4px; }}
  .stamp .big {{ font-size: 1.35rem; font-weight: 700; line-height: 1.1; }}

  section {{ padding: 56px 0; }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 16px;
    color: var(--wood-deep);
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--meat); font-weight: 700; }}

  .specialties {{ background: var(--wood-deep); color: var(--cream); }}
  .specialties h2 {{ color: var(--cream); }}
  ul.spec-list {{
    list-style: none;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 10px;
  }}
  ul.spec-list li {{
    display: flex; align-items: center; gap: 12px;
    font-size: 1rem;
    padding: 12px 14px;
    background: rgba(246,236,224,0.06);
    border-left: 4px solid var(--meat);
  }}
  .cut {{
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--meat);
    flex-shrink: 0;
  }}

  .info {{ background: var(--marble); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--meat); font-weight: 600; }}
  .contact-block p {{ margin-bottom: 10px; color: var(--ink-soft); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--meat);
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
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .stamp {{ justify-self: start; margin-top: 12px; }}
    ul.spec-list {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--meat); outline-offset: 3px; }}
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
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      {note_block}
      {rating_block}
      <a class="hero-cta" href="#info">{cta}</a>
    </div>
    {stamp_block}
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

<section class="specialties">
  <div class="wrap">
    <h2>Ons assortiment</h2>
    <ul class="spec-list">
      {specialties_html}
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
