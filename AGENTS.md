# agents.md

Hugo static site → GitHub Pages. No theme: every template is in `layouts/` (it began as `hugo-bearblog`, removed Oct 2026).

## Structure

```
hugo.toml          # site config, permalinks, build settings
content/           # markdown content (blog/, _index.md, now.md)
layouts/           # template overrides (_default/, partials/)
archetypes/        # front matter for `hugo new content/blog/…`
static/            # images, files
assets/            # social card background and fonts (og/, fonts/)
public/            # build output (git-ignored)
data/tags.json     # tag vocabulary (with descriptions), shared by Writing and TIL
data/projects.toml # the Projects page, by theme
scripts/           # check-til.py, check-tokens.py (CI + pre-commit)
```

## Commands

```bash
hugo server -D --openBrowser   # dev server (drafts enabled)
hugo --minify                  # production build
hugo new content/blog/post.md  # new post
```

## Blog Post Front Matter (TOML)

```toml
title = ""
date = "YYYY-MM-DD"
description = ""
tags = []
draft = false  # optional
```

## URLs

- Home `/` is the Writing index (`content/_index.md`, `layouts/_default/writing.html`); `/articles/` and `/blog/` redirect to it. About is `/about/` (`content/about.md`).
- Posts: `/articles/YYYY/MM/slug/`
- Tags: `/tags/<tag>/`, index `/tags/`. One `tags` taxonomy covers Writing posts and TIL notes; use names from `data/tags.json`. Old tag URLs (`/articles/<tag>/`, `/til/tags/<tag>.html`) are redirects published by `layouts/partials/tags/legacy-redirects.html`
- TIL notes: `/til/<unix-ts>/`. Week pages: `/til/weekly/YYYY-MM-DD.html` (for the feed; old toots link to `#anchor` there)

## TIL

One file per note: `content/til/<unix-ts>.md`, published at `/til/<unix-ts>/`. The timestamp is the permanent ID.

```toml
+++
title = "EmbeddingGemma 2"           # page title only; safe to change
date = 2026-10-19T12:00:00Z          # UTC; must match the filename's timestamp
tags = ["ai", "rag"]                 # from data/tags.json
mastodon = "117465622405124446"      # optional: status ID of a hand-made post; shows a "Discuss" link
anchor = "embeddinggemma-2"          # migrated notes only: keeps old week-page links
+++
Markdown body.
```

- Reader navigation (eyebrow row): Notes `/til/` (full notes, 10 per page) · Archive `/til/archive/` (titles by year) · Tags `/tags/`.
- `layouts/til/single.html` renders a note; `til-home.html` the stream; `til-archive.html` the archive; `til-home.tilrss.xml` the feed at `/til/rss.xml` (one item per week).
- `content/til/weekly/_content.gotmpl` creates a page per week from note filenames, for the feed and old toot links (not in the nav; `/til/weekly/` forwards to the archive). A week ends on the Sunday after the note's date (UTC); the adapter is the only place that computes this and gives each week page `params.notes`.
- Retired URLs redirect through `aliases` in the front matter of the page they now point to (notes, posts, `content/tags/<tag>/_index.md`). Don't add static redirect stubs.
- Newer/older links use `layouts/partials/pager.html` everywhere: newer on the left, older on the right.
- `scripts/check-til.py` enforces the rules above (date = filename, known keys and tags). CI runs it before the build; so does the local pre-commit hook.
- Add notes with cowork-kb's `scripts/til_add.py` (the `/til` skill), or by hand with a fresh timestamp.

## Social cards

Each post and TIL note gets its own 1200×630 card at `<page URL>og.png`, drawn by Hugo at build time. `layouts/partials/og/card.html` draws the eyebrow, title and tags on `assets/og/background.png`. `layouts/partials/_funcs/get-page-images.html` (a copy of Hugo's embedded one, plus one block) feeds the card to Hugo's OG and Twitter templates. Other pages use `static/images/og.png`. To use a hand-made image, set `images = ["/images/x.png"]` in front matter.

## Markdown copies and llms.txt

Every regular page (posts, TIL notes, About, Now, Projects) also renders `<page URL>index.md`: output format `markdown` in `hugo.toml`, template `layouts/_default/single.markdown.md`. The copy is the page's source with shortcodes rendered and site-relative links made absolute, under a short header.

- `custom_head.html` links it with `rel="alternate" type="text/markdown"`.
- `layouts/partials/page-markdown.html` draws the "Markdown Copy · View" row on posts, notes and prose pages. The Copy script is in `custom_body.html`.
- `/llms.txt` (`layouts/index.llms.txt`, output format `llms`) lists About, Projects, Now, every post and every note, pointing at the Markdown copies.
- Week pages set `outputs` to HTML only in the content adapter.

## Projects page

`content/projects.md` holds only the title, lede and intro. The projects live in `data/projects.toml`, grouped by theme; `layouts/_default/projects.html` renders them and `layouts/partials/projects-markdown.md` writes the same list into `/projects/index.md`.

- Themes, and the projects inside each theme, render in file order. Put ongoing work first.
- Each project: `one` (what it is), optional `short` (about 12 words, shown muted), `role`, optional `outcome` (shown in the accent).
- `detail` keeps the long story. The page does not show it; it is there for project pages later. Update it when a project changes.

## Naming

- **Writing**: long posts. Section `content/blog/`, URLs `/articles/…`, eyebrow "Writing". Say "post".
- **TIL**: short notes. Section `content/til/`, URLs `/til/…`, page title "Things I Learned". Say "note".
- **Tags**: shared by both, at `/tags/`.

## Deploy

Push to `main` → GitHub Actions (`hugo-deploy.yml`) → `scripts/check-til.py` → `scripts/check-tokens.py` → `hugo --minify` (Hugo pinned to 0.168.0) → GitHub Pages.

Nothing posts to social media automatically. Saurabh posts by hand (X, Mastodon, LinkedIn). To link a note to its Mastodon thread, set `mastodon` to the status ID in the note's front matter.

## Notes

- Custom styles: `layouts/partials/style.html`. Sizes, colors, line heights and tracking come from the tokens in its `:root`; `docs/brand/design-tokens.md` documents them and its rules (serif for display only, one body style). `scripts/check-tokens.py` (CI and pre-commit) fails when the two disagree or a component sets a literal font size.
- Syntax highlighting: `syntax-dark.css`, `syntax-light.css`
- `.pi/design/` is a copy of the tokens for Pi Pocket's Design canvas (DTCG tokens, a dark mode, component specimens). `style.html` stays the source of truth: when a token changes there, update it with Pi Pocket's `design_system` tool too. `dist/` is generated and git-ignored.
