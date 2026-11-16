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

* **Bricolage Grotesque: feste Instanz plus Zeichen-Subset.** Nur im Shop, als
  Schrift fuer Ueberschriften und fuer die Namen in den Produktkarten
  (`--shop-display` in `style.css`). Ausgeliefert wird nur ExtraBold, also wird
  die variable Datei auf wght 800, opsz 96, wdth 100 festgesetzt. Das sind alle
  drei die Defaults des Originals, es wird also nichts neu gerundet. Danach
  bleiben nur die Zeichen aus BRICOLAGE_ZEICHEN: 408 496 -> 20 984 Bytes.
  Herkunft: github.com/google/fonts, Datei
  `ofl/bricolagegrotesque/BricolageGrotesque[opsz,wdth,wght].ttf`, Version
  1.001, SHA-256 413e7357809ddd12fd80a96a8a396de0e401638d4acd3cb3e37532f0472ac682,
  geholt am 16.11.2026. Lizenz OFL 1.1 ohne reservierten Namen, der Text liegt
  daneben als `bricolage-grotesque-OFL.txt` und steht als Name-ID 13 auch in
  der ausgelieferten Datei.
  Warum Latin Extended-A? Kunden tippen ihre Namen in die Probefelder, und
  Namen wie Lukasz mit L-Strich (U+0141), Seyma mit S-Cedille (U+015E) oder
  Zeljko mit Z-Hatschek (U+017D) kommen vor. Bis 16.11.2026 fehlten der Datei
  34 solche Buchstaben, der Browser setzte jeden davon einzeln aus Arial
  Narrow Bold (per CSS.getPlatformFontsForNode nachgemessen). Mitten im
  Namen stand dann ein Buchstabe aus einer fremden, schmaleren Schrift.
  Warum ist hier ein Subset erlaubt, anders als unten bei Hanken? Bricolage
  steht im Stapel vor "Arial Narrow", sans-serif. Ein Zeichen ausserhalb des
  Subsets faellt einzeln auf die naechste Schrift im Stapel, nicht auf ein
  Kaestchen. So bleibt es fuer 25 Buchstaben aus Latin Extended-A, die auch
  das Original nicht hat (u.a. U+0108, U+0162, U+017F).
  Gegenprobe beim Umbau. Die 205 Zeichen der vorher ausgelieferten Datei haben
  in der neuen dieselben Umrisse und dieselben Vorschubbreiten (zerlegte
  Konturen verglichen, 0 Abweichungen), und im Browser laufen alle 42 436
  Zeichenpaare (206 mal 206) gleich breit wie vorher, das Kerning ist also
  unveraendert.
  Layout-Features nur `kern` und `locl`
  wie bisher, `case`, `frac`, `tnum` und Co. benutzt keine Seite.

Was sonst bewusst bleibt: der `cmap` von Hanken bleibt vollstaendig (Hanken ist
die Fliesstextschrift, ein Subset koennte dort aus einem Zeichen ein Kaestchen
machen), `fraunces-italic.woff2` und `inter.woff2` bleiben unberuehrt (Inter
gehoert zu `cozy/**` und wird auf BeThatHost nie geladen).

Aufruf:
    python3 scripts/build-fonts.py            # baut neu
    python3 scripts/build-fonts.py --pruefen  # meldet nur, ob aktuell
