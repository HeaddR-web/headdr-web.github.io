# 💰 BeThatHost — Money-Roadmap (der Nordstern)

> **Zweck dieses Dokuments:** Mein „Giga Brain" an einer Stelle. Es sagt mir, *woran* ich
> arbeite, *in welcher Reihenfolge*, und *warum*. Wenn ich unterwegs am Handy bin und nicht
> weiß, was ich tun soll → ich öffne diese Datei und nehme die oberste offene Aufgabe.
>
> **Die wichtigste Regel:** Tiefe schlägt Breite. Ein fertiges Projekt = Geld.
> Zehn halbfertige = 0 €. Keine neuen Baustellen, bevor das hier läuft.

---

## 🎯 Das EINE Ziel (Nadelöhr)

> **Die ersten 3 Amazon-Verkäufe in 180 Tagen erreichen.**

Warum genau das? Weil Amazon erst danach die Product-Advertising-/Creators-API freischaltet
(echte Produktbilder, Preise, Prime-Hinweis = der große Conversion-Hebel). Vorher dreht sich
alles um **Traffic → Klicks → erste Verkäufe**. Alles andere ist nachrangig.

```
   TRAFFIC          →     KLICKS          →    VERKÄUFE      →   API frei    →   FLYWHEEL
(Pinterest + SEO)      (Affiliate-Links)     (3 in 180 Tg.)   (echte Bilder)   (mehr Conversion)
```

Wir sind bei Schritt 1–2. Hier muss die ganze Energie rein.

### 🧭 Der UX-Nordstern: Einkaufen so leicht wie möglich machen

> Jede Seite und jeder Pin hat **eine Aufgabe**: dem Besucher das Einkaufen für seine Party
> **erleichtern** — vermitteln *und* ermöglichen. Wenn eine Änderung das Kaufen nicht
> leichter macht, ist sie nachrangig.

Konkrete Regeln, an denen wir jede Seite messen:
- **Alles direkt kaufbar, kein Suchen:** Jedes empfohlene Produkt = ein direkter Amazon-Link auf der Seite. (Umgesetzt 2026-06-24: Kategorie-Karten zeigen jetzt die *komplette* Liste, nicht nur einen Pick — Themen Watchparty, Cocktailabend, Girlsnight.)
- **Ein klarer Top-Pick pro Kategorie** (Vertrauen) **+ die volle Liste darunter** (Vollständigkeit).
- **Pin → genau die richtige Stelle:** Pins zeigen auf die Kategorie-Anker-URL, nicht auf die Startseite.
- **Kein Tab-Chaos / keine Sackgassen:** der Weg vom Ankommen bis zum Amazon-Klick ist kurz.
- **Offene Idee (Stufe 2):** „Meine Party-Liste" — Produkte über Kategorien hinweg sammeln und auf einen Schlag öffnen (CSS dafür liegt schon bereit: `.mynight`).

---

## 🥇 Priorität 1: Traffic-Maschine am Laufen halten (Pinterest)

Pinterest ist der Motor: Pin → Website → Affiliate-Klick. Der Auto-Upload läuft bereits
über GitHub Actions, gesteuert über die Notion-Tabelle / `docs/notion/content-plan.csv`.

