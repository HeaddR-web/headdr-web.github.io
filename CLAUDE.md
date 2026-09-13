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
- **RSS-Auto-Publish (Standardweg):** `scripts/make_feed.py` baut `feed.xml` aus `pinterest/pins.json` +
  `*/pins/queue.json`; Pinterest zieht das selbst, kein API-Token nötig. Details: `pinterest/README.md`.
- **Live-Posten über die API (aktiv, seit 2026-09):** `.github/workflows/pinterest-publish.yml` +
  `scripts/pinterest_publish.py` posten 2×/Tag aus den `*/pins/queue.json` über die offizielle
  Pinterest-API v5. Die Entwickler-App ist freigeschaltet; nötig sind nur die drei Secrets
  `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`, `PINTEREST_REFRESH_TOKEN`. Token erzeugen wahlweise
  ohne Terminal über den Workflow `pinterest-oauth.yml` (+ `scripts/pinterest_oauth_ci.py`,
  Redirect-URI `https://bethathost.de/`, schreibt das Secret selbst per API) oder lokal mit
  `scripts/pinterest_oauth.py`. Board-Zuordnung über Board-**Namen** in
  `pinterest/boards.json` — kein Secret pro Hub. Vor dem ersten scharfen Lauf immer erst die
  Workflow-Modi `doctor` und `dry-run` benutzen.
- **Doppelpost-Regel:** Die Queue-Dateien sind die einzige Sperre gegen doppelte Pins — was auf
  `"published": false` steht, wird gepostet. Pins, die schon per RSS oder Bulk-CSV draußen sind,
  stehen dort trotzdem noch auf `false`. Wer einen der anderen Wege benutzt hat, muss danach den
  Modus `mark-published-only` laufen lassen (hakt alles ab, ohne zu posten), sonst legt die API
  jeden dieser Pins ein zweites Mal an.
- `cozy/pins/queue.json` wird **nie** gepostet (Cozylore ist abgekoppelt) — die Ausnahme steckt in
  `SKIP_SITES` in `scripts/pinterest_publish.py` und in `scripts/make_feed.py`.
- **Einmal-Bulk-Upload:** `pinterest/make_bulk_csv.py` erzeugt eine CSV für Pinterests „Bulk-Pins erstellen".
- Inhaltlicher Tracker / Single Source of Truth: Notion-DB **„📌 Pinterest Pins"**. Details: `pinterest/README.md`.
- **Ziel-URL — eiserne Regel:** Jeder Pin braucht eine **serverseitig eindeutige** `link`-URL.
  `#anker` allein reicht **nicht** — Fragmente werden nie an den Server gesendet, Pinterest sieht
  sonst bei allen Pins einer Seite dieselbe URL und verwirft sie still als Duplikate (genau daran
  sind im Juli 2026 ~70 Pins gescheitert). Deshalb immer zusätzlich einen Query-Parameter setzen:
  `https://bethathost.de/casino/?pin=pokerset#cat-pokerset`. Die Seite lädt identisch, der Anker
  scrollt weiterhin, und das `<link rel="canonical">` der Seite schützt die SEO.
- **Bild-Eindeutigkeit — eiserne Regel:** Jeder Pin braucht ein **eigenes Bild**. Pinterest lehnt
  Pins mit bereits verwendetem Motiv ab („Doppeltes Pin-Bild", belegt beim Bulk-Upload im Juli 2026).
  Nie dasselbe Motiv für zwei Pins wiederverwenden — auch nicht Startseite + Anlass-Seite.
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
