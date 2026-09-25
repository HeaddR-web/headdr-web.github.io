#!/usr/bin/env python3
"""Doppelte Pins finden und (nur mit --loeschen) entfernen.

Warum: Im September 2026 lagen 298 Pins auf den Boards, obwohl es nur rund 70
verschiedene Motive gab. 105 Titel standen zwei- bis fuenfmal da, am 29.07.2026
kamen 85 Pins an einem Tag - RSS-Import, Bulk-CSV und Handarbeit hatten
dieselben Pins mehrfach angelegt. Pinterest wertet solche Wiederholungen als
Spam-Muster und spielt das ganze Konto seltener aus.

Regel (vom Inhaber am 25.09.2026 freigegeben):
  * Gruppe = gleicher Titel UND gleiche Zielseite (Pfad ohne ?pin=/#anker).
  * Pro Gruppe bleibt der Pin mit den meisten Impressionen (90 Tage, aus
    pinterest/stats/latest.json), bei Gleichstand der aelteste.
  * Eine weitere Kopie bleibt, wenn sie eigenstaendig >= 200 Impressionen hat.
    Gleiche Zahlen wie der behaltene Pin heissen: dieselbe Statistik, also
    derselbe Pin auf einem zweiten Board - die Kopie geht.
Jeder geloeschte Pin wird vorher mit Titel, Beschreibung, Link, Board und
Bild-URL in pinterest/geloescht/<datum>.json gesichert. So laesst sich jeder
bei Bedarf neu anlegen - geloescht ist bei Pinterest endgueltig.

Aufruf (CI: .github/workflows/pinterest-aufraeumen.yml):
  python3 scripts/pinterest_aufraeumen.py            # nur anzeigen
  python3 scripts/pinterest_aufraeumen.py --loeschen # wirklich loeschen
  python3 scripts/pinterest_aufraeumen.py --links   # alte Ziel-Links anzeigen (nur lesend)
"""
import datetime as dt
import importlib.util
import json
import os
import sys
import time
import urllib.parse
from collections import defaultdict
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parent
spec = importlib.util.spec_from_file_location("pp", HIER / "pinterest_publish.py")
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)

STATS = ROOT / "pinterest" / "stats" / "latest.json"
SICHERUNG = ROOT / "pinterest" / "geloescht"
EIGENSTAENDIG = 200
PAUSE = 1.0


def pfad(link: str) -> str:
    return urllib.parse.urlparse(link or "").path.rstrip("/")


def bild(pin: dict) -> str:
    bilder = (pin.get("media") or {}).get("images") or {}
    for groesse in ("originals", "1200x", "600x"):
        if bilder.get(groesse, {}).get("url"):
            return bilder[groesse]["url"]
    return ""


def plan(pins: list, impressionen: dict) -> tuple[list, list]:
    gruppen = defaultdict(list)
    for p in pins:
        titel = (p.get("title") or "").strip().lower()
        if titel:
            gruppen[(titel, pfad(p.get("link")))].append(p)
    weg, bleibt_extra = [], []
    for gruppe in gruppen.values():
        if len(gruppe) < 2:
            continue
        gruppe.sort(key=lambda p: (-impressionen.get(p["id"], 0), p.get("created_at") or ""))
        erster = impressionen.get(gruppe[0]["id"], 0)
        for p in gruppe[1:]:
            n = impressionen.get(p["id"], 0)
            if n >= EIGENSTAENDIG and n != erster:
                bleibt_extra.append(p)
            else:
                weg.append(p)
    return weg, bleibt_extra


