#!/usr/bin/env python3
"""OAuth-Tausch fuer Pinterest — komplett in GitHub Actions, ohne Terminal.

Gegenstueck zu ``pinterest_oauth.py`` (das lokal mit localhost-Callback laeuft).
Hier uebernimmt der Actions-Runner den Tausch; der Browser braucht nur eine
oeffentliche Redirect-URL, auf der der ``code``-Parameter in der Adresszeile
ablesbar ist — dafuer reicht die eigene Startseite, GitHub Pages ignoriert
unbekannte Query-Parameter (derselbe Mechanismus wie bei ``?pin=…``).

Zwei Schritte, beide ueber "Run workflow":

  url       Baut die Pinterest-Login-URL und gibt sie im Log aus.
            Braucht nur die App-ID (kein Secret — die App-ID ist die
            oeffentliche Client-Kennung und wird deshalb als Eingabefeld
            uebergeben, nicht als Secret: Actions maskiert Secret-Werte im
            Log, die URL waere sonst unbrauchbar).

  exchange  Tauscht den ``code`` aus der Adresszeile gegen Access- und
            Refresh-Token, schreibt den Refresh-Token (und die App-ID) direkt
            als Repo-Secret ueber die GitHub-API und listet zur Kontrolle die
            Boards des Kontos auf. Der Token wird nie ausgegeben.

Der Refresh-Token verlaesst damit nie den Runner. Noetig sind:
  PINTEREST_APP_SECRET  Repo-Secret
  GH_SECRETS_PAT        Repo-Secret: Fine-grained PAT auf dieses Repo mit
                        "Secrets: Read and write" (nur dafuer).
"""

import argparse
import base64
import json
import os
import secrets as pysecrets
import sys
import urllib.error
import urllib.parse
import urllib.request

AUTH_URL = "https://www.pinterest.com/oauth/"
TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
BOARDS_URL = "https://api.pinterest.com/v5/boards?page_size=100"
GITHUB_API = "https://api.github.com"
SCOPES = "boards:read,pins:read,pins:write"


def _json_request(url, data=None, headers=None, method="GET"):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace").strip()[:600]
        raise SystemExit(f"HTTP {exc.code} {exc.reason} — {body or '(leerer Body)'}")


def cmd_url(args) -> int:
    state = pysecrets.token_urlsafe(12)
    query = urllib.parse.urlencode({
        "client_id": args.app_id,
        "redirect_uri": args.redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    })
    print("=" * 72)
    print("SCHRITT 1 — diese URL im Browser oeffnen und die App autorisieren:")
    print()
    print(f"{AUTH_URL}?{query}")
    print()
    print("Danach landest du auf der Startseite. In der Adresszeile steht:")
    print(f"  {args.redirect_uri}?code=DEIN-CODE&state={state}")
    print()
    print("Den Wert hinter 'code=' kopieren (bis zum '&', ohne das '&').")
    print(f"Zur Kontrolle: 'state' muss {state} sein.")
    print()
    print("Dann diesen Workflow nochmal starten, Schritt '2-code-eintauschen',")
    print("den Code ins Feld einfuegen. Der Code ist nur wenige Minuten gueltig,")
    print("also zuegig weitermachen — sonst einfach Schritt 1 wiederholen.")
    print("=" * 72)
    return 0


def set_repo_secret(repo: str, pat: str, name: str, value: str) -> None:
    """Setzt ein Actions-Secret ueber die GitHub-API (libsodium-verschluesselt)."""
    from nacl import encoding, public  # pip install pynacl

    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "bethathost-oauth-setup",
    }
    key = _json_request(f"{GITHUB_API}/repos/{repo}/actions/secrets/public-key",
                        headers=headers)
    sealed = public.SealedBox(
        public.PublicKey(key["key"].encode(), encoding.Base64Encoder)
    ).encrypt(value.encode())
    payload = json.dumps({
        "encrypted_value": base64.b64encode(sealed).decode(),
        "key_id": key["key_id"],
    }).encode()
    _json_request(f"{GITHUB_API}/repos/{repo}/actions/secrets/{name}",
                  data=payload, headers={**headers, "Content-Type": "application/json"},
                  method="PUT")
    print(f"  ✓ Secret {name} gesetzt.")


def cmd_exchange(args) -> int:
    app_secret = os.environ.get("PINTEREST_APP_SECRET", "")
    pat = os.environ.get("GH_SECRETS_PAT", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    missing = [n for n, v in {"PINTEREST_APP_SECRET": app_secret,
                              "GH_SECRETS_PAT": pat}.items() if not v]
    if missing:
        raise SystemExit(
            f"Fehlende Secrets: {', '.join(missing)}. "
            "Unter Settings → Secrets and variables → Actions anlegen."
        )

    creds = base64.b64encode(f"{args.app_id}:{app_secret}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": args.code.strip(),
        "redirect_uri": args.redirect_uri,
    }).encode()
    result = _json_request(TOKEN_URL, data=body, method="POST", headers={
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/x-www-form-urlencoded",
    })

    refresh = result.get("refresh_token", "")
    access = result.get("access_token", "")
    if not refresh:
        raise SystemExit("Antwort enthaelt keinen refresh_token — Code abgelaufen "
                         "oder schon benutzt? Schritt 1 wiederholen.")
    # Beide Werte sofort maskieren, damit sie auch bei einem spaeteren
    # Fehler-Traceback nicht im Log auftauchen koennen.
    print(f"::add-mask::{refresh}")
    print(f"::add-mask::{access}")
    print("Token erhalten.")

    print("\nSecrets schreiben:")
    set_repo_secret(repo, pat, "PINTEREST_REFRESH_TOKEN", refresh)
    set_repo_secret(repo, pat, "PINTEREST_APP_ID", args.app_id)

    exp = result.get("refresh_token_expires_in")
    if exp:
        print(f"\nRefresh-Token gueltig ca. {int(exp) // 86400} Tage.")

    print("\nGegenprobe — Boards des Kontos:")
    boards = _json_request(BOARDS_URL, headers={"Authorization": f"Bearer {access}"})
    items = boards.get("items", [])
    if not items:
        print("  (keine Boards gefunden — stimmt das Konto?)")
    for b in items:
        print(f"  {b.get('id')}  {b.get('name')}  ({b.get('pin_count', '?')} Pins)")
    print("\nFertig. Der genaue Board-Name gehoert nach pinterest/boards.json.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["url", "exchange"])
    ap.add_argument("--app-id", required=True)
    ap.add_argument("--code", default="")
    ap.add_argument("--redirect-uri", default="https://bethathost.de/")
    args = ap.parse_args()

    if args.command == "url":
        return cmd_url(args)
    if not args.code:
        raise SystemExit("Fuer 'exchange' fehlt der Code aus der Adresszeile.")
    return cmd_exchange(args)


if __name__ == "__main__":
    sys.exit(main())
