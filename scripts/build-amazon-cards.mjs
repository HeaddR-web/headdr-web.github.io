#!/usr/bin/env node
/**
 * build-amazon-cards.mjs — GERÜST (noch nicht aktiv)
 *
 * Zweck: liest data/produkte.json, holt für jede ASIN echte Produktdaten
 * (Bild, Titel, Preis, Prime) über die offizielle Amazon-API (Creators API /
 * PA-API) und schreibt sie zurück. Läuft NUR im GitHub-Action-Build — die
 * Zugangsdaten kommen aus GitHub Secrets, niemals aus dem Repo.
 *
 * Aktivierung: siehe docs/amazon-produktkarten.md (erst nach den ersten
 * ~3 qualifizierten Verkäufen schaltet Amazon den API-Zugang frei).
 *
 * Bis dahin ist dieses Script ein bewusster No-Op: ohne Credentials bleibt
 * alles beim Fallback (eigenes_bild + suchlink), damit nie etwas bricht.
 */

const ACCESS_KEY = process.env.AMAZON_ACCESS_KEY;
const SECRET_KEY = process.env.AMAZON_SECRET_KEY;
const PARTNER_TAG = process.env.AMAZON_PARTNER_TAG; // "cozylore-21"

if (!ACCESS_KEY || !SECRET_KEY || !PARTNER_TAG) {
  console.log(
    "[build-amazon-cards] Keine Amazon-API-Credentials gesetzt — übersprungen. " +
      "Fallback (eigenes_bild + suchlink) bleibt aktiv. " +
      "Aktivierung: docs/amazon-produktkarten.md"
  );
  process.exit(0);
}

// --- AB HIER: später implementieren, sobald der API-Zugang da ist ---
//
// 1) data/produkte.json lesen
// 2) Für jede produkt[].asin GetItems aufrufen (Resources: Images.Primary.Large,
//    ItemInfo.Title, Offers.Listings.Price, Offers.Listings.DeliveryInfo.IsPrimeEligible)
// 3) Felder titel/preis/bild_api/prime zurückschreiben
// 4) data/produkte.json speichern (der Commit erfolgt im Workflow)
//
// Amazon-Vorgabe: API-Bilder/Preise max. 24 h cachen → Build täglich (Cron).

console.log("[build-amazon-cards] Credentials erkannt — Implementierung folgt bei Aktivierung.");
process.exit(0);
