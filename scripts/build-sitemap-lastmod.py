#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""<lastmod> in sitemap.xml auf den echten Aenderungsstand ziehen.

Bis September 2026 standen dort durchgehend Juni-/Juli-Daten, obwohl im
September jede Seite angefasst worden war (FAQ, Brotkrume, Weiterlesen-Block,
Bildgroessen). Google zieht <lastmod> nur heran, solange die Angabe
nachweislich stimmt - sind die Daten erkennbar veraltet, ignoriert der Crawler
das Feld komplett, und genau die frisch ueberarbeiteten Seiten werden spaeter
neu eingelesen.

Das Datum kommt aus git: der letzte Commit, der die Datei angefasst hat. Bei
noch nicht eingecheckten Aenderungen zaehlt heute - sonst behauptete die
Sitemap einen Stand, der aelter ist als die Datei.

Aufruf: python3 scripts/build-sitemap-lastmod.py [--pruefen]
"""
import datetime as dt
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(WURZEL, "sitemap.xml")
URL_RE = re.compile(r"<url><loc>(?P<loc>[^<]+)</loc><lastmod>(?P<datum>[^<]+)</lastmod>")


def datei_fuer(loc):
    pfad = urlparse(loc).path.lstrip("/")
    if pfad == "" or pfad.endswith("/"):
        pfad += "index.html"
    return pfad


def stand(pfad):
    voll = os.path.join(WURZEL, pfad)
    if not os.path.exists(voll):
        return None
    geaendert = subprocess.run(
        ["git", "status", "--porcelain", "--", pfad], cwd=WURZEL,
        capture_output=True, text=True).stdout.strip()
    if geaendert:
        return dt.date.today().isoformat()
    datum = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", pfad], cwd=WURZEL,
        capture_output=True, text=True).stdout.strip()
    return datum or None


def main():
    pruefen = "--pruefen" in sys.argv
    xml = open(SITEMAP, encoding="utf-8").read()
    offen = []
    fehlend = []

    def ersetze(m):
        pfad = datei_fuer(m.group("loc"))
        neu = stand(pfad)
        if neu is None:
            fehlend.append(f"Datei fehlt zu {m.group('loc')}: {pfad}")
            return m.group(0)
        if neu != m.group("datum"):
            offen.append(f"{pfad}: {m.group('datum')} -> {neu}")
        return f"<url><loc>{m.group('loc')}</loc><lastmod>{neu}</lastmod>"

    ergebnis = URL_RE.sub(ersetze, xml)
    if fehlend:
        print("\n".join(fehlend))
        sys.exit(1)
    if pruefen:
        if offen:
            print("\n".join(offen))
            sys.exit(1)
        print("sitemap.xml: alle lastmod aktuell")
        return
    if ergebnis != xml:
        open(SITEMAP, "w", encoding="utf-8").write(ergebnis)
    print(f"sitemap.xml: {len(offen)} von {len(URL_RE.findall(xml))} Daten aktualisiert")


if __name__ == "__main__":
    main()
