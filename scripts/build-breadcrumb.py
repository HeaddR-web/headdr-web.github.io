#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut die Brotkrumen-Navigation (<nav class="breadcrumb">) am Artikelanfang.

Warum: Bis September 2026 stand oben auf jeder Seite ein einzelner Rueckwaerts-
Link, und zwar in acht verschiedenen Ausfuehrungen - 19-mal "Alle Anlaesse",
daneben "Zurueck zur Ausstattung", "Zurueck zur Snack-Liste" und vier weitere.
Auf den Unterseiten fehlte die mittlere Ebene ganz: von der Pyjama-Party kam
man zum Maedelsabend, aber der Weg zurueck zur Startseite war unsichtbar.

Dazu kommt der Auftritt in der Suche: Ohne BreadcrumbList zeigt Google unter
dem Titel die nackte URL. Mit ihr steht dort "bethathost.de > Mottopartys >
Casino-Abend" - dieselbe Zeile, die der Leser auch auf der Seite sieht.

Die Zuordnung kommt aus der Startseite selbst: In welchem <section id="..."> die
Karte einer Seite steht, das ist ihre Kategorie. Verschiebt jemand eine Karte
von #anlaesse nach #mottopartys, wandert die Brotkrume beim naechsten Lauf mit -
es gibt keine zweite Liste, die dabei veralten koennte. Der Linktext kommt aus
NAME in build-related.py, damit eine Seite nicht an zwei Stellen anders heisst.

Der Block steht zwischen <!-- BREADCRUMB:START --> und <!-- BREADCRUMB:END -->
und wird bei jedem Lauf komplett ersetzt. Niemals von Hand bearbeiten.

