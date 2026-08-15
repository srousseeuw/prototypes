from .common import esc, build_highlights, maps_query as _maps_query


def _build_animals(items):
    pills = [f'<span class="animal-pill">{esc(i)}</span>' for i in items]
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
    accent = esc(brief.get("accent", "#e0a63e"))
    highlights_html = build_highlights(brief.get("highlights", []), mark="🐾")
    animals_html = _build_animals(brief.get("animals", []))
    maps_q = _maps_query(address)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --teal: #1e3d3a;
    --teal-deep: #142a27;
    --mint: #eef5ee;
    --paper: #fbfaf6;
    --accent: {accent};
    --ink: #1c2420;
    --ink-soft: #5c6b63;
    --line: #dbe4dd;
    --font-display: 'Baloo 2', sans-serif;
    --font-body: 'Nunito Sans', sans-serif;
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
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--teal-deep);
  }}
  .brand .dot {{
    width: 12px; height: 12px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
  }}
  .top-cta {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.92rem;
    background: var(--teal-deep);
    color: #fff;
    padding: 10px 20px;
    border-radius: 999px;
    text-decoration: none;
  }}

  .hero {{
    background: var(--mint);
    padding: 68px 0 60px;
    overflow: hidden;
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-family: var(--font-display);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--teal);
    font-weight: 700;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.1rem, 4.6vw, 3.1rem);
    font-weight: 700;
    line-height: 1.18;
    color: var(--teal-deep);
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
    border-left: 3px solid var(--accent);
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 0.88rem;
    color: var(--ink-soft);
    margin-bottom: 26px;
  }}
  .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; }}
  .hero-cta {{
    display: inline-block;
    background: var(--teal);
    color: #fff;
    font-family: var(--font-display);
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 999px;
    text-decoration: none;
    font-size: 0.98rem;
  }}
  .hero-cta.ghost {{
    background: transparent;
    color: var(--teal-deep);
    border: 1px solid var(--teal-deep);
  }}

  .animals-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }}
  .animal-pill {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 0.86rem;
    background: #fff;
    border: 1px solid var(--line);
    color: var(--teal-deep);
    padding: 7px 16px;
    border-radius: 999px;
  }}

  /* signature element: een pootafdruk opgebouwd uit cirkels, geen icon-library nodig */
  .pawprint {{
    position: relative;
    width: 220px;
    height: 220px;
    justify-self: end;
  }}
  .pawprint .pad {{
    position: absolute;
    left: 50%; top: 54%;
    transform: translate(-50%, -50%);
    width: 118px; height: 96px;
    border-radius: 50% 50% 46% 46%;
    background: var(--teal);
  }}
  .pawprint .toe {{
    position: absolute;
    width: 52px; height: 66px;
    border-radius: 50%;
    background: var(--accent);
  }}
  .pawprint .toe-1 {{ left: 8px;  top: 8px;  transform: rotate(-18deg); }}
  .pawprint .toe-2 {{ left: 62px; top: -14px; transform: rotate(-4deg); }}
  .pawprint .toe-3 {{ left: 118px; top: -10px; transform: rotate(6deg); }}
  .pawprint .toe-4 {{ left: 168px; top: 14px; transform: rotate(20deg); }}

  section {{ padding: 60px 0; }}
  .about .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  h2 {{
    font-family: var(--font-display);
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--teal-deep);
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
  .mark {{ font-size: 0.95rem; }}

  .info {{ background: var(--teal-deep); color: #fff; }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: #fff; }}
  .hours-note {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 8px;
    padding: 16px 18px;
    font-size: 0.94rem;
    color: rgba(255,255,255,0.9);
  }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(255,255,255,0.85); }}
  .contact-block a.phone-link {{
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    text-decoration: none;
    display: inline-block;
    margin-bottom: 6px;
  }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 700;
    color: var(--accent);
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
    .pawprint {{ justify-self: start; margin-top: 12px; width: 170px; height: 170px; transform: scale(0.85); transform-origin: left top; }}
  }}

  a:focus-visible, .hero-cta:focus-visible, .top-cta:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand"><span class="dot"></span>{name}</div>
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
      <div class="animals-row">
        {animals_html}
      </div>
    </div>
    <div class="pawprint" aria-hidden="true">
      <span class="toe toe-1"></span>
      <span class="toe toe-2"></span>
      <span class="toe toe-3"></span>
      <span class="toe toe-4"></span>
      <span class="pad"></span>
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
      <h2>Wat we bieden</h2>
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
