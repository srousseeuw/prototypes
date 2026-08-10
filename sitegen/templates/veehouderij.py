from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def _build_breeds(items):
    lis = [f'<li class="breed"><span class="brand-mark" aria-hidden="true"></span>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def _build_services(items):
    lis = [f'<li>{esc(i)}</li>' for i in items]
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
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="◆")
    breeds_html = _build_breeds(brief.get("breeds", []))
    services_html = _build_services(brief.get("services", []))
    maps_q = _maps_query(address)

    email_block = ""
    if email:
        email_block = f'<p><a href="mailto:{email}">{email}</a></p>'

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bitter:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --hide: #241a12;
    --hide-deep: #17110b;
    --saddle: #6b4327;
    --oak: #a97a4a;
    --ember: #b5652f;
    --cream: #f1e9dc;
    --paper: #ece2d0;
    --line: #3a2c1e;
    --ink-soft: #5c4d3c;
    --font-display: 'Bitter', serif;
    --font-body: 'Source Sans 3', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--cream);
    color: var(--hide);
    line-height: 1.55;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 20px 0;
    background: var(--hide-deep);
    border-bottom: 3px solid var(--ember);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--cream);
    letter-spacing: 0.01em;
    text-transform: uppercase;
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.86rem;
    background: var(--ember);
    color: var(--cream);
    padding: 10px 20px;
    text-decoration: none;
    letter-spacing: 0.02em;
  }}

  .hero {{
    padding: 76px 0 60px;
    background: var(--hide-deep);
    color: var(--cream);
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 48px;
    align-items: start;
  }}
  .eyebrow {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--oak);
    font-weight: 700;
    margin-bottom: 16px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.1rem, 4.4vw, 3.1rem);
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.08rem;
    color: rgba(241,233,220,0.8);
    max-width: 46ch;
    margin-bottom: 30px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--ember);
    color: var(--cream);
    font-weight: 700;
    padding: 14px 30px;
    text-decoration: none;
    font-size: 0.96rem;
    letter-spacing: 0.02em;
  }}

  .breeds-panel {{
    border: 1px solid rgba(169,122,74,0.4);
    padding: 26px;
  }}
  .breeds-panel .panel-title {{
    font-family: var(--font-display);
    font-size: 1.05rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--oak);
    margin-bottom: 16px;
  }}
  ul.breeds {{ list-style: none; }}
  li.breed {{
    display: flex; align-items: center; gap: 12px;
    padding: 11px 0;
    border-bottom: 1px solid rgba(169,122,74,0.25);
    font-family: var(--font-display);
    font-size: 1.05rem;
  }}
  li.breed:last-child {{ border-bottom: none; }}
  .brand-mark {{
    width: 10px; height: 10px;
    background: var(--ember);
    transform: rotate(45deg);
    flex-shrink: 0;
  }}

  section {{ padding: 58px 0; }}
  .about {{ border-bottom: 1px solid var(--line); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--saddle);
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--ember); font-weight: 700; }}

  .services {{ background: var(--paper); border-bottom: 1px solid var(--line); }}
  ul.service-list {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }}
  ul.service-list li {{
    background: var(--cream);
    border: 1px solid var(--line);
    padding: 14px 16px;
    font-weight: 600;
    font-size: 0.96rem;
  }}

  .info {{ background: var(--hide-deep); color: var(--cream); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--oak); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(241,233,220,0.15);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--oak); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(241,233,220,0.85); }}
  .contact-block a {{ text-decoration: underline; }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--oak);
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
    ul.service-list {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--oak); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel voor advies</a>
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
    <div class="breeds-panel">
      <div class="panel-title">Onze rassen</div>
      <ul class="breeds">
        {breeds_html}
      </ul>
    </div>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Over de Steenhoeve</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Waarom klanten voor ons kiezen</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

<section class="services">
  <div class="wrap">
    <h2>Diensten</h2>
    <ul class="service-list">
      {services_html}
    </ul>
  </div>
</section>

<section class="info" id="info">
  <div class="wrap">
    <div>
      <h2>Bereikbaarheid</h2>
      {hours_html}
    </div>
    <div class="contact-block">
      <h2>Contact</h2>
      <p>{address}</p>
      <p><a href="tel:{phone}">{phone}</a></p>
      {email_block}
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
