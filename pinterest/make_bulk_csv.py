#!/usr/bin/env python3
"""Erzeugt eine CSV im Format von Pinterests eingebautem "Bulk-Pins erstellen".

KEINE API, KEIN Selenium, KEIN Warten auf Freigabe:
Pinterest Business -> Erstellen -> "Bulk create Pins" -> diese Datei hochladen.

Pinterest-Spalten: Title | Media URL | Pinterest board | Thumbnail |
                    Description | Link | Publish date | Keywords

- Liest pins.json (von extract_pins.py).
- Liest den Status aus dem Notion-Tracker ("📌 Pinterest Pins"): standardmaessig
  kommen NUR Pins mit Status = "Offen" in die CSV. So landen bereits hochgeladene
  oder geplante Pins nicht erneut im Bulk-Upload.
- Verteilt die Pins zeitversetzt (Standard: 2/Tag, ab morgen), damit es natuerlich
  wirkt. Mit --now wird die Publish-Spalte leer gelassen (alle sofort).

Notion-Anbindung
----------------
Der Status wird ueber die offizielle Notion-API gelesen. Dafuer:
  1. Interne Notion-Integration anlegen (notion.so/my-integrations) und die
     Datenbank "📌 Pinterest Pins" mit ihr teilen.
  2. Den Integrations-Token als Umgebungsvariable NOTION_TOKEN setzen
     (in GitHub Actions: als Secret).
Die Datenbank-ID und die Property-Namen stehen in config.json.

Ist kein Token gesetzt (oder --no-notion), werden ALLE Pins exportiert
(Verhalten wie frueher) und es wird eine Warnung ausgegeben. Mit --strict
bricht das Skript stattdessen ab, wenn Notion nicht erreichbar ist.
"""
import argparse
import csv
import datetime as dt
import json
import os

import requests

HERE = os.path.dirname(os.path.abspath(__file__))

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Schlagworte je Seite fuer bessere Auffindbarkeit (Pinterest "Keywords")
KEYWORDS = {
    "home": "party planen, gastgeben, feier ideen, deko",
    "girlsnight": "mädelsabend, girls night, deko, cocktails, spiele",
    "watchparty": "wm party, fußball party, public viewing zuhause, snacks",
    "cocktailabend": "cocktailabend, hausbar, cocktails, drinks",
    "brunch": "brunch ideen, sonntagsbrunch, frühstückstisch, brunch deko",
    "geburtstag": "geburtstag deko, geburtstagsparty zuhause, torte, ballons",
    "spa-abend": "spa abend, wellness zuhause, selfcare, gesichtsmaske",
    "valentinstag": "valentinstag ideen, date night, romantisch, deko",
    "saison-deko": "herbstdeko, winterdeko, gemütlich, dekoideen",
    "spieleabend": "spieleabend, brettspiele, game night, snacks",
    "grillabend": "grillen, bbq, grillparty, gartenparty",
    "gartenparty": "gartenparty, sommerparty, lichterketten, outdoor deko",
    "mexiko-fiesta": "mexikanische party, fiesta, taco party, margarita, mottoparty",
    "jga": "jga, junggesellinnenabschied, team braut, bachelorette, deko",
    "hawaii-tiki": "hawaii party, tiki party, luau, sommerparty, mottoparty",
}

HEADER = ["Title", "Media URL", "Pinterest board", "Thumbnail",
          "Description", "Link", "Publish date", "Keywords"]


def _norm(url):
    """Links robust vergleichbar machen (ohne Trailing-Slash / Whitespace)."""
    return (url or "").strip().rstrip("/")


def fetch_open_links(cfg, status_value):
    """Liest aus dem Notion-Tracker die Links aller Pins mit dem gewuenschten
    Status (Standard: "Offen"). Gibt ein Set normalisierter Links zurueck.

    Wirft eine Exception, wenn Token/DB fehlen oder die API einen Fehler liefert
    – der Aufrufer entscheidet ueber Fallback vs. Abbruch.
    """
    token = os.environ.get("NOTION_TOKEN")
    database_id = cfg.get("notion_database_id")
    if not token:
        raise RuntimeError("NOTION_TOKEN ist nicht gesetzt")
    if not database_id:
        raise RuntimeError("notion_database_id fehlt in config.json")

    status_prop = cfg.get("notion_status_property", "Status")
    link_prop = cfg.get("notion_link_property", "Ziel-Link")

    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "filter": {"property": status_prop, "select": {"equals": status_value}},
        "page_size": 100,
    }

    links = set()
    while True:
        r = requests.post(
            f"{NOTION_API}/databases/{database_id}/query",
            headers=headers, json=payload, timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        for row in data.get("results", []):
            prop = row.get("properties", {}).get(link_prop, {})
            link = prop.get("url")
            if link:
                links.add(_norm(link))
        if data.get("has_more"):
            payload["start_cursor"] = data["next_cursor"]
        else:
            break
    return links


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=None, help="Board-Name (sonst aus config.json)")
    ap.add_argument("--per-day", type=int, default=2, help="Pins pro Tag")
    ap.add_argument("--now", action="store_true", help="ohne Zeitplan, alle sofort")
    ap.add_argument("--status", default=None,
                    help="Welcher Notion-Status exportiert wird (Standard: config.notion_open_status)")
    ap.add_argument("--no-notion", action="store_true",
                    help="Notion-Status ignorieren und ALLE Pins exportieren")
    ap.add_argument("--strict", action="store_true",
                    help="Abbrechen, wenn Notion nicht erreichbar ist (statt Fallback)")
    args = ap.parse_args()

    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    board = args.board or cfg.get("board_name", "Pins")
    status_value = args.status or cfg.get("notion_open_status", "Offen")

    with open(os.path.join(HERE, "pins.json"), encoding="utf-8") as f:
        pins = json.load(f)

    # --- Notion-Status: nur offene Pins behalten ---
    if args.no_notion:
        print("Notion-Filter deaktiviert (--no-notion): alle Pins werden exportiert.")
    else:
        try:
            open_links = fetch_open_links(cfg, status_value)
            before = len(pins)
            pins = [p for p in pins if _norm(p.get("link")) in open_links]
            print(f"Notion: {len(pins)}/{before} Pins mit Status '{status_value}' "
                  f"werden exportiert.")
        except Exception as e:  # noqa: BLE001 - bewusst breit, Fallback gewuenscht
            if args.strict:
                raise
            print(f"WARN: Notion nicht gelesen ({e}). "
                  f"Fallback: ALLE Pins werden exportiert.")

    # Zeitplan: ab morgen, taeglich um 10:00 und 16:00 (je nach per-day)
    slots = [10, 16, 13, 19, 8][: max(1, args.per_day)]
    start = dt.date.today() + dt.timedelta(days=1)

    rows = []
    for i, p in enumerate(pins):
        publish = ""
        if not args.now:
            day = start + dt.timedelta(days=i // len(slots))
            hour = slots[i % len(slots)]
            publish = dt.datetime(day.year, day.month, day.day, hour, 0).strftime(
                "%Y-%m-%dT%H:%M:%S")
        rows.append({
            "Title": p["title"],
            "Media URL": p["image"],
            "Pinterest board": board,
            "Thumbnail": "",
            "Description": p["description"],
            "Link": p["link"],
            "Publish date": publish,
            "Keywords": KEYWORDS.get(p["id"], ""),
        })

    out = os.path.join(HERE, "pinterest_bulk.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} Pins -> {out}")
    print(f"Board: {board} | Zeitplan: {'sofort' if args.now else f'{args.per_day}/Tag ab {start}'}")


if __name__ == "__main__":
    main()
