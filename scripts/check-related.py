#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft den Weiterlesen-Block (<nav class="related">).

Drei Fehler:
  * Ein Block fehlt oder passt nicht zum Plan in build-related.py - dann hat
    jemand von Hand editiert oder eine Seite ergaenzt, ohne sie in THEMA
    einzutragen.
  * Eine Seite ist eine Waise: kein einziger Artikel verlinkt auf sie, sie ist
    nur ueber die Startseite erreichbar. Genau das war im September 2026 bei
    neun Seiten der Fall.
  * Ein interner Link zeigt auf eine Datei, die es nicht gibt.
  * Inhalt steht zwischen </main> und <footer> und damit ausserhalb des
    Layout-Containers - er laeuft dann ohne Seitenrand quer ueber den ganzen
    Bildschirm. Genau so standen bis September 2026 14 handgemachte
    "Weitere Ideen:"-Absaetze auf der Seite, randlos und doppelt unter dem
    Weiterlesen-Block.

Beheben mit: python3 scripts/build-related.py
(Bei einer neuen Seite vorher den Slug in NAME und THEMA eintragen.)
"""
import collections
import glob
import importlib.util
import os
import re
import sys

spec = importlib.util.spec_from_file_location("build_related", "scripts/build-related.py")
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)

NUR_NAVIGATION = {"index.html", "ueber-uns.html", "datenschutz.html",
                  "impressum.html", "privacy.html", "dashboard.html",
                  "produkt-review.html", "404.html"}
LINK_RE = re.compile(r'href="(/[^"#?]*)"')


def norm(ziel):
    z = ziel.lstrip("/")
    return z + "index.html" if z.endswith("/") or z == "" else z


def main():
    fehler = []
    plan = br.ziele()

    # 1) Block vorhanden und aktuell?
    veraltet = []
    for seite, ziel_liste in sorted(plan.items()):
        html = open(seite, encoding="utf-8").read()
        block = br.BLOCK_RE.search(html)
        if not block or block.group(0) != br.block_fuer(ziel_liste):
            veraltet.append(seite)
    if veraltet:
        fehler.append("Nicht aktuell: " + ", ".join(veraltet))

    # 2) Waisen und tote Links ueber alle Seiten
    seiten = [f for f in sorted(glob.glob("**/*.html", recursive=True))
              if not f.startswith("cozy/") and not f.endswith("disclosure.html")]
    ein = collections.Counter()
    for f in seiten:
        html = open(f, encoding="utf-8").read()
        a = html.find("<main")
        a = a if a >= 0 else html.find("<article")
        b = html.rfind("</main")
        b = b if b >= 0 else html.rfind("</article")
        for ziel in {norm(z) for z in LINK_RE.findall(html[a:b])}:
            if ziel != f:
                ein[ziel] += 1
        for ziel in {norm(z) for z in LINK_RE.findall(html)}:
            if not os.path.exists(ziel):
                fehler.append(f"{f}: Link auf {ziel} - Datei gibt es nicht")

    for f in seiten:
        if f not in NUR_NAVIGATION and ein[f] == 0:
            fehler.append(f"{f}: Waise - kein Artikel verlinkt dorthin")

    # 3) Nichts zwischen </main> und <footer>: dort greift kein Seitenrand.
    for f in seiten:
        html = open(f, encoding="utf-8").read()
        a = html.rfind("</main>")
        b = html.find("<footer", a) if a >= 0 else -1
        if a >= 0 and b > a and html[a + len("</main>"):b].strip():
            fehler.append(f"{f}: Inhalt zwischen </main> und <footer> - ohne Seitenrand")

    if fehler:
        print("\n".join(sorted(set(fehler))))
        print("Beheben mit: python3 scripts/build-related.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
