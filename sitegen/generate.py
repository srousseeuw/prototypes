#!/usr/bin/env python3
"""
Site generator voor prototype.ocior.be
Gebruik: python3 generate.py briefs/<bedrijf>.json
Output:  output/<slug>/index.html  (klaar om te pushen naar GitHub/Cloudflare Pages)
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def build_hours_rows(hours):
    rows = []
    for day, time in hours:
        closed = "closed" if "esloten" in time or "losed" in time else ""
        rows.append(f'<div class="hours-row {closed}"><span>{esc(day)}</span><span>{esc(time)}</span></div>')
    return "\n".join(rows)

def build_highlights(items):
    lis = [f'<li><span class="mark">—</span>{esc(i)}</li>' for i in items]
    return "\n".join(lis)

def render(brief: dict) -> str:
    name = esc(brief["business_name"])
    category = esc(brief.get("category", ""))
    tagline = esc(brief.get("tagline", ""))
    address = esc(brief.get("address", ""))
    phone = esc(brief.get("phone", ""))
    about = esc(brief.get("about", ""))
    cta = esc(brief.get("cta_text", "Neem contact op"))
    rating = brief.get("rating")
    rating_count = brief.get("rating_count")
    hours_html = build_hours_rows(brief.get("hours", []))
    highlights_html = build_highlights(brief.get("highlights", []))
    maps_query = address.replace(" ", "+")

    rating_block = ""
    if rating:
        rating_block = f'''<div class="rating">
            <span class="stars">★★★★★</span>
            <span class="rating-text">{rating} / 5 — {rating_count or ""} beoordelingen</span>
        </div>'''

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {category}</title>
<meta name="description" content="{tagline}. {address}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --crust: #2b1c14;
    --crumb: #fbf3e7;
    --jam: #b23a2e;
    --gold: #d9a441;
    --line: #e7d9c3;
    --ink-soft: #6b5a48;
    --font-display: 'Fraunces', serif;
    --font-body: 'Inter', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--crumb);
    color: var(--crust);
    line-height: 1.5;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{
    padding: 20px 0;
    border-bottom: 1px solid var(--line);
  }}
  header.top .wrap {{
    display: flex; justify-content: space-between; align-items: center;
  }}
  .brand {{
    font-family: var(--font-display);
    font-weight: 600;
    font-size: 1.25rem;
    letter-spacing: -0.01em;
  }}
  .top-cta {{
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.9rem;
    background: var(--crust);
    color: var(--crumb);
    padding: 10px 18px;
    border-radius: 999px;
    text-decoration: none;
  }}

  .hero {{
    padding: 72px 0 56px;
    position: relative;
  }}
  .hero .wrap {{
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 48px;
    align-items: center;
  }}
  .eyebrow {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--jam);
    font-weight: 600;
    margin-bottom: 14px;
  }}
  h1 {{
    font-family: var(--font-display);
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.01em;
    margin-bottom: 18px;
  }}
  .tagline {{
    font-size: 1.15rem;
    color: var(--ink-soft);
    max-width: 42ch;
    margin-bottom: 28px;
  }}
  .rating {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 28px;
    font-size: 0.92rem;
  }}
  .stars {{ color: var(--gold); letter-spacing: 2px; }}
  .rating-text {{ color: var(--ink-soft); }}
  .hero-cta {{
    display: inline-block;
    background: var(--jam);
    color: var(--crumb);
    font-weight: 600;
    padding: 14px 28px;
    border-radius: 999px;
    text-decoration: none;
    font-size: 0.98rem;
  }}

  .stamp {{
    justify-self: end;
    width: 190px; height: 190px;
    border: 2px solid var(--crust);
    border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    transform: rotate(-6deg);
    font-family: var(--font-display);
    padding: 20px;
  }}
  .stamp .small {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; color: var(--jam); font-weight: 600; margin-bottom: 6px; }}
  .stamp .big {{ font-size: 1.5rem; font-weight: 700; line-height: 1.1; }}

  section {{ padding: 56px 0; }}
  .about {{ border-top: 1px solid var(--line); }}
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
  }}
  .about p {{ color: var(--ink-soft); font-size: 1.02rem; }}
  ul.highlights {{ list-style: none; }}
  ul.highlights li {{
    display: flex; gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.98rem;
  }}
  .mark {{ color: var(--jam); font-weight: 700; }}

  .info {{ background: var(--crust); color: var(--crumb); }}
  .info .wrap {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }}
  .info h2 {{ color: var(--crumb); }}
  .hours-row {{
    display: flex; justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(251,243,231,0.15);
    font-size: 0.94rem;
  }}
  .hours-row.closed span:last-child {{ color: var(--gold); }}
  .contact-block p {{ margin-bottom: 10px; color: rgba(251,243,231,0.85); }}
  .contact-block a.map-link {{
    display: inline-block;
    margin-top: 14px;
    font-weight: 600;
    color: var(--gold);
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
    .stamp {{ justify-self: start; margin-top: 12px; }}
  }}

  a:focus-visible, .hero-cta:focus-visible {{ outline: 2px solid var(--jam); outline-offset: 3px; }}
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
    <div>
      <div class="eyebrow">{category}</div>
      <h1>{tagline}</h1>
      <p class="tagline">{about}</p>
      {rating_block}
      <a class="hero-cta" href="#info">{cta}</a>
    </div>
    <div class="stamp">
      <div class="small">Vers gebakken</div>
      <div class="big">Elke dag<br>opnieuw</div>
    </div>
  </div>
</section>

<section class="about">
  <div class="wrap">
    <div>
      <h2>Waarom {name}</h2>
      <p>{about}</p>
    </div>
    <div>
      <h2>Wat je vindt</h2>
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
      <a class="map-link" href="https://www.google.com/maps/search/?api=1&query={maps_query}" target="_blank" rel="noopener">Bekijk op kaart →</a>
    </div>
  </div>
</section>

<footer>
  Prototype gebouwd voor {name} · <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
</footer>

</body>
</html>
"""

def main():
    if len(sys.argv) != 2:
        print("Gebruik: python3 generate.py briefs/<bedrijf>.json")
        sys.exit(1)

    brief_path = Path(sys.argv[1])
    brief = json.loads(brief_path.read_text(encoding="utf-8"))

    out_dir = ROOT / "output" / brief["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    html = render(brief)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Gegenereerd: {out_dir / 'index.html'}")

if __name__ == "__main__":
    main()
