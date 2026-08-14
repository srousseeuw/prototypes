"""
Sectorsjabloon: vrijetijd (gemeentelijk vrijetijds- en opvangaanbod).

Gemaakt voor het aanbod van een gemeente: speelpleinen, sportweken, uitstappen
en naschoolse activiteiten, met als uitgangspunt dat een ouder alles kan zien
zonder eerst in te loggen.

Drie pagina's:
  index.html            → aanbod met altijd zichtbare filters (het pronkstuk)
  praktisch/index.html  → locaties, hoe inschrijven werkt, veelgestelde vragen
  inschrijven/index.html → inschrijfflow in vier stappen, zonder account vooraf

De activiteiten komen uit het "activities" veld van de brief; het sjabloon
bevat zelf geen aanbod. Prijzen en het aantal vrije plaatsen zijn op zo'n
platform meestal pas na de login zichtbaar. Staat "prices_verified" of
"spots_verified" op false, dan toont elke pagina een duidelijke melding dat het
om voorbeeldcijfers gaat, zodat een demo nooit voor echte tarieven kan doorgaan.
"""
import json

from .common import esc

FONTS_HREF = (
    "https://fonts.googleapis.com/css2?"
    "family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800"
    "&family=Public+Sans:wght@400;500;600;700&display=swap"
)

