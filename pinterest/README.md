# Pinterest — drei Wege, Pins zu posten

Drei parallele Wege, denselben kuratierten Content (`*/pins/queue.json`,
`pinterest/pins.json`) auf Pinterest zu bringen. Alle drei sind ToS-konform —
kein Browser, kein gespeichertes Passwort, kein Selenium.

## Weg 1 — RSS-Auto-Publish (Fallback, kein API-Token nötig)
Pinterest kann selbst einen RSS-Feed abonnieren und daraus automatisch Pins
erstellen — ganz ohne Entwickler-App, ohne OAuth, ohne Secrets.

1. `scripts/make_feed.py` liest `pinterest/pins.json` (Cover-Pin je Seite) und
   alle `*/pins/queue.json` (kuratierte Kategorie-Pins mit Hashtags) und
   schreibt `feed.xml` im Repo-Root (RSS 2.0).
2. `.github/workflows/feed.yml` hält `feed.xml` automatisch aktuell — bei jedem
   Push, der Seiten/Sitemap/Queues ändert, plus täglich als Sicherheitsnetz.
3. Einmalig bei Pinterest verknüpfen (Desktop, Business-Konto mit verifizierter
   Domain nötig — haben wir bereits):
   Einstellungen → **Mehrere Pins gleichzeitig erstellen** → **Automatisch
   veröffentlichen** → **RSS-Feed verknüpfen** → `https://bethathost.de/feed.xml`
   einfügen → Ziel-Pinnwand wählen → Speichern.
4. Danach übernimmt Pinterest selbst: neue/aktualisierte Feed-Einträge werden
   **innerhalb von 24 Stunden** zu Pins (ältester Inhalt zuerst, max. 200/Tag).

Details: <https://help.pinterest.com/de/business/article/auto-publish-pins-from-your-rss-feed>

**Stand 09/2026:** Dieser Weg hat für dieses Konto nie einen Pin erzeugt, obwohl `feed.xml`
valides RSS ist (W3C-Validator: 0 Fehler), alle Bild-URLs mit HTTP 200 antworten und die Domain
verifiziert ist. Warum, ließ sich von außen nicht klären — Pinterest legt keine Fetch-Logs offen.
Seit die Entwickler-App freigeschaltet ist, ist **Weg 2 (API) der Hauptweg**; der Feed bleibt
bestehen, sollte aber nicht gleichzeitig mit Weg 2 auf dieselbe Pinnwand verknüpft sein, sonst
entstehen Duplikate.

**Achtung Duplikate:** Wenn Inhalte aus `feed.xml` bereits einmal manuell per
Bulk-CSV (Weg 3) hochgeladen wurden, erstellt Pinterest beim Verknüpfen des
Feeds trotzdem neue Pins dafür — es gibt keine automatische Dopplungs-Prüfung
zwischen den drei Wegen. Vor dem Verknüpfen im Notion-Tracker prüfen, was schon
„Hochgeladen" ist, und diese Einträge ggf. vorübergehend aus den Queues nehmen.

## Weg 2 — Live-API-Posten (aktiv, Entwickler-App ist freigeschaltet)
`scripts/pinterest_publish.py` postet die naechsten offenen Pins aus allen
`*/pins/queue.json` (ausser `cozy/`) ueber die offizielle Pinterest-API v5,
markiert sie als `"published": true` und schreibt die `pin_id` dazu — dadurch
wird nichts doppelt gepostet. `.github/workflows/pinterest-publish.yml` laeuft
2×/Tag (09:00 & 17:00 UTC, je 5 Pins) oder manuell und committet die
aktualisierten Queues zurueck.

### Einrichtung (einmalig)

Es braucht am Ende drei Repo-Secrets: `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`
und `PINTEREST_REFRESH_TOKEN`. Die ersten beiden stehen im Developer-Portal, der
Refresh-Token entsteht erst durch eine einmalige OAuth-Autorisierung. Dafuer gibt
es zwei Wege — Variante A braucht keinerlei Terminal.

