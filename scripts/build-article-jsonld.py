#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ergaenzt im Article-JSON-LD jeder Seite `dateModified` und `image`.

Grund: Bis September 2026 fehlten beide Felder auf allen 33 Artikelseiten.
Google fuehrt sie als empfohlen; ohne `image` ist eine Seite fuer die
Bilddarstellung in der Suche und in Discover nicht vorgesehen, und die
Search Console meldet jede Seite als "Fehlendes Feld image".

Quellen - nichts wird erfunden, beide Werte stehen schon auf der Seite:
  * image        <- <meta property="og:image">
  * dateModified <- sichtbares "Aktualisiert am 19. Juni 2026" im <p class="meta">
Google verlangt, dass das Datum im Markup zum sichtbaren Datum passt. Das
sichtbare Datum ist deshalb die Quelle; dieses Skript setzt es nie selbst.

Aufruf:  python3 scripts/build-article-jsonld.py            (schreibt)
         python3 scripts/build-article-jsonld.py --pruefen  (meldet nur, Exit 1)
"""

import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUS = ("cozy", ".git", "node_modules")

MONATE = {m: i for i, m in enumerate(
    ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
     "September", "Oktober", "November", "Dezember"], 1)}

SKRIPT_RE = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)
OG_RE = re.compile(r'<meta property="og:image" content="([^"]+)"')
DATUM_RE = re.compile(r'class="meta">Aktualisiert am (\d{1,2})\. (\w+) (\d{4})')
# Die generierten Zeilen - werden bei jedem Lauf entfernt und neu gesetzt.
ALT_RE = re.compile(r'\n[ \t]*"(?:dateModified|image)": [^\n]*(?=\n)')
PUBL_RE = re.compile(r'(\n([ \t]*)"datePublished": "([0-9-]+)"),?')


def seiten():
    for pfad, ordner, dateien in os.walk(WURZEL):
        ordner[:] = sorted(o for o in ordner if o not in AUS)
        for d in sorted(dateien):
            if d.endswith(".html"):
                yield os.path.join(pfad, d)


def umbau(text, name):
    """Liefert (neuer_text, fehler). fehler ist None oder eine Meldung."""
    for m in SKRIPT_RE.finditer(text):
        block = m.group(0)
        if '"@type": "Article"' not in block:
            continue
        og = OG_RE.search(text)
        dm = DATUM_RE.search(text)
        if not og:
            return text, "kein og:image"
        if not dm:
            return text, 'kein sichtbares "Aktualisiert am …"'
        monat = MONATE.get(dm.group(2))
        if not monat:
            return text, f"Monat unbekannt: {dm.group(2)}"
        datum = f"{dm.group(3)}-{monat:02d}-{int(dm.group(1)):02d}"

        neu = ALT_RE.sub("", block)
        p = PUBL_RE.search(neu)
        if not p:
            return text, "kein datePublished im Article-JSON-LD"
        if p.group(3) > datum:
            return text, f"datePublished {p.group(3)} liegt nach dem sichtbaren Datum {datum}"
        einzug = p.group(2)
        zusatz = (f'{p.group(1)},\n{einzug}"dateModified": "{datum}",'
                  f'\n{einzug}"image": ["{og.group(1)}"]')
        neu = neu[:p.start()] + zusatz + neu[p.end():]
        return text[:m.start()] + neu + text[m.end():], None
    return text, None


def main():
    pruefen = "--pruefen" in sys.argv
    geaendert, fehler, gesamt = [], [], 0
    for pfad in seiten():
        name = os.path.relpath(pfad, WURZEL)
        text = open(pfad, encoding="utf-8").read()
        if '"@type": "Article"' not in text:
            continue
        gesamt += 1
        neu, f = umbau(text, name)
        if f:
            fehler.append(f"{name}: {f}")
            continue
        if neu != text:
            geaendert.append(name)
            if not pruefen:
                open(pfad, "w", encoding="utf-8").write(neu)
    for f in fehler:
        print(f"  {f}")
    if pruefen:
        for n in geaendert:
            print(f"  {n}: dateModified/image nicht aktuell")
        sys.exit(1 if geaendert or fehler else 0)
    print(f"{gesamt} Artikelseiten, {len(geaendert)} geaendert")
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
