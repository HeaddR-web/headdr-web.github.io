# Hosting HQ — umbrella hosting platform · requirements

**Date:** 2026-06-16 · **Status:** brainstorm complete, ready for planning · **Scope:** Deep — product

Output of a `ce-brainstorm` session. Captures WHAT we're building so planning (`ce-plan`) doesn't
have to invent product behaviour. Repo-relative paths throughout.

## Problem / context

`girlsnight/` (Girls Night HQ) proved the model: a glam, single-occasion hosting hub with an
interactive "Build your night" planner + SEO articles + Amazon affiliate + Pinterest. The owner wants
to generalise it into a **multi-occasion hosting platform** so one engine serves many entertaining
niches instead of one. The current "Girls Night" brand can't be the umbrella — it excludes guys'
nights and reads female-only.

## Decision (locked this session)

- **New umbrella brand: "Hosting HQ"** — a portal that sits above many occasion hubs. (Already hinted
  by the existing eyebrow "Hosting HQ · for the girls" in `girlsnight/`.)
- **Homepage = occasion picker.** A new visitor first chooses a hosting occasion, then lands in that
  occasion's full hub (hero + builder + articles), i.e. everything already built for Girls Night.
- **Each occasion is its own hub**, cloned from the proven `girlsnight/` template (own `app.js`
  `CATEGORIES`, own articles, own pins). **Girls Night HQ becomes one hub among many.**
- **Untouched:** root `index.html` (HeaddR Wallpapers) and `/cozy/` (Cozylore). Hosting HQ is additive.

## Users

- **Primary:** someone planning a specific at-home gathering ("spa night for 4", "cocktail night",
  "guys' poker night", "autumn dinner") who wants ideas + a ready-to-shop list fast.
- **Traffic source:** Pinterest (fast) + Google SEO (compounding) — same as Girls Night / Cozylore.

## Proposed occasions (full backlog)

Girls Night ✅ · Guys Night / Party · Spa Night · Cocktail Night · Wine Night · Games Night ·
Seasonal Decor (Autumn / Winter / …) · Valentine's Day. (More occasions can be added later.)

### Product note — overlap risk (raised in brainstorm)

Several occasions overlap heavily — **Cocktail Night, Wine Night, Games Night** are all "evening with
friends" variants and risk thin, cannibalising content. **Girls Night, Guys Night, Spa Night, Seasonal
Decor, Valentine's** are more distinct audiences/intents. Recommendation: treat the distinct ones as
first-class hubs and let drink/game variants be strong *articles/categories within* a hub rather than
8 near-identical sites. → open question Q2.

## Scope

**In scope (v1):**
- New `Hosting HQ` portal page (occasion picker) at a new path (e.g. `host/`), since root is taken.
- Re-home Girls Night HQ as the first hub and link it from the portal.
- Build the next 1–2 occasion hubs from the template to prove "multi-hub".
- Shared visual system (the warm beige hosting theme already in `girlsnight/style.css`).

**Out of scope (now):**
- Custom domain (decide later — Q1).
- A single "universal" builder engine shared across hubs (start by cloning per-hub; refactor to a
  shared engine only once 3+ hubs exist and the pattern is stable).
- Print-on-Demand (parked earlier; revisit once traffic exists).
- Pinterest auto-publish (still blocked on API access; pins keep queuing as today).

## Approach / key decisions

- **Per-hub clone first, shared engine later.** Each hub = a folder like `girlsnight/` with its own
  `index.html`, `app.js` (`CATEGORIES`), `posts/`, `pins/queue.json`. Fastest path; avoids premature
  abstraction. Revisit a shared engine at 3+ hubs.
- **Consistent chrome, per-occasion accent.** All hubs share the beige hosting base theme; each
  occasion may get a subtle accent (e.g. Guys Night cooler/darker) so it's not literally pink for men.
- **Monetisation unchanged:** AdSense (`pub-4473022510510415`), Amazon affiliate (`cozylore-21`),
  Pinterest queue. No new accounts needed to ship.

## Success criteria

- A visitor can land on the Hosting HQ portal, pick an occasion, and reach a complete hub in one click.
- Girls Night HQ works unchanged as a hub under the portal.
- At least one *new* occasion hub is live and structurally identical (builder + ≥3 articles + pins).
- Adding a future occasion is a repeatable, documented step (extend `CONTENT-ENGINE.md`).

## Open questions (for planning / owner)

- **Q1 — Domain:** stay on `headdr-web.github.io/host/…` for now, or buy a custom hosting-brand domain?
- **Q2 — Occasion grouping:** which of the overlapping evening themes (cocktail/wine/games) are
  full hubs vs. articles inside a broader hub? (Resolve before mass-cloning.)
- **Q3 — First wave:** which 1–2 occasions to build right after the portal? Recommendation by leverage:
  **Spa Night** (distinct, evergreen, strong affiliate + Pinterest) and **Cocktail Night** (high
  search/affiliate), with **Valentine's / Seasonal** timed to the calendar.
- **Q4 — Portal vs. rebrand path:** new `host/` folder as portal (keeps `girlsnight/` URLs stable) —
  confirm vs. any preference to restructure existing URLs.

## Handoff

Next step: `ce-plan` to turn this into an implementation plan — portal page + re-home Girls Night +
first new hub — once Q2/Q3 are answered.
