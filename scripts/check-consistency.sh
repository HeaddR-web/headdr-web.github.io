#!/usr/bin/env bash
# Guardrail: erzwingt die Design-Konsistenz der BeThatHost-Seiten.
# Läuft in CI (.github/workflows/consistency.yml) UND lokal (vor jedem Push aufrufen).
# Cozylore (cozy/) ist eine eigene Marke und absichtlich ausgenommen.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
note() { echo "  ✗ $1"; fail=1; }

echo "▶ BeThatHost Konsistenz-Check"

# 1) Keine Alt-Fonts (Playfair / family=Inter) außerhalb Cozylore
hits=$(grep -rl --include='*.html' -e 'Playfair' -e 'family=Inter' . | grep -v '^./cozy/' || true)
[ -n "$hits" ] && { note "Alt-Fonts (Playfair/Inter) gefunden in:"; echo "$hits" | sed 's/^/      /'; }

# 2) Nur die zwei erlaubten style.css (zentral + Cozylore)
extra=$(find . -name style.css -not -path './assets/*' -not -path './cozy/*' || true)
[ -n "$extra" ] && { note "Verbotene lokale style.css-Kopien (eine zentrale Quelle nutzen!):"; echo "$extra" | sed 's/^/      /'; }
[ -f assets/style.css ] || note "assets/style.css fehlt (die zentrale Design-Quelle)."

# 3) Abweichende/tote Stylesheet-Pfade außerhalb Cozylore
bad=$(grep -rl --include='*.html' -e 'href="../style.css"' -e 'rel="stylesheet" href="style.css"' -e 'girlsnight/style.css' . | grep -v '^./cozy/' || true)
[ -n "$bad" ] && { note "Abweichende Stylesheet-Pfade (sollen /assets/style.css sein):"; echo "$bad" | sed 's/^/      /'; }

# 4) Keine doppelte zentrale Einbindung pro Datei
while IFS= read -r f; do
  c=$(grep -c '/assets/style.css' "$f")
  [ "$c" -gt 1 ] && note "Doppelte /assets/style.css-Einbindung in $f (${c}×)"
done < <(grep -rl --include='*.html' '/assets/style.css' . | grep -v '^./cozy/' || true)

# 5) Alle BeThatHost-Anlass-/Motto-Unterseiten enden im <title> auf "— BeThatHost"
for d in girlsnight watchparty cocktailabend brunch geburtstag spa-abend valentinstag \
         saison-deko spieleabend grillabend gartenparty mexiko-fiesta jga hawaii-tiki casino oktoberfest; do
  [ -f "$d/index.html" ] || continue
  grep -q '<title>.*— BeThatHost</title>' "$d/index.html" || note "$d/index.html: <title> nicht in Form '… — BeThatHost'"
done

# 6) DSGVO: keine direkte Google-Fonts-CDN-Einbindung mehr (self-hosted, siehe assets/fonts/)
hits=$(grep -rl --include='*.html' -e 'fonts\.googleapis\.com' -e 'fonts\.gstatic\.com' . || true)
[ -n "$hits" ] && { note "Google-Fonts-CDN direkt eingebunden (self-hosted /assets/fonts/fonts.css nutzen):"; echo "$hits" | sed 's/^/      /'; }

# 7) DSGVO: AdSense/Pinterest duerfen nur ueber consent.js nachgeladen werden, nie direkt im Markup
hits=$(grep -rl --include='*.html' -e 'src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js' -e 'src="https://assets\.pinterest\.com/js/pinit\.js' . || true)
[ -n "$hits" ] && { note "AdSense/Pinterest direkt (ohne Consent-Gate) eingebunden in:"; echo "$hits" | sed 's/^/      /'; }

# 8) Einkaufslisten-Block oben auf den Anlass-Seiten stimmt mit den .pick-Karten ueberein.
#    Der Block wird generiert (scripts/build-quickbuy.py); kommt unten ein Pick dazu oder
#    aendert sich eine ASIN, muss er neu gebaut werden, sonst zeigt die Liste oben ins Leere.
if ! command -v python3 >/dev/null 2>&1; then
  # Bewusst ein Fehler, kein stilles Ueberspringen: ein Guard, der sich ohne
  # Hinweis selbst abschaltet, taeuscht eine Pruefung vor, die nie lief.
  note "python3 fehlt — Punkte 8 und 9 konnten nicht geprueft werden"
