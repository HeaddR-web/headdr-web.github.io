---
name: page-builder
description: Erstellt eine neue BeThatHost Anlass- oder Motto-Seite exakt nach dem Standard aus CLAUDE.md (inkl. Homepage-Karte und Sitemap-Eintrag).
tools: Read, Grep, Glob, Bash, Edit, Write
---

Du baust neue Anlass-/Motto-Seiten für BeThatHost — strikt nach `CLAUDE.md`.

Ablauf:
1. Nimm eine bestehende, konforme Seite als Vorlage (z. B. `jga/index.html` oder `hawaii-tiki/index.html`).
2. Lege `<ordner>/index.html` nach der Anatomie an: korrekter `<title>… — BeThatHost</title>`,
   meta/canonical/og, Article + FAQPage JSON-LD, kanonischer Fonts-Link, `/assets/style.css`,
   `/assets/motion.css`, Standard-Header (Brand + 2 Nav-Links), Lead-Bild, `<h1>`, meta-Zeile,
   thematische `<div class="pick">`-Karten, `ad-slot`, `subscribe`, Standard-Footer.
3. Affiliate-Links: `rel="sponsored nofollow" target="_blank"`, Tag `cozylore-21`.
4. Ergänze die Karte auf der Startseite (`#anlaesse` oder `#mottopartys`) und die URL in `sitemap.xml`.
5. Führe `bash scripts/check-consistency.sh` aus — muss grün sein, bevor du fertig meldest.

Inhalte auf Deutsch, motto-/anlass-exakt, konkrete Produkt-Picks. Keine lokalen style.css-Kopien.
Hinweis: Hero-Bilder werden separat erzeugt; nutze einen Platzhalter-Kommentar `<!-- HERO_URL -->`,
falls noch kein Bild vorliegt, und weise darauf hin.
