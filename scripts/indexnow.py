#!/usr/bin/env python3
"""Meldet alle URLs aus sitemap.xml per IndexNow an Bing, Yandex, Seznam & Co.

Warum: Im Oktober 2026 fand eine Websuche nach site:bethathost.de nur zwei von
rund 45 Seiten. IndexNow braucht kein Konto: Der Schluessel liegt als
/<schluessel>.txt im Wurzelverzeichnis und beweist, dass die Meldung von der
Domain selbst kommt. Bing (und damit DuckDuckGo, Ecosia, ChatGPT-Suche) nimmt
neue und geaenderte Seiten dann meist innerhalb von Tagen auf. Google nutzt
IndexNow nicht - dafuer braucht es die Search Console (siehe web_stats.py).

Aufruf: python3 scripts/indexnow.py  (in CI: .github/workflows/indexnow.yml,
nach jeder Aenderung an sitemap.xml)
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "bethathost.de"


def schluessel():
    kandidaten = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(kandidaten) != 1:
        sys.exit(f"Genau eine IndexNow-Schluesseldatei erwartet, gefunden: {len(kandidaten)}")
    k = kandidaten[0]
    assert k.read_text().strip() == k.stem, "Schluesseldatei muss den Schluessel enthalten"
    return k.stem


def main():
    key = schluessel()
    urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    daten = {"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(daten).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print(f"IndexNow: HTTP {r.status} fuer {len(urls)} URLs")
    except urllib.error.HTTPError as e:
        # 202 = angenommen, Pruefung laeuft; 403 = Schluesseldatei (noch) nicht erreichbar
        print(f"IndexNow: HTTP {e.code} {e.read()[:300]!r}")
        if e.code not in (202,):
            sys.exit(1)


if __name__ == "__main__":
    main()
