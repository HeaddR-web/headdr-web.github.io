#!/usr/bin/env python3
"""Erzeugt einmalig den Pinterest-Refresh-Token fuer die API-Pipeline.

Laeuft LOKAL auf dem eigenen Rechner (nicht in GitHub Actions) und braucht nur
App-ID und App-Secret der Pinterest-Entwickler-App
(<https://developers.pinterest.com/apps/>).

Ablauf:
  1. Skript starten:
         python3 scripts/pinterest_oauth.py --app-id <ID> --app-secret <SECRET>
     (ohne Argumente fragt es beides interaktiv ab — das Secret verdeckt)
  2. Es oeffnet einen kleinen lokalen Webserver auf http://localhost:8085/callback
     und gibt eine Pinterest-Login-URL aus. Die im Browser oeffnen und die App
     autorisieren.
  3. Pinterest leitet auf localhost zurueck, das Skript tauscht den Code gegen
     Access- und Refresh-Token und gibt den REFRESH-TOKEN aus.

Wichtig:
  - In der Entwickler-App muss **http://localhost:8085/callback** als
    Redirect-URI eingetragen sein (exakt, inkl. Pfad), sonst lehnt Pinterest ab.
  - Der ausgegebene Refresh-Token ist ein Secret: nur in
    Repo → Settings → Secrets and variables → Actions als
    PINTEREST_REFRESH_TOKEN hinterlegen. Niemals ins Repo committen,
    nie in Chats/Issues posten. Er gilt max. 1 Jahr, danach neu erzeugen.
  - Ohne lokalen Browser: --no-server benutzen, die URL manuell oeffnen und den
    ``code``-Parameter aus der Redirect-URL mit --code uebergeben.
"""

import argparse
import base64
import getpass
import json
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

AUTH_URL = "https://www.pinterest.com/oauth/"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
DEFAULT_REDIRECT = "http://localhost:8085/callback"

# Genau die Rechte, die die Pipeline braucht — nicht mehr.
SCOPES = "boards:read,pins:read,pins:write"

_received = {}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 — von BaseHTTPRequestHandler vorgegeben
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        _received.update({k: v[0] for k, v in params.items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        ok = "code" in _received
        msg = ("Autorisierung erhalten — dieses Fenster kann geschlossen werden."
               if ok else "Kein Code erhalten. Bitte im Terminal nachsehen.")
        self.wfile.write(f"<html><body style='font:16px sans-serif;padding:3rem'>"
                         f"<p>{msg}</p></body></html>".encode())

    def log_message(self, *_args):  # Zugriffslog unterdruecken
        return


def authorize_url(app_id: str, redirect_uri: str, state: str) -> str:
    query = urllib.parse.urlencode({
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    })
    return f"{AUTH_URL}?{query}"


def exchange_code(app_id: str, app_secret: str, code: str, redirect_uri: str) -> dict:
    creds = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL, data=body, method="POST",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace").strip()[:600]
        raise SystemExit(f"Token-Austausch fehlgeschlagen: HTTP {exc.code} — {detail}")


def wait_for_code(port: int, state: str) -> str:
    server = HTTPServer(("localhost", port), _Handler)
    print(f"Warte auf die Weiterleitung von Pinterest (localhost:{port}) … "
          f"Abbruch mit Strg+C.")
    try:
        while "code" not in _received and "error" not in _received:
            server.handle_request()
    finally:
        server.server_close()
    if "error" in _received:
        raise SystemExit(f"Pinterest hat abgelehnt: {_received.get('error')} "
                         f"{_received.get('error_description', '')}")
    if _received.get("state") != state:
        raise SystemExit("state stimmt nicht ueberein — Abbruch (moeglicher CSRF).")
    return _received["code"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app-id", help="App-ID der Pinterest-Entwickler-App")
    ap.add_argument("--app-secret", help="App-Secret (besser interaktiv eingeben)")
    ap.add_argument("--redirect-uri", default=DEFAULT_REDIRECT,
                    help=f"Muss in der App hinterlegt sein (Standard: {DEFAULT_REDIRECT})")
    ap.add_argument("--code", help="Bereits erhaltener ?code=… aus der Redirect-URL")
    ap.add_argument("--no-server", action="store_true",
                    help="Keinen lokalen Server starten — nur die Login-URL ausgeben")
    args = ap.parse_args()

    app_id = args.app_id or input("Pinterest App-ID: ").strip()
    app_secret = args.app_secret or getpass.getpass("Pinterest App-Secret (verdeckt): ").strip()
    if not app_id or not app_secret:
        raise SystemExit("App-ID und App-Secret werden beide gebraucht.")

    code = args.code
    if not code:
        state = secrets.token_urlsafe(16)
        url = authorize_url(app_id, args.redirect_uri, state)
        print("\nDiese URL im Browser oeffnen und die App autorisieren:\n")
        print(url)
        print()
        if args.no_server:
            print("Danach den Wert des ?code=… Parameters aus der Redirect-URL kopieren "
                  "und das Skript erneut mit --code <CODE> aufrufen.")
            return 0
        port = urllib.parse.urlparse(args.redirect_uri).port or 80
        code = wait_for_code(port, state)
        print("Code erhalten, tausche gegen Token …")

    result = exchange_code(app_id, app_secret, code, args.redirect_uri)
    refresh = result.get("refresh_token", "")
    if not refresh:
        raise SystemExit(f"Keine refresh_token in der Antwort: {result}")

    print("\n" + "=" * 68)
    print("REFRESH-TOKEN (Secret — nur in GitHub Secrets einfuegen, nirgends sonst):")
    print()
    print(refresh)
    print()
    print("Als Repo-Secret hinterlegen:")
    print("  Settings → Secrets and variables → Actions → New repository secret")
    print("  Name:  PINTEREST_REFRESH_TOKEN")
    print("=" * 68)
    exp = result.get("refresh_token_expires_in")
    if exp:
        print(f"Gueltig ca. {int(exp) // 86400} Tage.")
    print("Nicht committen, nicht in Chats/Issues posten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
