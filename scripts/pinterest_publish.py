#!/usr/bin/env python3
"""Postet vorbereitete Pins ueber die offizielle Pinterest-API (v5).

Liest alle ``*/pins/queue.json`` (ausser ``cozy/`` — abgekoppelt, siehe
CLAUDE.md), tauscht den langlebigen Refresh-Token gegen einen kurzlebigen
Access-Token und veroeffentlicht die naechsten noch nicht geposteten Pins
(maximal ``MAX_PER_RUN`` pro Lauf). Jeder geposteten Eintrag wird mit
``"published": true`` markiert und bekommt seine ``pin_id`` — so wird nie
doppelt gepostet.

Board-Zuordnung pro Pin (erste Uebereinstimmung gewinnt):
  1. ``board_id`` direkt am Pin-Eintrag
  2. Env-Var ``PINTEREST_BOARD_ID_<SITE>`` (SITE = Ordnername in Grossbuchstaben,
     Bindestriche zu Unterstrichen, z. B. PINTEREST_BOARD_ID_SAISON_DEKO)
  3. Board-*Name* aus ``pinterest/boards.json`` -> per API in eine Board-ID
     aufgeloest (der bequeme Standardweg: keine IDs von Hand suchen)
  4. Env-Var ``PINTEREST_BOARD_ID`` (globales Fallback-Board)

Secrets kommen ausschliesslich aus Environment-Variablen (GitHub-Actions-Secrets):
  PINTEREST_APP_ID, PINTEREST_APP_SECRET, PINTEREST_REFRESH_TOKEN
  optional: PINTEREST_BOARD_ID, PINTEREST_BOARD_ID_<SITE>
Es wird niemals ein Secret ausgegeben.

Betriebsarten:
  python scripts/pinterest_publish.py            # normal posten
  python scripts/pinterest_publish.py --doctor   # nur pruefen (Token, Boards, Queues)
  python scripts/pinterest_publish.py --dry-run  # zeigen, was gepostet wuerde
  python scripts/pinterest_publish.py --list-boards
  python scripts/pinterest_publish.py --mark-published-only
        # markiert alle offenen Pins als veroeffentlicht, OHNE zu posten —
        # einmalig noetig, wenn die Pins bereits per Bulk-CSV hochgeladen wurden
        # und die API sie sonst ein zweites Mal anlegen wuerde.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.pinterest.com/v5"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOARDS_CONFIG = ROOT / "pinterest" / "boards.json"

# cozy/ (Cozylore) ist von der Seite abgekoppelt (einsprachig Deutsch,
# siehe CLAUDE.md) — die Queue bleibt liegen, wird aber nicht gepostet.
SKIP_SITES = {"cozy"}

# Pinterest empfiehlt Abstand zwischen Schreib-Requests; 2 s reichen locker.
SLEEP_BETWEEN_PINS = 2.0


class PinterestError(RuntimeError):
    """API-Fehler inklusive Response-Body (sonst sieht man nur 'HTTP 400')."""


def _request(url: str, data: bytes | None = None, headers: dict | None = None,
             method: str = "GET") -> dict:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace").strip()[:600]
        raise PinterestError(f"HTTP {exc.code} {exc.reason} — {body or '(leerer Body)'}") from None
    except urllib.error.URLError as exc:
        raise PinterestError(f"Netzwerkfehler: {exc.reason}") from None


def get_access_token(app_id: str, app_secret: str, refresh_token: str) -> str:
    """Tauscht den langlebigen Refresh-Token gegen einen Access-Token."""
    creds = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    body = urllib.parse.urlencode(
        {"grant_type": "refresh_token", "refresh_token": refresh_token}
    ).encode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    result = _request(f"{API_BASE}/oauth/token", body, headers, method="POST")
    token = result.get("access_token")
    if not token:
        raise PinterestError("Token-Antwort enthaelt kein access_token")
    return token


def list_boards(access_token: str) -> list[dict]:
    """Alle Boards des Kontos (mit Paginierung)."""
    headers = {"Authorization": f"Bearer {access_token}"}
    boards: list[dict] = []
    bookmark = ""
    while True:
        url = f"{API_BASE}/boards?page_size=100"
        if bookmark:
            url += "&bookmark=" + urllib.parse.quote(bookmark)
        result = _request(url, headers=headers)
        boards.extend(result.get("items", []))
        bookmark = result.get("bookmark") or ""
        if not bookmark:
            return boards


def create_pin(access_token: str, board_id: str, pin: dict) -> str:
    """Legt einen Pin an. Gibt die neue Pin-ID zurueck."""
    payload = {
        "board_id": board_id,
        "title": pin["title"][:100],
        "description": pin["description"][:800],
        "link": pin["link"],
        "media_source": {"source_type": "image_url", "url": pin["image_url"]},
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    result = _request(f"{API_BASE}/pins", json.dumps(payload).encode(), headers, method="POST")
    return result.get("id", "")


def find_queue_files() -> list[Path]:
    """Alle */pins/queue.json ausser den abgekoppelten Sites, stabil sortiert."""
    return sorted(
        qf for qf in ROOT.glob("*/pins/queue.json")
        if qf.relative_to(ROOT).parts[0] not in SKIP_SITES
    )


def load_board_names() -> dict:
    """pinterest/boards.json: {"default": "...", "sites": {"slug": "Board-Name"}}"""
    if not BOARDS_CONFIG.exists():
        return {}
    try:
        return json.loads(BOARDS_CONFIG.read_text())
    except Exception as exc:  # noqa: BLE001
        print(f"Warnung: {BOARDS_CONFIG.name} nicht lesbar ({exc}) — ignoriert.")
        return {}


def env_board(site: str) -> str:
    key = "PINTEREST_BOARD_ID_" + site.upper().replace("-", "_")
    return os.environ.get(key, "")


def board_for(pin: dict, site: str, name_to_id: dict, board_names: dict,
              default_board: str) -> tuple[str, str]:
    """Ziel-Board fuer einen Pin aufloesen. Gibt (board_id, Herkunft) zurueck."""
    if pin.get("board_id"):
        return pin["board_id"], "Pin-Eintrag"
    from_env = env_board(site)
    if from_env:
        return from_env, f"PINTEREST_BOARD_ID_{site.upper().replace('-', '_')}"
    wanted = (board_names.get("sites", {}) or {}).get(site) or board_names.get("default", "")
    if wanted:
        board_id = name_to_id.get(wanted.strip().lower())
        if board_id:
            return board_id, f'boards.json → "{wanted}"'
        print(f'  Warnung: Board "{wanted}" (fuer {site}) existiert nicht im Konto.')
    if default_board:
        return default_board, "PINTEREST_BOARD_ID"
    return "", "—"


def read_queues(queue_files: list[Path]) -> tuple[dict, list]:
    queues: dict[Path, list] = {}
    pending: list[tuple[Path, str, dict]] = []
    for qf in queue_files:
        try:
            data = json.loads(qf.read_text())
        except Exception as exc:  # noqa: BLE001
            print(f"Ueberspringe {qf}: nicht lesbar ({exc}).")
            continue
        queues[qf] = data
        site = qf.relative_to(ROOT).parts[0]
        for pin in data:
            if not pin.get("published"):
                pending.append((qf, site, pin))
    return queues, pending


def write_queues(queues: dict, touched: set) -> None:
    for qf in touched:
        qf.write_text(json.dumps(queues[qf], indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--doctor", action="store_true",
                    help="Nur pruefen: Token, Boards, Queue-Stand — postet nichts.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Zeigt, welche Pins auf welchem Board landen wuerden.")
    ap.add_argument("--list-boards", action="store_true",
                    help="Alle Boards des Kontos mit ID ausgeben.")
    ap.add_argument("--mark-published-only", action="store_true",
                    help="Alle offenen Pins als veroeffentlicht markieren, ohne zu posten.")
    ap.add_argument("--max", type=int, default=None,
                    help="Ueberschreibt MAX_PER_RUN fuer diesen Lauf.")
    args = ap.parse_args()

    queue_files = find_queue_files()
    queues, pending = read_queues(queue_files)

    if args.mark_published_only:
        touched = set()
        for qf, _site, pin in pending:
            pin["published"] = True
            pin.setdefault("pin_id", "")
            touched.add(qf)
        write_queues(queues, touched)
        print(f"{len(pending)} Pin(s) in {len(touched)} Queue(s) als veroeffentlicht "
              f"markiert (nichts gepostet).")
        return 0

    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    refresh_token = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    default_board = os.environ.get("PINTEREST_BOARD_ID", "")
    max_per_run = args.max if args.max is not None else int(os.environ.get("MAX_PER_RUN", "2"))

    missing = [
        name for name, val in {
            "PINTEREST_APP_ID": app_id,
            "PINTEREST_APP_SECRET": app_secret,
            "PINTEREST_REFRESH_TOKEN": refresh_token,
        }.items() if not val
    ]
    if missing:
        print(f"Fehlende Secrets: {', '.join(missing)}. "
              f"In Repo → Settings → Secrets and variables → Actions hinterlegen.")
        print("Kein Fehler — der Lauf endet einfach ohne zu posten.")
        return 0

    try:
        token = get_access_token(app_id, app_secret, refresh_token)
    except PinterestError as exc:
        print(f"Token-Austausch fehlgeschlagen: {exc}")
        print("Haeufigste Ursachen: Refresh-Token abgelaufen (max. 1 Jahr) oder fuer eine "
              "andere App erzeugt. Neu erzeugen mit scripts/pinterest_oauth.py.")
        return 1
    print("Access-Token erhalten.")

    try:
        boards = list_boards(token)
    except PinterestError as exc:
        print(f"Boards konnten nicht geladen werden: {exc}")
        boards = []
    name_to_id = {b.get("name", "").strip().lower(): b.get("id", "") for b in boards}

    if args.list_boards:
        print(f"\n{len(boards)} Board(s) im Konto:")
        for b in boards:
            print(f"  {b.get('id')}  {b.get('name')}  ({b.get('pin_count', '?')} Pins)")
        return 0

    board_names = load_board_names()

    if args.doctor:
        print(f"\nBoards im Konto ({len(boards)}):")
        for b in boards:
            print(f"  {b.get('id')}  {b.get('name')}  ({b.get('pin_count', '?')} Pins)")
        print(f"\nQueues ({len(queue_files)} Datei(en), cozy/ ausgenommen):")
        total = 0
        for qf in queue_files:
            data = queues.get(qf, [])
            open_n = sum(1 for p in data if not p.get("published"))
            total += open_n
            site = qf.relative_to(ROOT).parts[0]
            board_id, source = board_for({}, site, name_to_id, board_names, default_board)
            state = f"→ {board_id} ({source})" if board_id else "→ KEIN BOARD ZUGEORDNET"
            print(f"  {site:<14} {open_n:>3} offen / {len(data):>3} gesamt  {state}")
        print(f"\nInsgesamt {total} offene Pin(s). MAX_PER_RUN = {max_per_run}.")
        if total:
            days = -(-total // max(max_per_run, 1))
            print(f"Bei 2 Laeufen/Tag waeren das rund {-(-days // 2)} Tag(e) bis alles drausssen ist.")
        return 0

    if not pending:
        print("Alle Queues abgearbeitet — keine offenen Pins.")
        return 0

    posted = 0
    failed = 0
    touched: set[Path] = set()
    for qf, site, pin in pending:
        if posted >= max_per_run:
            break
        board_id, source = board_for(pin, site, name_to_id, board_names, default_board)
        if not board_id:
            print(f"Kein Board fuer [{site}] — uebersprungen: {pin.get('title')!r}")
            continue
        if args.dry_run:
            print(f"[dry-run] [{site}] {pin['title']!r} → Board {board_id} ({source})")
            posted += 1
            continue
        try:
            pin_id = create_pin(token, board_id, pin)
            pin["published"] = True
            pin["pin_id"] = pin_id
            posted += 1
            touched.add(qf)
            print(f"Gepostet [{site}]: {pin['title']!r} → Pin {pin_id} (Board {board_id})")
        except PinterestError as exc:
            failed += 1
            print(f"Fehlgeschlagen [{site}] {pin.get('title')!r}: {exc}")
        time.sleep(SLEEP_BETWEEN_PINS)

    write_queues(queues, touched)
    print(f"Fertig. {posted} Pin(s) gepostet, {failed} Fehler, "
          f"{len(pending) - posted} noch offen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
