#!/usr/bin/env python3
"""Postet neue Pins ueber die offizielle Pinterest-API (v5).

- Liest pins.json (von extract_pins.py erzeugt).
- Fuehrt ein Ledger (posted.json), damit kein Pin doppelt gepostet wird.
- Postet pro Lauf maximal `posts_per_run` neue Pins.
- DRY_RUN=1 (Standard, solange PINTEREST_LIVE != 'true') -> nichts wird gepostet,
  es wird nur angezeigt, was passieren wuerde.

Benoetigt: Umgebungsvariable PINTEREST_ACCESS_TOKEN (GitHub-Secret).
Nur Standardbibliothek + requests.
"""
import base64
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.pinterest.com/v5"
TOKEN_URL = f"{API}/oauth/token"


def refresh_access_token(app_id, app_secret, refresh_token):
    """Holt mit dem Refresh-Token einen frischen Access-Token (Pinterest v5).

    Refresh-Tokens sind langlebig (~1 Jahr); Access-Tokens nur ~30 Tage. So muss
    nie wieder ein Access-Token manuell erneuert werden. Wirft bei Fehler.
    """
    basic = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Token-Refresh fehlgeschlagen ({r.status_code}): {r.text[:300]}")
    return r.json().get("access_token", "")


def resolve_access_token():
    """Access-Token bestimmen: direktes Secret ODER frisch via Refresh-Token.

    Rueckgabe (token, quelle). token == "" bedeutet: nicht konfiguriert -> DRY-RUN.
    Bei vorhandenen Refresh-Credentials, die aber scheitern, wird die Exception
    durchgereicht (echter Fehler statt stillem DRY-RUN).
    """
    direct = os.environ.get("PINTEREST_ACCESS_TOKEN", "").strip()
    if direct:
        return direct, "Secret PINTEREST_ACCESS_TOKEN"
    app_id = os.environ.get("PINTEREST_APP_ID", "").strip()
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "").strip()
    refresh_token = os.environ.get("PINTEREST_REFRESH_TOKEN", "").strip()
    if app_id and app_secret and refresh_token:
        return refresh_access_token(app_id, app_secret, refresh_token), "Refresh-Token"
    return "", "nicht konfiguriert"


def load(name, default):
    path = os.path.join(HERE, name)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save(name, data):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def resolve_board(session, name):
    """Sucht die Board-ID anhand des Namens (paginierte Liste)."""
    bookmark = None
    while True:
        params = {"page_size": 100}
        if bookmark:
            params["bookmark"] = bookmark
        r = session.get(f"{API}/boards", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        for b in data.get("items", []):
            if b.get("name", "").strip().lower() == name.strip().lower():
                return b["id"]
        bookmark = data.get("bookmark")
        if not bookmark:
            return None


def main():
    live = os.environ.get("PINTEREST_LIVE", "").strip().lower() == "true"
    try:
        token, token_source = resolve_access_token()
    except Exception as e:  # noqa: BLE001 - Refresh-Fehler klar melden
        print(f"FEHLER beim Token-Refresh: {e}", file=sys.stderr)
        if live:
            sys.exit(1)
        token, token_source = "", "Refresh fehlgeschlagen"
    dry = not live or not token

    cfg = load("config.json", {})
    pins = load("pins.json", [])
    # Zusaetzliche Pins, die nur im Notion-Tracker leben (alte offene Pins),
    # mit aufnehmen — nach Link dedupliziert.
    seen_links = {p["link"] for p in pins}
    for extra in load("extra_notion_pins.json", []):
        if extra.get("link") and extra["link"] not in seen_links:
            seen_links.add(extra["link"])
            pins.append(extra)
    ledger = load("posted.json", {})  # link -> {pin_id, ts}

    todo = [p for p in pins if p["link"] not in ledger]
    cap = int(cfg.get("posts_per_run", 2))
    batch = todo[:cap]

    print(f"Pins gesamt: {len(pins)} | schon gepostet: {len(ledger)} | "
          f"offen: {len(todo)} | dieser Lauf: {len(batch)} (max {cap})")
    if not dry:
        print(f"Token-Quelle: {token_source}")
    if dry:
        why = "PINTEREST_LIVE != 'true'" if token else f"kein Token ({token_source})"
        print(f"== DRY-RUN ({why}) — es wird NICHTS gepostet ==")
        for p in batch:
            print(f"  + [{p['id']}] {p['title']}  ->  {p['link']}")
        return

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})

    board_id = cfg.get("board_id") or resolve_board(session, cfg["board_name"])
    if not board_id:
        print(f"FEHLER: Board '{cfg.get('board_name')}' nicht gefunden. "
              f"Lege es auf Pinterest an oder setze 'board_id' in config.json.",
              file=sys.stderr)
        sys.exit(1)

    posted = 0
    for p in batch:
        body = {
            "board_id": board_id,
            "title": p["title"],
            "description": p["description"],
            "link": p["link"],
            "alt_text": p["title"][:500],
            "media_source": {"source_type": "image_url", "url": p["image"]},
        }
        r = session.post(f"{API}/pins", json=body, timeout=60)
        if r.status_code in (200, 201):
            pin_id = r.json().get("id", "?")
            ledger[p["link"]] = {"pin_id": pin_id, "ts": int(time.time())}
            posted += 1
            print(f"  OK  [{p['id']}] -> Pin {pin_id}")
            save("posted.json", ledger)  # nach jedem Pin sichern
            time.sleep(5)
        else:
            print(f"  FEHLER [{p['id']}] {r.status_code}: {r.text[:300]}",
                  file=sys.stderr)

    print(f"Fertig: {posted} Pin(s) gepostet.")


if __name__ == "__main__":
    main()
