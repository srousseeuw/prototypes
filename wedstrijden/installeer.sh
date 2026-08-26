#!/usr/bin/env bash
# Zet de wedstrijdbot in één keer op: config invullen, testen en in cron zetten.
#   ./wedstrijden/installeer.sh
# Alles wat je invult komt in config.json (blijft buiten git). Het app-wachtwoord
# komt in .env, met rechten 600, en wordt door nacht.sh ingelezen.
set -uo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HIER"

command -v python3 >/dev/null || { echo "python3 niet gevonden."; exit 1; }

echo "Wedstrijdbot instellen"
echo "──────────────────────"
echo

[ -f config.json ] || { cp config.example.json config.json; echo "config.json aangemaakt vanuit het voorbeeld."; echo; }

huidig() { python3 -c "
import json,sys
c=json.load(open('config.json'))
for deel in sys.argv[1].split('.'): c=c.get(deel,'') if isinstance(c,dict) else ''
print(c if c not in (None,False) else '')" "$1"; }

vraag() {  # vraag <pad.in.config> <omschrijving>
  local pad="$1" tekst="$2" nu antwoord
  nu="$(huidig "$pad")"
  if [ -n "$nu" ]; then
    read -r -p "$tekst [$nu]: " antwoord
    echo "${antwoord:-$nu}"
  else
    read -r -p "$tekst: " antwoord
    echo "$antwoord"
  fi
}

jaNee() {  # jaNee <vraag> <standaard j|n>
  local antwoord standaard="$2"
  read -r -p "$1 [$([ "$standaard" = j ] && echo "J/n" || echo "j/N")]: " antwoord
  antwoord="${antwoord:-$standaard}"
  case "$antwoord" in [jJyY]*) return 0 ;; *) return 1 ;; esac
}

echo "1. Wie neemt deel?"
VOORNAAM="$(vraag deelnemer.voornaam '   Voornaam')"
ACHTERNAAM="$(vraag deelnemer.achternaam '   Achternaam')"
EMAIL="$(vraag deelnemer.email '   E-mailadres (een +wedstrijden-alias houdt je mailbox proper)')"
TELEFOON="$(vraag deelnemer.telefoon '   Telefoon')"
STRAAT="$(vraag deelnemer.straat '   Straat')"
HUISNUMMER="$(vraag deelnemer.huisnummer '   Huisnummer')"
POSTCODE="$(vraag deelnemer.postcode '   Postcode')"
GEMEENTE="$(vraag deelnemer.gemeente '   Gemeente')"
GEBOORTE="$(vraag deelnemer.geboortedatum '   Geboortedatum (JJJJ-MM-DD)')"
echo

echo "2. Hoe voorzichtig?"
if jaNee "   Echt deelnemen (nee = proefdraai: alles doen behalve versturen)" n; then
  DRYRUN=false; echo "   → er wordt echt ingezonden."
else
  DRYRUN=true;  echo "   → proefdraai; de digest toont wat hij zou versturen."
fi
if jaNee "   Ook formulieren zonder recept zelf proberen in te vullen" j; then
  RAADMEE=false   # alleen_met_recept
else
  RAADMEE=true
fi
if jaNee "   Nieuwsbrieven aanvinken waar dat gevraagd wordt" n; then
  NIEUWSBRIEF=true
else
  NIEUWSBRIEF=false
fi
MAXNACHT="$(vraag deelname.max_per_nacht '   Hoeveel deelnames per nacht maximaal')"
echo

echo "3. Mail (optioneel — vraagt een Google app-wachtwoord)"
echo "   Nodig om bevestigingsmails aan te klikken en de digest op te sturen."
if jaNee "   Nu instellen" n; then
  read -r -s -p "   App-wachtwoord (blijft onzichtbaar): " APPWW; echo
  if [ -n "$APPWW" ]; then
    printf "export GMAIL_APP_WACHTWOORD='%s'\n" "$APPWW" > .env
    chmod 600 .env
    MAILEN=true
    echo "   → bewaard in .env (rechten 600, buiten git)."
  else
    MAILEN=false; echo "   → niets ingevuld, mail blijft uit."
  fi
else
  MAILEN=false
fi
echo

python3 - "$VOORNAAM" "$ACHTERNAAM" "$EMAIL" "$TELEFOON" "$STRAAT" "$HUISNUMMER" \
          "$POSTCODE" "$GEMEENTE" "$GEBOORTE" "$DRYRUN" "$RAADMEE" "$NIEUWSBRIEF" \
          "$MAXNACHT" "$MAILEN" <<'PY'
import json, sys
from pathlib import Path

(vn, an, em, tel, st, hn, pc, gem, geb, dry, recept, nieuwsbrief, maxn, mailen) = sys.argv[1:15]
pad = Path("config.json")
c = json.loads(pad.read_text(encoding="utf-8"))

c["deelnemer"].update({
    "voornaam": vn, "achternaam": an, "email": em, "telefoon": tel, "straat": st,
    "huisnummer": hn, "postcode": pc, "gemeente": gem, "geboortedatum": geb,
    "nieuwsbrief_toestaan": nieuwsbrief == "true",
})
c["deelname"].update({
    "dry_run": dry == "true",
    "alleen_met_recept": recept == "true",
    "max_per_nacht": int(maxn) if str(maxn).isdigit() else c["deelname"].get("max_per_nacht", 8),
})
c["bevestiging"]["actief"] = mailen == "true"
c["bevestiging"]["gebruiker"] = em
c["digest"]["mailen"] = mailen == "true"
c["digest"]["smtp_gebruiker"] = em
c["digest"]["naar"] = em
c.pop("_uitleg", None)

pad.write_text(json.dumps(c, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
ontbreekt = [k for k in ("telefoon", "straat", "huisnummer", "postcode") if not c["deelnemer"].get(k)]
print("✓ config.json bijgewerkt." + (f"  Let op: {', '.join(ontbreekt)} nog leeg — "
      "formulieren die dat verplicht vragen gaan naar 'zelf afwerken'." if ontbreekt else ""))
PY
echo

echo "4. Bronnen testen"
python3 wedstrijden.py bronnen-check | sed 's/^/   /'
echo

echo "5. Eerste ronde draaien"
if jaNee "   Nu meteen een ronde doen" j; then
  [ -f .env ] && . ./.env
  python3 wedstrijden.py nacht | sed 's/^/   /'
fi
echo

echo "6. Elke nacht laten draaien"
if ! command -v crontab >/dev/null; then
  echo "   crontab niet gevonden — zet zelf een taak klaar die dit draait:"
  echo "   $HIER/nacht.sh"
else
  read -r -p "   Om hoe laat? (uu:mm) [03:15]: " TIJD
  TIJD="${TIJD:-03:15}"
  UUR="${TIJD%%:*}"; MIN="${TIJD#*:}"
  REGEL="${MIN#0} ${UUR#0} * * * $HIER/nacht.sh"
  if crontab -l 2>/dev/null | grep -qF "$HIER/nacht.sh"; then
    echo "   Stond er al in — laat ik ongemoeid:"
    crontab -l 2>/dev/null | grep -F "$HIER/nacht.sh" | sed 's/^/     /'
  elif jaNee "   In cron zetten ($REGEL)" j; then
    { crontab -l 2>/dev/null; echo "$REGEL"; } | crontab -
    echo "   ✓ in cron gezet."
    echo "   Slaapt je Mac op dat uur, kies dan een moment waarop hij aanstaat."
  fi
fi

echo
echo "Klaar. Digest na elke ronde: $HIER/data/digest.html"
echo "Handmatig draaien: python3 $HIER/wedstrijden.py nacht"
