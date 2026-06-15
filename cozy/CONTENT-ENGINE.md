# Cozylore content engine — recurring task spec

This file is the instruction the automation runs **each cycle** to publish a new article
without manual work. It can be driven by the `/loop` skill or a scheduled Claude Code web session.

## The task to run each cycle

> Read `cozy/CONTENT-ENGINE.md` and `cozy/README.md`. Pick the **topmost unpublished topic**
> from the backlog in README.md (one that has no file in `cozy/posts/` yet). Write a complete
> SEO article for it as a new file in `cozy/posts/`, copying the structure of
> `cozy/posts/cozy-bedroom-aesthetic-on-a-budget.html` exactly:
>
> 1. `<title>`, meta description, canonical URL, `Article` JSON-LD (and `FAQPage` JSON-LD if the post has FAQs).
> 2. 900–1500 words of genuinely useful, original content with `<h2>`/`<h3>` structure.
> 3. 1–2 affiliate `.pick` callout boxes with `rel="sponsored nofollow"` and `href="#"` placeholders
>    marked `<!-- AFFILIATE -->`. Never invent fake prices or fake product names.
> 4. One in-article `.ad-slot` div and the `<!-- ADSENSE -->` placeholder in `<head>`.
> 5. A newsletter block with the `<!-- NEWSLETTER -->` placeholder.
> 6. A "Related" line linking 1–2 existing posts, and add reciprocal links from those posts.
> 7. Add a new `.post-card` to the grid in `cozy/index.html` linking the new article.
> 8. Append 4 Pinterest pin ideas (title + description, keyword-rich) for this article to `cozy/PINS.md`.
> 9. Commit with a clear message and push to the working branch. Do not touch the root `index.html`.

## Rules

- One article per cycle. Quality over volume.
- Never fabricate specific product specs, prices, reviews, or statistics.
- Keep affiliate/ad/newsletter spots as placeholders until the owner adds real IDs.
- Keep everything inside `/cozy/`.
- When the backlog is empty, propose 10 new long-tail, affiliate-friendly topics, append them to
  README.md's backlog, then continue.

## Scheduling options (pick one)

- **`/loop` skill** — runs the task on an interval during an active session
  (e.g. `/loop 1d <the task above>`). Simple, but only runs while a session is alive.
- **Scheduled web session / cron trigger** — the durable option: a recurring Claude Code web
  session that runs the task on a schedule with no session kept open. See
  https://code.claude.com/docs/en/claude-code-on-the-web for triggers.

## Cadence

2–3 articles/week is plenty. The goal is a library of 25–30 quality posts in the first few months,
each one also pushed to Pinterest for immediate traffic while Google catches up.
