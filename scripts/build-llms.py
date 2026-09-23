#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut /llms.txt - das Inhaltsverzeichnis der Seite fuer KI-Suchen.

Warum: llms.txt wurde am 20. Juli 2026 von Hand angelegt und danach nie wieder
angefasst. Im September 2026 standen darin 13 von 37 Seiten: alle Mottopartys,
alle Anlass-Seiten (brunch, casino, geburtstag, jga, ...) und alle fuenf
Kaufratgeber fehlten. robots.txt laedt GPTBot, ClaudeBot, PerplexityBot & Co.
ausdruecklich ein - und schickte sie dann zu einer Liste, die zwei Drittel der
Seite verschwieg.

Deshalb wird die Datei jetzt erzeugt, und zwar aus den Listen, die es schon
gibt: Welche Seiten es gibt und wie sie heissen, steht in THEMA und NAME in
build-related.py (derselbe Ort, der auch den Weiterlesen-Block baut - eine
Seite ohne Eintrag dort faellt schon in Punkt 14 auf). Die Beschreibung je
Seite ist ihre meta description. Es gibt also keine zweite Liste, die wieder
veralten koennte.

Aufruf: python3 scripts/build-llms.py [--pruefen]
"""
import html
import importlib.util
import os
import re
import sys

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "build_related", os.path.join(WURZEL, "scripts", "build-related.py"))
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)

BASIS = "https://bethathost.de/"
ZIEL = os.path.join(WURZEL, "llms.txt")

KOPF = """# BeThatHost — bethathost.de

> Deutschsprachige Seite zum Planen von Feiern und Abenden zuhause: Mädelsabend, Cocktailabend, WM-Party, Geburtstag, Mottopartys und mehr. Pro Anlass kuratierte Produktempfehlungen mit direktem Link, ausführliche Guides und Kaufratgeber.

Finanziert über Affiliate-Links (Amazon.de) und Display-Werbung; jede Seite legt das offen. Alle Inhalte auf Deutsch.
"""

# Reihenfolge und Ueberschrift der Abschnitte. Jeder Schluessel ist ein THEMA
# aus build-related.py; ein neues Thema ohne Eintrag hier laesst --pruefen rot
# werden, statt still zu verschwinden.
ABSCHNITTE = [
    ("girlsnight", "Mädelsabend"),
    ("cocktail", "Cocktailabend"),
    ("watchparty", "WM- und Fußball-Party"),
    ("anlaesse", "Anlässe"),
    ("mottos", "Mottopartys"),
    ("ratgeber", "Kaufratgeber"),
]
# Nach der llms.txt-Konvention darf ein Leser den Abschnitt "Optional" auslassen.
OPTIONAL = [
    ("ueber-uns.html", "Über BeThatHost"),
    ("girlsnight/disclosure.html", "Offenlegung: Affiliate-Links"),
    ("datenschutz.html", "Datenschutz"),
    ("impressum.html", "Impressum"),
]

DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.S)


def url(pfad):
    return BASIS + (pfad[: -len("index.html")] if pfad.endswith("index.html") else pfad)


def beschreibung(pfad):
    text = open(os.path.join(WURZEL, pfad), encoding="utf-8").read()
    m = DESC_RE.search(text)
    return " ".join(html.unescape(m.group(1)).split()) if m else ""


def eintrag(pfad, name):
    desc = beschreibung(pfad)
    return f"- [{name}]({url(pfad)})" + (f": {desc}" if desc else "")


def baue():
    fehlt = [t for t in br.THEMA if t not in dict(ABSCHNITTE)]
    if fehlt:
        raise SystemExit(f"THEMA ohne Abschnitt in build-llms.py: {', '.join(fehlt)}")
    teile = [KOPF]
    for thema, titel in ABSCHNITTE:
        zeilen = [eintrag(p, br.NAME[p]) for p in br.THEMA[thema]]
        teile.append(f"## {titel}\n\n" + "\n".join(zeilen) + "\n")
    zeilen = [eintrag(p, n) for p, n in OPTIONAL if os.path.exists(os.path.join(WURZEL, p))]
    teile.append("## Optional\n\n" + "\n".join(zeilen) + "\n")
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
        print(f"llms.txt geschrieben ({neu.count(chr(10) + '- [')} Seiten)")
    else:
        print("llms.txt unveraendert")


if __name__ == "__main__":
    main()
