# Echte Amazon-Produktkarten — Plan & Aktivierung

**Ziel:** Auf den Anlass-Seiten echte Amazon-Produktkarten zeigen — **echtes Produktbild, Titel, aktueller Preis, Prime-Hinweis** — automatisch aktuell. Das ist der große Conversion-Hebel (man sieht genau, was man kauft).

**Status:** vorbereitet, **noch nicht aktiv.** Bis zur Freischaltung nutzen wir unsere eigenen, produktnahen Bilder + robuste Amazon-Suchlinks (regelkonform, kein Risiko).

---

## ⚠️ Wichtig zur Rechtslage (warum nicht „einfach Bilder nehmen")
- Amazon-Produktbilder dürfen **NICHT** heruntergeladen und selbst gehostet werden (Seite **oder** Pins). Das verstößt gegen die Associates-Bedingungen + Urheberrecht → **Kontosperre** möglich.
- Der **einzige erlaubte Weg**, echte Bilder/Titel/Preise zu nutzen, ist die **offizielle Amazon-API** (früher *PA-API*, Nachfolger *Creators API*).
- Quellen: Amazon Operating Agreement; PA-API/Creators-API-Doku.

## 🔑 Voraussetzung für den API-Zugang
Amazon schaltet die Product-Advertising-/Creators-API erst frei, nachdem das Partner-Konto **~3 qualifizierte Verkäufe innerhalb von 180 Tagen** über die Affiliate-Links erzielt hat. → **Erst Verkäufe, dann echte Produktbilder.**

---

## 🏗️ Architektur (für statische GitHub-Pages-Seite)
Die API **darf nicht clientseitig** aufgerufen werden — der Secret Key würde im öffentlichen Code landen. Stattdessen:

```
ASIN-Liste (data/produkte.json)
        │
        ▼
GitHub Action  ──►  scripts/build-amazon-cards.mjs
 (Secrets:            └─ ruft Amazon-API serverseitig auf
  ACCESS_KEY,            (Bild-URL, Titel, Preis, Prime)
  SECRET_KEY,         └─ schreibt die Daten in data/produkte.json zurück
  PARTNER_TAG)        └─ committet das Ergebnis
        │
        ▼
Statische Produktkarten rendern (App liest produkte.json)
```

- **Secrets** liegen in *GitHub → Settings → Secrets and variables → Actions* — niemals im Repo.
- Die Seite bleibt **100 % statisch**; nur der Build holt die Daten (z. B. täglich, damit Preise aktuell bleiben).
- Amazon-Vorgabe: API-Bilder/Preise dürfen **max. 24 h** gecacht werden → Build täglich per Cron laufen lassen.

## 🗂️ Datenschema
Siehe `data/produkte.example.json`. Pro Pick:
- `slot` — interne Bezeichnung (z. B. „Outdoor-Lichterkette")
- `asin` — die Amazon-ASIN des konkreten Produkts *(leer = noch Suchlink)*
- `suchlink` — aktueller Amazon-Suchlink mit `tag=cozylore-21` (Fallback, funktioniert immer)
- `eigenes_bild` — unser produktnahes Bild (Fallback bis API aktiv)
- `titel` / `preis` / `bild_api` / `prime` — werden vom Build aus der API gefüllt (jetzt `null`)

Die Render-Logik nutzt: **API-Felder, wenn vorhanden — sonst unser eigenes Bild + Suchlink.** So bricht nie etwas, und die Umstellung ist ein sanfter Übergang.

---

## ✅ Aktivierungs-Checkliste (wenn die ersten Verkäufe da sind)
1. **API-Zugang beantragen** im Partner-Konto (Tools → Product Advertising API / Creators API) → Access Key + Secret Key generieren.
2. Die 3 Keys als **GitHub Secrets** anlegen: `AMAZON_ACCESS_KEY`, `AMAZON_SECRET_KEY`, `AMAZON_PARTNER_TAG` (= `cozylore-21`).
3. In `data/produkte.json` die **ASINs** der konkret empfohlenen Produkte eintragen (statt nur Suchlink).
4. `scripts/build-amazon-cards.mjs` fertig implementieren (API-Call + Felder schreiben) — Gerüst ist angelegt.
5. GitHub-Action-Workflow (täglicher Cron) aktivieren.
6. Produktkarten-Render auf API-Felder umstellen → echte Bilder/Preise live. 🎉

**Bis dahin:** eigene Bilder + Suchlinks behalten, Fokus auf Traffic & die ersten Verkäufe.
