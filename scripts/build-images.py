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
LEAD_DIR = "assets/img/lead"
PRODUKT_DIR = "assets/img/produkt"
BREITEN = (480, 960)
# Eigene Leiter fuer die kleinen Kacheln (div.cover/div.thumb). Nachgemessen
# ueber zehn Viewports braucht so eine Kachel auf einem 2x-Display:
#   320 px -> 572   390 px -> 712   430 px -> 792   600 px -> 1132
#   700 px -> 1148  768 px -> 690   900 px -> 822  1024 px -> 946
#  1280 px -> 676
# Der Sprung bei 600-700 px kommt vom Gitter: minmax(330px, 1fr) fuellt dort
# noch eine einzige Spalte, die Kachel ist also fast so breit wie der
# Bildschirm. Ab 768 px sind es zwei Spalten und die Kachel wird wieder klein.
# Deshalb 720 als mittlere Stufe (deckt 320, 390, 768 und ab 1280 punktgenau)
# und 960 als obere (430 bis 1024). Ohne die 720 lud jedes Handy die 960er:
# auf watchparty/ waren das drei Bilder mit 246 KB, die dem Hero-Bild - dem
# LCP-Element - die Bandbreite nahmen, waehrend es noch unterwegs war.
# Die grossen Karten der Startseite (a.occ-media, 46vw) haben ihre eigene
# Leiter BREITEN; dort passt die 960 auf jeder Breite.
KACHEL_BREITEN = (480, 720, 960)
SEITE = (4, 3)
# Die 1x-Stufe wird Pixel fuer Pixel gezeigt und bleibt scharf; die 2x-Stufe und
# das Hero-Bild werden immer verkleinert dargestellt, da faellt weniger Qualitaet
# nicht auf - spart aber rund ein Drittel der Bytes.
QUALITAET = 80
QUALITAET_KLEIN = 72
HERO_BREITE = 1280
# Handy-Zuschnitt des Hero-Bildes. Das Desktop-Bild ist quer (1280 x 858), der
# Hero-Kasten auf dem Handy dagegen hoch: 358 x 487 CSS-Pixel bei 390 px
# Viewport, bei 320 px sogar 288 x 541. background-size:cover skaliert deshalb
# nach der Hoehe - und wirft links und rechts rund 40 Prozent der Bildbreite
# weg, die der Besucher trotzdem herunterlaedt. Schlimmer noch: 858 Bildpunkte
# Hoehe reichen fuer die 974 Geraetepunkte eines 2x-Displays gar nicht, das
# Bild wird also auch noch hochskaliert.
# 800 x 976 im Hochformat laedt nur noch das, was zu sehen ist: rund ein
# Drittel weniger Bytes bei 14 Prozent mehr Bildhoehe. Nachgemessen bleibt das
# Bild dabei exakt gleich scharf (mittlere Kantenstaerke 13,8 vorher wie
# nachher) und zeigt denselben Ausschnitt. Ab 461 px uebernimmt wieder das
# Querformat.
HERO_MOBIL_BREITE = 800
HERO_MOBIL_SEITE = (41, 50)
HERO_MOBIL_MQ = "(max-width: 460px)"
SIZES = "(max-width: 860px) 100vw, 46vw"
# Die Angabe muss zu den Messwerten bei KACHEL_BREITEN passen, sonst waehlt der
# Browser die falsche Stufe: "360px" stimmte zwar ab 1280 px, behauptete aber
# auch bei 1024 px 360 CSS-Pixel, wo die Kachel in Wahrheit 473 breit ist.
# Die Bruchstellen kommen aus dem Gitter selbst: repeat(auto-fill,
# minmax(330px, 1fr)) mit 26 px Luecke in einem Container von Bildschirm
# minus 34 px Seitenrand. Zwei Spalten passen ab 2*330+26 = 686 Container-
# Pixeln, also ab 720 px Bildschirm; drei ab 1042, also ab 1076 px. Die
# Kachel ist dann (Bildschirm - 34 - 26) / 2, das ist calc(50vw - 30px).
#   <= 719 px   eine Spalte,  Bildschirm minus Seitenrand
#   <= 1075 px  zwei Spalten, calc(50vw - 30px)
#   darueber    drei Spalten, rund 360 px (der Container ist gedeckelt)
# Auf zwei Pixel kommt es dabei an: mit 47vw statt calc(50vw - 30px) rechnet
# der Browser bei 768 px 721,9 Geraetepunkte aus - zwei mehr als die 720er
# Stufe hergibt - und laedt die 960er.
SIZES_KACHEL = ("(max-width: 719px) calc(100vw - 34px), "
                "(max-width: 1075px) calc(50vw - 30px), 360px")

