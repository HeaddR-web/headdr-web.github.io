#!/usr/bin/env python3
"""Erzeugt eine CSV im Format von Pinterests eingebautem "Bulk-Pins erstellen".

KEINE API, KEIN Selenium, KEIN Warten auf Freigabe:
Pinterest Business -> Erstellen -> "Bulk create Pins" -> diese Datei hochladen.

Pinterest-Spalten: Title | Media URL | Pinterest board | Thumbnail |
                    Description | Link | Publish date | Keywords

Quellen der Pins
----------------
- pins.json            : die Landing-Page-Pins (von extract_pins.py).
- extra_notion_pins.json: zusaetzliche Pins, die nur im Notion-Tracker leben
                          (z. B. aeltere Kategorie-/Content-Pins), als Snapshot.

Status aus Notion
-----------------
In die CSV kommen NUR offene Pins (Status = "Offen"):
- MIT NOTION_TOKEN: Der Status wird live ueber die offizielle Notion-API gelesen.
  Standardmaessig werden alle offenen Pins direkt aus Notion gezogen (Titel,
  Bild-URL, Beschreibung, Link) — so sind auch alte, noch nicht hochgeladene
  Pins automatisch dabei, ohne dass sie in pins.json stehen muessen.
- OHNE NOTION_TOKEN (oder --no-notion): Es wird der lokale Snapshot
  (pins.json + extra_notion_pins.json) exportiert. Dieser Snapshot bildet den
  aktuell offenen Stand ab.

Notion-Anbindung einrichten:
  1. Interne Notion-Integration anlegen (notion.so/my-integrations) und die
     Datenbank "📌 Pinterest Pins" mit ihr teilen.
  2. Den Integrations-Token als Umgebungsvariable NOTION_TOKEN setzen
     (in GitHub Actions: als Secret). DB-ID/Property-Namen stehen in config.json.

Verteilt die Pins zeitversetzt (Standard: 2/Tag, ab morgen). Mit --now wird die
Publish-Spalte leer gelassen (alle sofort).
"""
import argparse
import csv
import datetime as dt
import json
import os
import re

import requests

HERE = os.path.dirname(os.path.abspath(__file__))

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Schlagworte je Landing-Page fuer bessere Auffindbarkeit (Pinterest "Keywords")
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


def _hashtags_to_keywords(description):
    """Fallback: aus #hashtags der Beschreibung eine Keyword-Liste bauen."""
    tags = re.findall(r"#(\w+)", description or "")
    return ", ".join(tags[:6])


def load_local_pins():
    """pins.json + optional extra_notion_pins.json zusammenfuehren (nach Link dedupliziert)."""
    pins = []
    with open(os.path.join(HERE, "pins.json"), encoding="utf-8") as f:
        pins.extend(json.load(f))
    extra_path = os.path.join(HERE, "extra_notion_pins.json")
    if os.path.exists(extra_path):
        with open(extra_path, encoding="utf-8") as f:
            pins.extend(json.load(f))
    seen, out = set(), []
    for p in pins:
        key = _norm(p.get("link"))
        if key and key not in seen:
            seen.add(key)
            out.append(p)
    return out


def keyword_for(pin, link_to_local=None):
    """Keywords ermitteln: explizit > KEYWORDS[id] > Beschreibungs-Hashtags."""
    if pin.get("keywords"):
        return pin["keywords"]
    kw = KEYWORDS.get(pin.get("id", ""), "")
    if not kw and link_to_local is not None:
        local = link_to_local.get(_norm(pin.get("link")))
        if local:
            kw = local.get("keywords") or KEYWORDS.get(local.get("id", ""), "")
    return kw or _hashtags_to_keywords(pin.get("description", ""))


