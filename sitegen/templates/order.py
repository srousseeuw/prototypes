"""
Herbruikbare online-bestelpagina voor horecaprototypes.

Een sjabloon roept render(brief, theme) aan; theme bepaalt de kleuren zodat de
bestelpagina bij de hoofdsite van dat prototype past. De kaart komt uit het
"order_menu" veld van de brief:

  "order_menu": [
    {"category": "Pizza", "note": "...", "items": [
        {"name": "Margherita", "desc": "...", "price": 12.5}
    ]}
  ]

Als prijzen nog niet geverifieerd zijn, zet "menu_prices_verified": false in de
brief — de pagina toont dan bovenaan een duidelijke waarschuwing, zodat een
demo nooit voor een echte prijslijst kan doorgaan.
"""
from .common import esc

DEFAULT_THEME = {
    "bg": "#123b3a",
    "bg_deep": "#0b2726",
    "accent": "#eaa42e",
    "paper": "#faf6ee",
    "ink": "#14171c",
    "font_display": "'Fjalla One', sans-serif",
    "font_body": "'Work Sans', sans-serif",
    "fonts_href": "https://fonts.googleapis.com/css2?family=Fjalla+One&family=Work+Sans:wght@400;500;600;700&display=swap",
}

def _money(value):
    return f"{value:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")

