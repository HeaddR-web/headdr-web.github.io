# BeThatHost

Statische Website (GitHub Pages) rund ums Gastgeben: Anlässe & Mottopartys mit konkreten
Produkt-Empfehlungen. Domain: **bethathost.de**. Zweite Marke **Cozylore** unter `cozy/`.

> **Für Mitwirkende & Agenten:** Die verbindlichen Regeln stehen in **[`CLAUDE.md`](CLAUDE.md)**.

## Struktur
```
/                     Startseite (Anlässe + Mottopartys)
<anlass>/index.html   Anlass-/Motto-Seiten (girlsnight, jga, hawaii-tiki, …)
  └─ posts/           Blog-Artikel (Legacy-Layer)
cozy/                 Cozylore — eigene Marke (eigenes CSS, Englisch)
assets/style.css      ⭐ zentrale, einzige Design-Quelle (BeThatHost)
assets/motion.css     Animationen
ratgeber/             Kaufratgeber-Seiten
pinterest/            Pinterest-Pipeline (siehe pinterest/README.md)
scripts/              Hilfsskripte + check-consistency.sh
.claude/agents/       Wiederverwendbare Agenten-Rollen
.github/workflows/    Automatisierung (s. u.)
```

## Automatisierung („wie ein echtes Projekt")
- **GitHub-Agent** — `@claude` in einem Issue/PR-Kommentar löst `claude.yml` aus: der Agent
  ändert Code, öffnet PRs, beantwortet Fragen. *Voraussetzung:* Repo-Secret `ANTHROPIC_API_KEY`.
- **Konsistenz-Guardrail** — `consistency.yml` läuft bei jedem Push/PR und blockt
  Design-Inkonsistenz (eine zentrale CSS, keine Playfair/Inter, einheitliche Pfade/Titel).
- **Pinterest** — geplante Workflows posten/queuen Pins (s. `pinterest/README.md`).

## Lokal prüfen
```bash
bash scripts/check-consistency.sh   # muss grün sein, bevor du pushst
```

## Konventionen (Kurzfassung)
- Eine zentrale `/assets/style.css` — niemals pro-Ordner-Kopien.
- Fonts: **Fraunces + Hanken Grotesk** (BeThatHost). Cozylore separat.
- Titel: `… — BeThatHost`. Affiliate-Tag: `cozylore-21`.
- Branch je Aufgabe, PR statt Direkt-Push. Details: `CLAUDE.md`.