def merge_keywords(base, extras):
    """Globale Keywords anhaengen, ohne Duplikate (case-insensitive), Reihenfolge erhalten."""
    out, seen = [], set()
    for kw in [k.strip() for k in base.split(",")] + list(extras):
        k = kw.strip()
        if k and k.lower() not in seen:
            seen.add(k.lower())
            out.append(k)
    return ", ".join(out)


def fetch_open_pins(cfg, status_value):
    """Liest alle offenen Pins direkt aus dem Notion-Tracker (volle Datensaetze).

    Wirft eine Exception, wenn Token/DB fehlen oder die API einen Fehler liefert –
    der Aufrufer entscheidet ueber Fallback vs. Abbruch.
    """
    token = os.environ.get("NOTION_TOKEN")
    database_id = cfg.get("notion_database_id")
    if not token:
        raise RuntimeError("NOTION_TOKEN ist nicht gesetzt")
    if not database_id:
        raise RuntimeError("notion_database_id fehlt in config.json")

    status_prop = cfg.get("notion_status_property", "Status")
    link_prop = cfg.get("notion_link_property", "Ziel-Link")
    title_prop = cfg.get("notion_title_property", "Titel")
    image_prop = cfg.get("notion_image_property", "Bild-URL")
    desc_prop = cfg.get("notion_desc_property", "Beschreibung")

    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    payload = {
        "filter": {"property": status_prop, "select": {"equals": status_value}},
        "page_size": 100,
    }

    def _text(prop):
        if not prop:
            return ""
        if prop.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in prop.get("title", []))
        if prop.get("type") == "rich_text":
            return "".join(t.get("plain_text", "") for t in prop.get("rich_text", []))
        if prop.get("type") == "url":
            return prop.get("url") or ""
        return ""

    pins = []
    while True:
        r = requests.post(
            f"{NOTION_API}/databases/{database_id}/query",
            headers=headers, json=payload, timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        for row in data.get("results", []):
            props = row.get("properties", {})
            link = _text(props.get(link_prop))
            if not link:
                continue
            pins.append({
                "title": _text(props.get(title_prop)),
                "image": _text(props.get(image_prop)),
                "description": _text(props.get(desc_prop)),
                "link": link,
            })
        if data.get("has_more"):
            payload["start_cursor"] = data["next_cursor"]
        else:
            break
    return pins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=None, help="Board-Name (sonst aus config.json)")
    ap.add_argument("--per-day", type=int, default=2, help="Pins pro Tag")
    ap.add_argument("--now", action="store_true", help="ohne Zeitplan, alle sofort")
    ap.add_argument("--status", default=None,
                    help="Welcher Notion-Status exportiert wird (Standard: config.notion_open_status)")
    ap.add_argument("--no-notion", action="store_true",
                    help="Notion-API ignorieren und den lokalen Snapshot exportieren")
    ap.add_argument("--strict", action="store_true",
                    help="Abbrechen, wenn Notion nicht erreichbar ist (statt Fallback)")
    args = ap.parse_args()

    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    board = args.board or cfg.get("board_name", "Pins")
    status_value = args.status or cfg.get("notion_open_status", "Offen")

    local = load_local_pins()
    link_to_local = {_norm(p.get("link")): p for p in local}

    # --- Pin-Quelle bestimmen ---
    pins = None
    if not args.no_notion:
        try:
            pins = fetch_open_pins(cfg, status_value)
            print(f"Notion: {len(pins)} offene Pins (Status '{status_value}') live gelesen.")
        except Exception as e:  # noqa: BLE001 - bewusst breit, Fallback gewuenscht
            if args.strict:
                raise
            print(f"WARN: Notion nicht gelesen ({e}). "
                  f"Fallback: lokaler Snapshot (pins.json + extra_notion_pins.json).")
    if pins is None:
        pins = local
        if args.no_notion:
            print(f"Lokaler Snapshot (--no-notion): {len(pins)} Pins.")

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
            "Keywords": merge_keywords(keyword_for(p, link_to_local),
                                       cfg.get("global_keywords", [])),
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
