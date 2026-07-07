# Pinterest — drei Wege, Pins zu posten

Drei parallele Wege, denselben kuratierten Content (`*/pins/queue.json`,
`pinterest/pins.json`) auf Pinterest zu bringen. Alle drei sind ToS-konform —
kein Browser, kein gespeichertes Passwort, kein Selenium.

## Weg 1 — RSS-Auto-Publish (empfohlen, kein API-Token nötig)
Pinterest kann selbst einen RSS-Feed abonnieren und daraus automatisch Pins
erstellen — ganz ohne Entwickler-App, ohne OAuth, ohne Secrets.

1. `scripts/make_feed.py` liest `pinterest/pins.json` (Cover-Pin je Seite) und
   alle `*/pins/queue.json` (kuratierte Kategorie-Pins mit Hashtags) und
   schreibt `feed.xml` im Repo-Root (RSS 2.0).
2. `.github/workflows/feed.yml` hält `feed.xml` automatisch aktuell — bei jedem
   Push, der Seiten/Sitemap/Queues ändert, plus täglich als Sicherheitsnetz.
3. Einmalig bei Pinterest verknüpfen (Desktop, Business-Konto mit verifizierter
   Domain nötig — haben wir bereits):
   Einstellungen → **Mehrere Pins gleichzeitig erstellen** → **Automatisch
   veröffentlichen** → **RSS-Feed verknüpfen** → `https://bethathost.de/feed.xml`
   einfügen → Ziel-Pinnwand wählen → Speichern.
4. Danach übernimmt Pinterest selbst: neue/aktualisierte Feed-Einträge werden
   **innerhalb von 24 Stunden** zu Pins (ältester Inhalt zuerst, max. 200/Tag).

Details: <https://help.pinterest.com/de/business/article/auto-publish-pins-from-your-rss-feed>

**Achtung Duplikate:** Wenn Inhalte aus `feed.xml` bereits einmal manuell per
Bulk-CSV (Weg 3) hochgeladen wurden, erstellt Pinterest beim Verknüpfen des
Feeds trotzdem neue Pins dafür — es gibt keine automatische Dopplungs-Prüfung
zwischen den drei Wegen. Vor dem Verknüpfen im Notion-Tracker prüfen, was schon
„Hochgeladen" ist, und diese Einträge ggf. vorübergehend aus den Queues nehmen.

## Weg 2 — Live-API-Posten (geplant, braucht Pinterest-Entwickler-App)
1. `scripts/pinterest_publish.py` postet die nächsten unveröffentlichten Pins
   aus allen `*/pins/queue.json` über die offizielle Pinterest-API (v5) und
   markiert sie als `"published": true` (kein Doppelposten).
2. `.github/workflows/pinterest-publish.yml` läuft 2×/Tag (09:00 & 17:00 UTC)
   oder manuell und committet die aktualisierten Queues zurück.
3. Einrichtung: Pinterest-Entwickler-App unter
   <https://developers.pinterest.com/> anlegen, OAuth-Refresh-Token erzeugen,
   dann als **Repo-Secrets** hinterlegen:
   - `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`, `PINTEREST_REFRESH_TOKEN`
   - `PINTEREST_BOARD_ID` (Standard-Board) + optional
     `PINTEREST_BOARD_ID_<SITE>` (z. B. `PINTEREST_BOARD_ID_GIRLSNIGHT`) für
     Board-Overrides pro Ordner.
   Fehlen Secrets, bricht der Lauf sauber mit einer Meldung ab (kein Absturz).

## Weg 3 — Einmaliger Bulk-Upload (manuell, für Nachzügler)
`pinterest/make_bulk_csv.py` erzeugt `pinterest_bulk.csv` im Format von
Pinterests **„Bulk-Pins erstellen"**-Import (Pinterest Business → Erstellen →
„Bulk create Pins"). Spalten **wörtlich englisch** halten — `Title, Media URL,
Pinterest board, Thumbnail, Description, Link, Publish date, Keywords` — auch
bei deutschsprachigem Konto (getestet: deutsche Spaltennamen wie „Medien-URL"
führen zu „Fehlende Media-URL" für jede Zeile).

## Inhaltlicher Tracker
Single Source of Truth für den redaktionellen Stand: Notion-DB
**„📌 Pinterest Pins"** (Status `Offen`/`Hochgeladen`/`Geplant`). Neue Pin-Ideen
dort anlegen, dann `*/pins/queue.json` entsprechend ergänzen.

## Tipp: bessere Pin-Bilder
Pinterest bevorzugt **vertikale 2:3-Bilder**. Aktuell werden die querformatigen
`og:image`/Queue-Bilder (3:2) verwendet — funktioniert, ist aber nicht optimal.