CSS = """
:root{
  --ink:#14212b;
  --ink-2:#42586a;
  --ink-3:#6b7f8e;
  --paper:#eef3f3;
  --card:#ffffff;
  --brand:#0f6d78;
  --brand-deep:#0a4a53;
  --brand-tint:#dceded;
  --accent:#f2b134;
  --ok:#1a7a4c;
  --ok-tint:#e2f3ea;
  --warn:#a1521a;
  --warn-tint:#fbeddd;
  --full:#7d3a63;
  --full-tint:#f6e6ef;
  --line:rgba(20,33,43,0.14);
  --line-soft:rgba(20,33,43,0.08);
  --radius:16px;
  --shadow:0 10px 30px rgba(10,44,53,0.09);
  --font-display:'Bricolage Grotesque','Public Sans',system-ui,sans-serif;
  --font-body:'Public Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none !important}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  font-family:var(--font-body);
  background:var(--paper);
  color:var(--ink);
  line-height:1.55;
  font-size:16px;
  overflow-x:hidden;
  -webkit-font-smoothing:antialiased;
}
img,svg{max-width:100%}
a{color:var(--brand-deep)}
h1,h2,h3,h4{font-family:var(--font-display);line-height:1.15;letter-spacing:-0.015em;overflow-wrap:anywhere}
.wrap{width:100%;max-width:1080px;margin:0 auto;padding:0 18px}
.skip{position:absolute;left:-9999px;top:0;background:var(--brand-deep);color:#fff;padding:12px 18px;z-index:99}
.skip:focus{left:8px;top:8px}
a:focus-visible,button:focus-visible,select:focus-visible,input:focus-visible,summary:focus-visible{
  outline:3px solid var(--brand);outline-offset:2px;border-radius:6px;
}

/* ---------- prototypestrook + kop ---------- */
.proto{
  background:var(--brand-deep);color:#dff0f0;
  font-size:0.82rem;line-height:1.4;padding:9px 0;
}
.proto strong{color:#fff}
.site-head{background:var(--card);border-bottom:1px solid var(--line-soft)}
.site-head .wrap{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);margin-right:auto;min-height:44px}
.logo .mark{width:34px;height:34px;flex:0 0 34px}
.logo .word{font-family:var(--font-display);font-weight:800;font-size:1.12rem;line-height:1.1}
.logo .sub{display:block;font-family:var(--font-body);font-weight:500;font-size:0.72rem;color:var(--ink-3);letter-spacing:0.04em;text-transform:uppercase}
nav.main{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
nav.main a{
  display:inline-flex;align-items:center;min-height:44px;padding:0 14px;
  text-decoration:none;color:var(--ink-2);font-weight:600;font-size:0.94rem;border-radius:10px;
}
nav.main a:hover{background:var(--brand-tint);color:var(--brand-deep)}
nav.main a[aria-current="page"]{color:var(--brand-deep);background:var(--brand-tint)}
nav.main a.cta{background:var(--brand);color:#fff}
nav.main a.cta:hover{background:var(--brand-deep);color:#fff}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;background:var(--brand-deep);color:#fff;padding:26px 0 24px}
.hero .deco{position:absolute;inset:0;pointer-events:none;opacity:.55}
.hero .wrap{position:relative}
.hero .eyebrow{
  display:inline-block;font-weight:600;font-size:0.74rem;letter-spacing:0.1em;text-transform:uppercase;
  color:var(--accent);margin-bottom:8px;
}
.hero h1{font-size:clamp(1.7rem,6.4vw,2.9rem);font-weight:800;max-width:17ch;color:#fff}
.hero p.lead{margin-top:10px;font-size:clamp(0.98rem,2.6vw,1.14rem);color:#cfe4e5;max-width:52ch}
.hero .stats{display:flex;flex-wrap:wrap;gap:7px;margin-top:16px}
.hero .stat{
  background:rgba(255,255,255,0.11);border:1px solid rgba(255,255,255,0.18);
  border-radius:999px;padding:8px 15px;font-size:0.88rem;font-weight:600;
}
.hero .stat b{color:var(--accent);font-weight:800}

/* ---------- meldingen ---------- */
.notice{
  display:flex;gap:12px;align-items:flex-start;
  background:#fff8e8;border:1px solid #e8cf94;border-left:5px solid var(--accent);
  border-radius:12px;padding:14px 16px;font-size:0.92rem;color:#4d3a10;
}
.notice svg{flex:0 0 20px;margin-top:2px;color:#a6791a}
.notice strong{font-weight:700}

/* ---------- filters ---------- */
main{padding-bottom:10px}
section{padding:20px 0}
.panel{background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);box-shadow:var(--shadow)}
.filters{padding:16px}
.filters h2{font-size:1.1rem;margin-bottom:2px}
.filters .hint{color:var(--ink-3);font-size:0.86rem;margin-bottom:12px}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{
  display:inline-flex;align-items:center;gap:7px;min-height:44px;padding:0 13px;
  border:1.5px solid var(--line);background:#fff;color:var(--ink-2);
  border-radius:999px;font:inherit;font-size:0.92rem;font-weight:600;cursor:pointer;
  transition:background .13s ease,border-color .13s ease,color .13s ease;
}
.chip:hover{border-color:var(--brand);color:var(--brand-deep)}
.chip .n{font-size:0.8rem;font-weight:700;color:var(--ink-3);background:var(--paper);border-radius:999px;padding:1px 7px}
.chip[aria-pressed="true"]{background:var(--brand-deep);border-color:var(--brand-deep);color:#fff}
.chip[aria-pressed="true"] .n{background:rgba(255,255,255,0.2);color:#fff}
.fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}
.field.wide{grid-column:1 / -1}
.field label{display:block;font-size:0.8rem;font-weight:700;color:var(--ink-2);margin-bottom:4px}
.field select,.field input[type="text"],.field input[type="email"],.field input[type="tel"]{
  width:100%;min-height:48px;padding:10px 12px;
  border:1.5px solid var(--line);border-radius:10px;background:#fff;color:var(--ink);
  font-family:inherit;font-size:1rem;
}
.field select{appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2342586a' stroke-width='2.5' stroke-linecap='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 12px center;background-size:18px;padding-right:40px;
}
.filter-foot{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:10px}
.toggle{display:inline-flex;align-items:center;gap:9px;min-height:44px;cursor:pointer;font-weight:600;font-size:0.92rem;color:var(--ink-2);margin-right:auto}
.toggle input{width:24px;height:24px;accent-color:var(--brand);cursor:pointer}
.linkbtn{
  min-height:44px;padding:0 14px;border:1.5px solid var(--line);background:#fff;border-radius:10px;
  font:inherit;font-weight:600;font-size:0.92rem;color:var(--ink-2);cursor:pointer;
}
.linkbtn:hover{border-color:var(--brand);color:var(--brand-deep)}
.resultbar{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px;margin:16px 0 10px}
.resultbar .count{font-family:var(--font-display);font-weight:700;font-size:1.05rem}
.resultbar .of{color:var(--ink-3);font-size:0.9rem}

/* ---------- activiteitenkaarten ---------- */
.cards{display:grid;grid-template-columns:1fr;gap:10px;list-style:none}
.act{
  position:relative;background:var(--card);border:1px solid var(--line-soft);border-radius:14px;
  padding:12px 14px 12px 17px;overflow:hidden;
}
.act::before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--c,var(--brand))}
.act-top{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:6px}
.tag{
  display:inline-flex;align-items:center;gap:6px;font-size:0.74rem;font-weight:700;letter-spacing:0.06em;
  text-transform:uppercase;color:var(--c,var(--brand));background:color-mix(in srgb,var(--c,#0f6d78) 12%,#fff);
  border-radius:999px;padding:4px 10px;
}
.status{display:inline-flex;align-items:center;gap:6px;font-size:0.8rem;font-weight:700;border-radius:999px;padding:4px 11px;margin-left:auto}
.status::before{content:"";width:8px;height:8px;border-radius:50%;background:currentColor}
.st-vrij{color:var(--ok);background:var(--ok-tint)}
.st-bijna{color:var(--warn);background:var(--warn-tint)}
.st-vol{color:var(--full);background:var(--full-tint)}
.act h3{font-size:1.04rem;font-weight:700;margin-bottom:5px}
.meta{display:flex;flex-wrap:wrap;gap:2px 12px;list-style:none;color:var(--ink-2);font-size:0.86rem;line-height:1.4}
.meta li{display:inline-flex;align-items:center;gap:5px}
.meta svg{flex:0 0 15px;color:var(--ink-3)}
.act .desc{display:none;color:var(--ink-2);font-size:0.89rem;margin-top:7px}
.act-foot{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:9px;padding-top:8px;border-top:1px solid var(--line-soft)}
.price{font-family:var(--font-display);font-weight:700;font-size:1rem;line-height:1.25}
.price small{font-family:var(--font-body);font-weight:500;font-size:0.8rem;color:var(--ink-3);margin-left:5px}
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  min-height:44px;padding:0 16px;margin-left:auto;
  background:var(--brand);color:#fff;text-decoration:none;
  border:none;border-radius:10px;font-family:inherit;font-weight:700;font-size:0.95rem;cursor:pointer;
  transition:background .13s ease;
}
.btn:hover{background:var(--brand-deep);color:#fff}
.btn:disabled{background:#b9c6cd;cursor:not-allowed}
.btn.ghost{background:#fff;color:var(--brand-deep);border:1.5px solid var(--line);margin-left:0}
.btn.ghost:hover{background:var(--brand-tint);color:var(--brand-deep)}
.btn.wait{background:var(--full)}
.btn.wait:hover{background:#5f2c4b}
.flag{
  display:inline-flex;align-items:center;gap:5px;font-size:0.74rem;font-weight:600;color:var(--ink-3);
  border:1px dashed var(--line);border-radius:999px;padding:2px 8px;
}
.empty{background:var(--card);border:1px dashed var(--line);border-radius:14px;padding:28px 18px;text-align:center;color:var(--ink-2)}
.empty h3{font-size:1.1rem;margin-bottom:6px}

/* ---------- algemene blokken ---------- */
.band{background:var(--card);border-top:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft)}
h2.title{font-size:clamp(1.32rem,4vw,1.9rem);font-weight:800;margin-bottom:5px}
p.sub{color:var(--ink-2);max-width:60ch;margin-bottom:14px}
.grid2{display:grid;grid-template-columns:1fr;gap:10px}
.grid3{display:grid;grid-template-columns:1fr;gap:10px}
.tile{background:var(--card);border:1px solid var(--line-soft);border-radius:14px;padding:14px 16px}
.tile.plain{background:transparent;border:none;padding:0}
.tile h3{font-size:1rem;margin-bottom:4px}
.tile p{color:var(--ink-2);font-size:0.92rem}
.tile.step-tile{padding-left:56px;position:relative}
.stepnum{
  display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;
  background:var(--brand-tint);color:var(--brand-deep);border-radius:50%;
  font-family:var(--font-display);font-weight:700;font-size:0.95rem;margin-bottom:9px;
}
.tile.step-tile .stepnum{position:absolute;left:15px;top:14px;margin:0}
ul.linklist{list-style:none;margin-top:6px;font-size:0.9rem}
ul.linklist a{display:flex;align-items:center;min-height:44px;color:var(--brand-deep)}
ul.checks{list-style:none;display:grid;gap:9px}
ul.checks li{display:flex;gap:10px;align-items:flex-start;color:var(--ink-2);font-size:0.95rem}
ul.checks svg{flex:0 0 20px;color:var(--ok);margin-top:3px}
details.faq{background:var(--card);border:1px solid var(--line-soft);border-radius:12px;margin-bottom:9px}
details.faq summary{
  display:flex;align-items:center;gap:10px;min-height:52px;padding:10px 16px;cursor:pointer;
  font-weight:700;font-size:0.98rem;list-style:none;
}
details.faq summary::-webkit-details-marker{display:none}
details.faq summary::after{content:"+";margin-left:auto;font-size:1.35rem;color:var(--brand);line-height:1}
details.faq[open] summary::after{content:"\\2212"}
details.faq p{padding:0 16px 15px;color:var(--ink-2);font-size:0.93rem}
.callout{background:var(--brand-tint);border-radius:var(--radius);padding:18px 16px}
.callout h2{font-size:1.22rem;margin-bottom:6px}
.callout p{color:var(--brand-deep);max-width:56ch;margin-bottom:14px;font-size:0.94rem}

/* ---------- inschrijfflow ---------- */
.steps{display:flex;flex-wrap:wrap;gap:6px;list-style:none;margin-bottom:20px}
.steps li{
  display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:600;color:var(--ink-3);
  background:var(--card);border:1px solid var(--line-soft);border-radius:999px;padding:7px 13px;
}
.steps li b{
  display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;
  background:var(--paper);color:var(--ink-3);font-size:0.78rem;
}
.steps li[aria-current="step"]{background:var(--brand-deep);border-color:var(--brand-deep);color:#fff}
.steps li[aria-current="step"] b{background:rgba(255,255,255,0.22);color:#fff}
.steps li.done{color:var(--ok);border-color:var(--ok-tint);background:var(--ok-tint)}
.steps li.done b{background:var(--ok);color:#fff}
.step{padding:20px 18px}
.step h2{font-size:1.3rem;margin-bottom:6px}
.step > p.sub{margin-bottom:16px}
.pick{
  display:flex;align-items:flex-start;gap:12px;width:100%;text-align:left;
  background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:12px 14px;
  font:inherit;cursor:pointer;min-height:56px;margin-bottom:9px;
}
.pick:hover{border-color:var(--brand)}
.pick input{width:22px;height:22px;margin-top:2px;flex:0 0 22px;accent-color:var(--brand);cursor:pointer}
.pick .body{flex:1;min-width:0}
.pick .body b{display:block;font-size:0.98rem}
.pick .body span{display:block;color:var(--ink-2);font-size:0.86rem}
.pick .body .row{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;margin-top:5px}
.pick.on{border-color:var(--brand);background:#f4fbfb}
.pick.off{opacity:.62}
.formgrid{display:grid;grid-template-columns:1fr;gap:12px}
.err{color:#a3242b;font-size:0.86rem;font-weight:600;margin-top:5px}
.field.bad select,.field.bad input{border-color:#a3242b;background:#fff6f6}
.stepnav{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;padding-top:16px;border-top:1px solid var(--line-soft)}
.stepnav .btn{margin-left:0}
.stepnav .spacer{flex:1}
.summary{list-style:none;display:grid;gap:8px;margin-bottom:14px}
.summary li{display:flex;flex-wrap:wrap;gap:4px 10px;justify-content:space-between;padding:11px 13px;background:var(--paper);border-radius:10px;font-size:0.93rem}
.summary li b{font-weight:700}
.summary li .who{color:var(--ink-3);font-size:0.84rem;width:100%}
.total{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:13px;border-top:2px solid var(--line);font-family:var(--font-display);font-weight:800;font-size:1.15rem}
.done-mark{
  display:flex;align-items:center;justify-content:center;width:60px;height:60px;border-radius:50%;
  background:var(--ok-tint);color:var(--ok);margin-bottom:14px;
}

/* ---------- voet ---------- */
footer.site{background:var(--brand-deep);color:#cfe4e5;padding:26px 0 24px;margin-top:22px;font-size:0.94rem}
footer.site h4{color:#fff;font-size:0.96rem;margin-bottom:6px}
footer.site .cols{display:grid;grid-template-columns:1fr;gap:18px}
footer.site a{color:#fff}
footer.site ul{list-style:none;display:grid;font-size:0.92rem}
footer.site li{display:flex;align-items:center;min-height:44px}
footer.site ul a{display:flex;align-items:center;min-height:44px}
footer.site .fine a{display:inline-flex;align-items:center;min-height:44px}
footer.site .fine{
  margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.16);
  font-size:0.83rem;display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between;
}

@media (min-width:620px){
  .wrap{padding:0 24px}
  section{padding:26px 0}
  .fields{grid-template-columns:repeat(3,minmax(0,1fr))}
  .field.wide{grid-column:auto}
  .cards{grid-template-columns:repeat(2,minmax(0,1fr))}
  .act{padding:15px 16px 15px 19px;display:flex;flex-direction:column}
  .act .desc{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .act-foot{margin-top:auto;padding-top:12px}
  .grid2{grid-template-columns:repeat(2,minmax(0,1fr))}
  .formgrid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .step{padding:26px 24px}
  .filters{padding:22px 24px}
}
@media (min-width:980px){
  section{padding:34px 0}
  .hero{padding:56px 0 50px}
  .cards{grid-template-columns:repeat(3,minmax(0,1fr))}
  .grid3{grid-template-columns:repeat(3,minmax(0,1fr))}
  footer.site .cols{grid-template-columns:1.4fr 1fr 1fr}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none !important;animation:none !important}
  html{scroll-behavior:auto}
}
"""

