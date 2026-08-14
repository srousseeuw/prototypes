"""Sjabloon voor een sushi- / Aziatische afhaal- en leverzaak.

Visuele identiteit: aizome-indigo (het diepe blauw van Japans geverfd katoen),
rijstwit en een zalmoranje accent. Signature element is het seigaiha-golfpatroon
in de hero, in pure CSS getekend — geen afbeeldingen, geen neon-op-zwart.
De pagina is gebouwd rond de eigenlijke conversie van zo'n zaak: bestellen,
afhalen of laten leveren.

Velden in de brief:
  business_name, category, tagline, address, phone, email, about, cta_text
  order_url          (str)  -> knop "Bestel online"
  service_modes      (list[{title, desc, meta}])  -> afhalen / leveren kaarten
  menu_sections      (list[{title, items:[str]}]) -> kaartoverzicht
  menu_note          (str)  -> voetnoot onder de kaart
  highlights         (list[str])
  hours              (list[[dag, uren]])
  hours_note         (str)
"""
from .common import esc, build_hours_rows, maps_query as _maps_query


def _tel(phone):
    return "".join(c for c in str(phone) if c.isdigit() or c == "+")


def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    tel = _tel(brief.get("phone", ""))
    email = esc(brief.get("email", ""))
    about = esc(brief.get("about", ""))
    intro = esc(brief.get("intro", "")) or about
    cta = esc(brief.get("cta_text", "Bekijk de kaart"))
    order_url = esc(brief.get("order_url", ""))
    menu_note = esc(brief.get("menu_note", ""))
    hours_note = esc(brief.get("hours_note", ""))
    hours_html = build_hours_rows(brief.get("hours", []))
    maps_q = _maps_query(brief.get("address", ""))

    order_btn = (
        f'<a class="btn btn-solid" href="{order_url}" target="_blank" rel="noopener">Bestel online</a>'
        if order_url else
        f'<a class="btn btn-solid" href="tel:{tel}">Bel om te bestellen</a>'
    )

    # --- afhalen / leveren ------------------------------------------------
    modes = brief.get("service_modes", [])
    modes_section = ""
    if modes:
        cards = "\n".join(
            f'''<article class="mode">
          <h3>{esc(m.get("title", ""))}</h3>
          <p>{esc(m.get("desc", ""))}</p>
          <p class="meta">{esc(m.get("meta", ""))}</p>
        </article>'''
            for m in modes
        )
        modes_section = f'''<section class="modes" id="bestellen">
  <div class="wrap">
    <p class="eyebrow">Afhalen of leveren</p>
    <h2>Twee manieren om thuis te eten</h2>
    <div class="mode-grid">
      {cards}
    </div>
  </div>
</section>'''

    # --- kaart ------------------------------------------------------------
    sections = brief.get("menu_sections", [])
    menu_section = ""
    if sections:
        blocks = []
        for s in sections:
            items = "".join(
                f'<li>{esc(i)}</li>' for i in s.get("items", [])
            )
            blocks.append(
                f'''<div class="menu-block">
          <h3>{esc(s.get("title", ""))}</h3>
          <ul>{items}</ul>
        </div>'''
            )
        note = f'<p class="menu-note">{menu_note}</p>' if menu_note else ""
        menu_section = f'''<section class="menu" id="kaart">
  <div class="wrap">
    <p class="eyebrow light">De kaart</p>
    <h2>Van nigiri tot pad thai</h2>
    <div class="menu-grid">
      {"".join(blocks)}
    </div>
    {note}
  </div>
</section>'''

    # --- over ons ---------------------------------------------------------
    highlights = brief.get("highlights", [])
    hl_html = ""
    if highlights:
        hl_html = "<ul class=\"points\">" + "".join(
            f"<li>{esc(h)}</li>" for h in highlights
        ) + "</ul>"
    about_section = ""
    if about or hl_html:
        about_section = f'''<section class="over" id="over">
  <div class="wrap over-grid">
    <div>
      <p class="eyebrow">Over ons</p>
      <h2>Elke dag vers gesneden</h2>
      <p class="body-lg">{about}</p>
    </div>
    <div>{hl_html}</div>
  </div>
</section>'''

    email_p = f'<p><a class="plain" href="mailto:{email}">{email}</a></p>' if email else ""
    hours_note_p = f'<p class="hours-note">{hours_note}</p>' if hours_note else ""

    nav_items = [("#bestellen", "Bestellen", bool(modes)),
                 ("#kaart", "Kaart", bool(sections)),
                 ("#over", "Over ons", bool(about_section)),
                 ("#contact", "Contact", True)]
    nav_html = "\n".join(
        f'<a href="{href}">{label}</a>' for href, label, show in nav_items if show
    )

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}. {phone}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --indigo:      #16233d;
    --indigo-deep: #0e182c;
    --indigo-soft: #2c4471;
    --rice:        #f5f2ec;
    --rice-warm:   #eae5db;
    --salmon:      #e2704f;
    --salmon-soft: #f0a488;
    --ink:         #141b2a;
    --ink-soft:    #5a6478;
    --line:        #ddd6c9;
    --display: 'Shippori Mincho', Georgia, serif;
    --body: 'Zen Kaku Gothic New', system-ui, sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    font-family: var(--body);
    background: var(--rice);
    color: var(--ink);
    line-height: 1.65;
    -webkit-text-size-adjust: 100%;
    overflow-x: hidden;
  }}
  a {{ color: inherit; }}
  .wrap {{ width: 100%; max-width: 1060px; margin: 0 auto; padding: 0 22px; }}

  h1, h2, h3 {{ font-family: var(--display); font-weight: 600; line-height: 1.2; }}
  h2 {{ font-size: clamp(1.55rem, 3.4vw, 2.2rem); margin-bottom: 16px; }}
  h3 {{ font-size: 1.08rem; margin-bottom: 8px; }}

  .eyebrow {{
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.22em;
    font-weight: 700; color: var(--salmon); margin-bottom: 10px;
  }}
  .eyebrow.light {{ color: var(--salmon-soft); }}

  /* ---------- header ---------- */
  header.top {{
    position: sticky; top: 0; z-index: 40;
    background: rgba(22,35,61,0.97);
    color: var(--rice);
    border-bottom: 1px solid rgba(245,242,236,0.12);
  }}
  header.top .wrap {{ display: flex; align-items: center; gap: 14px; min-height: 62px; flex-wrap: wrap; }}
  .brand {{ font-family: var(--display); font-size: 1.2rem; font-weight: 700; margin-right: auto; white-space: nowrap; }}
  nav.main {{ display: flex; gap: 2px; flex-wrap: wrap; }}
  nav.main a {{
    display: inline-flex; align-items: center; min-height: 44px; padding: 0 12px;
    text-decoration: none; font-size: 0.88rem; font-weight: 500;
    color: rgba(245,242,236,0.8); border-radius: 6px;
  }}
  nav.main a:hover {{ color: #fff; background: rgba(255,255,255,0.10); }}

  /* ---------- hero met seigaiha-golven ---------- */
  .hero {{
    position: relative; overflow: hidden;
    background: var(--indigo);
    color: var(--rice);
    padding: 66px 0 76px;
  }}
  .hero::after {{
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 190px;
    opacity: 0.5; pointer-events: none;
    background-image:
      radial-gradient(circle at 50% 100%, transparent 26px, rgba(240,164,136,0.55) 27px, transparent 28px),
      radial-gradient(circle at 50% 100%, transparent 17px, rgba(240,164,136,0.42) 18px, transparent 19px),
      radial-gradient(circle at 50% 100%, transparent 8px, rgba(240,164,136,0.3) 9px, transparent 10px);
    background-size: 76px 38px;
    background-position: 0 0, 0 0, 0 0;
    -webkit-mask-image: linear-gradient(to bottom, transparent, #000);
    mask-image: linear-gradient(to bottom, transparent, #000);
  }}
  .hero .wrap {{ position: relative; z-index: 1; }}
  .hero .kicker {{
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.24em;
    font-weight: 700; color: var(--salmon-soft); margin-bottom: 18px;
  }}
  .hero h1 {{
    font-size: clamp(2.1rem, 5.6vw, 3.4rem);
    font-weight: 700; margin-bottom: 18px; max-width: 18ch;
  }}
  .hero p.sub {{ font-size: 1.06rem; color: rgba(245,242,236,0.84); max-width: 52ch; margin-bottom: 30px; }}
  .hero-btns {{ display: flex; gap: 12px; flex-wrap: wrap; }}

  .btn {{
    display: inline-flex; align-items: center; justify-content: center;
    min-height: 48px; padding: 0 24px;
    border-radius: 999px; text-decoration: none;
    font-weight: 700; font-size: 0.94rem;
    border: 2px solid transparent;
  }}
  .btn-solid {{ background: var(--salmon); color: #fff; }}
  .btn-solid:hover {{ background: #cf5f40; }}
  .btn-ghost {{ border-color: rgba(245,242,236,0.55); color: var(--rice); }}
  .btn-ghost:hover {{ background: rgba(255,255,255,0.10); }}

  /* ---------- secties ---------- */
  section {{ padding: 62px 0; }}
  .body-lg {{ font-size: 1.03rem; color: var(--ink-soft); }}

  .modes {{ background: var(--rice); }}
  .mode-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 18px; margin-top: 26px; }}
  .mode {{
    background: #fff; border: 1px solid var(--line);
    border-radius: 14px; padding: 24px 22px;
  }}
  .mode h3 {{ color: var(--indigo); }}
  .mode p {{ font-size: 0.95rem; color: var(--ink-soft); }}
  .mode p.meta {{
    margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--line);
    font-size: 0.87rem; color: var(--indigo-soft); font-weight: 500;
  }}

  /* ---------- kaart ---------- */
  .menu {{ background: var(--indigo-deep); color: var(--rice); }}
  .menu h2 {{ color: var(--rice); }}
  .menu-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 26px; margin-top: 28px; }}
  .menu-block h3 {{
    color: var(--salmon-soft); padding-bottom: 8px;
    border-bottom: 1px solid rgba(245,242,236,0.18); margin-bottom: 12px;
  }}
  .menu-block ul {{ list-style: none; }}
  .menu-block li {{
    font-size: 0.93rem; color: rgba(245,242,236,0.82);
    padding: 5px 0 5px 16px; position: relative;
  }}
  .menu-block li::before {{
    content: ""; position: absolute; left: 0; top: 13px;
    width: 6px; height: 6px; border-radius: 50%; background: var(--salmon);
  }}
  .menu-note {{ margin-top: 26px; font-size: 0.87rem; color: rgba(245,242,236,0.6); }}

  /* ---------- over ---------- */
  .over {{ background: var(--rice-warm); }}
  .over-grid {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 44px; align-items: start; }}
  ul.points {{ list-style: none; }}
  ul.points li {{
    position: relative; padding: 12px 0 12px 28px;
    border-bottom: 1px solid var(--line); font-size: 0.96rem;
  }}
  ul.points li:first-child {{ border-top: 1px solid var(--line); }}
  ul.points li::before {{
    content: ""; position: absolute; left: 2px; top: 21px;
    width: 10px; height: 10px; border-radius: 50%;
    border: 2px solid var(--salmon);
  }}

  /* ---------- contact ---------- */
  .contact {{ background: var(--indigo); color: var(--rice); }}
  .contact h2 {{ color: var(--rice); }}
  .contact .wrap {{ display: grid; grid-template-columns: 1fr 1fr; gap: 44px; }}
  .hours-row {{
    display: flex; justify-content: space-between; gap: 12px;
    padding: 11px 0; border-bottom: 1px solid rgba(245,242,236,0.16);
    font-size: 0.95rem;
  }}
  .hours-row:first-child {{ border-top: 1px solid rgba(245,242,236,0.16); }}
  .hours-row.closed span:last-child {{ color: var(--salmon-soft); font-weight: 700; }}
  .hours-note {{ margin-top: 12px; font-size: 0.86rem; color: rgba(245,242,236,0.6); }}
  .contact p {{ color: rgba(245,242,236,0.86); margin-bottom: 8px; }}
  a.plain {{ color: var(--salmon-soft); text-decoration: underline; text-underline-offset: 3px; }}
  a.map-link {{
    display: inline-flex; align-items: center; min-height: 44px;
    margin-top: 6px; font-weight: 700; font-size: 0.92rem;
    color: var(--salmon-soft); text-decoration: none;
  }}
  a.map-link:hover {{ text-decoration: underline; }}

  footer {{
    background: var(--indigo-deep); color: rgba(245,242,236,0.6);
    padding: 26px 0; text-align: center; font-size: 0.82rem;
  }}
  footer a {{ color: var(--salmon-soft); }}

  a:focus-visible, .btn:focus-visible {{ outline: 3px solid var(--salmon-soft); outline-offset: 3px; border-radius: 6px; }}

  @media (max-width: 860px) {{
    .over-grid, .contact .wrap {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 620px) {{
    header.top .wrap {{ padding-top: 8px; padding-bottom: 8px; }}
    .brand {{ width: 100%; margin-right: 0; }}
    nav.main {{ width: 100%; }}
    nav.main a {{ padding: 0 10px; font-size: 0.84rem; }}
    section {{ padding: 46px 0; }}
    .hero {{ padding: 44px 0 60px; }}
    .hero-btns .btn {{ flex: 1 1 100%; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <span class="brand">{name}</span>
    <nav class="main" aria-label="Hoofdnavigatie">
      {nav_html}
    </nav>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <p class="kicker">{category}</p>
    <h1>{tagline}</h1>
    <p class="sub">{intro}</p>
    <div class="hero-btns">
      {order_btn}
      <a class="btn btn-ghost" href="#kaart">{cta}</a>
    </div>
  </div>
</section>

{modes_section}

{menu_section}

{about_section}

<section class="contact" id="contact">
  <div class="wrap">
    <div>
      <p class="eyebrow light">Openingsuren</p>
      <h2>Wanneer we open zijn</h2>
      {hours_html}
      {hours_note_p}
    </div>
    <div>
      <p class="eyebrow light">Contact</p>
      <h2>Waar je ons vindt</h2>
      <p>{address}</p>
      <p><a class="plain" href="tel:{tel}">{phone}</a></p>
      {email_p}
      <a class="map-link" href="https://www.google.com/maps/search/?api=1&amp;query={maps_q}" target="_blank" rel="noopener">Route op Google Maps &rarr;</a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    Websiteprototype voor {name} · gemaakt door <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
  </div>
</footer>

</body>
</html>
"""