def render(brief: dict, theme: dict = None) -> str:
    t = {**DEFAULT_THEME, **(theme or {})}
    name = esc(brief["business_name"])
    slug = esc(brief["slug"])
    phone = esc(brief.get("phone", ""))
    address = esc(brief.get("address", ""))
    phone_href = phone.replace(" ", "").replace("(0)", "")
    menu = brief.get("order_menu", [])
    prices_verified = brief.get("menu_prices_verified", True)
    deals = brief.get("order_deals", [])

    disclaimer = ""
    if not prices_verified:
        disclaimer = """  <div class="notice">
    <strong>Voorbeeldkaart.</strong> De gerechten en prijzen hieronder zijn ter illustratie ingevuld
    om te tonen hoe online bestellen eruit kan zien. De echte kaart en prijzen worden overgenomen
    van de zaak zelf voor dit live gaat.
  </div>"""

    # Korte promo's blijven pillen; die zijn kort genoeg.
    deals_html = ""
    if deals:
        chips = "\n".join(f'      <span class="deal">{esc(d)}</span>' for d in deals)
        deals_html = f"""  <div class="deals">
{chips}
  </div>"""

    # Afhalen/leveren is een zin, geen label — dus een kaartje, geen pil.
    service_html = ""
    service = brief.get("order_service", [])
    if service:
        kaarten = "\n".join(
            f"""      <div class="svc-card">
        <span class="svc-title">{esc(s.get('title', ''))}</span>
        <span class="svc-detail">{esc(s.get('detail', ''))}</span>
        {f'<span class="svc-meta">{esc(s["meta"])}</span>' if s.get("meta") else ""}
      </div>"""
            for s in service
        )
        service_html = f"""  <div class="services">
{kaarten}
  </div>"""

    sections = []
    for cat_index, category in enumerate(menu):
        cat_name = esc(category.get("category", ""))
        cat_note = esc(category.get("note", ""))
        note_html = f'<p class="cat-note">{cat_note}</p>' if cat_note else ""
        rows = []
        for item_index, item in enumerate(category.get("items", [])):
            item_id = f"{cat_index}-{item_index}"
            item_name = esc(item.get("name", ""))
            item_desc = esc(item.get("desc", ""))
            price = float(item.get("price", 0))
            desc_html = f'<span class="item-desc">{item_desc}</span>' if item_desc else ""
            rows.append(f"""        <li class="item">
          <div class="item-text">
            <span class="item-name">{item_name}</span>
            {desc_html}
          </div>
          <div class="item-buy">
            <span class="item-price">&euro;&nbsp;{_money(price)}</span>
            <button class="add" type="button"
              data-id="{item_id}" data-name="{item_name}" data-price="{price:.2f}"
              aria-label="{item_name} toevoegen">+</button>
          </div>
        </li>""")
        sections.append(f"""    <section class="cat" id="cat-{cat_index}">
      <h2>{cat_name}</h2>
      {note_html}
      <ul class="items">
{chr(10).join(rows)}
      </ul>
    </section>""")

    nav_links = "\n".join(
        f'      <a href="#cat-{i}">{esc(c.get("category", ""))}</a>'
        for i, c in enumerate(menu)
    )

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Online bestellen — {name}</title>
<meta name="description" content="Bestel online bij {name}. Kies je gerechten en haal ze af.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{t['fonts_href']}" rel="stylesheet">
<style>
  :root {{
    --bg: {t['bg']};
    --bg-deep: {t['bg_deep']};
    --accent: {t['accent']};
    --paper: {t['paper']};
    --ink: {t['ink']};
    --ink-soft: #5f6570;
    --line: rgba(20,23,28,0.12);
    --font-display: {t['font_display']};
    --font-body: {t['font_body']};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-body);
    background: var(--paper);
    color: var(--ink);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}

  header.top {{ background: var(--bg); color: #fff; padding: 16px 0; }}
  header.top .wrap {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
  .back {{ font-size: 0.88rem; color: rgba(255,255,255,0.8); text-decoration: none; }}
  .back:hover {{ color: #fff; }}
  .brand {{ font-family: var(--font-display); font-size: 1.25rem; letter-spacing: 0.02em; text-transform: uppercase; }}

  .hero {{ background: var(--bg-deep); color: #fff; padding: 34px 0 30px; }}
  .hero h1 {{ font-family: var(--font-display); font-size: clamp(1.8rem, 4vw, 2.5rem); text-transform: uppercase; letter-spacing: 0.01em; margin-bottom: 8px; }}
  .hero p {{ color: rgba(255,255,255,0.75); font-size: 0.98rem; }}

  .notice {{
    background: #fff5d6;
    border-left: 4px solid var(--accent);
    color: #4a3a12;
    font-size: 0.9rem;
    padding: 14px 18px;
    border-radius: 6px;
    margin: 24px 0 0;
  }}
  .deals {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }}
  .deal {{
    background: var(--accent);
    color: var(--bg-deep);
    font-weight: 600;
    font-size: 0.84rem;
    padding: 7px 14px;
    border-radius: 999px;
  }}

  /* Afhalen / leveren: hele zinnen, dus kaartjes in plaats van pillen. */
  .services {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 12px;
    margin-top: 22px;
  }}
  .svc-card {{
    display: flex; flex-direction: column; gap: 3px;
    background: #fff;
    border: 1px solid var(--line);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 14px 16px;
  }}
  .svc-title {{
    font-size: 0.74rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--accent);
  }}
  .svc-detail {{ font-weight: 600; font-size: 1rem; }}
  .svc-meta {{ color: var(--ink-soft); font-size: 0.88rem; }}

  .catnav {{
    position: sticky; top: 0; z-index: 20;
    background: var(--paper);
    border-bottom: 1px solid var(--line);
    margin-top: 26px;
  }}
  /* Op een breed scherm past alles: laten afbreken in plaats van schuiven. */
  .catnav .wrap {{
    display: flex; flex-wrap: wrap; gap: 6px;
    padding-top: 10px; padding-bottom: 10px;
  }}
  .catnav a {{
    white-space: nowrap;
    font-size: 0.86rem; font-weight: 600;
    text-decoration: none;
    padding: 7px 14px;
    border-radius: 999px;
    color: var(--ink-soft);
    border: 1px solid transparent;
  }}
  .catnav a:hover {{ background: rgba(20,23,28,0.06); color: var(--ink); border-color: var(--line); }}

  .layout {{ display: grid; grid-template-columns: 1fr 330px; gap: 40px; align-items: start; padding: 30px 0 80px; }}

  .cat {{ margin-bottom: 34px; scroll-margin-top: 70px; }}
  .cat h2 {{ font-family: var(--font-display); font-size: 1.5rem; text-transform: uppercase; margin-bottom: 6px; }}
  .cat-note {{ color: var(--ink-soft); font-size: 0.9rem; margin-bottom: 12px; }}
  ul.items {{ list-style: none; }}
  .item {{
    display: flex; justify-content: space-between; align-items: center; gap: 16px;
    padding: 14px 0;
    border-bottom: 1px solid var(--line);
  }}
  .item-text {{ display: flex; flex-direction: column; gap: 2px; }}
  .item-name {{ font-weight: 600; }}
  .item-desc {{ color: var(--ink-soft); font-size: 0.88rem; }}
  .item-buy {{ display: flex; align-items: center; gap: 12px; flex-shrink: 0; }}
  .item-price {{ font-variant-numeric: tabular-nums; font-weight: 600; }}
  .add {{
    width: 34px; height: 34px;
    border: 1px solid var(--bg);
    background: var(--bg);
    color: #fff;
    border-radius: 50%;
    font-size: 1.25rem; line-height: 1;
    cursor: pointer;
    transition: transform 0.12s ease, background 0.12s ease;
  }}
  .add:hover {{ background: var(--bg-deep); transform: scale(1.08); }}

  .cart {{
    position: sticky; top: 76px;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 20px;
  }}
  .cart h2 {{ font-family: var(--font-display); font-size: 1.25rem; text-transform: uppercase; margin-bottom: 14px; }}
  .cart-empty {{ color: var(--ink-soft); font-size: 0.9rem; }}
  ul.cart-lines {{ list-style: none; margin-bottom: 14px; }}
  .cart-line {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--line); font-size: 0.92rem; }}
  .qty {{ display: flex; align-items: center; gap: 7px; }}
  .qty button {{
    width: 24px; height: 24px;
    border: 1px solid var(--line); background: #fff;
    border-radius: 50%; cursor: pointer; line-height: 1;
    color: var(--ink);
  }}
  .qty button:hover {{ background: rgba(20,23,28,0.06); }}
  .qty span {{ min-width: 1.2em; text-align: center; font-variant-numeric: tabular-nums; }}
  .line-name {{ flex: 1; }}
  .line-price {{ font-variant-numeric: tabular-nums; }}
  .total {{ display: flex; justify-content: space-between; font-weight: 700; font-size: 1.1rem; padding: 12px 0 16px; }}
  .pickup {{ margin-bottom: 14px; }}
  .pickup label {{ display: block; font-size: 0.82rem; color: var(--ink-soft); margin-bottom: 5px; }}
  .pickup select {{
    width: 100%; padding: 9px 12px;
    border: 1px solid var(--line); border-radius: 8px;
    font-family: inherit; font-size: 0.92rem; background: #fff; color: var(--ink);
  }}
  .checkout {{
    width: 100%;
    background: var(--accent); color: var(--bg-deep);
    font-family: var(--font-body); font-weight: 700; font-size: 0.98rem;
    border: none; border-radius: 8px;
    padding: 14px; cursor: pointer;
  }}
  .checkout:hover {{ filter: brightness(1.06); }}
  .checkout:disabled {{ opacity: 0.45; cursor: not-allowed; }}
  .cart-foot {{ font-size: 0.8rem; color: var(--ink-soft); margin-top: 12px; text-align: center; }}

  dialog {{
    border: none; border-radius: 12px; padding: 28px;
    max-width: 420px; width: calc(100% - 40px);
    color: var(--ink);
  }}
  dialog::backdrop {{ background: rgba(11,39,38,0.55); }}
  dialog h3 {{ font-family: var(--font-display); font-size: 1.4rem; text-transform: uppercase; margin-bottom: 10px; }}
  dialog p {{ color: var(--ink-soft); font-size: 0.94rem; margin-bottom: 8px; }}
  dialog .call {{ display: inline-block; margin-top: 14px; font-weight: 600; color: var(--bg); }}
  dialog button {{
    margin-top: 18px; width: 100%;
    background: var(--bg); color: #fff;
    border: none; border-radius: 8px; padding: 12px;
    font-family: inherit; font-weight: 600; cursor: pointer;
  }}

  footer {{ border-top: 1px solid var(--line); padding: 24px 0 40px; font-size: 0.84rem; color: var(--ink-soft); text-align: center; }}

  @media (max-width: 860px) {{
    .layout {{ grid-template-columns: 1fr; }}
    .cart {{ position: static; }}
  }}

  /* Op een gsm passen twintig categorieën niet op een paar regels, dus daar
     wél schuiven — maar met een zichtbare afloop, zodat het bedoeld oogt. */
  @media (max-width: 700px) {{
    .catnav {{ position: relative; }}
    .catnav .wrap {{
      flex-wrap: nowrap;
      overflow-x: auto;
      scroll-snap-type: x proximity;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
      padding-right: 34px;
    }}
    .catnav .wrap::-webkit-scrollbar {{ display: none; }}
    .catnav a {{ scroll-snap-align: start; }}
    .catnav::after {{
      content: "";
      position: absolute; top: 0; right: 0; bottom: 1px;
      width: 34px;
      pointer-events: none;
      background: linear-gradient(to right, transparent, var(--paper));
    }}
  }}
  a:focus-visible, button:focus-visible, select:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
</style>
</head>
<body>

<header class="top">
  <div class="wrap">
    <div class="brand">{name}</div>
    <a class="back" href="/{slug}/">&larr; Terug naar de site</a>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <h1>Online bestellen</h1>
    <p>Stel je bestelling samen en haal ze af in de {address.split(',')[0] if address else 'zaak'}.</p>
  </div>
</section>

<div class="wrap">
{disclaimer}
{deals_html}
{service_html}
</div>

<nav class="catnav">
  <div class="wrap">
{nav_links}
  </div>
</nav>

<div class="wrap">
  <div class="layout">
    <div>
{chr(10).join(sections)}
    </div>

    <aside class="cart">
      <h2>Je bestelling</h2>
      <p class="cart-empty" id="cart-empty">Nog niets gekozen.</p>
      <ul class="cart-lines" id="cart-lines"></ul>
      <div class="total"><span>Totaal</span><span id="cart-total">&euro;&nbsp;0,00</span></div>
      <div class="pickup">
        <label for="slot">Afhalen om</label>
        <select id="slot">
          <option>Zo snel mogelijk</option>
          <option>17:30</option>
          <option>18:00</option>
          <option>18:30</option>
          <option>19:00</option>
          <option>19:30</option>
          <option>20:00</option>
          <option>20:30</option>
        </select>
      </div>
      <button class="checkout" id="checkout" disabled>Bestelling doorgeven</button>
      <p class="cart-foot">Betalen doe je bij afhaling.</p>
    </aside>
  </div>
</div>

<dialog id="confirm">
  <h3>Zo werkt het straks</h3>
  <p>In de echte versie vertrekt je bestelling hier rechtstreeks naar de keuken, met een
     bevestiging per mail of sms.</p>
  <p>Dit is een prototype, dus er wordt nog niets verstuurd.</p>
  <a class="call" href="tel:{phone_href}">Bel {phone} om nu te bestellen</a>
  <button id="close-confirm" type="button">Sluiten</button>
</dialog>

<footer>
  Prototype gebouwd voor {name} &middot; <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a>
</footer>

<script>
  const cart = new Map();
  const linesEl = document.getElementById('cart-lines');
  const emptyEl = document.getElementById('cart-empty');
  const totalEl = document.getElementById('cart-total');
  const checkoutEl = document.getElementById('checkout');

  const money = (n) => '\\u20ac\\u00a0' + n.toFixed(2).replace('.', ',');

  function change(id, name, price, delta) {{
    const line = cart.get(id) || {{ name, price, qty: 0 }};
    line.qty += delta;
    if (line.qty <= 0) cart.delete(id); else cart.set(id, line);
    draw();
  }}

  function draw() {{
    linesEl.innerHTML = '';
    let total = 0;
    for (const [id, line] of cart) {{
      total += line.price * line.qty;
      const li = document.createElement('li');
      li.className = 'cart-line';
      const qty = document.createElement('div');
      qty.className = 'qty';
      const minus = document.createElement('button');
      minus.type = 'button';
      minus.textContent = '\\u2212';
      minus.setAttribute('aria-label', 'Eén minder ' + line.name);
      minus.onclick = () => change(id, line.name, line.price, -1);
      const count = document.createElement('span');
      count.textContent = line.qty;
      const plus = document.createElement('button');
      plus.type = 'button';
      plus.textContent = '+';
      plus.setAttribute('aria-label', 'Eén meer ' + line.name);
      plus.onclick = () => change(id, line.name, line.price, 1);
      qty.append(minus, count, plus);
      const nameEl = document.createElement('span');
      nameEl.className = 'line-name';
      nameEl.textContent = line.name;
      const priceEl = document.createElement('span');
      priceEl.className = 'line-price';
      priceEl.textContent = money(line.price * line.qty);
      li.append(qty, nameEl, priceEl);
      linesEl.appendChild(li);
    }}
    const has = cart.size > 0;
    emptyEl.style.display = has ? 'none' : 'block';
    totalEl.textContent = money(total);
    checkoutEl.disabled = !has;
  }}

  document.querySelectorAll('.add').forEach((btn) => {{
    btn.addEventListener('click', () => {{
      change(btn.dataset.id, btn.dataset.name, parseFloat(btn.dataset.price), 1);
    }});
  }});

  const dialog = document.getElementById('confirm');
  checkoutEl.addEventListener('click', () => dialog.showModal());
  document.getElementById('close-confirm').addEventListener('click', () => dialog.close());
</script>

</body>
</html>
"""
