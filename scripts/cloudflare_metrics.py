#!/usr/bin/env python3
"""Zieht KPIs aus Cloudflare Web Analytics (GraphQL) und schreibt data/metrics.json.

Das Dashboard (dashboard.html) liest diese Datei und zeigt die Live-Zahlen an.
Läuft in CI (.github/workflows/metrics.yml). Keine Secrets im Code.

Benötigte Umgebungsvariablen (als GitHub-Secrets hinterlegen):
  CLOUDFLARE_API_TOKEN   – Token mit Recht "Account Analytics: Read"
  CLOUDFLARE_ACCOUNT_ID  – Account-ID (Cloudflare-Dashboard, rechte Spalte)
  CLOUDFLARE_SITE_TAG    – Site-Tag der Web-Analytics-Property

Fehlt etwas, schreibt das Script eine Platzhalter-Datei und endet sauber (Exit 0),
damit weder CI noch Dashboard hart fehlschlagen.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

ENDPOINT = "https://api.cloudflare.com/client/v4/graphql"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "metrics.json")

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
SITE = os.environ.get("CLOUDFLARE_SITE_TAG", "").strip()


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def write(data):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"geschrieben: {OUT}")


def placeholder(reason):
    write({
        "updated": iso(datetime.now(timezone.utc)),
        "status": "no-data",
        "reason": reason,
        "ranges": {}, "topPages": [], "topReferrers": [],
    })


def gql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


QUERY = """
query ($account: String!, $site: String!, $since7: Time!, $since30: Time!, $until: Time!) {
  viewer {
    accounts(filter: { accountTag: $account }) {
      d7: rumPageloadEventsAdaptiveGroups(
        filter: { siteTag: $site, datetime_geq: $since7, datetime_leq: $until }
        limit: 1
      ) { count sum { visits } }
      d30: rumPageloadEventsAdaptiveGroups(
        filter: { siteTag: $site, datetime_geq: $since30, datetime_leq: $until }
        limit: 1
      ) { count sum { visits } }
      pages: rumPageloadEventsAdaptiveGroups(
        filter: { siteTag: $site, datetime_geq: $since7, datetime_leq: $until }
        limit: 8, orderBy: [count_DESC]
      ) { count dimensions { requestPath } }
      refs: rumPageloadEventsAdaptiveGroups(
        filter: { siteTag: $site, datetime_geq: $since7, datetime_leq: $until }
        limit: 8, orderBy: [count_DESC]
      ) { count dimensions { refererHost } }
    }
  }
}
"""


def main():
    if not (TOKEN and ACCOUNT and SITE):
        placeholder("Secrets fehlen (CLOUDFLARE_API_TOKEN / _ACCOUNT_ID / _SITE_TAG)")
        print("Hinweis: Secrets nicht gesetzt — Platzhalter geschrieben.", file=sys.stderr)
        return

    now = datetime.now(timezone.utc)
    variables = {
        "account": ACCOUNT, "site": SITE,
        "since7": iso(now - timedelta(days=7)),
        "since30": iso(now - timedelta(days=30)),
        "until": iso(now),
    }
    try:
        res = gql(QUERY, variables)
    except Exception as e:  # Netzwerk/HTTP
        placeholder(f"API-Aufruf fehlgeschlagen: {e}")
        print(f"FEHLER: {e}", file=sys.stderr)
        return

    if res.get("errors"):
        placeholder("GraphQL-Fehler: " + json.dumps(res["errors"])[:300])
        print("GraphQL-Fehler:", res["errors"], file=sys.stderr)
        return

    try:
        acc = res["data"]["viewer"]["accounts"][0]
    except (KeyError, IndexError):
        placeholder("Keine Account-/Site-Daten — Account-ID/Site-Tag prüfen.")
        return

    def total(node):
        n = (node or [{}])
        n = n[0] if n else {}
        return {"views": (n.get("count") or 0), "visits": ((n.get("sum") or {}).get("visits") or 0)}

    data = {
        "updated": iso(now),
        "status": "ok",
        "ranges": {"7d": total(acc.get("d7")), "30d": total(acc.get("d30"))},
        "topPages": [
            {"path": p["dimensions"]["requestPath"], "views": p["count"]}
            for p in (acc.get("pages") or [])
        ],
        "topReferrers": [
            {"host": r["dimensions"]["refererHost"] or "(direkt)", "views": r["count"]}
            for r in (acc.get("refs") or [])
        ],
    }
    write(data)
    print(f"7d: {data['ranges']['7d']} | 30d: {data['ranges']['30d']}")


if __name__ == "__main__":
    main()
