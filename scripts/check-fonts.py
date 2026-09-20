#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die ausgelieferten Schriftdateien gegen die Originale.

Zwei Fehler:
  * Eine ausgelieferte Datei passt nicht mehr zu ihrem Original in
    assets/fonts/src/. Dann liegt im Repo eine Schrift, die kein Skript mehr
    erzeugen kann - beim naechsten Lauf von build-fonts.py aendert sie sich
    kommentarlos, und niemand weiss mehr, welcher Stand der richtige war.
  * Eine Seite oder ein Stylesheet verweist auf eine woff2, die es nicht gibt,
    oder umgekehrt liegt in assets/fonts/ eine woff2, auf die nichts mehr
    zeigt. Beides faellt sonst nicht auf: die fehlende erst beim Besucher
    (Ersatzschrift, Sprung im Layout), die ueberfluessige nie.

Beheben mit: python3 scripts/build-fonts.py
"""

import os
import re
import subprocess
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = "assets/fonts"
# cozy/** ist abgekoppelt und bringt eigene Schriften mit - hier nicht pruefen.
AUS = ("cozy", ".git", "node_modules")

WOFF_RE = re.compile(r"/assets/fonts/([A-Za-z0-9._-]+\.woff2)")


def seiten():
    for pfad, ordner, dateien in os.walk(WURZEL):
        ordner[:] = [o for o in ordner if o not in AUS]
        for d in dateien:
            if d.endswith((".html", ".css")):
                yield os.path.join(pfad, d)


def main():
    fehler = []

    # 1) Ableitungen aktuell?
    lauf = subprocess.run(
        [sys.executable, os.path.join(WURZEL, "scripts", "build-fonts.py"), "--pruefen"],
        capture_output=True,
        text=True,
    )
    if lauf.returncode != 0:
        fehler.append(lauf.stdout.strip() or lauf.stderr.strip())

    # 2) Verlinkt und vorhanden decken sich?
    verlinkt = set()
    for datei in seiten():
        with open(datei, encoding="utf-8", errors="ignore") as fh:
            verlinkt.update(WOFF_RE.findall(fh.read()))

    vorhanden = {
        d for d in os.listdir(os.path.join(WURZEL, FONT_DIR)) if d.endswith(".woff2")
    }
    for name in sorted(verlinkt - vorhanden):
        fehler.append(f"Schrift fehlt auf der Platte: {FONT_DIR}/{name}")
    for name in sorted(vorhanden - verlinkt):
        fehler.append(f"Schrift verwaist (keine Seite bindet sie ein): {FONT_DIR}/{name}")

    if fehler:
        print("\n".join(fehler))
        sys.exit(1)
    print("Schriftdateien aktuell und vollstaendig verlinkt")


if __name__ == "__main__":
    main()
