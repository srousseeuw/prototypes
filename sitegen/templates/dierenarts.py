from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Maak een afspraak"))
    emergency_note = esc(brief.get("emergency_note", ""))
    vets = brief.get("team_size_vets")
    assistants = brief.get("team_size_assistants")
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="✓")
    maps_q = _maps_query(address)

    team_block = ""
    if vets or assistants:
        team_block = f'''<div class="team-badge">
            <div class="team-num">{vets or ""}</div>
            <div class="team-label">dierenartsen</div>
            <div class="team-divider"></div>
            <div class="team-num">{assistants or ""}</div>
            <div class="team-label">assistenten</div>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --sage: #4d7268;
    --sage-deep: #2f4a44;
    --mist: #eef3f1;
    --paper: #fbfcfb;
    --clay: #c98a5e;
    --line: #dce6e2;
    --ink: #223330;
    --ink-soft: #5a6b66;
    --font-display: 'Source Serif 4', serif;
    --font-body: 'Inter', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.6;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 20px 0;
    border-bottom: 1px solid var(--line);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.2rem;
    color: var(--sage-deep);
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.88rem;
    background: var(--sage-deep);
    color: #fff;
    padding: 10px 18px;
    border-radius: 6px;
    text-decoration: none;
  }}

  .hero {{
    padding: 68px 0 60px;
    background: var(--mist);
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--sage);
    font-weight: 600;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 4.6vw, 3.2rem);
    font-weight: 600;
    line-height: 1.15;
    color: var(--sage-deep);
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.08rem;
    color: var(--ink-soft);
    max-width: 44ch;
    margin-bottom: 22px;
  }}
  .emergency {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #fff;
    border: 1px solid var(--line);
    border-left: 3px solid var(--clay);
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 0.88rem;
    color: var(--ink-soft);
    margin-bottom: 28px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--sage);
    color: #fff;
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.98rem;
  }}

  .team-badge {{
    justify-self: end;
    background: var(--sage-deep);
    color: #fff;
    border-radius: 10px;
    padding: 28px 30px;
    display: flex;
    align-items: center;
    gap: 18px;
    width: 100%;
    max-width: 300px;
  }}
  .team-num {{
    font-family: var(--font-display);
    font-size: 2.4rem;
    font-weight: 600;
    line-height: 1;
  }}
  .team-label {{
    font-size: 0.8rem;
    color: rgba(255,255,255,0.75);
    margin-top: 4px;
  }}
  .team-divider {{
    width: 1px;
    align-self: stretch;
    background: rgba(255,255,255,0.2);
  }}

  section {{ padding: 56px 0; }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--sage-deep);
    margin-bottom: 16px;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--sage); font-weight: 700; }}

  .info {{ background: var(--sage-deep); color: #fff; }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: #fff; }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--clay); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(255,255,255,0.85); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--clay);
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
    .team-badge {{ justify-self: start; margin-top: 12px; max-width: none; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--sage-deep); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel de praktijk</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      <div class="emergency">🕐 {emergency_note}</div>
      <div>
        <a class="hero-cta" href="#info">{cta}</a>
      </div>
    </div>
    {team_block}
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Onze zorg</h2>
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