# Lead-Bild der Artikel (article img.lead) - das LCP-Element jeder Artikelseite.
# Bis September 2026 kam es als Original: bis zu 637 KB (1600 x 2385) fuer einen
# Kasten von 358 x 460 CSS-Pixeln auf dem Handy, 720 x 460 auf dem Desktop.
# Gemessener LCP auf world-cup-watch-party 4,3 s, auf girls-night-games 3,2 s.
# Der Kasten ist breitengesteuert (width:100%, max-height:460px, object-fit:
# cover): das Bild wird immer nach der Breite skaliert, bei jedem Viewport und
# jedem Seitenverhaeltnis der Originale. Deshalb reicht eine reine Breiten-
# Leiter ohne Zuschnitt - sichtbar bleibt exakt dasselbe Bild.
#   720   Handy bis 360 CSS-Pixel bei 2x, Desktop bei 1x (Pixel fuer Pixel)
#   1080  Handys mit 3x und Tablets
#   1440  Desktop bei 2x (720 CSS-Pixel)
# Ein Original, das schmaler ist als die oberste Stufe, bekommt seine eigene
# Breite als letzte Stufe (1264, 1024, 848) - nie hochskalieren.
LEAD_BREITEN = (720, 1080, 1440)
# Artikelbreite: --read 720px, Seitenrand 16 px bis 640 px Bildschirm, darueber
# 24 px. Ab 768 px passt die volle Leselaenge.
SIZES_LEAD = ("(max-width: 640px) calc(100vw - 32px), "
              "(max-width: 767px) calc(100vw - 48px), 720px")
LEAD_RE = re.compile(r'<img class="lead"\s[^>]*?/?>')

# Produktfotos in den Pick-Karten (div.pick-photo img). Der Kasten ist quadratisch
# (aspect-ratio 1/1, object-fit: contain) und klein: 170 CSS-Pixel Bild auf dem
# Desktop (190 px minus 2 x 10 px Innenabstand), bis 640 px Bildschirm 240
# (max-width 260 px minus Innenabstand). Ausgeliefert wurden bis September 2026
# die 1024 x 1024 grossen Originale ohne width/height - 870 KB fuer sieben Karten
# auf gartenparty/.
#   360  Desktop bei 2x (340 Geraetepunkte)
#   540  Handy bei 2x (480)
#   720  Handy bei 3x (720)
# Kein Zuschnitt: die Originale sind quadratisch, und contain zeigt ohnehin alles.
PRODUKT_BREITEN = (360, 540, 720)
SIZES_PRODUKT = "(max-width: 640px) 240px, 170px"
PRODUKT_RE = re.compile(r'(<div class="pick-photo">)(<img\s[^>]*?/?>)')

OCC_RE = re.compile(r'<a class="occ-media"[^>]*>.*?</a>', re.S)
IMG_RE = re.compile(r'<img\s[^>]*?/?>', re.S)
ATTR_RE = re.compile(r'(\w[\w-]*)="([^"]*)"')
KACHEL_RE = re.compile(
    r'<div class="(?P<klasse>cover|thumb)"(?: style="(?P<stil>[^"]*)")?>(?P<inhalt>.*?)</div>',
    re.S,
)
PFAD_RE = re.compile(r'/assets/img/(?:kachel/|hero/|lead/|produkt/)?(?P<stamm>[^"\'/]+?)(?:-\d+)?\.jpg')


def stamm_aus(pfad):
    """Stamm des Originals - egal ob Original oder Ableitung verlinkt ist."""
    m = PFAD_RE.search(pfad)
    return m.group("stamm") if m else None


def original(stamm):
    return os.path.join(WURZEL, ORIGINAL_DIR, stamm + ".jpg")


def zuschnitt(im, seite=SEITE):
    """Zentrierter Ausschnitt im gewuenschten Seitenverhaeltnis."""
    b, h = im.size
    ziel = seite[0] / seite[1]
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
    """Die Stufen einer kleinen Kachel (siehe KACHEL_BREITEN)."""
    with Image.open(original(stamm)) as im:
        max_b = zuschnitt(im).size[0]
    return tuple(b for b in KACHEL_BREITEN if b <= max_b) or (max_b,)


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
    breiten = kachel_breiten(stamm)
    gross = breiten[-1]
    srcset = ", ".join(f"{url(stamm, b)} {b}w" for b in breiten)
    return (
        f'<img src="{url(stamm, gross)}" srcset="{srcset}" sizes="{SIZES_KACHEL}"'
        f' width="{gross}" height="{int(round(gross * SEITE[1] / SEITE[0]))}"'
        ' alt="" loading="lazy" fetchpriority="low" />'
    )


