"""
Sectorsjabloon: dansschool.

Meerdere pagina's: home, dansaanbod, uurrooster, lesprijzen en — het pronkstuk —
een inschrijfpagina die in vier stappen door één formulier loopt, zonder account
of tweede login.

Verwacht in de brief o.a.: styles, demo, locations, schedule (lijst lessen met
day/loc/addr/time/style/ages/min/max/demo/price), prices, teachers, extra_offer,
faq, news. Ontbrekende velden worden gewoon overgeslagen.
"""
import json

from .common import esc, build_highlights, build_list, maps_query as _maps_query

FONTS_HREF = (
    "https://fonts.googleapis.com/css2?"
    "family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600;1,9..144,700"
    "&family=Manrope:wght@400;500;600;700;800&display=swap"
)

DAY_ORDER = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]

CSS = """
:root{
  --ink:#1B1220;
  --ink-2:#4a3b50;
  --ink-soft:#6f6076;
  --red:#CE181C;
  --red-deep:#a3121a;
  --red-tint:rgba(206,24,28,0.09);
  --blush:#FCEBE7;
  --blush-2:#F7D8D0;
  --paper:#FFFCFB;
  --card:#ffffff;
  --line:rgba(27,18,32,0.13);
  --line-soft:rgba(27,18,32,0.07);
  --ok:#1d7a4c;
  --radius:20px;
  --shadow:0 18px 44px rgba(27,18,32,0.10);
  --font-display:'Fraunces',Georgia,'Times New Roman',serif;
  --font-body:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none !important}
html{scroll-behavior:smooth}
body{
  font-family:var(--font-body);
  background:var(--paper);
  color:var(--ink);
  line-height:1.62;
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}
img{max-width:100%;display:block}
a{color:inherit}
button{font:inherit;color:inherit}
.wrap{width:min(1120px,calc(100% - 36px));margin-inline:auto}
.wrap-narrow{width:min(760px,calc(100% - 36px));margin-inline:auto}
:focus-visible{outline:3px solid var(--red);outline-offset:3px;border-radius:6px}
.skip{position:absolute;left:-9999px;top:0;background:var(--red);color:#fff;padding:10px 16px;z-index:99}
.skip:focus{left:8px;top:8px}

/* ---------- kop ---------- */
.site-head{
  position:sticky;top:0;z-index:60;
  background:rgba(255,252,251,0.93);
  backdrop-filter:saturate(1.4) blur(10px);
  border-bottom:1px solid var(--line-soft);
}
.site-head .wrap{display:flex;align-items:center;gap:12px;min-height:70px}
.logo{display:block;text-decoration:none;margin-right:auto;line-height:1}
.logo .word{
  font-family:var(--font-display);font-style:italic;font-weight:700;
  font-size:1.72rem;color:var(--red);letter-spacing:-0.01em;
}
.logo .sub{
  display:block;font-size:0.58rem;font-weight:700;letter-spacing:0.34em;
  text-transform:uppercase;color:var(--ink-soft);margin-top:4px;
}
nav.main{display:flex;align-items:center;gap:2px}
nav.main a{
  text-decoration:none;font-weight:600;font-size:0.94rem;color:var(--ink-2);
  padding:10px 13px;border-radius:999px;
}
nav.main a:hover{background:var(--blush);color:var(--ink)}
nav.main a[aria-current]{color:var(--red)}
.btn-signup{
  background:var(--red);color:#fff;text-decoration:none;font-weight:700;
  font-size:0.93rem;padding:12px 20px;border-radius:999px;white-space:nowrap;
}
.btn-signup:hover{background:var(--red-deep)}
.nav-toggle{
  display:none;border:1px solid var(--line);background:transparent;
  width:46px;height:46px;border-radius:14px;align-items:center;justify-content:center;cursor:pointer;
}
.nav-toggle span{display:block;width:20px;height:2px;background:var(--ink);position:relative}
.nav-toggle span::before,.nav-toggle span::after{
  content:"";position:absolute;left:0;width:20px;height:2px;background:var(--ink);
}
.nav-toggle span::before{top:-6px}
.nav-toggle span::after{top:6px}
@media(max-width:940px){
  nav.main{
    display:none;position:absolute;left:0;right:0;top:100%;
    flex-direction:column;align-items:stretch;gap:2px;
    background:var(--paper);border-bottom:1px solid var(--line);
    padding:10px 18px 18px;box-shadow:var(--shadow);
  }
  nav.main.open{display:flex}
  nav.main a{padding:15px 12px;font-size:1.05rem;border-radius:12px}
  .nav-toggle{display:inline-flex}
  .site-head .wrap{position:relative}
}
@media(max-width:420px){
  .btn-signup{padding:11px 14px;font-size:0.86rem}
  .logo .word{font-size:1.45rem}
}

/* ---------- hero ---------- */
.hero{position:relative;padding:70px 0 60px;overflow:hidden}
.hero .wrap{position:relative;z-index:2}
.hero-grid{display:grid;grid-template-columns:1.15fr 0.85fr;gap:44px;align-items:center}
.eyebrow{
  display:inline-flex;align-items:center;gap:9px;
  font-size:0.74rem;font-weight:700;text-transform:uppercase;letter-spacing:0.16em;
  color:var(--red);background:var(--red-tint);padding:8px 15px;border-radius:999px;
}
h1{
  font-family:var(--font-display);font-weight:700;
  font-size:clamp(2.5rem,7vw,4.3rem);line-height:1.02;letter-spacing:-0.02em;
  margin:20px 0 18px;
}
h1 em{font-style:italic;color:var(--red)}
.lede{font-size:clamp(1.02rem,2.4vw,1.16rem);color:var(--ink-2);max-width:46ch}
.hero-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:9px;
  text-decoration:none;font-weight:700;font-size:1rem;
  padding:15px 27px;border-radius:999px;border:2px solid transparent;cursor:pointer;
  min-height:52px;
}
.btn-primary{background:var(--red);color:#fff}
.btn-primary:hover{background:var(--red-deep)}
.btn-ghost{background:transparent;color:var(--ink);border-color:var(--line)}
.btn-ghost:hover{background:var(--blush);border-color:var(--blush-2)}
.btn[disabled]{opacity:.45;cursor:not-allowed}

.ribbon{position:absolute;inset:0;z-index:1;pointer-events:none}
.ribbon svg{position:absolute;right:-16%;top:-26%;width:min(680px,76vw);height:auto;opacity:.95}
@media(max-width:940px){.ribbon svg{right:-34%;top:auto;bottom:-8%;opacity:.28;width:150vw}}

.stats{
  display:grid;grid-template-columns:repeat(2,1fr);gap:14px;
  background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);
  padding:24px;box-shadow:var(--shadow);
}
.stat .num{font-family:var(--font-display);font-weight:700;font-size:2.3rem;line-height:1;color:var(--red)}
.stat .lbl{font-size:0.84rem;color:var(--ink-soft);margin-top:5px;font-weight:600}

/* ---------- marquee ---------- */
.marquee{background:var(--ink);color:var(--paper);overflow:hidden;padding:15px 0}
.marquee-track{display:flex;width:max-content;animation:pv-slide 38s linear infinite}
.marquee-track span{
  font-family:var(--font-display);font-style:italic;font-weight:600;
  font-size:1.15rem;padding:0 22px;white-space:nowrap;opacity:.92;
}
.marquee-track span::after{content:"·";margin-left:22px;color:var(--red);font-style:normal}
@keyframes pv-slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.marquee-track{animation:none}}

/* ---------- secties ---------- */
section{padding:66px 0}
.section-head{max-width:58ch;margin-bottom:34px}
.kicker{
  font-size:0.73rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;
  color:var(--red);margin-bottom:12px;
}
h2{
  font-family:var(--font-display);font-weight:700;
  font-size:clamp(1.75rem,4vw,2.5rem);line-height:1.1;letter-spacing:-0.015em;
}
h2 em{font-style:italic;color:var(--red)}
h3{font-family:var(--font-display);font-weight:600;font-size:1.22rem;line-height:1.25}
.section-head p{color:var(--ink-2);margin-top:14px}
.tint{background:var(--blush)}
.dark{background:var(--ink);color:var(--paper)}
.dark h2,.dark h3{color:#fff}
.dark .kicker{color:var(--blush-2)}
.dark p{color:rgba(255,252,251,0.78)}

.two-col{display:grid;grid-template-columns:1fr 1fr;gap:52px;align-items:start}
ul.highlights{list-style:none}
ul.highlights li{
  display:flex;gap:12px;padding:13px 0;border-bottom:1px solid var(--line-soft);
  font-size:0.99rem;
}
ul.highlights li:last-child{border-bottom:0}
.mark{color:var(--red);font-weight:800}

.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.cards.two{grid-template-columns:repeat(2,1fr)}
.card{
  background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);
  padding:26px 24px;
}
.card .tag{
  display:inline-block;font-size:0.74rem;font-weight:700;letter-spacing:0.08em;
  text-transform:uppercase;color:var(--red);background:var(--red-tint);
  padding:5px 11px;border-radius:999px;margin-bottom:13px;
}
.card p{color:var(--ink-2);font-size:0.96rem;margin-top:10px}
.dark .card{background:rgba(255,255,255,0.06);border-color:rgba(255,255,255,0.14)}
.dark .card .tag{color:var(--blush-2);background:rgba(255,255,255,0.10)}
.dark .card p{color:rgba(255,252,251,0.76)}

.pill-list{display:flex;flex-wrap:wrap;gap:9px;list-style:none}
.pill-list li{
  background:var(--card);border:1px solid var(--line);border-radius:999px;
  padding:9px 16px;font-size:0.92rem;font-weight:600;
}
.people{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;list-style:none}
.people li{
  background:var(--card);border:1px solid var(--line-soft);border-radius:14px;padding:15px 17px;
}
.people .nm{font-weight:700}
.people .rl{font-size:0.85rem;color:var(--ink-soft);margin-top:3px}

.loc-list{list-style:none;display:grid;gap:12px}
.loc-list li{
  background:var(--card);border:1px solid var(--line-soft);border-radius:14px;
  padding:16px 18px;display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;
}
.loc-list .nm{font-weight:700}
.loc-list .ad{font-size:0.9rem;color:var(--ink-soft)}
.loc-list a{font-weight:700;color:var(--red);text-decoration:none;font-size:0.88rem;white-space:nowrap}

details.faq{
  background:var(--card);border:1px solid var(--line-soft);border-radius:14px;
  padding:4px 18px;margin-bottom:10px;
}
details.faq summary{
  cursor:pointer;font-weight:700;padding:15px 0;list-style:none;
  display:flex;justify-content:space-between;gap:14px;align-items:center;
}
details.faq summary::-webkit-details-marker{display:none}
details.faq summary::after{content:"+";color:var(--red);font-size:1.4rem;line-height:1}
details.faq[open] summary::after{content:"–"}
details.faq p{padding:0 0 16px;color:var(--ink-2)}

.cta-band{background:var(--red);color:#fff;border-radius:var(--radius);padding:44px 40px;text-align:center}
.cta-band h2{color:#fff}
.cta-band p{color:rgba(255,255,255,0.86);margin:14px auto 26px;max-width:52ch}
.cta-band .btn-primary{background:#fff;color:var(--red)}
.cta-band .btn-primary:hover{background:var(--blush)}

.note{
  background:var(--blush);border-left:4px solid var(--red);border-radius:0 12px 12px 0;
  padding:15px 18px;font-size:0.93rem;color:var(--ink-2);
}

/* ---------- uurrooster ---------- */
.filters{
  background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);
  padding:20px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;box-shadow:var(--shadow);
}
.filters .f{display:flex;flex-direction:column;gap:6px}
.filters label{font-size:0.79rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--ink-soft)}
.filters select,.filters input{
  font:inherit;font-size:1rem;padding:12px 13px;min-height:50px;
  border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--ink);
  width:100%;
}
.filter-meta{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin:22px 0 14px}
.filter-meta .count{font-weight:700}
.linkish{background:none;border:0;color:var(--red);font-weight:700;cursor:pointer;text-decoration:underline;padding:8px 2px}

.daygroup{margin-bottom:34px}
.daygroup h3{
  font-size:1.5rem;padding-bottom:10px;border-bottom:2px solid var(--ink);margin-bottom:6px;
}
.lesrow{
  display:grid;grid-template-columns:112px 1fr auto;gap:16px;align-items:center;
  padding:15px 4px;border-bottom:1px solid var(--line-soft);
}
.lesrow .tm{font-weight:700;font-variant-numeric:tabular-nums;font-size:0.95rem}
.lesrow .st{font-weight:700}
.lesrow .meta{font-size:0.87rem;color:var(--ink-soft);margin-top:2px}
.badge{
  display:inline-block;font-size:0.7rem;font-weight:800;letter-spacing:0.07em;text-transform:uppercase;
  padding:4px 9px;border-radius:999px;background:var(--red-tint);color:var(--red);margin-left:8px;
}
.badge.lvl{background:rgba(27,18,32,0.07);color:var(--ink-2)}
.lesrow .loc{font-size:0.87rem;color:var(--ink-soft);text-align:right}
.empty{padding:28px;text-align:center;color:var(--ink-soft);background:var(--card);border-radius:14px;border:1px dashed var(--line)}

/* ---------- prijzen ---------- */
.pricetable{background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);overflow:hidden}
.pricetable .row{
  display:flex;justify-content:space-between;gap:18px;padding:15px 22px;
  border-bottom:1px solid var(--line-soft);font-size:0.98rem;
}
.pricetable .row:last-child{border-bottom:0}
.pricetable .row .amt{font-weight:700;white-space:nowrap}
.pricetable h3{padding:20px 22px 6px}

/* ---------- inschrijfflow ---------- */
.wiz-head{padding:30px 0 6px}
.wiz-head h1{font-size:clamp(2rem,5.5vw,2.9rem);margin:12px 0 10px}
.protobar{
  background:var(--ink);color:var(--paper);font-size:0.87rem;
  padding:11px 0;text-align:center;
}
.protobar strong{color:var(--blush-2)}
.steps{display:flex;gap:8px;margin:26px 0 8px;list-style:none}
.steps li{flex:1;min-width:0}
.steps .bar{height:6px;border-radius:99px;background:var(--line);display:block}
.steps li.done .bar,.steps li.current .bar{background:var(--red)}
.steps .nm{
  display:block;font-size:0.76rem;font-weight:700;margin-top:8px;color:var(--ink-soft);
  text-transform:uppercase;letter-spacing:0.06em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.steps li.current .nm{color:var(--red)}
.stepcount{font-size:0.86rem;font-weight:700;color:var(--ink-soft);letter-spacing:0.04em}

.step{display:none;padding:26px 0 130px}
.step.active{display:block}
.step h2{font-size:clamp(1.55rem,4vw,2.1rem);margin-bottom:8px}
.step .sub{color:var(--ink-2);margin-bottom:26px;max-width:56ch}

fieldset{border:0}
legend{font-weight:700;margin-bottom:12px}
.field{margin-bottom:20px}
.field label,.field .lab{display:block;font-weight:700;font-size:0.95rem;margin-bottom:7px}
.field .hint{font-size:0.86rem;color:var(--ink-soft);margin:-3px 0 8px}
.field input[type=text],.field input[type=email],.field input[type=tel],.field input[type=date],.field textarea,.field select{
  width:100%;font:inherit;font-size:1rem;padding:14px 15px;min-height:54px;
  border:1.5px solid var(--line);border-radius:14px;background:var(--card);color:var(--ink);
}
.field textarea{min-height:110px;resize:vertical}
.field input:focus,.field textarea:focus,.field select:focus{border-color:var(--red);outline:none;box-shadow:0 0 0 3px var(--red-tint)}
.field.has-error input,.field.has-error textarea,.field.has-error select{border-color:var(--red);background:#fff6f6}
.err{display:none;color:var(--red-deep);font-size:0.88rem;font-weight:600;margin-top:7px}
.field.has-error .err{display:block}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:0 18px}

.choice{display:grid;gap:10px}
.choice input{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.choice label{
  display:flex;align-items:center;gap:13px;cursor:pointer;
  border:1.5px solid var(--line);border-radius:16px;padding:16px 18px;background:var(--card);
  font-weight:600;min-height:58px;
}
.choice input:checked+label{border-color:var(--red);background:var(--red-tint)}
.choice input:focus-visible+label{outline:3px solid var(--red);outline-offset:2px}
.choice .dot{
  width:22px;height:22px;border-radius:50%;border:2px solid var(--line);flex:none;position:relative;background:#fff;
}
.choice input:checked+label .dot{border-color:var(--red)}
.choice input:checked+label .dot::after{
  content:"";position:absolute;inset:4px;border-radius:50%;background:var(--red);
}

.chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.chip{
  border:1.5px solid var(--line);background:var(--card);border-radius:999px;
  padding:10px 16px;font-size:0.9rem;font-weight:700;cursor:pointer;min-height:44px;
}
.chip[aria-pressed=true]{background:var(--ink);color:#fff;border-color:var(--ink)}

.les-day{font-family:var(--font-display);font-weight:700;font-size:1.25rem;margin:26px 0 10px}
.les-pick{
  display:flex;gap:14px;align-items:flex-start;width:100%;text-align:left;
  border:1.5px solid var(--line);background:var(--card);border-radius:16px;
  padding:15px 16px;margin-bottom:10px;cursor:pointer;min-height:64px;
}
.les-pick:hover{border-color:var(--blush-2);background:#fffafa}
.les-pick[aria-pressed=true]{border-color:var(--red);background:var(--red-tint)}
.les-pick .box{
  width:26px;height:26px;border-radius:9px;border:2px solid var(--line);flex:none;
  display:flex;align-items:center;justify-content:center;background:#fff;margin-top:2px;
}
.les-pick[aria-pressed=true] .box{background:var(--red);border-color:var(--red)}
.les-pick .box svg{width:15px;height:15px;opacity:0}
.les-pick[aria-pressed=true] .box svg{opacity:1}
.les-pick .txt{display:block;flex:1;min-width:0}
.les-pick .t1{display:block;font-weight:700}
.les-pick .t2{display:block;font-size:0.88rem;color:var(--ink-soft);margin-top:3px}

.warn{
  background:#fff6ed;border:1px solid #f0c9a0;border-radius:14px;padding:13px 16px;
  font-size:0.9rem;color:#7a4a12;margin-bottom:14px;
}
.summary{background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);overflow:hidden;margin-bottom:24px}
.summary .head{
  display:flex;justify-content:space-between;align-items:center;gap:12px;
  padding:15px 20px;background:var(--blush);font-weight:700;
}
.summary .head button{background:none;border:0;color:var(--red);font-weight:700;cursor:pointer;text-decoration:underline;font-size:0.88rem;padding:6px}
.summary .row{display:flex;justify-content:space-between;gap:16px;padding:13px 20px;border-bottom:1px solid var(--line-soft);font-size:0.95rem}
.summary .row:last-child{border-bottom:0}
.summary .row .k{color:var(--ink-soft)}
.summary .row.total{font-weight:800;font-size:1.05rem;background:#fff}
.check{display:flex;gap:13px;align-items:flex-start;margin-bottom:16px;cursor:pointer}
.check input{width:26px;height:26px;flex:none;margin-top:2px;accent-color:var(--red)}
.check span{font-size:0.95rem}

.wiz-bar{
  position:sticky;bottom:0;z-index:30;
  background:rgba(255,252,251,0.95);backdrop-filter:blur(10px);
  border-top:1px solid var(--line);
  padding:12px 0 calc(12px + env(safe-area-inset-bottom));
  margin-top:-120px;
}
.wiz-bar .wrap-narrow{display:flex;align-items:center;gap:12px}
.wiz-bar .info{flex:1;font-size:0.86rem;color:var(--ink-soft);font-weight:600;min-width:0}
.wiz-bar .btn{padding:14px 24px;font-size:0.98rem}
.formerr{display:none;background:#fff6f6;border:1px solid #f2c2c2;color:var(--red-deep);border-radius:12px;padding:12px 15px;font-weight:600;font-size:0.92rem;margin-bottom:18px}
.formerr.show{display:block}
.done-mark{
  width:76px;height:76px;border-radius:50%;background:var(--red);color:#fff;
  display:flex;align-items:center;justify-content:center;margin-bottom:22px;
}

/* ---------- footer ---------- */
footer.site{background:var(--ink);color:var(--paper);padding:56px 0 30px;margin-top:10px}
footer.site .cols{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:40px}
footer.site h4{font-family:var(--font-display);font-weight:600;font-size:1.1rem;margin-bottom:14px}
footer.site p,footer.site li{color:rgba(255,252,251,0.74);font-size:0.94rem}
footer.site ul{list-style:none;display:grid;gap:8px}
footer.site a{color:rgba(255,252,251,0.86);text-decoration:none}
footer.site a:hover{color:#fff;text-decoration:underline}
footer.site .socials{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
footer.site .socials a{
  border:1px solid rgba(255,255,255,0.22);border-radius:999px;padding:8px 15px;font-size:0.87rem;font-weight:600;
}
footer.site .fine{
  margin-top:38px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.16);
  font-size:0.83rem;color:rgba(255,252,251,0.58);display:flex;gap:14px;justify-content:space-between;flex-wrap:wrap;
}

@media(max-width:940px){
  .hero-grid,.two-col,footer.site .cols{grid-template-columns:1fr}
  .cards,.cards.two{grid-template-columns:1fr 1fr}
  .people{grid-template-columns:1fr 1fr}
  .filters{grid-template-columns:1fr 1fr}
}
@media(max-width:640px){
  section{padding:48px 0}
  .hero{padding:44px 0 40px}
  .cards,.cards.two,.people{grid-template-columns:1fr}
  .filters{grid-template-columns:1fr}
  .grid-2{grid-template-columns:1fr}
  .stats{grid-template-columns:1fr 1fr;padding:20px}
  .lesrow{grid-template-columns:82px 1fr;gap:10px}
  .lesrow .loc{grid-column:1 / -1;text-align:left;margin-top:-6px}
  .cta-band{padding:34px 22px}
  .steps .nm{display:none}
  .hero-actions .btn{flex:1 1 100%}
  .wiz-bar .btn{padding:14px 18px;font-size:0.93rem}
  .wiz-bar .info{flex-basis:100%;order:-1;margin-bottom:2px}
  .wiz-bar .wrap-narrow{flex-wrap:wrap}
}
"""

