#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft, dass keine Seite beim Aufruf etwas von einem fremden Host laedt.

Jeder solche Abruf schickt die Besucher-IP ohne Einwilligung an den fremden
Server, genau wie frueher der Google-Fonts-Link (DSGVO Art. 6, vgl. LG Muenchen I,
Urt. v. 20.01.2022, Az. 3 O 17493/20). Bis September 2026 zog cozy/style.css sein
Hero-Bild direkt vom Higgsfield-CDN (cloudfront.net). Eine grep-Zeile hat dafuer
nicht gereicht: <link rel="stylesheet">, srcset-Kandidaten, Grossschreibung,
unquotierte Werte und mehrzeiliges CSS rutschten durch.

Geprueft wird, was der Browser von selbst abruft:
- HTML: src, srcset, poster, data (object), <link> mit ladendem rel,
  <base href>, SVG-href, style-Attribute und <style>-Bloecke, Inline-Skripte
  und on*-Attribute, eingebettetes HTML in iframe srcdoc
- CSS: url(), @import, image-set()
- JS: absolute URLs in String-Literalen (Heuristik, siehe JS_ERLAUBT)

Gilt auch fuer Cozylore: die DSGVO kennt keine Marke.

Geprueft wird der Repo-Ordner, egal aus welchem Verzeichnis das Skript startet.
Ein anderer Ordner geht als Argument (fuer Testdateien).