# Beide Custom Properties bzw. beide Preload-Zeilen mitfassen, damit ein
# zweiter Lauf nichts verdoppelt.
HERO_RE = re.compile(
    r"--hero-img: url\('(?P<quelle>[^']+)'\)"
    r"(?:; --hero-img-mobil: url\('[^']+'\))?"
)
VORLADEN_RE = re.compile(
    r'(?P<einzug>[ \t]*)<link rel="preload" as="image" href="(?P<quelle>[^"]+)"[^>]*>\n'
    r'(?:[ \t]*<link rel="preload" as="image"[^>]*>\n)?'
)


def hero_url(stamm, breite=None):
    return f"/{HERO_DIR}/{stamm}-{breite or HERO_BREITE}.jpg"


def hero_dateien(stamm):
    return [os.path.join(HERO_DIR, f"{stamm}-{b}.jpg")
            for b in (HERO_BREITE, HERO_MOBIL_BREITE)]


def hero_erzeuge(stamm, schreiben=True):
    """Beide Hero-Ableitungen: Desktop-Breite ohne Zuschnitt, Handy-Zuschnitt.

    Auf dem Desktop bleibt das Bild ungeschnitten - background-position
    entscheidet dort, welcher Ausschnitt zu sehen ist, und das darf sich nicht
    aendern. Fuer das Handy wird vorgeschnitten, was der Browser ohnehin zeigt
    (siehe HERO_MOBIL_SEITE). Das Original bleibt beidemale liegen, es ist
    zugleich og:image.
    """
    neu = []
    for breite, seite in ((HERO_BREITE, None), (HERO_MOBIL_BREITE, HERO_MOBIL_SEITE)):
        ziel = os.path.join(WURZEL, HERO_DIR, f"{stamm}-{breite}.jpg")
        if os.path.exists(ziel):
            continue
        neu.append(os.path.relpath(ziel, WURZEL))
        if not schreiben:
            continue
        with Image.open(original(stamm)) as im:
            im = im.convert("RGB")
            if seite:
                im = zuschnitt(im, seite)
                masse = (breite, int(round(breite * seite[1] / seite[0])))
            else:
                masse = (breite, int(round(breite * im.size[1] / im.size[0])))
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            im.resize(masse, Image.LANCZOS).save(
                ziel, "JPEG", quality=QUALITAET_KLEIN, optimize=True, progressive=True
            )
    return neu


def lead_breiten(stamm):
    with Image.open(original(stamm)) as im:
        max_b = im.size[0]
    stufen = [b for b in LEAD_BREITEN if b <= max_b]
    if not stufen or stufen[-1] < min(max_b, LEAD_BREITEN[-1]):
        stufen.append(max_b)
    return stufen


def lead_url(stamm, breite):
    return f"/{LEAD_DIR}/{stamm}-{breite}.jpg"


def lead_erzeuge(stamm, schreiben=True):
    """Ungeschnittene Verkleinerungen des Originals (siehe LEAD_BREITEN)."""
    neu = []
    for breite in lead_breiten(stamm):
        ziel = os.path.join(WURZEL, LEAD_DIR, f"{stamm}-{breite}.jpg")
        if os.path.exists(ziel):
            continue
        neu.append(os.path.relpath(ziel, WURZEL))
        if not schreiben:
            continue
        with Image.open(original(stamm)) as im:
            im = im.convert("RGB")
            masse = (breite, int(round(breite * im.size[1] / im.size[0])))
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            # Die 720er wird auf dem Desktop bei 1x Pixel fuer Pixel gezeigt.
            guete = QUALITAET if breite == LEAD_BREITEN[0] else QUALITAET_KLEIN
            im.resize(masse, Image.LANCZOS).save(
                ziel, "JPEG", quality=guete, optimize=True, progressive=True
            )
    return neu


