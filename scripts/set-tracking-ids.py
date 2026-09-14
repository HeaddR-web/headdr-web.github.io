#!/usr/bin/env python3
"""Setzt je Seitenordner die passende Amazon-Tracking-ID in alle Affiliate-Links.

Warum: PartnerNet berichtet Klicks und Verkaeufe pro Tracking-ID. Mit einer
einzigen ID fuer die ganze Seite laesst sich nicht sagen, ob die 60.000
Aufrufe auf einer Seite haengen, die nie klickt, oder sich gleichmaessig
verteilen. Mit einer ID je Ordner steht das direkt im PartnerNet-Bericht -
ohne eigenes Tracking, ohne Cookies, ohne Einwilligungspflicht.

Die Zuordnung steht in scripts/tracking-ids.json. Dort ist auch beschrieben,
wie die IDs im PartnerNet angelegt werden - das muss vorher passieren, sonst
verfaellt die Provision.

Aufruf:  python3 scripts/set-tracking-ids.py [--check]
         --check schreibt nichts und meldet nur Abweichungen.

Danach immer scripts/build-quickbuy.py laufen lassen, damit die
Einkaufslisten dieselben Tags tragen.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "tracking-ids.json"

# Nur das tag=-Argument innerhalb eines amazon.de-Links, nichts anderes.
LINK_RE = re.compile(r'https://www\.amazon\.de/[^"\s]*')
TAG_RE = re.compile(r'(?<=[?&])tag=[A-Za-z0-9._-]+')

# cozy/** ist abgekoppelt und wird nicht angefasst (siehe CLAUDE.md).
SKIP_DIRS = {"cozy", ".git", "assets", "scripts", "pinterest", ".github"}


def target_id(path: Path, mapping: dict, default: str) -> str:
    """Welche ID gehoert an eine Datei? Bestimmt vom obersten Ordner."""
    rel = path.relative_to(ROOT)
    top = rel.parts[0] if len(rel.parts) > 1 else ""
    return mapping.get(top, default)


def main() -> int:
    check = "--check" in sys.argv
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    default = cfg["standard"]
    mapping = cfg["seiten"]

    changed, wrong = [], []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        html = path.read_text(encoding="utf-8")
        if "amazon.de" not in html:
            continue
        want = target_id(path, mapping, default)

        def fix(m):
            link = m.group(0)
            if "tag=" not in link:
                return link          # untagged Beleglink (z. B. Datenschutz)
            return TAG_RE.sub("tag=" + want, link)

        new = LINK_RE.sub(fix, html)
        if new == html:
            continue
        if check:
            wrong.append(str(rel))
        else:
            path.write_text(new, encoding="utf-8")
            changed.append(str(rel))

    if check:
        if wrong:
            print("Falsche Tracking-ID in:")
            for w in wrong:
                print("  " + w)
            print("Beheben mit: python3 scripts/set-tracking-ids.py")
            return 1
        print("Alle Affiliate-Links tragen die vorgesehene Tracking-ID.")
        return 0

    if changed:
        for c in changed:
            print("angepasst: " + c)
        print("\nNicht vergessen: python3 scripts/build-quickbuy.py")
    else:
        print("Nichts zu tun - alle Links tragen bereits die vorgesehene ID.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
