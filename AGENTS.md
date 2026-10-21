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
scripts/           # til-mastodon.py (run by CI)
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

- Posts: `/articles/YYYY/MM/slug/`
- Tags: `/articles/slug`
- Tag index: `/tags/`. One `tags` taxonomy covers Writing posts and TIL notes; use names from `data/tags.json`
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
- `content/til/weekly/_content.gotmpl` creates a page per week from note filenames, for the feed and old toot links (not in the nav; `/til/weekly/` forwards to the archive). A week ends on the Sunday after the note's date (UTC).
- Redirect stubs for retired URLs (old articles, `/til/tags/*.html`) are static files in `static/til/`.
- Add notes with cowork-kb's `scripts/til_add.py` (the `/til` skill), or by hand with a fresh timestamp.

## Deploy

Push to `main` → GitHub Actions (`hugo-deploy.yml`) → `hugo --minify` → GitHub Pages.

`til-mastodon.yml` posts new note files to Mastodon (`scripts/til-mastodon.py`), edits the toot when a posted note changes, and commits the status IDs. It needs the `MASTODON_ACCESS_TOKEN` secret. Notes dated more than 14 days back are not posted.

## Notes

- Hugo extended required (SCSS)
- Clone with `--recursive` for submodules
- Custom styles: `layouts/partials/style.html`
- Syntax highlighting: `syntax-dark.css`, `syntax-light.css`