NAV_JS = """
(function(){
  var t=document.querySelector('.nav-toggle'), n=document.getElementById('mainnav');
  if(!t||!n) return;
  t.addEventListener('click',function(){
    var open=n.classList.toggle('open');
    t.setAttribute('aria-expanded', open?'true':'false');
  });
})();
"""

FILTER_JS = """
(function(){
  var rows=[].slice.call(document.querySelectorAll('.lesrow'));
  var groups=[].slice.call(document.querySelectorAll('.daygroup'));
  var fDay=document.getElementById('f-day'), fLoc=document.getElementById('f-loc'),
      fStyle=document.getElementById('f-style'), fAge=document.getElementById('f-age'),
      out=document.getElementById('f-count'), empty=document.getElementById('f-empty'),
      reset=document.getElementById('f-reset');
  if(!rows.length) return;
  function apply(){
    var d=fDay.value, l=fLoc.value, s=fStyle.value, a=parseInt(fAge.value,10);
    var shown=0;
    rows.forEach(function(r){
      var ok=true;
      if(d && r.dataset.day!==d) ok=false;
      if(l && r.dataset.loc!==l) ok=false;
      if(s && r.dataset.style!==s) ok=false;
      if(!isNaN(a) && (a<parseInt(r.dataset.min,10)||a>parseInt(r.dataset.max,10))) ok=false;
      r.hidden=!ok;
      if(ok) shown++;
    });
    groups.forEach(function(g){
      g.hidden = !g.querySelector('.lesrow:not([hidden])');
    });
    out.textContent = shown===1 ? '1 les gevonden' : shown+' lessen gevonden';
    empty.hidden = shown>0;
  }
  [fDay,fLoc,fStyle,fAge].forEach(function(el){
    el.addEventListener('change',apply); el.addEventListener('input',apply);
  });
  reset.addEventListener('click',function(){
    fDay.value=''; fLoc.value=''; fStyle.value=''; fAge.value=''; apply();
  });
  apply();
})();
"""

