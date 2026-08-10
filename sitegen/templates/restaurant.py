from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    about_raw = brief.get("about", "")
    about = esc(about_raw)
    about_short = esc(about_raw if len(about_raw) <= 140 else about_raw[:140].rsplit(" ", 1)[0] + "…")
    wine_note = esc(brief.get("wine_note", ""))
    events_note = esc(brief.get("events_note", ""))
    cta = esc(brief.get("cta_text", "Reserveer uw tafel"))
    hours_html = build_hours_rows(brief.get("hours", []), closed_class="hours-row")
    highlights_html = build_highlights(brief.get("highlights", []), mark="✦")
    maps_q = _maps_query(address)
    phone_href = phone.replace(" ", "").replace("(0)", "")

    email_block = ""
    if email:
        email_block = f'<p><a class="email-link" href="mailto:{email}">{email}</a></p>'

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Playfair+Display:wght@500;600;700&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bordeaux: #4a0e18;
    --bordeaux-deep: #2c060d;
    --anthracite: #1c1c1e;
    --brass: #b3894a;
    --brass-light: #d9b877;
    --linen: #f4efe8;
    --ink-soft: rgba(244,239,232,0.72);
    --hairline: rgba(179,137,74,0.35);
    --font-display: 'Playfair Display', serif;
    --font-serif: 'Cormorant Garamond', serif;
    --font-body: 'Jost', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    font-weight: 300;
    background: var(--anthracite);
    color: var(--linen);
    line-height: 1.6;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 28px; }}

  .ornament {{
    display: flex; align-items: center; justify-content: center;
    gap: 14px;
    color: var(--brass);
  }}
  .ornament::before, .ornament::after {{
    content: "";
    height: 1px;
    width: 46px;
    background: var(--hairline);
  }}
  .ornament .glyph {{ font-size: 0.9rem; letter-spacing: 0.05em; }}

  header.top {{
    padding: 26px 0;
    border-bottom: 1px solid var(--hairline);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.2rem;
    letter-spacing: 0.03em;
    color: var(--brass-light);
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 400;
    font-size: 0.82rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid var(--brass);
    color: var(--brass-light);
    padding: 10px 20px;
    text-decoration: none;
  }}
  .top-cta:hover {{ background: var(--brass); color: var(--anthracite); }}

  .hero {{
    padding: 88px 0 68px;
    text-align: center;
    background:
      radial-gradient(ellipse at top, rgba(74,14,24,0.55), transparent 60%),
      var(--anthracite);
  }}
  .eyebrow {{
    font-family: var(--font-body);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: var(--brass);
    margin-bottom: 22px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    font-weight: 600;
    line-height: 1.15;
    max-width: 18ch;
    margin: 0 auto 24px;
  }}
  .hero .tagline-sub {{
    font-family: var(--font-serif);
    font-size: 1.3rem;
    font-style: italic;
    color: var(--ink-soft);
    max-width: 46ch;
    margin: 0 auto 34px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--brass);
    color: var(--bordeaux-deep);
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.86rem;
    padding: 15px 34px;
    text-decoration: none;
  }}
  .hero-cta:hover {{ background: var(--brass-light); }}

  section {{ padding: 64px 0; }}

  .about-section {{
    border-top: 1px solid var(--hairline);
    background: var(--bordeaux-deep);
  }}
  .about-section .wrap {{
    max-width: 760px;
    text-align: center;
  }}
  .about-section .ornament {{ margin-bottom: 26px; }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--brass-light);
    margin-bottom: 20px;
  }}
  .about-section p {{
    font-family: var(--font-serif);
    font-size: 1.2rem;
    color: var(--ink-soft);
  }}

  .offer {{ border-top: 1px solid var(--hairline); }}
  .offer .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 56px;
  }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 14px;
    padding: 13px 0;
    border-bottom: 1px solid var(--hairline);
    font-size: 1rem;
    color: var(--ink-soft);
  }}
  .mark {{ color: var(--brass); font-weight: 600; }}
  .side-notes p {{
    font-family: var(--font-serif);
    font-size: 1.08rem;
    color: var(--ink-soft);
    margin-bottom: 22px;
  }}
  .side-notes h3 {{
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 1.05rem;
    color: var(--brass-light);
    margin-bottom: 8px;
  }}

  .info {{ background: var(--bordeaux); border-top: 1px solid var(--hairline); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 56px;
  }}
  .info h2 {{ color: var(--linen); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid rgba(244,239,232,0.14);
    font-size: 0.95rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--brass-light); font-style: italic; }}
  .contact-block p {{ margin-bottom: 10px; color: var(--ink-soft); }}
  .contact-block a.map-link, .contact-block a.email-link {{
    display: inline-block;
    font-weight: 500;
    color: var(--brass-light);
    text-decoration: none;
    font-size: 0.94rem;
  }}
  .contact-block a.map-link {{ margin-top: 12px; }}

  footer {{
    padding: 30px 0;
    text-align: center;
    font-size: 0.8rem;
    color: var(--ink-soft);
    background: var(--anthracite);
  }}

  @media (max-width: 760px) {{
    .offer .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--brass-light); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone_href}">Reserveren</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="eyebrow">{category}</div>
    <h1>{tagline}</h1>
    <p class="tagline-sub">{about_short}</p>
    <a class="hero-cta" href="#info">{cta}</a>
  </div>
</section>

<section class="about-section">
  <div class="wrap">
    <div class="ornament"><span class="glyph">✦</span></div>
    <h2>De zaak</h2>
    <p>{about}</p>
  </div>
</section>

<section class="offer">
  <div class="wrap">
    <div>
      <h2>Op de kaart</h2>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
    <div class="side-notes">
      <h3>Wijnkaart</h3>
      <p>{wine_note}</p>
      <h3>Feesten &amp; recepties</h3>
      <p>{events_note}</p>
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
      <h2>Reserveren &amp; bezoek</h2>
      <p>{address}</p>
      <p><a class="map-link" href="tel:{phone_href}">{phone}</a></p>
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
