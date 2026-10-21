# agents.md

Hugo static site → GitHub Pages. Theme: `hugo-bearblog` (git submodule).

## Structure

```
hugo.toml          # site config, permalinks, build settings
content/           # markdown content (blog/, _index.md, now.md)
layouts/           # template overrides (_default/, partials/)
themes/            # git submodules (hugo-bearblog, hugo-admonitions, typo)
static/            # images, files
public/            # build output (git-ignored)
data/tags.json     # tag vocabulary (with descriptions), shared by Writing and TIL
scripts/           # check-til.py (CI + pre-commit), til-mastodon.py (CI)
```

## Commands

```bash
hugo server -D --openBrowser   # dev server (drafts enabled)
hugo --minify                  # production build
hugo new content/blog/post.md  # new post
git submodule update --init --recursive  # init themes after clone
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
toot = "..."                         # optional Mastodon short form
mastodon = "117465622405124446"      # set by CI after posting
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

## Naming

- **Writing**: long posts. Section `content/blog/`, URLs `/articles/…`, eyebrow "Writing". Say "post".
- **TIL**: short notes. Section `content/til/`, URLs `/til/…`, page title "Things I Learned". Say "note".
- **Tags**: shared by both, at `/tags/`.

## Deploy

Push to `main` → GitHub Actions (`hugo-deploy.yml`) → `scripts/check-til.py` → `hugo --minify` (Hugo pinned to 0.168.0) → GitHub Pages.

`til-mastodon.yml` runs `scripts/til-mastodon.py` on every note changed by the push: it posts new notes, edits the toot when a posted note's toot text changes, commits the status IDs, then starts `hugo-deploy.yml` again. It needs the `MASTODON_ACCESS_TOKEN` secret. Notes dated more than 14 days back are not posted.

## Notes

- Hugo extended required (SCSS)
- Clone with `--recursive` for submodules
- Custom styles: `layouts/partials/style.html`
- Syntax highlighting: `syntax-dark.css`, `syntax-light.css`
