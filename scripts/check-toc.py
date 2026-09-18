#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Inhaltsverzeichnisse (<nav class="toc">).

Zwei Fehler, die hier wehtun:
  * Der Block passt nicht mehr zu den Ueberschriften darunter - jemand hat eine
    <h2> ergaenzt, umbenannt oder geloescht und build-toc.py nicht laufen lassen.
    Dann zeigt das Verzeichnis dem Leser Abschnitte, die es nicht gibt, oder ein
    Link springt ins Leere. (Beides faellt hier als "nicht aktuell" auf: das
    Skript baut den Block neu und vergleicht ihn mit dem, was in der Datei steht.)
  * Das Verzeichnis steht ueber der Einkaufsliste. Die Liste ist der einzige
    Kaufweg above the fold; alles, was sie nach unten schiebt, kostet Umsatz.
    Genau das passiert, wenn build-quickbuy.py und build-toc.py um dieselbe
    Einfuegestelle streiten.

Beheben in beiden Faellen mit: python3 scripts/build-toc.py
"""
import glob
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("build_toc", "scripts/build-toc.py")
build_toc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_toc)


def main():
    fehler, veraltet = [], []
    for pfad in sorted(glob.glob("**/*.html", recursive=True)):
        if pfad.startswith("cozy/") or pfad in build_toc.AUSGENOMMEN:
            continue
        html = open(pfad, encoding="utf-8").read()
        block = build_toc.BLOCK_RE.search(html)

        soll = build_toc.verarbeite(pfad, schreiben=False)
        if soll is None:
            if block:
                fehler.append(f"{pfad}: Verzeichnis auf einer zu kurzen Seite")
            continue
        if not block or soll[1]:
            veraltet.append(pfad)
            continue

        qb = html.find("<!-- QUICKBUY:END -->")
        if 0 <= qb and block.start() < qb:
            fehler.append(f"{pfad}: Verzeichnis steht ueber der Einkaufsliste")

    if veraltet:
        fehler.insert(0, "Nicht aktuell: " + ", ".join(veraltet))
    if fehler:
        print("\n".join(fehler))
        print("Beheben mit: python3 scripts/build-toc.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
