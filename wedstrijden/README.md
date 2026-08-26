# Wedstrijdbot

Zoekt elke nacht gratis wedstrijden die nuttig kunnen zijn voor het gezin,
neemt deel waar dat kan, en zet 's ochtends één overzichtje klaar met wat er
gebeurd is en wat jij nog zelf moet doen.

Alles is stdlib-Python, net als de rest van deze repo: geen dependencies, geen
build-stap. Enkel de optionele browser-modus vraagt `playwright`.

## Lees dit eerst

Automatisch deelnemen botst met de regels van veel wedstrijden. Bijna elk
reglement zegt "één deelname per persoon" (dat bewaakt het script), maar
sommige verbieden expliciet geautomatiseerde inzendingen, en een winst kan
ongeldig verklaard worden als blijkt dat een script deelnam. Daarnaast geef je
per deelname je naam, e-mail en soms adres aan een onbekende partij — reken op
meer reclame in je mailbox.

Daarom staat het script standaard **op proefdraai** (`dry_run: true`): het
zoekt, filtert, leest het formulier en toont wat het zou versturen, zonder iets
te versturen. Kijk een week mee, en zet het pas dan echt aan. Een aparte
mailbox of een `+wedstrijden`-alias (`sebastiaan.rousseeuw+wedstrijden@gmail.com`)
houdt de gewone mail proper — de meeste sites accepteren dat gewoon.

## In gang zetten

Eén commando, op de Mac waar het script moet draaien:

```bash
./wedstrijden/installeer.sh
```

Dat vraagt je gegevens (naam, adres, telefoon, geboortedatum), of hij echt mag
inzenden of eerst wil proefdraaien, of hij formulieren zonder recept zelf mag
proberen, en hoeveel deelnames per nacht maximaal. Daarna test hij de bronnen,
draait één ronde, en zet zichzelf in cron. Alles wat je invult komt in
`config.json`; een app-wachtwoord komt in `.env` met rechten 600. Beide blijven
buiten git.

Opnieuw draaien mag altijd — hij toont je huidige antwoorden tussen `[ ]` en
zet zichzelf geen tweede keer in cron.

### Of met de hand

```bash
cd wedstrijden
cp config.example.json config.json
$EDITOR config.json
python3 wedstrijden.py bronnen-check    # doen de bronnen het?
python3 wedstrijden.py zoek --alles     # wat vindt hij, en met welke score?
```

En in `crontab -e`:

```
15 3 * * * /Users/seb/Documents/GitHub/prototypes/wedstrijden/nacht.sh
```

`nacht.sh` leest `.env` in, draait `wedstrijden.py nacht` en logt naar
`data/nacht.log`. Cron kent je shell-omgeving niet, dus wachtwoorden horen
daar in `.env` te staan en niet in je `.zshrc`. Slaapt de Mac om 3u, kies dan
een uur waarop hij aanstaat; op macOS heeft cron soms "Volledige schijftoegang"
nodig (Systeeminstellingen → Privacy).

### Eerst kijken, dan pas versturen

`bronnen-check` is niet optioneel: de overzichtssites in `config.example.json`
zijn echte Belgische wedstrijdsites, maar of ze een bruikbare feed hebben kon
ik niet testen (de omgeving waarin dit geschreven is, mag niet naar buiten).
Wat niets oplevert: URL aanpassen of `"actief": false` zetten.

Kies je bij de installatie voor proefdraai, dan doet het script alles behalve
versturen en zie je in de digest wat het zou ingediend hebben. Omschakelen kan
later door `installeer.sh` opnieuw te draaien, of met
`"dry_run": false` in `config.json`.

## Wat er 's nachts gebeurt

1. **Zoeken** — elke bron uit `config.json` wordt opgehaald. Eerst wordt een
   RSS/Atom-feed gezocht (uit de `<head>`, of via `/feed/`, `/rss`, …); lukt dat
   niet, dan worden de links met een deftige titel van de overzichtspagina
   geplukt. `robots.txt` wordt gerespecteerd.
