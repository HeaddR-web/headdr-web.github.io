# BeThatHost

Statische Website (GitHub Pages) unter **bethathost.de**. Seit 02.11.2026 ist die Domain nur noch
der Shop für eigene Teile aus dem 3D-Drucker, jedes lässt sich individualisieren. Zum Start gibt
es Platzkartenhalter und JGA-Anhänger. Bestellt wird über Etsy,
eine eigene Kasse gibt es nicht. Die frühere Anlass- und Ratgeber-Seite ist abgeschaltet, ihre
Adressen leiten auf den Shop. Cozylore unter `cozy/` ist abgekoppelt und bleibt unberührt.

> **Für Mitwirkende & Agenten:** Die verbindlichen Regeln stehen in **[`CLAUDE.md`](CLAUDE.md)**,
> zuerst den Abschnitt „Stand seit 02.11.2026“ lesen.

## Struktur
```
/                     Shop-Startseite (aus dem Generator, siehe CLAUDE.md)
shop/                 Produktseiten (zum Start Platzkartenhalter und JGA-Anhänger)
impressum.html        Impressum
datenschutz.html      Datenschutz
<alter-ordner>/       Weiterleitungen auf den Shop (noindex)
assets/style.css      zentrale Design-Quelle, der Generator bettet sie in die Shop-Seiten ein
assets/fonts/         self-hosted Schriften
cozy/                 Cozylore, abgekoppelt, nicht anfassen
scripts/              Hilfsskripte + check-consistency.sh
.github/workflows/    Automatisierung
```

## Lokal prüfen
```bash
bash scripts/check-consistency.sh   # muss grün sein, bevor du pushst
```

## Konventionen (Kurzfassung)
- Eine zentrale `/assets/style.css`, niemals pro-Ordner-Kopien. Die Shop-Seiten tragen sie
  eingebettet, nach einer Änderung den Generator laufen lassen.
- Titel: `… | BeThatHost`, höchstens 60 Zeichen.
- Branch je Aufgabe, PR statt Direkt-Push, gemergt wird von Hand. Details: `CLAUDE.md`.