WIZARD_JS = """
(function(){
  var COURSES = __COURSES__;
  var TARIFFS = __TARIFFS__;
  var STEPS = 5;
  var state = {step:1, forSelf:null, selected:[], age:null, showAll:false, loc:''};

  var stepEls=[].slice.call(document.querySelectorAll('.step'));
  var barItems=[].slice.call(document.querySelectorAll('.steps li'));
  var counter=document.getElementById('stepcount');
  var btnPrev=document.getElementById('wz-prev'), btnNext=document.getElementById('wz-next');
  var barInfo=document.getElementById('wz-info');

  function $(id){return document.getElementById(id);}
  function val(id){var e=$(id); return e?e.value.trim():'';}
  function fieldOf(el){return el.closest('.field');}
  function clearErr(el){var f=fieldOf(el); if(f){f.classList.remove('has-error'); el.removeAttribute('aria-invalid');}}
  function setErr(el,msg){
    var f=fieldOf(el); if(!f) return;
    f.classList.add('has-error'); el.setAttribute('aria-invalid','true');
    var e=f.querySelector('.err'); if(e) e.textContent=msg;
  }
  ['d-voornaam','d-achternaam','d-geboorte','c-email','c-gsm','c-straat','c-postcode','c-gemeente','c-ouder']
    .forEach(function(id){var e=$(id); if(e) e.addEventListener('input',function(){clearErr(e);});});

  function ageFrom(dateStr){
    if(!dateStr) return null;
    var d=new Date(dateStr+'T00:00:00');
    if(isNaN(d.getTime())) return null;
    var t=new Date(), a=t.getFullYear()-d.getFullYear();
    var m=t.getMonth()-d.getMonth();
    if(m<0 || (m===0 && t.getDate()<d.getDate())) a--;
    return a;
  }
  function money(n){return '\\u20AC\\u00A0'+n.toFixed(2).replace('.',',');}
  function dateNL(s){
    var m=/^(\\d{4})-(\\d{2})-(\\d{2})$/.exec(s||'');
    return m ? m[3]+'/'+m[2]+'/'+m[1] : (s||'');
  }
  function minutes(t){
    var m=t.match(/(\\d{1,2})u(\\d{2})/g);
    if(!m||!m.length) return null;
    var a=m[0].match(/(\\d{1,2})u(\\d{2})/);
    return parseInt(a[1],10)*60+parseInt(a[2],10);
  }
  function endMinutes(t){
    var m=t.match(/(\\d{1,2})u(\\d{2})/g);
    if(!m||m.length<2) return null;
    var a=m[1].match(/(\\d{1,2})u(\\d{2})/);
    return parseInt(a[1],10)*60+parseInt(a[2],10);
  }

  function priceLines(){
    var lines=[], n=0;
    state.selected.forEach(function(i){
      var c=COURSES[i], p;
      if(c.price){ p=c.price; }
      else { p=TARIFFS[Math.min(n,TARIFFS.length-1)]; n++; }
      lines.push({c:c,p:p});
    });
    return lines;
  }
  function total(){return priceLines().reduce(function(s,l){return s+l.p;},0);}

  /* ---- stap 2: lessenlijst ---- */
  function renderCourses(){
    var host=$('les-list'); if(!host) return;
    host.innerHTML='';
    var locs={};
    COURSES.forEach(function(c){locs[c.loc]=1;});
    var list=COURSES.map(function(c,i){return {c:c,i:i};}).filter(function(o){
      if(state.loc && o.c.loc!==state.loc) return false;
      if(state.showAll || state.age===null) return true;
      return state.age>=o.c.min && state.age<=o.c.max;
    });
    if(!list.length){
      host.innerHTML='<div class="empty">Geen lessen gevonden met deze filters. Zet de filters uit om alles te zien.</div>';
      updateBar(); return;
    }
    var byDay={};
    list.forEach(function(o){ (byDay[o.c.day]=byDay[o.c.day]||[]).push(o); });
    __DAYS__.forEach(function(day){
      if(!byDay[day]) return;
      var h=document.createElement('div');
      h.className='les-day'; h.textContent=day;
      host.appendChild(h);
      byDay[day].forEach(function(o){
        var b=document.createElement('button');
        b.type='button'; b.className='les-pick';
        b.setAttribute('aria-pressed', state.selected.indexOf(o.i)>-1?'true':'false');
        b.dataset.idx=o.i;
        var demo=o.c.demo?'<span class="badge">auditie</span>':'';
        b.innerHTML='<span class="box"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10.5l4 4 8-9" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'+
          '<span class="txt"><span class="t1">'+o.c.style+' &middot; '+o.c.ages+demo+'</span>'+
          '<span class="t2">'+o.c.time+' &middot; '+o.c.loc+', '+o.c.addr+'</span></span>';
        b.addEventListener('click',function(){toggle(o.i,b);});
        host.appendChild(b);
      });
    });
    updateBar();
  }
  function toggle(i,btn){
    var k=state.selected.indexOf(i);
    if(k>-1) state.selected.splice(k,1); else state.selected.push(i);
    btn.setAttribute('aria-pressed', k>-1?'false':'true');
    updateBar(); checkClash();
    var fe=$('err-lessen'); if(fe) fe.classList.remove('show');
  }
  function checkClash(){
    var box=$('clash'); if(!box) return;
    var msgs=[];
    for(var a=0;a<state.selected.length;a++){
      for(var b=a+1;b<state.selected.length;b++){
        var x=COURSES[state.selected[a]], y=COURSES[state.selected[b]];
        if(x.day!==y.day) continue;
        var xs=minutes(x.time), xe=endMinutes(x.time), ys=minutes(y.time), ye=endMinutes(y.time);
        if(xs===null||ys===null) continue;
        if(xs<ye && ys<xe) msgs.push(x.style+' ('+x.time+') en '+y.style+' ('+y.time+') overlappen op '+x.day.toLowerCase()+'.');
      }
    }
    if(msgs.length){
      box.innerHTML='<strong>Let op:</strong> '+msgs.join(' ')+' Je mag doorgaan &mdash; de school neemt contact op om dit samen te bekijken.';
      box.hidden=false;
    } else { box.hidden=true; }
  }
  function updateBar(){
    if(state.step===2){
      var n=state.selected.length;
      barInfo.textContent = n===0 ? 'Nog geen les gekozen'
        : (n===1?'1 les':n+' lessen')+' \\u00B7 richtprijs '+money(total())+' per jaar';
    } else if(state.step===4){
      barInfo.textContent='Richtprijs '+money(total())+' per jaar';
    } else {
      barInfo.textContent='';
    }
  }

  /* ---- validatie ---- */
  function showFormErr(id,msg){
    var e=$(id); if(!e) return;
    e.textContent=msg; e.classList.add('show');
  }
  function validate(step){
    var ok=true, first=null;
    function bad(el,msg){ setErr(el,msg); if(!first) first=el; ok=false; }
    if(step===1){
      var vn=$('d-voornaam'), an=$('d-achternaam'), gb=$('d-geboorte');
      if(!vn.value.trim()) bad(vn,'Vul de voornaam in.');
      if(!an.value.trim()) bad(an,'Vul de achternaam in.');
      var a=ageFrom(gb.value);
      if(a===null) bad(gb,'Vul een geldige geboortedatum in.');
      else if(a<3) bad(gb,'Dansen kan bij ons vanaf 3 jaar. Neem gerust contact op als je twijfelt.');
      else if(a>110) bad(gb,'Kijk de geboortedatum nog eens na.');
      else state.age=a;
      if(state.forSelf===null){ showFormErr('err-wie','Kies voor wie je inschrijft.'); ok=false; }
    }
    if(step===2){
      if(!state.selected.length){ showFormErr('err-lessen','Kies minstens één les om verder te gaan.'); ok=false; }
    }
    if(step===3){
      var em=$('c-email'), gs=$('c-gsm'), st=$('c-straat'), pc=$('c-postcode'), gm=$('c-gemeente');
      if(!/^[^@\\s]+@[^@\\s]+\\.[a-z]{2,}$/i.test(em.value.trim())) bad(em,'Vul een e-mailadres in waarop we je kunnen bereiken.');
      if(gs.value.replace(/\\D/g,'').length<9) bad(gs,'Vul een gsm-nummer in van minstens 9 cijfers.');
      if(!st.value.trim()) bad(st,'Vul straat en huisnummer in.');
      if(!/^\\d{4}$/.test(pc.value.trim())) bad(pc,'Een Belgische postcode heeft 4 cijfers.');
      if(!gm.value.trim()) bad(gm,'Vul de gemeente in.');
      if(state.age!==null && state.age<18){
        var ou=$('c-ouder');
        if(!ou.value.trim()) bad(ou,'Vul de naam van de ouder of voogd in.');
      }
    }
    if(step===4){
      var ak=$('s-akkoord');
      if(!ak.checked){ showFormErr('err-akkoord','Vink aan dat je akkoord gaat met de voorwaarden.'); ok=false; }
    }
    if(first){ first.focus(); first.scrollIntoView({block:'center',behavior:'smooth'}); }
    return ok;
  }

  /* ---- samenvatting ---- */
  function renderSummary(){
    var d=$('sum-danser'), l=$('sum-lessen'), c=$('sum-contact');
    if(!d) return;
    var naam=val('d-voornaam')+' '+val('d-achternaam');
    d.innerHTML=
      row('Naam',naam)+
      row('Geboortedatum',dateNL(val('d-geboorte'))+(state.age!==null?' ('+state.age+' jaar)':''))+
      row('Inschrijving voor', state.forSelf?'Mezelf':'Mijn kind');
    var lines=priceLines(), html='';
    lines.forEach(function(o){
      html+=row(o.c.style+' &middot; '+o.c.ages+'<br><span style="font-size:.85em">'+o.c.day+' '+o.c.time+' &middot; '+o.c.loc+'</span>', money(o.p));
    });
    html+='<div class="row total"><span>Richtprijs per jaar</span><span>'+money(total())+'</span></div>';
    l.innerHTML=html;
    var ct=row('E-mail',val('c-email'))+row('Gsm',val('c-gsm'))+
      row('Adres',val('c-straat')+', '+val('c-postcode')+' '+val('c-gemeente'));
    if(state.age!==null && state.age<18) ct+=row('Ouder of voogd',val('c-ouder'));
    c.innerHTML=ct;
    var st=$('sum-total'); if(st) st.textContent=money(total());
  }
  function row(k,v){
    return '<div class="row"><span class="k">'+k+'</span><span class="v">'+(v||'&mdash;')+'</span></div>';
  }

  /* ---- navigatie ---- */
  function go(n){
    if(n>state.step){ for(var s=state.step;s<n;s++){ if(!validate(s)) return; } }
    state.step=n;
    stepEls.forEach(function(el,i){ el.classList.toggle('active', i===n-1); });
    barItems.forEach(function(li,i){
      var cur = (n<STEPS && i===n-1);
      li.classList.toggle('current', cur);
      li.classList.toggle('done', n===STEPS || i<n-1);
      if(cur) li.setAttribute('aria-current','step'); else li.removeAttribute('aria-current');
    });
    counter.textContent = n<STEPS ? ('Stap '+n+' van '+(STEPS-1)) : 'Ingeschreven';
    btnPrev.hidden = (n===1 || n===STEPS);
    btnNext.textContent = n===STEPS-1 ? 'Inschrijving afronden' : 'Volgende';
    btnNext.hidden = (n===STEPS);
    var bar=document.querySelector('.wiz-bar'); if(bar) bar.hidden=(n===STEPS);
    /* de pitch hoort bij stap 1; daarna maakt hij enkel de mobiele pagina langer */
    var lede=document.querySelector('.wiz-head .lede'); if(lede) lede.hidden=(n>1);
    document.querySelectorAll('.formerr').forEach(function(e){e.classList.remove('show');});
    if(n===2){ renderCourses(); checkClash(); }
    if(n===4){ renderSummary(); }
    updateBar();
    var h=stepEls[n-1].querySelector('h2');
    if(h){ h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); }
    window.scrollTo({top:0,behavior:'smooth'});
  }
  btnNext.addEventListener('click',function(){ if(state.step<STEPS) go(state.step+1); });
  btnPrev.addEventListener('click',function(){ if(state.step>1) go(state.step-1); });
  document.querySelectorAll('[data-goto]').forEach(function(b){
    b.addEventListener('click',function(){ go(parseInt(b.dataset.goto,10)); });
  });

  [].slice.call(document.querySelectorAll('input[name=wie]')).forEach(function(r){
    r.addEventListener('change',function(){
      state.forSelf = r.value==='zelf';
      var e=$('err-wie'); if(e) e.classList.remove('show');
    });
  });
  var gb=$('d-geboorte');
  if(gb) gb.addEventListener('change',function(){
    var a=ageFrom(gb.value);
    state.age = (a!==null && a>=0 && a<=110) ? a : null;
    var p=$('ouderblok');
    if(p) p.hidden = !(state.age!==null && state.age<18);
    var t=$('les-intro');
    if(t) t.textContent = state.age!==null
      ? 'Dit zijn de lessen die passen bij '+ (state.age) +' jaar. Je mag er meerdere kiezen.'
      : 'Kies de lessen die je wil volgen. Je mag er meerdere kiezen.';
  });
  var sa=$('les-toonalles');
  if(sa) sa.addEventListener('click',function(){
    state.showAll=!state.showAll;
    sa.setAttribute('aria-pressed', state.showAll?'true':'false');
    sa.textContent = state.showAll ? 'Toon enkel passende lessen' : 'Toon alle lessen';
    renderCourses();
  });
  var lf=$('les-locatie');
  if(lf) lf.addEventListener('change',function(){ state.loc=lf.value; renderCourses(); });
  var ak=$('s-akkoord');
  if(ak) ak.addEventListener('change',function(){ var e=$('err-akkoord'); if(e) e.classList.remove('show'); });
  var again=$('wz-again');
  if(again) again.addEventListener('click',function(){ location.reload(); });

  go(1);
})();
"""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _base_style(style):
    s = style.replace(" gevorderden", "").replace(" ervaring", "")
    if s == "Klassiek":
        s = "Klassiek ballet"
    return s