ICONS = """<svg class="sprite" aria-hidden="true" focusable="false" style="position:absolute;width:0;height:0;overflow:hidden">
  <symbol id="i-cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></symbol>
  <symbol id="i-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/></symbol>
  <symbol id="i-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.6v.6"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 12.6l5 5L20 6.6"/></symbol>
</svg>"""

STATUS_CLASS = {"vrij": "st-vrij", "bijna": "st-bijna", "vol": "st-vol"}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _money(value):
    return "€ " + f"{float(value):.2f}".replace(".", ",")


def _href(slug, page=""):
    return f"/{slug}/" + (page + "/" if page else "")


def _status(act):
    """Geeft (sleutel, korte tekst) voor de beschikbaarheid van een activiteit."""
    spots = int(act.get("spots_left", 0) or 0)
    if spots <= 0:
        return "vol", "Volzet · wachtlijst"
    if spots <= 5:
        return "bijna", f"Nog {spots} plaats{'en' if spots > 1 else ''}"
    return "vrij", f"{spots} plaatsen vrij"


def _loc_map(brief):
    return {l["key"]: l["name"] for l in brief.get("locations", [])}


def _kind_map(brief):
    return {k["key"]: k["label"] for k in brief.get("kinds", [])}



def _current_year(brief):
    """Referentiejaar voor het omrekenen van geboortejaar naar leeftijd."""
    return int(brief.get("current_year", 2026))


def _age_options(brief):
    """Bouwt de leeftijdskeuze op uit de geboortejaren die in het aanbod voorkomen."""
    current_year = _current_year(brief)
    years = sorted({y for a in brief.get("activities", []) for y in a.get("years", [])}, reverse=True)
    return [(y, f"{current_year - y} jaar · geboren {y}") for y in years]


