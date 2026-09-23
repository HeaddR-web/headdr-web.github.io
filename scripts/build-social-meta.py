#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ergaenzt die Social-Meta-Tags im <head> - fuer die Vorschau beim Teilen.

Warum: Bis September 2026 trug jede Seite og:title, og:description, og:type und
og:image - und sonst nichts. Es fehlten:

  * og:url            ohne sie zaehlt Facebook /casino/ und /casino/?pin=pokerset
                      als zwei Seiten; jeder Pinterest-Link ist so eine eigene URL
  * og:site_name      "BeThatHost" ueber der Vorschau in WhatsApp und Facebook
  * og:locale         de_DE, sonst raet Facebook en_US
  * og:image:width/-height  ohne Masse laedt Facebook das Bild beim ersten Teilen
                      erst nachtraeglich, die erste Vorschau bleibt bildlos
  * og:image:alt      Bildbeschreibung fuer Screenreader in den Apps
  * twitter:card      ohne sie zeigt X nur ein briefmarkengrosses Bild

Dazu stand auf oktoberfest/ ein SVG als og:image - das zeigen WhatsApp,
Facebook und Pinterest gar nicht an. Das Skript bricht deshalb bei jedem
og:image ab, das kein JPG/PNG ist.

Quellen stehen alle schon auf der Seite: og:url <- canonical, Masse <- die
Bilddatei selbst, og:image:alt <- alt des Lead-Bilds, wenn es dasselbe Motiv
ist, sonst og:title. Der Block steht direkt hinter og:image zwischen
<!-- SOCIAL:START ... --> und <!-- SOCIAL:END --> und wird bei jedem Lauf
komplett ersetzt. Seiten ohne og:image (Rechtstexte, Offenlegungen, interne
Werkzeuge, 404 - alle noindex) bleiben unberuehrt.

Aufruf: python3 scripts/build-social-meta.py [--pruefen]
"""
import html
import os
import re
import sys

from PIL import Image

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = "https://bethathost.de/"
SITE_NAME = "BeThatHost"
LOCALE = "de_DE"

START = "<!-- SOCIAL:START — erzeugt von scripts/build-social-meta.py, nicht von Hand aendern -->"
ENDE = "<!-- SOCIAL:END -->"
BLOCK_RE = re.compile(r"\n?[ \t]*<!-- SOCIAL:START.*?<!-- SOCIAL:END -->", re.S)
OG_IMAGE_RE = re.compile(r'^([ \t]*)<meta property="og:image" content="([^"]+)" />[ \t]*$', re.M)
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
OG_TITLE_RE = re.compile(r'<meta property="og:title" content="([^"]*)"')
LEAD_RE = re.compile(r'<img class="lead"\s[^>]*?/?>')
# Von Hand gesetzte Tags, die der Block uebernimmt (ueber-uns.html hatte og:url).
ALT_RE = re.compile(
    r'\n[ \t]*<meta (?:property="og:(?:url|site_name|locale|image:(?:width|height|alt))"'
    r'|name="twitter:card") content="[^"]*" />')


def seiten():
    for ordner, unter, dateien in os.walk(WURZEL):
        rel = os.path.relpath(ordner, WURZEL)
        teile = rel.split(os.sep)
        if teile[0] in ("cozy", "assets", "scripts", "node_modules") or (rel != "." and teile[0].startswith(".")):
            unter[:] = []
            continue
        for d in dateien:
            if d.endswith(".html"):
                yield os.path.normpath(os.path.join(rel, d))


def stamm(url):
    name = url.rsplit("/", 1)[-1]
    name = re.sub(r"\.(jpe?g|png|webp|svg)$", "", name)
    return re.sub(r"-\d+$", "", name)


def attr(tag, name):
    m = re.search(r'\s%s="([^"]*)"' % name, tag)
    return m.group(1) if m else None


def block(text, pfad):
    og = OG_IMAGE_RE.search(text)
    if not og:
        return None, None
    einzug, bild = og.group(1), og.group(2)
    if not bild.startswith(BASIS + "assets/"):
        raise SystemExit(f"{pfad}: og:image liegt nicht unter {BASIS}assets/: {bild}")
    if not re.search(r"\.(jpe?g|png)$", bild, re.I):
        raise SystemExit(f"{pfad}: og:image muss JPG oder PNG sein (WhatsApp/Facebook/Pinterest "
                         f"zeigen nichts anderes an): {bild}")
    datei = os.path.join(WURZEL, bild[len(BASIS):])
    if not os.path.exists(datei):
        raise SystemExit(f"{pfad}: og:image fehlt: {bild}")
    with Image.open(datei) as im:
        breite, hoehe = im.size

    canon = CANONICAL_RE.search(text)
    if not canon:
        raise SystemExit(f"{pfad}: kein canonical - og:url braucht es als Quelle")

    alt = None
    lead = LEAD_RE.search(text)
    if lead and stamm(attr(lead.group(0), "src") or "") == stamm(bild):
        alt = attr(lead.group(0), "alt")
    if not alt:
        t = OG_TITLE_RE.search(text)
        alt = t.group(1) if t else None
    if not alt:
        raise SystemExit(f"{pfad}: weder Lead-alt noch og:title fuer og:image:alt")
    alt = html.escape(html.unescape(alt), quote=True)

    zeilen = [
        START,
        f'<meta property="og:url" content="{canon.group(1)}" />',
        f'<meta property="og:site_name" content="{SITE_NAME}" />',
        f'<meta property="og:locale" content="{LOCALE}" />',
        f'<meta property="og:image:width" content="{breite}" />',
        f'<meta property="og:image:height" content="{hoehe}" />',
        f'<meta property="og:image:alt" content="{alt}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        ENDE,
    ]
    return og, "\n".join(einzug + z for z in zeilen)


def verarbeite(text, pfad):
    text = BLOCK_RE.sub("", text)
    og, neu = block(text, pfad)
    if og is None:
        return text
    text = ALT_RE.sub("", text)
    og = OG_IMAGE_RE.search(text)
    return text[:og.end()] + "\n" + neu + text[og.end():]


def main():
    pruefen = "--pruefen" in sys.argv[1:]
    fehler, geaendert, gesamt = [], 0, 0
    for pfad in sorted(seiten()):
        voll = os.path.join(WURZEL, pfad)
        with open(voll, encoding="utf-8") as f:
            alt = f.read()
        neu = verarbeite(alt, pfad)
        if START in neu:
            gesamt += 1
        if neu != alt:
            if pruefen:
                fehler.append(pfad)
            else:
                with open(voll, "w", encoding="utf-8") as f:
                    f.write(neu)
                geaendert += 1
    if pruefen:
        if fehler:
            print("Social-Meta nicht aktuell (python3 scripts/build-social-meta.py):")
            for p in fehler:
                print("  " + p)
            sys.exit(1)
        print(f"Social-Meta aktuell ({gesamt} Seiten)")
    else:
        print(f"{geaendert} Seiten aktualisiert, {gesamt} mit Social-Meta")


if __name__ == "__main__":
    main()
