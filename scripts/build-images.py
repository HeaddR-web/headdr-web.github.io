#!/usr/bin/env python3
"""Kachelbilder in Anzeigegroesse erzeugen und im Markup verlinken.

Die Kategorie-Kacheln (Startseite: a.occ-media img, Hubs: div.cover und div.thumb) zeigen ein
Bild von rund 360 x 270 CSS-Pixeln. Ausgeliefert wurden bis September 2026 die
Originale mit 1264 x 848 bis 1600 x 2385 Pixeln - beim girlsnight-Hub 2,5 MB
allein an Kacheln, gemessener LCP 6,2 s auf gedrosseltem Mobilfunk (Schwelle
2,5 s). Die Originale bleiben unangetastet: 29 von ihnen sind zugleich og:image
oder Lead-Bild, ein Verkleinern an Ort und Stelle wuerde die Social-Vorschauen
zerstoeren.

Deshalb liegen daneben Ableitungen in /assets/img/kachel/<stamm>-<breite>.jpg.
Zuschnitt ist ein zentrierter 4:3-Ausschnitt - genau das, was object-fit:cover
bzw. background-size:cover ohnehin aus dem Original machen (beide zentrieren,
und ein zentrierter Zuschnitt auf 4:3 mit anschliessendem Zuschnitt auf das
Kachel-Format ergibt dasselbe Bild wie ein Zuschnitt direkt aus dem Original).
Sichtbar aendert sich also nichts, nur die uebertragene Datenmenge.

Der Dateiname der Ableitung traegt den Stamm des Originals. Deshalb findet das
Skript das Original auch dann wieder, wenn im Markup laengst die Ableitung
steht - der Lauf ist beliebig oft wiederholbar.

Aufruf: python3 scripts/build-images.py [--pruefen]
"""
import os
import re
import sys

from PIL import Image

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL_DIR = "assets/img"
KACHEL_DIR = "assets/img/kachel"
HERO_DIR = "assets/img/hero"
BREITEN = (480, 960)
SEITE = (4, 3)
# Die 1x-Stufe wird Pixel fuer Pixel gezeigt und bleibt scharf; die 2x-Stufe und
# das Hero-Bild werden immer verkleinert dargestellt, da faellt weniger Qualitaet
# nicht auf - spart aber rund ein Drittel der Bytes.
QUALITAET = 80
QUALITAET_KLEIN = 72
HERO_BREITE = 1280
SIZES = "(max-width: 860px) 100vw, 46vw"
SIZES_KACHEL = "(max-width: 700px) 100vw, 360px"

OCC_RE = re.compile(r'<a class="occ-media"[^>]*>.*?</a>', re.S)
IMG_RE = re.compile(r'<img\s[^>]*?/?>', re.S)
ATTR_RE = re.compile(r'(\w[\w-]*)="([^"]*)"')
KACHEL_RE = re.compile(
    r'<div class="(?P<klasse>cover|thumb)"(?: style="(?P<stil>[^"]*)")?>(?P<inhalt>.*?)</div>',
    re.S,
)
PFAD_RE = re.compile(r'/assets/img/(?:kachel/|hero/)?(?P<stamm>[^"\'/]+?)(?:-\d+)?\.jpg')


def stamm_aus(pfad):
    """Stamm des Originals - egal ob Original oder Ableitung verlinkt ist."""
    m = PFAD_RE.search(pfad)
    return m.group("stamm") if m else None


def original(stamm):
    return os.path.join(WURZEL, ORIGINAL_DIR, stamm + ".jpg")


def zuschnitt(im):
    """Zentrierter 4:3-Ausschnitt."""
    b, h = im.size
    ziel = SEITE[0] / SEITE[1]
    if b / h > ziel:
        neu_b = int(round(h * ziel))
        links = (b - neu_b) // 2
        return im.crop((links, 0, links + neu_b, h))
    neu_h = int(round(b / ziel))
    oben = (h - neu_h) // 2
    return im.crop((0, oben, b, oben + neu_h))


def breiten_fuer(stamm):
    """Welche Stufen fuer dieses Bild sinnvoll sind (nie hochskalieren)."""
    with Image.open(original(stamm)) as im:
        max_b = zuschnitt(im).size[0]
    # Nie hochskalieren: ein kleineres Original begrenzt die Stufen.
    return [b for b in BREITEN if b <= max_b] or [max_b]


