#!/usr/bin/env python3
"""Pinterest-API-Token (v5) bequem erzeugen — ohne curl.

Ablauf (einmalig):
  1. App anlegen: https://developers.pinterest.com/  -> "Connect app".
     - Scopes aktivieren: boards:read, pins:read, pins:write
     - Redirect-URI eintragen, z. B.:  https://bethathost.de/
     - App-ID (client_id) und App-Secret notieren.
  2. Dieses Skript starten:
        python pinterest/get_token.py
     (oder App-ID/Secret/Redirect direkt als Argumente/ENV uebergeben)
  3. Den angezeigten Link oeffnen, mit deinem Pinterest-Konto bestaetigen.
  4. Pinterest leitet auf deine Redirect-URI weiter, z. B.:
        https://bethathost.de/?code=abc123...
     Die GANZE Adresse (oder nur den code-Wert) hier einfuegen.
  5. Das Skript tauscht den Code gegen Access- und Refresh-Token.

Den ACCESS-TOKEN dann als GitHub-Secret PINTEREST_ACCESS_TOKEN hinterlegen.
(Access-Token laufen nach ~30 Tagen ab; mit dem Refresh-Token laesst sich ein
neuer holen — sag Bescheid, dann baue ich das Auto-Refresh in den Workflow.)

Nur Standardbibliothek + requests. Es werden KEINE Tokens gespeichert/committet.
"""
import argparse
import base64
import os
import sys
import urllib.parse

import requests

AUTH_URL = "https://www.pinterest.com/oauth/"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
SCOPES = "boards:read,pins:read,pins:write"


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val or (default or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-id", default=os.environ.get("PINTEREST_APP_ID"))
    ap.add_argument("--app-secret", default=os.environ.get("PINTEREST_APP_SECRET"))
    ap.add_argument("--redirect-uri", default=os.environ.get("PINTEREST_REDIRECT_URI",
                                                             "https://bethathost.de/"))
    args = ap.parse_args()

    app_id = args.app_id or ask("Pinterest App-ID (client_id)")
    app_secret = args.app_secret or ask("Pinterest App-Secret")
    redirect_uri = args.redirect_uri or ask("Redirect-URI", "https://bethathost.de/")
    if not (app_id and app_secret and redirect_uri):
        print("Abbruch: App-ID, App-Secret und Redirect-URI sind noetig.", file=sys.stderr)
        sys.exit(1)

    # 1) Autorisierungs-Link bauen und anzeigen
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
    }
    print("\n1) Diesen Link im Browser oeffnen und mit Pinterest bestaetigen:\n")
    print("   " + AUTH_URL + "?" + urllib.parse.urlencode(params))
    print(f"\n   (Danach wirst du auf {redirect_uri}?code=... weitergeleitet.)\n")

    # 2) Code entgegennehmen (ganze URL oder nur der Code)
    raw = ask("2) Weitergeleitete Adresse ODER nur den code-Wert hier einfuegen")
    code = raw
    if "code=" in raw:
        q = urllib.parse.urlparse(raw).query
        code = urllib.parse.parse_qs(q).get("code", [""])[0]
    if not code:
        print("Abbruch: kein Code erkannt.", file=sys.stderr)
        sys.exit(1)

    # 3) Code gegen Token tauschen (HTTP Basic mit client_id:client_secret)
    basic = base64.b64encode(f"{app_id}:{app_secret}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {basic}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "authorization_code", "code": code,
              "redirect_uri": redirect_uri},
        timeout=30,
    )
    if r.status_code != 200:
        print(f"\nFEHLER {r.status_code}: {r.text[:500]}", file=sys.stderr)
        print("Tipp: Redirect-URI muss EXAKT der in der App hinterlegten entsprechen.",
              file=sys.stderr)
        sys.exit(1)

    tok = r.json()
    print("\n=== ERFOLG ===")
    print("ACCESS-TOKEN  (-> GitHub-Secret PINTEREST_ACCESS_TOKEN):\n")
    print("   " + tok.get("access_token", "?"))
    if tok.get("refresh_token"):
        print("\nREFRESH-TOKEN (empfohlen — laeuft nie ab):\n")
        print("   " + tok["refresh_token"])
    print("\n--- Im Repo hinterlegen: Settings -> Secrets and variables -> Actions ---")
    print("Empfohlen (Auto-Refresh, kein Ablauf): diese 3 Secrets setzen")
    print("   PINTEREST_APP_ID       = deine App-ID")
    print("   PINTEREST_APP_SECRET   = dein App-Secret")
    print("   PINTEREST_REFRESH_TOKEN= der Refresh-Token oben")
    print("Alternativ (einfach, laeuft ~30 Tage ab):")
    print("   PINTEREST_ACCESS_TOKEN = der Access-Token oben")
    print("In beiden Faellen zusaetzlich: Variable PINTEREST_LIVE = true")


if __name__ == "__main__":
    main()
