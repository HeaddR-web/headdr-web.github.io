# CLAUDE.md — Projekt- & Agenten-Leitfaden

Verbindliche Regeln für **jeden** Agenten (lokal, GitHub Action, Subagent), der an diesem
Repo arbeitet. Ziel: **Konsistenz**. Inkonsistenz ist der Hauptfehler, den es zu vermeiden gilt.

## Was das ist
Statische Website auf **GitHub Pages**, Domain **bethathost.de**.
Repo: `headdr-web/headdr-web.github.io`. Kein Build-Step — reines HTML/CSS/JS.
**Einsprachig Deutsch** — BeThatHost ist die einzige aktive Marke.

## Cozylore (`cozy/**`) — abgekoppelt, seit 2026-07-20
Cozylore war eine englischsprachige Sub-Marke, ist aber **nicht mehr Teil der Live-Seite**:
kein Link mehr in Navigation, Startseite oder Cross-Links, nicht in `sitemap.xml`/`llms.txt`.
Die Dateien unter `cozy/**` bleiben unverändert im Repo (nichts gelöscht, könnte später eine
eigene Domain bekommen), werden aber **nicht mehr gepflegt oder verlinkt**. `cozy/**` bleibt
weiterhin tabu für BeThatHost-Änderungen (eigenständiges `cozy/style.css`, Fonts Fraunces +
Inter) — einfach komplett getrennt behandeln, in keine Richtung vermischen.

## Design-System (BeThatHost) — eiserne Regeln
- **Eine einzige Stylesheet-Quelle:** `/assets/style.css`. **Niemals** pro-Ordner-Kopien
  (`style.css`, `../style.css`) anlegen. Alle Seiten binden `/assets/style.css` + `/assets/motion.css` ein.
- **Fonts nur über die CSS-Variablen** `--display` (Fraunces) und `--ui` (Hanken Grotesk).
  **Nie** Playfair Display oder Inter auf BeThatHost-Seiten einführen.
- Google-Fonts-Link (identisch auf jeder Seite):
  `https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,400&family=Hanken+Grotesk:wght@400;500;600;700&display=swap`

## Anatomie einer Anlass-/Motto-Seite (`<ordner>/index.html`)
1. `<head>`: charset/viewport, `<title>… — BeThatHost</title>`, meta description, canonical,
   og-Tags, **Article + FAQPage JSON-LD**, Fonts-Link, `/assets/style.css`, `/assets/motion.css`, AdSense.
2. `<header class="site">`: Brand `<a class="brand" href="/">BeThatHost</a>` + Nav mit genau
   zwei Links: `Alle Anlässe` → `/`, `Über uns` → `/ueber-uns.html` (absolute Pfade, einheitlich auf allen Ebenen).
3. `<article>`: Lead-Bild (3:2), `<h1>`, `<p class="meta">Aktualisiert am … · 5 Min. Lesezeit · BeThatHost</p>`,
   Intro, thematische Abschnitte mit `<div class="pick">`-Karten, ein `<div class="ad-slot">`, `<div class="subscribe">`.
4. `<footer class="site">`: Standard-Offenlegung (leser-finanziert, `/datenschutz.html`, `/impressum.html`).

## Affiliate-Konvention
Jeder Produktlink: `rel="sponsored nofollow" target="_blank"`, Amazon-Tag **`cozylore-21`**,
Form `https://www.amazon.de/s?k=<suchbegriff>&tag=cozylore-21`.

## Produkt-Picks — Realitäts-Regel
Picks sind **realistische, bezahlbare Impuls-/Mitnahmekäufe fürs Gastgeben** (Deko, Gläser,
Snack-Zubehör, Spiele, Fanartikel, Verbrauchsmaterial). **Keine geplanten Big-Ticket-Anschaffungen**
(Beamer, teure Elektronik, Großmöbel) als „Unser Pick" mit direktem Kauf-CTA — niemand kauft so etwas
spontan für eine Feier. Solche Posten höchstens als **optionalen Hinweis** mit Link zum passenden
**Kaufratgeber** (`/ratgeber/…`, Label „Optional", CTA „Zum Kaufratgeber →"), nicht als Amazon-Direktlink.

## Neue Anlass-/Motto-Seite anlegen
1. Ordner + `index.html` exakt nach obiger Anatomie.
2. Hero-Bild (3:2, querformat), als `og:image` und Lead.
3. Karte auf der Startseite ergänzen (`#anlaesse` für Anlässe, `#mottopartys` für Mottos).
4. URL in `sitemap.xml` eintragen.
5. `scripts/check-consistency.sh` laufen lassen — muss grün sein.

## Pinterest
- **RSS-Auto-Publish (Standardweg):** `scripts/make_feed.py` baut `feed.xml` aus `pinterest/pins.json` +
  `*/pins/queue.json`; Pinterest zieht das selbst, kein API-Token nötig. Details: `pinterest/README.md`.
- **Live-Posten (automatisch, optional):** `.github/workflows/pinterest-publish.yml` + `scripts/pinterest_publish.py`
  posten geplant aus den `*/pins/queue.json` über die offizielle API (Refresh-Token, Pro-Board-Logik).
- **Einmal-Bulk-Upload:** `pinterest/make_bulk_csv.py` erzeugt eine CSV für Pinterests „Bulk-Pins erstellen".
- Inhaltlicher Tracker / Single Source of Truth: Notion-DB **„📌 Pinterest Pins"**. Details: `pinterest/README.md`.
- **Bildformat — eiserne Regel:** Jedes neue Pin-Bild ist **vertikal 2:3** (z. B. 848×1264). Nie Quer-Bilder
  (og:image, Hero-Bilder, 3:2/16:9) für neue Pins wiederverwenden oder generieren.

## Workflow / Konventionen
- **Vor jedem Push:** `bash scripts/check-consistency.sh` (CI erzwingt es ohnehin).
- Branch je Aufgabe, **kein** Direkt-Push auf `main` ohne PR.
- Commit-Präfixe: `content:`, `design:`, `feat:`, `fix:`, `chore:`.
- Keine Secrets committen (API-Keys etc. liegen als GitHub-Secrets).
- Antworten/Inhalte auf Deutsch (einsprachig — `cozy/**` ist abgekoppelt, siehe oben).

## Automatisierung auf GitHub
- `@claude` in einem Issue/PR-Kommentar → der GitHub-Agent (`.github/workflows/claude.yml`) übernimmt.
- Jeder Push/PR → CI-Konsistenz-Check (`.github/workflows/consistency.yml`).
- Wiederverwendbare Rollen: `.claude/agents/` (consistency-auditor, page-builder, pinterest-manager).
