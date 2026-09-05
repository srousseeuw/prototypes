from .common import esc, build_highlights, maps_query as _maps_query

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    phone_href = esc(brief.get("phone", "").replace(" ", "").replace("/", ""))
    email = esc(brief.get("email", ""))
    founded = esc(brief.get("founded", ""))
    intro = esc(brief.get("intro", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Vraag een offerte aan"))
    appointment_note = esc(brief.get("appointment_note", ""))
    highlights_html = build_highlights(brief.get("highlights", []), mark="✂")
    maps_q = _maps_query(address)

    assortment = brief.get("assortment", [])
    assortment_html = "\n".join(
        f'''      <div class="swatch">
        <span class="swatch-num">0{i+1}</span>
        <h3>{esc(item.get("title", ""))}</h3>
        <p>{esc(item.get("desc", ""))}</p>
      </div>''' for i, item in enumerate(assortment)
    )

    hours = brief.get("hours", [])
    if hours:
        rows = "\n".join(
            f'<div class="hours-row"><span>{esc(d)}</span><span>{esc(t)}</span></div>'
            for d, t in hours
        )
        hours_block = f'<h2>Openingsuren</h2>\n{rows}'
    else:
        hours_block = f'''<h2>Op afspraak</h2>
      <p class="appt-copy">{appointment_note or "Elk naaiwerk begint met een gesprek over de mogelijkheden. Neem contact op per telefoon of e-mail om iets af te spreken."}</p>'''

    est_badge = f'<div class="est">sinds {founded}</div>' if founded else ""

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Work+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --linen: #f4efe6;
    --linen-deep: #e9e0d0;
    --petrol: #223b3a;
    --petrol-deep: #16282a;
    --thread: #c1553f;
    --thread-soft: #e0a08e;
    --ink: #2a2622;
    --ink-soft: rgba(42,38,34,0.66);
    --font-display: 'Fraunces', serif;
    --font-body: 'Work Sans', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    font-weight: 400;
    background: var(--linen);
    color: var(--ink);
    line-height: 1.65;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 980px; margin: 0 auto; padding: 0 28px; }}

  .stitch {{
    height: 0;
    border-top: 2px dashed var(--thread-soft);
  }}

  header.top {{
    padding: 26px 0;
    background: var(--petrol-deep);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 1.2rem;
    color: var(--linen);
    display: flex; align-items: center; gap: 10px;
  }}
  .brand svg {{ flex: none; }}
  .top-cta {{
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    border: 1px solid var(--thread-soft);
    color: var(--linen);
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 999px;
    transition: background 0.2s ease, color 0.2s ease;
  }}
  .top-cta:hover {{ background: var(--thread); border-color: var(--thread); }}

  .hero {{
    padding: 90px 0 80px;
    background: var(--petrol-deep);
    color: var(--linen);
    position: relative;
    overflow: hidden;
  }}
  .hero::after {{
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 1px;
    background-image: linear-gradient(to right, var(--thread-soft) 60%, transparent 0%);
    background-size: 16px 1px;
    background-repeat: repeat-x;
  }}
  .hero .wrap {{ position: relative; z-index: 1; }}
  .eyebrow {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    color: var(--thread-soft);
    margin-bottom: 22px;
  }}
  .hero h1 {{
    font-family: var(--font-display);
    font-weight: 500;
    font-size: clamp(2.1rem, 5vw, 3.3rem);
    line-height: 1.24;
    max-width: 18ch;
    margin-bottom: 22px;
    color: var(--linen);
  }}
  .hero .lede {{
    font-size: 1.08rem;
    color: rgba(244,239,230,0.78);
    max-width: 52ch;
    margin-bottom: 36px;
  }}
  .hero-cta {{
    display: inline-block;
    background: var(--thread);
    color: var(--linen);
    font-weight: 500;
    font-size: 0.9rem;
    letter-spacing: 0.02em;
    padding: 15px 32px;
    text-decoration: none;
    border-radius: 999px;
    transition: background 0.2s ease;
  }}
  .hero-cta:hover {{ background: #a8432f; }}

  section {{ padding: 72px 0; }}

  .about-section .wrap {{
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 52px;
    align-items: start;
  }}
  .est {{
    display: inline-block;
    font-family: var(--font-display);
    font-style: italic;
    font-size: 1.4rem;
    color: var(--thread);
    border: 2px dashed var(--thread-soft);
    border-radius: 50%;
    width: 128px; height: 128px;
    display: flex; align-items: center; justify-content: center;
    text-align: center;
    line-height: 1.3;
  }}
  h2 {{
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 1.7rem;
    color: var(--petrol);
    margin-bottom: 20px;
  }}
  .about-section p {{
    font-size: 1.02rem;
    color: var(--ink-soft);
    max-width: 60ch;
  }}

  .offer {{
    background: var(--linen-deep);
  }}
  .offer .wrap {{ text-align: center; }}
  .offer h2 {{ margin-bottom: 8px; }}
  .offer .lede-small {{
    color: var(--ink-soft);
    max-width: 50ch;
    margin: 0 auto 44px;
  }}
  .swatches {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 28px;
    text-align: left;
  }}
  .swatch {{
    background: var(--linen);
    border: 1px solid var(--linen-deep);
    border-radius: 4px;
    padding: 28px 26px;
    position: relative;
  }}
  .swatch::before {{
    content: "";
    position: absolute;
    top: 14px; left: 14px; right: 14px; bottom: 14px;
    border: 1px dashed rgba(193,85,63,0.35);
    border-radius: 2px;
    pointer-events: none;
  }}
  .swatch-num {{
    font-family: var(--font-display);
    font-style: italic;
    color: var(--thread-soft);
    font-size: 0.95rem;
  }}
  .swatch h3 {{
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 1.18rem;
    color: var(--petrol);
    margin: 8px 0 10px;
  }}
  .swatch p {{
    font-size: 0.94rem;
    color: var(--ink-soft);
  }}

  .highlights-section .wrap {{ text-align: center; }}
  ul.highlights {{
    list-style: none;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 40px;
    max-width: 760px;
    margin: 0 auto;
    text-align: left;
  }}
  ul.highlights li {{
    display: flex; gap: 14px; align-items: baseline;
    padding: 14px 0;
    border-bottom: 1px dashed var(--linen-deep);
    font-size: 0.98rem;
    color: var(--ink-soft);
  }}
  .mark {{ color: var(--thread); font-size: 0.85rem; }}

  .info {{
    background: var(--petrol-deep);
    color: var(--linen);
  }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
  }}
  .info h2 {{ color: var(--linen); text-align: left; }}
  .appt-copy {{ color: rgba(244,239,230,0.78); max-width: 44ch; }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px dashed rgba(244,239,230,0.2);
    font-size: 0.92rem;
    color: rgba(244,239,230,0.78);
  }}
  .contact-block a.phone-link {{
    font-family: var(--font-display);
    font-weight: 500;
    font-size: 1.5rem;
    color: var(--linen);
    text-decoration: none;
    display: inline-block;
    margin-bottom: 8px;
  }}
  .contact-block p {{ margin-bottom: 8px; color: rgba(244,239,230,0.78); }}
  .contact-block a.email-link {{
    color: var(--thread-soft);
    text-decoration: none;
    display: inline-block;
    margin-bottom: 8px;
  }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 16px;
    font-weight: 500;
    color: var(--thread-soft);
    text-decoration: none;
    font-size: 0.86rem;
  }}

  footer {{
    padding: 30px 0;
    text-align: center;
    font-size: 0.78rem;
    color: var(--ink-soft);
    background: var(--linen);
  }}

  @media (max-width: 720px) {{
    .about-section .wrap {{ grid-template-columns: 1fr; }}
    .info .wrap {{ grid-template-columns: 1fr; }}
    .swatches {{ grid-template-columns: 1fr; }}
    ul.highlights {{ grid-template-columns: 1fr; }}
  }}

  a:focus-visible, .hero-cta:focus-visible, .top-cta:focus-visible {{ outline: 2px solid var(--thread); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M3 21 L14 10" stroke="#e0a08e" stroke-width="1.6" stroke-dasharray="2 2"/>
        <circle cx="17" cy="7" r="3.4" stroke="#f4efe6" stroke-width="1.6"/>
        <path d="M19.4 4.6 L21.5 2.5" stroke="#f4efe6" stroke-width="1.6" stroke-linecap="round"/>
      </svg>
      {name}
    </div>
    <a class="top-cta" href="#info">{cta}</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="eyebrow">{category}</div>
    <h1>{tagline}</h1>
    <p class="lede">{intro}</p>
    <a class="hero-cta" href="tel:{phone_href}">Bel voor een afspraak</a>
  </div>
</section>

<section class="about-section">
  <div class="wrap">
    {est_badge}
    <div>
      <h2>Over het atelier</h2>
      <p>{about}</p>
    </div>
  </div>
</section>

<section class="offer">
  <div class="wrap">
    <h2>Wat er gemaakt wordt</h2>
    <p class="lede-small">Elk stuk wordt op maat gemaakt — hieronder een greep uit wat er mogelijk is.</p>
    <div class="swatches">
      {assortment_html}
    </div>
  </div>
</section>

<section class="highlights-section">
  <div class="wrap">
    <h2>In het kort</h2>
    <ul class="highlights">
      {highlights_html}
    </ul>
  </div>
</section>

<section class="info" id="info">
  <div class="wrap">
    <div>
      {hours_block}
    </div>
    <div class="contact-block">
      <h2>Contact</h2>
      <a class="phone-link" href="tel:{phone_href}">{phone}</a>
      <a class="email-link" href="mailto:{email}">{email}</a>
      <p>{address}</p>
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
