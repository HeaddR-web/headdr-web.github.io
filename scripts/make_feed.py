#!/usr/bin/env python3
"""Erzeugt feed.xml (RSS 2.0) aus den bestehenden Pinterest-Inhalten.

Zweck: Pinterest kann RSS-Feeds mit einem Unternehmenskonto verknuepfen und
erstellt daraus automatisch Pins, ohne API-Token und ohne manuellen CSV-Upload.
Siehe: https://help.pinterest.com/de/business/article/auto-publish-pins-from-your-rss-feed

Quellen (dieselben wie fuer die Pinterest-API-Pipeline / Notion-Tracker):
  - pinterest/pins.json      -> ein "Cover"-Pin je Seite (Startseite + Anlaesse)
  - */pins/queue.json        -> die kuratierten Kategorie-Pins mit Hashtags
                                (dieselben Inhalte, die pinterest_publish.py
                                 ueber die offizielle API posten wuerde)

pubDate wird aus sitemap.xml (lastmod der Seite) abgeleitet, sonst aus dem
letzten Git-Commit der Quelldatei.
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
from email.utils import format_datetime
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MIME = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}


def mime_for(url):
    ext = os.path.splitext(url)[1].lstrip(".").lower()
    return MIME.get(ext, "image/png")


def load_sitemap_lastmod():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        sitemap = f.read()
    lastmod = {}
    for url, date in re.findall(r"<loc>(.*?)</loc>(?:<lastmod>(.*?)</lastmod>)?", sitemap):
        slug = url.replace("https://bethathost.de/", "").strip("/").split("/")[0]
        if date:
            lastmod.setdefault(slug or "home", date)
    return lastmod


_git_date_cache = {}


def git_date(path):
    if path in _git_date_cache:
        return _git_date_cache[path]
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        out = ""
    _git_date_cache[path] = out or None
    return _git_date_cache[path]


def rfc822(date_str):
    try:
        d = dt.datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        d = dt.datetime.now()
    return format_datetime(d.replace(tzinfo=dt.timezone.utc))


def main():
    lastmod = load_sitemap_lastmod()
    items = []

    # 1) Cover-Pins je Seite
    with open(os.path.join(ROOT, "pinterest", "pins.json"), encoding="utf-8") as f:
        for p in json.load(f):
            slug = p["id"] if p["id"] != "home" else "home"
            date = lastmod.get(slug)
            items.append({
                "title": p["title"],
                "link": p["link"],
                "description": p["description"],
                "image": p["image"],
                "date": date,
            })

    # 2) Kuratierte Kategorie-Pins aus */pins/queue.json
    for qf in sorted(glob.glob(os.path.join(ROOT, "*", "pins", "queue.json"))):
        slug = os.path.basename(os.path.dirname(os.path.dirname(qf)))
        date = lastmod.get(slug) or git_date(os.path.relpath(qf, ROOT))
        with open(qf, encoding="utf-8") as f:
            for p in json.load(f):
                items.append({
                    "title": p["title"],
                    "link": p["link"],
                    "description": p["description"],
                    "image": p["image_url"],
                    "date": date,
                })

    for it in items:
        it["pub_date"] = rfc822(it["date"])
        it["mime"] = mime_for(it["image"])

    items.sort(key=lambda i: i["date"] or "0000-00-00", reverse=True)

    now = format_datetime(dt.datetime.now(dt.timezone.utc))
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        "    <title>BeThatHost — Party- &amp; Gastgeber-Ideen</title>",
        "    <link>https://bethathost.de/</link>",
        '    <atom:link href="https://bethathost.de/feed.xml" rel="self" type="application/rss+xml" />',
        "    <description>Anlass- und Motto-Party-Ideen, Deko, Ausstattung und Einkaufslisten von BeThatHost.</description>",
        "    <language>de-DE</language>",
        f"    <lastBuildDate>{now}</lastBuildDate>",
    ]
    seen_guids = set()
    for it in items:
        guid = it["link"] + "#" + it["image"].rsplit("/", 1)[-1]
        if guid in seen_guids:
            continue
        seen_guids.add(guid)
        parts += [
            "    <item>",
            f"      <title>{escape(it['title'])}</title>",
            f"      <link>{escape(it['link'])}</link>",
            f'      <guid isPermaLink="false">{escape(guid)}</guid>',
            f"      <description>{escape(it['description'])}</description>",
            f"      <pubDate>{it['pub_date']}</pubDate>",
            f'      <enclosure url="{escape(it["image"])}" type="{it["mime"]}" length="0" />',
            "    </item>",
        ]
    parts += ["  </channel>", "</rss>", ""]

    out = os.path.join(ROOT, "feed.xml")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"{len(seen_guids)} Items -> {out}")


if __name__ == "__main__":
    main()