"""

import io
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELL_DIR = "assets/fonts/src"
ZIEL_DIR = "assets/fonts"

# Zeichen der Bricolage-Ableitung als feste Bereiche (erster, letzter Codepunkt).
# Absichtlich hingeschrieben und nicht aus der alten Datei abgeleitet: was hier
# fehlt, setzt der Browser aus der Ersatzschrift.
BRICOLAGE_ZEICHEN = (
    (0x0020, 0x007E),  # Basic Latin
    (0x00A0, 0x00FF),  # Latin-1 (U+00A4 und U+00AD hat das Original nicht)
    (0x0100, 0x017F),  # Latin Extended-A, seit 16.11.2026
    (0x0218, 0x021B),  # S und T mit Komma darunter (rumaenisch), seit 16.11.2026
    (0x2013, 0x2014),  # Halbgeviert- und Geviertstrich
    (0x2018, 0x201A),  # einfache Anfuehrungszeichen
    (0x201C, 0x201E),  # doppelte Anfuehrungszeichen
    (0x2022, 0x2022),  # Aufzaehlungspunkt
    (0x2026, 0x2026),  # Auslassungspunkte
    (0x2032, 0x2033),  # Minuten- und Sekundenzeichen
    (0x2039, 0x203A),  # einfache Guillemets
    (0x20AC, 0x20AC),  # Euro
    (0x2212, 0x2212),  # Minus
)

# Ausgelieferte Datei -> Bauplan.
#   achsen:   Achsen-Grenzen. Dreier-Tupel ist (Minimum, Default, Maximum), eine
#             einzelne Zahl setzt die Achse fest. Der Default muss stehen
#             bleiben, sonst werden die Umrisse neu gerundet.
#   quelle:   Original in assets/fonts/src/, ohne Angabe gleicher Name.
#   zeichen:  optional, Bereiche fuer ein Subset. Ohne Angabe bleibt der cmap
#             vollstaendig.
#   features, name_ids: nur mit zeichen, was das Subset behaelt.
SCHRIFTEN = {
    "hanken-grotesk.woff2": {"achsen": {"wght": (400, 400, 900)}},
    "bricolage-grotesque-800.woff2": {
        "quelle": "bricolage-grotesque.ttf",
        "achsen": {"wght": 800, "opsz": 96, "wdth": 100},
        "zeichen": BRICOLAGE_ZEICHEN,
        "features": ["kern", "locl"],
        # 13 ist der Lizenztext (OFL), den die Lizenz beim Weitergeben verlangt.
        "name_ids": [0, 1, 2, 3, 4, 5, 6, 13, 14],
    },
}


def baue(name, plan):
    """Liefert die fertigen woff2-Bytes der Ableitung.

    Das Ergebnis muss Byte fuer Byte reproduzierbar sein, sonst kann der
    Konsistenz-Check nicht dagegen pruefen und jeder Lauf erzeugt einen Diff.
    TTFont schreibt beim Speichern aber von sich aus die aktuelle Uhrzeit in
    head.modified, und daran haengen zwei Pruefsummen - drei wandernde Bytes
    pro Lauf. recalcTimestamp=False laesst den Stand des Originals stehen.
    """
    quelle = os.path.join(WURZEL, QUELL_DIR, plan.get("quelle", name))
    schrift = TTFont(quelle, recalcTimestamp=False)
    schrift = instantiateVariableFont(schrift, dict(plan["achsen"]), updateFontNames=False)
    if "zeichen" in plan:
        optionen = subset.Options()
        optionen.layout_features = list(plan["features"])
        optionen.name_IDs = list(plan["name_ids"])
        teiler = subset.Subsetter(optionen)
        teiler.populate(
            unicodes=[c for erster, letzter in plan["zeichen"] for c in range(erster, letzter + 1)]
        )
        teiler.subset(schrift)
    schrift.flavor = "woff2"
    puffer = io.BytesIO()
    schrift.save(puffer)
    return puffer.getvalue()


def main():
    pruefen = "--pruefen" in sys.argv
    offen = []
    for name, plan in SCHRIFTEN.items():
        quellname = plan.get("quelle", name)
        quelle = os.path.join(WURZEL, QUELL_DIR, quellname)
        if not os.path.exists(quelle):
            offen.append(f"Original fehlt: {QUELL_DIR}/{quellname}")
            continue
        ziel = os.path.join(WURZEL, ZIEL_DIR, name)
        neu = baue(name, plan)
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
