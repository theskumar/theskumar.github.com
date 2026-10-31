# saurabh-kumar.com

Personal website of [Saurabh Kumar](https://saurabh-kumar.com), built with [Hugo](https://gohugo.io/). It started on the [Bear Blog](https://github.com/janraasch/hugo-bearblog) theme; the templates now live in `layouts/`. Deployed to GitHub Pages.

## Goals

- **Simplicity** — minimal design, no JavaScript bloat
- **Performance** — static HTML, fast everywhere
- **[DRY](http://en.wikipedia.org/wiki/Don't_repeat_yourself)** — don't repeat yourself
- **Adaptability** — easy to tweak and extend

## Getting Started

```bash
git clone git@github.com:theskumar/saurabh-kumar.com.git
cd saurabh-kumar.com

# Run local dev server (with drafts)
hugo server -D --openBrowser
```

> Requires [Hugo](https://gohugo.io/installation/) 0.168.0, the version CI pins.

## Writing a New Post

```bash
hugo new content/blog/my-post.md
```

Front matter uses TOML:

```toml
title = "My Post Title"
date = "2026-05-12"
description = "A short summary"
tags = ["tag1", "tag2"]
draft = false
```

## Deployment

Push to `main` → GitHub Actions builds with `hugo --minify` → published to GitHub Pages.

## Project Guide

See **[AGENTS.md](AGENTS.md)** for the full project structure, conventions, and development reference — useful for both humans and AI coding agents.

## License

Content © Saurabh Kumar. All rights reserved.