def lead_img(alt_tag, stamm):
    """Das Lead-Bild mit srcset. width/height reservieren den Platz (dazu
    height:auto in style.css), fetchpriority="high", weil es das LCP-Element ist."""
    attr = dict(ATTR_RE.findall(alt_tag))
    breiten = lead_breiten(stamm)
    with Image.open(original(stamm)) as im:
        b, h = im.size
    mitte = breiten[min(1, len(breiten) - 1)]
    srcset = ", ".join(f"{lead_url(stamm, x)} {x}w" for x in breiten)
    return (
        f'<img class="lead" src="{lead_url(stamm, mitte)}" srcset="{srcset}"'
        f' sizes="{SIZES_LEAD}" width="{mitte}" height="{int(round(mitte * h / b))}"'
        f' alt="{attr.get("alt", "")}" fetchpriority="high" />'
    )


def verarbeite_lead(pfad, schreiben=True):
    voll = os.path.join(WURZEL, pfad)
    html = open(voll, encoding="utf-8").read()
    staemme = []

    def ersetze(m):
        stamm = stamm_aus(m.group(0))
        if not stamm or not os.path.exists(original(stamm)):
            return m.group(0)
        staemme.append(stamm)
        return lead_img(m.group(0), stamm)

    ergebnis = LEAD_RE.sub(ersetze, html)
    geaendert = ergebnis != html
    if geaendert and schreiben:
        open(voll, "w", encoding="utf-8").write(ergebnis)
    return staemme, geaendert


def produkt_breiten(stamm):
    with Image.open(original(stamm)) as im:
        max_b = im.size[0]
    stufen = [b for b in PRODUKT_BREITEN if b <= max_b]
    return stufen or [max_b]


def produkt_url(stamm, breite):
    return f"/{PRODUKT_DIR}/{stamm}-{breite}.jpg"


def produkt_erzeuge(stamm, schreiben=True):
    """Ungeschnittene Verkleinerungen des Produktfotos (siehe PRODUKT_BREITEN)."""
    neu = []
    for breite in produkt_breiten(stamm):
        ziel = os.path.join(WURZEL, PRODUKT_DIR, f"{stamm}-{breite}.jpg")
        if os.path.exists(ziel):
            continue
        neu.append(os.path.relpath(ziel, WURZEL))
        if not schreiben:
            continue
        with Image.open(original(stamm)) as im:
            im = im.convert("RGB")
            masse = (breite, int(round(breite * im.size[1] / im.size[0])))
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            im.resize(masse, Image.LANCZOS).save(
                ziel, "JPEG", quality=QUALITAET_KLEIN, optimize=True, progressive=True
            )
    return neu


def produkt_img(alt_tag, stamm):
    """Produktfoto mit srcset. width/height reservieren den Platz (height:auto
    in style.css), loading="lazy": die Karten liegen alle unter dem Falz."""
    attr = dict(ATTR_RE.findall(alt_tag))
    breiten = produkt_breiten(stamm)
    with Image.open(original(stamm)) as im:
        b, h = im.size
    klein = breiten[0]
    srcset = ", ".join(f"{produkt_url(stamm, x)} {x}w" for x in breiten)
    return (
        f'<img src="{produkt_url(stamm, klein)}" srcset="{srcset}"'
        f' sizes="{SIZES_PRODUKT}" width="{klein}" height="{int(round(klein * h / b))}"'
        f' alt="{attr.get("alt", "")}" loading="lazy" decoding="async" />'
    )


def verarbeite_produkt(pfad, schreiben=True):
    voll = os.path.join(WURZEL, pfad)
    html = open(voll, encoding="utf-8").read()
    staemme = []

    def ersetze(m):
        stamm = stamm_aus(m.group(2))
        if not stamm or not os.path.exists(original(stamm)):
            return m.group(0)
        staemme.append(stamm)
        return m.group(1) + produkt_img(m.group(2), stamm)

    ergebnis = PRODUKT_RE.sub(ersetze, html)
    geaendert = ergebnis != html
    if geaendert and schreiben:
        open(voll, "w", encoding="utf-8").write(ergebnis)
    return staemme, geaendert


