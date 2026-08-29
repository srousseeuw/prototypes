from .common import esc, build_hours_rows, build_highlights, maps_query as _maps_query


def _build_services(items):
    lis = [f'<li class="svc"><span class="svc-tick"></span>{esc(i)}</li>' for i in items]
    return "\n".join(lis)


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Bel voor een afspraak"))
    area = esc(brief.get("service_area", ""))
    hours_note = esc(brief.get("hours_note", ""))
    hours_html = build_hours_rows(brief.get("hours", [])) if brief.get("hours") else (
        f'<p class="hours-note-text">{hours_note}</p>' if hours_note else ""
    )
    highlights_html = build_highlights(brief.get("highlights", []), mark="✓")
    services_html = _build_services(brief.get("services", []))
    maps_q = _maps_query(address)

    eyebrow = esc(brief.get("eyebrow", "Karweibedrijf"))
    stat1_value = esc(str(brief.get("stat1_value", "1")))
    stat1_label = esc(brief.get("stat1_label", "vakman, rechtstreeks contact"))
    stat2_value = esc(brief.get("stat2_value", ""))
    stat2_label = esc(brief.get("stat2_label", "werkgebied"))

    mail_btn = f'<a class="btn btn-ghost" href="mailto:{email}">Mail ons</a>' if email else ""
    email_row = (
        f'<div class="info-row"><span>E-mail</span><a href="mailto:{email}">{email}</a></div>'
        if email else ""
    )

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #221f1a;
    --orange: #dd5c1e;
    --orange-deep: #a8420f;
    --steel: #383d45;
    --steel-deep: #23262c;
    --paper: #f2f0ea;
    --paper-dim: #e7e3d9;
    --line: #d8d2c2;
    --font-mono: 'JetBrains Mono', monospace;
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
  .wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 24px; }}

  /* hazard-tape signature strip: the visual shorthand for "vakwerk" */
  .tape {{
    background-image: repeating-linear-gradient(
      135deg,
      var(--orange) 0px, var(--orange) 22px,
      var(--steel-deep) 22px, var(--steel-deep) 44px
    );
    height: 10px;
  }}

  /* ruler-tick pattern used behind the hero, echoing a tape measure */
  .ticks {{
    background-image: repeating-linear-gradient(
      90deg,
      rgba(242,240,234,0.14) 0px, rgba(242,240,234,0.14) 1px,
      transparent 1px, transparent 28px
    ), repeating-linear-gradient(
      90deg,
      rgba(242,240,234,0.28) 0px, rgba(242,240,234,0.28) 2px,
      transparent 2px, transparent 140px
    );
  }}

  header.top {{
    background: var(--steel-deep);
    padding: 16px 0;
  }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .brand {{
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 1.05rem;
    color: #fff;
    letter-spacing: -0.01em;
  }}
  .brand span {{ color: var(--orange); }}
  .top-cta {{
    font-family: var(--font-mono);
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--steel-deep);
    background: #fff;
    padding: 9px 18px;
    border-radius: 3px;
    text-decoration: none;
  }}

  .hero {{
    position: relative;
    padding: 64px 0 52px;
    color: #fff;
    background: var(--steel-deep);
    overflow: hidden;
  }}
  .hero .ticks {{ position: absolute; inset: 0; }}
  .hero::after {{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(20,22,26,0.15), rgba(15,16,19,0.85));
  }}
  .hero .wrap {{ position: relative; z-index: 1; }}
  .hero .eyebrow {{
    display: inline-block;
    font-family: var(--font-mono);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.72rem;
    color: var(--steel-deep);
    background: var(--orange);
    padding: 5px 12px;
    border-radius: 2px;
    margin-bottom: 18px;
    transform: rotate(-1deg);
  }}
  .hero h1 {{
    font-family: var(--font-body);
    font-weight: 700;
    font-size: clamp(2rem, 5vw, 3.1rem);
    letter-spacing: -0.02em;
    max-width: 18ch;
    margin-bottom: 16px;
  }}
  .hero p.tag {{
    font-size: 1.1rem;
    max-width: 46ch;
    color: #ece9e1;
    margin-bottom: 28px;
  }}
  .hero-actions {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .btn {{
    display: inline-block;
    font-family: var(--font-mono);
    font-weight: 600;
    font-size: 0.9rem;
    padding: 13px 26px;
    border-radius: 3px;
    text-decoration: none;
  }}
  .btn-primary {{ background: var(--orange); color: #fff; }}
  .btn-ghost {{ background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.5); }}

  .stat-strip {{
    background: var(--steel);
    color: var(--paper);
    padding: 18px 0;
  }}
  .stat-strip .wrap {{
    display: flex; gap: 28px; flex-wrap: wrap; justify-content: space-between;
    font-family: var(--font-mono);
    font-weight: 600;
    font-size: 0.88rem;
  }}
  .stat-strip .stat b {{ color: var(--orange); font-size: 1.1rem; margin-right: 6px; }}

  section {{ padding: 56px 0; }}
  h2 {{
    font-family: var(--font-body);
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 8px;
    color: var(--steel-deep);
  }}
  .section-sub {{ color: #55524a; margin-bottom: 28px; max-width: 56ch; }}

  .services-grid {{
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
  }}
  .svc {{
    background: #fff;
    border: 1px solid var(--line);
    border-left: 4px solid var(--orange);
    border-radius: 4px;
    padding: 18px 20px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .svc-tick {{
    flex-shrink: 0;
    width: 3px; height: 18px;
    background: var(--steel-deep);
  }}

  .split {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 40px;
    align-items: start;
  }}
  @media (max-width: 780px) {{ .split {{ grid-template-columns: 1fr; }} }}

  .about-card {{
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 28px;
  }}
  .about-card p {{ margin-bottom: 14px; color: #33312b; }}
  ul.highlights {{ list-style: none; margin-top: 16px; }}
  ul.highlights li {{
    display: flex; gap: 10px; align-items: flex-start;
    padding: 8px 0;
    border-bottom: 1px dashed var(--line);
    font-size: 0.95rem;
  }}
  ul.highlights li:last-child {{ border-bottom: none; }}
  ul.highlights .mark {{
    flex-shrink: 0;
    width: 22px; height: 22px;
    background: var(--orange);
    color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: var(--font-mono);
  }}

  .info-card {{
    background: var(--steel-deep);
    color: #fff;
    border-radius: 6px;
    padding: 28px;
  }}
  .info-card h3 {{
    font-family: var(--font-mono);
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 14px;
    color: var(--orange);
  }}
  .info-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 7px 0; font-size: 0.92rem; border-bottom: 1px solid rgba(255,255,255,0.14); }}
  .info-row span:first-child {{ color: #b8b4a8; font-family: var(--font-mono); font-size: 0.8rem; }}
  .info-row a {{ text-decoration: none; color: #fff; font-weight: 600; }}

  .hours-block {{ margin-top: 18px; }}
  .hours-row {{ display: flex; justify-content: space-between; font-size: 0.88rem; padding: 4px 0; }}
  .hours-row.closed {{ opacity: 0.55; }}
  .hours-note-text {{ font-size: 0.88rem; color: #d8d4c8; }}

  .area-strip {{
    background: var(--paper-dim);
    border: 1px dashed var(--orange-deep);
    border-radius: 4px;
    padding: 14px 18px;
    margin-top: 18px;
    font-size: 0.88rem;
    color: var(--steel-deep);
  }}

  .cta-band {{
    background: var(--steel-deep);
    color: #fff;
    padding: 48px 0;
    text-align: center;
  }}
  .cta-band h2 {{ color: #fff; }}
  .cta-band .btn-primary {{ margin-top: 18px; }}

  footer {{
    background: var(--ink);
    color: #b8b4a8;
    padding: 26px 0;
    font-size: 0.82rem;
    text-align: center;
  }}
  footer a {{ color: var(--orange); }}
</style>
</head>
<body>

<div class="tape"></div>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="top-cta" href="tel:{phone}">Bel direct</a>
  </div>
</header>

<section class="hero ticks">
  <div class="wrap">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{name}</h1>
    <p class="tag">{tagline}</p>
    <div class="hero-actions">
      <a class="btn btn-primary" href="tel:{phone}">{cta}</a>
      {mail_btn}
    </div>
  </div>
</section>

<div class="stat-strip">
  <div class="wrap">
    <div class="stat"><b>{stat1_value}</b>{stat1_label}</div>
    <div class="stat"><b>{stat2_value}</b>{stat2_label}</div>
    <div class="stat"><b>op maat</b>vrijblijvend advies</div>
  </div>
</div>

<section id="diensten">
  <div class="wrap">
    <h2>Wat Ad Dockx voor u doet</h2>
    <p class="section-sub">Karwei- en onderhoudswerk aan woningen in de ruimste zin van het woord — geen klus te gek.</p>
    <ul class="services-grid">
      {services_html}
    </ul>
  </div>
</section>

<div class="tape"></div>

<section id="over" style="background:#fff;">
  <div class="wrap split">
    <div class="about-card">
      <h2>Over {name}</h2>
      <p>{about}</p>
      <ul class="highlights">
        {highlights_html}
      </ul>
    </div>
    <div class="info-card">
      <h3>Contact &amp; praktisch</h3>
      <div class="info-row"><span>Adres</span><a href="https://www.google.com/maps/search/?api=1&query={maps_q}" target="_blank" rel="noopener">{address}</a></div>
      <div class="info-row"><span>Telefoon</span><a href="tel:{phone}">{phone}</a></div>
      {email_row}
      <div class="hours-block">
        {hours_html}
      </div>
      <div class="area-strip">Werkgebied: {area}</div>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>Een klus die opgelost moet worden?</h2>
    <p style="color:#d8d4c8;">{"Bel of mail" if email else "Bel"} voor een vrijblijvend advies — persoonlijk contact, geen tussenpersoon.</p>
    <a class="btn btn-primary" href="tel:{phone}">{cta}</a>
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