def _level(style):
    if "gevorderden" in style:
        return "gevorderden"
    if "ervaring" in style:
        return "ervaring"
    return ""


def _start_minutes(time_str):
    """'16u30 – 17u30' -> 990. Onbekend formaat sorteert achteraan."""
    head = time_str.split("–")[0].strip()
    if "u" in head:
        hh, _, mm = head.partition("u")
        if hh.strip().isdigit():
            return int(hh) * 60 + (int(mm) if mm.strip().isdigit() else 0)
    return 24 * 60


def _sorted_schedule(brief):
    """Lessen op dag en beginuur, zodat een bezoeker chronologisch kan lezen."""
    order = {d: i for i, d in enumerate(DAY_ORDER)}
    return sorted(
        brief.get("schedule", []),
        key=lambda c: (order.get(c["day"], 99), _start_minutes(c["time"]), c["loc"]),
    )


def _href(slug, page=""):
    return f"/{slug}/" + (page + "/" if page else "")


def _nav(slug, active):
    pages = [("", "Home"), ("dansaanbod", "Dansaanbod"), ("uurrooster", "Uurrooster"),
             ("lesprijzen", "Lesprijzen")]
    out = []
    for key, label in pages:
        cur = ' aria-current="page"' if key == active else ""
        out.append(f'<a href="{_href(slug, key)}"{cur}>{esc(label)}</a>')
    out.append(f'<a href="{_href(slug)}#contact">Contact</a>')
    return "\n      ".join(out)


