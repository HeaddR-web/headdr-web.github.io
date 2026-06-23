#!/usr/bin/env python3
"""Liest die OpenGraph-/Canonical-Metadaten aus den HTML-Seiten der Website und
schreibt daraus eine pins.json — die Quelle fuer den automatischen Pinterest-Upload.

Bewusst ohne Fremd-Pakete (nur Standardbibliothek), damit es ueberall laeuft.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))


def meta(content, prop):
    """Holt den content-Wert eines <meta property="..."> oder <meta name="...">."""
    for attr in ("property", "name"):
        m = re.search(
            r'<meta[^>]*\b' + attr + r'=["\']' + re.escape(prop) +
            r'["\'][^>]*\bcontent=["\'](.*?)["\']', content, re.I | re.S)
        if m:
            return m.group(1).strip()
    return None


def canonical(content):
    m = re.search(r'<link[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\'](.*?)["\']',
                  content, re.I | re.S)
    return m.group(1).strip() if m else None


def unescape(s):
    if not s:
        return s
    repl = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
            "&#39;": "'", "&#x27;": "'", "&apos;": "'"}
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def clean_title(t):
    """Markenzusatz entfernen, auf Pinterest-Laenge (100) kuerzen."""
    if not t:
        return t
    # Markenzusatz am Ende ODER am Anfang entfernen
    t = re.split(r"\s*[—–|]\s*BeThatHost", t)[0].strip()
    t = re.sub(r"^BeThatHost\s*[—–|:]\s*", "", t).strip()
    return t[:100]


def main():
    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)

    pins = []
    for rel in cfg["pages"]:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print(f"  uebersprungen (fehlt): {rel}", file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()

        title = clean_title(unescape(meta(html, "og:title")))
        desc = unescape(meta(html, "og:description"))
        image = meta(html, "og:image")
        link = canonical(html)

        if not (title and image and link):
            print(f"  uebersprungen (unvollstaendig): {rel}", file=sys.stderr)
            continue

        pins.append({
            "id": rel.replace("/index.html", "").replace("index.html", "home"),
            "title": title,
            "description": (desc or "")[:800],
            "link": link,
            "image": image,
        })

    out = os.path.join(HERE, "pins.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(pins, f, ensure_ascii=False, indent=2)
    print(f"{len(pins)} Pins → {out}")


if __name__ == "__main__":
    main()
