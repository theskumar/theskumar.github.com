# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal website/blog built with Hugo, a static site generator. The site is deployed to GitHub Pages via GitHub Actions on every push to the `main` branch.

## Architecture

### Site Structure

- **hugo.toml**: Main Hugo configuration file defining site metadata, theme, permalinks, and build settings
- **content/**: All site content in Markdown format
  - `_index.md`: Homepage content
  - `now.md`: "Now" page describing current activities
  - `blog/`: Blog posts with front matter (title, date, description, tags)
- **layouts/**: Custom Hugo layout overrides
  - `_default/`: Default page templates
  - `partials/`: Reusable template components (custom footer, favicon, styling, syntax highlighting)
- **themes/**: Hugo themes as git submodules
  - `hugo-bearblog`: Primary theme (active theme)
  - `hugo-admonitions`: Additional theme for content annotations
  - `typo`: Additional theme (untracked)
- **static/**: Static assets served directly (images, files, etc.)
- **public/**: Generated site output (git-ignored, created during build)

### Theme System

The site uses `hugo-bearblog` as the primary theme, installed as a git submodule. Custom layouts in the `layouts/` directory override theme defaults. The theme is minimalist and focused on content with "Bearblog"-like URLs.

### Deployment

Automated deployment via GitHub Actions (.github/workflows/hugo-deploy.yml):
1. Triggers on push to `main` branch
2. Checks out repository with submodules
3. Installs Hugo (latest extended version)
4. Builds site with `hugo --minify`
5. Uploads `public/` directory as GitHub Pages artifact
6. Deploys to GitHub Pages

## Common Commands

### Development Server
```bash
hugo server -D --openBrowser
```
Starts local development server with draft posts enabled and opens browser automatically.

### Build Site
```bash
hugo
```
Generates static site in `public/` directory.

```bash
hugo --minify
```
Production build with minified output (same as CI/CD).

```bash
hugo --cleanDestinationDir
```
Builds site after cleaning the destination directory.

### Content Creation
```bash
hugo new content/blog/my-post.md
```
Creates a new blog post with appropriate front matter.

### Theme Management
```bash
git submodule update --init --recursive
```
Initializes and updates all theme submodules (required after fresh clone).

```bash
git submodule update --remote themes/hugo-bearblog
```
Updates the hugo-bearblog theme to latest version.

## Content Conventions

### Blog Post Front Matter
Blog posts require TOML front matter with:
- `title`: Post title
- `date`: Publication date (format: "YYYY-MM-DD")
- `description`: Post summary for meta tags and listings
- `tags`: Array of topic tags
- `draft`: Optional boolean (exclude from production builds)

### URL Structure
- Blog posts: `/articles/YYYY/MM/slug/`
- Tags: `/articles/slug`
- Taxonomy is disabled (`disableKinds = ["taxonomy"]`)

## Notes

- Hugo version must have extended support (required for SCSS processing)
- Theme is managed as a git submodule; always use `--recursive` when cloning
- Custom styling is in `layouts/partials/style.html`
- Syntax highlighting uses custom CSS (`syntax-dark.css` and `syntax-light.css`)
- The site intentionally disables taxonomy/category pages for simplicity
