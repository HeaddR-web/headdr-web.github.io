#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut den Weiterlesen-Block (<nav class="related">) am Ende jeder Seite.

Warum: Gemessen im September 2026 verlinkte kein Artikel auf neun der Seiten -
brunch, casino, geburtstag, oktoberfest, saison-deko, ueber-uns und drei
Mädelsabend-Guides waren nur über die Startseite erreichbar. Vier Seiten hatten
gar keinen ausgehenden Link: wer dort ankam, hatte als einzigen Weg weiter den
Zurück-Button. Die handgemachten "Weitere Anlässe"-Absätze gab es nur auf zehn
Seiten und sie zeigten fast alle auf dieselben zwei Ziele (girlsnight,
cocktailabend), was den Rest der Seite verhungern liess.

Wie es funktioniert: Jede Seite gehoert zu einem THEMA. Innerhalb eines Themas
bilden die Seiten einen Ring - jede verlinkt auf die beiden naechsten. Ein Ring
kann per Konstruktion keine Waise enthalten: wer ausgehende Links hat, hat auch
eingehende. Dazu kommt ein dritter Link in das PARTNER-Thema, reihum, damit die
Ringe nicht voneinander abgeschnitten sind (sonst landet ein Leser im Ratgeber
nie wieder bei einem Anlass).

Der Block steht zwischen <!-- RELATED:START --> und <!-- RELATED:END --> und
wird bei jedem Lauf komplett ersetzt. Niemals von Hand bearbeiten.