def delete_pin(token: str, pin_id: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    pp._request(f"{pp.API_BASE}/pins/{pin_id}", headers=headers, method="DELETE")


# --- Alte Ziel-Links (nur Anzeige) -------------------------------------------------------
# Alte Ziel-Adressen -> bethathost.de (nur Vorschlag, siehe links()). headdr-web.github.io leitet per 301
# weiter, aber Pinterest wertet den Umweg schlechter, und die Cozylore-Seiten
# (abgekoppelt, englisch, nicht mehr gepflegt) sollen gar kein Ziel mehr sein.
# Cozylore-Pins bekommen die naechstliegende BeThatHost-Seite (Inhaber-Freigabe
# 25.09.2026). Jede neue URL traegt ?pin=umzug-<pin-id-ende> - serverseitig eindeutig,
# siehe Ziel-URL-Regel in CLAUDE.md.
BASIS = "https://bethathost.de"
COZY_ZIEL = {
    "cozy-bathroom-spa-ideas": "/spa-abend/#cat-bath",
    "cozy-balcony-ideas": "/gartenparty/#cat-light",
    "cozy-fall-decor-ideas": "/saison-deko/#kalender",
    "cozy-apartment-in-winter": "/saison-deko/#kalender",
    "coziest-throw-blankets": "/saison-deko/#cat-textiles",
    "best-cozy-rugs": "/saison-deko/#cat-textiles",
    "cozy-bedroom-aesthetic-on-a-budget": "/saison-deko/#cat-textiles",
    "cozy-minimalist-bedroom": "/saison-deko/#cat-textiles",
    "cozy-living-room-ideas-small-apartments": "/saison-deko/#cat-textiles",
    "cozy-rental-ideas": "/saison-deko/#cat-textiles",
    "cozy-reading-nook-ideas": "/saison-deko/#cat-textiles",
    "best-warm-light-bulbs-cozy-glow": "/saison-deko/#cat-light",
    "cozy-bedroom-lighting-ideas": "/saison-deko/#cat-light",
    "best-cozy-candles": "/saison-deko/#cat-safe-light",
    "cozy-entryway-ideas": "/saison-deko/#cat-natural",
    "cozy-bookshelf-styling": "/saison-deko/#cat-natural",
    "cozy-kitchen-ideas": "/saison-deko/#cat-natural",
    "cozy-desk-setup-ideas": "/saison-deko/#cat-light",
    "warm-paint-colors-cozy-room": "/saison-deko/#cat-textiles",
    "hygge-living-habits": "/saison-deko/#cat-light",
    "cheap-cozy-decor-under-25": "/saison-deko/#cat-natural",
}


def neuer_link(link: str, pin_id: str):
    """Neue Ziel-URL oder None, wenn der Link schon passt."""
    u = urllib.parse.urlparse(link or "")
    if not u.netloc:
        return None
    alt_host = u.netloc.lower() in ("headdr-web.github.io", "www.headdr-web.github.io")
    cozy = u.path.startswith("/cozy/")
    if not (alt_host or cozy):
        return None
    if cozy:
        slug = u.path.rstrip("/").rsplit("/", 1)[-1].removesuffix(".html")
        ziel = COZY_ZIEL.get(slug, "/saison-deko/#cat-light")
    else:
        ziel = u.path + (f"#{u.fragment}" if u.fragment else "")
    pfad, _, anker = ziel.partition("#")
    if not (ROOT / (pfad.lstrip("/") + ("index.html" if pfad.endswith("/") else ""))).exists():
        raise SystemExit(f"Zielseite fehlt im Repo: {pfad} (fuer {link})")
    return f"{BASIS}{pfad}?pin=umzug-{pin_id[-6:]}" + (f"#{anker}" if anker else "")


def links(pins: list) -> int:
    """Nur anzeigen. Umbiegen per API geht nicht: Pinterest sperrt PATCH /pins
    fuer unsere App (HTTP 401, restricted feature: pin_edit - getestet am
    25.09.2026). Die Liste zum Umstellen von Hand steht in
    pinterest/COZY-PINS-UMBIEGEN.md."""
    plan_ = [(p, neuer_link(p.get("link"), p["id"])) for p in pins]
    plan_ = [(p, n) for p, n in plan_ if n]
    print(f"{len(plan_)} Pins mit alter oder Cozylore-Adresse.")
    for p, n in plan_:
        print(f"  {p['id']}  {p.get('link')}\n      -> {n}")
    return 0


def main() -> int:
    loeschen = "--loeschen" in sys.argv[1:]
    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    refresh = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    if not (app_id and app_secret and refresh):
        print("Fehlende Secrets - nichts getan.")
        return 0
    if not STATS.exists():
        print("pinterest/stats/latest.json fehlt - erst pinterest-stats.yml laufen lassen.")
        return 1
    impressionen = {p["id"]: (p.get("summe") or {}).get("IMPRESSION", 0)
                    for p in json.loads(STATS.read_text(encoding="utf-8"))["pins"]}

    token = pp.get_access_token(app_id, app_secret, refresh)
    boards = pp.list_boards(token)
    pins = []
    for b in boards:
        for p in pp.list_board_pins(token, b["id"]):
            p["_board"] = b.get("name", "")
            pins.append(p)
    if "--links" in sys.argv[1:]:
        return links(pins)
    weg, bleibt_extra = plan(pins, impressionen)
    print(f"{len(pins)} Pins auf {len(boards)} Boards. Zu loeschen: {len(weg)}, "
          f"als eigenstaendige Kopie behalten: {len(bleibt_extra)}.")
    print(f"Impressionen (90 Tage) der zu loeschenden Kopien zusammen: "
          f"{sum(impressionen.get(p['id'], 0) for p in weg)}")
    for p in weg:
        print(f"  weg  {p['id']}  [{p['_board']}]  {impressionen.get(p['id'], 0):>6}  {p.get('title')!r}")
    for p in bleibt_extra:
        print(f"  bleibt {p['id']}  [{p['_board']}]  {impressionen.get(p['id'], 0):>6}  {p.get('title')!r}")

    if not loeschen:
        print("\nNur angezeigt. Loeschen mit --loeschen (Workflow-Modus 'loeschen').")
        return 0

    SICHERUNG.mkdir(parents=True, exist_ok=True)
    datei = SICHERUNG / f"{dt.date.today().isoformat()}.json"
    gesichert = json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else []
    fehler = 0
    for p in weg:
        eintrag = {"id": p["id"], "board": p["_board"], "title": p.get("title"),
                   "description": p.get("description"), "link": p.get("link"),
                   "image_url": bild(p), "created_at": p.get("created_at"),
                   "impressionen_90t": impressionen.get(p["id"], 0)}
        try:
            delete_pin(token, p["id"])
            gesichert.append(eintrag)
            print(f"Geloescht {p['id']} {p.get('title')!r}")
        except pp.PinterestError as exc:
            fehler += 1
            print(f"Fehler bei {p['id']}: {exc}")
            if "HTTP 429" in str(exc):
                time.sleep(60)
            if fehler >= 5 and len(gesichert) == 0:
                print("Fuenf Fehler ohne einen Erfolg - Abbruch.")
                break
        # Nach jedem Pin sichern: bricht der Lauf ab, ist trotzdem alles
        # Geloeschte dokumentiert.
        datei.write_text(json.dumps(gesichert, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        time.sleep(PAUSE)
    print(f"\nFertig: {len(gesichert)} geloescht, {fehler} Fehler. Sicherung: {datei.relative_to(ROOT)}")
    return 1 if fehler and not gesichert else 0


if __name__ == "__main__":
    sys.exit(main())
