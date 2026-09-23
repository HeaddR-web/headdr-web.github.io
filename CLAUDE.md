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
  `/assets/fonts/fonts.css`; die Originale liegen in `/assets/fonts/src/`, siehe
  Abschnitt „Schriftdateien“). **Niemals** dynamisch vom Google-Fonts-CDN laden
  (`fonts.googleapis.com`/`fonts.gstatic.com`, auch kein `preconnect` dorthin) —
  das überträgt beim Seitenaufruf die Besucher-IP an Google-Server ohne
  Einwilligung (DSGVO Art. 6; vgl. LG München I, Urt. v. 20.01.2022, Az. 3 O
  17493/20). Jede Seite bindet stattdessen ein:
  `<link rel="stylesheet" href="/assets/fonts/fonts.css" />`
  Davor stehen zwei **Preload-Zeilen** fuer die beiden Schnitte, die above the fold
  gebraucht werden (`fraunces.woff2`, `hanken-grotesk.woff2`, jeweils mit `crossorigin`).
  Grund: `fonts.css` ist ein eigenes Stylesheet, ohne Preload entdeckt der Browser die
  `woff2` erst danach, tauscht die Schrift mitten im Aufbau und schiebt alles darunter
  nach unten — gemessen **CLS 0,13** auf `watchparty/` und `cocktailabend/` (Schwelle 0,1).
  Mit Preload: 0,01.
  Neue Schriftschnitte: mit modernem Browser-User-Agent von
  `fonts.googleapis.com/css2?family=...` abrufen, die `woff2`-URLs
  (`fonts.gstatic.com`) daraus greifen, nach `/assets/fonts/` herunterladen,
  `@font-face` in `fonts.css` ergänzen — nie den CDN-Link selbst einbinden.