Neue Seite: Slug in NAME und in das passende THEMA eintragen, sonst bekommt sie
weder Block noch eingehende Links.
"""
import re
import sys
from pathlib import Path

# Kurzer Linktext je Seite. Die <h1> taugen nicht: "Mädelsabend zu Hause mit
# kleinem Budget: 20 günstige Ideen mit Spaßgarantie" sprengt jede Kachel.
NAME = {
    "brunch/index.html": "Sonntags-Brunch",
    "casino/index.html": "Casino-Abend",
    "gartenparty/index.html": "Gartenparty",
    "geburtstag/index.html": "Geburtstag zuhause",
    "grillabend/index.html": "Grillabend",
    "jga/index.html": "JGA",
    "saison-deko/index.html": "Saison-Deko",
    "spa-abend/index.html": "Spa-Abend",
    "spieleabend/index.html": "Spieleabend",
    "valentinstag/index.html": "Valentinstag",

    "hawaii-tiki/index.html": "Hawaii-Party",
    "mexiko-fiesta/index.html": "Mexiko-Fiesta",
    "oktoberfest/index.html": "Oktoberfest zuhause",

    "girlsnight/index.html": "Mädelsabend",
    "girlsnight/posts/girls-night-budget.html": "Mädelsabend mit kleinem Budget",
    "girlsnight/posts/girls-night-drinks.html": "Drinks für den Mädelsabend",
    "girlsnight/posts/girls-night-galentines.html": "Galentine's Day",
    "girlsnight/posts/girls-night-games.html": "Mädelsabend-Spiele",
    "girlsnight/posts/girls-night-movie-night.html": "Filmabend mit den Girls",
    "girlsnight/posts/girls-night-pamper-spa.html": "Pflege- & Spa-Abend",
    "girlsnight/posts/girls-night-snacks.html": "Snacks & Grazing-Board",
    "girlsnight/posts/girls-night-themes.html": "Mädelsabend-Mottos",
    "girlsnight/posts/pyjama-party.html": "Pyjama-Party",
    "girlsnight/posts/wine-tasting-girls.html": "Wine Tasting",

    "cocktailabend/index.html": "Cocktailabend",
    "cocktailabend/posts/cocktailabend-zuhause.html": "Cocktailabend zuhause planen",
    "cocktailabend/posts/signature-cocktails-vorbereiten.html": "Signature-Cocktails vorbereiten",

    "watchparty/index.html": "WM-Party",
    "watchparty/posts/world-cup-watch-party.html": "WM-Party planen",
    "watchparty/posts/wm-snacks-rezepte.html": "WM-Snacks",
    "watchparty/posts/wm-spiel-heute-abend.html": "Spontane Mini-Party",

    "ratgeber/bluetooth-lautsprecher-garten.html": "Bluetooth-Lautsprecher",
    "ratgeber/cocktail-shaker-set.html": "Cocktail-Shaker-Set",
    "ratgeber/mini-beamer-filmabend.html": "Mini-Beamer",
    "ratgeber/outdoor-lichterkette.html": "Outdoor-Lichterkette",
    "ratgeber/raclette-fondue-set.html": "Raclette & Fondue",
}

# Reihenfolge im Ring = Reihenfolge hier. Thematisch benachbarte Seiten sollten
# beieinander stehen, dann passen die Vorschlaege inhaltlich zueinander.
THEMA = {
    "anlaesse": [
        "brunch/index.html", "gartenparty/index.html", "grillabend/index.html",
        "geburtstag/index.html", "spieleabend/index.html", "casino/index.html",
        "spa-abend/index.html", "valentinstag/index.html",
        "saison-deko/index.html", "jga/index.html",
    ],
    "mottos": [
        "hawaii-tiki/index.html", "mexiko-fiesta/index.html",
        "oktoberfest/index.html",
    ],
    "girlsnight": [
        "girlsnight/index.html",
        "girlsnight/posts/girls-night-themes.html",
        "girlsnight/posts/girls-night-games.html",
        "girlsnight/posts/girls-night-snacks.html",
        "girlsnight/posts/girls-night-drinks.html",
        "girlsnight/posts/wine-tasting-girls.html",
        "girlsnight/posts/girls-night-movie-night.html",
        "girlsnight/posts/girls-night-pamper-spa.html",
        "girlsnight/posts/pyjama-party.html",
        "girlsnight/posts/girls-night-galentines.html",
        "girlsnight/posts/girls-night-budget.html",
    ],
    "cocktail": [
        "cocktailabend/index.html",
        "cocktailabend/posts/cocktailabend-zuhause.html",
        "cocktailabend/posts/signature-cocktails-vorbereiten.html",
    ],
    "watchparty": [
        "watchparty/index.html",
        "watchparty/posts/world-cup-watch-party.html",
        "watchparty/posts/wm-snacks-rezepte.html",
        "watchparty/posts/wm-spiel-heute-abend.html",
    ],
    "ratgeber": [
        "ratgeber/outdoor-lichterkette.html",
        "ratgeber/bluetooth-lautsprecher-garten.html",
        "ratgeber/mini-beamer-filmabend.html",
        "ratgeber/cocktail-shaker-set.html",
        "ratgeber/raclette-fondue-set.html",
    ],
}

# Wohin der dritte Link zeigt. Die Kette laeuft im Kreis, damit von jedem Thema
# aus jedes andere in wenigen Klicks erreichbar bleibt.
PARTNER = {
    "anlaesse": "girlsnight",
    "girlsnight": "cocktail",
    "cocktail": "ratgeber",
    "ratgeber": "watchparty",
    "watchparty": "mottos",
    "mottos": "anlaesse",
}

BLOCK_RE = re.compile(r'[ \t]*<!-- RELATED:START.*?<!-- RELATED:END -->\n?', re.S)
# Die handgemachten Vorgaenger: <p>Weitere Anlaesse: ... </p>
ALT_RE = re.compile(r'[ \t]*<p>\s*Weitere Anlässe:.*?</p>\n?', re.S)


def url(pfad):
    """Absoluter Pfad, Ordnerseiten ohne index.html."""
    return "/" + (pfad[:-len("index.html")] if pfad.endswith("index.html") else pfad)


def ziele():
    """Pro Seite drei Ziele: zwei aus dem eigenen Ring, eins beim Partner."""
    plan = {}
    for thema, seiten in THEMA.items():
        partner = THEMA[PARTNER[thema]]
        for i, seite in enumerate(seiten):
            nachbarn = [seiten[(i + n) % len(seiten)] for n in (1, 2)]
            nachbarn = [z for z in nachbarn if z != seite]
            plan[seite] = nachbarn + [partner[i % len(partner)]]
    return plan


def block_fuer(ziel_liste):
    e = "        "
    zeilen = [f"{e}<!-- RELATED:START — erzeugt von scripts/build-related.py, nicht von Hand aendern -->",
              f'{e}<nav class="related" aria-labelledby="rel-head">',
              f'{e}  <p class="rel-head" id="rel-head">Das passt auch dazu</p>',
              f"{e}  <ul>"]
    for z in ziel_liste:
        zeilen.append(f'{e}    <li><a href="{url(z)}">{NAME[z]}</a></li>')
    zeilen += [f'{e}    <li><a href="/">Alle Anlässe</a></li>',
               f"{e}  </ul>", f"{e}</nav>", f"{e}<!-- RELATED:END -->"]
    return "\n".join(zeilen) + "\n"


def main():
    unbekannt = [s for gruppe in THEMA.values() for s in gruppe if s not in NAME]
    if unbekannt:
        print("ohne Namen in NAME: " + ", ".join(unbekannt))
        return 1

    plan = ziele()
    geaendert = 0
    for seite, ziel_liste in sorted(plan.items()):
        pfad = Path(seite)
        if not pfad.exists():
            print(f"fehlt: {seite}")
            return 1
        html = original = pfad.read_text(encoding="utf-8")
        html = ALT_RE.sub("", html)
        block = block_fuer(ziel_liste)

        if BLOCK_RE.search(html):
            html = BLOCK_RE.sub(lambda _: block, html, count=1)
        else:
            # Ans Ende des Inhaltsbereichs, vor </main> bzw. </article>.
            for schluss in ("</main>", "</article>"):
                pos = html.rfind(schluss)
                if pos >= 0:
                    break
            else:
                print(f"{seite}: kein </main> oder </article> gefunden")
                return 1
            zeilenanfang = html.rfind("\n", 0, pos) + 1
            html = html[:zeilenanfang] + block + html[zeilenanfang:]

        if html != original:
            pfad.write_text(html, encoding="utf-8")
            geaendert += 1
            print(f"  {seite}")

    print(f"\n{len(plan)} Seiten verlinkt, {geaendert} geaendert")
    return 0


if __name__ == "__main__":
    sys.exit(main())
