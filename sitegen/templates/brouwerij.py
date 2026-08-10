from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query


def _build_beers(items):
    lis = [f'<li class="beer">{esc(i)}</li>' for i in items]
    return "\n".join(lis)


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Neem contact op"))
    since = esc(str(brief.get("since", "")))
    team = esc(brief.get("team", ""))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="●")
    beers_html = _build_beers(brief.get("beer_styles", []))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --copper: #b5652f;
    --copper-bright: #d97f3f;
    --rust: #8a3f22;
    --concrete: #3a3835;
    --concrete-dark: #211f1d;
    --paper: #f2ede4;
    --steam: #eae3d6;
    --line: #4d4a45;
    --font-display: 'Bebas Neue', sans-serif;
    --font-body: 'Barlow', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--concrete-dark);
    line-height: 1.6;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    background: var(--concrete-dark);
    padding: 16px 0;
    border-bottom: 3px solid var(--copper);
  }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-display);
    letter-spacing: 0.04em;
    font-size: 1.5rem;
    color: var(--steam);
  }}
  .brand span {{ color: var(--copper-bright); }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--concrete-dark);
    background: var(--copper-bright);
    padding: 10px 20px;
    text-decoration: none;
  }}

  .hero {{
    position: relative;
    background: var(--concrete-dark);
    color: var(--steam);
    padding: 76px 0 60px;
    overflow: hidden;
  }}
  /* signature element: schematic brew-kettle silhouette with rising steam lines */
  .kettle-mark {{
    position: absolute;
    right: -40px; top: 50%;
    transform: translateY(-50%);
    width: 340px; height: 340px;
    opacity: 0.16;
    pointer-events: none;
  }}
  .hero .wrap {{ position: relative; z-index: 1; }}
  .hero .eyebrow {{
    font-family: var(--font-body);
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-size: 0.78rem;
    color: var(--copper-bright);
    margin-bottom: 18px;
    font-weight: 600;
  }}
  .hero h1 {{
    font-family: var(--font-display);
    font-size: clamp(3rem, 8vw, 5.6rem);
    letter-spacing: 0.02em;
    line-height: 0.95;
    max-width: 16ch;
    margin-bottom: 18px;
  }}
  .hero p.tag {{
    font-size: 1.15rem;
    max-width: 48ch;
    color: #cfc7ba;
    margin-bottom: 30px;
  }}
  .hero-actions {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .btn {{
    display: inline-block;
    font-family: var(--font-body);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.88rem;
    padding: 14px 28px;
    text-decoration: none;
  }}
  .btn-primary {{ background: var(--copper-bright); color: var(--concrete-dark); }}
  .btn-ghost {{ background: transparent; color: var(--steam); border: 1px solid var(--line); }}

  .since-strip {{
    background: var(--copper);
    color: var(--concrete-dark);
    padding: 14px 0;
    font-family: var(--font-display);
    letter-spacing: 0.03em;
  }}
  .since-strip .wrap {{ display: flex; gap: 32px; flex-wrap: wrap; justify-content: space-between; font-size: 1.05rem; }}

  section {{ padding: 64px 0; }}
  h2 {{
    font-family: var(--font-display);
    font-size: 2.4rem;
    letter-spacing: 0.02em;
    margin-bottom: 10px;
    color: var(--rust);
  }}
  .section-sub {{ color: #57534c; margin-bottom: 32px; max-width: 58ch; }}

  .split {{
    display: grid;
    grid-template-columns: 1.05fr 0.95fr;
    gap: 44px;
    align-items: start;
  }}
  @media (max-width: 780px) {{ .split {{ grid-template-columns: 1fr; }} }}

  .about-card p {{ margin-bottom: 14px; color: #2b2823; }}
  ul.highlights {{ list-style: none; margin-top: 18px; }}
  ul.highlights li {{
    display: flex; gap: 12px; align-items: flex-start;
    padding: 9px 0;
    border-bottom: 1px solid #ded5c4;
    font-size: 0.95rem;
  }}
  ul.highlights li:last-child {{ border-bottom: none; }}
  ul.highlights .mark {{ color: var(--copper); flex-shrink: 0; font-size: 0.7rem; margin-top: 5px; }}

  .info-card {{
    background: var(--concrete);
    color: var(--steam);
    padding: 30px;
    border-top: 4px solid var(--copper-bright);
  }}
  .info-card h3 {{
    font-family: var(--font-display);
    font-size: 1.5rem;
    letter-spacing: 0.03em;
    margin-bottom: 16px;
    color: var(--copper-bright);
  }}
  .info-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 8px 0; font-size: 0.92rem; border-bottom: 1px solid #55524c; }}
  .info-row span:first-child {{ color: #a89f8e; }}
  .info-row a {{ text-decoration: none; color: var(--steam); font-weight: 600; }}

  .hours-block {{ margin-top: 20px; }}
  .hours-row {{ display: flex; justify-content: space-between; font-size: 0.88rem; padding: 5px 0; }}
  .hours-row.closed {{ opacity: 0.5; }}

  .note-strip {{
    background: rgba(217,127,63,0.12);
    border: 1px dashed var(--copper);
    padding: 12px 16px;
    margin-top: 18px;
    font-size: 0.82rem;
    color: #d9c9b3;
  }}

  .beers {{
    background: var(--concrete-dark);
    color: var(--steam);
  }}
  .beers h2 {{ color: var(--copper-bright); }}
  .beer-grid {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 2px;
    background: var(--line);
  }}
  .beer {{
    background: var(--concrete);
    padding: 20px 18px;
    font-family: var(--font-display);
    font-size: 1.2rem;
    letter-spacing: 0.02em;
  }}

  .cta-band {{
    background: var(--copper-bright);
    color: var(--concrete-dark);
    padding: 52px 0;
    text-align: center;
  }}
  .cta-band h2 {{ color: var(--concrete-dark); }}
  .cta-band .btn-primary {{ background: var(--concrete-dark); color: var(--copper-bright); margin-top: 20px; }}

  footer {{
    background: var(--concrete-dark);
    color: #a89f8e;
    padding: 26px 0;
    font-size: 0.82rem;
    text-align: center;
    border-top: 3px solid var(--copper);
  }}
  footer a {{ color: var(--copper-bright); }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">CROW <span>MOUNTAIN</span></div>
    <a class="top-cta" href="mailto:{email}">{cta}</a>
  </div>
</header>

<section class="hero">
  <svg class="kettle-mark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <path d="M40 100 Q40 170 100 170 Q160 170 160 100 L155 60 Q150 40 100 40 Q50 40 45 60 Z" fill="none" stroke="#d97f3f" stroke-width="4"/>
    <rect x="92" y="20" width="16" height="24" fill="#d97f3f"/>
    <path d="M70 20 Q65 5 75 -5" fill="none" stroke="#d97f3f" stroke-width="3" stroke-linecap="round"/>
    <path d="M100 15 Q95 0 105 -10" fill="none" stroke="#d97f3f" stroke-width="3" stroke-linecap="round"/>
    <path d="M130 20 Q125 5 135 -5" fill="none" stroke="#d97f3f" stroke-width="3" stroke-linecap="round"/>
  </svg>
  <div class="wrap">
    <div class="eyebrow">Microbrouwerij op de Kraaienberg · Essen-Horendonk</div>
    <h1>{name}</h1>
    <p class="tag">{tagline}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="mailto:{email}">{cta}</a>
      <a class="btn btn-ghost" href="tel:{phone}">Bel de brouwerij</a>
    </div>
  </div>
</section>

<div class="since-strip">
  <div class="wrap">
    <span>Brouwend sinds {since}</span>
    <span>Eigen brouwerij sinds september 2021</span>
    <span>{team}</span>
  </div>
</div>

<section id="over">
  <div class="wrap split">
    <div class="about-card">
      <h2>Het verhaal</h2>
      <p class="section-sub">Van washandje tot brouwketel — een familieverhaal op de Kraaienberg.</p>
      <p>{about}</p>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
    <div class="info-card">
      <h3>Bezoek &amp; contact</h3>
      <div class="info-row"><span>Adres</span><a href="https://www.google.com/maps/search/?api=1&query={maps_q}" target="_blank" rel="noopener">{address}</a></div>
      <div class="info-row"><span>Telefoon</span><a href="tel:{phone}">{phone}</a></div>
      <div class="info-row"><span>E-mail</span><a href="mailto:{email}">{email}</a></div>
      <div class="hours-block">
        {hours_html}
      </div>
      <div class="note-strip">Bezoek, proeverij of afhaling? Neem best vooraf contact op — de brouwerij werkt met een kleine, ambachtelijke ploeg.</div>
    </div>
  </div>
</section>

<section class="beers">
  <div class="wrap">
    <h2>Op het brouwrek</h2>
    <p class="section-sub" style="color:#cfc7ba;">Puur gebrouwen, zonder kunstmatige smaak- of kleurstoffen — met respect voor de Belgische biertraditie.</p>
    <ul class="beer-grid">
      {beers_html}
    </ul>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>Proef het verschil</h2>
    <p>Mail of bel ons voor bezoekmogelijkheden, bestellingen of meer informatie.</p>
    <a class="btn btn-primary" href="mailto:{email}">{cta}</a>
  </div>
</section>

<footer>
  <div class="wrap">
    {name} · {address} · <a href="tel:{phone}">{phone}</a>
  </div>
</footer>

</body>
</html>
"""
