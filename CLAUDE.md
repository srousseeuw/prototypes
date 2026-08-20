# Prototypes — ocior.be

Dit is de repo voor automatisch gegenereerde website-prototypes voor lokale
ondernemers rond Essen. Doel: minimale effort, maximaal herbruikbaar.

## Structuur

```
sitegen/
  generate.py          → genereert een site vanuit een JSON-brief
  briefs/<slug>.json    → één databestand per bedrijf
sites/
  index.html            → overzichtspagina van alle prototypes
  <slug>/index.html     → het gegenereerde prototype (Cloudflare Pages servet dit op
                           prototype.ocior.be/<slug>/)
```

## Workflow voor een NIEUW prototype

Wanneer gevraagd wordt "maak een prototype voor [bedrijfsnaam] in Essen":

1. **Data verzamelen**
   - Gebruik de `places_search` tool (Google Places) om naam, adres, telefoon,
     openingsuren, categorie en rating op te halen.
   - Als het bedrijf al een website heeft: fetch die site en haal er extra
     content uit (diensten, foto's, tone-of-voice, unique selling points).
   - Vul ontbrekende velden aan met korte, feitelijke copy — nooit reviews
     woordelijk overnemen (auteursrecht), wel de teneur ervan parafraseren.

2. **Brief schrijven**
   - Maak `sitegen/briefs/<slug>.json` volgens het schema van
     `bakkerij-van-thillo.json` (zelfde velden, andere inhoud).
   - `slug` = lowercase, spaties → streepjes, geen speciale tekens.

3. **Site genereren**
   ```
   python3 sitegen/generate.py sitegen/briefs/<slug>.json
   ```
   Dit schrijft direct naar `sites/<slug>/index.html` in deze repo.

4. **Overzichtspagina bijwerken**
   ```
   python3 sitegen/build_index.py
   ```
   Dit genereert `sites/index.html` opnieuw uit alle briefs. Bewerk dat
   bestand nooit met de hand — draai dit script na elk nieuw of verwijderd
   prototype, dan kan het overzicht niet uit sync lopen.

5. **Committen en pushen**
   ```
   git add sites/<slug> sitegen/briefs/<slug>.json sites/index.html
   git commit -m "Prototype: <bedrijfsnaam>"
   git push
   ```
   Cloudflare Pages pikt de push automatisch op — geen verdere actie nodig.
   Live op: `https://prototype.ocior.be/<slug>/`

## Handgemaakte sites

Niet elke site komt uit een sjabloon. Wie met de hand gemaakt is (of
rechtstreeks via GitHub geüpload), krijgt tóch een brief, zodat hij op het
overzicht verschijnt — maar met:

```json
"generated": false
```

`generate.py` weigert dan te schrijven, ook binnen een lus over alle briefs.
Bewerk zo'n site rechtstreeks in `sites/<slug>/index.html`.

## Outreach bijhouden

De overzichtspagina toont per prototype de contactstatus en laat erop
filteren. Die status staat in de brief zelf, zodat er maar één bron van
waarheid is:

```json
"outreach": {
  "status": "gecontacteerd",
  "date": "2026-08-13",
  "note": "via contactformulier"
}
```

Statussen: `nieuw` (standaard als het veld ontbreekt), `gepland`,
`gecontacteerd`, `gereageerd`, `klant`, `geen-vervolg`. `date` en `note`
zijn optioneel en verschijnen klein onderaan de kaart.

Kan een zaak niet gemaild worden? Zet daarnaast `"only_phone": true` in
hetzelfde outreach-blok. Dat is een **kanaal**, geen fase: de kaart houdt
haar gewone status en verschijnt daarnaast onder "Enkel telefonisch". Een
zaak die je opbelde, staat dus tegelijk bij `gecontacteerd` én daar.

Na het aanpassen van een status: `python3 sitegen/build_index.py` draaien,
dan committen en pushen.

## Belangrijke regels

- **Geen reviews of externe teksten woordelijk kopiëren** — auteursrecht.
  Altijd herschrijven in eigen bewoordingen.
- **Elk prototype is één self-contained `index.html`** (inline CSS) —
  geen build-stap, geen dependencies, zodat Cloudflare Pages het direct kan
  serveren.
- **Nooit automatisch mailen** vanuit deze workflow. Het aanmaken/versturen
  van outreach-mails is een aparte, bewust manuele stap (zie project-README).
- Bij twijfel over de juistheid van gegevens (adres, telefoon, uren): meld dit
  expliciet in de commit message of aan de gebruiker, in plaats van te gokken.

## Design-richtlijn

Elk prototype moet een eigen visuele identiteit krijgen passend bij de sector
(bakkerij ≠ kapper ≠ restaurant) — geen kopie van het bakkerij-sjabloon met
enkel andere tekst. Pas kleur, typografie en het "signature element" aan per
sector. Vermijd de generieke AI-look (crème + terracotta, of zwart met neon-
accent) tenzij dat echt bij de zaak past.
