#!/usr/bin/env python3
"""Rendert die Grafik-Pins aus pinterest/grafik-pins.json und fuellt die Queues.

Warum: Im September 2026 war die Pinterest-Queue leer - alle 70 Pins draussen,
der Workflow lief zweimal taeglich ins Leere. Neue Fotos kosten Credits (Canva,
Higgsfield). Rezeptkarten, Checklisten und Ablaufplaene dagegen entstehen aus
dem, was ohnehin auf den Seiten steht, und gehoeren zu den Pin-Formaten, die
auf Pinterest am haeufigsten gemerkt werden.

Was es tut:
  * rendert jede Karte als assets/pins/<site>-<id>.jpg, 1000 x 1500 (2:3,
    Bildformat-Regel), in den Farben und Schriften der Seite. Jede Karte ist ein
    eigenes Motiv (Bild-Eindeutigkeit-Regel).
  * traegt jeden Pin einmal in <site>/pins/queue.json ein - mit eindeutiger
    Ziel-URL (?pin=<id>#<anker>), "kanal": "api" (nicht in feed.xml, sonst
    Doppelpost) und "prio" fuer die Reihenfolge (REIHENFOLGE unten).
    Was schon in der Queue steht, bleibt unangetastet.

Braucht Playwright + Chromium (lokal, nicht in CI):
  python3 scripts/build-pin-grafiken.py [--nur-queue]
"""
import functools
import html
import http.server
import json
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUELLE = ROOT / "pinterest" / "grafik-pins.json"
ZIEL = ROOT / "assets" / "pins"
BASIS = "https://bethathost.de"

# Saisonales zuerst (Wiesn bis 4.10., dann Herbst/Advent), danach im Wechsel,
# damit nie drei Pins derselben Seite hintereinander kommen.
REIHENFOLGE = [
    "oktoberfest-obatzda", "mengenrechner-getraenke", "saison-deko-kalender",
    "oktoberfest-weisswurst", "spieleabend-akte", "casino-vesper",
    "oktoberfest-spiele", "saison-deko-licht", "spa-abend-reihenfolge",
    "mengenrechner-fehler", "oktoberfest-playlist", "jga-aufgaben",
    "casino-chips", "mexiko-fiesta-guacamole", "spieleabend-regeln",
    "saison-deko-kerzen", "hawaii-tiki-maitai", "mengenrechner-eis",
    "jga-survivalkit", "casino-ablauf", "spa-abend-diy", "mexiko-fiesta-margarita",
    "grillabend-marinaden", "jga-ablauf", "mengenrechner-fleisch",
    "hawaii-tiki-bowle", "mexiko-fiesta-tacobar", "grillabend-zonen",
    "hawaii-tiki-luau", "mexiko-fiesta-aguafresca", "grillabend-zeitplan",
    "grillabend-fehler",
]

FARBEN = {
    # Hintergrund, Text, gedaempfter Text, Akzent, Linie
    "nacht":      ("#241f1a", "#fbf6ec", "#cdbfa9", "#d8b46a", "rgba(251,246,236,.18)"),
    "gruen":      ("#29432f", "#fbf6ec", "#c9d4c1", "#e0c07a", "rgba(251,246,236,.18)"),
    "gold":       ("#fbf6ec", "#241f1a", "#7d6d5b", "#a9824a", "rgba(36,31,26,.14)"),
    "terrakotta": ("#b9543f", "#fffaf2", "#f6dccd", "#ffe1a8", "rgba(255,250,242,.25)"),
    "salbei":     ("#e4e8d8", "#241f1a", "#5d6450", "#b9543f", "rgba(36,31,26,.14)"),
    "rosa":       ("#f3dcc3", "#241f1a", "#7a6552", "#963f2e", "rgba(36,31,26,.14)"),
    "blau":       ("#1d3b63", "#ffffff", "#c7d6ea", "#9cc7f0", "rgba(255,255,255,.2)"),
}

