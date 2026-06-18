# BeThatHost – Inhalte nach Notion importieren

So bringst du den fertigen Plan in Notion – **ohne API-Key, ohne Risiko**.

## content-plan.csv → Notion-Datenbank

1. In Notion eine neue Seite öffnen.
2. `/import` tippen (oder oben links **Import** → **CSV**).
3. Die Datei **`content-plan.csv`** auswählen.
4. Notion erstellt automatisch eine Tabelle/Datenbank mit den Spalten:
   - **Status** (To Do / In Arbeit / Veröffentlicht) – als „Select" umstellen
   - **Hub** (WM-Party, Mädelsabend, …) – als „Select"
   - **Pin-Titel**
   - **Beschreibung** (inkl. Hashtags)
   - **Ziel-Link** (kommt bei Pinterest ins Link-Feld)
   - **Bild-Link** (zum Pin-Bild)
   - **Geplantes Datum** – als „Date" umstellen
5. Optional: Ansicht auf **Board (Kanban)** nach „Status" umstellen → dann kannst du Pins von „To Do" nach „Veröffentlicht" ziehen.

## Workflow „Vorarbeit / Nacharbeit"

- **Ich (vorarbeit):** neue Pins/Artikel-Ideen als weitere Zeilen in die CSV (oder neue CSV) → du importierst sie dazu.
- **Du (nacharbeit):** Pin bei Pinterest hochladen, Datum setzen, Status auf „Veröffentlicht".

> Hinweis: Der API-Key-Weg ist hier bewusst nicht genutzt. Secrets gehören nie in Chats oder ins Repo. Wenn wir Notion später automatisieren wollen, dann nur über einen offiziellen Notion-Connector (OAuth), der außerhalb des Chats eingerichtet wird.