def _ribbon():
    return """<div class="ribbon" aria-hidden="true"><svg viewBox="0 0 620 520" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M40 430C130 300 60 190 200 120c140-70 210 40 300-20 60-40 70-90 60-110" stroke="#F7D8D0" stroke-width="58" stroke-linecap="round"/>
  <path d="M90 470C180 340 110 230 250 160c140-70 210 40 300-20 60-40 70-90 60-110" stroke="#CE181C" stroke-width="12" stroke-linecap="round" opacity=".85"/>
  <path d="M140 500C230 370 160 260 300 190c140-70 210 40 300-20" stroke="#1B1220" stroke-width="3" stroke-linecap="round" opacity=".35"/>
  <circle cx="558" cy="86" r="13" fill="#CE181C"/>
</svg></div>"""


def _shell(brief, *, title, description, active, body, page_js="", head_extra=""):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    phone = esc(brief.get("phone", ""))
    phone_href = phone.replace(" ", "")
    email = esc(brief.get("email", ""))
    address = esc(brief.get("address", ""))
    address_note = esc(brief.get("address_note", ""))
    vat = esc(brief.get("vat", ""))
    socials = brief.get("socials", {})
    soc_labels = {"facebook": "Facebook", "instagram": "Instagram", "tiktok": "TikTok",
                  "youtube": "YouTube", "linkedin": "LinkedIn"}
    soc_html = "\n        ".join(
        f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(soc_labels.get(net, net.capitalize()))}</a>'
        for net, url in socials.items()
    )
    locs = "\n          ".join(
        f'<li>{esc(l["name"])} &middot; {esc(l["address"])}</li>' for l in brief.get("locations", [])
    )
    js = NAV_JS + page_js

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS_HREF}" rel="stylesheet">
<style>{CSS}</style>
{head_extra}
</head>
<body>
<a class="skip" href="#main">Naar de inhoud</a>

<header class="site-head">
  <div class="wrap">
    <a class="logo" href="{_href(slug)}">
      <span class="word">Pivolt&eacute;</span>
      <span class="sub">Dansstudio</span>
    </a>
    <nav class="main" id="mainnav" aria-label="Hoofdnavigatie">
      {_nav(slug, active)}
    </nav>
    <a class="btn-signup" href="{_href(slug, 'inschrijven')}">Inschrijven</a>
    <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="mainnav"><span></span></button>
  </div>
</header>

<main id="main">
{body}
</main>

<footer class="site" id="contact">
  <div class="wrap">
    <div class="cols">
      <div>
        <h4>{name}</h4>
        <p>{address}<br><span style="opacity:.7">{address_note}</span></p>
        <p style="margin-top:14px">
          <a href="tel:{phone_href}">{phone}</a><br>
          <a href="mailto:{email}">{email}</a>
        </p>
        <div class="socials">
        {soc_html}
        </div>
      </div>
      <div>
        <h4>Danslocaties</h4>
        <ul>
          {locs}
        </ul>
      </div>
      <div>
        <h4>Snel naar</h4>
        <ul>
          <li><a href="{_href(slug, 'dansaanbod')}">Dansaanbod</a></li>
          <li><a href="{_href(slug, 'uurrooster')}">Uurrooster</a></li>
          <li><a href="{_href(slug, 'lesprijzen')}">Lesprijzen</a></li>
          <li><a href="{_href(slug, 'inschrijven')}">Inschrijven</a></li>
        </ul>
      </div>
    </div>
    <div class="fine">
      <span>{vat}</span>
      <span>Prototype gebouwd voor {name} &middot; <a href="https://ocior.be" target="_blank" rel="noopener">ocior.be</a></span>
    </div>
  </div>
</footer>

<script>{js}</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# pagina's
# --------------------------------------------------------------------------- #

