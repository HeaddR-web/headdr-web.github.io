#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut /llms.txt - das Inhaltsverzeichnis der Seite fuer KI-Suchen.

Seit 02.11.2026 ist bethathost.de nur noch ein Shop fuer eigene 3D-Druck-Teile
(zum Start Platzkartenhalter und JGA-Anhaenger); alle alten Inhaltsseiten sind
Weiterleitungen. Die
Datei wird deshalb nicht mehr aus THEMA/NAME (build-related.py) erzeugt,
sondern aus der kurzen Liste unten. Jede dort verlinkte Seite muss als Datei
existieren, sonst bricht der Lauf ab. Texte nur mit Fakten aus shop/*.html,
keine Preise (stehen dort noch nicht fest).

Aufruf: python3 scripts/build-llms.py [--pruefen]
"""
import os
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = "https://bethathost.de/"
ZIEL = os.path.join(WURZEL, "llms.txt")

KOPF = """# BeThatHost, bethathost.de

> Online-Shop für eigene Teile aus dem 3D-Drucker. Manche Entwürfe sind fertig, individualisieren lässt sich jedes, zum Beispiel mit einem Namen oder Text. Zum Start gibt es Platzkartenhalter und JGA-Anhänger. Entworfen von BeThatHost, gedruckt bei einem 3D-Druck-Partner, verschickt von BeThatHost selbst.

Die Seite hat keine eigene Kasse. Bestellt wird über ein Etsy-Listing, dort gibst du den Namen oder Text an. Solange die Listings noch nicht stehen, sind die Produktseiten Platzhalter. Preise, Material und Maße stehen noch nicht fest.
"""

ABSCHNITTE = [
    ("Shop", [
        ("index.html", "Shop-Startseite",
         "Alle Produkte im Überblick, jedes lässt sich individualisieren. Dazu der Ablauf der Bestellung."),
        ("shop/platzkartenhalter.html", "Platzkartenhalter mit Namen",
         "Ein Halter je Gast, mit dem Namen gedruckt, für Hochzeit und Geburtstag."),
        ("shop/jga-anhaenger.html", "JGA-Anhänger im Set",
         "Schlüsselanhänger im Set für die ganze Gruppe beim Junggesellenabschied."),
    ]),
    ("Rechtliches", [
        ("impressum.html", "Impressum", ""),
        ("datenschutz.html", "Datenschutz", ""),
    ]),
]


def url(pfad):
    return BASIS + (pfad[: -len("index.html")] if pfad.endswith("index.html") else pfad)


def baue():
    teile = [KOPF]
    for titel, eintraege in ABSCHNITTE:
        zeilen = []
        for pfad, name, text in eintraege:
            if not os.path.exists(os.path.join(WURZEL, pfad)):
                raise SystemExit(f"llms.txt verlinkt {pfad}, die Datei gibt es nicht")
            zeilen.append(f"- [{name}]({url(pfad)})" + (f": {text}" if text else ""))
        teile.append(f"## {titel}\n\n" + "\n".join(zeilen) + "\n")
    return "\n".join(teile)


def main():
    neu = baue()
    alt = open(ZIEL, encoding="utf-8").read() if os.path.exists(ZIEL) else ""
    if "--pruefen" in sys.argv:
        if neu != alt:
            print("llms.txt nicht aktuell")
            sys.exit(1)
        print("llms.txt aktuell")
        return
    if neu != alt:
        open(ZIEL, "w", encoding="utf-8").write(neu)
        print("llms.txt geschrieben")
    else:
        print("llms.txt unveraendert")


if __name__ == "__main__":
    main()
