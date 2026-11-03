#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Kachel-, Hero-, Lead- und Produktbilder.

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
  * Eine Ableitung liegt herum, die keine Seite mehr verlinkt. Das passiert
    bei jeder Aenderung an den Stufen (etwa Kacheln von 960 auf 720) und
    faellt sonst niemandem auf: die Dateien bleiben im Repo, und spaeter ist
    nicht mehr zu erkennen, welche davon noch gebraucht werden.
    Ausgenommen sind nur die Altbilder in scripts/altbilder.txt.

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

# Seit 02.11.2026 sind die alten Inhaltsseiten Weiterleitungen und verlinken
# keine Bilder mehr. Ihre Ableitungen bleiben bis zum Aufraeum-PR liegen
# (nichts loeschen, auch nicht per build-images.py, das Verwaistes entfernt).
# Erlaubt sind genau die Dateien in dieser Liste, damit neue Reste auffallen.
ALTBILDER = os.path.join(HIER, "altbilder.txt")


def altbilder():
    if not os.path.exists(ALTBILDER):
        return set()
    with open(ALTBILDER, encoding="utf-8") as f:
        return {z.strip() for z in f if z.strip() and not z.startswith("#")}


def main():
    offen = []
    gebraucht = set()
    for pfad in bilder.seiten():
        staemme, heroes, geaendert = bilder.verarbeite(pfad, schreiben=False)
        if geaendert:
            offen.append(f"Markup nicht aktuell: {pfad}")
        for stamm, breiten in staemme.items():
            for datei in bilder.erzeuge(stamm, breiten, schreiben=False):
                offen.append(f"Ableitung fehlt: {datei}")
            gebraucht.update(os.path.join(bilder.KACHEL_DIR, f"{stamm}-{b}.jpg")
                             for b in breiten)
        for stamm in dict.fromkeys(heroes):
            for datei in bilder.hero_erzeuge(stamm, schreiben=False):
                offen.append(f"Hero-Ableitung fehlt: {datei}")
            gebraucht.update(bilder.hero_dateien(stamm))
        if HINTERGRUND_RE.search(open(os.path.join(bilder.WURZEL, pfad), encoding="utf-8").read()):
            offen.append(f"Kachel noch als CSS-Hintergrund: {pfad}")

    # Lead-Bilder der Artikel (article img.lead) - das LCP-Element der Seite.
    for pfad in bilder.lead_seiten():
        staemme, geaendert = bilder.verarbeite_lead(pfad, schreiben=False)
        if geaendert:
            offen.append(f"Lead-Bild nicht aktuell: {pfad}")
        for stamm in staemme:
            for datei in bilder.lead_erzeuge(stamm, schreiben=False):
                offen.append(f"Lead-Ableitung fehlt: {datei}")
            gebraucht.update(os.path.join(bilder.LEAD_DIR, f"{stamm}-{b}.jpg")
                             for b in bilder.lead_breiten(stamm))

        # Produktfotos der Pick-Karten (div.pick-photo img).
        staemme, geaendert = bilder.verarbeite_produkt(pfad, schreiben=False)
        if geaendert:
            offen.append(f"Produktfoto nicht aktuell: {pfad}")
        for stamm in staemme:
            for datei in bilder.produkt_erzeuge(stamm, schreiben=False):
                offen.append(f"Produkt-Ableitung fehlt: {datei}")
            gebraucht.update(os.path.join(bilder.PRODUKT_DIR, f"{stamm}-{b}.jpg")
                             for b in bilder.produkt_breiten(stamm))

    erlaubt = altbilder()
    verwaist = set(bilder.verwaist(gebraucht))
    for datei in sorted(verwaist - erlaubt):
        offen.append(f"Ableitung verwaist: {datei}")
    # eine Zeile, die nicht mehr verwaist ist (geloescht oder wieder gebraucht),
    # wuerde spaeter eine neue Datei gleichen Namens unbemerkt durchlassen
    for datei in sorted(erlaubt - verwaist):
        offen.append(f"Altbild-Liste veraltet, Zeile streichen: {datei}")

    if offen:
        print("\n".join(offen))
        sys.exit(1)
    print("Kachel-, Hero-, Lead- und Produktbilder aktuell"
          + (f" ({len(erlaubt)} Altbilder laut scripts/altbilder.txt)" if erlaubt else ""))


if __name__ == "__main__":
    main()
