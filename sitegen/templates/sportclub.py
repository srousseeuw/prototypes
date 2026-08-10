from .common import esc, build_highlights, maps_query as _maps_query

def _build_agenda_rows(items):
    rows = [f'<div class="agenda-row"><span class="agenda-date">{esc(d)}</span><span>{esc(t)}</span></div>' for d, t in items]
    return "\n".join(rows)

def _build_teams(items):
    lis = [f'<li>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    stamnummer = esc(brief.get("stamnummer", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Word lid van de club"))
    agenda_html = _build_agenda_rows(brief.get("agenda", []))
    teams_html = _build_teams(brief.get("teams", []))
    highlights_html = build_highlights(brief.get("highlights", []))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --navy: #10203f;
    --navy-deep: #0a1730;
    --pitch: #1c6e3c;
    --pitch-line: rgba(255,255,255,0.14);
    --gold: #c9a227;
    --paper: #f4f6f5;
    --ink-soft: #566073;
    --font-display: 'Barlow Condensed', sans-serif;
    --font-body: 'Inter', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--navy);
    line-height: 1.5;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 20px 0;
    background: var(--navy);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 800;
    font-size: 1.4rem;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: #fff;
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--gold);
    color: var(--navy-deep);
    padding: 10px 18px;
    border-radius: 4px;
    text-decoration: none;
  }}

  .hero {{
    padding: 64px 0 72px;
    background:
      repeating-linear-gradient(115deg, var(--pitch-line) 0 2px, transparent 2px 64px),
      linear-gradient(160deg, var(--pitch) 0%, #114f2c 100%);
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
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--gold);
    font-weight: 700;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.6rem, 5.5vw, 4rem);
    font-weight: 800;
    text-transform: uppercase;
    line-height: 1.02;
    letter-spacing: 0.01em;
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.1rem;
    color: rgba(255,255,255,0.85);
    max-width: 42ch;
    margin-bottom: 28px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--gold);
    color: var(--navy-deep);
    font-weight: 700;
    padding: 14px 28px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.98rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }}

  .scoreboard {{
    justify-self: end;
    background: var(--navy-deep);
    border: 2px solid var(--gold);
    border-radius: 6px;
    padding: 22px 26px;
    width: 100%;
    max-width: 260px;
  }}
  .scoreboard .label {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--gold);
    font-weight: 600;
    margin-bottom: 10px;
  }}
  .scoreboard .stamnr {{
    font-family: var(--font-display);
    font-size: 2.6rem;
    font-weight: 800;
    color: #fff;
    line-height: 1;
  }}
  .scoreboard .stamnr-sub {{
    font-size: 0.8rem;
    color: rgba(255,255,255,0.65);
    margin-top: 6px;
  }}

  section {{ padding: 56px 0; }}
  .about {{ border-top: 1px solid rgba(16,32,63,0.1); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.01em;
    margin-bottom: 16px;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(16,32,63,0.1);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--pitch); font-weight: 700; }}

  .teams {{ background: #fff; border-top: 1px solid rgba(16,32,63,0.1); }}
  ul.team-list {{ list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  ul.team-list li {{
    font-family: var(--font-display);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    font-size: 1.05rem;
    padding: 12px 16px;
    background: var(--paper);
    border-left: 4px solid var(--pitch);
  }}

  .info {{ background: var(--navy); color: #fff; }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: #fff; }}
  .agenda-row {{
    display: flex; gap: 16px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.15);
    font-size: 0.94rem;
  }}
  .agenda-date {{ color: var(--gold); font-weight: 700; min-width: 3.5em; }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(255,255,255,0.85); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--gold);
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
    .scoreboard {{ justify-self: start; margin-top: 12px; max-width: none; }}
    ul.team-list {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--gold); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel de kantine</a>
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
    <div class="scoreboard">
      <div class="label">Stamnummer</div>
      <div class="stamnr">{stamnummer}</div>
      <div class="stamnr-sub">Koninklijke Belgische Voetbalbond</div>
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
      <h2>Waarom KAVV</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

<section class="teams">
  <div class="wrap">
    <h2>Onze ploegen</h2>
    <ul class="team-list">
      {teams_html}
    </ul>
  </div>
</section>

<section class="info" id="info">
  <div class="wrap">
    <div>
      <h2>Agenda</h2>
      {agenda_html}
    </div>
    <div class="contact-block">
      <h2>Bezoek ons</h2>
      <p>{address}</p>
      <p>Tel. kantine: {phone}</p>
      <p>{email}</p>
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