else
  if out=$(python3 scripts/build-quickbuy.py --check 2>&1); then
    echo "  ✓ Einkaufslisten stimmen mit den Pick-Karten ueberein"
  else
    note "Einkaufsliste nicht aktuell:"; echo "$out" | sed 's/^/      /'
  fi

# 9) Jeder Affiliate-Link traegt die fuer seinen Ordner vorgesehene Tracking-ID
#    (scripts/tracking-ids.json), und jeder rel="sponsored"-Link hat ueberhaupt eins.
#    Ein Link mit falschem oder fehlendem tag= bringt keine Provision.
  if out=$(python3 scripts/set-tracking-ids.py --check 2>&1); then
    echo "  ✓ Alle Affiliate-Links tragen die vorgesehene Tracking-ID"
  else
    note "Affiliate-Tracking-IDs stimmen nicht:"; echo "$out" | sed 's/^/      /'
  fi

# 10) Meta-Descriptions in SERP-Laenge. Google schneidet deutsche Snippets bei rund
#     155-160 Zeichen ab; was dahinter steht, sieht in der Suche niemand.
  if out=$(python3 scripts/check-meta.py 2>&1); then
    echo "  ✓ Alle Meta-Descriptions passen in das Suchergebnis"
  else
    note "Meta-Descriptions ausserhalb der SERP-Laenge:"; echo "$out" | sed 's/^/      /'
  fi

# 11) Jede Pick-Karte hat Ueberschrift, Beschreibung und Kauf-Button, und keine
#     zwei Karten einer Seite zeigen auf dieselbe ASIN. Eine Karte ohne Text ist
#     ein Kauf-Button ohne Kaufargument; eine doppelte ASIN schickt den Leser
#     garantiert auf das falsche Produkt.
  if out=$(python3 scripts/check-picks.py 2>&1); then
    echo "  ✓ Alle Pick-Karten sind vollstaendig"
  else
    note "Pick-Karten unvollstaendig:"; echo "$out" | sed 's/^/      /'
  fi

# 12) Jede Inhaltsseite hat genau einen Werbeplatz, und der ist im Quelltext leer.
#     Fehlt er, kann AdSense auf der Seite nichts ausliefern; steht Text darin,
#     sieht jeder Besucher dauerhaft einen Kasten mit einer Baustellen-Notiz.
  if out=$(python3 scripts/check-ads.py 2>&1); then
    echo "  ✓ Werbeplaetze sitzen auf allen Inhaltsseiten"
  else
    note "Werbeplaetze stimmen nicht:"; echo "$out" | sed 's/^/      /'
  fi

# 13) Das Inhaltsverzeichnis passt zu den Ueberschriften und steht unter der
#     Einkaufsliste. Stimmt es nicht, schickt es den Leser auf Abschnitte, die
#     es nicht mehr gibt; steht es zu weit oben, verdraengt es den Kaufweg.
  if out=$(python3 scripts/check-toc.py 2>&1); then
    echo "  ✓ Inhaltsverzeichnisse sind aktuell"
  else
    note "Inhaltsverzeichnisse stimmen nicht:"; echo "$out" | sed 's/^/      /'
  fi

# 14) Jede Seite ist aus dem Artikeltext heraus erreichbar und verlinkt weiter.
#     Eine Seite ohne eingehenden Link findet nur, wer ueber die Startseite
#     kommt; eine ohne ausgehenden endet fuer den Leser im Zurueck-Button.
  if out=$(python3 scripts/check-related.py 2>&1); then
    echo "  ✓ Weiterlesen-Blocks sind aktuell, keine Waisen"
  else
    note "Interne Verlinkung stimmt nicht:"; echo "$out" | sed 's/^/      /'
  fi

# 15) Jede ausgezeichnete FAQ steht auch sichtbar auf der Seite. Googles
#     Richtlinie fuer strukturierte Daten verlangt das; und wer die Frage im
#     Suchergebnis anklickt, soll die Antwort auch vorfinden.
  if out=$(python3 scripts/check-faq.py 2>&1); then
    echo "  ✓ FAQs stehen sichtbar auf der Seite"
  else
    note "FAQ-Auszeichnung ohne sichtbaren Inhalt:"; echo "$out" | sed 's/^/      /'
  fi
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "✓ Konsistenz-Check bestanden."
else
  echo "✗ Konsistenz-Check FEHLGESCHLAGEN — bitte oben gelistete Punkte beheben."
fi
exit $fail