def _card(act, brief, locs):
    key, label = _status(act)
    cls = STATUS_CLASS[key]
    accent = act.get("accent", "#0f6d78")
    kind_label = _kind_map(brief).get(act.get("kind"), act.get("kind", ""))
    price = act.get("price")
    price_html = (
        f'<span class="price">{_money(price)}<small>{esc(act.get("price_unit", ""))}'
        f'{" · voorbeeld" if not brief.get("prices_verified", True) else ""}</small></span>'
        if price is not None else ""
    )
    flag = ""
    if not act.get("years_verified", True):
        flag = '<span class="flag" title="Leeftijdsgroep nog te bevestigen door de gemeente">leeftijd nog te bevestigen</span>'
    if key == "vol":
        btn = (f'<a class="btn wait" href="{_href(esc(brief["slug"]), "inschrijven")}?a={esc(act["id"])}">'
               f'Op de wachtlijst</a>')
    else:
        btn = (f'<a class="btn" href="{_href(esc(brief["slug"]), "inschrijven")}?a={esc(act["id"])}">'
               f'Inschrijven</a>')
    return f"""      <li class="act" id="{esc(act['id'])}" style="--c:{esc(accent)}"
          data-kind="{esc(act.get('kind',''))}" data-period="{esc(act.get('period',''))}"
          data-loc="{esc(act.get('location',''))}" data-years="{','.join(str(y) for y in act.get('years', []))}"
          data-spots="{int(act.get('spots_left', 0) or 0)}">
        <div class="act-top">
          <span class="tag">{esc(kind_label)}</span>
          <span class="status {cls}">{esc(label)}</span>
        </div>
        <h3>{esc(act['name'])}</h3>
        <ul class="meta">
          <li><svg width="15" height="15"><use href="#i-cal"/></svg>{esc(act.get('date_short') or act.get('date_label',''))}</li>
          <li><svg width="15" height="15"><use href="#i-pin"/></svg>{esc(locs.get(act.get('location',''), ''))}</li>
          <li><svg width="15" height="15"><use href="#i-user"/></svg>{esc(act.get('years_label',''))}</li>
        </ul>
        <p class="desc">{esc(act.get('desc',''))}</p>
        <div class="act-foot">
          {price_html}
          {flag}
          {btn}
        </div>
      </li>"""


def _data_notice(brief):
    if brief.get("prices_verified", True) and brief.get("spots_verified", True):
        return ""
    return f"""<div class="notice">
  <svg width="20" height="20" aria-hidden="true"><use href="#i-info"/></svg>
  <div><strong>Voorbeeldbedragen en voorbeeldcijfers.</strong> {esc(brief.get('data_notice',''))}</div>
</div>"""


# --------------------------------------------------------------------------- #
# schil
# --------------------------------------------------------------------------- #

def _shell(brief, *, title, description, active, body, page_js=""):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    org = esc(brief.get("org", ""))
    site = esc(brief.get("current_site", ""))
    pages = [("", "Aanbod"), ("praktisch", "Praktisch"), ("inschrijven", "Inschrijven")]
    current = ' aria-current="page"'
    links = []
    for key, label in pages:
        cls = ' class="cta"' if key == "inschrijven" else ""
        mark = current if key == active else ""
        links.append(f'<a{cls} href="{_href(slug, key)}"{mark}>{esc(label)}</a>')
    nav = "\n      ".join(links)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0a4a53">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS_HREF}" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Naar de inhoud</a>
{ICONS}

<div class="proto">
  <div class="wrap"><strong>Prototype</strong> &mdash; geen offici&euml;le site van {org}. Er wordt niets verstuurd of betaald.</div>
</div>

<header class="site-head">
  <div class="wrap">
    <a class="logo" href="{_href(slug)}">
      <svg class="mark" viewBox="0 0 40 40" aria-hidden="true">
        <rect width="40" height="40" rx="11" fill="#0f6d78"/>
        <circle cx="14.5" cy="15" r="5.5" fill="#f2b134"/>
        <path d="M8 31c0-5.2 4.3-8.4 9.6-8.4S27 25.8 27 31" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/>
        <path d="M25 9.5c5.2 0 8.5 3.4 8.5 8.2 0 3.4-2 6-5 7.6" stroke="#8fd3d0" stroke-width="3" fill="none" stroke-linecap="round"/>
      </svg>
      <span>
        <span class="word">{name}</span>
        <span class="sub">{org}</span>
      </span>
    </a>
    <nav class="main" aria-label="Hoofdnavigatie">
      {nav}
    </nav>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <h4>{name}</h4>
        <p>{esc(brief.get('intro_short',''))}</p>
        <p style="margin-top:12px;font-size:0.88rem;opacity:.85">{esc(brief.get('contact_note',''))}</p>
      </div>
      <div>
        <h4>Snel naar</h4>
        <ul>
          <li><a href="{_href(slug)}#aanbod">Volledig aanbod</a></li>
          <li><a href="{_href(slug, 'praktisch')}">Praktisch &amp; veelgestelde vragen</a></li>
          <li><a href="{_href(slug, 'inschrijven')}">Inschrijven</a></li>
        </ul>
      </div>
      <div>
        <h4>Huidig platform</h4>
        <ul>
          <li><a href="{site}" target="_blank" rel="noopener">{site.replace('https://','')}</a></li>
          <li>Inschrijvingen lopen vandaag daar.</li>
        </ul>
      </div>
    </div>
    <div class="fine">
      <span>Prototype gebouwd voor {org}</span>
      <span><a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a></span>
    </div>
  </div>
</footer>
{page_js}
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# pagina: aanbod (home)
# --------------------------------------------------------------------------- #

