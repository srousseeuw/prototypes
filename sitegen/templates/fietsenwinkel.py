from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def _build_services(items):
    lis = [f'<li class="svc"><span class="svc-dot"></span>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    phone_href = esc(brief.get("phone", "").replace(" ", ""))
    email = esc(brief.get("email", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Neem contact op"))
    accent = esc(brief.get("accent", "#c6ff2f"))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="→")
    services_html = _build_services(brief.get("services", brief.get("highlights", [])))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --asphalt: #1b1f24;
    --asphalt-deep: #101317;
    --steel: #2c3540;
    --steel-line: rgba(255,255,255,0.08);
    --accent: {accent};
    --paper: #f2f3f1;
    --ink: #1b1f24;
    --ink-soft: #5b6570;
    --font-display: 'Rajdhani', sans-serif;
    --font-body: 'Archivo', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.5;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 18px 0;
    background: var(--asphalt);
    border-bottom: 3px solid var(--accent);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.5rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: #fff;
  }}
  .brand span {{ color: var(--accent); }}
  .top-cta {{
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    background: var(--accent);
    color: var(--asphalt-deep);
    padding: 10px 20px;
    border-radius: 2px;
    text-decoration: none;
    text-transform: uppercase;
  }}

  .hero {{
    position: relative;
    padding: 80px 0 90px;
    background: linear-gradient(120deg, var(--asphalt) 0%, var(--asphalt-deep) 100%);
    color: #fff;
    overflow: hidden;
  }}
  .hero::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
      repeating-linear-gradient(78deg, transparent 0 46px, var(--steel-line) 46px 48px),
      repeating-linear-gradient(78deg, transparent 0 200px, rgba(198,255,47,0.05) 200px 204px);
    pointer-events: none;
  }}
  .hero .wrap {{ position: relative; }}
  .eyebrow {{
    font-family: var(--font-display);
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: var(--accent);
    font-weight: 700;
    margin-bottom: 16px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.6rem, 6vw, 4.4rem);
    font-weight: 700;
    text-transform: uppercase;
    line-height: 0.98;
    letter-spacing: 0.01em;
    margin-bottom: 20px;
    max-width: 16ch;
  }}
  .tagline {{
    font-size: 1.15rem;
    color: rgba(255,255,255,0.78);
    max-width: 46ch;
    margin-bottom: 32px;
  }}
  .hero-cta {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: var(--accent);
    color: var(--asphalt-deep);
    font-family: var(--font-display);
    font-weight: 700;
    padding: 15px 30px;
    border-radius: 2px;
    text-decoration: none;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    clip-path: polygon(0 0, 100% 0, 96% 100%, 0% 100%);
  }}

  section {{ padding: 64px 0; }}
  h2 {{
    font-family: var(--font-display);
    font-size: 2rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.01em;
    margin-bottom: 20px;
  }}

  .about {{ border-top: 1px solid rgba(27,31,36,0.1); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 56px;
    align-items: start;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.05rem; }}
  .about-tag {{
    display: inline-block;
    margin-top: 20px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--asphalt);
    border-left: 4px solid var(--accent);
    padding-left: 12px;
  }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 12px; align-items: baseline;
    padding: 12px 0;
    border-bottom: 1px solid rgba(27,31,36,0.1);
    font-size: 1rem;
  }}
  .mark {{ color: var(--accent); font-weight: 700; background: var(--asphalt); padding: 1px 6px; font-family: var(--font-display); }}

  .services {{ background: var(--steel); color: #fff; }}
  .services h2 {{ color: #fff; }}
  ul.svc-list {{ list-style: none; display: grid; grid-template-columns: 1fr 1fr; gap: 4px 32px; }}
  li.svc {{
    display: flex; align-items: center; gap: 12px;
    padding: 14px 0;
    border-bottom: 1px solid var(--steel-line);
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.08rem;
    text-transform: uppercase;
    letter-spacing: 0.01em;
  }}
  .svc-dot {{
    width: 10px; height: 10px;
    background: var(--accent);
    flex-shrink: 0;
    transform: rotate(45deg);
  }}

  .info {{ background: var(--paper); border-top: 1px solid rgba(27,31,36,0.1); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 56px;
  }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid rgba(27,31,36,0.1);
    font-size: 0.96rem;
  }}
  .hours-row span:first-child {{ font-weight: 600; }}
  .hours-row.closed span:last-child {{ color: var(--ink-soft); }}
  .contact-block p {{ margin-bottom: 10px; color: var(--ink-soft); font-size: 1rem; }}
  .contact-block a.map-link {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 14px;
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--asphalt);
    text-decoration: none;
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 2px;
  }}

  footer {{
    padding: 30px 0;
    text-align: center;
    background: var(--asphalt);
    font-size: 0.82rem;
    color: rgba(255,255,255,0.55);
  }}
  footer a {{ color: var(--accent); }}

  @media (max-width: 760px) {{
    .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    ul.svc-list {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name.split()[0] if name.split() else name}<span>.</span></div>
    <a class="top-cta" href="tel:{phone_href}">Bel de winkel</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="eyebrow">{category}</div>
    <h1>{tagline}</h1>
    <p class="tagline">{about}</p>
    <a class="hero-cta" href="#info">{cta} →</a>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Over {name}</h2>
      <p>{about}</p>
      <span class="about-tag">{address}</span>
    </div>
    <div>
      <h2>Waarom hier</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
  </div>
</section>

<section class="services">
  <div class="wrap">
    <h2>Diensten &amp; aanbod</h2>
    <ul class="svc-list">
      {services_html}
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
      <h2>Bezoek de winkel</h2>
      <p>{address}</p>
      <p>Tel. {phone}</p>
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
