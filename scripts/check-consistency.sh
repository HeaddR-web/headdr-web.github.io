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

echo
if [ "$fail" -eq 0 ]; then
  echo "✓ Konsistenz-Check bestanden."
else
  echo "✗ Konsistenz-Check FEHLGESCHLAGEN — bitte oben gelistete Punkte beheben."
fi
exit $fail