def lead_seiten():
    treffer = []
    for ordner, dirs, dateien in os.walk(WURZEL):
        rel = os.path.relpath(ordner, WURZEL)
        dirs[:] = sorted(d for d in dirs if not d.startswith(".")
                         and not (rel == "." and d in ("cozy", "assets", "scripts")))
        for name in sorted(dateien):
            if name.endswith(".html"):
                treffer.append(os.path.normpath(os.path.join(rel, name)))
    return treffer


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
        return (f"--hero-img: url('{hero_url(stamm)}')"
                f"; --hero-img-mobil: url('{hero_url(stamm, HERO_MOBIL_BREITE)}')")

    def vorladen(m):
        stamm = stamm_aus(m.group("quelle"))
        if not stamm or not os.path.exists(original(stamm)):
            return m.group(0)
        # Zwei Zeilen mit media-Bedingung: der Browser laedt nur die, die zu
        # seinem Viewport passt. Ohne media haette er beide geholt - der
        # Handy-Zuschnitt wuerde das Bild dann groesser statt kleiner machen.
        ein = m.group("einzug")
        return (
            f'{ein}<link rel="preload" as="image" href="{hero_url(stamm)}"'
            f' media="(min-width: 461px)" fetchpriority="high" />\n'
            f'{ein}<link rel="preload" as="image" href="{hero_url(stamm, HERO_MOBIL_BREITE)}"'
            f' media="{HERO_MOBIL_MQ}" fetchpriority="high" />\n'
        )

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


def verwaist(gebraucht):
    """Ableitungen, die keine Seite mehr verlinkt.

    Aendert sich eine Stufe (etwa die Kacheln von 960 auf 720), bleiben die
    alten Dateien sonst als toter Ballast im Repo liegen - und niemand sieht
    spaeter, welche davon noch gebraucht werden.
    """
    raus = []
    for ordner in (KACHEL_DIR, HERO_DIR, LEAD_DIR, PRODUKT_DIR):
        voll = os.path.join(WURZEL, ordner)
        if not os.path.isdir(voll):
            continue
        for name in sorted(os.listdir(voll)):
            rel = os.path.join(ordner, name)
            if rel not in gebraucht:
                raus.append(rel)
    return raus


def main():
    pruefen = "--pruefen" in sys.argv
    offen = []
    gebraucht = set()
    for pfad in seiten():
        staemme, heroes, geaendert = verarbeite(pfad, schreiben=not pruefen)
        neu = []
        for stamm, breiten in staemme.items():
            neu += erzeuge(stamm, breiten, schreiben=not pruefen)
            gebraucht.update(os.path.join(KACHEL_DIR, f"{stamm}-{b}.jpg") for b in breiten)
        for stamm in dict.fromkeys(heroes):
            neu += hero_erzeuge(stamm, schreiben=not pruefen)
            gebraucht.update(hero_dateien(stamm))
        if pruefen:
            if geaendert:
                offen.append(f"Markup nicht aktuell: {pfad}")
            for datei in neu:
                offen.append(f"Ableitung fehlt: {datei}")
        elif staemme or heroes:
            zusatz = f", {len(neu)} neu erzeugt" if neu else ""
            print(f"{pfad}: {len(staemme)} Kacheln{zusatz}")

    for pfad in lead_seiten():
        staemme, geaendert = verarbeite_lead(pfad, schreiben=not pruefen)
        neu = []
        for stamm in staemme:
            neu += lead_erzeuge(stamm, schreiben=not pruefen)
            gebraucht.update(os.path.join(LEAD_DIR, f"{stamm}-{b}.jpg")
                             for b in lead_breiten(stamm))
        if pruefen:
            if geaendert:
                offen.append(f"Markup nicht aktuell: {pfad}")
            for datei in neu:
                offen.append(f"Ableitung fehlt: {datei}")
        elif neu:
            print(f"{pfad}: Lead-Bild, {len(neu)} neu erzeugt")

        staemme, geaendert = verarbeite_produkt(pfad, schreiben=not pruefen)
        neu = []
        for stamm in staemme:
            neu += produkt_erzeuge(stamm, schreiben=not pruefen)
            gebraucht.update(os.path.join(PRODUKT_DIR, f"{stamm}-{b}.jpg")
                             for b in produkt_breiten(stamm))
        if pruefen:
            if geaendert:
                offen.append(f"Markup nicht aktuell: {pfad}")
            for datei in neu:
                offen.append(f"Ableitung fehlt: {datei}")
        elif neu:
            print(f"{pfad}: {len(staemme)} Produktfotos, {len(neu)} neu erzeugt")

    alt = verwaist(gebraucht)
    if pruefen:
        for datei in alt:
            offen.append(f"Ableitung verwaist: {datei}")
        if offen:
            print("\n".join(offen))
            sys.exit(1)
        print("Kachel-, Hero-, Lead- und Produktbilder aktuell")
    else:
        for datei in alt:
            os.remove(os.path.join(WURZEL, datei))
        if alt:
            print(f"{len(alt)} verwaiste Ableitungen geloescht")


if __name__ == "__main__":
    main()
