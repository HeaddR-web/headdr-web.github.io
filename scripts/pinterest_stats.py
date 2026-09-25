#!/usr/bin/env python3
"""Pinterest-Zahlen abholen und als Bericht ins Repo schreiben.

Warum: Bis September 2026 wusste niemand, ob Pinterest etwas bringt. Die Queue
war seit Tagen leer, der Workflow lief zweimal taeglich ins Leere - und weil
keine Zahlen erfasst wurden, fiel es nicht auf.

Was es tut: liest alle Pins aller Boards (nur lesend), holt fuer jeden Pin die
Tageswerte der letzten 90 Tage (so weit reicht die API zurueck) und schreibt
  * pinterest/STATISTIK.md       - Wochenverlauf, Top-Pins, Zahlen je Seite
  * pinterest/stats/latest.json  - Rohdaten je Pin fuer spaetere Auswertungen
Der Git-Verlauf beider Dateien ist die Zeitreihe.

Braucht nur die Scopes, die der Posting-Token ohnehin hat (boards:read,
pins:read). Konto-weite Zahlen (user_accounts:read) werden bewusst nicht
abgefragt - dafuer muesste der Token neu erzeugt werden.

Aufruf (in CI ueber .github/workflows/pinterest-stats.yml):
  python3 scripts/pinterest_stats.py
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

METRIKEN = ["IMPRESSION", "SAVE", "PIN_CLICK", "OUTBOUND_CLICK"]
NAMEN = {"IMPRESSION": "Impressionen", "SAVE": "Gemerkt", "PIN_CLICK": "Pin-Klicks",
         "OUTBOUND_CLICK": "Klicks zur Seite"}
TAGE = 89  # die API erlaubt hoechstens 90 Tage Rueckblick
PAUSE = 0.6  # Sekunden zwischen zwei Analytics-Abfragen
BERICHT = ROOT / "pinterest" / "STATISTIK.md"
ROHDATEN = ROOT / "pinterest" / "stats" / "latest.json"


def pin_analytics(token: str, pin_id: str, start: dt.date, ende: dt.date) -> dict:
    """Tageswerte eines Pins. Beim ersten Lauf (298 Pins am Stueck) lieferte
    die API ab Pin 140 nur noch HTTP 429 - deshalb Pause zwischen den Abfragen
    und bei 429 eine Minute warten, hoechstens dreimal."""
    for versuch in range(4):
        try:
            time.sleep(PAUSE)
            return _analytics(token, pin_id, start, ende)
        except pp.PinterestError as exc:
            if "HTTP 429" not in str(exc) or versuch == 3:
                raise
            print(f"  Rate-Limit bei Pin {pin_id} - 60 s warten")
            time.sleep(60)


def _analytics(token: str, pin_id: str, start: dt.date, ende: dt.date) -> dict:
    query = urllib.parse.urlencode({
        "start_date": start.isoformat(), "end_date": ende.isoformat(),
        "metric_types": ",".join(METRIKEN), "app_types": "ALL", "split_field": "NO_SPLIT",
    })
    headers = {"Authorization": f"Bearer {token}"}
    return pp._request(f"{pp.API_BASE}/pins/{pin_id}/analytics?{query}", headers=headers)


def seite(link: str) -> str:
    """https://bethathost.de/casino/?pin=x#y -> /casino/"""
    if not link or "bethathost.de" not in link:
        return "(andere)"
    pfad = urllib.parse.urlparse(link).path or "/"
    return pfad