#### Variante A — ohne Terminal, komplett in GitHub Actions
1. **Redirect-URI eintragen.** Unter <https://developers.pinterest.com/apps/> in
   der App `https://www.bethathost.de/` als Redirect-URI hinterlegen — exakt,
   **mit `www`** und mit abschliessendem Schraegstrich. Pinterest vergleicht
   zeichengenau und weist jede Abweichung mit „400 — Der angegebene
   Weiterleitungs-URI stimmt nicht mit dem registrierten URI ueberein" ab
   (genau daran ist der Login am 14.09.2026 gescheitert: registriert war die
   www-Form, der Workflow schickte die ohne). GitHub Pages leitet www per 301
   auf die Hauptdomain um und behaelt den Query-String — der `?code=…` landet
   also sichtbar in der Adresszeile. Der Wert im Feld `redirect_uri` muss in
   Schritt 1 und Schritt 2 **identisch** sein, sonst scheitert der Tausch und
   der Code ist verbraucht. Die Startseite laedt dabei ganz normal —
   GitHub Pages ignoriert den angehaengten `?code=…` genau wie die `?pin=…`
   Parameter der Pins.
2. **Zwei Secrets anlegen** (Settings → Secrets and variables → Actions):
   - `PINTEREST_APP_SECRET` — das App-Secret.
   - `GH_SECRETS_PAT` — ein Fine-grained Personal Access Token auf *dieses*
     Repo mit der Berechtigung **Secrets: Read and write**. Nur dafuer da:
     Secrets schreiben kann das eingebaute `GITHUB_TOKEN` nicht.
3. **Actions → *Pinterest OAuth einrichten* → Run workflow**, Schritt
   `1-login-url`, App-ID ins Feld. Das Log gibt eine Pinterest-Login-URL aus.
4. URL oeffnen, App autorisieren. Pinterest leitet auf die Startseite weiter;
   in der Adresszeile steht `https://bethathost.de/?code=…&state=…`. Den Wert
   hinter `code=` bis zum `&` kopieren.
5. Denselben Workflow nochmal starten, Schritt `2-code-eintauschen`, Code
   einfuegen. Er tauscht den Code, schreibt `PINTEREST_REFRESH_TOKEN` und
   `PINTEREST_APP_ID` per API als Secrets und listet zur Kontrolle alle Boards
   des Kontos mit ID auf. Der Token wird nie ins Log geschrieben.

   Der `code` ist nur wenige Minuten gueltig. Kommt „Antwort enthaelt keinen
   refresh_token", ist er abgelaufen oder schon benutzt — einfach Schritt 3
   wiederholen.

Die App-ID ist bewusst ein Eingabefeld und kein Secret: sie ist die
oeffentliche Client-Kennung, und Actions maskiert Secret-Werte im Log — die
Login-URL waere sonst unbrauchbar.

#### Variante B — lokal im Terminal
Setzt Python und einen Klon des Repos auf dem eigenen Rechner voraus.
1. In der App `http://localhost:8085/callback` als Redirect-URI hinterlegen.
2. `python3 scripts/pinterest_oauth.py --app-id <APP-ID>` — das App-Secret wird
   verdeckt abgefragt. Das Skript startet einen kleinen Server auf
   `localhost:8085`, gibt die Login-URL aus, faengt die Weiterleitung ab und
   tauscht den Code gegen den Refresh-Token.
   Ohne lokalen Browser: `--no-server`, URL manuell oeffnen, `code`-Parameter
   aus der Redirect-URL mit `--code <CODE>` uebergeben.
3. Die drei Secrets von Hand unter Settings → Secrets and variables → Actions
   anlegen.

Wie lange der Refresh-Token gilt, sagt Pinterest beim Tausch selbst — der
Workflow gibt es am Ende aus (bei unserer App **rund 60 Tage**, Stand 09/2026,
nicht das oft genannte Jahr). Laeuft er ab, schlaegt der Publish-Lauf mit
„Token-Austausch fehlgeschlagen" fehl; dann einfach Schritt 1 + 2 der
Variante A wiederholen. Der Token gehoert **nie** ins Repo und nie in Chats
oder Issues.

