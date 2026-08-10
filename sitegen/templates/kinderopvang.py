from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Neem contact op"))
    since = esc(brief.get("since", ""))
    capacity = esc(brief.get("capacity", ""))
    supervision = esc(brief.get("supervision", ""))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="●")
    maps_q = _maps_query(address)

    badge_block = ""
    if since:
        badge_block = f'''<div class="badge">
            <div class="badge-label">Erkend sinds</div>
            <div class="badge-year">{since}</div>
            <div class="badge-sub">{supervision}</div>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700&family=Nunito+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --sun: #f2a341;
    --sun-soft: #fdecd2;
    --sky: #5b93a8;
    --sky-deep: #3a6779;
    --coral: #e8735a;
    --cream: #fffaf2;
    --ink: #3a3530;
    --ink-soft: #6f6a62;
    --line: #ece2cf;
    --font-display: 'Quicksand', sans-serif;
    --font-body: 'Nunito Sans', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--cream);
    color: var(--ink);
    line-height: 1.6;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 20px 0;
  }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.35rem;
    color: var(--sky-deep);
  }}
  .top-cta {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--coral);
    color: #fff;
    padding: 10px 20px;
    border-radius: 20px;
    text-decoration: none;
  }}

  .hero {{
    padding: 56px 0 64px;
    position: relative;
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
    color: var(--coral);
    font-weight: 700;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 4.8vw, 3.2rem);
    font-weight: 700;
    line-height: 1.15;
    color: var(--sky-deep);
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.1rem;
    color: var(--ink-soft);
    max-width: 42ch;
    margin-bottom: 28px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--sky-deep);
    color: #fff;
    font-family: var(--font-display);
    font-weight: 600;
    padding: 14px 30px;
    border-radius: 24px;
    text-decoration: none;
    font-size: 1rem;
  }}

  .badge {{
    justify-self: end;
    width: 200px; height: 200px;
    background: var(--sun-soft);
    border-radius: 50%;
    border: 6px solid var(--sun);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    padding: 20px;
  }}
  .badge-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--sky-deep); font-weight: 700; margin-bottom: 4px; }}
  .badge-year {{ font-family: var(--font-display); font-size: 2.2rem; font-weight: 700; color: var(--coral); line-height: 1; }}
  .badge-sub {{ font-size: 0.72rem; color: var(--ink-soft); margin-top: 8px; }}

  section {{ padding: 52px 0; }}

  .facts {{ background: var(--sky-deep); color: #fff; }}
  .facts .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }}
  .fact {{
    background: rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 22px 24px;
  }}
  .fact-label {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--sun);
    margin-bottom: 6px;
  }}
  .fact-value {{ font-size: 1.05rem; }}

  .about {{ border-bottom: 1px solid var(--line); }}
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
    color: var(--sky-deep);
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--coral); font-weight: 700; }}

  .info {{ background: var(--sun-soft); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--sky-deep); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(58,53,48,0.12);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--coral); font-weight: 600; }}
  .contact-block p {{ margin-bottom: 10px; color: var(--ink); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--sky-deep);
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
    .hero .wrap, .about .wrap, .info .wrap, .facts .wrap {{ grid-template-columns: 1fr; }}
    .badge {{ justify-self: start; margin-top: 12px; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--sky-deep); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel ons</a>
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
    {badge_block}
  </div>
</section>

<section class="facts">
  <div class="wrap">
    <div class="fact">
      <div class="fact-label">Capaciteit</div>
      <div class="fact-value">{capacity}</div>
    </div>
    <div class="fact">
      <div class="fact-label">Toezicht</div>
      <div class="fact-value">{supervision}</div>
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
      <h2>Waarom kiezen voor ons</h2>
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
      <h2>Contacteer ons</h2>
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
