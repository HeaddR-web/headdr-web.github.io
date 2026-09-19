#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Kachel- und Hero-Bilder.

Drei Fehler:
  * Das Markup ist nicht aktuell: eine Kachel zeigt noch auf das Original
    statt auf die Ableitung. Dann laedt der Besucher wieder 1600 px breite
    Bilder fuer eine 360-px-Kachel - genau das, was auf girlsnight/ einen
    LCP von 6,2 s verursacht hat (Schwelle: 2,5 s).
  * Eine Ableitung fehlt auf der Platte, obwohl das Markup sie verlinkt.
    Dann bleibt die Kachel leer.
  * Eine Seite bindet ein Kachelbild noch als CSS-Hintergrund ein. Ein
    Hintergrund laesst sich nicht verzoegern (loading="lazy"), er laedt
    immer sofort mit - auf girlsnight/ waren das elf Bilder auf einmal.

Beheben mit: python3 scripts/build-images.py
"""
import importlib.util
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("build_images", os.path.join(HIER, "build-images.py"))
bilder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bilder)

HINTERGRUND_RE = bilder.re.compile(
    r'<div class="(?:cover|thumb)" style="[^"]*background-image'
)


def main():
    offen = []
    for pfad in bilder.seiten():
        staemme, heroes, geaendert = bilder.verarbeite(pfad, schreiben=False)
        if geaendert:
            offen.append(f"Markup nicht aktuell: {pfad}")
        for stamm, breiten in staemme.items():
            for datei in bilder.erzeuge(stamm, breiten, schreiben=False):
                offen.append(f"Ableitung fehlt: {datei}")
        for stamm in dict.fromkeys(heroes):
            for datei in bilder.hero_erzeuge(stamm, schreiben=False):
                offen.append(f"Hero-Ableitung fehlt: {datei}")
        if HINTERGRUND_RE.search(open(os.path.join(bilder.WURZEL, pfad), encoding="utf-8").read()):
            offen.append(f"Kachel noch als CSS-Hintergrund: {pfad}")

    if offen:
        print("\n".join(offen))
        sys.exit(1)
    print("Kachel- und Hero-Bilder aktuell")


if __name__ == "__main__":
    main()
