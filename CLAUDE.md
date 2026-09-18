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
1. `<head>`: charset/viewport, `<title>… — BeThatHost</title>`, meta description
   (**max. 160 Zeichen** — Google schneidet deutsche Snippets bei rund 155-160 ab;
   `scripts/check-meta.py` prüft das mit, Punkt 10 im Konsistenz-Check), canonical,
   og-Tags, **Article + FAQPage JSON-LD**, `/assets/fonts/fonts.css` (self-hosted, kein CDN),
   `/assets/style.css`, `/assets/motion.css`, AdSense-Verifizierungs-Meta (Skript selbst erst
   nach Consent, siehe Abschnitt „Cookie-Consent" unten).
2. `<header class="site">`: Brand `<a class="brand" href="/">BeThatHost</a>` + Nav mit genau
   zwei Links: `Alle Anlässe` → `/`, `Über uns` → `/ueber-uns.html` (absolute Pfade, einheitlich auf allen Ebenen).
3. `<article>`: Lead-Bild (3:2), `<h1>`, `<p class="meta">Aktualisiert am … · 5 Min. Lesezeit · BeThatHost</p>`,
   Intro, **Einkaufslisten-Block** (`<aside class="quickbuy">`, siehe unten), **Inhaltsverzeichnis**
   (`<nav class="toc">`, siehe unten), thematische Abschnitte mit
   `<div class="pick">`-Karten, ein **leerer** `<div class="ad-slot"></div>` (siehe unten).
   Ein `<div class="subscribe">` gehoert erst dazu, wenn ein echtes Newsletter-Formular
   dahinterhaengt — bis dahin sammelt es Adressen ein, die nirgends ankommen (siehe unten).
4. `<footer class="site">`: Standard-Offenlegung (leser-finanziert, `/datenschutz.html`, `/impressum.html`)
   + Cookie-Einstellungen-Button (siehe „Cookie-Consent" unten).
5. Vor `</body>`: Cloudflare Web Analytics, dann `<script src="/js/consent.js" defer></script>`
   (siehe „Cookie-Consent"). **Kein** direktes `<script ... adsbygoogle.js>` und **kein** direktes
   `<script ... pinit.js>` mehr im Markup — beide lädt `consent.js` erst nach Opt-in nach.

## Werbeplätze (`div.ad-slot`) — immer leer im Quelltext
Jede Inhaltsseite hat **genau einen** `<div class="ad-slot"></div>`, ungefähr in der Mitte des
Artikels (vor der mittleren `<h2>`). Er steht im Quelltext **leer** und wird erst von
`js/consent.js` nach der Einwilligung mit einer In-Artikel-Anzeige befüllt.

- **Nie Text hineinschreiben.** `.ad-slot:empty` blendet den leeren Platz aus; sobald Text
  darin steht, sieht jeder Besucher dauerhaft einen Kasten. Genau so stand bis September 2026
  „Werbeplatz — im Artikel (responsiv). Erscheint, sobald AdSense aktiv ist." auf `oktoberfest/`.
- **Anzeigenblock-ID:** `ADSENSE_SLOT` in `js/consent.js` — die eine Stelle, an der die
  `data-ad-slot`-Nummer steht. Solange sie leer ist, wird **nichts** eingesetzt und **nichts**
  geladen; die Slots sind dann unsichtbar. ID im AdSense-Konto unter *Anzeigen → Nach
  Anzeigenblock → In-Artikel-Anzeige* anlegen und dort eintragen.
- Liefert AdSense keine Anzeige (`data-ad-status="unfilled"`), leert `consent.js` den Platz
  wieder — dann greift `:empty` und der Kasten verschwindet, statt als Lücke stehen zu bleiben.
- Die Anzeige bekommt eine `<span class="ad-label">Anzeige</span>` (Kennzeichnungspflicht,
  § 6 Abs. 1 Nr. 1 DDG, § 5a UWG).
- **Ohne Werbeplatz** bleiben bewusst: Rechtstexte (`impressum`, `datenschutz`, `privacy`),
  die drei `disclosure.html` und die internen Werkzeuge (`dashboard`, `produkt-review`) —
  Werbung neben der Anbieterkennung oder der Affiliate-Offenlegung untergräbt genau das
  Vertrauenssignal, für das diese Seiten da sind.
- `scripts/check-ads.py` prüft das mit, Punkt 12 im Konsistenz-Check.

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

## Einkaufslisten-Block (`aside.quickbuy`) — generiert, nie von Hand
Direkt unter der Einleitung steht auf jeder Anlass-Seite eine kompakte Liste **aller** Picks der
Seite mit Direktlink. Grund: Ohne den Block taucht die erste Empfehlung erst nach rund 900 Zeichen
Fließtext auf — wer vorher abspringt (mobil die Mehrheit), sieht nie ein Produkt.

- Gebaut von `scripts/build-quickbuy.py` aus den vorhandenen `.pick`-Karten. **Niemals von Hand
  bearbeiten** — der Block steht zwischen `<!-- QUICKBUY:START … -->` und `<!-- QUICKBUY:END -->`
  und wird bei jedem Lauf komplett ersetzt.
- Nach **jeder** Änderung an den Picks einer Seite (neuer Pick, andere ASIN, anderer Name):
  `python3 scripts/build-quickbuy.py`
- `scripts/check-consistency.sh` prüft das mit (Punkt 8) und wird rot, wenn der Block nicht zu den
  Karten darunter passt. Neue Anlass-Seite: Slug in das `ANLASS`-Dict des Skripts eintragen, sonst
  bekommt sie keinen Block.
- Picks mit dem Label `Optional` (Kaufratgeber-Verweise) bleiben bewusst draußen — die Liste ist
  für Direktkäufe.

## Inhaltsverzeichnis (`nav.toc`) — generiert, nie von Hand
Unter der Einkaufsliste steht auf jeder Seite mit mindestens vier Abschnitten ein
Sprungverzeichnis. Grund: Die Artikel haben vier bis neun Abschnitte, der Leser sah beim
Ankommen aber nur die Einleitung und musste raten, ob sein Thema überhaupt vorkommt —
mobil die häufigste Abbruchstelle. Nebeneffekt: Google bekommt die Sprungmarken für Sitelinks.

- Gebaut von `scripts/build-toc.py` aus den `<h2>` des Inhaltsbereichs. **Niemals von Hand
  bearbeiten** — der Block steht zwischen `<!-- TOC:START … -->` und `<!-- TOC:END -->` und
  wird bei jedem Lauf komplett ersetzt.
- Nach **jeder** Änderung an den `<h2>` einer Seite (neu, umbenannt, gelöscht):
  `python3 scripts/build-toc.py`
- **Bestehende `id`-Attribute werden nie angefasst.** Die 65 `cat-*`-Anker stecken in den
  Pinterest-Ziel-URLs (`/casino/?pin=pokerset#cat-pokerset`); ein umbenannter Anker macht
  jeden dieser Pins kaputt. Fehlende ids ergänzt das Skript, vorhandene bleiben.
- **Reihenfolge ist Pflicht: Einkaufsliste → Verzeichnis → erstes `<h2>`.** Die Liste ist der
  einzige Kaufweg above the fold; alles, was sie nach unten schiebt, kostet Umsatz. Beide
  Generatoren zielen deshalb aufeinander: `build-quickbuy.py` setzt vor `<!-- TOC:START`,
  `build-toc.py` hinter `<!-- QUICKBUY:END -->` — egal welches Skript zuletzt läuft.
- Unter vier Abschnitten (`MIN_ABSCHNITTE`) bekommt eine Seite bewusst kein Verzeichnis,
  dort steht es dem Leser nur im Weg. Ausgenommen sind außerdem Startseite, Rechtstexte,
  die drei `disclosure.html` und die internen Werkzeuge.
- `scripts/check-toc.py` prüft das mit, Punkt 13 im Konsistenz-Check.

## Weiterlesen-Block (`nav.related`) — generiert, nie von Hand
Am Ende jeder Seite stehen drei thematisch passende Verweise plus „Alle Anlässe". Grund:
Im September 2026 verlinkte **kein Artikel** auf neun der Seiten (brunch, casino, geburtstag,
oktoberfest, saison-deko und drei Mädelsabend-Guides) — sie waren nur über die Startseite
erreichbar. Vier Seiten hatten gar keinen ausgehenden Link: wer dort ankam, hatte als einzigen
Weg weiter den Zurück-Button. Die handgemachten „Weitere Anlässe"-Absätze gab es nur auf zehn
Seiten und zeigten fast alle auf dieselben zwei Ziele.

- Gebaut von `scripts/build-related.py`. **Niemals von Hand bearbeiten** — der Block steht
  zwischen `<!-- RELATED:START … -->` und `<!-- RELATED:END -->` und wird bei jedem Lauf
  komplett ersetzt.
- **Wie die Ziele entstehen:** Jede Seite gehört zu einem Thema (`THEMA`). Innerhalb eines
  Themas bilden die Seiten einen **Ring** — jede verlinkt auf die beiden nächsten. Ein Ring
  kann per Konstruktion keine Waise enthalten. Der dritte Link geht reihum ins Partner-Thema
  (`PARTNER`), damit die Ringe nicht voneinander abgeschnitten sind.
- **Neue Seite:** Slug in `NAME` (kurzer Linktext — die `<h1>` sind für eine Kachel zu lang)
  **und** in das passende `THEMA` eintragen, dann `python3 scripts/build-related.py`.
  Ohne Eintrag bekommt die Seite weder Block noch eingehende Links.
- Links immer **absolut** (`/casino/`). Die alten Blöcke nutzten `../casino/` und
  `../index.html` — auf den Guide-Unterseiten zeigt das eine Ebene daneben.
- `scripts/check-related.py` prüft das mit, Punkt 14 im Konsistenz-Check: Block aktuell,
  keine Waisen, kein interner Link auf eine Datei, die es nicht gibt.

## Newsletter (`div.subscribe`) — erst mit echtem Formular
Bis September 2026 stand auf genau einer Seite (`oktoberfest/`) ein Anmeldekasten mit
`<form action="#" method="post">`. Der schickt beim Absenden auf dieselbe Seite zurück: jede
eingegebene Adresse war weg, der Leser hielt sich aber für angemeldet. Dazu wurde eine
E-Mail-Adresse erhoben, ohne dass Zweck oder Empfänger in der Datenschutzerklärung standen.
Der Kasten ist deshalb entfernt; die CSS-Regeln bleiben in `/assets/style.css`.

Zurück kommt er, sobald ein echter Anbieter (beehiiv, MailerLite o. ä.) dahinterhängt —
dann auf **alle** Anlass-Seiten, nicht nur auf eine, und mit einem Absatz in
`/datenschutz.html` (Anbieter, Zweck, Speicherdauer, Widerruf). Vorher nicht ausrollen:
ein kaputter CTA auf 38 Seiten ist 38-mal enttäuschter Leser.

## Affiliate-Konvention
Jeder Produktlink: `rel="sponsored nofollow" target="_blank"`, Amazon-Tag **`cozylore-21`**,
Form `https://www.amazon.de/s?k=<suchbegriff>&tag=cozylore-21`.

**Ein Affiliate-Link ist genau einer mit `rel="sponsored"` — und der braucht ein `tag=`.**
`scripts/set-tracking-ids.py` prüft (und ergänzt) das; bis September 2026 fiel ein Link ohne
jedes `tag=` durch, weil das Skript nur vorhandene IDs korrigierte und fehlende bewusst in Ruhe
liess. Ein solcher Link bringt keine Provision, egal wie oft er geklickt wird. Beleglinks ohne
`rel="sponsored"` (z. B. Amazons Hilfeseite in `datenschutz.html`) bleiben absichtlich ohne Tag.

**Tracking-IDs pro Seite:** Welche ID an welchen Ordner gehoert, steht in
`scripts/tracking-ids.json`; `scripts/set-tracking-ids.py` schreibt sie in alle Links,
`check-consistency.sh` (Punkt 9) prueft sie. Aktuell steht ueberall `cozylore-21`, das Skript
aendert also nichts. Sinn der Sache: PartnerNet berichtet Klicks **und** Verkaeufe je ID — erst
damit ist sichtbar, welche Seite traegt. Eine ID **erst im PartnerNet anlegen**, dann eintragen —
Links mit einer ID, die es im Konto nicht gibt, werden nicht verguetet.

## Produkt-Picks — Realitäts-Regel
Picks sind **realistische, bezahlbare Impuls-/Mitnahmekäufe fürs Gastgeben** (Deko, Gläser,
Snack-Zubehör, Spiele, Fanartikel, Verbrauchsmaterial). **Keine geplanten Big-Ticket-Anschaffungen**
(Beamer, teure Elektronik, Großmöbel) als „Unser Pick" mit direktem Kauf-CTA — niemand kauft so etwas
spontan für eine Feier. Solche Posten höchstens als **optionalen Hinweis** mit Link zum passenden
**Kaufratgeber** (`/ratgeber/…`, Label „Optional", CTA „Zum Kaufratgeber →"), nicht als Amazon-Direktlink.

**Jede Karte braucht Text.** Label, `<h4>`, ein `<p>` mit dem Kaufargument (1-2 Sätze, warum
genau das beim Gastgeben hilft), `<!-- AFFILIATE -->`, dann der CTA. Eine Karte ohne Beschreibung
ist ein Kauf-Button ohne Grund zu klicken — im September 2026 waren 21 solcher Karten auf 10 Seiten
unterwegs, alle nachträglich per Hand angehängt. **Zwei Karten derselben Seite dürfen nie auf
dieselbe ASIN zeigen** (Kopierfehler; schickt den Leser garantiert auf das falsche Produkt).
Für die Hero-Picks der Hub-Seiten (`cocktailabend`, `girlsnight`, `watchparty`) gilt dasselbe:
`hp-label`, `hp-name`, **`hp-desc`** (ein kurzer Nutzen-Satz), `hp-btn`.
`scripts/check-picks.py` prüft beide Kartentypen, Punkt 11 im Konsistenz-Check.

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
  `scripts/pinterest_oauth.py`. **Scope-Regel:** der Token braucht
  `boards:read,boards:write,pins:read,pins:write` — `boards:write` ist fuer `POST /v5/pins`
  Pflicht, obwohl es nach einem reinen Board-Recht aussieht; ohne es scheitert jeder Pin mit
  `HTTP 401 – Missing: ['boards:write']`. Der Tausch-Schritt prueft das erteilte `scope`-Feld
  und schreibt bei einer Luecke gar kein Secret. Board-Zuordnung über Board-**Namen** in
  `pinterest/boards.json` — kein Secret pro Hub. Vor dem ersten scharfen Lauf immer erst die
  Workflow-Modi `doctor` und `dry-run` benutzen.
- **Doppelpost-Regel:** Die Queue-Dateien sind die einzige Sperre gegen doppelte Pins — was auf
  `"published": false` steht, wird gepostet. Pins, die schon per RSS oder Bulk-CSV draußen sind,
  stehen dort trotzdem noch auf `false`. Nicht raten, sondern messen: Modus `check-duplicates`
  liest die Pins der Ziel-Boards per API und meldet pro offenem Queue-Eintrag `neu` oder `DOPPELT`
  (Abgleich ueber Ziel-URL ohne Fragment, sonst Titel). Ist alles doppelt, danach
  `mark-published-only` laufen lassen (hakt alles ab, ohne zu posten), sonst legt die API
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