#### Rechte (Scopes) — `boards:write` ist Pflicht
Die Login-URL fordert genau vier Rechte an:
`boards:read,boards:write,pins:read,pins:write` (Konstante `SCOPES` in
`scripts/pinterest_oauth_ci.py` und `scripts/pinterest_oauth.py`).

**`boards:write` sieht ueberfluessig aus, ist es aber nicht:** Pinterest
verlangt es fuer `POST /v5/pins`, obwohl dabei kein Board veraendert wird. Ein
Token ohne dieses Recht laesst sich anstandslos erzeugen, liest Boards und
Pins — und scheitert dann bei *jedem* Pin mit
`HTTP 401 – Missing: ['boards:write']`. Genau das ist am 13.09.2026 passiert:
70 offene Pins, 70 Fehler, kein einziger gepostet.

Deshalb prueft der Tausch-Schritt jetzt selbst nach, welche Rechte Pinterest
tatsaechlich erteilt hat (Feld `scope` in der Token-Antwort). Fehlt eines,
bricht Variante A ab und schreibt **kein** Secret — der bisherige Token bleibt
unangetastet —, und Variante B warnt im Terminal. Beim Pinterest-Login also
alle Haken stehen lassen.

Ein Token, der vor dem 13.09.2026 erzeugt wurde, hat `boards:write` nicht und
muss ueber Schritt 1 + 2 der Variante A neu geholt werden.

#### Danach: pruefen, bevor irgendetwas rausgeht
Actions → *Pinterest auto-publish* → *Run workflow* → Modus **`doctor`**. Der
Lauf holt einen Token, listet alle Boards des Kontos und zeigt pro Hub, wie
viele Pins offen sind und auf welchem Board sie landen wuerden — ohne einen
einzigen Pin zu posten. Danach Modus **`check-duplicates`** (siehe unten) und
erst dann **`dry-run`** fuer die konkrete naechste Charge.

### Board-Zuordnung
`pinterest/boards.json` enthaelt Board-**Namen**, keine IDs — das Skript loest
sie beim Lauf ueber die API auf. Es braucht also kein Secret pro Hub.
```json
{ "default": "Party & Gastgeben Ideen", "sites": { "girlsnight": "Mädelsabend" } }
```
`sites` ordnet einzelnen Repo-Ordnern ein abweichendes Board zu, alles Uebrige
geht auf `default`. Die exakten Namen liefert der Workflow-Modus
`list-boards`. Reihenfolge der Aufloesung: `board_id` am Pin →
`PINTEREST_BOARD_ID_<SITE>` → `boards.json` → `PINTEREST_BOARD_ID`.

### Achtung: Queues zuerst mit dem Ist-Stand abgleichen
Die Queue-Dateien sind die einzige Doppelpost-Sperre der API — was dort auf
`"published": false` steht, wird gepostet. Pins, die schon ueber Weg 1 (RSS)
oder Weg 3 (Bulk-CSV) auf Pinterest gelandet sind, stehen dort aber weiterhin
auf `false` und wuerden ein zweites Mal angelegt.

Vor dem ersten scharfen Lauf deshalb **nicht raten, sondern messen**: Modus
**`check-duplicates`** liest die Pins der Ziel-Boards ueber die API und
vergleicht sie mit den offenen Queue-Eintraegen (Ziel-URL ohne Fragment, sonst
Titel). Er postet und aendert nichts, sondern sagt pro Eintrag `neu` oder
`DOPPELT`.

- Alles `DOPPELT` → Modus **`mark-published-only`** ausfuehren: hakt alle
  offenen Pins ab, **ohne** zu posten, und committet die Queues zurueck.
- Alles `neu` → `publish` ist gefahrlos.
- Gemischt → die als `DOPPELT` gemeldeten Eintraege in den `queue.json` von
  Hand auf `"published": true` setzen, dann `publish`.

### Wann der Lauf rot wird
- **Fehlende Secrets** → gruener Lauf mit Meldung im Log. Keine Fehler-Mail,
  bevor die Einrichtung ueberhaupt begonnen hat.
- **Einzelne Pins scheitern, andere gehen durch** → gruener Lauf mit Hinweis.
  Die gescheiterten bleiben offen und kommen beim naechsten Lauf erneut dran.
