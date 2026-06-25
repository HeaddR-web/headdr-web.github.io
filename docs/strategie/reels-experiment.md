# 🎬 Reels-Experiment: Higgsfield-Video-Funnel (Proof of Concept)

> **Ziel:** Risikofrei beweisen, dass wir per Higgsfield kurze Social-Videos (Reels/Idea Pins)
> für BeThatHost-Themen erzeugen können — bevor wir den Funnel automatisieren oder auf
> ein riskantes Thema (Finanzen) übertragen.

## ✅ Ergebnis des ersten Tests (2026-06-24)

- **Thema:** WM-/Fußball-Watchparty (saisonal, Juni 2026)
- **Modell:** `kling3_0_turbo` (schnelles Text-zu-Video)
- **Format:** 9:16 vertikal, **5 Sek.** (⚠️ nur Technik-Test — zu kurz für einen echten Reel, siehe unten), 720p
- **Kosten:** ~**7,5 Credits** pro 5-Sek-Clip → sehr günstig, viele Tests möglich
- **Ergebnis-Video:** `hf_20260624_152846_98459946-b85a-412f-b301-dc40f3322a8a.mp4`
  (in der Higgsfield-History abrufbar; Job-ID `98459946-b85a-412f-b301-dc40f3322a8a`)

**Fazit:** Der Funnel funktioniert technisch und ist spottbillig. ✔️ ABER 5 Sek. ist nur ein Test —
für echte Reichweite brauchen wir das richtige Format (siehe „Was performt wirklich").

## 🔥 Was performt wirklich (recherchiert 2026-06-24)

**Nicht die Länge entscheidet, sondern die Completion-Rate + der Hook.**

- **Optimale Länge:** **7–15 Sek.** für maximale Reichweite (leicht zu Ende zu schauen + loopt), **15–30 Sek.** für höchste Interaktion. → Unsere 5 Sek. sind zu kurz; **Ziel ~10–15 Sek.**
- **Hook in den ersten 1,5–3 Sek. ist alles:** ~50 % springen sonst ab. Direkt in den spannendsten Moment, **kein Logo-/Slow-Intro.** Drei Ebenen gleichzeitig: auffälliges Bild + emotionaler Satz + Text-Overlay mit Neugier-Lücke.
- **Watch-Time + Loops** sind das wichtigste Ranking-Signal. 10-Sek-Reel mit 80 % Completion schlägt 60-Sek-Reel mit 30 %.
- **Sends (Weiterleiten per DM) zählen 3–5× mehr als Likes** für neue Reichweite → Content machen, den man Freunden schickt.
- ⚠️ **Originality-Score:** Instagram drosselt recycelten/generischen Content. Reiner Faceless-KI-Brei ohne eigenen Twist verliert Reichweite → unser **Humor/Winkel** ist Pflicht, kein Bonus.
- **Erste Stunde aktiv sein:** auf Kommentare antworten → Engagement-Signal.

**Konsequenz für unsere Higgsfield-Produktion:** Ein 5-Sek-Clip ist zu kurz. Lösung: **2–3 kurze
Clips zu ~10–15 Sek. zusammenschneiden** + **Text-Hook** in Sek. 1 + Untertitel. Higgsfield Personal
Clipper kann Untertitel brennen.

### 📌 Plattform-Spezifika
- **Instagram Reels:** 9:16, Ziel 7–30 Sek., < 90 Sek. fürs Feed-Discovery.
- **Pinterest Idea Pins:** 9:16 (1080×1920), **15–60 Sek. gesamt**, 3–7 Seiten à 10–20 Sek., Caption 300–500 Zeichen mit Keywords. Ideal für Schritt-für-Schritt (Deko/Rezepte) — passt perfekt zu BeThatHost.

### 🗓️ Wie viel posten?
- **Neuer Account:** Konsistenz schlägt Masse → **3 Reels/Woche** nachhaltig starten.
- **Wachstum:** auf **4–7/Woche** steigern. Größter Reichweiten-Sprung beim Wechsel von 1–2 → 3–5/Woche.
- **Nicht** 10+/Woche auf Kosten der Qualität — bringt Rückschritt + Burnout.

### Quellen
- [Reels-Länge 2026 (heytrendy)](https://heytrendy.app/blog/instagram-reel-length) · [Retention/Länge (OpusClip)](https://www.opus.pro/blog/ideal-instagram-reels-length)
- [Hook-Formeln & Viralität (OpusClip)](https://www.opus.pro/blog/instagram-reels-hook-formulas) · [Reels-Reichweite 2026 (TrueFuture)](https://www.truefuturemedia.com/articles/instagram-reels-reach-2026-business-growth-guide)
- [Post-Frequenz 2026 (Buffer, 2 Mio. Posts)](https://buffer.com/resources/how-often-to-post-on-instagram/) · [Frequenz (Kontentino)](https://www.kontentino.com/blog/how-often-to-post-on-instagram/)
- [Pinterest Idea Pins Länge/Format (OpusClip)](https://www.opus.pro/blog/pinterest-idea-pins-length-format-for-retention)

## 🍳 Wiederholbares Rezept (Mensch-im-Loop)

1. **Thema wählen** aus dem Saison-Kalender (`money-roadmap.md`).
2. **Prompt-Schema** (hat hier funktioniert): `Vertical social media reel, cinematic. [Szene auf Deutsch-Englisch beschreiben: Setting, Deko, Snacks, Licht]. [Kamerabewegung: slow push-in / pan]. Energetic, inviting, premium look.`
3. Mit `get_cost: true` **Kosten vorab prüfen** (Routine).
4. Generieren (`count: 1` zum Testen, `count: 2–4` für Auswahl).
5. **Mensch prüft** das Ergebnis (Qualität, keine seltsamen Artefakte) — nie blind posten.
6. Caption + Hashtags + Ziel-Link (Kategorie-Anker) dazu, wie bei den Pinterest-Pins.

## 📈 Nächste Ausbaustufen (wenn das zündet)

- [ ] 3–5 verschiedene Party-Themen als Reels testen → welches Format performt?
- [ ] Bestehende Party-**Bilder** aus `assets/` per Image-to-Video animieren (statt nur Text-zu-Video) — oft realistischer
- [ ] Text-Overlay/Untertitel hinzufügen (Higgsfield Personal Clipper kann Untertitel brennen)
- [ ] Reels in die Pinterest-Idea-Pin- bzw. Instagram-Pipeline einklinken
- [ ] **Erst wenn ein Format nachweislich Reichweite bringt:** Upload automatisieren

## 💡 Warum das auch für Venture #2 (Finanz) zählt

Dieser Test beweist das **Video-Playbook** an einem rechtlich unbedenklichen Thema. Genau dieses
bewiesene Playbook ist die Voraussetzung, bevor wir es jemals auf Finanz-Content übertragen
(siehe `venture-2-finanz-instagram.md`). Erst hier gewinnen, dann dort wagen.

---

_Experiment durchgeführt: 2026-06-24 mit Higgsfield (Plus-Plan)._
