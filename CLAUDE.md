# CLAUDE.md — Projekt- & Agenten-Leitfaden

Verbindliche Regeln für **jeden** Agenten (lokal, GitHub Action, Subagent), der an diesem
Repo arbeitet. Ziel: **Konsistenz**. Inkonsistenz ist der Hauptfehler, den es zu vermeiden gilt.

## Was das ist
Statische Website auf **GitHub Pages**, Domain **bethathost.de**.
Repo: `headdr-web/headdr-web.github.io`. Kein Build-Step — reines HTML/CSS/JS.

## Zwei Marken — NIEMALS vermischen
| Marke | Pfad | Sprache | Look |
|------|------|---------|------|
| **BeThatHost** | Root + Anlass-/Motto-Ordner | Deutsch | warm (Creme/Terrakotta/Sand), Fonts **Fraunces + Hanken Grotesk** |
| **Cozylore** | `cozy/**` | Englisch | eigenes `cozy/style.css`, Fonts **Fraunces + Inter** |

`cozy/**` ist tabu für BeThatHost-Änderungen und umgekehrt.

## Design-System (BeThatHost) — eiserne Regeln
- **Eine einzige Stylesheet-Quelle:** `/assets/style.css`. **Niemals** pro-Ordner-Kopien
  (`style.css`, `../style.css`) anlegen. Alle Seiten binden `/assets/style.css` + `/assets/motion.css` ein.
- **Fonts nur über die CSS-Variablen** `--display` (Fraunces) und `--ui` (Hanken Grotesk).
  **Nie** Playfair Display oder Inter auf BeThatHost-Seiten einführen.
- **Fonts sind self-hosted** (`/assets/fonts/*.woff2` + `@font-face`-Regeln in
  `/assets/fonts/fonts.css`). **Niemals** dynamisch vom Google-Fonts-CDN laden
  (`fonts.googleapis.com`/`fonts.gstatic.com`, auch kein `preconnect` dorthin) —
  das überträgt beim Seitenaufruf die Besucher-IP an Google-Server ohne
  Einwilligung (DSGVO Art. 6; vgl. LG München I, Urt. v. 20.01.2022, Az. 3 O
  17493/20). Jede Seite bindet stattdessen ein:
  `<link rel="stylesheet" href="/assets/fonts/fonts.css" />`
  Neue Schriftschnitte: mit modernem Browser-User-Agent von
  `fonts.googleapis.com/css2?family=...` abrufen, die `woff2`-URLs
  (`fonts.gstatic.com`) daraus greifen, nach `/assets/fonts/` herunterladen,
  `@font-face` in `fonts.css` ergänzen — nie den CDN-Link selbst einbinden.

## Anatomie einer Anlass-/Motto-Seite (`<ordner>/index.html`)
1. `<head>`: charset/viewport, `<title>… — BeThatHost</title>`, meta description, canonical,
   og-Tags, **Article + FAQPage JSON-LD**, `/assets/fonts/fonts.css` (self-hosted, kein CDN),
   `/assets/style.css`, `/assets/motion.css`, AdSense-Verifizierungs-Meta (Skript selbst erst
   nach Consent, siehe Abschnitt „Cookie-Consent" unten).
2. `<header class="site">`: Brand `<a class="brand" href="/">BeThatHost</a>` + Nav mit genau
   zwei Links: `Alle Anlässe` → `/`, `Über uns` → `/ueber-uns.html` (absolute Pfade, einheitlich auf allen Ebenen).
3. `<article>`: Lead-Bild (3:2), `<h1>`, `<p class="meta">Aktualisiert am … · 5 Min. Lesezeit · BeThatHost</p>`,
   Intro, thematische Abschnitte mit `<div class="pick">`-Karten, ein `<div class="ad-slot">`, `<div class="subscribe">`.
4. `<footer class="site">`: Standard-Offenlegung (leser-finanziert, `/datenschutz.html`, `/impressum.html`)
   + Cookie-Einstellungen-Button (siehe „Cookie-Consent" unten).
5. Vor `</body>`: Cloudflare Web Analytics, dann `<script src="/js/consent.js" defer></script>`
   (siehe „Cookie-Consent"). **Kein** direktes `<script ... adsbygoogle.js>` und **kein** direktes
   `<script ... pinit.js>` mehr im Markup — beide lädt `consent.js` erst nach Opt-in nach.

## Cookie-Consent (DSGVO Art. 13, § 25 TDDDG)
AdSense (`adsbygoogle.js`) und Pinterest (`pinit.js`) setzen Cookies/übertragen die IP vor jeder
Einwilligung — deshalb werden beide **nie** direkt im HTML eingebunden, sondern ausschließlich von
`/js/consent.js` per Script-Injection nachgeladen, und zwar nur nach aktivem Opt-in.
- Einbindung auf jeder Seite (Body-Ende, nach Cloudflare-Analytics):
  `<script src="/js/consent.js" defer></script>`
- Banner (bei erstem Besuch): zwei **gleichwertige** Buttons „Nur notwendige" / „Akzeptieren" —
  gleiche Größe/Optik, keine Vorauswahl, kein Nudging.
- Entscheidung liegt in `localStorage` (geräte­lokal). Widerruf/Ändern jederzeit über
  `window.bthOpenConsentSettings()` — dafür jede Seite mit einem Footer-Button
  (`class="cookie-settings-link"`) verknüpfen, der genau das aufruft.
- Google-adsense-account-Meta-Tag ist unkritisch (keine Cookies) und bleibt direkt im `<head>`.
- Neue Drittanbieter-Skripte, die Cookies/IDs setzen: **immer** nach demselben Muster über
  `consent.js` nachladen, nie direkt einbinden — sonst driftet die Datenschutzerklärung
  wieder von der technischen Realität weg.

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
- **Live-Posten (automatisch):** `.github/workflows/pinterest-publish.yml` + `scripts/pinterest_publish.py`
  posten geplant aus den `*/pins/queue.json` über die offizielle API (Refresh-Token, Pro-Board-Logik).
- **Einmal-Bulk-Upload:** `pinterest/make_bulk_csv.py` erzeugt eine CSV für Pinterests „Bulk-Pins erstellen".
- Inhaltlicher Tracker / Single Source of Truth: Notion-DB **„📌 Pinterest Pins"**. Details: `pinterest/README.md`.

## Workflow / Konventionen
- **Vor jedem Push:** `bash scripts/check-consistency.sh` (CI erzwingt es ohnehin).
- Branch je Aufgabe, **kein** Direkt-Push auf `main` ohne PR.
- Commit-Präfixe: `content:`, `design:`, `feat:`, `fix:`, `chore:`.
- Keine Secrets committen (API-Keys etc. liegen als GitHub-Secrets).
- Antworten/Inhalte auf Deutsch (außer Cozylore = Englisch).

## Automatisierung auf GitHub
- `@claude` in einem Issue/PR-Kommentar → der GitHub-Agent (`.github/workflows/claude.yml`) übernimmt.
- Jeder Push/PR → CI-Konsistenz-Check (`.github/workflows/consistency.yml`).
- Wiederverwendbare Rollen: `.claude/agents/` (consistency-auditor, page-builder, pinterest-manager).
