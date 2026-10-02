#!/usr/bin/env python3
"""Besucher (Cloudflare) und Google-Suche (Search Console) als Bericht ins Repo.

Warum: Bis Oktober 2026 kannte niemand die Besucherzahlen der Seite. Gemessen
wurde nur Pinterest (8 Klicks zur Seite in 30 Tagen) - ob Google ueberhaupt
Besucher schickt und welche Seiten indexiert sind, wusste keiner. Ohne diese
Zahlen ist jede Entscheidung geraten.

Schreibt statistik/WEB.md (lesbar) und statistik/web.json (Rohdaten). Der
Git-Verlauf beider Dateien ist die Zeitreihe. Jeder Teil laeuft nur, wenn
seine Secrets gesetzt sind; fehlt etwas, steht im Bericht, was fehlt.

Cloudflare Web Analytics (GraphQL, nur lesend):
  CF_API_TOKEN   API-Token mit "Account Analytics: Read"
  CF_ACCOUNT_ID  Konto-ID (rechts unten auf der Cloudflare-Uebersicht)

Google Search Console (Dienstkonto):
  GSC_SERVICE_ACCOUNT  komplette JSON-Schluesseldatei des Dienstkontos. Das
                       Dienstkonto muss in der Search Console als Nutzer der
                       Property eingetragen sein ("Inhaber", damit es die
                       Sitemap einreichen darf).
  Liest Klicks/Impressionen/Position je Seite und Suchbegriff, den
  Indexierungsstatus jeder URL aus sitemap.xml (URL-Pruefung) und reicht die
  Sitemap ein, falls sie dort noch fehlt.

Aufruf: python3 scripts/web_stats.py  (in CI: .github/workflows/web-stats.yml)
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZIEL = ROOT / "statistik"
HOST = "bethathost.de"
TAGE = 28


def post_json(url, daten, headers):
    req = urllib.request.Request(url, data=json.dumps(daten).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


# ---------------------------------------------------------------- Cloudflare
CF_QUERY = """
query($acc: String!, $von: Date!, $bis: Date!, $host: String!) {
  viewer { accounts(filter: {accountTag: $acc}) {
    tage: rumPageloadEventsAdaptiveGroups(limit: 100, orderBy: [date_ASC],
          filter: {date_geq: $von, date_leq: $bis, requestHost: $host}) {
      count sum { visits } dimensions { date } }
    seiten: rumPageloadEventsAdaptiveGroups(limit: 25, orderBy: [sum_visits_DESC],
          filter: {date_geq: $von, date_leq: $bis, requestHost: $host}) {
      count sum { visits } dimensions { requestPath } }
    quellen: rumPageloadEventsAdaptiveGroups(limit: 15, orderBy: [sum_visits_DESC],
          filter: {date_geq: $von, date_leq: $bis, requestHost: $host}) {
      count sum { visits } dimensions { refererHost } }
    geraete: rumPageloadEventsAdaptiveGroups(limit: 5, orderBy: [sum_visits_DESC],
          filter: {date_geq: $von, date_leq: $bis, requestHost: $host}) {
      count sum { visits } dimensions { deviceType } }
  } }
}"""


def cloudflare():
    token, konto = os.environ.get("CF_API_TOKEN"), os.environ.get("CF_ACCOUNT_ID")
    if not token or not konto:
        return {"fehlt": "Secrets CF_API_TOKEN und CF_ACCOUNT_ID"}
    bis = dt.date.today()
    von = bis - dt.timedelta(days=TAGE - 1)
    r = post_json("https://api.cloudflare.com/client/v4/graphql",
                  {"query": CF_QUERY, "variables": {"acc": konto, "von": von.isoformat(),
                                                    "bis": bis.isoformat(), "host": HOST}},
                  {"Authorization": f"Bearer {token}"})
    if r.get("errors"):
        return {"fehler": "; ".join(e.get("message", "?") for e in r["errors"])}
    a = r["data"]["viewer"]["accounts"][0]
    zeile = lambda g, k: {"wert": g["dimensions"][k] or "(direkt)", "besuche": g["sum"]["visits"],
                          "aufrufe": g["count"]}
    return {
        "von": von.isoformat(), "bis": bis.isoformat(),
        "tage": [{"datum": g["dimensions"]["date"], "besuche": g["sum"]["visits"], "aufrufe": g["count"]}
                 for g in a["tage"]],
        "seiten": [zeile(g, "requestPath") for g in a["seiten"]],
        "quellen": [zeile(g, "refererHost") for g in a["quellen"]],
        "geraete": [zeile(g, "deviceType") for g in a["geraete"]],
    }


# ------------------------------------------------------------ Search Console
def gsc_sitzung():
    roh = os.environ.get("GSC_SERVICE_ACCOUNT")
    if not roh:
        return None
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    cred = service_account.Credentials.from_service_account_info(
        json.loads(roh), scopes=["https://www.googleapis.com/auth/webmasters"])
    return AuthorizedSession(cred)


def search_console():
    s = gsc_sitzung()
    if s is None:
        return {"fehlt": "Secret GSC_SERVICE_ACCOUNT"}
    api = "https://www.googleapis.com/webmasters/v3"
    seiten = s.get(f"{api}/sites").json().get("siteEntry", [])
    property_ = next((e["siteUrl"] for e in seiten if HOST in e["siteUrl"]), None)
    if not property_:
        return {"fehler": "Das Dienstkonto sieht keine Property fuer bethathost.de - "
                          "in der Search Console als Nutzer eintragen."}
    p = urllib.parse.quote(property_, safe="")
    erg = {"property": property_}

    # Sitemap: Stand abfragen, bei Bedarf einreichen
    sitemap = f"https://{HOST}/sitemap.xml"
    vorhanden = s.get(f"{api}/sites/{p}/sitemaps").json().get("sitemap", [])
    if not any(m.get("path") == sitemap for m in vorhanden):
        r = s.put(f"{api}/sites/{p}/sitemaps/{urllib.parse.quote(sitemap, safe='')}")
        erg["sitemap_eingereicht"] = r.status_code in (200, 204)
        vorhanden = s.get(f"{api}/sites/{p}/sitemaps").json().get("sitemap", [])
    erg["sitemaps"] = [{"pfad": m.get("path"), "zuletzt": m.get("lastDownloaded"),
                        "fehler": m.get("errors"), "warnungen": m.get("warnings"),
                        "eingereicht": sum(int(c.get("submitted", 0)) for c in m.get("contents", []))}
                       for m in vorhanden]

    # Suchleistung (Daten haengen rund zwei Tage hinterher)
    bis = dt.date.today() - dt.timedelta(days=2)
    von = bis - dt.timedelta(days=TAGE - 1)
    def abfrage(dim, n):
        r = s.post(f"{api}/sites/{p}/searchAnalytics/query",
                   json={"startDate": von.isoformat(), "endDate": bis.isoformat(),
                         "dimensions": dim, "rowLimit": n}).json()
        return r.get("rows", [])
    erg["von"], erg["bis"] = von.isoformat(), bis.isoformat()
    erg["tage"] = [{"datum": z["keys"][0], "klicks": z["clicks"], "impressionen": z["impressions"]}
                   for z in abfrage(["date"], 100)]
    erg["seiten"] = [{"seite": z["keys"][0], "klicks": z["clicks"], "impressionen": z["impressions"],
                      "position": round(z["position"], 1)} for z in abfrage(["page"], 50)]
    erg["suchbegriffe"] = [{"begriff": z["keys"][0], "klicks": z["clicks"],
                            "impressionen": z["impressions"], "position": round(z["position"], 1)}
                           for z in abfrage(["query"], 50)]

    # Indexierung jeder URL aus der Sitemap (URL-Pruefung, 2000 pro Tag erlaubt)
    urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    index = []
    for u in urls:
        r = s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                   json={"inspectionUrl": u, "siteUrl": property_}).json()
        st = r.get("inspectionResult", {}).get("indexStatusResult", {})
        index.append({"url": u, "status": st.get("coverageState") or r.get("error", {}).get("message", "?"),
                      "zuletzt_gecrawlt": st.get("lastCrawlTime")})
    erg["index"] = index
    return erg


# ------------------------------------------------------------------- Bericht
def zahl(x):
    return f"{x:,.0f}".replace(",", ".")


def bericht(cf, gsc):
    z = [f"# Besucher & Google-Suche", "",
         f"Stand: {dt.date.today().isoformat()} · erzeugt von `scripts/web_stats.py` "
         f"(Workflow `web-stats.yml`, montags). Nicht von Hand bearbeiten.", ""]

    z += ["## Besucher (Cloudflare Web Analytics)", ""]
    if "tage" in cf:
        bes = sum(t["besuche"] for t in cf["tage"]); auf = sum(t["aufrufe"] for t in cf["tage"])
        z += [f"**{zahl(bes)} Besuche, {zahl(auf)} Seitenaufrufe** vom {cf['von']} bis {cf['bis']}.", "",
              "| Tag | Besuche | Aufrufe |", "|---|---:|---:|"]
        z += [f"| {t['datum']} | {zahl(t['besuche'])} | {zahl(t['aufrufe'])} |" for t in cf["tage"]]
        for titel, k in (("Meistbesuchte Seiten", "seiten"), ("Woher die Besucher kommen", "quellen"),
                         ("Geräte", "geraete")):
            z += ["", f"### {titel}", "", "| | Besuche | Aufrufe |", "|---|---:|---:|"]
            z += [f"| {g['wert']} | {zahl(g['besuche'])} | {zahl(g['aufrufe'])} |" for g in cf[k]]
    else:
        z += [f"_Nicht abgerufen: {cf.get('fehlt') or cf.get('fehler')}_"]

    z += ["", "## Google-Suche (Search Console)", ""]
    if "seiten" in gsc:
        kl = sum(t["klicks"] for t in gsc["tage"]); im = sum(t["impressionen"] for t in gsc["tage"])
        idx = gsc["index"]; drin = [i for i in idx if i["status"] == "Submitted and indexed"]
        z += [f"Property `{gsc['property']}` · {gsc['von']} bis {gsc['bis']}: "
              f"**{zahl(kl)} Klicks, {zahl(im)} Impressionen**.", "",
              f"**Indexiert: {len(drin)} von {len(idx)} Seiten aus der Sitemap.**"]
        if gsc.get("sitemap_eingereicht") is not None:
            z += ["", f"Sitemap neu eingereicht: {'ja' if gsc['sitemap_eingereicht'] else 'FEHLGESCHLAGEN'}"]
        z += ["", "### Indexierung je Seite", "", "| Seite | Status | Zuletzt gecrawlt |", "|---|---|---|"]
        z += [f"| {i['url'].replace('https://bethathost.de', '') or '/'} | {i['status']} | "
              f"{(i['zuletzt_gecrawlt'] or '–')[:10]} |" for i in sorted(idx, key=lambda i: i["status"])]
        z += ["", "### Seiten in der Suche", "", "| Seite | Klicks | Impressionen | Position |",
              "|---|---:|---:|---:|"]
        z += [f"| {g['seite'].replace('https://bethathost.de', '')} | {g['klicks']} | {g['impressionen']} | "
              f"{g['position']} |" for g in gsc["seiten"]]
        z += ["", "### Suchbegriffe", "", "| Begriff | Klicks | Impressionen | Position |",
              "|---|---:|---:|---:|"]
        z += [f"| {g['begriff']} | {g['klicks']} | {g['impressionen']} | {g['position']} |"
              for g in gsc["suchbegriffe"]]
    else:
        z += [f"_Nicht abgerufen: {gsc.get('fehlt') or gsc.get('fehler')}_"]
    return "\n".join(z) + "\n"


def main():
    ZIEL.mkdir(exist_ok=True)
    try:
        cf = cloudflare()
    except Exception as exc:  # noqa: BLE001 - Bericht soll trotzdem entstehen
        cf = {"fehler": str(exc)}
    try:
        gsc = search_console()
    except Exception as exc:  # noqa: BLE001
        gsc = {"fehler": str(exc)}
    (ZIEL / "web.json").write_text(json.dumps({"cloudflare": cf, "search_console": gsc},
                                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ZIEL / "WEB.md").write_text(bericht(cf, gsc), encoding="utf-8")
    print(bericht(cf, gsc)[:3000])


if __name__ == "__main__":
    main()
