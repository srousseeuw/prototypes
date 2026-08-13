#!/usr/bin/env python3
"""
Site generator voor prototype.ocior.be
Gebruik: python3 generate.py briefs/<bedrijf>.json
Output:  ../sites/<slug>/index.html  (klaar om te pushen naar GitHub/Cloudflare Pages)

Sectorsjablonen staan in templates/<sector>.py, elk met een render(brief) functie.
Welk sjabloon gebruikt wordt, bepaalt het "sector" veld in de brief-JSON.

Een sjabloon mag daarnaast render_extra_pages(brief) aanbieden, die een dict
{relatief/pad.html: html} teruggeeft voor subpagina's (bv. een bestelpagina).
"""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

def main():
    if len(sys.argv) != 2:
        print("Gebruik: python3 generate.py briefs/<bedrijf>.json")
        sys.exit(1)

    brief_path = Path(sys.argv[1])
    brief = json.loads(brief_path.read_text(encoding="utf-8"))

    sector = brief.get("sector", "bakery")
    try:
        template = importlib.import_module(f"templates.{sector}")
    except ModuleNotFoundError:
        available = sorted(p.stem for p in (ROOT / "templates").glob("*.py") if p.stem not in ("__init__", "common"))
        print(f"Onbekende sector '{sector}'. Beschikbaar: {', '.join(available)}")
        sys.exit(1)

    out_dir = ROOT.parent / "sites" / brief["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    html = template.render(brief)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Gegenereerd: {out_dir / 'index.html'}")

    extra = getattr(template, "render_extra_pages", None)
    if extra:
        for rel_path, page_html in extra(brief).items():
            page_path = out_dir / rel_path
            page_path.parent.mkdir(parents=True, exist_ok=True)
            page_path.write_text(page_html, encoding="utf-8")
            print(f"✓ Gegenereerd: {page_path}")

if __name__ == "__main__":
    main()
