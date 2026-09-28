#!/usr/bin/env python3
"""Erzeugt eine CSV im Format von Pinterests eingebautem "Bulk-Pins erstellen".

KEINE API, KEIN Selenium, KEIN Warten auf Freigabe:
Pinterest Business -> Erstellen -> "Bulk create Pins" -> diese Datei hochladen.

Pinterest-Spalten: Title | Media URL | Pinterest board | Thumbnail |
                    Description | Link | Publish date | Keywords

WICHTIG: Der Bulk-Importer erwartet diese Spaltennamen exakt auf Englisch —
auch bei deutschsprachigem Konto. Die deutschen Bezeichnungen aus dem
Hilfe-Center ("Medien-URL", "Miniaturansicht", "Beschreibung") sind nur
übersetzte Beschreibungen, keine gültigen Spaltenköpfe (getestet: führt zu
"Fehlende Media-URL" für jede Zeile, obwohl die URL vorhanden ist).

- Liest pins.json (von extract_pins.py), oder mit --queue alle offenen Eintraege
  aus */pins/queue.json (nach "prio" sortiert) -> pinterest/bulk-neue-pins.csv.
  Das ist seit September 2026 der Hauptweg: Die Entwickler-App hat nur
  Trial-Zugang ("Apps with Trial access may not create Pins in production"),
  und der RSS-Feed hat fuer dieses Konto nie einen Pin erzeugt.
- Verteilt die Pins zeitversetzt (Standard: 2/Tag, ab morgen), damit es natuerlich
  wirkt. Mit --now wird die Publish-Spalte leer gelassen (alle sofort).
"""
import argparse
import csv
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

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
    "casino": "casino abend, james bond party, pokerabend, mottoparty",
    "oktoberfest": "oktoberfest zuhause, wiesn party, obatzda, brotzeit",
    "mengenrechner": "party planen, mengen pro person, einkaufsliste party, gastgeben",
}

HEADER = ["Title", "Media URL", "Pinterest board", "Thumbnail",
          "Description", "Link", "Publish date", "Keywords"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=None, help="Board-Name (sonst aus config.json)")
    ap.add_argument("--per-day", type=int, default=2, help="Pins pro Tag")
    ap.add_argument("--now", action="store_true", help="ohne Zeitplan, alle sofort")
    ap.add_argument("--queue", action="store_true",
                    help="offene Eintraege aus */pins/queue.json statt pins.json")
    ap.add_argument("--start", default=None, help="erster Tag (JJJJ-MM-TT), sonst morgen")
    args = ap.parse_args()

    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    board = args.board or cfg.get("board_name", "Pins")

    if args.queue:
        import glob
        with open(os.path.join(HERE, "boards.json"), encoding="utf-8") as f:
            board = args.board or json.load(f).get("default", board)
        pins = []
        for qf in sorted(glob.glob(os.path.join(HERE, "..", "*", "pins", "queue.json"))):
            site = os.path.basename(os.path.dirname(os.path.dirname(qf)))
            if site == "cozy":
                continue
            with open(qf, encoding="utf-8") as f:
                for q in json.load(f):
                    if not q.get("published"):
                        pins.append({"id": site, "title": q["title"], "image": q["image_url"],
                                     "description": q["description"], "link": q["link"],
                                     "prio": q.get("prio", 0)})
        pins.sort(key=lambda p: p["prio"])
    else:
        with open(os.path.join(HERE, "pins.json"), encoding="utf-8") as f:
            pins = json.load(f)

    # Zeitplan: ab morgen, taeglich um 10:00 und 16:00 (je nach per-day)
    slots = [10, 16, 13, 19, 8][: max(1, args.per_day)]
    start = (dt.date.fromisoformat(args.start) if args.start
             else dt.date.today() + dt.timedelta(days=1))

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

    out = os.path.join(HERE, "bulk-neue-pins.csv" if args.queue else "pinterest_bulk.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} Pins -> {out}")
    print(f"Board: {board} | Zeitplan: {'sofort' if args.now else f'{args.per_day}/Tag ab {start}'}")


if __name__ == "__main__":
    main()
