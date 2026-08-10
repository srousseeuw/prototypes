# prototypes — ocior.be

Automatisch gegenereerde website-prototypes voor lokale ondernemers rond
Essen. Zie `CLAUDE.md` voor de workflow die Claude Code volgt bij het maken
van een nieuw prototype.

## 1. Deze bestanden in je lokale repo zetten

Pak de zip uit in `/Users/seb/Documents/GitHub/prototypes` (of kopieer de
inhoud erin als de map al bestaat), dan in Terminal:

```bash
cd /Users/seb/Documents/GitHub/prototypes
git init                      # als dit nog niet gebeurd is
git add .
git commit -m "Init: sitegen + eerste prototype (Bakkerij Van Thillo)"
git branch -M main
git remote add origin git@github.com:<jouw-gebruikersnaam>/prototypes.git
git push -u origin main
```

(Vervang de remote-URL door die van je eigen GitHub-repo — te vinden via
"Code" → "SSH" of "HTTPS" op de GitHub-repopagina.)

## 2. Cloudflare Pages koppelen

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**.
2. Kies de `prototypes` repo.
3. Build-instellingen:
   - **Build command**: (leeg laten — het zijn statische bestanden)
   - **Build output directory**: `sites`
4. Deploy. Cloudflare geeft je een `*.pages.dev`-URL — test die eerst.
5. **Custom domain**: voeg `prototype.ocior.be` toe onder het Pages-project
   → Cloudflare zet automatisch de juiste DNS-record (als het domein al in
   je Cloudflare-account zit).

Resultaat: elke push naar `main` deployt automatisch. Een prototype in
`sites/<slug>/index.html` is dan live op
`https://prototype.ocior.be/<slug>/`.

## 3. Claude Code gebruiken voor nieuwe prototypes

Open deze map in Claude Code en geef gewoon de opdracht, bv.:

> Maak een prototype voor Bakkerij 't Bakkershuizeke in Essen, adres Over d'Aa
> 171. Zoek de gegevens op en genereer + commit + push.

Claude Code volgt dan automatisch de stappen in `CLAUDE.md`.

## 4. Outreach-mail (bewust nog manueel)

Er is voorlopig geen automatische verzendstap. Zodra jullie hier klaar voor
zijn, koppelen we sebastiaan@ocior.be (Gmail of AgentMail) zodat Claude
automatisch een gepersonaliseerde **draft** klaarzet per nieuw prototype —
Sebastiaan verstuurt die dan met één klik. Volledig automatisch verzenden
raden we af zonder een korte check op de regels rond ongevraagde B2B-mail in
België.

## Wildcard-subdomeinen (optioneel, later)

Momenteel draait alles via paden (`prototype.ocior.be/<slug>/`). Wil je
liever per zaak een eigen subdomein (`bakkerij-van-thillo.prototype.ocior.be`),
dan is dat mogelijk met een kleine Cloudflare Worker die op basis van de
hostname doorroutet — laat het weten en die bouwen we erbij.
