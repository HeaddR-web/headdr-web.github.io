#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Meta-Descriptions aller BeThatHost-Seiten auf SERP-Laenge.

Google schneidet deutsche Snippets bei rund 155-160 Zeichen ab. Laengere
Beschreibungen sind nicht kaputt, aber der Teil hinter dem Schnitt ist
verschenkt - und genau dort stand frueher ueberall derselbe Textbaustein.
Die Untergrenze faengt Platzhalter und versehentlich geleerte Tags ab.

Rechtstexte tragen bewusst keine Description (sie stehen auf noindex).
"""
import glob
import os
import re
import sys

MAX = 160
MIN = 50
OHNE_DESCRIPTION_OK = {"datenschutz.html", "impressum.html", "privacy.html"}
# dashboard/produkt-review sind per robots.txt gesperrt, cozy/ ist abgekoppelt
IGNORIEREN = {"dashboard.html", "produkt-review.html"}

DESC_RE = re.compile(r'<meta[^>]+name="description"[^>]+content="([^"]*)"')


def seiten():
    for f in sorted(glob.glob("**/*.html", recursive=True)):
        if f.startswith("cozy" + os.sep) or f.startswith("cozy/"):
            continue
        if f in IGNORIEREN:
            continue
        yield f


def main():
    probleme = []
    geprueft = 0
    for f in seiten():
        html = open(f, encoding="utf-8", errors="ignore").read()
        m = DESC_RE.search(html)
        if not m:
            if f not in OHNE_DESCRIPTION_OK:
                probleme.append(f"{f}: keine meta description")
            continue
        geprueft += 1
        n = len(m.group(1))
        if n > MAX:
            probleme.append(f"{f}: Description {n} Zeichen (max {MAX}) — wird abgeschnitten")
        elif n < MIN:
            probleme.append(f"{f}: Description nur {n} Zeichen (min {MIN})")

    if probleme:
        for p in probleme:
            print("  " + p)
        return 1
    print(f"{geprueft} Meta-Descriptions in SERP-Laenge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
