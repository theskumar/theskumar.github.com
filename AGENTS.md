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
- Taxonomy disabled (`disableKinds = ["taxonomy"]`)

## Deploy

Push to `main` → GitHub Actions → `hugo --minify` → GitHub Pages.

## Notes

- Hugo extended required (SCSS)
- Clone with `--recursive` for submodules
- Custom styles: `layouts/partials/style.html`
- Syntax highlighting: `syntax-dark.css`, `syntax-light.css`
