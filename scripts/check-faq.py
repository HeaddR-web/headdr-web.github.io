#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft, dass jede ausgezeichnete FAQ auch auf der Seite steht.

Bis September 2026 trugen 16 Seiten ein FAQPage-JSON-LD, dessen Fragen im
Artikel nirgends vorkamen. Google verlangt fuer strukturierte Daten, dass der
ausgezeichnete Inhalt fuer den Besucher sichtbar ist; unsichtbare Auszeichnung
riskiert eine manuelle Massnahme. Schlimmer fuer den Umsatz: Wer die Frage im
Suchergebnis anklickt, landet auf einer Seite ohne die Antwort und ist sofort
wieder weg.

Das Skript baut den sichtbaren Block aus dem JSON-LD neu und vergleicht ihn mit
dem, was in der Datei steht. Damit faellt beides auf:
  * JSON-LD ohne sichtbaren Block (oder mit veraltetem Text)
  * ein sichtbarer FAQ-Block, den kein JSON-LD mehr deckt

Beheben mit: python3 scripts/build-faq.py && python3 scripts/build-toc.py
"""
import glob
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("build_faq", "scripts/build-faq.py")
build_faq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_faq)


def main():
    abweichend = []
    for pfad in sorted(glob.glob("**/*.html", recursive=True)):
        if pfad.startswith("cozy/"):
            continue
        html = open(pfad, encoding="utf-8").read()
        if "FAQPage" not in html and "<!-- FAQ:START" not in html:
            continue
        geaendert, _ = build_faq.verarbeite(pfad, schreiben=False)
        if geaendert:
            fragen = len(build_faq.fragen(html))
            grund = "Fragen stehen nicht im Artikel" if fragen else "Block ohne JSON-LD"
            abweichend.append(f"{pfad}: {grund}")

    if abweichend:
        print("\n".join(abweichend))
        print("Beheben mit: python3 scripts/build-faq.py && python3 scripts/build-toc.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