- [ ] **Jede Woche 5–10 neue Pins** in die Pinterest-Pipeline geben (Status `To Do` → wird gepostet)
- [ ] Pins immer auf eine **konkrete Kategorie-Anker-URL** zeigen lassen (z. B. `…/watchparty/#cat-decor`), nie nur auf die Startseite
- [ ] Saisonale Themen vorziehen (siehe „Saison-Kalender" unten) — Pinterest belohnt Vorlauf von 4–6 Wochen
- [ ] Funktioniert der Pinterest-Workflow noch? → Actions-Tab prüfen, rote Läufe fixen

**Mobiler Befehl an Claude:** *„Erstelle 8 neue Pin-Zeilen für die content-plan.csv zum Thema X, mit Beschreibung + Hashtags + Ziel-Link."*

---

## 🥈 Priorität 2: Content-Surface vergrößern (mehr Ratgeber & Guides)

Mehr gute Seiten = mehr Pin-Anlässe + mehr Google-Long-Tail = mehr Traffic-Eingänge.
Jeder neue Ratgeber ist ein neuer Verkaufstrichter.

- [ ] Pro Woche **1 neuer Kaufratgeber** (Muster: `ratgeber/…`) zu einem Produkt mit echtem Suchvolumen
- [ ] Pro Woche **1 neuer Guide-Post** in einer bestehenden Rubrik (`*/posts/…`)
- [ ] Jeder neue Artikel: interne Links zu 2–3 verwandten Seiten (hält Besucher auf der Seite)
- [ ] Jeder neue Artikel: in `sitemap.xml` eintragen (passiert idealerweise automatisch im Build)

**Mobiler Befehl an Claude:** *„Schreib einen neuen Kaufratgeber zu [Produkt] im gleichen Stil wie ratgeber/raclette-fondue-set.html, mit Affiliate-Suchlinks (tag=cozylore-21)."*

### Ideen-Backlog (nächste Ratgeber/Guides)
> Hier sammle ich Themen. Claude darf diese Liste ergänzen, wenn ihm gute Themen einfallen.
- [ ] _(z. B. „Beste Heißluftfritteuse für Partysnacks")_
- [ ] _(z. B. „Outdoor-Heizstrahler für Gartenpartys")_
- [ ] _(…)_

---

## 🥉 Priorität 3: Geld-Hygiene (kein Cent darf verloren gehen)

- [ ] Stichprobe: Funktionieren die Affiliate-Links? Ist überall `tag=cozylore-21` dran?
- [ ] Keine selbst gehosteten Amazon-Produktbilder (→ Kontosperre-Risiko, siehe `docs/amazon-produktkarten.md`)
- [ ] `ads.txt` korrekt (Display-Werbung)
- [ ] Datenschutz/Impressum aktuell (Affiliate- + Werbe-Hinweis Pflicht in DE)

**Mobiler Befehl an Claude:** *„Prüf alle Amazon-Links auf der Seite, ob der Affiliate-Tag fehlt, und melde mir Treffer."*

---

## 🚀 Stufe 2: Erst NACH den ersten 3 Verkäufen

Nicht vorher anfassen — das ist die Belohnung, nicht die Vorarbeit:
- [ ] Amazon-API beantragen → Keys als GitHub Secrets (siehe `docs/amazon-produktkarten.md`, Checkliste)
- [ ] `scripts/build-amazon-cards.mjs` fertig implementieren (echte Bilder/Preise per Cron)
- [ ] Produktkarten-Render auf API-Felder umstellen

---

## 🗓️ Saison-Kalender (Pinterest-Vorlauf einplanen!)

| Monat | Thema-Fokus (4–6 Wochen vorher pinnen) |
|-------|----------------------------------------|
| Jun–Jul | WM/Fußball-Watchparty, Gartenparty, Grillabend |
| Aug–Sep | Spätsommer, Cocktailabend, Geburtstag |
| Okt–Nov | Cozy/Herbst, Spieleabend, Halloween-Deko |
| Dez | Cozy-Winter, Silvester, Raclette/Fondue |
| Jan–Feb | Valentinstag, Mädelsabend/Galentine's, Spa-Abend |
| Mär–Mai | Frühling, Brunch, JGA-Saison, Mottopartys |

---

## 📱 So arbeite ich unterwegs (das „mobile Kommandozentrum")

1. **GitHub-App** auf dem Handy: Issues lesen/anlegen, diese Roadmap abhaken.
2. **Claude Code im Web** (claude.ai/code): Ich schreibe eine Aufgabe, Claude baut + committet + pusht — auch aus der Bahn.
3. Faustregel: Wenn ich 5 Minuten habe → eine Checkbox hier abarbeiten oder einen mobilen Befehl an Claude schicken.

---

## 📊 Fortschritt (hier ehrlich mitschreiben)

- Amazon-Verkäufe bisher: **0 / 3**
- Indexierte Seiten (sitemap): **~62**
- Letztes Review dieser Roadmap: _2026-06-24_

> Wenn diese Datei 4 Wochen nicht angefasst wurde → ist ein schlechtes Zeichen. Dann zurück zu Priorität 1.