def zahl(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def quote(a, b) -> str:
    return f"{100 * a / b:.1f} %".replace(".", ",") if b else "–"


def main() -> int:
    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    refresh = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    if not (app_id and app_secret and refresh):
        print("Fehlende Secrets - nichts abgefragt.")
        return 0
    token = pp.get_access_token(app_id, app_secret, refresh)
    print("Access-Token erhalten.")

    boards = pp.list_boards(token)
    heute = dt.date.today()
    start = heute - dt.timedelta(days=TAGE)

    pins = []
    for b in boards:
        for p in pp.list_board_pins(token, b["id"]):
            pins.append({"id": p.get("id"), "titel": (p.get("title") or "").strip(),
                         "link": p.get("link") or "", "erstellt": (p.get("created_at") or "")[:10],
                         "board": b.get("name", "")})
    print(f"{len(boards)} Boards, {len(pins)} Pins.")

    fehler = []
    for p in pins:
        try:
            daten = pin_analytics(token, p["id"], start, heute).get("all", {})
        except pp.PinterestError as exc:
            fehler.append(f"{p['id']}: {exc}")
            p["taeglich"], p["summe"] = {}, {}
            continue
        p["summe"] = {m: daten.get("summary_metrics", {}).get(m, 0) or 0 for m in METRIKEN}
        p["taeglich"] = {
            t["date"]: {m: (t.get("metrics") or {}).get(m, 0) or 0 for m in METRIKEN}
            for t in daten.get("daily_metrics", []) if t.get("date")
        }
    if fehler:
        print(f"{len(fehler)} Pin(s) ohne Zahlen, z. B. {fehler[0]}")
    if pins and len(fehler) == len(pins):
        print("Fuer keinen Pin gab es Zahlen - Bericht wird nicht ueberschrieben.")
        return 1

    # Wochenverlauf ueber alle Pins (ISO-Wochen, Montag als Beginn)
    woche = defaultdict(lambda: defaultdict(int))
    for p in pins:
        for tag, werte in p["taeglich"].items():
            d = dt.date.fromisoformat(tag)
            montag = d - dt.timedelta(days=d.weekday())
            for m, v in werte.items():
                woche[montag][m] += v

    # Wie viele Pins pro Woche neu dazukamen - faellt diese Spalte auf null,
    # bricht ein paar Wochen spaeter die Reichweite ein (August 2026).
    neu_je_woche = defaultdict(int)
    for p in pins:
        if p["erstellt"]:
            d = dt.date.fromisoformat(p["erstellt"])
            neu_je_woche[d - dt.timedelta(days=d.weekday())] += 1

    # Letzte 30 Tage je Pin und je Seite
    grenze = (heute - dt.timedelta(days=30)).isoformat()
    for p in pins:
        p["30t"] = {m: sum(w[m] for t, w in p["taeglich"].items() if t >= grenze) for m in METRIKEN}
    je_seite = defaultdict(lambda: defaultdict(int))
    anzahl = defaultdict(int)
    for p in pins:
        s = seite(p["link"])
        anzahl[s] += 1
        for m in METRIKEN:
            je_seite[s][m] += p["30t"][m]

    gesamt = {m: sum(p["30t"][m] for p in pins) for m in METRIKEN}
    z = [
        "# Pinterest-Statistik",
        "",
        f"Stand: {heute.isoformat()} · erzeugt von `scripts/pinterest_stats.py` "
        f"(Workflow `pinterest-stats.yml`, montags). Nicht von Hand bearbeiten.",
        "",
        f"**{len(pins)} Pins** auf {len(boards)} Boards. Letzte 30 Tage: "
        f"{zahl(gesamt['IMPRESSION'])} Impressionen, {zahl(gesamt['SAVE'])}× gemerkt, "
        f"{zahl(gesamt['PIN_CLICK'])} Pin-Klicks, **{zahl(gesamt['OUTBOUND_CLICK'])} Klicks zur Seite** "
        f"(Klickrate zur Seite {quote(gesamt['OUTBOUND_CLICK'], gesamt['IMPRESSION'])}).",
        "",
        "Pinterest braucht erfahrungsgemaess einige Wochen, bis neue Pins nennenswert ausgespielt",
        "werden. Die Zahlen der letzten zwei, drei Tage sind oft noch unvollstaendig.",
        "",
        "## Verlauf pro Woche",
        "",
        "| Woche ab | Neue Pins | Impressionen | Gemerkt | Pin-Klicks | Klicks zur Seite |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for montag in sorted(set(woche) | {m for m in neu_je_woche if m >= start - dt.timedelta(days=7)}):
        w = woche[montag]
        z.append(f"| {montag.strftime('%d.%m.%Y')} | {neu_je_woche.get(montag, 0)} | {zahl(w['IMPRESSION'])} | "
                 f"{zahl(w['SAVE'])} | {zahl(w['PIN_CLICK'])} | {zahl(w['OUTBOUND_CLICK'])} |")
    z += ["", "## Top 15 Pins (letzte 30 Tage, nach Impressionen)", "",
          "| Pin | Seite | Impressionen | Gemerkt | Klicks zur Seite |", "|---|---|---:|---:|---:|"]
    for p in sorted(pins, key=lambda p: (-p["30t"]["IMPRESSION"], -p["30t"]["OUTBOUND_CLICK"]))[:15]:
        titel = (p["titel"] or "(ohne Titel)").replace("|", "/")[:60]
        z.append(f"| {titel} | {seite(p['link'])} | {zahl(p['30t']['IMPRESSION'])} | "
                 f"{zahl(p['30t']['SAVE'])} | {zahl(p['30t']['OUTBOUND_CLICK'])} |")
    z += ["", "## Je Seite (letzte 30 Tage)", "",
          "| Seite | Pins | Impressionen | Gemerkt | Klicks zur Seite |", "|---|---:|---:|---:|---:|"]
    for s in sorted(je_seite, key=lambda s: -je_seite[s]["IMPRESSION"]):
        w = je_seite[s]
        z.append(f"| {s} | {anzahl[s]} | {zahl(w['IMPRESSION'])} | {zahl(w['SAVE'])} | "
                 f"{zahl(w['OUTBOUND_CLICK'])} |")
    titel = defaultdict(list)
    for p in pins:
        titel[p["titel"].strip().lower()].append(p)
    doppelt = {t: ps for t, ps in titel.items() if t and len(ps) > 1}
    alt = [p for p in pins if p["link"] and "bethathost.de" not in p["link"]]
    z += ["", "## Aufräumbedarf", "",
          f"- **{len(doppelt)} Titel mehrfach** auf den Boards, zusammen "
          f"{sum(len(ps) for ps in doppelt.values())} Pins (bis zu "
          f"{max((len(ps) for ps in doppelt.values()), default=0)}× derselbe). Pinterest wertet "
          "Wiederholungen als Spam-Muster und drosselt die Reichweite.",
          f"- **{len(alt)} Pins** verlinken nicht auf bethathost.de (alte Adresse oder Cozylore)."]
    if fehler:
        z += ["", f"_{len(fehler)} Pin(s) ohne Zahlen (API-Fehler), z. B.: `{fehler[0][:200]}`_"]
    BERICHT.write_text("\n".join(z) + "\n", encoding="utf-8")

    ROHDATEN.parent.mkdir(parents=True, exist_ok=True)
    roh = {"stand": heute.isoformat(), "von": start.isoformat(),
           "pins": [{k: p[k] for k in ("id", "titel", "link", "erstellt", "board", "summe", "30t")}
                    for p in pins],
           "wochen": {m.isoformat(): dict(w) for m, w in sorted(woche.items())}}
    ROHDATEN.write_text(json.dumps(roh, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(z[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