def render(brief: dict) -> str:
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    org = esc(brief.get("org", ""))
    acts = sorted(brief.get("activities", []), key=lambda a: (a.get("sort", ""), a.get("name", "")))
    locs = _loc_map(brief)

    tally = {}
    for a in acts:
        tally[a.get("kind")] = tally.get(a.get("kind"), 0) + 1
    chips = [f'<button class="chip" type="button" data-kind="alles" aria-pressed="true">'
             f'Alles <span class="n">{len(acts)}</span></button>']
    for k in brief.get("kinds", []):
        n = tally.get(k["key"], 0)
        if n:
            chips.append(f'<button class="chip" type="button" data-kind="{esc(k["key"])}" aria-pressed="false">'
                         f'{esc(k["label"])} <span class="n">{n}</span></button>')

    age_opts = "\n            ".join(
        f'<option value="{y}">{esc(label)}</option>' for y, label in _age_options(brief)
    )
    period_opts = "\n            ".join(
        f'<option value="{esc(p["key"])}">{esc(p["label"])}</option>' for p in brief.get("periods", [])
    )
    loc_opts = "\n            ".join(
        f'<option value="{esc(l["key"])}">{esc(l["name"])}</option>' for l in brief.get("locations", [])
    )

    cards = "\n".join(_card(a, brief, locs) for a in acts)
    free_total = sum(int(a.get("spots_left", 0) or 0) for a in acts)

    improvements = "\n        ".join(
        f'<li><svg width="20" height="20" aria-hidden="true"><use href="#i-check"/></svg><span>{esc(t)}</span></li>'
        for t in brief.get("improvements", [])
    )

    body = f"""
<section class="hero">
  <svg class="deco" viewBox="0 0 1200 400" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <circle cx="1050" cy="70" r="180" fill="#0f6d78"/>
    <circle cx="1160" cy="330" r="120" fill="#12838d"/>
    <path d="M760 400c0-140 90-230 230-230" stroke="#f2b134" stroke-width="16" fill="none" stroke-linecap="round" opacity=".8"/>
    <circle cx="905" cy="255" r="26" fill="#f2b134"/>
  </svg>
  <div class="wrap">
    <span class="eyebrow">{esc(brief.get('season_label',''))} &middot; {org}</span>
    <h1>{esc(brief.get('headline') or brief.get('tagline',''))}</h1>
    <p class="lead">{esc(brief.get('intro_short',''))}</p>
    <div class="stats">
      <span class="stat"><b>{len(acts)}</b> activiteiten</span>
      <span class="stat"><b>{len(brief.get('locations', []))}</b> locaties</span>
      <span class="stat"><b>{free_total}</b> plaatsen vrij</span>
    </div>
  </div>
</section>

<section id="aanbod">
  <div class="wrap">
    {_data_notice(brief)}
    <div class="panel filters" style="margin-top:18px">
      <h2>Vind een activiteit</h2>
      <p class="hint">De lijst past zich meteen aan. Geen login nodig.</p>
      <div class="chips" role="group" aria-label="Soort activiteit">
        {chr(10).join('        ' + c for c in chips).strip()}
      </div>
      <div class="fields">
        <div class="field wide">
          <label for="f-jaar">Leeftijd van je kind</label>
          <select id="f-jaar">
            <option value="alles">Alle leeftijden</option>
            {age_opts}
          </select>
        </div>
        <div class="field">
          <label for="f-periode">Wanneer</label>
          <select id="f-periode">
            <option value="alles">Hele jaar</option>
            {period_opts}
          </select>
        </div>
        <div class="field">
          <label for="f-loc">Waar</label>
          <select id="f-loc">
            <option value="alles">Alle locaties</option>
            {loc_opts}
          </select>
        </div>
      </div>
      <div class="filter-foot">
        <label class="toggle" for="f-vrij"><input type="checkbox" id="f-vrij"> Alleen met vrije plaatsen</label>
        <button class="linkbtn" type="button" id="f-reset">Wissen</button>
      </div>
    </div>

    <div class="resultbar">
      <span class="count" id="count" role="status" aria-live="polite">{len(acts)} activiteiten</span>
      <span class="of" id="of">van de {len(acts)} in het aanbod</span>
    </div>

    <ul class="cards" id="cards">
{cards}
    </ul>

    <div class="empty" id="empty" hidden>
      <h3>Niets gevonden met deze filters</h3>
      <p>Probeer een andere leeftijd of periode, of wis de filters.</p>
      <p style="margin-top:12px"><button class="btn ghost" type="button" id="f-reset2">Wis alle filters</button></p>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="callout">
      <h2>Inschrijven in vier stappen</h2>
      <p>Kies je kind, vink de activiteiten aan, kijk alles na op &eacute;&eacute;n scherm en bevestig.
         Een account maak je pas bij die laatste stap &mdash; niet om te kijken wat er te doen is.</p>
      <a class="btn" style="margin-left:0" href="{_href(slug, 'inschrijven')}">Start een inschrijving</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 class="title">Wat er anders is</h2>
    <p class="sub">Zelfde aanbod als {esc(brief.get('current_site','').replace('https://',''))}, omgekeerde volgorde: eerst informatie, dan pas aanmelden.</p>
    <ul class="checks">
    {improvements}
    </ul>
    <p style="margin-top:16px"><a class="btn ghost" href="{_href(slug, 'praktisch')}">Praktische info en veelgestelde vragen</a></p>
  </div>
</section>
"""

    js = """<script>
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll('#cards .act'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var jaar = document.getElementById('f-jaar');
  var periode = document.getElementById('f-periode');
  var loc = document.getElementById('f-loc');
  var vrij = document.getElementById('f-vrij');
  var count = document.getElementById('count');
  var of = document.getElementById('of');
  var empty = document.getElementById('empty');
  var totaal = cards.length;
  var state = { k: 'alles', j: 'alles', p: 'alles', l: 'alles', v: false };

  function fromUrl() {
    var q = new URLSearchParams(location.search);
    if (q.get('soort')) state.k = q.get('soort');
    if (q.get('jaar')) state.j = q.get('jaar');
    if (q.get('periode')) state.p = q.get('periode');
    if (q.get('locatie')) state.l = q.get('locatie');
    if (q.get('vrij') === '1') state.v = true;
    chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c.dataset.kind === state.k)); });
    if (!chips.some(function (c) { return c.dataset.kind === state.k; })) {
      state.k = 'alles';
      chips[0].setAttribute('aria-pressed', 'true');
    }
    jaar.value = has(jaar, state.j) ? state.j : 'alles';
    periode.value = has(periode, state.p) ? state.p : 'alles';
    loc.value = has(loc, state.l) ? state.l : 'alles';
    vrij.checked = state.v;
  }

  function has(sel, val) {
    return Array.prototype.some.call(sel.options, function (o) { return o.value === val; });
  }

  function toUrl() {
    var q = new URLSearchParams();
    if (state.k !== 'alles') q.set('soort', state.k);
    if (state.j !== 'alles') q.set('jaar', state.j);
    if (state.p !== 'alles') q.set('periode', state.p);
    if (state.l !== 'alles') q.set('locatie', state.l);
    if (state.v) q.set('vrij', '1');
    var s = q.toString();
    history.replaceState(null, '', s ? location.pathname + '?' + s : location.pathname);
  }

  function apply() {
    var zichtbaar = 0;
    cards.forEach(function (card) {
      var ok = true;
      if (state.k !== 'alles' && card.dataset.kind !== state.k) ok = false;
      if (ok && state.p !== 'alles' && card.dataset.period !== state.p) ok = false;
      if (ok && state.l !== 'alles' && card.dataset.loc !== state.l) ok = false;
      if (ok && state.j !== 'alles' && card.dataset.years.split(',').indexOf(state.j) === -1) ok = false;
      if (ok && state.v && parseInt(card.dataset.spots, 10) <= 0) ok = false;
      card.hidden = !ok;
      if (ok) zichtbaar++;
    });
    count.textContent = zichtbaar === 1 ? '1 activiteit' : zichtbaar + ' activiteiten';
    of.textContent = zichtbaar === totaal ? 'van de ' + totaal + ' in het aanbod' : 'van de ' + totaal + ' \\u2014 filters actief';
    empty.hidden = zichtbaar > 0;
    toUrl();
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      state.k = chip.dataset.kind;
      chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c === chip)); });
      apply();
    });
  });
  jaar.addEventListener('change', function () { state.j = jaar.value; apply(); });
  periode.addEventListener('change', function () { state.p = periode.value; apply(); });
  loc.addEventListener('change', function () { state.l = loc.value; apply(); });
  vrij.addEventListener('change', function () { state.v = vrij.checked; apply(); });

  function reset() {
    state = { k: 'alles', j: 'alles', p: 'alles', l: 'alles', v: false };
    chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c.dataset.kind === 'alles')); });
    jaar.value = 'alles'; periode.value = 'alles'; loc.value = 'alles'; vrij.checked = false;
    apply();
  }
  document.getElementById('f-reset').addEventListener('click', reset);
  document.getElementById('f-reset2').addEventListener('click', function () {
    reset();
    document.getElementById('aanbod').scrollIntoView();
  });

  fromUrl();
  apply();
})();
</script>"""

    return _shell(
        brief,
        title=f"{name} — {esc(brief.get('category',''))}",
        description=esc(brief.get("intro_short", "")),
        active="",
        body=body,
        page_js=js,
    )


