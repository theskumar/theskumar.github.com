<!--
  Agent handoff + working guide for the saurabh-kumar.com UI.
  Read this BEFORE editing layouts/, CSS, or the homepage structure.
  Brand rules live in docs/brand/BRAND.md — this file is the implementation map.
-->

# Website UI — Working Guide & Handoff

## Overview

Personal site + blog of Saurabh Kumar. Hugo static site, deployed to GitHub Pages
via `.github/workflows/hugo-deploy.yml` on push to `main`.

Identity (2026 rebrand): **“Systems that hold”** — engineering-drawing aesthetic.
Warm paper + warm ink, one ember accent, hairline rules, monospace annotations,
node-and-edge schematics, "drafting" motion (lines draw on, content settles).
Full brand spec: `docs/brand/BRAND.md`. Writing voice: `docs/STYLE-GUIDE.md`.

## Information architecture

- `/` → About/home (`layouts/_default/about.html`, content `content/_index.md`)
  Hero (eyebrow + tagline + lede + animated route-map SVG: contours, dated
  waypoints '12→now, ember ping, compass) then a 6-column “drafting sheet” of
  numbered panels 01–07 (open source, now, recent writing, worked with,
  working together, off the clock — travel/photography on pause, contact
  `#contact`).
- `/til/` → separate repo (`~/work/pr/til`, `build-site.js`) deployed to the
  same domain; carries the same tokens, mark, living nav line, and ridgescape.
- Organic canvases: `#fx-nav` (breathing contour under the nav, replaces the
  static rule when JS runs) and `#fx-ridge` (five-ridge horizon above the
  footer). Module lives in `layouts/partials/custom_body.html`.
- `/articles/` → Writing index (`layouts/_default/writing.html`, content
  `content/articles.md`), grouped by year, entries via
  `layouts/partials/post-entry.html`.
- `/articles/YYYY/MM/slug/` → posts (`layouts/_default/single.html`, type `blog`).
  Serif prose (`content[data-prose]`), italic lede from `description`,
  reading-progress hairline, floating TOC (`layouts/partials/toc.html`).
- `/projects/`, `/now/` → markdown pages; `page-prose` styling turns `###`
  headings into mono annotations and `- [link] - desc` lists into ruled rows.
- 404 → `layouts/404.html` (“node unreachable”).

## Key files

| File | What it is |
|---|---|
| `layouts/partials/style.html` | The whole design system. Tokens (colors/type) at top. |
| `layouts/partials/custom_head.html` | Pre-paint theme boot, fonts (Newsreader var + Geist + Geist Mono), theme-color. |
| `layouts/partials/custom_body.html` | Motion JS: scroll reveal, stagger, schematic draw-on, reading progress. |
| `layouts/partials/header.html` | Node-graph K mark (inline SVG), nav, theme toggle. |
| `layouts/_default/about.html` | Home; contains the hero schematic SVG (fig. 01). |
| `static/images/brand/` + `static/images/favicon.svg` | Brand assets (see BRAND.md §7). |

## Conventions & gotchas

- Body width is `--width` (720px); home overrides via `.page-home { --width: 880px }`.
  `<body>` gets `page-{{ .Type }}` + `page-home` classes from `baseof.html`.
- Light/dark via `light-dark()` + `data-theme` attribute; theme resolved
  pre-paint in `custom_head.html`. Update all three `theme-color` spots if bg changes.
- Cross-document View Transitions are enabled; `.reveal` entrances are disabled
  when arriving via VT (`html.vt-nav`) to avoid double animation.
- All motion respects `prefers-reduced-motion` (static, fully drawn).
- Ember accent is scarce: junction node, active nav, hovers, eyebrows, signals only.
- No new colors, no new fonts, no shadows heavier than the TOC panel's.
- Homepage GitHub stars are fetched at build time (`resources.GetRemote`), with
  a hardcoded fallback in `about.html`.
- Hugo bearblog theme is still the base (submodule); nearly everything visible
  is overridden locally. `hugo server -D` to develop; screenshots may catch
  paused view-transition fades in a background tab — nudge with a scroll first.
