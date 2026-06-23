# Pinterest Auto-Post

Postet automatisch neue Pins von **bethathost.de** auf Pinterest — über die
**offizielle Pinterest-API (v5)**, ausgeführt von **GitHub Actions**.
Kein Browser, kein gespeichertes Passwort, ToS-konform.

## Warum nicht der Selenium-Bot?
Der ursprünglich angefragte `PinterestBulkPostBot` steuert einen echten Chrome
und braucht manuelles Login. Das ist für **unbeaufsichtigte Automatisierung**
ungeeignet (Captchas, Sperr-Risiko durch gespeicherte Sessions). Diese Lösung
nutzt stattdessen die offizielle API.

## Wie es funktioniert
1. `extract_pins.py` liest aus jeder Seite (`config.json` → `pages`) die
   OpenGraph-Daten (Titel, Beschreibung, Bild, Link) und schreibt `pins.json`.
2. `post_pins.py` postet pro Lauf max. `posts_per_run` **neue** Pins und merkt
   sich Gepostetes in `posted.json` (kein Doppelposten).
3. Der Workflow `.github/workflows/pinterest.yml` läuft per Zeitplan (Mo & Do)
   oder manuell und schreibt das Ledger zurück ins Repo.

## Einmalige Einrichtung (einziger manueller Schritt)
1. **Pinterest-App anlegen:** <https://developers.pinterest.com/> → „Connect app".
   App erstellen, Scopes `boards:read`, `pins:read`, `pins:write` aktivieren.
2. **Access-Token erzeugen** (über den OAuth-Flow der App). Es genügt ein Token
   für deinen eigenen Account.
3. **Board anlegen** auf Pinterest mit dem Namen aus `config.json`
   (`"board_name"`), Standard: **„Party & Gastgeben Ideen"**. Namen ggf. anpassen.
4. Im GitHub-Repo unter **Settings → Secrets and variables → Actions**:
   - **Secret** `PINTEREST_ACCESS_TOKEN` = dein Token
   - **Variable** `PINTEREST_LIVE` = `true`  (Schalter: ohne ihn bleibt alles DRY-RUN)

## Erst testen, dann scharf schalten
- **DRY-RUN (Standard):** Solange `PINTEREST_LIVE` ≠ `true` oder kein Token da ist,
  wird **nichts** gepostet — der Lauf zeigt nur, was er tun würde.
- Lokal testen: `python pinterest/extract_pins.py && python pinterest/post_pins.py`
- Live schalten: Variable `PINTEREST_LIVE=true` setzen. Erst dann postet der
  nächste Lauf (Zeitplan oder „Run workflow" im Actions-Tab) echte Pins.

## Einstellungen (`config.json`)
| Feld            | Bedeutung                                                  |
|-----------------|------------------------------------------------------------|
| `base_url`      | Domain der Website                                          |
| `board_name`    | Ziel-Board (per Name; wird automatisch zur ID aufgelöst)   |
| `board_id`      | optional: Board-ID direkt (überschreibt `board_name`)      |
| `posts_per_run` | Pins pro Lauf (klein halten, wirkt natürlicher) — Standard 2|
| `pages`         | Liste der Seiten, aus denen Pins erzeugt werden            |

## Tipp: bessere Pin-Bilder
Pinterest bevorzugt **vertikale 2:3-Bilder**. Aktuell werden die `og:image`
(quer, 3:2) verwendet — funktioniert, ist aber nicht optimal. Auf Wunsch
erzeuge ich pro Seite ein eigenes vertikales Pin-Bild und hänge dessen URL an.
