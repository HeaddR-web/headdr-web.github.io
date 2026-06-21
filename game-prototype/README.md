# MORPH — Core-Loop-Prototyp 🦎

Ein **Fun-Test-Prototyp** für ein Spiel im Geist von *MECCHA CHAMELEON* —
aber mit unserem Twist: **Du verwandelst dich in Objekte und passt die Tarnung
danach von Hand an.**

Das hier ist bewusst *kein* fertiges Spiel. Es soll genau **eine Frage**
beantworten, bevor wir Geld/Zeit in Multiplayer & Steam stecken:

> Macht der Kern-Loop „verwandeln → anpassen → einfrieren → nicht entdeckt
> werden" allein schon Spaß und erzeugt diese „fast erwischt!"-Momente?

## Starten

1. [Godot 4.3+](https://godotengine.org/download) herunterladen (eine ~70 MB
   Datei, keine Installation nötig).
2. Godot öffnen → **Import** → diesen Ordner (`game-prototype/`) wählen →
   `project.godot` öffnen.
3. **F5** drücken.

> Hinweis: In dieser Cloud-Umgebung lässt sich der Prototyp nicht ausführen
> (keine GPU/kein Godot-Editor), nur lokal. Der Code ist Godot-4-Standard und
> rein prozedural (alles in `Main.gd`), also leicht anzupassen.

## Steuerung

| Taste        | Aktion                                            |
|--------------|---------------------------------------------------|
| Pfeiltasten  | Bewegen                                           |
| **F**        | In nächstes Objekt verwandeln (oder zurück zum Blob) |
| **Q / E**    | Tarnung anpassen (Helligkeit Richtung „passt")    |
| **Leertaste**| Pose einfrieren / lösen                           |
| **Enter**    | Neue Runde (nach Sieg/Niederlage)                 |

## Spielziel

Überlebe **75 Sekunden**, ohne dass der rote Seeker-Bot dich enttarnt.
Der Verdachtsbalken oben rechts steigt, wenn der Seeker dich im Sichtkegel hat
und etwas nicht stimmt:

- **Weißer Blob** im Blickfeld → sofort verdächtig.
- **Bewegung** im Blickfeld → hoher Verdacht.
- **Schlechter Blend** (Tarnung nicht angepasst) → mittlerer Verdacht.
- **Objekt am falschen Ort** (z. B. ein Fass mitten im leeren Raum) → verdächtig.
- **Eingefroren + 100 % Blend + am richtigen Ort** → praktisch unsichtbar,
  übersteht sogar eine Inspektion aus nächster Nähe.

Optimaler Loop: nah an **gleichartige** Objekte → **F** → mit **Q/E** auf 100 % Blend →
rechtzeitig **Leertaste** zum Einfrieren, wenn der Kegel auf dich schwenkt.

### Der Seeker reagiert (v2)

Er patrouilliert nicht mehr stur. Steigt der Verdacht, **dreht er sich zur
verdächtigen Stelle, wird langsamer und starrt** (Status `investigate` → `alert`,
mit `?`/`!` über dem Kopf). Hältst du dann perfekt still und getarnt, sinkt der
Verdacht wieder, er dreht ab — und du bekommst den **„Puh, gerade so..."-Flash**.
Genau dieser Beinahe-erwischt-Moment ist das, was wir testen wollen.

## Was dieser Prototyp bewusst NICHT hat

- Multiplayer / Netcode (kommt erst, wenn der Loop Spaß macht)
- Mehrere Maps, Sound, Art, Animationen
- Seeker-„Anstupsen"/Reveal-Animation, Mass-Budget, Comeback-Mechanik

Das sind die nächsten Ausbaustufen aus dem Brainstorm — siehe Roadmap unten.

## Qualität / Tests

Der Prototyp wurde mit **Godot 4.3 headless** gegengeprüft (kompiliert + rendert
fehlerfrei mit echtem OpenGL-Renderer). Zusätzlich gibt es ein kleines
**Balance-Testharness**, das die Design-Annahmen automatisch verifiziert:

```bash
MORPH_SELFTEST=1 godot --headless --path .
```

Prüft u. a.: Überlebt perfekte Tarnung das Anstarren und eine Nah-Inspektion?
Wird ein laufender Blob zuverlässig enttarnt? Bestraft „Bewegung trotz Tarnung"
und „Objekt am falschen Ort"? Aktuell **6/6 PASS**. Der Test läuft nur mit der
`MORPH_SELFTEST`-Umgebungsvariable, im normalen Spiel ist er inaktiv.

## Warum dieser Twist (Design-Kern)

Reines „in Objekte verwandeln + verstecken" ist **Prop Hunt** (2007) und
existiert tausendfach. MECCHA CHAMELEONs viraler Reiz liegt im **handgemachten,
kreativen Tarnen**. Wir fusionieren beides:

1. **Form-Layer** — in welches Objekt verwandle ich mich (Silhouette muss passen)?
2. **Anpassungs-Layer** — die generische Form an die konkrete Stelle anpassen
   (hier: Helligkeit/Ton; später: Muster, Staub, Kratzer, Neigung).

Zwei Skill-Ebenen = doppelt so viele Beinahe-Enttarnungen = mehr Clip-Momente.

## Roadmap

Erledigt in v2:

- [x] Seeker reagiert auf Verdacht (investigate/alert, dreht sich hin, starrt)
- [x] „Objekt am falschen Ort" wird bestraft (Positions-Skill)
- [x] Perfekte Tarnung übersteht Nah-Inspektion (Fantasie-Fix)
- [x] „Beinahe erwischt"-Feedback (Relief-Flash)
- [x] Automatisiertes Balance-Testharness

Als Nächstes (nach bestandenem Fun-Test):

- [ ] Anpassung ausbauen: Farbe **und** Muster/Textur, nicht nur Helligkeit
- [ ] „Mass-Budget": großes Objekt = besseres Versteck, aber träge/auffällig
- [ ] Seeker-Reveal: Objekte anstupsen → echtes fällt um, du zuckst
- [ ] Multiplayer (Hider vs. Seeker, 2–10), Steam Networking
- [ ] Maps, Art-Pass, Sound, Replay-/Clip-Export für Streamer
