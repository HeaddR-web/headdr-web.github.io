# Girls Night HQ — girls-night planning site (income engine #2)

> **Stand Juni 2026:** Teil der **Hosting HQ**-Plattform (Portal im Root + Hubs `watchparty/`, `cocktailabend/`).
> Inhalte **auf Deutsch / DACH** (zu `amazon.de`). Builder = **vereinfachte Kategorie-Ansicht mit direkten
> Amazon-Links** (kein Add-to-Liste/Tracker mehr).

A reader-supported content + tool site in the **girls night / party planning** niche. Same money model as
Cozylore, with a warm, elegant **hosting** look — cream & beige, soft terracotta-rose and sand accents, brushed
gold (light theme; the deliberate contrast to Cozylore's calm tone is the warm entertaining vibe, not loudness).
It makes money two ways, with **no store and no products to ship**:

1. **Display ads** (Google AdSense → later Ezoic/Mediavine as traffic grows)
2. **Affiliate links** (Amazon Associates, tag `cozylore-21` — commission when a reader buys)

Traffic comes from **Google SEO** (slow, compounding) **+ Pinterest** (fast — reuses the same publishing engine
as Cozylore; this niche is huge on Pinterest).

It lives entirely in `/girlsnight/` as one hub under the **Hosting HQ** portal (root `index.html`); it does not touch `/cozy/`.

---

## ✨ The hook: the "Build your night" tool

The homepage isn't just a blog — it's an interactive planner (gamified):

- 6 category tiles: **Games, Drinks, Snacks, Deko & Themes, Pamper & Spa, Movie Night**.
- Each tile has curated **+ Add** picks (Amazon affiliate searches).
- A **progress tracker (x/6)** fills as the user plans more categories.
- Everything added lands in **"My Night"** — a shopping list with affiliate links, *Copy list* and *Clear all*.
- 100% static: pure JS + `localStorage`, no backend, no tracking. See `app.js`.

To add/adjust categories or picks, edit the `CATEGORIES` array at the top of `girlsnight/app.js`.

---

## ✅ What YOU need to add (one-time setup)

| # | Account | Why | Cost | Where it plugs in |
|---|---------|-----|------|-------------------|
| 1 | **Amazon Associates** | Commission on linked products | Free | Tag `cozylore-21` is already wired into `app.js` + every `.pick` box. Swap the tag if you want a separate one. |
| 2 | **Google AdSense** | Display ads = passive income | Free | Loader tag already in `<head>` (pub-4473022510510415); the `.ad-slot` divs are where ads show. |
| 3 | **beehiiv** (or MailerLite) | Newsletter list | Free tier | Replace `action="#"` on each `<form>` (search `NEWSLETTER`). |
| 4 | **Pinterest** (already have one!) | Free traffic from day one | Free | Pins auto-publish from `girlsnight/pins/queue.json` via the shared Action. Optional: set a separate board with the `PINTEREST_BOARD_ID_GIRLSNIGHT` secret. |
| 5 | *(later)* **Google Search Console** | See rankings | Free | Verify the domain once. |

---

## 🔌 Exact spots to edit

- **Affiliate tag:** `AFF_TAG` in `app.js`, and `tag=cozylore-21` in the post `.pick` boxes (search `AFFILIATE`).
- **AdSense:** already loaded; ads fill the `.ad-slot` divs once approved.
- **Newsletter:** search `NEWSLETTER` — replace the form `action`.
- **Categories / picks:** the `CATEGORIES` array in `app.js`.

---

## 🔁 How the content engine runs (recurring, see CONTENT-ENGINE.md)

Each cycle: pick the top unpublished topic from the backlog below, write a full SEO article into
`girlsnight/posts/` using an existing post as the template, link it from the homepage guides grid and related
posts, add a pin to `girlsnight/pins/queue.json`, commit & push. Never touch the root `index.html` or `/cozy/`.

---

## 🗂️ Content backlog (next articles)

High-intent, affiliate-friendly, strong Pinterest pull:

- ~~Galentine's Day Party Ideas~~ ✅ published → `posts/girls-night-galentines.html`
- ~~Girls Night In Ideas on a Budget~~ ✅ published → `posts/girls-night-budget.html`
- Bachelorette / Hen Party Night-In Ideas
- 30 Truth or Dare Questions for Girls Night
- Wine & Paint Night at Home
- Best Girls Night Board & Card Games (buyer guide)
- DIY Cocktail Bar Cart Essentials (buyer guide)
- Cosy Autumn Girls Night Ideas
- Y2K / 2000s Throwback Party Theme
- Galentine's Gift Bag / Party Favour Ideas

---

## ⏱️ Honest expectations

- Months 1–3: build the library (15–25 articles), Pinterest brings the first trickle (this niche pins extremely well).
- Months 4–6: Google starts trusting the site; first steady ad + affiliate income. The interactive planner is a
  retention/affiliate-click advantage Cozylore doesn't have.
- Low-touch, not zero-touch: ~1 hour/month from you (payouts, account health, direction).
