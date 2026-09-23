#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut das Inhaltsverzeichnis (<nav class="toc">) jeder laengeren Seite.

Warum: Die Artikel haben vier bis neun Abschnitte, aber der Leser sah beim
Ankommen nur die Einleitung. Wer wissen will, ob die Seite sein Thema ueberhaupt
behandelt ("gibt es hier auch Drinks?"), musste scrollen - mobil die haeufigste
Abbruchstelle. Das Verzeichnis beantwortet das in einem Blick und gibt Google
ausserdem die Sprungmarken fuer Sitelinks im Suchergebnis.

Wie das Quickbuy-Pendant: Der Block steht zwischen <!-- TOC:START --> und
<!-- TOC:END --> und wird bei jedem Lauf komplett ersetzt. Niemals von Hand
bearbeiten.

Zwei Regeln, die hier wichtig sind:
  * Bestehende id-Attribute werden NIE geaendert. Die "cat-*"-Anker stecken in
    den Pinterest-Ziel-URLs (z. B. /casino/?pin=pokerset#cat-pokerset); ein
    umbenannter Anker macht jeden dieser Pins kaputt.
  * Erst ab MIN_ABSCHNITTE Abschnitten lohnt sich ein Verzeichnis. Darunter
    steht es dem Leser nur im Weg.
"""
import glob
import re
import sys

MIN_ABSCHNITTE = 4
AUSGENOMMEN = {
    "index.html", "datenschutz.html", "impressum.html", "privacy.html", "404.html",
    "dashboard.html", "produkt-review.html",
    "cocktailabend/disclosure.html", "girlsnight/disclosure.html",
    "watchparty/disclosure.html",
}

H2_RE = re.compile(r'<h2(?P<attr>[^>]*)>(?P<text>.*?)</h2>', re.S)
ID_RE = re.compile(r'\bid="(?P<id>[^"]+)"')
TAGS_RE = re.compile(r'<[^>]+>')
BLOCK_RE = re.compile(r'[ \t]*<!-- TOC:START.*?<!-- TOC:END -->\n?', re.S)

UMLAUTE = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
           "Ä": "ae", "Ö": "oe", "Ü": "ue", "é": "e", "è": "e", "à": "a"}


def klartext(html):
    """Ueberschriftentext ohne Tags und ohne die fuehrende Nummerierung."""
    t = TAGS_RE.sub("", html)
    t = t.replace("&amp;", "&").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", t).strip()


def slug(text, vergeben):
    s = "".join(UMLAUTE.get(c, c) for c in text).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = "-".join(s.split("-")[:6])[:50].strip("-") or "abschnitt"
    kandidat, n = s, 2
    while kandidat in vergeben:
        kandidat, n = f"{s}-{n}", n + 1
    vergeben.add(kandidat)
    return kandidat


def bereich(html):
    """Start/Ende des Inhaltsbereichs - <main> wenn da, sonst <article>."""
    for auf, zu in (("<main", "</main>"), ("<article", "</article>")):
        a, b = html.find(auf), html.find(zu)
        if a >= 0 and b > a:
            return a, b
    return None, None


def verarbeite(pfad, schreiben=True):
    html = original = open(pfad, encoding="utf-8").read()
    von, bis = bereich(html)
    if von is None:
        return None

    treffer = [m for m in H2_RE.finditer(html, von, bis)
               if "cat-card" not in html[max(0, m.start() - 200):m.start()]]
    if len(treffer) < MIN_ABSCHNITTE:
        return None

    # 1) fehlende id-Attribute ergaenzen, bestehende unangetastet lassen
    vergeben = set(ID_RE.findall(html))
    eintraege = []
    for m in reversed(treffer):
        vorhanden = ID_RE.search(m.group("attr"))
        text = klartext(m.group("text"))
        if vorhanden:
            anker = vorhanden.group("id")
        else:
            anker = slug(text, vergeben)
            neu = f'<h2 id="{anker}"{m.group("attr")}>{m.group("text")}</h2>'
            html = html[:m.start()] + neu + html[m.end():]
        eintraege.append((anker, text))
    eintraege.reverse()

    # 2) Verzeichnis bauen und einsetzen
    einzug = "        "
    zeilen = [f"{einzug}<!-- TOC:START — erzeugt von scripts/build-toc.py, nicht von Hand aendern -->",
              f'{einzug}<nav class="toc" aria-label="Inhalt dieser Seite">',
              f'{einzug}  <p class="toc-title">Auf dieser Seite</p>',
              f"{einzug}  <ol>"]
    for anker, text in eintraege:
        sichtbar = re.sub(r"^\d+\.\s*", "", text).replace("&", "&amp;")
        zeilen.append(f'{einzug}    <li><a href="#{anker}">{sichtbar}</a></li>')
    zeilen += [f"{einzug}  </ol>", f"{einzug}</nav>", f"{einzug}<!-- TOC:END -->"]
    block = "\n".join(zeilen) + "\n"

    if BLOCK_RE.search(html):
        html = BLOCK_RE.sub(lambda _: block, html, count=1)
    else:
        # Direkt unter die Einkaufsliste, wenn es eine gibt - sonst vor das erste
        # Kapitel. Beide Generatoren zielen sonst auf dieselbe Stelle und
        # vertauschen die Bloecke bei jedem Lauf.
        qb = html.find("<!-- QUICKBUY:END -->")
        if qb >= 0:
            zeilenanfang = html.find("\n", qb) + 1
            while html[zeilenanfang:zeilenanfang + 1] == "\n":
                zeilenanfang += 1
            html = html[:zeilenanfang] + block + "\n" + html[zeilenanfang:]
        else:
            erste = H2_RE.search(html, html.find("<main") if "<main" in html
                                 else html.find("<article"))
            zeilenanfang = html.rfind("\n", 0, erste.start()) + 1
            html = html[:zeilenanfang] + block + "\n" + html[zeilenanfang:]

    if schreiben and html != original:
        open(pfad, "w", encoding="utf-8").write(html)
    return len(eintraege), html != original


def main():
    gebaut = geaendert = 0
    for pfad in sorted(glob.glob("**/*.html", recursive=True)):
        if pfad.startswith("cozy/") or pfad in AUSGENOMMEN:
            continue
        ergebnis = verarbeite(pfad)
        if not ergebnis:
            continue
        anzahl, hat_sich_geaendert = ergebnis
        gebaut += 1
        geaendert += bool(hat_sich_geaendert)
        if hat_sich_geaendert:
            print(f"  {pfad}: {anzahl} Abschnitte")
    print(f"\n{gebaut} Seiten mit Inhaltsverzeichnis, {geaendert} geaendert")
    return 0


if __name__ == "__main__":
    sys.exit(main())