def erzeuge(stamm, breiten, schreiben=True):
    """Fehlende Ableitungen bauen. Gibt die neu geschriebenen Pfade zurueck."""
    neu = []
    quelle = original(stamm)
    zugeschnitten = None
    for breite in sorted(breiten):
        ziel = os.path.join(WURZEL, KACHEL_DIR, f"{stamm}-{breite}.jpg")
        if os.path.exists(ziel):
            continue
        neu.append(os.path.relpath(ziel, WURZEL))
        if not schreiben:
            continue
        if zugeschnitten is None:
            with Image.open(quelle) as im:
                zugeschnitten = zuschnitt(im.convert("RGB"))
        hoehe = int(round(breite * SEITE[1] / SEITE[0]))
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        guete = QUALITAET if breite == min(BREITEN) else QUALITAET_KLEIN
        zugeschnitten.resize((breite, hoehe), Image.LANCZOS).save(
            ziel, "JPEG", quality=guete, optimize=True, progressive=True
        )
    return neu


def url(stamm, breite):
    return f"/{KACHEL_DIR}/{stamm}-{breite}.jpg"


def img_tag(alt_tag, stamm, zuerst):
    """Das <img> neu bauen - alt bleibt, Quelle und Groessenangaben kommen neu."""
    attr = dict(ATTR_RE.findall(alt_tag))
    breiten = breiten_fuer(stamm)
    gross = breiten[-1]
    srcset = ", ".join(f"{url(stamm, b)} {b}w" for b in breiten)
    teile = [
        f'src="{url(stamm, gross)}"',
        f'srcset="{srcset}"',
        f'sizes="{SIZES}"',
        f'width="{gross}"',
        f'height="{int(round(gross * SEITE[1] / SEITE[0]))}"',
        f'alt="{attr.get("alt", "")}"',
    ]
    # Das erste Bild ist auf der Startseite der LCP-Kandidat: nicht verzoegern.
    teile.append('fetchpriority="high"' if zuerst else 'loading="lazy"')
    return "<img " + " ".join(teile) + " />"


def kachel_breiten(stamm):
    """div.cover/div.thumb sind 190-210 px hoch, hoechstens rund 460 px breit - 1x und 2x."""
    moeglich = breiten_fuer(stamm)
    return moeglich[0], moeglich[-1]


def kachel_img(stamm):
    """Die Kachel als echtes <img>.

    Als CSS-background liessen sich die Kacheln nicht verzoegern: auf
    girlsnight/ luden elf davon sofort, zusammen 1,2 MB, und schoben den LCP
    auf ueber 5 s. Ein <img loading="lazy"> laedt nur, was wirklich in den
    Blick kommt. fetchpriority="low", damit die direkt unter dem Hero stehenden
    Kacheln dem Hero-Bild - dem LCP-Element - nicht die Bandbreite wegnehmen.
    alt bleibt leer - die Kachel wiederholt nur die Ueberschrift daneben,
    Screenreader sollen sie ueberspringen.
    """
    klein, gross = kachel_breiten(stamm)
    srcset = ", ".join(f"{url(stamm, b)} {b}w" for b in dict.fromkeys((klein, gross)))
    return (
        f'<img src="{url(stamm, gross)}" srcset="{srcset}" sizes="{SIZES_KACHEL}"'
        f' width="{gross}" height="{int(round(gross * SEITE[1] / SEITE[0]))}"'
        ' alt="" loading="lazy" fetchpriority="low" />'
    )


HERO_RE = re.compile(r"""--hero-img: url\('(?P<quelle>[^']+)'\)""")
VORLADEN_RE = re.compile(r'(<link rel="preload" as="image" href=")(?P<quelle>[^"]+)(")')


def hero_url(stamm):
    return f"/{HERO_DIR}/{stamm}-{HERO_BREITE}.jpg"