## Anatomie einer Anlass-/Motto-Seite (`<ordner>/index.html`)
1. `<head>`: charset/viewport, `<title>… — BeThatHost</title>` (**max. 60 Zeichen inkl.
   „ — BeThatHost"** — Google zeigt rund 580 Pixel; bis September 2026 waren 24 Titel länger,
   hinter dem Schnitt verschwand genau die Marke. Hauptsuchwort nach vorn; die `<h1>` darf
   länger sein), meta description
   (**max. 160 Zeichen** — Google schneidet deutsche Snippets bei rund 155-160 ab;
   `scripts/check-meta.py` prüft das mit, Punkt 10 im Konsistenz-Check), canonical,
   og-Tags, **Article + FAQPage JSON-LD**, `/assets/fonts/fonts.css` (self-hosted, kein CDN),
   `/assets/style.css`, `/assets/motion.css`, AdSense-Verifizierungs-Meta (Skript selbst erst
   nach Consent, siehe Abschnitt „Cookie-Consent" unten).
2. `<header class="site">`: Brand `<a class="brand" href="/">BeThatHost</a>` + Nav mit genau
   zwei Links: `Alle Anlässe` → `/`, `Über uns` → `/ueber-uns.html` (absolute Pfade, einheitlich auf allen Ebenen).
3. `<article>`: generierte **Brotkrume** (`<nav class="breadcrumb">`, siehe unten), Lead-Bild (3:2), `<h1>`, `<p class="meta">Aktualisiert am … · 5 Min. Lesezeit · BeThatHost</p>`,
   Intro, **Einkaufslisten-Block** (`<aside class="quickbuy">`, siehe unten), **Inhaltsverzeichnis**
   (`<nav class="toc">`, siehe unten), thematische Abschnitte mit
   `<div class="pick">`-Karten, ein **leerer** `<div class="ad-slot"></div>` (siehe unten), zum Schluss der
   generierte **FAQ-Abschnitt** (`<section class="faq">`, siehe unten).
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

## Article-JSON-LD: `image` und `dateModified` — generiert
Bis September 2026 fehlten beide Felder im `Article`-JSON-LD aller 33 Artikelseiten. Google
fuehrt sie als empfohlen; ohne `image` kommt eine Seite fuer die Bilddarstellung in der Suche
und in Discover nicht in Frage, die Search Console meldet sie als unvollstaendig.

- Gebaut von `scripts/build-article-jsonld.py`. **Nicht von Hand pflegen** — beide Zeilen
  werden bei jedem Lauf entfernt und neu gesetzt.
- **Quellen stehen schon auf der Seite:** `image` ← `og:image`, `dateModified` ← sichtbares
  „Aktualisiert am 19. Juni 2026" im `<p class="meta">`. Google verlangt, dass Markup-Datum und
  sichtbares Datum uebereinstimmen — deshalb ist das sichtbare Datum die Quelle, und das Skript
  setzt es nie selbst. Wer eine Seite wesentlich ueberarbeitet, aendert das sichtbare Datum
  und laesst danach das Skript laufen.
- Nach jeder Aenderung an `og:image` oder am sichtbaren Datum:
  `python3 scripts/build-article-jsonld.py`
- Punkt 19 im Konsistenz-Check.

## `llms.txt` — generiert, nie von Hand
`robots.txt` lädt GPTBot, ClaudeBot, PerplexityBot & Co. ausdrücklich ein; `llms.txt` ist das
Inhaltsverzeichnis, das diese Crawler lesen. Von Hand angelegt am 20. Juli 2026 und danach nie
wieder angefasst, fehlten im September 2026 **24 von 37 Seiten** — alle Mottopartys, alle
Anlass-Seiten, alle Kaufratgeber.

- Gebaut von `scripts/build-llms.py`, **aus den Listen, die es schon gibt**: Seiten und
  Linktext aus `THEMA` und `NAME` in `build-related.py`, Beschreibung aus der meta description.
  Wer eine Seite in `THEMA` einträgt, hat sie damit auch in `llms.txt`.
- Neues Thema in `THEMA`: auch in `ABSCHNITTE` von `build-llms.py` eintragen — sonst bricht
  das Skript ab, statt das Thema still zu verschweigen.
- Nach jeder Änderung an `THEMA`/`NAME` oder an einer meta description:
  `python3 scripts/build-llms.py`
- Punkt 20 im Konsistenz-Check.

## Fehlerseite (`404.html`)
GitHub Pages liefert `/404.html` für jede unbekannte URL aus. Bis September 2026 gab es keine —
wer über einen alten Pin oder einen Tippfehler kam, sah die nackte GitHub-Fehlerseite ohne
einen einzigen Link zurück. Die Seite steht auf `noindex, follow`, nutzt nur **absolute** Pfade
(sie wird unter jeder beliebigen URL ausgeliefert) und ist wie die Rechtstexte von Werbeplatz,
Brotkrume, Verzeichnis und Weiterlesen-Block ausgenommen.

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

## Brotkrumen (`nav.breadcrumb`) — generiert, nie von Hand
Ganz oben in jedem Artikel steht der Weg dorthin: `Start › Mottopartys › Casino-Abend`.
Grund: Bis September 2026 stand dort ein einzelner Rückwärts-Link in **acht** verschiedenen
Ausführungen (19× „Alle Anlässe", daneben „Zurück zur Ausstattung", „Zurück zur Snack-Liste"
und vier weitere). Auf den Unterseiten fehlte die mittlere Ebene ganz: von der Pyjama-Party
kam man zum Mädelsabend, aber der Weg zur Startseite war unsichtbar. Dazu der Auftritt in der
Suche: ohne `BreadcrumbList` zeigt Google unter dem Titel die nackte URL.

- Gebaut von `scripts/build-breadcrumb.py`. **Niemals von Hand bearbeiten** — der Block steht
  zwischen `<!-- BREADCRUMB:START … -->` und `<!-- BREADCRUMB:END -->` und wird bei jedem Lauf
  komplett ersetzt. Er enthält beides: die sichtbare Zeile **und** das `BreadcrumbList`-JSON-LD.
- **Die Kategorie kommt aus der Startseite selbst.** In welchem `<section id="…">` die Karte
  einer Seite steht, das ist ihre Kategorie (`#anlaesse` → „Anlässe", `#mottopartys` →
  „Mottopartys", `#ratgeber` → „Kaufratgeber"). Verschiebt jemand eine Karte, wandert die
  Brotkrume beim nächsten Lauf mit — es gibt keine zweite Liste, die veralten könnte.
  Der Linktext kommt aus `NAME` in `build-related.py`, damit eine Seite nicht an zwei Stellen
  anders heißt.
- **Wo der Block landet:** Artikelseiten direkt hinter `<article>` (also über dem Lead-Bild),
  Hub-Seiten in den `hero-inner`-Kasten über die Eyebrow-Zeile. Beides liegt innerhalb eines
  Containers — außerhalb greift kein Seitenrand.
- Der alte `<a class="backlink">` wird dabei ersetzt; er bleibt nur auf `/ueber-uns.html`, das
  keine Brotkrume bekommt. Die CSS-Regel dafür bleibt deshalb in `/assets/style.css`.
- Nach jeder Änderung an den Startseiten-Karten oder an `NAME`:
  `python3 scripts/build-breadcrumb.py`
- `scripts/check-breadcrumb.py` prüft das mit, Punkt 16 im Konsistenz-Check.

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
- Links immer **absolut** (`/casino/`) — auf der **ganzen** Seite, nicht nur im Block.
  `../index.html` zeigt auf den Guide-Unterseiten eine Ebene daneben, und `/index.html`
  ist eine zweite URL für die Startseite, deren Canonical `/` lautet.
- **Nichts zwischen `</main>` und `<footer>`.** Dort greift kein Layout-Container: der
  Inhalt läuft randlos über den ganzen Bildschirm. Genau so standen 14 handgemachte
  „Weitere Ideen:"-Absätze auf der Seite — randlos und inhaltlich doppelt unter dem
  Weiterlesen-Block, den sie ersetzen sollten. `ALT_RE` in `build-related.py` räumt
  beide Schreibweisen („Weitere Anlässe:" und „Weitere Ideen:") weg.
- `scripts/check-related.py` prüft das mit, Punkt 14 im Konsistenz-Check: Block aktuell,
  keine Waisen, kein interner Link auf eine Datei, die es nicht gibt.

## FAQ-Abschnitt (`section.faq`) — generiert, nie von Hand
Am Ende des Artikels, vor dem Weiterlesen-Block, steht der sichtbare FAQ-Abschnitt.
Grund: Im September 2026 trugen **16 Seiten** ein `FAQPage`-JSON-LD, dessen zwei bis drei
Fragen im Artikel **nirgends vorkamen** — darunter beide Hubs `cocktailabend/` und
`watchparty/` sowie alle fünf `ratgeber/`-Seiten. Googles Richtlinie für strukturierte Daten
verlangt, dass der ausgezeichnete Inhalt für den Besucher sichtbar ist; unsichtbare
Auszeichnung riskiert eine manuelle Maßnahme. Teurer noch: Wer die Frage im Suchergebnis
anklickt, landet auf einer Seite ohne die Antwort und ist sofort wieder weg.

- **Das JSON-LD ist die Quelle, der sichtbare Block die Ausgabe.** Gebaut von
  `scripts/build-faq.py` aus dem `FAQPage`-JSON-LD der Seite. **Niemals von Hand bearbeiten** —
  der Block steht zwischen `<!-- FAQ:START … -->` und `<!-- FAQ:END -->` und wird bei jedem
  Lauf komplett ersetzt. Neue Frage also **im JSON-LD** ergänzen, nicht im Markup.
- Nach **jeder** Änderung am `FAQPage`-JSON-LD:
  `python3 scripts/build-faq.py && python3 scripts/build-toc.py`
  Das Verzeichnis muss hinterher, weil der Block eine neue `<h2 id="haeufige-fragen">` mitbringt.
- **Wo der Block landet:** ans Ende des Inhalts-`<article>`. Produktkarten (`cat-card`,
  `post-card`) zaehlen dabei nicht als Artikel — ein blosses „letztes `</article>`" traf auf
  den Hub-Seiten die letzte Kachel, und die FAQ stand bis September 2026 mitten im
  Kachelgitter (wo `app.js` sie beim Neuaufbau ersatzlos wegraeumte). Hub-Seiten haben gar
  keinen Inhalts-`<article>`; dort geht der Block vor den Weiterlesen-Block.
- Entfällt das JSON-LD, räumt das Skript den Block weg — eine Seite soll nie eine FAQ zeigen,
  die die Structured Data nicht mehr decken.
- `scripts/check-faq.py` prüft beide Richtungen, Punkt 15 im Konsistenz-Check: JSON-LD ohne
  sichtbaren Block **und** sichtbarer Block ohne JSON-LD.

## Kachelbilder (`assets/img/kachel/`, `assets/img/hero/`) — generiert, nie von Hand
Die Kategorie-Kacheln (Startseite `a.occ-media img`, Hubs `div.cover` und `div.thumb`) zeigen
ein Bild von rund 360 × 270 Punkten. Ausgeliefert wurden bis September 2026 die Originale mit
1264 × 848 bis 1600 × 2385 Pixeln — auf `girlsnight/` allein 2,5 MB Kacheln, gemessener
**LCP 6,2 s** auf gedrosseltem Mobilfunk (Schwelle 2,5 s), auf der Startseite 4,5 s.

- Gebaut von `scripts/build-images.py`. Die Ableitungen liegen in `/assets/img/kachel/`
  und `/assets/img/hero/` (jeweils `<stamm>-<breite>.jpg`). **Die Originale bleiben
  unangetastet** — 29 von ihnen sind zugleich `og:image` oder Lead-Bild, ein Verkleinern an
  Ort und Stelle wuerde die Social-Vorschauen zerstoeren.
- **Zwei Kachel-Leitern, nicht eine.** Die kleinen Kacheln der Hubs (`div.cover`, `div.thumb`)
  haben `KACHEL_BREITEN = (480, 720, 960)`, die grossen Karten der Startseite
  (`a.occ-media`) `BREITEN = (480, 960)`. Die 720er-Stufe gibt es, weil ohne sie **jedes
  Handy die 960er** lud: auf `watchparty/` waren das drei Bilder mit 246 KB, die dem
  Hero-Bild — dem LCP-Element — die Bandbreite nahmen, waehrend es noch unterwegs war.
- **`SIZES_KACHEL` muss zum Gitter passen, auf zwei Pixel genau.** Die Kachelbreite springt
  mit den Spalten: `repeat(auto-fill, minmax(330px, 1fr))` mit 26 px Luecke fuellt bis 719 px
  Bildschirm **eine** Spalte (die Kachel ist dann fast so breit wie der Bildschirm), ab 720 px
  zwei, ab 1076 px drei. Nachgemessen braucht sie auf einem 2x-Display 572 (320 px) bis 1148
  (700 px) Geraetepunkte. Steht in `sizes` eine Zahl, die davon abweicht, laedt der Browser
  die falsche Stufe — mit `47vw` statt `calc(50vw - 30px)` rechnet er bei 768 px 721,9
  Punkte aus, zwei mehr als die 720er Stufe hergibt, und nimmt die 960er. Nach jeder
  Aenderung am Gitter-CSS also nachmessen, nicht schaetzen.
- **Die Stufe darf zu gross sein, nie zu klein.** `.cover` und `.thumb` teilen sich ein
  `sizes`, ihre Gitter brechen aber unterschiedlich um; bei 700 und 1024 px laedt `.thumb`
  deshalb die 960er, wo die 720er reichte. Das ist die richtige Richtung: ein paar Bytes zu
  viel auf dem Tablet kosten weniger als ein hochskaliertes Bild.
- **Das Hero-Bild gibt es zweimal: quer fuers Grosse, hoch fuers Handy.** Der Hero-Kasten ist
  auf dem Handy hoch (288 × 541 bei 320 px Viewport, 358 × 487 bei 390 px), das Desktop-Bild
  dagegen quer (1280 × 858). `background-size: cover` skaliert deshalb nach der Hoehe und
  wirft rund 40 % der Bildbreite weg, die der Besucher trotzdem laedt — und 858 Bildpunkte
  reichen fuer die 974 Geraetepunkte eines 2x-Displays ohnehin nicht. Deshalb zusaetzlich
  `<stamm>-800.jpg` im Hochformat 41:50. Im Markup haengen beide als Custom Property am
  `.hero` (`--hero-img` und `--hero-img-mobil`), in `/assets/style.css` schaltet
  `@media (max-width: 460px)` um. **Beide Preload-Zeilen tragen ein `media`-Attribut** — ohne
  das holt der Browser beide Bilder, und der Handy-Zuschnitt macht die Seite schwerer statt
  leichter. Nachgemessen ist das Handy-Bild exakt gleich scharf (mittlere Kantenstaerke 13,8
  vorher wie nachher) bei rund einem Drittel weniger Bytes.
- **Verwaiste Ableitungen raeumt das Skript weg.** Was in `kachel/` oder `hero/` liegt und von
  keiner Seite mehr verlinkt wird, loescht `build-images.py` (und `check-images.py` meldet es
  als vierten Fehlerfall). Sonst bleibt bei jeder Aenderung an den Stufen — etwa Kacheln von
  960 auf 720 — die alte Datei im Repo liegen, und spaeter ist nicht mehr zu erkennen, welche
  davon noch gebraucht wird.
- Der Dateiname der Ableitung traegt den Stamm des Originals. Deshalb findet das Skript das
  Original auch dann wieder, wenn im Markup laengst die Ableitung steht — der Lauf ist
  beliebig oft wiederholbar. Nach jedem neuen oder getauschten Kachelbild:
  `python3 scripts/build-images.py`
- **Kacheln sind echte `<img loading="lazy">`, nie CSS-Hintergruende.** Ein Hintergrund laesst
  sich nicht verzoegern; auf `girlsnight/` luden so elf Kacheln sofort mit. Das `alt` bleibt
  leer: die Kachel wiederholt nur die Ueberschrift daneben.
- Der 4:3-Zuschnitt aendert sichtbar nichts. `object-fit: cover` und `background-size: cover`
  schneiden beide zentriert; ein zentrierter Zuschnitt auf 4:3 mit anschliessendem Zuschnitt
  auf das Kachel-Format ergibt dasselbe Bild wie ein Zuschnitt direkt aus dem Original.
- **Lead-Bilder der Artikel (`article img.lead`) laufen ueber dasselbe Skript**, Ableitungen in
  `/assets/img/lead/`, Leiter `LEAD_BREITEN = (720, 1080, 1440)` — **ohne Zuschnitt**. Der
  Kasten ist breitengesteuert (`width: 100%`, `max-height: 460px`, `object-fit: cover`), das
  Bild wird bei jedem Viewport nach der Breite skaliert; eine reine Verkleinerung zeigt also
  exakt denselben Ausschnitt. Bis September 2026 kam das Original: 637 KB (1600 × 2385) fuer
  einen 358 × 460-Kasten, gemessener **LCP 4,3 s** auf `world-cup-watch-party`, danach 1,9 s.
  `height: auto` in `/assets/style.css` gehoert dazu — sonst nimmt der Browser das
  `height`-Attribut woertlich und jedes Querformat-Lead waere 460 px hoch.
- `scripts/check-images.py` prueft das mit, Punkt 17 im Konsistenz-Check.

Gemessen (Chromium, 390 × 844, DPR 2, 1,6 Mbit/s, 150 ms Latenz), Ausgangslage → nach den
Ableitungen → nach Kachel-Leiter und Handy-Hero:
`/` 4,51 s → 1,70 s (kein Hero) · `/girlsnight/` 6,23 s → 2,42 s → **1,87 s** ·
`/cocktailabend/` 4,98 s → 2,13 s → **1,75 s** · `/watchparty/` 6,00 s → 2,84 s → **1,93 s**.
CLS ueberall ≤ 0,022. Seitengewicht `/girlsnight/`: 2520 KB → 466 KB.
Auf einem 768-px-Tablet liegen die drei Hubs weiterhin bei 2,5-2,8 s — dort greift der
Handy-Zuschnitt nicht mehr, das Querformat schon.

## Schriftdateien (`assets/fonts/`) — Ableitung aus `assets/fonts/src/`
Die Originale liegen in `assets/fonts/src/`, ausgeliefert wird die Ableitung daneben.
Grund: `hanken-grotesk.woff2` und `fraunces.woff2` haengen als Preload in allen 42 Seiten
und werden damit **vor** dem Hero-Bild geladen — dem LCP-Element. Jedes Kilobyte dort
kostet doppelt.

- Gebaut von `scripts/build-fonts.py` (`--pruefen` meldet nur). Nach jeder Aenderung an
  einer Datei unter `assets/fonts/src/`: `python3 scripts/build-fonts.py`.
- **Nur `hanken-grotesk.woff2` wird geschrumpft**, und nur an der **unteren** Achsenhaelfte:
  `wght: (400, 400, 900)` — Minimum auf 400, Default und Maximum unveraendert. Damit faellt
  der komplette negative Delta-Satz weg (`fonts.css` liefert ohnehin nur 400–700 aus):
  34 704 → 24 052 Bytes (−31 %). Nachgemessen **Pixel fuer Pixel identisch**: ein Specimen
  mit 300/400/500/600/700/800/900 in beiden Schnitten und beiden Werten von
  `font-optical-sizing` ergab 0 abweichende Pixel.
- **Der Default einer Achse darf nie verschoben werden.** Sobald er ausserhalb der neuen
  Grenzen liegt, rechnet fontTools die Umrisse auf ganze Font-Einheiten um und die Schrift
  sieht anders aus. Deshalb immer das **Dreier-Tupel** `(Minimum, Default, Maximum)`
  benutzen, nie die Kurzform `(Minimum, Maximum)`.
- **Auch oben kuerzen (`(400, 700)`): nein.** Spart 856 Bytes, rechnet dabei aber den oberen
  Delta-Satz um: bei `wght: 600` — sieben Mal in `style.css` — wandert die Textbreite um
  einen Pixel, 5 355 Pixel des Specimens weichen ab.
- **`fraunces.woff2` bleibt unangetastet.** Der Default seiner `wght`-Achse liegt bei **900**,
  also ausserhalb der ausgelieferten 400–700; jede Begrenzung verschiebt ihn. Zusammen mit
  der zweiten Achse `opsz` (die `font-optical-sizing: auto`, der CSS-Standard, tatsaechlich
  benutzt) aendert das die Darstellung sichtbar: 45 400 abweichende Pixel, in jeder
  getesteten Variante. Gewinn waeren 3–8 KB — dafuer wird die Schrift hier nicht veraendert.
- Der `cmap` bleibt vollstaendig (ein weiteres Subset koennte aus einem Zeichen ein
  Kaestchen machen). `fraunces-italic.woff2` und `inter.woff2` bleiben unberuehrt
  (Inter gehoert zu `cozy/**` und wird auf BeThatHost nie geladen).
- `scripts/check-fonts.py` prueft das mit, Punkt 18 im Konsistenz-Check: Ableitung nicht
  aktuell, verlinkte Schrift fehlt, vorhandene Schrift verwaist.

Gemessen (Chromium, 390 × 844, DPR 2, 1,6 Mbit/s, 150 ms Latenz), Original → Ableitung:
`/` 1,68 → **1,61 s** · `/watchparty/` 1,96 → **1,90 s** · `/girlsnight/` 1,88 → **1,80 s** ·
`/cocktailabend/` 1,74 → **1,67 s**. CLS unveraendert, 11 KB weniger je Seite.

## Hub-Seiten: `app.js` rendert nur als Rueckfallebene
`cocktailabend/app.js`, `girlsnight/app.js` und `watchparty/app.js` bauen das Kachelgitter
(`#build-grid`) aus einer eingebetteten Liste. Bis September 2026 warfen sie dabei bei jedem
Aufruf das statisch vorgerenderte Gitter weg und bauten es neu — das kostete dreifach:
das Layout sprang sichtbar (**CLS 0,18** auf `watchparty/`), die Kacheln wurden ein zweites
Mal geladen (in voller Aufloesung statt als Ableitung), und **alles, was sonst noch im
Gitter stand, verschwand fuer jeden Besucher mit JavaScript** — auf `cocktailabend/` und
`watchparty/` war das der komplette FAQ-Abschnitt, waehrend das `FAQPage`-JSON-LD ihn
weiterhin behauptete. Dazu fehlte den Zweit- und Dritt-Picks im JS-Aufbau die `hp-desc`,
die im statischen Markup steht.

**Regel:** `render()` baut nur, wenn `#build-grid` noch keine `.cat-card` enthaelt. Was im
HTML steht, gewinnt. Aendert sich eine Kategorie, gehoert sie in **beides** — in das
statische Markup und in die Liste in `app.js`.

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
5. Generatoren laufen lassen: `python3 scripts/build-quickbuy.py`, `build-toc.py`,
   `build-related.py`, `build-faq.py`, `build-breadcrumb.py`, `build-images.py`,
   `build-article-jsonld.py`, `build-llms.py`, `build-sitemap-lastmod.py`.
6. `scripts/check-consistency.sh` laufen lassen — muss grün sein.

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
- **Vor jedem Push:** `bash scripts/check-consistency.sh` (CI erzwingt es ohnehin) und
  `python3 scripts/build-sitemap-lastmod.py` — das Skript holt jedes `<lastmod>` aus dem
  letzten Commit der jeweiligen Datei. Bis September 2026 standen dort durchgehend
  Juni-/Juli-Daten, obwohl alle Seiten im September ueberarbeitet worden waren; Google
  ignoriert `<lastmod>` komplett, sobald die Angabe erkennbar nicht stimmt.
- **Python-Abhaengigkeiten stehen in `scripts/requirements.txt`.** Aktuell nur Pillow
  (fuer `build-images.py` und damit Punkt 17). Ein neues Modul gehoert dort hinein,
  sonst faellt es erst in CI auf: lokal ist es meist schon installiert, der Runner
  bringt nur die Standardbibliothek mit. Genau so scheiterte der erste Lauf mit
  Punkt 17 an `ModuleNotFoundError: No module named 'PIL'`.
- **`paths:` in `.github/workflows/consistency.yml` deckt `scripts/**` mit ab.** Vorher
  liefen bei einer reinen Skript-Aenderung gar keine Checks — der Guard schaltete sich
  genau dann ab, wenn der Guard selbst geaendert wurde.
- Branch je Aufgabe, **kein** Direkt-Push auf `main` ohne PR.
- Commit-Präfixe: `content:`, `design:`, `feat:`, `fix:`, `chore:`.
- Keine Secrets committen (API-Keys etc. liegen als GitHub-Secrets).
- Antworten/Inhalte auf Deutsch (einsprachig — `cozy/**` ist abgekoppelt, siehe oben).

## Automatisierung auf GitHub
- `@claude` in einem Issue/PR-Kommentar → der GitHub-Agent (`.github/workflows/claude.yml`) übernimmt.
- Jeder Push/PR → CI-Konsistenz-Check (`.github/workflows/consistency.yml`).
- Wiederverwendbare Rollen: `.claude/agents/` (consistency-auditor, page-builder, pinterest-manager).
