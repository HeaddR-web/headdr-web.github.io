#!/usr/bin/env python3
"""Baut den Schnellkauf-Block ("Die Einkaufsliste") oben auf jeder Anlass-Seite.

Warum es den Block gibt: Vor der Einfuehrung stand der erste Affiliate-Link bei
25-48 % der Seitenlaenge. Auf dem Handy - und ein Grossteil des Traffics kommt
ueber Pinterest, also mobil - hat ein Besucher bis dahin zwei bis drei Mal
gewischt. Wer vorher abspringt, sieht nie eine Empfehlung. Der Block zieht alle
Picks einer Seite als kompakte Liste direkt unter die Einleitung; die
Begruendung zu jedem Pick bleibt weiter unten im Fliesstext stehen.

Der Block wird aus den vorhandenen .pick-Karten generiert, nicht von Hand
gepflegt - so kann er nicht auseinanderlaufen, wenn unten ein Pick dazukommt
oder sich eine ASIN aendert. Skript ist idempotent: ein vorhandener Block wird
ersetzt, nicht verdoppelt.

Picks mit dem Label "Optional" (Kaufratgeber-Verweise statt Direktkauf, siehe
CLAUDE.md, Abschnitt "Produkt-Picks - Realitaets-Regel") bleiben aussen vor.

Aufruf:  python3 scripts/build-quickbuy.py [--check]
         --check schreibt nichts und meldet nur, ob alle Bloecke aktuell sind.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Wofuer wird eingekauft - steht in der Ueberschrift des Blocks. Bewusst von
# Hand gepflegt: aus dem <h1> abgeleitete Formulierungen klingen auf Deutsch
# regelmaessig schief ("Einkaufsliste fuer Sonntags Family Brunch: planen").
ANLASS = {
    "brunch": "deinen Brunch",
    "casino": "deinen Casino-Abend",
    "gartenparty": "deine Gartenparty",
    "geburtstag": "deinen Geburtstag",
    "grillabend": "deinen Grillabend",
    "hawaii-tiki": "deine Hawaii-Party",
    "jga": "den JGA",
    "mexiko-fiesta": "deine Fiesta",
    "oktoberfest": "deine Wiesn-Party",
    "saison-deko": "die gemuetliche Jahreszeit",
    "spa-abend": "deinen Spa-Abend",
    "spieleabend": "deinen Spieleabend",
    "valentinstag": "eure Date Night",
}

PICK_OPEN_RE = re.compile(r'<div class="pick">')
DIV_RE = re.compile(r'<(/?)div\b')
LABEL_RE = re.compile(r'<span class="label">([^<]*)</span>')
NAME_RE = re.compile(r'<h4>(?P<name>.*?)</h4>', re.S)
HREF_RE = re.compile(r'<a class="cta" href="(?P<href>[^"]+)"')

# Der Start-Marker traegt hinter QUICKBUY:START noch einen Hinweistext, das
# Muster darf also nicht auf "-->" direkt dahinter bestehen - sonst findet es
# den eigenen Block nicht wieder und jeder Lauf haengt einen weiteren an.
# Nachfolgende Leerzeilen werden mitgenommen, damit die Datei nicht waechst.
BLOCK_RE = re.compile(
    r'[ \t]*<!-- QUICKBUY:START\b.*?<!-- QUICKBUY:END -->\n+', re.S)


def pick_bodies(html: str):
    """Der Inhalt jeder .pick-Karte, inklusive verschachtelter <div>.

    Eine nicht-gierige Regex bis zum ersten </div> reicht nicht: Picks mit
    Produktfoto haben innen zwei weitere <div> (.pick-photo/.pick-text) und
    wuerden dann mitten im Bild abgeschnitten - die Karte fiele stumm aus der
    Einkaufsliste heraus (so passiert auf gartenparty: 3 statt 10 Eintraege).
    Deshalb wird ab der Oeffnung mitgezaehlt, bis die Tiefe wieder 0 ist.
    """
    for m in PICK_OPEN_RE.finditer(html):
        depth = 0
        pos = m.start()
        for d in DIV_RE.finditer(html, m.start()):
            depth += -1 if d.group(1) else 1
            if depth == 0:
                yield html[m.end():d.start()]
                break


def picks_of(html: str):
    """Alle Direktkauf-Picks einer Seite als (Name, Amazon-URL)."""
    out = []
    for body in pick_bodies(html):
        label = LABEL_RE.search(body)
        if label and label.group(1).strip().lower().startswith("optional"):
            continue          # Kaufratgeber-Verweis, kein Impulskauf
        name = NAME_RE.search(body)
        href = HREF_RE.search(body)
        if not name or not href:
            continue
        if "amazon.de" not in href.group("href"):
            continue
        clean = re.sub(r"<[^>]+>", "", name.group("name"))
        out.append((" ".join(clean.split()), href.group("href")))
    return out


def render(anlass: str, items) -> str:
    li = "\n".join(
        '            <li><a href="{href}" rel="sponsored nofollow noopener" '
        'target="_blank">{name}</a></li>'.format(href=h, name=n)
        for n, h in items)
    return (
        '        <!-- QUICKBUY:START generiert von scripts/build-quickbuy.py - nicht von Hand aendern -->\n'
        '        <aside class="quickbuy" aria-labelledby="qb-head">\n'
        '          <p class="qb-head" id="qb-head">Die Einkaufsliste für {anlass}</p>\n'
        '          <p class="qb-sub">Alle Empfehlungen dieser Seite auf einen Blick. '
        'Warum genau diese, steht weiter unten bei den Details.</p>\n'
        '          <ul class="qb-list">\n'
        '{li}\n'
        '          </ul>\n'
        '          <p class="qb-note">Affiliate-Links: Kaufst du darüber etwas, bekommen wir '
        'eine kleine Provision. Für dich ändert sich am Preis nichts.</p>\n'
        '        </aside>\n'
        '        <!-- QUICKBUY:END -->\n'
    ).format(anlass=anlass, li=li)


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for slug, anlass in sorted(ANLASS.items()):
        path = ROOT / slug / "index.html"
        if not path.exists():
            print(f"fehlt: {path}")
            return 1
        html = path.read_text(encoding="utf-8")
        items = picks_of(html)
        if not items:
            print(f"{slug}: keine Picks gefunden - uebersprungen")
            continue

        block = render(anlass, items)
        without = BLOCK_RE.sub("", html)
        # Der Block gehoert zwischen Einleitung und erste Kapitel-Ueberschrift.
        # Steht dort schon das Inhaltsverzeichnis (scripts/build-toc.py), muss die
        # Einkaufsliste davor - sonst schieben sich beide Generatoren gegenseitig
        # nach unten und der Konsistenz-Check wird abwechselnd rot.
        pos = without.find("<!-- TOC:START")
        if pos >= 0:
            pos = without.rfind("\n", 0, pos) + 1
        else:
            pos = without.find("        <h2")
        if pos < 0:
            print(f"{slug}: kein <h2> gefunden - uebersprungen")
            return 1
        new = without[:pos] + block + "\n" + without[pos:]

        if new == html:
            continue
        stale.append(slug)
        if not check:
            path.write_text(new, encoding="utf-8")
            print(f"{slug}: {len(items)} Picks in die Einkaufsliste")

    if check:
        if stale:
            print("Nicht aktuell: " + ", ".join(stale))
            print("Beheben mit: python3 scripts/build-quickbuy.py")
            return 1
        print("Alle Einkaufslisten aktuell.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
