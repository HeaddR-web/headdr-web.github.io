#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Pick-Karten aller BeThatHost-Seiten auf Vollstaendigkeit.

Eine Pick-Karte ist die Verkaufseinheit der Seite. Fehlt der Beschreibungstext,
steht dort nur eine Ueberschrift ueber einem Kauf-Button - der Leser bekommt
keinen Grund zu klicken und kein Signal, dass hier jemand ausgewaehlt hat.
Genau so waren im September 2026 21 Karten auf 10 Seiten unterwegs; sie sind
alle nachtraeglich per Hand angehaengt worden, ohne Text.

Zweite Pruefung: zwei Karten derselben Seite duerfen nicht auf dieselbe ASIN
zeigen. Passiert beim Kopieren einer Karte und schickt den Leser garantiert
auf das falsche Produkt (so geschehen auf jga/ mit B0D6YWD9TX).
"""
import glob
import re
import sys

MIN_TEXT = 30  # Zeichen; darunter ist es kein Kaufargument, sondern ein Platzhalter
IGNORIEREN = {"dashboard.html", "produkt-review.html"}

DIV_RE = re.compile(r'<(/?)div\b[^>]*>')
H4_RE = re.compile(r'<h4[^>]*>(.*?)</h4>', re.S)
P_RE = re.compile(r'<p>(.*?)</p>', re.S)
ASIN_RE = re.compile(r'amazon\.de/(?:dp|gp/product)/([A-Z0-9]{10})')
TAGS_RE = re.compile(r'<[^>]+>')


def karten(html):
    """Liefert jede <div class="pick">...</div> als Text - verschachtelungsfest.

    Ein einfaches Suchen nach dem naechsten </div> reicht nicht: die Karten mit
    Produktfoto enthalten <div class="pick-photo"> und <div class="pick-text">.
    """
    for start in re.finditer(r'<div class="pick">', html):
        tiefe = 0
        for t in DIV_RE.finditer(html, start.start()):
            tiefe += -1 if t.group(1) else 1
            if tiefe == 0:
                yield html[start.start():t.end()]
                break


def main():
    fehler = []
    for datei in sorted(glob.glob("**/*.html", recursive=True)):
        if datei.startswith("cozy/") or datei in IGNORIEREN:
            continue
        html = open(datei, encoding="utf-8").read()
        asins = {}
        for karte in karten(html):
            t = H4_RE.search(karte)
            name = TAGS_RE.sub("", t.group(1)).strip() if t else "(ohne Ueberschrift)"
            if not t:
                fehler.append(f"{datei}: Pick-Karte ohne <h4>")
            if 'class="cta"' not in karte:
                fehler.append(f"{datei}: Pick-Karte {name!r} ohne Kauf-Button")
            if not any(len(TAGS_RE.sub("", p).strip()) >= MIN_TEXT for p in P_RE.findall(karte)):
                fehler.append(f"{datei}: Pick-Karte {name!r} ohne Beschreibungstext")
            a = ASIN_RE.search(karte)
            if a:
                if a.group(1) in asins:
                    fehler.append(
                        f"{datei}: {name!r} und {asins[a.group(1)]!r} zeigen beide auf {a.group(1)}")
                asins[a.group(1)] = name

    for zeile in fehler:
        print(zeile)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
