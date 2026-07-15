#!/usr/bin/env python3
"""Publish queued pins to Pinterest via the official API (v5).

Scans every ``*/pins/queue.json`` in the repo (currently ``cozy/`` and
``girlsnight/``), refreshes a short-lived access token from the stored refresh
token, then publishes the next unpublished pins across all queues (up to
MAX_PER_RUN total). Each published entry is marked so it is never posted twice.

Board selection per pin (first match wins):
  1. ``board_id`` on the individual pin entry
  2. ``PINTEREST_BOARD_ID_<SITE>`` env var, where <SITE> is the top-level
     folder name upper-cased (e.g. PINTEREST_BOARD_ID_GIRLSNIGHT)
  3. ``PINTEREST_BOARD_ID`` (the default board)

Secrets are read from environment variables (set as GitHub Actions secrets):
  PINTEREST_APP_ID, PINTEREST_APP_SECRET, PINTEREST_REFRESH_TOKEN,
  PINTEREST_BOARD_ID  (+ optional PINTEREST_BOARD_ID_<SITE> overrides)

No secret is ever printed.
"""

import base64
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.pinterest.com/v5"


def _post(url: str, data: bytes, headers: dict) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get_access_token(app_id: str, app_secret: str, refresh_token: str) -> str:
    """Exchange the long-lived refresh token for a short-lived access token."""
    creds = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    body = urllib.parse.urlencode(
        {"grant_type": "refresh_token", "refresh_token": refresh_token}
    ).encode()
    headers = {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    result = _post(f"{API_BASE}/oauth/token", body, headers)
    token = result.get("access_token")
    if not token:
        raise RuntimeError("No access_token in token response")
    return token


def create_pin(access_token: str, board_id: str, pin: dict) -> str:
    """Create one pin. Returns the new pin id."""
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
    result = _post(f"{API_BASE}/pins", json.dumps(payload).encode(), headers)
    return result.get("id", "")


def find_queue_files() -> list[Path]:
    """Return every */pins/queue.json in the repo, sorted for stable order."""
    return sorted(Path(".").glob("*/pins/queue.json"))


def board_for(pin: dict, site: str, default_board: str) -> str:
    """Resolve the destination board id for a pin (see module docstring)."""
    if pin.get("board_id"):
        return pin["board_id"]
    site_board = os.environ.get(f"PINTEREST_BOARD_ID_{site.upper()}")
    if site_board:
        return site_board
    return default_board


def main() -> int:
    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    refresh_token = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    default_board = os.environ.get("PINTEREST_BOARD_ID", "")
    max_per_run = int(os.environ.get("MAX_PER_RUN", "2"))

    missing = [
        name
        for name, val in {
            "PINTEREST_APP_ID": app_id,
            "PINTEREST_APP_SECRET": app_secret,
            "PINTEREST_REFRESH_TOKEN": refresh_token,
            "PINTEREST_BOARD_ID": default_board,
        }.items()
        if not val
    ]
    if missing:
        print(f"Missing secrets: {', '.join(missing)}. Add them in repo Settings → Secrets.")
        return 0

    queue_files = find_queue_files()
    if not queue_files:
        print("No */pins/queue.json files found; nothing to do.")
        return 0

    # Load every queue and build a flat work list of pending pins.
    queues: dict[Path, list] = {}
    pending: list[tuple[Path, str, dict]] = []  # (queue_path, site, pin)
    for qf in queue_files:
        try:
            data = json.loads(qf.read_text())
        except Exception as exc:  # noqa: BLE001
            print(f"Skipping {qf}: cannot parse ({exc}).")
            continue
        queues[qf] = data
        site = qf.parts[0]  # top-level folder, e.g. "cozy" or "girlsnight"
        for pin in data:
            if not pin.get("published"):
                pending.append((qf, site, pin))

    if not pending:
        print("All queues empty — no unpublished pins.")
        return 0

    token = get_access_token(app_id, app_secret, refresh_token)

    posted = 0
    touched: set[Path] = set()
    for qf, site, pin in pending:
        if posted >= max_per_run:
            break
        board_id = board_for(pin, site, default_board)
        try:
            pin_id = create_pin(token, board_id, pin)
            pin["published"] = True
            pin["pin_id"] = pin_id
            posted += 1
            touched.add(qf)
            print(f"Published [{site}]: {pin['title']!r} -> pin {pin_id}")
        except Exception as exc:  # noqa: BLE001 — keep going on a single failure
            print(f"Failed to publish {pin.get('title')!r}: {exc}")

    for qf in touched:
        qf.write_text(json.dumps(queues[qf], indent=2, ensure_ascii=False) + "\n")

    print(f"Done. Published {posted} pin(s) this run across {len(touched)} queue(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