- **Kein einziger Pin kommt durch** → **Exit 1, roter Lauf.** Das ist nie ein
  Zufall, sondern Token, Scope oder Board. Frueher lief genau dieser Fall
  gruen durch und waere wochenlang nicht aufgefallen.

Ausserdem bricht der Lauf nach drei Fehlschlaegen ohne einen einzigen Erfolg
ab, und `MAX_PER_RUN` begrenzt **Versuche**, nicht Erfolge — ein kaputter Token
kostet damit 5 API-Calls pro Lauf statt einmal quer durch die ganze Queue.
Erste Anlaufstelle bei Rot: Modus `doctor`.

Die Queues werden auch bei einem roten Lauf zurueckcommittet (`if: always()` im
Workflow): was gepostet wurde, **muss** abgehakt sein, sonst legt der naechste
Lauf dieselben Pins ein zweites Mal an.

## Weg 3 — Einmaliger Bulk-Upload (manuell, für Nachzügler)
`pinterest/make_bulk_csv.py` erzeugt `pinterest_bulk.csv` im Format von
Pinterests **„Bulk-Pins erstellen"**-Import (Pinterest Business → Erstellen →
„Bulk create Pins"). Spalten **wörtlich englisch** halten — `Title, Media URL,
Pinterest board, Thumbnail, Description, Link, Publish date, Keywords` — auch
bei deutschsprachigem Konto (getestet: deutsche Spaltennamen wie „Medien-URL"
führen zu „Fehlende Media-URL" für jede Zeile).

## Inhaltlicher Tracker
Single Source of Truth für den redaktionellen Stand: Notion-DB
**„📌 Pinterest Pins"** (Status `Offen`/`Hochgeladen`/`Geplant`). Neue Pin-Ideen
dort anlegen, dann `*/pins/queue.json` entsprechend ergänzen.

## Pflicht: eindeutige Ziel-URL für jeden Pin
Jeder Pin braucht eine **serverseitig eindeutige** `link`-URL. Ein `#anker` genügt **nicht**:
URL-Fragmente werden vom Browser nie an den Server geschickt, d. h. Pinterests Crawler sieht bei
`/casino/#cat-pokerset` und `/casino/#cat-drinks` exakt dieselbe URL `/casino/` — und verwirft die
zusätzlichen Pins still als Duplikate.

**Richtig:** zusätzlich einen Query-Parameter setzen, der tatsächlich übertragen wird:
```
https://bethathost.de/casino/?pin=pokerset#cat-pokerset
```
Die Seite lädt identisch (GitHub Pages ignoriert unbekannte Query-Parameter), der Anker scrollt
weiterhin zum richtigen Abschnitt, und das `<link rel="canonical">` jeder Seite verhindert
Duplicate-Content-Probleme bei Google.

**Historie:** Im Juli 2026 kamen ~70 neue Pins nie bei Pinterest an, weil 106 Feed-Einträge
serverseitig auf nur 37 URLs zeigten. Der Feed selbst war die ganze Zeit valides RSS
(W3C-Validator: 0 Fehler) — die Ursache war ausschließlich die fehlende URL-Eindeutigkeit.

## Pflicht: Bildformat für jeden neuen Pin
**Jedes neue Pin-Bild MUSS vertikal im Seitenverhältnis 2:3 sein** (z. B.
848×1264 oder 1000×1500). Das ist das von Pinterest empfohlene Format und wird
im Feed/Algorithmus bevorzugt ausgespielt — kein Ausnahmefall, keine
Wiederverwendung von Quer-Bildern (og:image, Hero-Bilder, 3:2/16:9 o. ä.).

Bei Bildgenerierung (z. B. Higgsfield `generate_image`): immer explizit
`aspect_ratio: "2:3"` setzen. Bereits bestehende Quer-Bilder in `pins.json`
(die ursprünglichen 15 Cover-Pins) sind historisch bedingt noch 3:2 — bei
Gelegenheit durch neue 2:3-Versionen ersetzen, aber **kein neuer Pin darf
mehr mit Querformat angelegt werden.**
