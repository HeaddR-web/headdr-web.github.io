#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Werbeplaetze (<div class="ad-slot">) aller BeThatHost-Seiten.

Zwei Dinge koennen hier schiefgehen, beide waren schon da:

1. Der Platz fehlt. Im September 2026 hatte genau eine von 46 Seiten einen
   Werbeplatz (oktoberfest/); auf allen anderen Seiten konnte AdSense nichts
   ausliefern, egal wie viele Leser kamen.

2. Der Platz ist nicht leer. Genau ein <div class="ad-slot"></div> gehoert in
   die Seite - befuellt wird er erst von js/consent.js nach der Einwilligung.
   Steht dort Text im Quelltext (frueher "Werbeplatz - im Artikel (responsiv).
   Erscheint, sobald AdSense aktiv ist."), sieht jeder Besucher dauerhaft einen
   Kasten mit einer Baustellen-Notiz darin, weil .ad-slot:empty dann nicht mehr
   greift.

Rechtstexte, Offenlegungsseiten und die internen Werkzeuge stehen bewusst ohne
Werbeplatz: Werbung neben der Affiliate-Offenlegung oder der Anbieterkennung
untergraebt genau das Vertrauenssignal, fuer das die Seiten da sind.
"""
import glob
import re
import sys

OHNE_WERBUNG = {
    "datenschutz.html": "Rechtstext",
    "impressum.html": "Rechtstext",
    "privacy.html": "Rechtstext",
    "404.html": "Fehlerseite (noindex, nur Wegweiser)",
    "dashboard.html": "internes Werkzeug",
    "produkt-review.html": "internes Werkzeug",
    "cocktailabend/disclosure.html": "Affiliate-Offenlegung",
    "girlsnight/disclosure.html": "Affiliate-Offenlegung",
    "watchparty/disclosure.html": "Affiliate-Offenlegung",
}

SLOT_RE = re.compile(r'<div class="ad-slot[^"]*">(.*?)</div>', re.S)


def main():
    funde = []
    for pfad in sorted(glob.glob("**/*.html", recursive=True)):
        if pfad.startswith("cozy/"):
            continue

        slots = SLOT_RE.findall(open(pfad, encoding="utf-8").read())

        if pfad in OHNE_WERBUNG:
            if slots:
                funde.append(f"{pfad}: Werbeplatz auf einer Seite ohne Werbung "
                             f"({OHNE_WERBUNG[pfad]})")
            continue

        if not slots:
            funde.append(f"{pfad}: kein Werbeplatz (<div class=\"ad-slot\"></div> fehlt)")
        elif len(slots) > 1:
            funde.append(f"{pfad}: {len(slots)} Werbeplaetze, genau einer gehoert hin")
        elif slots[0].strip():
            funde.append(f"{pfad}: Werbeplatz ist im Quelltext nicht leer "
                         f"(\"{slots[0].strip()[:60]}\") - er muss leer bleiben, "
                         f"sonst steht der Kasten dauerhaft im Text")

    for f in funde:
        print(f"  ✗ {f}")
    return 1 if funde else 0


if __name__ == "__main__":
    sys.exit(main())