VORLAGE = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<style>
html,body{{margin:0;width:1000px;height:1500px;overflow:hidden}}
body{{background:{bg};color:{fg};font-family:"Hanken Grotesk",sans-serif;-webkit-font-smoothing:antialiased}}
.karte{{position:absolute;inset:0;padding:92px 86px 0;display:flex;flex-direction:column}}
.rand{{position:absolute;inset:26px;border:2px solid {linie};border-radius:10px;pointer-events:none}}
.kicker{{font-weight:700;font-size:25px;letter-spacing:.2em;text-transform:uppercase;color:{akzent}}}
h1{{font-family:Fraunces,serif;font-weight:800;font-size:var(--h1,92px);line-height:1.02;letter-spacing:-.02em;margin:24px 0 18px;hyphens:manual}}
.unter{{font-size:33px;color:{mut};margin:0 0 8px;line-height:1.3}}
.strich{{width:120px;height:5px;background:{akzent};margin:34px 0 38px;border-radius:3px}}
.inhalt{{flex:1 1 0;min-height:0;overflow:hidden;font-size:var(--fs,38px);line-height:1.3}}
ul,ol{{list-style:none;margin:0;padding:0}}
li{{padding:.42em 0;border-top:2px solid {linie};display:flex;gap:.6em;align-items:baseline}}
li:first-child{{border-top:none}}
.dot{{flex:0 0 auto;width:.42em;height:.42em;border-radius:50%;background:{akzent};transform:translateY(-.12em)}}
.box{{flex:0 0 auto;font-size:.95em;color:{akzent}}}
.nr{{flex:0 0 1.3em;font-family:Fraunces,serif;font-weight:800;font-size:1.25em;color:{akzent};line-height:1}}
.lbl{{flex:0 0 7.2em;font-weight:700;color:{akzent};font-size:.82em;letter-spacing:.02em}}
.tab li{{justify-content:space-between}}
.tab b{{font-family:Fraunces,serif;font-size:1.12em;white-space:nowrap}}
.blk{{padding:.55em 0;border-top:2px solid {linie}}}
.blk:first-child{{border-top:none;padding-top:0}}
.blk h3{{font-family:Fraunces,serif;font-weight:700;font-size:1.22em;margin:0 0 .18em;color:{fg}}}
.blk p{{margin:0;color:{mut};font-size:.9em;line-height:1.35}}
.fuss{{font-size:29px;font-style:italic;color:{mut};margin:26px 0 0;line-height:1.35}}
.band{{height:170px;flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;border-top:2px solid {linie};margin-top:30px}}
.marke{{font-family:Fraunces,serif;font-weight:800;font-size:44px}}
.marke b{{color:{akzent}}}
.url{{font-size:27px;color:{mut};text-align:right;line-height:1.35}}
.url strong{{color:{fg};font-weight:700}}
</style></head><body>
<div class="rand"></div>
<div class="karte">
  <div class="kicker">{kicker}</div>
  <h1>{titel}</h1>
  {unter}
  <div class="strich"></div>
  <div class="inhalt" id="inhalt">{inhalt}{fuss}</div>
  <div class="band"><div class="marke">Be<b>That</b>Host</div>
  <div class="url">Alles dazu auf<br><strong>{url}</strong></div></div>
