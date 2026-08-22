# Wedstrijdbot als Cloudflare Worker

Zelfde bot als `wedstrijden/`, maar draaiend in de cloud in plaats van op de
Mac: elke nacht om 03:15 zoekt hij de overzichtssites af, kiest wat nuttig is
voor het gezin, en schrijft in. Geen Mac nodig die aanstaat.

Lees eerst de waarschuwing in [`../wedstrijden/README.md`](../wedstrijden/README.md):
automatisch deelnemen botst met de regels van veel wedstrijden, en je geeft per
deelname je gegevens aan een onbekende partij. Daarom staat ook deze versie
standaard op proefdraai.

## Wat hij doet

| Trigger | Wat er gebeurt |
|---|---|
| **cron** (03:15) | bronnen ophalen → scoren → inschrijven → digest in KV → optioneel mailen |
| **fetch** | op een geheim pad: het volledige overzicht van alles waar je aan deelnam, plus de laatste ronde; al de rest krijgt 404 |
| **email** | bevestigingsmails ("klik om je deelname te bevestigen") aanklikken en de rest doorsturen naar je gewone mailbox |

De eerste nacht staat er nog niets in KV. Dan doet hij een **inhaalbeweging**:
alles wat op dat moment online staat is nieuw, en het plafond gaat van 10 naar
30 deelnames (`maxEersteNacht` in `src/config.js`).

## Opzetten

```bash
cd worker
npm run lijsten                              # woordenlijsten uit selectie.json
npx wrangler login
npx wrangler kv namespace create WEDSTRIJDEN # zet het id in wrangler.toml
```

Dan je gegevens als secrets — die staan nooit in git:

```bash
npx wrangler secret put DEELNEMER
```

Plak als waarde één regel JSON:

```json
{"voornaam":"Sebastiaan","achternaam":"Rousseeuw","email":"sebastiaan.rousseeuw+wedstrijden@gmail.com","telefoon":"04...","straat":"...","huisnummer":"...","postcode":"2910","gemeente":"Essen","land":"België","geboortedatum":"1980-01-01","nieuwsbriefToestaan":false}
```

En het geheime pad waarop je de digest kan lezen:

```bash
npx wrangler secret put DIGEST_PAD      # bv. een willekeurige reeks als "d7f3a91b"
npx wrangler deploy
```

Die pagina is meteen ook je logboek: bovenaan staat alles waaraan je ooit
deelnam (nieuwste eerst, met datum, status en link), daaronder wat er de
laatste nacht gebeurde. Te bekijken op
`https://wedstrijdbot.<jouw-subdomein>.workers.dev/<DIGEST_PAD>` — zet die
in je favorieten.

### Eerst proefdraaien

Je hoeft niet tot 03:15 te wachten: surf naar `<worker-url>/<DIGEST_PAD>/nu`
en hij draait meteen een ronde, met de instelling die op dat moment geldt
(dus proefdraai zolang `DRY_RUN = "true"`). Na een halve minuut springt de
pagina naar het overzicht.

Lokaal kan ook, zonder te deployen:

```bash
npx wrangler dev --test-scheduled
curl "http://localhost:8787/__scheduled"
```

Kijk de digest na. Ziet het er goed uit, zet dan `DRY_RUN = "false"` in
`wrangler.toml` en `npx wrangler deploy`. Vanaf dan wordt er echt ingeschreven.

### Bevestigingsmails (aanrader)

Veel wedstrijden tellen je deelname pas mee na een klik in een bevestigingsmail.
Laat die mails bij de Worker toekomen via Cloudflare Email Routing:

1. Cloudflare → je domein `ocior.be` → **Email** → **Email Routing** aanzetten.
2. Bij **Destination addresses**: je Gmail toevoegen en bevestigen.
3. Bij **Routes**: adres `wedstrijden@ocior.be` → **Send to a Worker** →
   `wedstrijdbot`.
4. `npx wrangler secret put DIGEST_NAAR` → je Gmail (daar gaat alles heen wat
   geen bevestigingsmail is, bijvoorbeeld een prijsmelding).
5. Zet datzelfde adres in `DEELNEMER.email`, zodat de wedstrijden er ook
   naartoe schrijven.

De Worker klikt alleen bevestigingslinks aan van domeinen waar hij zelf heeft
ingeschreven — een willekeurige "bevestig hier"-knop in andere post blijft
onaangeroerd.

### Digest mailen (optioneel)

Zonder dit staat de digest gewoon op je geheime pad. Wil je hem in je mailbox:

```bash
npx wrangler secret put RESEND_API_KEY   # resend.com, gratis tier
npx wrangler secret put DIGEST_VAN       # bv. wedstrijden@ocior.be (geverifieerd domein)
npx wrangler secret put DIGEST_NAAR      # je Gmail
```

Is er niets gebeurd, dan volgt er geen mail — een lege mail per nacht is erger
dan geen mail.

## Bijstellen

* **Andere interesses** → `../wedstrijden/selectie.json`, daarna
  `npm run lijsten && npx wrangler deploy`. Python en Worker delen die lijst.
* **Andere sites, of meer/minder per nacht** → `src/config.js`.
* **Uur** → `crons` in `wrangler.toml` (staat in UTC, dus `15 1 * * *` is 03:15
  Belgische zomertijd).

## Testen zonder Cloudflare

`test/lokaal.mjs` draait de volledige ronde onder gewone node, met een nep-KV
en een lokale testsite. Handig om de selectie of het invullen aan te passen
zonder iets te deployen:

```bash
node test/lokaal.mjs http://127.0.0.1:8765/
```

## Grenzen

* **Geen browser.** Een Worker kan geen JavaScript-formulier bedienen en geen
  captcha oplossen. Die wedstrijden komen op de digest onder "zelf afwerken".
  Wil je ze tóch automatisch, dan is de Mac-versie met Playwright de plek.
* **Nederlandse wedstrijden** staan in de bronnenlijst, maar leveren vaak enkel
  binnen Nederland of vragen een NL-postcode. De bot vult je Belgische adres in;
  reken erop dat een deel daarvan afgekeurd wordt.
* **Datacenter-IP.** Sommige sites weigeren of vertragen inzendingen die niet van
  een gewone thuisverbinding komen. Blijft een bron structureel mislukken, dan
  zie je dat in de digest.
* De bot meldt geen prijzen. Win je iets, dan komt die mail gewoon in je mailbox
  (via Email Routing doorgestuurd naar Gmail).
