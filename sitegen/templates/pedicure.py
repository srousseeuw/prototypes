from .common import esc, build_highlights, maps_query as _maps_query


def _build_pills(items, cls="pill"):
    pills = [f'<span class="{cls}">{esc(i)}</span>' for i in items]
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
    appointment_note = esc(brief.get("appointment_note", "Uitsluitend op afspraak"))
    hours_note = esc(brief.get("hours_note", ""))
    specialisaties_html = _build_pills(brief.get("specialisaties", []), cls="pill")
    certifications_html = _build_pills(brief.get("certifications", []), cls="cert-pill")
    highlights_html = build_highlights(brief.get("highlights", []), mark="✓")
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --plum: #3d2432;
    --plum-deep: #2a1823;
    --rose: #b85c6b;
    --rose-deep: #934652;
    --sage: #7c9483;
    --paper: #fbf6f4;
    --panel: #f3e6e2;
    --ink: #3d2432;
    --ink-soft: #7a5c65;
    --line: #e7d4cf;
    --font-display: 'Fraunces', serif;
    --font-body: 'Work Sans', sans-serif;
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
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.4rem;
    color: var(--plum-deep);
    font-style: italic;
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--rose);
    color: #fff;
    padding: 10px 20px;
    border-radius: 999px;
    text-decoration: none;
  }}

  .hero {{
    background: var(--panel);
    padding: 64px 0 56px;
    overflow: hidden;
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-family: var(--font-body);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--rose-deep);
    font-weight: 700;
    margin-bottom: 16px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.1rem, 4.6vw, 3.1rem);
    font-weight: 600;
    line-height: 1.2;
    color: var(--plum-deep);
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.06rem;
    color: var(--ink-soft);
    max-width: 46ch;
    margin-bottom: 22px;
  }}
  .appointment-note {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #fff;
    border: 1px solid var(--line);
    border-left: 3px solid var(--rose);
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 0.88rem;
    color: var(--ink-soft);
    margin-bottom: 24px;
  }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 26px; }}
  .hero-cta {{
    display: inline-block;
    background: var(--plum);
    color: #fff;
    font-family: var(--font-body);
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 999px;
    text-decoration: none;
    font-size: 0.98rem;
  }}
  .hero-cta.ghost {{
    background: transparent;
    color: var(--plum-deep);
    border: 1px solid var(--plum-deep);
  }}

  .pills-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .pill {{
    font-size: 0.82rem;
    font-weight: 600;
    background: #fff;
    border: 1px solid var(--line);
    color: var(--plum-deep);
    padding: 6px 14px;
    border-radius: 999px;
  }}

  /* signature element: een voetafdruk uit cirkels opgebouwd, geen icon-library */
  .footprint {{
    position: relative;
    width: 200px;
    height: 240px;
    justify-self: end;
  }}
  .footprint .sole {{
    position: absolute;
    left: 30px; top: 60px;
    width: 130px; height: 170px;
    border-radius: 48% 48% 55% 55% / 40% 40% 60% 60%;
    background: var(--rose);
    opacity: 0.92;
  }}
  .footprint .toe {{
    position: absolute;
    border-radius: 50%;
    background: var(--plum);
  }}
  .footprint .toe-1 {{ width: 30px; height: 34px; left: 78px; top: 4px; }}
  .footprint .toe-2 {{ width: 26px; height: 30px; left: 46px; top: 10px; transform: rotate(-8deg); }}
  .footprint .toe-3 {{ width: 22px; height: 26px; left: 20px; top: 24px; transform: rotate(-16deg); }}
  .footprint .toe-4 {{ width: 20px; height: 22px; left: 108px; top: 12px; transform: rotate(8deg); }}
  .footprint .toe-5 {{ width: 17px; height: 19px; left: 132px; top: 24px; transform: rotate(16deg); }}

  section {{ padding: 58px 0; }}

  .certs {{ background: var(--plum-deep); }}
  .certs .wrap {{ display: flex; flex-wrap: wrap; align-items: center; gap: 14px; }}
  .certs-label {{
    font-family: var(--font-display);
    font-style: italic;
    color: #fff;
    font-size: 1rem;
    margin-right: 6px;
  }}
  .cert-pill {{
    font-size: 0.8rem;
    font-weight: 600;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.25);
    color: #fff;
    padding: 6px 14px;
    border-radius: 999px;
  }}

  .about {{ border-bottom: 1px solid var(--line); }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--plum-deep);
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
  .mark {{ color: var(--rose-deep); font-weight: 700; }}

  .info {{ background: var(--panel); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .hours-note {{
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px 18px;
    font-size: 0.94rem;
    color: var(--ink-soft);
  }}
  .contact-block p {{ margin-bottom: 10px; color: var(--ink); }}
  .contact-block a.phone-link {{
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--plum-deep);
    text-decoration: none;
    display: inline-block;
    margin-bottom: 10px;
  }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--rose-deep);
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
    .footprint {{ justify-self: start; margin-top: 12px; width: 150px; height: 180px; transform: scale(0.85); transform-origin: left top; }}
  }}

  a:focus-visible, .hero-cta:focus-visible, .top-cta:focus-visible {{ outline: 2px solid var(--rose-deep); outline-offset: 3px; }}
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
      <p class="tagline">{about}</p>
      <div class="appointment-note">📅 {appointment_note}</div>
      <div class="hero-actions">
        <a class="hero-cta" href="tel:{phone_href}">{cta}</a>
        <a class="hero-cta ghost" href="#info">Adres &amp; contact</a>
      </div>
      <div class="pills-row">
        {specialisaties_html}
      </div>
    </div>
    <div class="footprint" aria-hidden="true">
      <span class="sole"></span>
      <span class="toe toe-1"></span>
      <span class="toe toe-2"></span>
      <span class="toe toe-3"></span>
      <span class="toe toe-4"></span>
      <span class="toe toe-5"></span>
    </div>
  </div>
</section>

<section class="certs">
  <div class="wrap">
    <span class="certs-label">Erkenningen</span>
    {certifications_html}
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Over {name}</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Waarom kiezen voor {name}</h2>
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