</div></body></html>"""


def e(t):
    return html.escape(t, quote=False)


def inhalt(pin):
    art, punkte = pin["art"], pin["punkte"]
    if art == "liste":
        return "<ul>" + "".join(f'<li><span class="dot"></span><span>{e(p)}</span></li>' for p in punkte) + "</ul>"
    if art == "haken":
        return "<ul>" + "".join(f'<li><span class="box">☐</span><span>{e(p)}</span></li>' for p in punkte) + "</ul>"
    if art == "nummern":
        return "<ol>" + "".join(f'<li><span class="nr">{i}</span><span>{e(p)}</span></li>'
                                for i, p in enumerate(punkte, 1)) + "</ol>"
    if art == "schritte":
        teile = [p.split("|", 1) for p in punkte]
        if all(a.strip().isdigit() for a, _ in teile):
            return "<ol>" + "".join(f'<li><span class="nr">{e(a)}</span><span>{e(b)}</span></li>'
                                    for a, b in teile) + "</ol>"
        return "<ul>" + "".join(f'<li><span class="lbl">{e(a)}</span><span>{e(b)}</span></li>'
                                for a, b in teile) + "</ul>"
    if art == "tabelle":
        return '<ul class="tab">' + "".join(
            f'<li><span>{e(a)}</span><b>{e(b)}</b></li>' for a, b in (p.split("|", 1) for p in punkte)) + "</ul>"
    if art == "block":
        return "".join(f'<div class="blk"><h3>{e(a)}</h3><p>{e(b)}</p></div>'
                       for a, b in (p.split("|", 1) for p in punkte))
    raise SystemExit(f"Unbekannte Art: {art}")


def seite_html(pin):
    bg, fg, mut, akzent, linie = FARBEN[pin["farbe"]]
    return VORLAGE.format(
        bg=bg, fg=fg, mut=mut, akzent=akzent, linie=linie,
        kicker=e(pin["kicker"]), titel=e(pin["titel"]),
        unter=f'<p class="unter">{e(pin["unter"])}</p>' if pin.get("unter") else "",
        inhalt=inhalt(pin),
        fuss=f'<p class="fuss">{e(pin["fuss"])}</p>' if pin.get("fuss") else "",
        url=f"bethathost.de/{pin['site']}",
    )


class StillerHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def server():
    handler = functools.partial(StillerHandler, directory=str(ROOT))
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def rendern(pins):
    from playwright.sync_api import sync_playwright
    from PIL import Image

    ZIEL.mkdir(parents=True, exist_ok=True)
    srv = server()
    port = srv.server_address[1]
    # Jede Karte unter eigenem Dateinamen: mit einer gemeinsamen _render.html
    # lieferte der Browser per 304 die vorige Karte aus dem Cache, und 20 von
    # 32 Grafiken zeigten den Inhalt einer anderen.
    tmp = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page(viewport={"width": 1000, "height": 1500})
            for pin in pins:
                tmp = ZIEL / f"_render-{pin['site']}-{pin['id']}.html"
                tmp.write_text(seite_html(pin), encoding="utf-8")
                page.goto(f"http://127.0.0.1:{port}/assets/pins/{tmp.name}")
                page.evaluate("document.fonts.ready")
                # Schrift und Titel so lange verkleinern, bis alles in die Karte passt.
                ok = page.evaluate("""() => {
                  const inh = document.getElementById('inhalt'), r = document.documentElement.style;
                  const passt = () => inh.scrollHeight <= inh.clientHeight + 1 &&
                                      document.querySelector('h1').getBoundingClientRect().height < 420;
                  // Gross anfangen und nur so weit verkleinern, bis alles passt -
                  // auf dem Handy ist eine Pin-Karte rund 180 px breit.
                  let fs = 54, h1 = 120;
                  r.setProperty('--fs', fs + 'px'); r.setProperty('--h1', h1 + 'px');
                  while (!passt() && fs > 26) { fs -= 1; h1 = Math.max(70, h1 - 2);
                    r.setProperty('--fs', fs + 'px'); r.setProperty('--h1', h1 + 'px'); }
                  return passt();
                }""")
                if not ok:
                    raise SystemExit(f"{pin['site']}-{pin['id']}: Inhalt passt nicht auf die Karte - kuerzen")
                png = ZIEL / f"_{pin['site']}-{pin['id']}.png"
                page.screenshot(path=str(png))
                Image.open(png).convert("RGB").save(
                    ZIEL / f"{pin['site']}-{pin['id']}.jpg", "JPEG", quality=86, optimize=True, progressive=True)
                png.unlink()
                tmp.unlink()
                tmp = None
            browser.close()
    finally:
        if tmp:
            tmp.unlink(missing_ok=True)
        srv.shutdown()


def queues_fuellen(pins):
    rang = {k: i for i, k in enumerate(REIHENFOLGE, 1)}
    fehlt = [f"{p['site']}-{p['id']}" for p in pins if f"{p['site']}-{p['id']}" not in rang]
    if fehlt:
        raise SystemExit("Nicht in REIHENFOLGE: " + ", ".join(fehlt))
    neu = 0
    for pin in pins:
        qf = ROOT / pin["site"] / "pins" / "queue.json"
        qf.parent.mkdir(parents=True, exist_ok=True)
        queue = json.loads(qf.read_text(encoding="utf-8")) if qf.exists() else []
        link = f"{BASIS}/{pin['site']}/?pin={pin['id']}#{pin['anker']}"
        if any(q.get("link") == link for q in queue):
            continue
        bild = f"{BASIS}/assets/pins/{pin['site']}-{pin['id']}.jpg"
        if any(q.get("image_url") == bild for q in queue):
            raise SystemExit(f"Bild schon in der Queue, aber mit anderer URL: {bild}")
        queue.append({
            "title": pin["pin_titel"][:100],
            "description": pin["beschreibung"][:800],
            "link": link,
            "image_url": bild,
            "published": False,
            "pin_id": "",
            "kanal": "api",
            "prio": rang[f"{pin['site']}-{pin['id']}"],
        })
        qf.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        neu += 1
    return neu


def pruefen(pins):
    """Ziel-Seite und Anker muessen existieren, sonst landet der Pin im Leeren."""
    for pin in pins:
        datei = ROOT / pin["site"] / "index.html"
        if not datei.exists():
            raise SystemExit(f"Seite fehlt: {datei}")
        if f'id="{pin["anker"]}"' not in datei.read_text(encoding="utf-8"):
            raise SystemExit(f"{pin['site']}: Anker #{pin['anker']} gibt es nicht")
    ids = [f"{p['site']}-{p['id']}" for p in pins]
    doppelt = {i for i in ids if ids.count(i) > 1}
    if doppelt:
        raise SystemExit("Doppelte ids: " + ", ".join(sorted(doppelt)))


def main():
    pins = json.loads(QUELLE.read_text(encoding="utf-8"))["pins"]
    pruefen(pins)
    if "--nur-queue" not in sys.argv:
        rendern(pins)
        print(f"{len(pins)} Grafiken in {ZIEL.relative_to(ROOT)}/")
    print(f"{queues_fuellen(pins)} neue Queue-Eintraege")


if __name__ == "__main__":
    main()
