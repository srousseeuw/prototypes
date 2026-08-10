from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def _build_departments(items):
    lis = [f'<li class="dept">{esc(i)}</li>' for i in items]
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
    highlights_html = build_highlights(brief.get("highlights", []), mark="🌿")
    departments_html = _build_departments(brief.get("departments", []))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Archivo:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --soil: #3a2f1e;
    --bark: #5c4a30;
    --moss: #4d6b3c;
    --moss-deep: #364e29;
    --leaf: #8faa5e;
    --terra: #c17a3c;
    --paper: #f6f2e7;
    --paper-dim: #efe8d6;
    --line: #ddd2b4;
    --font-display: 'Fraunces', serif;
    --font-body: 'Archivo', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--soil);
    line-height: 1.55;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 18px 0;
    background: var(--moss-deep);
  }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.3rem;
    color: var(--paper);
  }}
  .brand::before {{ content: "🌱 "; }}
  .top-cta {{
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--terra);
    color: var(--paper);
    padding: 10px 18px;
    border-radius: 3px;
    text-decoration: none;
  }}

  .hero {{
    padding: 68px 0 60px;
    background:
      radial-gradient(circle at 85% 20%, rgba(143,170,94,0.35), transparent 55%),
      linear-gradient(170deg, var(--moss) 0%, var(--moss-deep) 100%);
    color: var(--paper);
    position: relative;
    overflow: hidden;
  }}
  .hero::after {{
    content: "";
    position: absolute;
    right: -60px; bottom: -80px;
    width: 320px; height: 320px;
    border: 40px solid rgba(246,242,231,0.06);
    border-radius: 50%;
  }}
  .hero .wrap {{ position: relative; }}
  .eyebrow {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--leaf);
    font-weight: 600;
    margin-bottom: 16px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.3rem, 5vw, 3.5rem);
    font-weight: 600;
    line-height: 1.08;
    max-width: 16ch;
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.1rem;
    color: rgba(246,242,231,0.85);
    max-width: 46ch;
    margin-bottom: 30px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--terra);
    color: var(--paper);
    font-weight: 600;
    padding: 14px 30px;
    border-radius: 3px;
    text-decoration: none;
    font-size: 0.98rem;
  }}

  section {{ padding: 56px 0; }}

  .departments {{ border-bottom: 1px solid var(--line); }}
  .dept-grid {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }}
  .dept {{
    background: var(--paper-dim);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 16px 14px;
    font-weight: 600;
    font-size: 0.95rem;
    text-align: center;
    color: var(--bark);
  }}

  .about {{ background: var(--paper-dim); }}
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
    color: var(--moss-deep);
  }}
  .about p {{ color: var(--bark); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ font-weight: 700; }}

  .info {{ background: var(--soil); color: var(--paper); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--leaf); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(246,242,231,0.15);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--terra); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(246,242,231,0.85); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--leaf);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{
    padding: 28px 0;
    text-align: center;
    font-size: 0.82rem;
    color: var(--bark);
  }}

  @media (max-width: 760px) {{
    .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .dept-grid {{ grid-template-columns: 1fr 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--terra); outline-offset: 3px; }}
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
    <div class="eyebrow">{category}</div>
    <h1>{tagline}</h1>
    <p class="tagline">{about}</p>
    <a class="hero-cta" href="#info">{cta}</a>
  </div>
</section>

<section class="departments">
  <div class="wrap">
    <h2>Onze afdelingen</h2>
    <ul class="dept-grid">
      {departments_html}
    </ul>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Over {name}</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Waarom bij ons</h2>
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