Neue Seite: Karte auf der Startseite ergaenzen und Slug in NAME eintragen
(beides steht ohnehin in CLAUDE.md), dann python3 scripts/build-breadcrumb.py
"""
import glob
import html as H
import importlib.util
import json
import re
import sys

spec = importlib.util.spec_from_file_location("build_related", "scripts/build-related.py")
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)

BASIS = "https://bethathost.de/"
START = "Start"

# Ueberschrift je Startseiten-Abschnitt. Steht eine Karte in einem Abschnitt,
# der hier fehlt, bekommt die Seite bewusst keine Brotkrume.
ABSCHNITTE = {
    "anlaesse": "Anlässe",
    "mottopartys": "Mottopartys",
    "ratgeber": "Kaufratgeber",
}

AUSGENOMMEN = {
    "index.html", "datenschutz.html", "impressum.html", "privacy.html", "404.html",
    "dashboard.html", "produkt-review.html", "ueber-uns.html",
    "cocktailabend/disclosure.html", "girlsnight/disclosure.html",
    "watchparty/disclosure.html",
}

BLOCK_RE = re.compile(r'[ \t]*<!-- BREADCRUMB:START.*?<!-- BREADCRUMB:END -->\n?', re.S)
# Der alte, handgepflegte Einzellink, den dieser Block ersetzt.
ALT_RE = re.compile(r'[ \t]*<a class="backlink"[^>]*>.*?</a>\n?', re.S)
SECTION_RE = re.compile(r'<section id="(?P<id>[^"]+)"(?P<rest>.*?)</section>', re.S)
# Wo die Brotkrume hin darf: Artikelseiten direkt hinter <article> (also ueber
# das Lead-Bild), Hub-Seiten in den Hero-Kasten ueber die Eyebrow-Zeile. Beides
# liegt innerhalb eines Containers - ausserhalb greift kein Seitenrand und die
# Zeile liefe quer ueber den Bildschirm.
EINSTIEG_RE = re.compile(r'<article[^>]*>\n|<div class="hero-inner">\n')
HREF_RE = re.compile(r'href="(?P<ziel>[^"#?]+)')


def norm(ziel):
    """Relatives oder absolutes Linkziel -> Pfad wie in NAME."""
    z = ziel.lstrip("/")
    return z + "index.html" if z.endswith("/") or z == "" else z


def kategorien():
    """{Seitenpfad: (Abschnitts-Anker, Ueberschrift)} aus der Startseite."""
    start = open("index.html", encoding="utf-8").read()
    raus = {}
    for m in SECTION_RE.finditer(start):
        titel = ABSCHNITTE.get(m.group("id"))
        if not titel:
            continue
        for treffer in HREF_RE.finditer(m.group("rest")):
            raus.setdefault(norm(treffer.group("ziel")), (m.group("id"), titel))
    return raus


def pfad_fuer(seite):
    """Die Kette [(Linktext, URL oder None), ...] fuer eine Seite."""
    kat = kategorien()
    if seite not in br.NAME:
        return None

    # Unterseite? Dann haengt sie unter ihrer Hub-Seite.
    hub = seite.rsplit("/", 1)[0].split("/")[0] + "/index.html"
    eltern = [] if hub == seite else ([hub] if hub in br.NAME else [])

    wurzel = eltern[0] if eltern else seite
    if wurzel not in kat:
        return None
    anker, titel = kat[wurzel]

    kette = [(START, "/"), (titel, "/#" + anker)]
    kette += [(br.NAME[p], "/" + p.replace("index.html", "")) for p in eltern]
    kette.append((br.NAME[seite], None))
    return kette


def baue(kette):
    zeilen = [
        "        <!-- BREADCRUMB:START — erzeugt von scripts/build-breadcrumb.py, nicht von Hand aendern -->",
        '        <nav class="breadcrumb" aria-label="Wo du gerade bist">',
    ]
    for text, url in kette:
        sicher = H.escape(text, quote=False)
        if url:
            zeilen.append(f'          <a href="{url}">{sicher}</a>')
        else:
            zeilen.append(f'          <span aria-current="page">{sicher}</span>')
    zeilen.append("        </nav>")

    daten = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": text,
             **({"item": BASIS + url.lstrip("/")} if url else {})}
            for i, (text, url) in enumerate(kette, 1)
        ],
    }
    zeilen.append('        <script type="application/ld+json">')
    zeilen.append("        " + json.dumps(daten, ensure_ascii=False))
    zeilen.append("        </script>")
    zeilen.append("        <!-- BREADCRUMB:END -->")
    return "\n".join(zeilen) + "\n"


def verarbeite(pfad, schreiben=True):
    """(Kettenlaenge, hat_sich_geaendert) - oder None, wenn die Seite draussen bleibt."""
    html = open(pfad, encoding="utf-8").read()
    kette = pfad_fuer(pfad)

    if not kette:
        # Keine Zuordnung: einen alten Block wegraeumen, sonst nichts anfassen.
        ergebnis = BLOCK_RE.sub("", html, count=1)
        if ergebnis != html and schreiben:
            open(pfad, "w", encoding="utf-8").write(ergebnis)
        return None

    # Der alte Block und der handgepflegte Einzellink, den er ersetzt, kommen weg.
    rest = ALT_RE.sub("", BLOCK_RE.sub("", html, count=1), count=1)
    m = re.search(EINSTIEG_RE, rest)
    if not m:
        sys.exit(f"{pfad}: keine Stelle fuer die Brotkrume gefunden")
    ergebnis = rest[:m.end()] + baue(kette) + rest[m.end():]

    geaendert = ergebnis != html
    if geaendert and schreiben:
        open(pfad, "w", encoding="utf-8").write(ergebnis)
    return len(kette), geaendert


def main():
    gebaut = geaendert = 0
    for pfad in sorted(glob.glob("**/*.html", recursive=True)):
        if pfad.startswith("cozy/") or pfad in AUSGENOMMEN:
            continue
        ergebnis = verarbeite(pfad)
        if not ergebnis:
            continue
        _, hat = ergebnis
        gebaut += 1
        geaendert += bool(hat)
        if hat:
            print("  aktualisiert:", pfad)
    print(f"{gebaut} Brotkrumen, davon {geaendert} geaendert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