# --------------------------------------------------------------------------- #
# pagina: praktisch
# --------------------------------------------------------------------------- #

def _page_praktisch(brief):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    acts = brief.get("activities", [])
    per_loc = {}
    for a in acts:
        per_loc.setdefault(a.get("location"), []).append(a)

    loc_tiles = []
    for l in brief.get("locations", []):
        items = per_loc.get(l["key"], [])
        lis = "".join(f'<li><a href="{_href(slug)}#{esc(a["id"])}">{esc(a["name"])}</a></li>' for a in items)
        loc_tiles.append(f"""      <div class="tile">
        <h3>{esc(l['name'])}</h3>
        <p>{esc(l.get('note',''))}</p>
        <ul class="linklist">{lis}</ul>
      </div>""")

    faq = "\n      ".join(
        f'<details class="faq"><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>'
        for f in brief.get("faq", [])
    )
    problems = "\n      ".join(
        f'<div class="tile"><h3>{esc(p["title"])}</h3><p>{esc(p["body"])}</p></div>'
        for p in brief.get("problems", [])
    )
    steps = "\n      ".join(
        f'<div class="tile step-tile"><span class="stepnum">{i+1}</span>'
        f'<h3>{esc(s["title"])}</h3><p>{esc(s["body"])}</p></div>'
        for i, s in enumerate(brief.get("steps", []))
    )

    body = f"""
<section class="hero">
  <div class="wrap">
    <span class="eyebrow">Praktisch</span>
    <h1>Alles wat je moet weten voor je inschrijft</h1>
    <p class="lead">Locaties, hoe de inschrijving verloopt en de vragen die het vaakst terugkomen.</p>
  </div>
</section>

<section>
  <div class="wrap">
    {_data_notice(brief)}
    <h2 class="title" style="margin-top:26px">Waar gaat het door?</h2>
    <p class="sub">Zes locaties in en rond Essen. Klik door naar de activiteiten die er plaatsvinden.</p>
    <div class="grid3">
{chr(10).join(loc_tiles)}
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="title">Hoe inschrijven verloopt</h2>
    <p class="sub">Vier stappen, en pas op het einde een account.</p>
    <div class="grid2">
      {steps}
    </div>
    <p style="margin-top:20px"><a class="btn" style="margin-left:0" href="{_href(slug, 'inschrijven')}">Start een inschrijving</a></p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 class="title">Veelgestelde vragen</h2>
    <p class="sub">Kort en zonder omwegen.</p>
      {faq}
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="title">Waarom deze pagina bestaat</h2>
    <p class="sub">{esc(brief.get('about',''))}</p>
    <p class="sub">Wat er op het huidige inschrijfplatform vandaag in de weg zit:</p>
    <div class="grid2">
      {problems}
    </div>
    <p class="sub" style="margin-top:20px">Alles op deze pagina is nagebouwd zonder foto's of teksten van de bestaande site over te nemen. De omschrijvingen zijn eigen samenvattingen.</p>
  </div>
</section>
"""
    return _shell(
        brief,
        title=f"Praktisch — {name}",
        description="Locaties, verloop van de inschrijving en veelgestelde vragen.",
        active="praktisch",
        body=body,
    )


# --------------------------------------------------------------------------- #
# pagina: inschrijven
# --------------------------------------------------------------------------- #