def render(brief: dict) -> str:
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    tagline = esc(brief.get("tagline", ""))
    category = esc(brief.get("category", ""))
    about = esc(brief.get("about", ""))
    about_short = esc(brief.get("about_short", ""))
    season = esc(brief.get("season", ""))

    stats = "\n      ".join(
        f'<div class="stat"><div class="num">{esc(s["value"])}</div><div class="lbl">{esc(s["label"])}</div></div>'
        for s in brief.get("stats", [])
    )
    marquee_items = [s["name"] for s in brief.get("styles", [])]
    marquee = "".join(f"<span>{esc(i)}</span>" for i in marquee_items)
    styles_cards = "\n      ".join(
        f'<article class="card"><span class="tag">{esc(s["ages"])}</span><h3>{esc(s["name"])}</h3><p>{esc(s["desc"])}</p></article>'
        for s in brief.get("styles", [])[:6]
    )
    highlights = build_highlights(brief.get("highlights", []), mark="/")
    news_cards = "\n      ".join(
        f'<article class="card"><span class="tag">{esc(n["when"])}</span><h3>{esc(n["title"])}</h3><p>{esc(n["desc"])}</p></article>'
        for n in brief.get("news", [])
    )
    demo = brief.get("demo", {})
    demo_cards = "\n      ".join(
        f'<article class="card"><span class="tag">{esc(g["ages"])}</span><h3>{esc(g["name"])}</h3><p>{esc(g["desc"])}</p></article>'
        for g in demo.get("groups", [])
    )
    faq_html = "\n      ".join(
        f'<details class="faq"><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>'
        for f in brief.get("faq", [])
    )
    loc_rows = "\n        ".join(
        '<li><span><span class="nm">{nm}</span><br><span class="ad">{ad}{note}</span></span>'
        '<a href="https://www.google.com/maps/search/?api=1&query={q}" target="_blank" rel="noopener">Op kaart &rarr;</a></li>'.format(
            nm=esc(l["name"]), ad=esc(l["address"]),
            note=(" &middot; " + esc(l["note"])) if l.get("note") else "",
            q=_maps_query(esc(l["address"])),
        )
        for l in brief.get("locations", [])
    )

    body = f"""
<section class="hero">
  {_ribbon()}
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">{category}</span>
        <h1>Laat je passie <em>dansen</em></h1>
        <p class="lede">{about_short}</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{_href(slug, 'inschrijven')}">Schrijf je in voor {season}</a>
          <a class="btn btn-ghost" href="{_href(slug, 'uurrooster')}">Bekijk het uurrooster</a>
        </div>
      </div>
      <div class="stats">
      {stats}
      </div>
    </div>
  </div>
</section>

<div class="marquee" aria-hidden="true">
  <div class="marquee-track">{marquee}{marquee}</div>
</div>

<section>
  <div class="wrap">
    <div class="two-col">
      <div>
        <p class="kicker">Over de school</p>
        <h2>Al {esc(brief.get("years_active", ""))} jaar dansen in <em>Brasschaat en Schoten</em></h2>
        <p style="color:var(--ink-2);margin-top:16px">{about}</p>
        <div class="hero-actions">
          <a class="btn btn-ghost" href="{_href(slug, 'dansaanbod')}">Ontdek het dansaanbod</a>
        </div>
      </div>
      <div>
        <ul class="highlights">
        {highlights}
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Dansstijlen</p>
      <h2>Van kleuterdans tot <em>floorwork</em></h2>
      <p>Negen stijlen, elk met een eigen startleeftijd. Twijfel je? In juni en september kan je gratis komen proeven.</p>
    </div>
    <div class="cards">
      {styles_cards}
    </div>
    <div class="hero-actions">
      <a class="btn btn-ghost" href="{_href(slug, 'dansaanbod')}">Alle stijlen en het volledige aanbod</a>
    </div>
  </div>
</section>

<section class="dark">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Demogroepen</p>
      <h2>Dansen op wedstrijdniveau</h2>
      <p>{esc(demo.get("intro", ""))}</p>
    </div>
    <div class="cards">
      {demo_cards}
    </div>
    <p style="margin-top:22px">{esc(demo.get("note", ""))}</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="two-col">
      <div>
        <p class="kicker">Waar</p>
        <h2>Vijf zalen, <em>twee gemeentes</em></h2>
        <p style="color:var(--ink-2);margin-top:14px">De lessen gaan door in Brasschaat en Schoten. In het uurrooster kan je meteen filteren op locatie, dag, stijl en leeftijd.</p>
        <ul class="loc-list" style="margin-top:22px">
        {loc_rows}
        </ul>
      </div>
      <div>
        <p class="kicker">Nieuws</p>
        <h2>Dit seizoen</h2>
        <div class="cards" style="grid-template-columns:1fr;margin-top:20px">
        {news_cards}
        </div>
      </div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap-narrow">
    <div class="section-head">
      <p class="kicker">Veelgestelde vragen</p>
      <h2>Goed om te weten</h2>
    </div>
    {faq_html}
  </div>
</section>

<section>
  <div class="wrap">
    <div class="cta-band">
      <h2>Klaar om in te schrijven?</h2>
      <p>Eén pagina, vier stappen, geen account nodig. Je kiest je lessen en ziet meteen wat het kost.</p>
      <a class="btn btn-primary" href="{_href(slug, 'inschrijven')}">Start je inschrijving</a>
    </div>
  </div>
</section>
"""
    return _shell(
        brief,
        title=f"{name} &mdash; {category}",
        description=f"{tagline}. Dansles vanaf 3 jaar in Brasschaat en Schoten.",
        active="",
        body=body,
    )


def _page_dansaanbod(brief):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    demo = brief.get("demo", {})
    styles_cards = "\n      ".join(
        f'<article class="card"><span class="tag">{esc(s["ages"])}</span><h3>{esc(s["name"])}</h3><p>{esc(s["desc"])}</p></article>'
        for s in brief.get("styles", [])
    )
    demo_cards = "\n      ".join(
        f'<article class="card"><span class="tag">{esc(g["ages"])}</span><h3>{esc(g["name"])}</h3><p>{esc(g["desc"])}</p></article>'
        for g in demo.get("groups", [])
    )
    extra_cards = "\n      ".join(
        f'<article class="card"><span class="tag">{esc(x["who"])}</span><h3>{esc(x["name"])}</h3><p>{esc(x["desc"])}</p></article>'
        for x in brief.get("extra_offer", [])
    )
    people = "\n        ".join(
        f'<li><div class="nm">{esc(t["name"])}</div><div class="rl">{esc(t["role"])}</div></li>'
        for t in brief.get("teachers", [])
    )

    body = f"""
<section class="hero" style="padding-bottom:34px">
  {_ribbon()}
  <div class="wrap">
    <span class="eyebrow">Dansaanbod</span>
    <h1>Negen stijlen, <em>één school</em></h1>
    <p class="lede">Van je eerste passen als kleuter tot techniekles voor volwassenen. Elke stijl heeft een startleeftijd; de docent kijkt bij een proefles mee of de groep past.</p>
  </div>
</section>

<section style="padding-top:20px">
  <div class="wrap">
    <div class="cards">
      {styles_cards}
    </div>
  </div>
</section>

<section class="dark">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Demogroepen</p>
      <h2>Voor wie verder wil gaan</h2>
      <p>{esc(demo.get("intro", ""))}</p>
    </div>
    <div class="cards">
      {demo_cards}
    </div>
    <p style="margin-top:22px">{esc(demo.get("note", ""))}</p>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Naast de wekelijkse les</p>
      <h2>Dansdagen, workshops en <em>privéles</em></h2>
    </div>
    <div class="cards two">
      {extra_cards}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head">
      <p class="kicker">Docenten</p>
      <h2>Wie voor de klas staat</h2>
      <p>Alle lesgevers volgden zelf een dansopleiding en geven les in hun eigen specialiteit.</p>
    </div>
    <ul class="people">
      {people}
    </ul>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="cta-band">
      <h2>Eerst eens proeven?</h2>
      <p>In juni en september kan je gratis proeflessen volgen. Je komt langs op het uur van de les en verwittigt de docent ter plaatse.</p>
      <a class="btn btn-primary" href="{_href(slug, 'uurrooster')}">Bekijk wanneer welke les doorgaat</a>
    </div>
  </div>
</section>
"""
    return _shell(
        brief,
        title=f"Dansaanbod &mdash; {name}",
        description="Kleuterdans, kinderdans, klassiek ballet, jazz, modern, hiphop, pointes, floorwork en musical.",
        active="dansaanbod",
        body=body,
    )


