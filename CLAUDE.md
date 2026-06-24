# CLAUDE.md — Nordstern für BeThatHost (bethathost.de)

> Diese Datei wird in jeder Claude-Session automatisch geladen. Sie ist verbindlich.
> Vor größeren Änderungen: die Strategie-Docs unter `docs/strategie/` lesen.

## Was das hier ist
**BeThatHost** (bethathost.de) — deutschsprachige Plattform zum Planen von Partys/Abenden
zuhause. Pro Anlass kuratierte Produktempfehlungen + Guides. Statische Seite auf GitHub Pages
(läuft von `main`). Geld-Modell: **Affiliate (Amazon, Tag `cozylore-21`) + Display-Werbung.**

## Die zwei Nordsterne (immer einhalten)

1. **Einkaufen erleichtern.** Jede Seite/jeder Pin hat eine Aufgabe: dem Besucher das Kaufen
   für seine Party leichter machen — vermitteln *und* ermöglichen. Jedes empfohlene Produkt
   ist ein **direkter** Amazon-Link auf der Seite, kein Suchen. Macht eine Änderung das Kaufen
   nicht leichter, ist sie nachrangig.

2. **Konsistenz über alle Seiten.** Alle Anlass-Seiten sind **gleich aufgebaut** — gleiche
   Reihenfolge, gleiche Bausteine, gleiche Navigation, gleiche Wörter. Ein Besucher, der eine
   Seite versteht, versteht alle. **Verbindlicher Bauplan: `docs/strategie/seiten-standard.md`.**
   Neue Seiten folgen ihm; bestehende werden daran angeglichen.

## Harte Regeln
- Affiliate-Tag **immer** `cozylore-21`. Amazon-Links sind **Such-Links**
  (`amazon.de/s?k=…&tag=cozylore-21`) mit `rel="sponsored nofollow" target="_blank"`.
  **Keine erfundenen** Produktnamen/Preise/ASINs. Keine selbst gehosteten Amazon-Bilder.
- Seite bleibt **statisch & schnell** (Core Web Vitals). **Keine** schweren Videos auf der
  Website „für SEO" — Video gehört auf Social (Pinterest/Reels) als Traffic-Quelle.
- Markenname „BeThatHost", deutsche Labels. (`cozy/` wird ebenfalls angeglichen.)
- Jede neue Seite kommt in `sitemap.xml`; jeder Artikel verlinkt 2–3 verwandte Seiten.

## Wo was steht
- `docs/strategie/money-roadmap.md` — Prioritäten & das Geld-Ziel (erste 3 Amazon-Verkäufe).
- `docs/strategie/seiten-standard.md` — verbindlicher Seiten-Bauplan + Migrations-Status.
- `docs/strategie/reels-experiment.md` — Video-/Reels-Playbook (Higgsfield).
- `docs/strategie/venture-2-finanz-instagram.md` — geparkte Idee, nicht jetzt anfassen.
- `docs/amazon-produktkarten.md` — Plan für echte Amazon-API-Karten (erst nach 3 Verkäufen).

## Verifizieren
- Nach Änderungen an `app.js`: `node --check <pfad>/app.js`.
- Vorbild-Seiten für Struktur: `watchparty/`, `cocktailabend/`, `girlsnight/`.
