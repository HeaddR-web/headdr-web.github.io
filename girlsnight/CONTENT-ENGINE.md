# Girls Night HQ content engine — recurring task spec

This file is the instruction the automation runs **each cycle** to publish a new article without manual work.
It can be driven by the `/loop` skill or a scheduled Claude Code web session.

## The task to run each cycle

> Read `girlsnight/CONTENT-ENGINE.md` and `girlsnight/README.md`. Pick the **topmost unpublished topic**
> from the backlog in README.md (one that has no file in `girlsnight/posts/` yet). Write a complete
> SEO article for it as a new file in `girlsnight/posts/`, copying the structure of
> `girlsnight/posts/girls-night-games.html` exactly:
>
> 1. `<title>`, meta description, canonical URL, `Article` JSON-LD (and `FAQPage` JSON-LD if the post has FAQs).
> 2. 900–1500 words of genuinely useful, original content with `<h2>`/`<h3>` structure.
> 3. 1–2 affiliate `.pick` callout boxes with `rel="sponsored nofollow"` and the `tag=cozylore-21` Amazon
>    search links, marked `<!-- AFFILIATE -->`. Never invent fake prices or fake product names.
> 4. One in-article `.ad-slot` div (AdSense is already loaded in `<head>`).
> 5. A newsletter block with the `<!-- NEWSLETTER -->` placeholder.
> 6. A "Related" line linking 1–2 existing posts, and add reciprocal links from those posts.
> 7. Add a new `.post-card` to the guides grid in `girlsnight/index.html` linking the new article. If the topic
>    fits a build-your-night category, consider adding a pick to the `CATEGORIES` array in `girlsnight/app.js`.
> 8. Append a pin (title + keyword-rich description + image_url + link, `published: false`) to
>    `girlsnight/pins/queue.json`.
> 9. Commit with a clear message and push to the working branch. Do not touch the root `index.html` or `/cozy/`.

## Rules

- One article per cycle. Quality over volume.
- Never fabricate specific product specs, prices, reviews, or statistics.
- Keep affiliate/ad/newsletter spots as placeholders/searches until the owner adds real product links.
- Keep everything inside `/girlsnight/`.
- Keep the voice fun, warm and encouraging — but useful. Think elegant hosting, not loud nightclub.
- **Pin/article images must be at least 1000px wide.** Generate new ones in the site's warm hosting style
  (prompts: "girls night / hosting … warm beige & cream, soft terracotta-rose and gold accents, elegant,
  cozy chic … no text"). Square 1:1 @ 2k or 2:3 @ 2k both clear Pinterest's 1000px minimum.
- When the backlog is empty, propose 10 new long-tail, affiliate-friendly girls-night topics, append them to
  README.md's backlog, then continue.

## Scheduling options (pick one)

- **`/loop` skill** — runs the task on an interval during an active session (e.g. `/loop 1d <the task above>`).
- **Scheduled web session / cron trigger** — the durable option. See
  https://code.claude.com/docs/en/claude-code-on-the-web for triggers.

## Cadence

2–3 articles/week. Goal: 15–25 quality posts in the first few months, each also pushed to Pinterest for immediate
traffic while Google catches up.
