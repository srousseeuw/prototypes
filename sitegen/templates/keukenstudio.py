from .common import esc, build_hours_rows, build_list, maps_query as _maps_query


def _wood_grain_swatches():
    """Signature element: houtnerf-swatches i.p.v. iconen, verwijst naar massief eiken."""
    labels = ["Landelijk eiken", "Strak modern", "Op maat gezaagd", "Handgeolied"]
    out = []
    for i, lab in enumerate(labels):
        out.append(f'<div class="swatch swatch-{i % 4}"><span>{esc(lab)}</span></div>')
    return "\n".join(out)


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Plan een bezoek aan de showroom"))
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_list(brief.get("highlights", []), item_class="highlight")
    services_html = build_list(brief.get("services", []), item_class="service")
    swatches_html = _wood_grain_swatches()
    maps_q = _maps_query(address)
    tel_href = phone.replace(" ", "").replace("(0)", "")

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --walnut: #5a3a26;
    --walnut-deep: #3c2416;
    --walnut-light: #8a5f3e;
    --stone: #cfc6ba;
    --stone-soft: #ece6dc;
    --near-black: #1c1a18;
    --paper: #f7f4ef;
    --ink: #241d16;
    --ink-soft: #6f6357;
    --line: #ddd4c7;
    --gold: #a9824c;
    --font-display: 'Cormorant Garamond', serif;
    --font-body: 'Jost', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.65;
    font-weight: 300;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1120px; margin: 0 auto; padding: 0 32px; }}

  header.top {{
    padding: 26px 0;
    background: var(--near-black);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.5rem;
    letter-spacing: 0.03em;
    color: #f2ece1;
  }}
  .brand span {{ color: var(--gold); }}
  header.top nav a {{
    text-decoration: none;
    color: #f2ece1;
    font-size: 0.82rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border: 1px solid rgba(242,236,225,0.35);
    padding: 10px 20px;
  }}

  .hero {{
    background: var(--near-black);
    color: #f2ece1;
    padding: 80px 0 90px;
    position: relative;
  }}
  .hero::after {{
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 6px;
    background: linear-gradient(90deg, var(--walnut-deep), var(--walnut-light), var(--gold));
  }}
  .hero-inner {{ max-width: 720px; }}
  .kicker {{
    font-size: 0.78rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 22px;
  }}
  .hero h1 {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: clamp(2.4rem, 5.2vw, 3.6rem);
    line-height: 1.15;
    margin-bottom: 22px;
    color: #f7f2ea;
  }}
  .hero p {{
    font-size: 1.15rem;
    color: #d9d0c3;
    max-width: 52ch;
    margin-bottom: 34px;
  }}
  .hero-actions {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .btn {{
    display: inline-block;
    padding: 15px 30px;
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-decoration: none;
  }}
  .btn-primary {{ background: var(--gold); color: var(--near-black); font-weight: 500; }}
  .btn-secondary {{ border: 1px solid rgba(242,236,225,0.4); color: #f2ece1; }}

  .swatch-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.08);
  }}
  .swatch {{
    aspect-ratio: 1.6 / 1;
    display: flex;
    align-items: flex-end;
    padding: 14px;
    background-size: cover;
  }}
  .swatch span {{
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    color: #f7f2ea;
    text-transform: uppercase;
  }}
  .swatch-0 {{ background: repeating-linear-gradient(100deg, #6b4529, #6b4529 6px, #7c5433 6px, #7c5433 11px); }}
  .swatch-1 {{ background: repeating-linear-gradient(96deg, #4a3020, #4a3020 8px, #59391f 8px, #59391f 15px); }}
  .swatch-2 {{ background: repeating-linear-gradient(102deg, #8a5f3e, #8a5f3e 5px, #96693f 5px, #96693f 9px); }}
  .swatch-3 {{ background: repeating-linear-gradient(98deg, #3c2416, #3c2416 7px, #4a2c1a 7px, #4a2c1a 13px); }}

  section {{ padding: 72px 0; }}
  h2 {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 2.1rem;
    color: var(--walnut-deep);
    margin-bottom: 26px;
  }}

  .about-section {{ background: var(--stone-soft); }}
  .about-grid {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 48px; align-items: start; }}
  @media (max-width: 780px) {{ .about-grid {{ grid-template-columns: 1fr; }} }}
  .about-grid p {{ font-size: 1.05rem; color: var(--ink-soft); }}

  .highlights-list {{ list-style: none; }}
  .highlight {{
    padding: 14px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
    position: relative;
    padding-left: 24px;
  }}
  .highlight::before {{
    content: "—";
    position: absolute; left: 0;
    color: var(--gold);
  }}

  .services-section {{ background: var(--paper); }}
  .services-list {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 18px;
  }}
  .service {{
    border: 1px solid var(--line);
    padding: 24px 22px;
    background: #fff;
  }}
  .service::before {{
    content: "";
    display: block;
    width: 34px; height: 2px;
    background: var(--gold);
    margin-bottom: 14px;
  }}

  .grid-2 {{ display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 40px; }}
  @media (max-width: 780px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

  .panel {{
    background: var(--near-black);
    color: #f2ece1;
    padding: 32px;
  }}
  .panel h3 {{
    font-family: var(--font-display);
    font-size: 1.35rem;
    color: var(--gold);
    margin-bottom: 18px;
    font-weight: 600;
  }}
  .hours-row {{
    display: flex;
    justify-content: space-between;
    padding: 9px 0;
    border-bottom: 1px solid rgba(242,236,225,0.14);
    font-size: 0.92rem;
  }}
  .hours-row:last-child {{ border-bottom: none; }}
  .hours-row.closed span:last-child {{ color: #a89e8e; }}
  .contact-block {{ margin-top: 22px; }}
  .contact-block a {{
    display: block;
    text-decoration: none;
    color: #f2ece1;
    font-size: 0.95rem;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(242,236,225,0.2);
    padding-bottom: 8px;
  }}

  .map-wrap {{ border: 1px solid var(--line); }}
  .map-wrap iframe {{ width: 100%; height: 320px; border: 0; display: block; filter: grayscale(0.25) sepia(0.12); }}

  .cta-band {{
    background: linear-gradient(120deg, var(--walnut-deep), var(--walnut));
    color: #f7f2ea;
    text-align: center;
    padding: 70px 24px;
  }}
  .cta-band h2 {{ color: #f7f2ea; }}
  .cta-band p {{ color: #e6dccb; max-width: 52ch; margin: 0 auto 30px; }}

  footer {{
    background: var(--near-black);
    padding: 36px 0;
    text-align: center;
    color: #a89e8e;
    font-size: 0.85rem;
  }}
  footer .foot-brand {{ font-family: var(--font-display); color: #f2ece1; font-size: 1.15rem; margin-bottom: 8px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">Keukens <span>Konings</span></div>
    <nav><a href="#contact">Showroom &amp; contact</a></nav>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="hero-inner">
      <div class="kicker">Massief eiken · Maatwerk · Eigen atelier</div>
      <h1>{tagline}</h1>
      <p>{about}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#contact">{cta}</a>
        <a class="btn btn-secondary" href="tel:{esc(tel_href)}">Bel {phone}</a>
      </div>
    </div>
  </div>
  <div class="swatch-row">
    {swatches_html}
  </div>
</section>

<section class="about-section">
  <div class="wrap about-grid">
    <div>
      <h2>Waarom {name}</h2>
      <p>Een keuken is meer dan een werkplek — het is het hart van de leefruimte. Daarom houdt {name} elk traject in eigen hand: van eerste schets tot productie in het eigen atelier en plaatsing tot in het kleinste detail.</p>
    </div>
    <ul class="highlights-list">
      {highlights_html}
    </ul>
  </div>
</section>

<section class="services-section">
  <div class="wrap">
    <h2>Wat we maken</h2>
    <ul class="services-list">
      {services_html}
    </ul>
  </div>
</section>

<section id="contact">
  <div class="wrap grid-2">
    <div class="panel">
      <h3>Showroom</h3>
      {hours_html}
      <div class="contact-block">
        <a href="tel:{esc(tel_href)}">{phone}</a>
        <a href="mailto:{email}">{email}</a>
        <a href="https://www.google.com/maps?q={maps_q}" target="_blank" rel="noopener">{address}</a>
      </div>
    </div>
    <div class="map-wrap">
      <iframe loading="lazy" src="https://www.google.com/maps?q={maps_q}&output=embed"></iframe>
    </div>
  </div>
</section>

<div class="cta-band">
  <h2>{cta}</h2>
  <p>Bezoek de showroom in Essen en ontdek massief eiken keukens op maat, van landelijk tot strak modern — een afspraak vooraf is welkom.</p>
  <a class="btn btn-primary" href="mailto:{email}">Neem contact op</a>
</div>

<footer>
  <div class="foot-brand">{name}</div>
  <div>{address} · {phone}</div>
</footer>

</body>
</html>"""
