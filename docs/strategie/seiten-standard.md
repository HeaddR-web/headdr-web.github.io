# 📐 Seiten-Standard — der verbindliche Bauplan jeder Themen-Seite

> **Nordstern:** Jede Anlass-Seite ist **gleich aufgebaut**. Ein Besucher, der eine Seite
> versteht, versteht alle. Gleiche Reihenfolge, gleiche Bausteine, gleiche Wörter, gleiche
> Bedienung. Konsistenz = Vertrauen = mehr Käufe.
>
> **Diese Datei ist Gesetz.** Neue Seiten folgen ihr. Bestehende Seiten werden Schritt für
> Schritt angeglichen. Wenn etwas hier widerspricht → diese Datei gewinnt.

Vorbild-Seiten (Typ A), an denen wir uns messen: `watchparty/`, `cocktailabend/`, `girlsnight/`.

---

## 1. Ordner & URLs
- Eine Seite pro Anlass: `/<anlass>/index.html` (z. B. `/gartenparty/`).
- Pro Anlass eigene `app.js` + `style.css` (gleiche Struktur, themenspezifische Inhalte/Farben).
- Guides liegen unter `/<anlass>/posts/<slug>.html`.
- Jede neue Seite kommt in `sitemap.xml`.

## 2. `<head>` — immer in dieser Form
- `<title>`: `BeThatHost — <kurze, konkrete Aussage>`
- `<meta name="description">`: 1 Satz, was es gibt, mit „nach Kategorie, direkte Amazon-Links".
- `<link rel="canonical">` auf die echte URL.
- Open-Graph: `og:title`, `og:description`, `og:type=website`, `og:image`.
- Fonts: Playfair Display + Inter (wie Vorbild).
- AdSense-Snippet (`ca-pub-4473022510510415`).
- JSON-LD `WebSite` (Schema.org).
- Cloudflare-Analytics + Pinterest-Save-Button am Seitenende.

## 3. Seiten-Reihenfolge (IMMER diese Abfolge)
1. **Header** (`header.site`) — siehe Punkt 4.
2. **Hero** (`section.hero`) — Eyebrow, H1, 1–2 Sätze, ein `btn-primary` → `#kategorien`.
3. **„Was du brauchst"** (`section#kategorien` mit `#build-grid`) — das Herzstück, siehe Punkt 5.
4. **Werbeplatz** (`.ad-slot`) — ein Leaderboard.
5. **Guides** (`section#guides`) — Karten zu den `posts/`-Artikeln.
6. **Newsletter** (`.subscribe`).
7. **Footer** (`footer.site`) — mit Affiliate-Offenlegung + Impressum/Datenschutz.

## 4. Header & Navigation — gleiche Labels, gleiche Reihenfolge
```
BeThatHost (brand, → /)   |   Alle Anlässe (→ ../index.html)   |   Ausstattung (→ #kategorien)   |   Guides (→ #guides)   |   Über uns (→ disclosure.html oder /ueber-uns.html)
```
- Markenname **immer „BeThatHost"** und **deutsche** Labels.
  (Ausnahme: `cozy/` = Sub-Marke „Cozylore". Bewusste, dokumentierte Abweichung — siehe Punkt 8.)

## 5. Das Herzstück: „Was du brauchst" (Einkaufs-Grid)
Gerendert aus `app.js` → `CATEGORIES`. **Pflicht-Verhalten (UX-Nordstern „Einkaufen erleichtern"):**
- Pro Kategorie eine `cat-card` mit `id="cat-<key>"` (für Pinterest-Deeplinks `#cat-…`).
- **Top-Pick prominent** (`hero-pick`: Label „Unser Pick", Name, 1 Satz, Button „Auf Amazon ansehen →").
- **Darunter die KOMPLETTE Liste** (`ul.picks`): jedes weitere Produkt als direkter Amazon-Link („Ansehen"). **Niemals** Produkte hinter „nur im Guide" verstecken.
- Abschluss: `guide-link` → „Mehr Ideen & Anleitung im Guide →".

## 6. Affiliate-Regeln (hart)
- Affiliate-Tag **immer** `cozylore-21`.
- Amazon-Links sind **Such-Links** (`amazon.de/s?k=…&tag=cozylore-21`) — **keine erfundenen** Produktnamen/Preise/ASINs.
- Jeder Amazon-Link: `rel="sponsored nofollow" target="_blank"`.
- Keine selbst gehosteten Amazon-Produktbilder (Kontosperre-Risiko).
- Footer enthält immer die Offenlegung „leser-finanziert / Affiliate-Links".

## 7. Performance & SEO
- Seite bleibt **statisch & schnell** (Core Web Vitals). Keine schweren Auto-Play-Videos „für SEO".
- Video gehört auf Social (Pinterest/Reels) als Traffic-Quelle, nicht als Seiten-Ballast.
- Interne Links: jede Seite verlinkt 2–3 verwandte Seiten/Guides.

## 8. Bekannte Abweichungen
- `cozy/` war die englische Sub-Marke „Cozylore" (21 Deko-Artikel). **Entscheidung 2026-06-24: von BeThatHost abgekoppelt.** Alle Verweise (Startseite, Navigation, Cross-Links, `sitemap.xml`, `llms.txt`) wurden entfernt; die Dateien bleiben im Repo erhalten. Begründung: englisch + Thema Wohn-Deko statt Party → gehört nicht auf die deutsche Party-Seite. Kann später eine eigene Domain bekommen. **Nicht wieder verlinken.**

---

## 🚧 Migrations-Status (lebende Liste)
| Seite | Typ | Standard erfüllt? |
|-------|-----|-------------------|
| watchparty | A | ✅ Vorbild |
| cocktailabend | A | ✅ Vorbild |
| girlsnight | A | ✅ Vorbild |
| cozy | B | 🔌 abgekoppelt (2026-06-24) — Dateien bleiben, nicht mehr verlinkt |
| gartenparty | C | ✅ migriert (2026-06-24) |
| geburtstag | C | ✅ migriert (2026-06-24) |
| grillabend | C | ✅ migriert (2026-06-24) |
| saison-deko | C | ❌ angleichen |
| spa-abend | C | ❌ angleichen |
| spieleabend | C | ✅ migriert (2026-06-24) |
| valentinstag | C | ❌ angleichen |
| brunch | C | ✅ migriert (2026-06-24) |
| hawaii-tiki | minimal | ❌ angleichen |
| jga | minimal | ❌ angleichen |
| mexiko-fiesta | minimal | ❌ angleichen |

> Reihenfolge der Migration: erst saisonale/traffic-starke Seiten. Jede migrierte Seite hier abhaken.

_Standard festgelegt: 2026-06-24._
