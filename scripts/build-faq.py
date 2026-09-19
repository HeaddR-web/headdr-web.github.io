#!/usr/bin/env python3
"""Macht den FAQ-Abschnitt aus den Structured Data sichtbar.

Bis September 2026 trugen 16 Seiten ein FAQPage-JSON-LD mit zwei bis drei
Fragen, die im Artikel nirgends vorkamen. Das ist zum einen ein Verstoss gegen
Googles Richtlinie fuer strukturierte Daten (der ausgezeichnete Inhalt muss fuer
den Besucher sichtbar sein), zum anderen schickt es jeden, der die Frage im
Suchergebnis anklickt, auf eine Seite ohne die Antwort - der teuerste Absprung,
den es gibt.

Das JSON-LD ist die Quelle, der sichtbare Block die Ausgabe: Was hier steht,
steht damit garantiert auch auf der Seite. Der Block liegt zwischen
<!-- FAQ:START ... --> und <!-- FAQ:END --> und wird bei jedem Lauf komplett
ersetzt - niemals von Hand bearbeiten.

Nach jeder Aenderung am FAQPage-JSON-LD:  python3 scripts/build-faq.py
Danach immer scripts/build-toc.py, damit das Verzeichnis die neue
Ueberschrift kennt.
"""
import glob
import html as H
import json
import re
import sys

ANKER = "haeufige-fragen"
UEBERSCHRIFT = "Häufige Fragen"

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
BLOCK_RE = re.compile(r'[ \t]*<!-- FAQ:START.*?<!-- FAQ:END -->\n?', re.S)
# Der handgeschriebene Abschnitt der Hub-Seiten, damit er nicht doppelt steht.
ALT_RE = re.compile(r'[ \t]*<section class="faq">.*?</section>\n?', re.S)


def fragen(html):
    """Alle Frage/Antwort-Paare aus dem FAQPage-JSON-LD der Seite."""
    raus = []
    for m in JSONLD_RE.finditer(html):
        try:
            daten = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        for obj in daten if isinstance(daten, list) else [daten]:
            if not isinstance(obj, dict) or obj.get("@type") != "FAQPage":
                continue
            for eintrag in obj.get("mainEntity", []):
                frage = eintrag.get("name", "").strip()
                antwort = (eintrag.get("acceptedAnswer") or {}).get("text", "").strip()
                if frage and antwort:
                    raus.append((frage, antwort))
    return raus


def baue(paare):
    zeilen = [
        "        <!-- FAQ:START — erzeugt von scripts/build-faq.py aus dem FAQPage-JSON-LD, nicht von Hand aendern -->",
        '        <section class="faq">',
        f'          <h2 id="{ANKER}">{UEBERSCHRIFT}</h2>',
    ]
    for frage, antwort in paare:
        zeilen.append(f"          <h3>{H.escape(frage, quote=False)}</h3>")
        zeilen.append(f"          <p>{H.escape(antwort, quote=False)}</p>")
    zeilen.append("        </section>")
    zeilen.append("        <!-- FAQ:END -->")
    return "\n".join(zeilen) + "\n"


def verarbeite(pfad, schreiben=True):
    html = open(pfad, encoding="utf-8").read()
    paare = fragen(html)
    ohne = BLOCK_RE.sub("", html)
    if not paare:
        # Kein FAQPage-JSON-LD mehr: ein alter Block muss weg, sonst behauptet
        # die Seite weiter etwas, das die Structured Data nicht mehr decken.
        if ohne != html and schreiben:
            open(pfad, "w", encoding="utf-8").write(ohne)
        return ohne != html, ohne

    ohne = ALT_RE.sub("", ohne)
    block = baue(paare)

    ende = ohne.rfind("</article>")
    if ende < 0:
        ende = ohne.rfind("</main>")
    if ende < 0:
        print(f"{pfad}: weder </article> noch </main> - uebersprungen")
        return False, html
    zeilenanfang = ohne.rfind("\n", 0, ende) + 1
    neu = ohne[:zeilenanfang] + block + ohne[zeilenanfang:]

    if neu != html and schreiben:
        open(pfad, "w", encoding="utf-8").write(neu)
    return neu != html, neu


def seiten():
    return [f for f in sorted(glob.glob("**/*.html", recursive=True))
            if not f.startswith("cozy/")]


def main():
    mit = geaendert = 0
    for pfad in seiten():
        if "FAQPage" not in open(pfad, encoding="utf-8").read():
            continue
        mit += 1
        aend, _ = verarbeite(pfad)
        if aend:
            geaendert += 1
            print(f"  {pfad}")
    print(f"\n{mit} Seiten mit FAQ, {geaendert} geaendert")
    return 0


if __name__ == "__main__":
    sys.exit(main())