def hero_erzeuge(stamm, schreiben=True):
    """Das Hero-Bild in Anzeigebreite. Kein Zuschnitt - background-position
    entscheidet, welcher Ausschnitt zu sehen ist, das darf sich nicht aendern.
    Das Original bleibt liegen, es ist zugleich og:image."""
    ziel = os.path.join(WURZEL, HERO_DIR, f"{stamm}-{HERO_BREITE}.jpg")
    if os.path.exists(ziel):
        return []
    if schreiben:
        with Image.open(original(stamm)) as im:
            im = im.convert("RGB")
            hoehe = int(round(HERO_BREITE * im.size[1] / im.size[0]))
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            im.resize((HERO_BREITE, hoehe), Image.LANCZOS).save(
                ziel, "JPEG", quality=QUALITAET_KLEIN, optimize=True, progressive=True
            )
    return [os.path.relpath(ziel, WURZEL)]


def verarbeite(pfad, schreiben=True):
    voll = os.path.join(WURZEL, pfad)
    html = open(voll, encoding="utf-8").read()
    staemme = {}

    zaehler = [0]

    def occ(m):
        block = m.group(0)
        tag = IMG_RE.search(block)
        if not tag:
            return block
        stamm = stamm_aus(tag.group(0))
        if not stamm or not os.path.exists(original(stamm)):
            return block
        staemme.setdefault(stamm, set()).update(breiten_fuer(stamm))
        zaehler[0] += 1
        return block[: tag.start()] + img_tag(tag.group(0), stamm, zaehler[0] == 1) + block[tag.end():]

    def hintergrund(m):
        # Quelle ist der alte Inline-Hintergrund oder das schon gesetzte <img>.
        stamm = stamm_aus(m.group("stil") or "") or stamm_aus(m.group("inhalt"))
        if not stamm or not os.path.exists(original(stamm)):
            return m.group(0)
        staemme.setdefault(stamm, set()).update(kachel_breiten(stamm))
        rest = IMG_RE.sub("", m.group("inhalt"))
        return f'<div class="{m.group("klasse")}">{kachel_img(stamm)}{rest}</div>'

    heroes = []

    def hero(m):
        stamm = stamm_aus(m.group("quelle"))
        if not stamm or not os.path.exists(original(stamm)):
            return m.group(0)
        heroes.append(stamm)
        return f"--hero-img: url('{hero_url(stamm)}')"

    def vorladen(m):
        stamm = stamm_aus(m.group("quelle"))
        if not stamm or not os.path.exists(original(stamm)):
            return m.group(0)
        return m.group(1) + hero_url(stamm) + m.group(3)

    ergebnis = KACHEL_RE.sub(hintergrund, OCC_RE.sub(occ, html))
    ergebnis = VORLADEN_RE.sub(vorladen, HERO_RE.sub(hero, ergebnis))
    geaendert = ergebnis != html
    if geaendert and schreiben:
        open(voll, "w", encoding="utf-8").write(ergebnis)
    return staemme, heroes, geaendert


def seiten():
    treffer = ["index.html"]
    for eintrag in sorted(os.listdir(WURZEL)):
        kandidat = os.path.join(eintrag, "index.html")
        if eintrag == "cozy" or not os.path.isdir(os.path.join(WURZEL, eintrag)):
            continue
        if os.path.exists(os.path.join(WURZEL, kandidat)):
            treffer.append(kandidat)
    return treffer


def main():
    pruefen = "--pruefen" in sys.argv
    offen = []
    for pfad in seiten():
        staemme, heroes, geaendert = verarbeite(pfad, schreiben=not pruefen)
        neu = []
        for stamm, breiten in staemme.items():
            neu += erzeuge(stamm, breiten, schreiben=not pruefen)
        for stamm in dict.fromkeys(heroes):
            neu += hero_erzeuge(stamm, schreiben=not pruefen)
        if pruefen:
            if geaendert:
                offen.append(f"Markup nicht aktuell: {pfad}")
            for datei in neu:
                offen.append(f"Ableitung fehlt: {datei}")
        elif staemme or heroes:
            zusatz = f", {len(neu)} neu erzeugt" if neu else ""
            print(f"{pfad}: {len(staemme)} Kacheln{zusatz}")
    if pruefen:
        if offen:
            print("\n".join(offen))
            sys.exit(1)
        print("Kachelbilder aktuell")


if __name__ == "__main__":
    main()
