#!/usr/bin/env python3
"""Publish queued cozy pins to Pinterest via the official API (v5).

Reads cozy/pins/queue.json, refreshes a short-lived access token from the
stored refresh token, then publishes the next unpublished pins (up to
MAX_PER_RUN). Each published entry is marked so it is never posted twice.

Secrets are read from environment variables (set as GitHub Actions secrets):
  PINTEREST_APP_ID, PINTEREST_APP_SECRET, PINTEREST_REFRESH_TOKEN, PINTEREST_BOARD_ID

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
QUEUE_PATH = Path("cozy/pins/queue.json")


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


def main() -> int:
    app_id = os.environ.get("PINTEREST_APP_ID", "")
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    refresh_token = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    board_id = os.environ.get("PINTEREST_BOARD_ID", "")
    max_per_run = int(os.environ.get("MAX_PER_RUN", "2"))

    missing = [
        name
        for name, val in {
            "PINTEREST_APP_ID": app_id,
            "PINTEREST_APP_SECRET": app_secret,
            "PINTEREST_REFRESH_TOKEN": refresh_token,
            "PINTEREST_BOARD_ID": board_id,
        }.items()
        if not val
    ]
    if missing:
        print(f"Missing secrets: {', '.join(missing)}. Add them in repo Settings → Secrets.")
        return 1

    if not QUEUE_PATH.exists():
        print(f"No queue file at {QUEUE_PATH}; nothing to do.")
        return 0

    queue = json.loads(QUEUE_PATH.read_text())
    pending = [p for p in queue if not p.get("published")]
    if not pending:
        print("Queue empty — no unpublished pins.")
        return 0

    token = get_access_token(app_id, app_secret, refresh_token)

    posted = 0
    for pin in pending:
        if posted >= max_per_run:
            break
        try:
            pin_id = create_pin(token, board_id, pin)
            pin["published"] = True
            pin["pin_id"] = pin_id
            posted += 1
            print(f"Published: {pin['title']!r} -> pin {pin_id}")
        except Exception as exc:  # noqa: BLE001 — keep going on a single failure
            print(f"Failed to publish {pin.get('title')!r}: {exc}")

    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n")
    print(f"Done. Published {posted} pin(s) this run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