def _page_uurrooster(brief):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    season = esc(brief.get("season", ""))
    schedule = _sorted_schedule(brief)

    days = [d for d in DAY_ORDER if any(c["day"] == d for c in schedule)]
    locs = sorted({c["loc"] for c in schedule})
    styles = sorted({_base_style(c["style"]) for c in schedule})

    groups = []
    for day in days:
        rows = []
        for c in schedule:
            if c["day"] != day:
                continue
            lvl = _level(c["style"])
            lvl_html = f'<span class="badge lvl">{esc(lvl)}</span>' if lvl else ""
            demo_html = '<span class="badge">auditie</span>' if c.get("demo") else ""
            rows.append(
                '<div class="lesrow" data-day="{day}" data-loc="{loc}" data-style="{base}" data-min="{mn}" data-max="{mx}">'
                '<div class="tm">{time}</div>'
                '<div><div class="st">{style}{lvl}{demo}</div><div class="meta">{ages}</div></div>'
                '<div class="loc">{loc}<br>{addr}</div>'
                "</div>".format(
                    day=esc(day), loc=esc(c["loc"]), base=esc(_base_style(c["style"])),
                    mn=c["min"], mx=c["max"], time=esc(c["time"]),
                    style=esc(_base_style(c["style"])), lvl=lvl_html, demo=demo_html,
                    ages=esc(c["ages"]), addr=esc(c["addr"]),
                )
            )
        groups.append(
            f'<div class="daygroup"><h3>{esc(day)}</h3>' + "\n      ".join(rows) + "</div>"
        )

    day_opts = "\n        ".join(f'<option value="{esc(d)}">{esc(d)}</option>' for d in days)
    loc_opts = "\n        ".join(f'<option value="{esc(l)}">{esc(l)}</option>' for l in locs)
    style_opts = "\n        ".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in styles)
    loc_rows = "\n        ".join(
        '<li><span><span class="nm">{nm}</span><br><span class="ad">{ad}</span></span>'
        '<a href="https://www.google.com/maps/search/?api=1&query={q}" target="_blank" rel="noopener">Op kaart &rarr;</a></li>'.format(
            nm=esc(l["name"]), ad=esc(l["address"]), q=_maps_query(esc(l["address"])),
        )
        for l in brief.get("locations", [])
    )

    body = f"""
<section class="hero" style="padding-bottom:30px">
  {_ribbon()}
  <div class="wrap">
    <span class="eyebrow">Uurrooster {season}</span>
    <h1>Wanneer danst <em>jij</em>?</h1>
    <p class="lede">{len(schedule)} lessen per week, verspreid over vijf zalen. Filter op dag, locatie, stijl of leeftijd &mdash; of vul gewoon je leeftijd in en zie wat overblijft.</p>
  </div>
</section>

<section style="padding-top:10px">
  <div class="wrap">
    <div class="filters">
      <div class="f">
        <label for="f-day">Dag</label>
        <select id="f-day"><option value="">Alle dagen</option>
        {day_opts}
        </select>
      </div>
      <div class="f">
        <label for="f-loc">Locatie</label>
        <select id="f-loc"><option value="">Alle locaties</option>
        {loc_opts}
        </select>
      </div>
      <div class="f">
        <label for="f-style">Dansstijl</label>
        <select id="f-style"><option value="">Alle stijlen</option>
        {style_opts}
        </select>
      </div>
      <div class="f">
        <label for="f-age">Leeftijd</label>
        <input id="f-age" type="number" inputmode="numeric" min="3" max="99" placeholder="bv. 8">
      </div>
    </div>

    <div class="filter-meta">
      <span class="count" id="f-count" role="status" aria-live="polite"></span>
      <button class="linkish" type="button" id="f-reset">Filters wissen</button>
    </div>

    <div class="empty" id="f-empty" hidden>Geen les gevonden met deze combinatie. Probeer een andere dag of locatie, of bel ons &mdash; er is vaak meer mogelijk dan het rooster toont.</div>

    {"".join(groups)}

    <div class="note" style="margin-top:26px">
      Privélessen gaan door op afspraak. Roosters kunnen tijdens het seizoen wijzigen &mdash; de school bevestigt je definitieve lesuur bij de inschrijving.
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="two-col">
      <div>
        <p class="kicker">Locaties</p>
        <h2>Waar de lessen <em>doorgaan</em></h2>
        <ul class="loc-list" style="margin-top:20px">
        {loc_rows}
        </ul>
      </div>
      <div>
        <div class="cta-band">
          <h2>Les gevonden?</h2>
          <p>Schrijf je in en kies je lessen in één doorlopend formulier.</p>
          <a class="btn btn-primary" href="{_href(slug, 'inschrijven')}">Naar de inschrijving</a>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    return _shell(
        brief,
        title=f"Uurrooster {season} &mdash; {name}",
        description="Het volledige lesrooster, filterbaar op dag, locatie, stijl en leeftijd.",
        active="uurrooster",
        body=body,
        page_js=FILTER_JS,
    )


def _page_lesprijzen(brief):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    prices = brief.get("prices", {})
    season = esc(brief.get("price_season", ""))

    def table(rows):
        return "\n      ".join(
            f'<div class="row"><span>{esc(r["label"])}</span><span class="amt">{esc(r["price"])}</span></div>'
            for r in rows
        )

    faq_html = "\n      ".join(
        f'<details class="faq"><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>'
        for f in brief.get("faq", [])
    )
    extras = build_list([x["name"] + " — " + x["who"] for x in brief.get("extra_offer", [])])

    body = f"""
<section class="hero" style="padding-bottom:26px">
  {_ribbon()}
  <div class="wrap">
    <span class="eyebrow">Lesprijzen {season}</span>
    <h1>Wat kost een <em>dansjaar</em>?</h1>
    <p class="lede">Eén bedrag voor het hele seizoen. Volg je meerdere lessen per week, dan zakt het tarief per bijkomende les.</p>
  </div>
</section>

<section style="padding-top:10px">
  <div class="wrap">
    <div class="two-col">
      <div>
        <div class="pricetable">
          <h3>Danslessen</h3>
          {table(prices.get("lessons", []))}
        </div>
        <div class="pricetable" style="margin-top:18px">
          <h3>Demo &amp; privéles</h3>
          {table(prices.get("demo", []))}
        </div>
        <div class="pricetable" style="margin-top:18px">
          <h3>Dansdagen, -avonden &amp; workshops</h3>
          {table(prices.get("extras", []))}
        </div>
        <div class="note" style="margin-top:20px">{esc(prices.get("season_note", ""))}</div>
      </div>
      <div>
        <p class="kicker">Zo werkt het</p>
        <h2>Van proefles tot <em>plaats in de groep</em></h2>
        <ul class="highlights" style="margin-top:18px">
          <li><span class="mark">1</span>Kom gratis proeven in juni of september &mdash; gewoon langskomen en de docent verwittigen.</li>
          <li><span class="mark">2</span>Schrijf online in. Je kiest je lessen en ziet meteen de richtprijs.</li>
          <li><span class="mark">3</span>De school bevestigt je plaats en bezorgt de betaalgegevens.</li>
          <li><span class="mark">4</span>Je danst het hele seizoen mee, tot en met de shows op het einde.</li>
        </ul>
        <p class="kicker" style="margin-top:32px">Ook mogelijk</p>
        <ul class="pill-list">
          {extras}
        </ul>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{_href(slug, 'inschrijven')}">Bereken je eigen prijs</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap-narrow">
    <div class="section-head">
      <p class="kicker">Veelgestelde vragen</p>
      <h2>Nog een vraag?</h2>
    </div>
    {faq_html}
  </div>
</section>
"""
    return _shell(
        brief,
        title=f"Lesprijzen &mdash; {name}",
        description="Jaartarieven voor de danslessen, demogroepen, dansdagen en workshops.",
        active="lesprijzen",
        body=body,
    )


def _page_inschrijven(brief):
    slug = esc(brief["slug"])
    name = esc(brief["business_name"])
    season = esc(brief.get("season", ""))
    schedule = _sorted_schedule(brief)
    email = esc(brief.get("email", ""))
    phone = esc(brief.get("phone", ""))
    phone_href = phone.replace(" ", "")

    courses = [
        {
            "day": c["day"], "loc": c["loc"], "addr": c["addr"], "time": c["time"],
            "style": _base_style(c["style"]) + ((" (" + _level(c["style"]) + ")") if _level(c["style"]) else ""),
            "ages": c["ages"], "min": c["min"], "max": c["max"],
            "demo": bool(c.get("demo")), "price": c.get("price"),
        }
        for c in schedule
    ]
    tariffs = []
    for row in brief.get("prices", {}).get("lessons", []):
        digits = "".join(ch for ch in row["price"].split("euro")[0] if ch.isdigit())
        if digits:
            tariffs.append(int(digits))
    if not tariffs:
        tariffs = [195, 185, 175, 165]

    data_js = json.dumps(courses, ensure_ascii=False).replace("<", "\\u003c")
    js = (WIZARD_JS
          .replace("__COURSES__", data_js)
          .replace("__TARIFFS__", json.dumps(tariffs))
          .replace("__DAYS__", json.dumps(DAY_ORDER, ensure_ascii=False)))

    locs = sorted({c["loc"] for c in schedule})
    loc_opts = "\n            ".join(f'<option value="{esc(l)}">{esc(l)}</option>' for l in locs)

    steps_labels = ["Danser", "Lessen", "Contact", "Nakijken"]
    steps_html = "\n      ".join(
        f'<li><span class="bar"></span><span class="nm">{esc(l)}</span></li>' for l in steps_labels
    )

    body = f"""