Einzige Ausnahme ist der Cloudflare-Beacon, bewusst so entschieden und in
datenschutz.html Punkt 9 begruendet. AdSense und Pinterest duerfen nur aus
js/consent.js kommen, das sie erst nach dem Opt-in nachlaedt (Punkt 7 im
Konsistenz-Check haelt sie aus dem Markup).
"""
import glob
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit

EIGENE = {"bethathost.de", "www.bethathost.de"}
ERLAUBT = EIGENE | {"static.cloudflareinsights.com"}
# In JS stehen auch reine Link-Ziele (Affiliate-Links). Die loesen keinen Abruf
# aus, solange niemand klickt. Kommt ein neues Link-Ziel dazu, hier eintragen.
JS_ERLAUBT = ERLAUBT | {"www.amazon.de"}
# Erst nach Einwilligung nachgeladen, deshalb nur in dieser einen Datei erlaubt.
NACH_OPT_IN = {"js/consent.js": {"pagead2.googlesyndication.com", "assets.pinterest.com"}}

LADENDE_REL = {"stylesheet", "preload", "modulepreload", "prefetch", "preconnect",
               "dns-prefetch", "icon", "apple-touch-icon", "manifest", "mask-icon"}

CSS_KOMMENTAR = re.compile(r"/\*.*?\*/", re.S)
CSS_URL = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)]*?))\s*\)", re.S | re.I)
CSS_IMPORT = re.compile(r"@import\s+(?:\"([^\"]*)\"|'([^']*)')", re.I)
CSS_IMAGE_SET = re.compile(r"image-set\(", re.I)
CSS_STRING = re.compile(r"\"([^\"]*)\"|'([^']*)'")
JS_STRING = re.compile(r"[\"'`]((?:https?:)?//[^\"'`\s]+)", re.I)


def fremd(url, erlaubt=ERLAUBT):
    """Host zurueckgeben, wenn die URL absolut ist und nicht auf eine erlaubte Adresse zeigt."""
    u = url.strip()
    if u.lower().startswith(("http://", "https://")):
        host = urlsplit(u).hostname
    elif u.startswith("//"):
        host = urlsplit("https:" + u).hostname
    else:
        return None
    return host if host and host not in erlaubt else None


def css_ziele(text):
    text = CSS_KOMMENTAR.sub("", text)
    for m in CSS_URL.finditer(text):
        ziel = next(g for g in m.groups() if g is not None)
        if not ziel.strip().lower().startswith("data:"):
            yield ziel
    for m in CSS_IMPORT.finditer(text):
        yield m.group(1) if m.group(1) is not None else m.group(2)
    # image-set() kann url() enthalten, deshalb bis zur passenden Klammer lesen
    for m in CSS_IMAGE_SET.finditer(text):
        tiefe, ende = 1, m.end()
        while ende < len(text) and tiefe:
            tiefe += {"(": 1, ")": -1}.get(text[ende], 0)
            ende += 1
        for s in CSS_STRING.finditer(text[m.end():ende]):
            yield s.group(1) if s.group(1) is not None else s.group(2)


def js_ziele(text):
    for m in JS_STRING.finditer(text):
        yield m.group(1)


class Seite(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.funde = []      # (host, wie)
        self._in = None      # "style" oder "script" (nur Inline-Skripte)

    def _pruefe(self, url, wie, erlaubt=ERLAUBT):
        host = fremd(url, erlaubt)
        if host:
            self.funde.append((host, wie))

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        for name in ("src", "poster"):
            if name in a:
                self._pruefe(a[name], f"<{tag} {name}>")
        for name in ("srcset", "imagesrcset"):
            for kandidat in a.get(name, "").split(","):
                if kandidat.strip():
                    self._pruefe(kandidat.split()[0], f"<{tag} {name}>")
        if tag == "object" and "data" in a:
            self._pruefe(a["data"], "<object data>")
        # ein fremdes base macht jede relative Adresse der Seite fremd
        if tag == "base" and "href" in a:
            self._pruefe(a["href"], "<base href>")
        if "srcdoc" in a:
            innen = Seite()
            innen.feed(a["srcdoc"])
            innen.close()
            self.funde += [(host, f"<{tag} srcdoc> {wie}") for host, wie in innen.funde]
        if tag == "link" and LADENDE_REL & set(a.get("rel", "").lower().split()):
            self._pruefe(a.get("href", ""), f"<link rel={a['rel']}>")
        if tag in ("image", "use", "feimage"):
            for name in ("href", "xlink:href"):
                if name in a:
                    self._pruefe(a[name], f"<{tag} {name}>")
        if "style" in a:
            for ziel in css_ziele(a["style"]):
                self._pruefe(ziel, "style-Attribut")
        for name, wert in a.items():
            if name.startswith("on"):
                for ziel in js_ziele(wert):
                    self._pruefe(ziel, f"{name}-Attribut", JS_ERLAUBT)
        if tag == "style":
            self._in = "style"
        elif tag == "script" and "src" not in a and "json" not in a.get("type", "").lower():
            self._in = "script"

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._in = None

    def handle_data(self, data):
        if self._in == "style":
            for ziel in css_ziele(data):
                self._pruefe(ziel, "<style>")
        elif self._in == "script":
            for ziel in js_ziele(data):
                self._pruefe(ziel, "Inline-Skript", JS_ERLAUBT)


def dateien(muster):
    for f in sorted(glob.glob(muster, recursive=True)):
        teile = f.split(os.sep)
        if ".git" in teile or "node_modules" in teile:
            continue
        yield f


def main():
    wurzel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    os.chdir(wurzel)
    funde = []
    n = {"html": 0, "css": 0, "js": 0}
    for f in dateien("**/*.html"):
        n["html"] += 1
        p = Seite()
        with open(f, encoding="utf-8", errors="replace") as fh:
            p.feed(fh.read())
        p.close()
        funde += [(f, host, wie) for host, wie in p.funde]
    for f in dateien("**/*.css"):
        n["css"] += 1
        with open(f, encoding="utf-8", errors="replace") as fh:
            funde += [(f, h, "CSS") for h in (fremd(z) for z in css_ziele(fh.read())) if h]
    for f in dateien("**/*.js"):
        n["js"] += 1
        erlaubt = JS_ERLAUBT | NACH_OPT_IN.get(f.replace(os.sep, "/"), set())
        with open(f, encoding="utf-8", errors="replace") as fh:
            funde += [(f, h, "JS-String") for h in (fremd(z, erlaubt) for z in js_ziele(fh.read())) if h]

    if funde:
        for f, host, wie in sorted(set(funde)):
            print(f"{f}: {host} ({wie})")
        print("Datei ins Repo legen (Bilder nach /assets/img/) und lokal verlinken. "
              "Nur ein Link-Ziel in JS? Dann den Host in JS_ERLAUBT eintragen.")
        return 1
    print(f"keine Fremd-Hosts ({n['html']} HTML, {n['css']} CSS, {n['js']} JS geprueft)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
