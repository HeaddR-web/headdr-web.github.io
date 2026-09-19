#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Brotkrumen-Navigation (<nav class="breadcrumb">).

Drei Fehler:
  * Der Block fehlt oder passt nicht mehr zur Startseite - jemand hat eine
    Karte von #anlaesse nach #mottopartys verschoben, eine Seite umbenannt
    oder eine neue angelegt, ohne build-breadcrumb.py laufen zu lassen. Dann
    zeigt Google im Suchergebnis eine Kategorie an, die nicht mehr stimmt.
  * Eine Seite hat gar keine Zuordnung: sie steht in keinem Abschnitt der
    Startseite oder nicht in NAME - dann bekommt sie weder Brotkrume noch
    BreadcrumbList und faellt aus der Struktur.
  * Sichtbare Zeile und BreadcrumbList sagen Verschiedenes. Beides baut
    dieselbe Funktion, dieser Punkt trifft also nicht Handarbeit (die faengt
    schon "nicht aktuell" ab), sondern einen Fehler im Generator selbst: Wenn
    baue() die beiden Ausgaben auseinanderlaufen laesst, zeigt Google etwas
    anderes an als der Leser sieht, und das faellt sonst erst Wochen spaeter
    in der Search Console auf.

Beheben mit: python3 scripts/build-breadcrumb.py
(Bei einer neuen Seite vorher die Karte auf der Startseite anlegen und den
Slug in NAME in build-related.py eintragen.)
"""
import glob
import html as H
import importlib.util
import json
import re
import sys

spec = importlib.util.spec_from_file_location("build_breadcrumb", "scripts/build-breadcrumb.py")
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)

TEXT_RE = re.compile(r'<(?:a|span)[^>]*>(?P<text>[^<]*)</(?:a|span)>')
JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def sichtbar(block):
    nav = re.search(r'<nav class="breadcrumb".*?</nav>', block, re.S)
    return [H.unescape(m.group("text")).strip() for m in TEXT_RE.finditer(nav.group(0))] if nav else []


def ausgezeichnet(block):
    for m in JSONLD_RE.finditer(block):
        try:
            daten = json.loads(m.group(1))
        except json.JSONDecodeError:
            return None
        if isinstance(daten, dict) and daten.get("@type") == "BreadcrumbList":
            return [e.get("name", "") for e in daten.get("itemListElement", [])]
    return None


def main():
    fehler, veraltet, ohne = [], [], []

    for pfad in sorted(glob.glob("**/*.html", recursive=True)):
        if pfad.startswith("cozy/") or pfad in bb.AUSGENOMMEN:
            continue
        html = open(pfad, encoding="utf-8").read()
        block = bb.BLOCK_RE.search(html)

        if bb.pfad_fuer(pfad) is None:
            ohne.append(pfad)
            continue
        if not block:
            veraltet.append(pfad)
            continue

        _, hat_sich_geaendert = bb.verarbeite(pfad, schreiben=False)
        if hat_sich_geaendert:
            veraltet.append(pfad)
            continue

        gesehen, markup = sichtbar(block.group(0)), ausgezeichnet(block.group(0))
        if markup is None:
            fehler.append(f"{pfad}: Brotkrume ohne BreadcrumbList")
        elif gesehen != markup:
            fehler.append(f"{pfad}: sichtbar {gesehen} != ausgezeichnet {markup}")

    if ohne:
        fehler.insert(0, "Ohne Zuordnung (Karte auf der Startseite? Slug in NAME?): "
                         + ", ".join(ohne))
    if veraltet:
        fehler.insert(0, "Nicht aktuell: " + ", ".join(veraltet))
    if fehler:
        print("\n".join(fehler))
        print("Beheben mit: python3 scripts/build-breadcrumb.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