<div class="protobar">
  <div class="wrap"><strong>Prototype.</strong> Dit formulier verstuurt niets en bewaart niets &mdash; het toont hoe inschrijven zou kunnen werken.</div>
</div>

<section class="wiz-head">
  <div class="wrap-narrow">
    <span class="eyebrow">Inschrijven {season}</span>
    <h1>Vier stappen, <em>geen account</em></h1>
    <p class="lede">Je hoeft niets aan te maken en nergens apart in te loggen. Vul in wie er komt dansen, kies de lessen, en je ziet meteen wat het kost.</p>
    <ol class="steps" aria-label="Voortgang">
      {steps_html}
    </ol>
    <p class="stepcount" id="stepcount">Stap 1 van 4</p>
  </div>
</section>

<div class="wrap-narrow">

  <section class="step active" id="step1">
    <h2>Wie komt er dansen?</h2>
    <p class="sub">We gebruiken de geboortedatum om de juiste lesgroepen te tonen.</p>

    <fieldset class="field">
      <legend class="lab">Voor wie schrijf je in?</legend>
      <div class="choice">
        <input type="radio" name="wie" id="wie-kind" value="kind">
        <label for="wie-kind"><span class="dot"></span>Voor mijn kind</label>
        <input type="radio" name="wie" id="wie-zelf" value="zelf">
        <label for="wie-zelf"><span class="dot"></span>Voor mezelf</label>
      </div>
      <p class="formerr" id="err-wie" role="alert"></p>
    </fieldset>

    <div class="grid-2">
      <div class="field">
        <label for="d-voornaam">Voornaam van de danser</label>
        <input id="d-voornaam" type="text" autocomplete="given-name" enterkeyhint="next">
        <p class="err"></p>
      </div>
      <div class="field">
        <label for="d-achternaam">Achternaam</label>
        <input id="d-achternaam" type="text" autocomplete="family-name" enterkeyhint="next">
        <p class="err"></p>
      </div>
    </div>

    <div class="field">
      <label for="d-geboorte">Geboortedatum</label>
      <p class="hint">Dansen kan bij ons vanaf 3 jaar.</p>
      <input id="d-geboorte" type="date" autocomplete="bday">
      <p class="err"></p>
    </div>
  </section>

  <section class="step" id="step2">
    <h2>Kies je lessen</h2>
    <p class="sub" id="les-intro">Kies de lessen die je wil volgen. Je mag er meerdere kiezen.</p>

    <div class="chips">
      <button class="chip" type="button" id="les-toonalles" aria-pressed="false">Toon alle lessen</button>
    </div>
    <div class="field">
      <label for="les-locatie">Filter op locatie</label>
      <select id="les-locatie">
        <option value="">Alle locaties</option>
            {loc_opts}
      </select>
    </div>

    <div class="warn" id="clash" hidden></div>
    <p class="formerr" id="err-lessen" role="alert"></p>
    <div id="les-list"></div>

    <div class="note" style="margin-top:20px">
      Bij demogroepen hoort een auditie of selectie. Je mag ze hier aanduiden &mdash; de school neemt daarna contact op over het auditiemoment.
    </div>
  </section>

  <section class="step" id="step3">
    <h2>Hoe bereiken we je?</h2>
    <p class="sub">Eén e-mailadres en gsm-nummer volstaan. Je krijgt de bevestiging per mail.</p>

    <div class="field">
      <label for="c-email">E-mailadres</label>
      <input id="c-email" type="email" inputmode="email" autocomplete="email" enterkeyhint="next">
      <p class="err"></p>
    </div>
    <div class="field">
      <label for="c-gsm">Gsm-nummer</label>
      <input id="c-gsm" type="tel" inputmode="tel" autocomplete="tel" placeholder="04.. .. .. ..">
      <p class="err"></p>
    </div>
    <div class="field">
      <label for="c-straat">Straat en huisnummer</label>
      <input id="c-straat" type="text" autocomplete="street-address">
      <p class="err"></p>
    </div>
    <div class="grid-2">
      <div class="field">
        <label for="c-postcode">Postcode</label>
        <input id="c-postcode" type="text" inputmode="numeric" maxlength="4" autocomplete="postal-code">
        <p class="err"></p>
      </div>
      <div class="field">
        <label for="c-gemeente">Gemeente</label>
        <input id="c-gemeente" type="text" autocomplete="address-level2">
        <p class="err"></p>
      </div>
    </div>
    <div id="ouderblok" hidden>
      <div class="field">
        <label for="c-ouder">Naam van de ouder of voogd</label>
        <p class="hint">Nodig zolang de danser jonger is dan 18.</p>
        <input id="c-ouder" type="text" autocomplete="name">
        <p class="err"></p>
      </div>
    </div>
  </section>

  <section class="step" id="step4">
    <h2>Nog even nakijken</h2>
    <p class="sub">Klopt alles? Dan ben je klaar. Aanpassen kan met de knopjes hiernaast.</p>

    <div class="summary">
      <div class="head"><span>De danser</span><button type="button" data-goto="1">Aanpassen</button></div>
      <div id="sum-danser"></div>
    </div>
    <div class="summary">
      <div class="head"><span>Gekozen lessen</span><button type="button" data-goto="2">Aanpassen</button></div>
      <div id="sum-lessen"></div>
    </div>
    <div class="summary">
      <div class="head"><span>Contactgegevens</span><button type="button" data-goto="3">Aanpassen</button></div>
      <div id="sum-contact"></div>
    </div>

    <div class="field">
      <label for="s-opmerking">Iets dat we moeten weten? (optioneel)</label>
      <p class="hint">Bijvoorbeeld een blessure, allergie of een vraag over de groep.</p>
      <textarea id="s-opmerking"></textarea>
    </div>

    <label class="check"><input type="checkbox" id="s-akkoord"><span>Ik ga akkoord met de algemene voorwaarden en de privacyverklaring van {name}.</span></label>
    <label class="check"><input type="checkbox" id="s-fotos"><span>Foto's van lessen en shows mogen gebruikt worden op de website en sociale media. (optioneel)</span></label>
    <p class="formerr" id="err-akkoord" role="alert"></p>

    <div class="note">De richtprijs van <strong id="sum-total"></strong> per jaar is berekend op de gepubliceerde tarieven. De school bevestigt het exacte bedrag samen met je plaats in de groep.</div>
  </section>

  <section class="step" id="step5">
    <div class="done-mark" aria-hidden="true">
      <svg width="34" height="34" viewBox="0 0 24 24" fill="none"><path d="M4 12.5l5 5 11-11" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </div>
    <h2>Dat was het</h2>
    <p class="sub">In de echte versie krijg je nu een bevestigingsmail met je gekozen lessen, het lesuur, de locatie en het te betalen bedrag. De school bevestigt je plaats in de groep.</p>
    <div class="note" style="margin-bottom:22px">
      <strong>Dit is een prototype.</strong> Er is niets verzonden en er werd niets bewaard. Zodra je deze pagina sluit of herlaadt, zijn de ingevulde gegevens weg.
    </div>
    <p style="color:var(--ink-2)">Vragen over dit prototype of over een inschrijving? Mail naar <a href="mailto:{email}" style="color:var(--red);font-weight:700">{email}</a> of bel <a href="tel:{phone_href}" style="color:var(--red);font-weight:700">{phone}</a>.</p>
    <div class="hero-actions">
      <button class="btn btn-ghost" type="button" id="wz-again">Opnieuw beginnen</button>
      <a class="btn btn-primary" href="{_href(slug)}">Terug naar de site</a>
    </div>
  </section>

</div>

<div class="wiz-bar">
  <div class="wrap-narrow">
    <button class="btn btn-ghost" type="button" id="wz-prev" hidden>Terug</button>
    <span class="info" id="wz-info" aria-live="polite"></span>
    <button class="btn btn-primary" type="button" id="wz-next">Volgende</button>
  </div>
</div>
"""
    return _shell(
        brief,
        title=f"Inschrijven {season} &mdash; {name}",
        description="Schrijf je in voor het nieuwe dansseizoen. Vier stappen, geen account nodig.",
        active="inschrijven",
        body=body,
        page_js=js,
    )


def render_extra_pages(brief: dict) -> dict:
    return {
        "dansaanbod/index.html": _page_dansaanbod(brief),
        "uurrooster/index.html": _page_uurrooster(brief),
        "lesprijzen/index.html": _page_lesprijzen(brief),
        "inschrijven/index.html": _page_inschrijven(brief),
    }
