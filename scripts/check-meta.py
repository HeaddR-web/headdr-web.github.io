#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Meta-Descriptions aller BeThatHost-Seiten auf SERP-Laenge.

Google schneidet deutsche Snippets bei rund 155-160 Zeichen ab. Laengere
Beschreibungen sind nicht kaputt, aber der Teil hinter dem Schnitt ist
verschenkt - und genau dort stand frueher ueberall derselbe Textbaustein.
Die Untergrenze faengt Platzhalter und versehentlich geleerte Tags ab.

Rechtstexte tragen bewusst keine Description (sie stehen auf noindex).

Dazu der <title>: Google zeigt rund 580 Pixel, bei deutschem Text etwa 60
Zeichen. Bis September 2026 waren 24 Titel laenger (bis 88 Zeichen) - hinter
dem Schnitt verschwand genau das " — BeThatHost", also die Marke.
"""
import glob
import html as htmllib
import os
import re
import sys

MAX = 160
TITEL_MAX = 60
MIN = 50
OHNE_DESCRIPTION_OK = {"datenschutz.html", "impressum.html", "privacy.html"}
# dashboard/produkt-review sind per robots.txt gesperrt, cozy/ ist abgekoppelt
IGNORIEREN = {"dashboard.html", "produkt-review.html"}

TITEL_RE = re.compile(r"<title>(.*?)</title>", re.S)
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
        mt = TITEL_RE.search(html)
        if not mt:
            probleme.append(f"{f}: kein <title>")
        else:
            nt = len(htmllib.unescape(mt.group(1).strip()))
            if nt > TITEL_MAX:
                probleme.append(f"{f}: Titel {nt} Zeichen (max {TITEL_MAX}) — wird abgeschnitten")
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
    print(f"{geprueft} Meta-Descriptions und alle Titel in SERP-Laenge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