def _page_inschrijven(brief):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    locs = _loc_map(brief)
    kinds = _kind_map(brief)
    acts = sorted(brief.get("activities", []), key=lambda a: (a.get("sort", ""), a.get("name", "")))

    payload = [{
        "id": a["id"],
        "name": a["name"],
        "kind": kinds.get(a.get("kind"), a.get("kind", "")),
        "accent": a.get("accent", "#0f6d78"),
        "date": a.get("date_label", ""),
        "loc": locs.get(a.get("location", ""), ""),
        "years": a.get("years", []),
        "years_label": a.get("years_label", ""),
        "price": a.get("price", 0),
        "unit": a.get("price_unit", ""),
        "spots": int(a.get("spots_left", 0) or 0),
    } for a in acts]
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    year_opts = "\n              ".join(
        f'<option value="{y}">{esc(label)}</option>' for y, label in _age_options(brief)
    )
    prices_note = "" if brief.get("prices_verified", True) else (
        '<p class="sub" style="font-size:0.86rem;margin-top:10px">De bedragen hieronder zijn voorbeelden, '
        'geen offici&euml;le tarieven.</p>'
    )

    body = f"""
<section style="padding-top:22px">
  <div class="wrap">
    {_data_notice(brief)}

    <ol class="steps" id="steps" style="margin-top:18px">
      <li aria-current="step" data-step="1"><b>1</b> Kind</li>
      <li data-step="2"><b>2</b> Activiteiten</li>
      <li data-step="3"><b>3</b> Nakijken</li>
      <li data-step="4"><b>4</b> Klaar</li>
    </ol>

    <div class="panel step" id="step-1">
      <h2>Voor wie schrijf je in?</h2>
      <p class="sub">Voornaam en geboortejaar volstaan. Je hebt hier nog geen account voor nodig &mdash;
         dat komt pas bij het bevestigen.</p>
      <div id="kids"></div>
      <div class="formgrid" style="margin-top:6px">
        <div class="field" id="w-voornaam">
          <label for="voornaam">Voornaam van het kind</label>
          <input type="text" id="voornaam" autocomplete="off" placeholder="Bijvoorbeeld Fien">
        </div>
        <div class="field" id="w-jaar">
          <label for="geboortejaar">Geboortejaar</label>
          <select id="geboortejaar">
            <option value="">Kies een jaar</option>
              {year_opts}
          </select>
        </div>
      </div>
      <p class="err" id="err-1" hidden></p>
      <div class="stepnav">
        <button class="btn ghost" type="button" id="add-kid">Kind toevoegen</button>
        <span class="spacer"></span>
        <button class="btn" type="button" id="to-2">Verder naar de activiteiten</button>
      </div>
    </div>

    <div class="panel step" id="step-2" hidden>
      <h2>Wat kiezen we voor <span id="kid-naam">dit kind</span>?</h2>
      <p class="sub" id="kid-uitleg">Alleen wat bij die leeftijd past.</p>
      {prices_note}
      <div id="aanbod-lijst"></div>
      <p class="err" id="err-2" hidden></p>
      <div class="stepnav">
        <button class="btn ghost" type="button" data-back="1">Terug</button>
        <span class="spacer"></span>
        <button class="btn" type="button" id="to-3">Nakijken</button>
      </div>
    </div>

    <div class="panel step" id="step-3" hidden>
      <h2>Klopt alles?</h2>
      <p class="sub">Nog niets vastgelegd. Kijk je keuzes na en laat weten hoe we je kunnen bereiken.</p>
      <ul class="summary" id="overzicht"></ul>
      <div class="total"><span>Totaal</span><span id="totaal">&euro;&nbsp;0,00</span></div>
      <h3 style="margin-top:20px;font-size:1.05rem">Jouw gegevens</h3>
      <p class="sub" style="font-size:0.88rem">Als ouder of voogd. Hierna pas maak je een account aan of log je in.</p>
      <div class="formgrid">
        <div class="field" id="w-ouder">
          <label for="ouder">Naam ouder of voogd</label>
          <input type="text" id="ouder" autocomplete="name">
        </div>
        <div class="field" id="w-mail">
          <label for="mail">E-mailadres</label>
          <input type="email" id="mail" autocomplete="email" inputmode="email">
        </div>
        <div class="field" id="w-tel">
          <label for="tel">Telefoonnummer</label>
          <input type="tel" id="tel" autocomplete="tel" inputmode="tel">
        </div>
      </div>
      <p class="err" id="err-3" hidden></p>
      <div class="stepnav">
        <button class="btn ghost" type="button" data-back="2">Terug</button>
        <span class="spacer"></span>
        <button class="btn" type="button" id="to-4">Inschrijving bevestigen</button>
      </div>
    </div>

    <div class="panel step" id="step-4" hidden>
      <div class="done-mark"><svg width="30" height="30" aria-hidden="true"><use href="#i-check"/></svg></div>
      <h2>Zo zou het eruitzien</h2>
      <p class="sub">In de echte versie krijg je hier je bevestiging per mail, met een betaallink en de
         mogelijkheid om alles later nog aan te passen.</p>
      <div class="notice" style="margin-bottom:18px">
        <svg width="20" height="20" aria-hidden="true"><use href="#i-info"/></svg>
        <div><strong>Dit is een prototype.</strong> Er is niets verstuurd, niets betaald en niets geregistreerd.
             Je gegevens blijven in dit tabblad en verdwijnen als je het sluit.</div>
      </div>
      <ul class="summary" id="overzicht-2"></ul>
      <div class="total"><span>Totaal</span><span id="totaal-2">&euro;&nbsp;0,00</span></div>
      <div class="stepnav">
        <a class="btn ghost" href="{_href(slug)}">Terug naar het aanbod</a>
        <span class="spacer"></span>
        <button class="btn" type="button" id="opnieuw">Nog een inschrijving</button>
      </div>
    </div>
  </div>
</section>
"""

    js = """<script id="aanbod-data" type="application/json">__DATA__</script>
<script>
(function () {
  var ACTS = JSON.parse(document.getElementById('aanbod-data').textContent);
  var HUIDIG = __JAAR__;
  var kids = [];
  var actief = null;
  var gekozen = {};
  var vooraf = new URLSearchParams(location.search).get('a');

  function euro(n) { return '\\u20ac\\u00a0' + n.toFixed(2).replace('.', ','); }
  function el(id) { return document.getElementById(id); }

  /* ---------- stap 1: kinderen ---------- */
  function tekenKids() {
    var doel = el('kids');
    doel.innerHTML = '';
    kids.forEach(function (kid, i) {
      var lab = document.createElement('label');
      lab.className = 'pick' + (actief === i ? ' on' : '');
      var radio = document.createElement('input');
      radio.type = 'radio';
      radio.name = 'kind';
      radio.checked = actief === i;
      radio.addEventListener('change', function () { actief = i; gekozen = {}; tekenKids(); });
      var body = document.createElement('span');
      body.className = 'body';
      var b = document.createElement('b');
      b.textContent = kid.naam;
      var s = document.createElement('span');
      s.textContent = (HUIDIG - kid.jaar) + ' jaar \\u00b7 geboren ' + kid.jaar;
      body.append(b, s);
      lab.append(radio, body);
      doel.appendChild(lab);
    });
  }

  function voegKidToe() {
    var naam = el('voornaam').value.trim();
    var jaar = el('geboortejaar').value;
    el('w-voornaam').classList.toggle('bad', naam.length < 2);
    el('w-jaar').classList.toggle('bad', !jaar);
    if (naam.length < 2 || !jaar) {
      fout('err-1', 'Vul een voornaam van minstens 2 letters in en kies een geboortejaar.');
      return false;
    }
    if (actief !== null) gekozen = {};
    kids.push({ naam: naam, jaar: parseInt(jaar, 10) });
    actief = kids.length - 1;
    el('voornaam').value = '';
    el('geboortejaar').value = '';
    fout('err-1', '');
    tekenKids();
    return true;
  }

  function fout(id, tekst) {
    var e = el(id);
    e.textContent = tekst;
    e.hidden = !tekst;
  }

  /* ---------- stap 2: activiteiten ---------- */
  function tekenAanbod() {
    var kid = kids[actief];
    el('kid-naam').textContent = kid.naam;
    var passend = ACTS.filter(function (a) { return a.years.indexOf(kid.jaar) !== -1; });
    el('kid-uitleg').textContent = passend.length + ' van de ' + ACTS.length +
      ' activiteiten passen bij ' + kid.naam + ' (' + (HUIDIG - kid.jaar) + ' jaar). De rest is voor andere leeftijden.';
    /* Keuzes die niet bij deze leeftijd horen vallen weg, met uitleg. */
    var weg = Object.keys(gekozen).filter(function (id) {
      return !passend.some(function (a) { return a.id === id; });
    });
    weg.forEach(function (id) { delete gekozen[id]; });
    if (weg.length) {
      var namen = weg.map(function (id) {
        var a = ACTS.filter(function (x) { return x.id === id; })[0];
        return a ? a.name : id;
      });
      fout('err-2', namen.join(', ') + ' past niet bij de leeftijd van ' + kid.naam +
        ' en staat niet meer in je keuze.');
    } else {
      fout('err-2', '');
    }
    var doel = el('aanbod-lijst');
    doel.innerHTML = '';
    if (!passend.length) {
      var p = document.createElement('div');
      p.className = 'empty';
      p.innerHTML = '<h3>Niets voor deze leeftijd</h3><p>Er staat op dit moment geen aanbod open voor ' +
        (HUIDIG - kid.jaar) + '-jarigen.</p>';
      doel.appendChild(p);
      return;
    }
    passend.forEach(function (a) {
      var vol = a.spots <= 0;
      var lab = document.createElement('label');
      lab.className = 'pick' + (gekozen[a.id] ? ' on' : '');
      lab.style.borderLeft = '5px solid ' + a.accent;
      var box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = !!gekozen[a.id];
      box.addEventListener('change', function () {
        if (box.checked) gekozen[a.id] = vol ? 'wachtlijst' : 'plaats';
        else delete gekozen[a.id];
        lab.classList.toggle('on', box.checked);
        fout('err-2', '');
      });
      var body = document.createElement('span');
      body.className = 'body';
      var b = document.createElement('b');
      b.textContent = a.name;
      var s = document.createElement('span');
      s.textContent = a.date + ' \\u00b7 ' + a.loc;
      var row = document.createElement('span');
      row.className = 'row';
      var prijs = document.createElement('b');
      prijs.textContent = euro(a.price) + ' ' + a.unit;
      var st = document.createElement('span');
      st.className = 'status ' + (vol ? 'st-vol' : (a.spots <= 5 ? 'st-bijna' : 'st-vrij'));
      st.style.marginLeft = '0';
      st.textContent = vol ? 'Volzet \\u00b7 op de wachtlijst' : (a.spots <= 5 ? 'Nog ' + a.spots + ' plaatsen' : a.spots + ' plaatsen vrij');
      row.append(prijs, st);
      body.append(b, s, row);
      lab.append(box, body);
      doel.appendChild(lab);
    });
  }

  /* ---------- stap 3: overzicht ---------- */
  function tekenOverzicht(lijstId, totaalId) {
    var doel = el(lijstId);
    doel.innerHTML = '';
    var totaal = 0;
    var kid = kids[actief];
    Object.keys(gekozen).forEach(function (id) {
      var a = ACTS.filter(function (x) { return x.id === id; })[0];
      if (!a) return;
      var wacht = gekozen[id] === 'wachtlijst';
      if (!wacht) totaal += a.price;
      var li = document.createElement('li');
      var links = document.createElement('span');
      links.innerHTML = '<b>' + a.name + '</b>';
      var rechts = document.createElement('span');
      rechts.textContent = wacht ? 'wachtlijst \\u2014 nog niets aangerekend' : euro(a.price);
      var wie = document.createElement('span');
      wie.className = 'who';
      wie.textContent = kid.naam + ' \\u00b7 ' + a.date + ' \\u00b7 ' + a.loc;
      li.append(links, rechts, wie);
      doel.appendChild(li);
    });
    el(totaalId).textContent = euro(totaal);
  }

  /* ---------- stappen ---------- */
  function toon(n) {
    [1, 2, 3, 4].forEach(function (i) { el('step-' + i).hidden = i !== n; });
    Array.prototype.forEach.call(el('steps').children, function (li) {
      var s = parseInt(li.dataset.step, 10);
      li.classList.toggle('done', s < n);
      if (s === n) li.setAttribute('aria-current', 'step');
      else li.removeAttribute('aria-current');
    });
    var top = el('steps').getBoundingClientRect().top + window.pageYOffset - 12;
    window.scrollTo({ top: top, behavior: 'smooth' });
  }

  el('add-kid').addEventListener('click', voegKidToe);

  el('to-2').addEventListener('click', function () {
    /* Half ingevuld formulier telt ook: dan valideren in plaats van negeren. */
    var bezig = el('voornaam').value.trim() || el('geboortejaar').value;
    if (!kids.length || actief === null || bezig) {
      if (!voegKidToe()) return;
    }
    fout('err-1', '');
    tekenAanbod();
    toon(2);
  });

  el('to-3').addEventListener('click', function () {
    if (!Object.keys(gekozen).length) {
      fout('err-2', 'Kies minstens \\u00e9\\u00e9n activiteit om verder te gaan.');
      return;
    }
    tekenOverzicht('overzicht', 'totaal');
    toon(3);
  });

  el('to-4').addEventListener('click', function () {
    var naam = el('ouder').value.trim();
    var mail = el('mail').value.trim();
    var tel = el('tel').value.replace(/[^0-9]/g, '');
    var okNaam = naam.length >= 2;
    var okMail = /^[^\\s@]+@[^\\s@]+\\.[a-z]{2,}$/i.test(mail);
    var okTel = tel.length >= 9;
    el('w-ouder').classList.toggle('bad', !okNaam);
    el('w-mail').classList.toggle('bad', !okMail);
    el('w-tel').classList.toggle('bad', !okTel);
    if (!okNaam || !okMail || !okTel) {
      var mist = [];
      if (!okNaam) mist.push('je naam');
      if (!okMail) mist.push('een geldig e-mailadres');
      if (!okTel) mist.push('een telefoonnummer van minstens 9 cijfers');
      var laatste = mist.pop();
      fout('err-3', 'Vul nog ' + (mist.length ? mist.join(', ') + ' en ' : '') + laatste + ' in.');
      return;
    }
    fout('err-3', '');
    tekenOverzicht('overzicht-2', 'totaal-2');
    toon(4);
  });

  Array.prototype.forEach.call(document.querySelectorAll('[data-back]'), function (b) {
    b.addEventListener('click', function () {
      var n = parseInt(b.dataset.back, 10);
      if (n === 2) tekenAanbod();
      toon(n);
    });
  });

  el('opnieuw').addEventListener('click', function () {
    gekozen = {};
    toon(1);
  });

  if (vooraf) {
    var a = ACTS.filter(function (x) { return x.id === vooraf; })[0];
    if (a) {
      gekozen[a.id] = a.spots <= 0 ? 'wachtlijst' : 'plaats';
      var hint = document.createElement('div');
      hint.className = 'notice';
      hint.style.marginBottom = '16px';
      hint.innerHTML = '<svg width="20" height="20" aria-hidden="true"><use href="#i-info"/></svg><div>' +
        '<strong>' + a.name + '</strong> staat klaar. Vul eerst in voor welk kind, dan zie je of het bij die leeftijd past.' +
        ' Bedoeld voor ' + a.years_label + '.</div>';
      el('step-1').insertBefore(hint, el('step-1').firstChild.nextSibling);
    }
  }
  tekenKids();
})();
</script>"""
    js = js.replace("__DATA__", data).replace("__JAAR__", str(_current_year(brief)))

    return _shell(
        brief,
        title=f"Inschrijven — {name}",
        description="Schrijf je kind in vier stappen in, zonder eerst een account te maken.",
        active="inschrijven",
        body=body,
        page_js=js,
    )


def render_extra_pages(brief: dict) -> dict:
    return {
        "praktisch/index.html": _page_praktisch(brief),
        "inschrijven/index.html": _page_inschrijven(brief),
    }
