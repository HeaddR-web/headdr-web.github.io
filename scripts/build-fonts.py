#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut die ausgelieferten Schriftdateien aus den Originalen in assets/fonts/src/.

Warum ueberhaupt: `hanken-grotesk.woff2` und `fraunces.woff2` haengen als
Preload in jeder der 42 Seiten und werden damit **vor** dem Hero-Bild geladen -
dem LCP-Element. Jedes Kilobyte dort kostet doppelt.

Was geschrumpft wird und was nicht:

* **Hanken Grotesk: ja.** Die Datei traegt die Achse `wght` 100-900, ausgeliefert
  wird laut `fonts.css` aber nur 400-700. Wird die **untere** Haelfte der Achse
  entfernt (`(400, 400, 900)` - Minimum 400, Default und Maximum unveraendert),
  faellt der komplette negative Delta-Satz weg: 34 704 -> 24 052 Bytes (-31 %).
  Nachgemessen ist das Ergebnis **Pixel fuer Pixel identisch** mit dem Original -
  ein Specimen mit 300/400/500/600/700/800/900 in beiden Schnitten und beiden
  Werten von `font-optical-sizing` ergab 0 abweichende Pixel.

* **Auch oben kuerzen (`(400, 700)`): nein.** Das spart weitere 856 Bytes, aber
  der obere Delta-Satz wird dabei umgerechnet und gerundet. Bei `wght: 600` -
  auf der Seite sieben Mal in `style.css` - wandert die Textbreite um einen
  Pixel, 5 355 Pixel des Specimens weichen ab. 856 Bytes sind das nicht wert.

* **Fraunces: nein, gar nicht.** Der Default der `wght`-Achse liegt bei **900**,
  also ausserhalb der ausgelieferten 400-700. Jede Begrenzung setzt den Default
  neu und rechnet die Umrisse dabei auf ganze Font-Einheiten - zusammen mit der
  zweiten Achse `opsz` (die `font-optical-sizing: auto`, der CSS-Standard,
  tatsaechlich benutzt) aendert das die Darstellung sichtbar: 45 400 abweichende
  Pixel bei `(400, 700)`, 45 400 auch wenn man den Default auf 900 festhaelt,
  48 456 zusaetzlich mit gekuerzter `opsz`. Gewinn waeren 3-8 KB. Dafuer wird
  hier die Schrift nicht veraendert.

Was sonst bewusst bleibt: der `cmap` bleibt vollstaendig (ein weiteres Subset
koennte aus einem Zeichen ein Kaestchen machen), `fraunces-italic.woff2` und
`inter.woff2` bleiben unberuehrt (Inter gehoert zu `cozy/**` und wird auf
BeThatHost nie geladen).

Aufruf:
    python3 scripts/build-fonts.py            # baut neu
    python3 scripts/build-fonts.py --pruefen  # meldet nur, ob aktuell
"""

import io
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELL_DIR = "assets/fonts/src"
ZIEL_DIR = "assets/fonts"

# Dateiname -> Achsen-Grenzen. Dreier-Tupel ist (Minimum, Default, Maximum);
# der Default muss stehen bleiben, sonst werden die Umrisse neu gerundet.
SCHRIFTEN = {
    "hanken-grotesk.woff2": {"wght": (400, 400, 900)},
}


def baue(name, achsen):
    """Liefert die fertigen woff2-Bytes der Ableitung.

    Das Ergebnis muss Byte fuer Byte reproduzierbar sein, sonst kann der
    Konsistenz-Check nicht dagegen pruefen und jeder Lauf erzeugt einen Diff.
    TTFont schreibt beim Speichern aber von sich aus die aktuelle Uhrzeit in
    head.modified, und daran haengen zwei Pruefsummen - drei wandernde Bytes
    pro Lauf. recalcTimestamp=False laesst den Stand des Originals stehen.
    """
    schrift = TTFont(os.path.join(WURZEL, QUELL_DIR, name), recalcTimestamp=False)
    schrift = instantiateVariableFont(schrift, dict(achsen), updateFontNames=False)
    schrift.flavor = "woff2"
    puffer = io.BytesIO()
    schrift.save(puffer)
    return puffer.getvalue()


def main():
    pruefen = "--pruefen" in sys.argv
    offen = []
    for name, achsen in SCHRIFTEN.items():
        quelle = os.path.join(WURZEL, QUELL_DIR, name)
        if not os.path.exists(quelle):
            offen.append(f"Original fehlt: {QUELL_DIR}/{name}")
            continue
        ziel = os.path.join(WURZEL, ZIEL_DIR, name)
        neu = baue(name, achsen)
        alt = open(ziel, "rb").read() if os.path.exists(ziel) else None
        if alt == neu:
            continue
        if pruefen:
            offen.append(
                f"Schrift nicht aktuell: {ZIEL_DIR}/{name} "
                f"- 'python3 scripts/build-fonts.py' laufen lassen"
            )
            continue
        open(ziel, "wb").write(neu)
        vorher = os.path.getsize(quelle)
        print(
            f"{ZIEL_DIR}/{name}: {vorher} -> {len(neu)} Bytes "
            f"(-{round(100 - 100 * len(neu) / vorher)} %)"
        )
    if offen:
        print("\n".join(offen))
        sys.exit(1)
    if pruefen:
        print("Schriftdateien aktuell")


if __name__ == "__main__":
    main()
