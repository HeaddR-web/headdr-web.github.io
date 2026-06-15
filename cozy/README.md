# Cozylore — cozy-home content site (income engine #1)

A reader-supported content site in the **cozy home / aesthetic** niche. It makes money two ways, with **no store and no products to ship**:

1. **Display ads** (Google AdSense → later Ezoic/Mediavine when traffic grows)
2. **Affiliate links** (Amazon Associates etc. — commission when a reader buys)

Traffic comes from **Google SEO** (slow, compounding) **+ Pinterest** (fast, reuses your existing HeaddR Pinterest engine).

It lives in `/cozy/` so it never touches your live `index.html` (HeaddR Wallpapers).

---

## ✅ What YOU need to add (one-time setup)

These are the things only you can do — they need your identity / payout details. Roughly 1–2 hours total.

| # | Account | Why | Cost | Where it plugs in |
|---|---------|-----|------|-------------------|
| 1 | **Amazon Associates** (affiliate program) | Earn commission on linked products | Free | Replace every `href="#"` inside `.pick` boxes with your tracking link |
| 2 | **Google AdSense** | Display ads = passive income | Free | Paste loader tag where you see `<!-- ADSENSE -->`; needs the site live + some content first |
| 3 | **beehiiv** (or MailerLite) | Newsletter list = owned audience + ad revenue later | Free tier | Replace `action="#"` on the `<form>` with your embed action |
| 4 | **Pinterest** (you already have one!) | Free traffic from day one | Free | Pin each new article via your existing API app |
| 5 | *(later)* **Google Search Console** | See what Google ranks you for | Free | Verify the domain once |

> **Order:** do #1 + #4 now (instant). Do #2 after ~10–15 articles are live (AdSense wants real content before approving). #3 anytime.

---

## 🔌 Exact spots to edit

- **Affiliate links:** search the files for `AFFILIATE` — each marks an `href="#"` to replace.
- **AdSense:** search for `ADSENSE` — paste your script in `<head>`; the `.ad-slot` divs are where ads show.
- **Newsletter:** search for `NEWSLETTER` — replace the form `action`.

That's it. Everything else (writing, structure, SEO) is the engine's job.

---

## 🔁 How the engine runs (my part — recurring, no work for you)

Each cycle I:
1. Pick a target keyword from the backlog below (long-tail, low competition).
2. Write a full SEO article into `cozy/posts/` using the same template as the bedroom post (meta tags, FAQ schema, affiliate `.pick` boxes, ad slots).
3. Add it to the homepage grid + internally link related posts.
4. Draft 3–5 Pinterest pin titles/descriptions so your Pinterest app can push it for instant traffic.
5. Commit & push.

This can run on a schedule via the `/loop` skill or a scheduled web session — so it keeps producing without you.

---

## 🗂️ Content backlog (next articles)

High-intent, affiliate-friendly, strong Pinterest pull:

- The Best Warm-Light Bulbs for a Cozy Glow (buyer guide — high affiliate value)
- Cozy Living Room Ideas for Small Apartments
- 12 Cozy Reading Nook Ideas (any space)
- How to Make Your Apartment Feel Cozy in Winter
- Cozy Desk Setup Ideas That Still Look Tidy
- The Coziest Throw Blankets, Ranked (buyer guide)
- Warm Paint Colors That Make a Room Feel Cozy
- Cozy Bedroom Lighting Ideas (no overhead light)
- How to Style a Cozy Bookshelf
- Cheap Cozy Decor Finds Under €25 (roundup — affiliate-heavy)

---

## ⏱️ Honest expectations

- Months 1–3: build the library (20–30 articles), Pinterest brings the first trickle.
- Months 4–6: Google starts trusting the site; first steady ad + affiliate income, realistically low-to-mid two/three figures per month **if the niche cooperates**. It compounds from there.
- This is low-touch, not zero-touch: ~1 hour/month from you (check payouts, account health, approve direction).
