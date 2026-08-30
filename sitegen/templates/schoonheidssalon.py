from .common import esc, build_highlights, maps_query as _maps_query


def _build_pills(items):
    pills = [f'<span class="pill">{esc(i)}</span>' for i in items]
    return "\n".join(pills)


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    phone_href = esc(brief.get("phone", "").replace(" ", "").replace("/", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Bel voor een afspraak"))
    hours_note = esc(brief.get("hours_note", ""))
    kenmerken_html = _build_pills(brief.get("kenmerken", []))
    highlights_html = build_highlights(brief.get("highlights", []), mark="·")
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #1b2a2c;
    --ink-deep: #0f1c1e;
    --ink-soft: #536262;
    --coral: #d97a5f;
    --coral-deep: #b85f47;
    --mint: #e7efe9;
    --paper: #f8f7f3;
    --line: #dbe2dc;
    --font-display: 'Cormorant Garamond', serif;
    --font-body: 'DM Sans', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.6;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1060px; margin: 0 auto; padding: 0 24px; }}

  header.top {{ padding: 22px 0; border-bottom: 1px solid var(--line); }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.5rem;
    color: var(--ink-deep);
    letter-spacing: 0.01em;
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.88rem;
    background: var(--ink-deep);
    color: #fff;
    padding: 10px 20px;
    border-radius: 999px;
    text-decoration: none;
  }}

  .hero {{ padding: 68px 0 60px; overflow: hidden; }}
  .hero .wrap {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 48px; align-items: center; }}
  .eyebrow {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: var(--coral-deep);
    font-weight: 700;
    margin-bottom: 18px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.3rem, 4.8vw, 3.4rem);
    font-weight: 600;
    line-height: 1.18;
    color: var(--ink-deep);
    margin-bottom: 20px;
  }}
  .sub {{ font-size: 1.06rem; color: var(--ink-soft); max-width: 48ch; margin-bottom: 28px; }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 26px; }}
  .hero-cta {{
    display: inline-block;
    background: var(--coral);
    color: #fff;
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 999px;
    text-decoration: none;
    font-size: 0.98rem;
  }}
  .hero-cta.ghost {{
    background: transparent;
    color: var(--ink-deep);
    border: 1px solid var(--ink-deep);
  }}
  .pills-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .pill {{
    font-size: 0.82rem;
    font-weight: 600;
    background: #fff;
    border: 1px solid var(--line);
    color: var(--ink-deep);
    padding: 6px 14px;
    border-radius: 999px;
  }}

  /* signature element: kalme rimpelringen, met CSS-cirkels opgebouwd */
  .ripple {{
    position: relative;
    width: 260px;
    height: 260px;
    justify-self: end;
  }}
  .ripple .ring {{
    position: absolute;
    border-radius: 50%;
    border: 1px solid var(--coral);
    opacity: 0.35;
  }}
  .ripple .ring-1 {{ inset: 0; }}
  .ripple .ring-2 {{ inset: 30px; opacity: 0.5; }}
  .ripple .ring-3 {{ inset: 60px; opacity: 0.7; }}
  .ripple .core {{
    position: absolute;
    inset: 90px;
    border-radius: 50%;
    background: var(--coral);
  }}

  section {{ padding: 60px 0; }}

  .about {{ background: var(--mint); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
  .about .wrap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 48px; }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--ink-deep);
    margin-bottom: 16px;
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 12px; align-items: flex-start;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--coral-deep); font-weight: 700; }}

  .info .wrap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 48px; }}
  .hours-note {{
    background: var(--mint);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px 18px;
    font-size: 0.94rem;
    color: var(--ink-soft);
  }}
  .contact-block a.phone-link {{
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 600;
    color: var(--ink-deep);
    text-decoration: none;
    display: inline-block;
    margin-bottom: 10px;
  }}
  .contact-block p {{ margin-bottom: 10px; color: var(--ink); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--coral-deep);
    text-decoration: none;
    font-size: 0.92rem;
  }}

  footer {{ padding: 28px 0; text-align: center; font-size: 0.82rem; color: var(--ink-soft); }}

  @media (max-width: 760px) {{
    .hero .wrap, .about .wrap, .info .wrap {{ grid-template-columns: 1fr; }}
    .ripple {{ justify-self: start; margin-top: 8px; width: 180px; height: 180px; }}
    .ripple .ring-2 {{ inset: 20px; }}
    .ripple .ring-3 {{ inset: 40px; }}
    .ripple .core {{ inset: 62px; }}
  }}

  a:focus-visible, .hero-cta:focus-visible, .top-cta:focus-visible {{ outline: 2px solid var(--coral-deep); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone_href}">{cta}</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="sub">{about}</p>
      <div class="hero-actions">
        <a class="hero-cta" href="tel:{phone_href}">{cta}</a>
        <a class="hero-cta ghost" href="#info">Adres &amp; contact</a>
      </div>
      <div class="pills-row">
        {kenmerken_html}
      </div>
    </div>
    <div class="ripple" aria-hidden="true">
      <span class="ring ring-1"></span>
      <span class="ring ring-2"></span>
      <span class="ring ring-3"></span>
      <span class="core"></span>
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
      <h2>Openingstijden</h2>
      <div class="hours-note">{hours_note}</div>
    </div>
    <div class="contact-block">
      <h2>Maak een afspraak</h2>
      <a class="phone-link" href="tel:{phone_href}">{phone}</a>
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