2. **Selecteren** — elk item krijgt een score uit `config.selectie`: punten per
   categorie (boodschappen +5, kinderen +4, uitstap +4, huishouden +3, …), een
   bonus voor "gratis", en een dikke min voor gokken, tabak, sms-spelletjes en
   NL-only acties. Alles onder `min_score` valt af.
3. **Deelnemen** — het formulier wordt gelezen en ingevuld. Voorwaarden-vinkjes
   gaan aan, nieuwsbrief-vinkjes alleen als `nieuwsbrief_toestaan: true`.
   Captcha, login of een verplicht veld dat het script niet begrijpt → geen
   gok, maar door naar "zelf afwerken".
4. **Bevestigen** — optioneel: bevestigingsmails ("klik hier om je deelname te
   bevestigen") worden via IMAP opgezocht en aangeklikt. Staat standaard uit.
5. **Digest** — `data/digest.html`, met bovenaan wat jij nog moet doen.
   Mailen naar jezelf kan, maar staat standaard uit.

## Commando's

| Commando | Wat het doet |
|---|---|
| `nacht` | de volledige ronde (dit draait cron) |
| `zoek` | enkel zoeken en tonen, verstuurt nooit iets |
| `zoek --alles` | ook de afgewezen items, met score en reden — om de filter te ijken |
| `deelnemen` | deelnemen aan wat al gevonden is |
| `bevestig` | bevestigingsmails aanklikken |
| `digest` | digest opnieuw opbouwen uit de log |
| `bronnen-check` | test elke bron, verstuurt niets |

`--echt` zet proefdraai uit voor één run, `--proef` zet hem aan.

## Bijstellen

**Andere interesses?** Pas `selectie.categorieen` aan in `config.json` — woorden
en gewichten. Matching gebeurt op woordbegin, dus `gezin` vangt ook
"gezinsticket" en `plopsa` ook "Plopsaland". Zit er rommel tussen, draai dan
`zoek --alles`: je ziet per item welke woorden aansloegen.

**Te weinig deelnames?** Standaard doet het script enkel mee op sites waarvoor
een recept bestaat (`deelname.alleen_met_recept: true`). Zet dat op `false` en
het probeert elk formulier zelf te lezen — dat werkt verrassend vaak, maar kijk
de eerste nachten de proefdraai na.

**Een site die vaak terugkomt?** Schrijf er een recept voor:
`recepten/<domein>.json`, zie `recepten/_voorbeeld.json`. Daarin leg je per
veld vast wat er in moet (`{{voornaam}}`, `{{email}}`, …), en voor
JavaScript-formulieren kan je met `"modus": "playwright"` een echte browser
laten klikken (`pip install playwright && playwright install chromium`).

## Wachtwoorden

Bevestigingsmails lezen en de digest mailen vraagt een **app-wachtwoord** van
Google (niet je gewone wachtwoord; via je Google-account → Beveiliging →
App-wachtwoorden, met 2FA aan). `installeer.sh` vraagt ernaar en zet het in
`.env`:

```
export GMAIL_APP_WACHTWOORD='xxxx xxxx xxxx xxxx'
```

`nacht.sh` leest dat bestand in. Het staat in `.gitignore` en heeft rechten 600.

## Wat er niet in git komt

`config.json` (adres, telefoon), `.env` (app-wachtwoord) en heel `data/` (wat we gezien hebben, waaraan
we deelnamen, de digest). Alleen de code en het voorbeeldbestand worden
gedeeld.

## Grenzen

* Wedstrijden met een captcha, een quizvraag of een verplichte upload kan het
  script niet doen — die komen in de digest te staan.
* Facebook- en Instagram-acties ("liken en delen") zitten er niet in.
* Of een wedstrijd openstaat voor België wordt enkel uit de tekst afgeleid;
  een NL-only actie kan er dus doorglippen.
* Wint er iets? Dan komt die mail gewoon in je gewone mailbox — het script
  leest wel bevestigingslinks, maar meldt geen prijzen.
