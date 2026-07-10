# Saurabh Kumar — Brand Guidelines

**Concept: “Systems that hold.”**
The brand borrows the language of engineering drawings — warm paper, warm ink,
hairline rules, monospace annotations, and one ember accent. It should feel like
a well-kept schematic: calm, precise, quietly confident. Never loud, never
decorated for decoration's sake.

Applies to: saurabh-kumar.com, social cards, slides, README headers.

---

## 1. Logo — the node-graph K

A letter **K** drawn as a system diagram: four terminal nodes, three edges, and
an ember junction where the strokes meet. It reads as both a monogram and a
node-and-edge graph.

- Master: `static/images/brand/mark.svg` (ink on transparent)
- Favicon: `static/images/favicon.svg` (mark on paper tile, dark-mode aware)
- Construction: 32×32 grid; strokes 1.8, round caps; terminal nodes r 2.4; junction r 2.9 in ember.

Rules:

- The junction node is **always** ember; terminals always ink (or cream on dark).
- Minimum size 16 px. Below 20 px, drop the wordmark.
- Clear space: one terminal-node diameter on all sides.
- Don't rotate, outline, gradient-fill, or add shadows.

Lockup: mark + wordmark “Saurabh Kumar” in Newsreader 500, mark cap-height
aligned, gap ≈ 0.45× mark width.

## 2. Color

One neutral family (warm), one accent. Nothing else.

| Token | Light | Dark | Use |
|---|---|---|---|
| paper (`--bg`) | `#F7F4ED` | `#171411` | page background |
| surface | `#FCFAF5` | `#1E1B16` | panels, cards, code |
| ink (`--heading`) | `#1D1810` | `#F1EBDD` | display type, strong |
| body (`--text`) | `#3B352A` | `#C9C2B1` | body copy |
| muted | `#7C7462` | `#8F8875` | secondary copy |
| faint | `#A59C87` | `#6A6455` | annotations, ticks |
| **ember** (`--accent`) | `#B4491F` | `#E08B54` | junction node, links hover, active nav, signals, eyebrows |
| hairline | `rgba(30,25,16,.16)` | `rgba(240,232,214,.14)` | rules, panel borders |

Rules: ember is a signal, not a paint — if a screen is >5% ember, it's too much.
Never pure black or pure white. No gradients except ambient washes ≤6% opacity.

## 3. Typography

Three faces, three jobs:

| Face | Role | Notes |
|---|---|---|
| **Newsreader** (variable, opsz) | Display + long-form prose | 500 for display, 400 for prose, italic for ledes/asides |
| **Geist** | UI, short copy | 400/500/600 |
| **Geist Mono** | Annotations, labels, code, dates | 400/500; labels: 0.72–0.78 rem, +0.12–0.14 em tracking, uppercase |

Scale (site): hero `clamp(1.95rem→2.55rem)`; page titles ~2.2–2.5 rem; prose
1.13 rem / 1.75; UI 1.0625 rem / 1.62; annotations 0.72 rem.
Negative tracking on display (−0.02 em), positive on mono labels. Sentence case
everywhere; uppercase is reserved for mono annotations.

## 4. Graphic language

- **Hairline rules** structure everything; borders are 1px, radius ≤4px.
- **Mono annotations**: `01 — open source`, `fig. 01 — request path`. Index in ember, label muted, trailing hairline.
- **Corner ticks** on panels (9px L-marks, top-left + bottom-right), ember on hover.
- **Registration crosshairs** as ornaments, one per page head.
- **Schematics**: node-and-edge / survey-map figures with mono labels remain
  available language for article figures and diagrams.
- **Hills into ocean** (the signature): Saurabh's tattoo — hills transforming
  into ocean waves (his hills, her beaches) — is the site's organic motif.
  Full-bleed hill ridgelines crest against the very top of the browser
  (`#fx-hills`); full-bleed swells lap against the very bottom (`#fx-waves`);
  on the home page a fixed full-viewport field (`#fx-field`) draws ~13 faint
  lines that morph from ridge folds to rollers with scroll — the
  transformation itself. All canvas-drawn in `--faint` ink with paper-fill
  occlusion, one ember walker on the front ridge and one buoy on the swell.
  These must read as drawings, not effects: line alpha ≤0.55 for bands,
  ≤0.08 for the field.
- Blueprint grid (72px) at ≤ 0.3 × hairline opacity, faded with a radial mask; film grain ≤ 3%.

## 5. Motion

Drafting motion: things are *drawn*, not bounced.

- Edges draw on via `stroke-dashoffset`, 1.1s `cubic-bezier(0.6,0,0.3,1)`, staggered ~140ms.
- Content reveals: 14px rise + fade, 0.65s `cubic-bezier(0.16,1,0.3,1)`, 70ms stagger.
- Signals: small ember dots on `offset-path`, 3–7s linear loops.
- Hovers 150–250ms; presses `scale(0.98)`. Page navigation: 0.45s cross-fade (View Transitions).
- Organic canvases (`#fx-hills`, `#fx-waves`, `#fx-field`): simplex-noise (CDN,
  value-noise fallback), 30fps cap, paused offscreen/hidden, theme-aware ink.
- Everything respects `prefers-reduced-motion` — static, fully drawn.

## 6. Voice

Plain, specific, first-person. The judgment is the product; state it.

- Do: “where the connection pool gives out”, “RAG that cites its sources”.
- Don't: elevate, seamless, unleash, passionate, next-gen; exclamation marks; title case in headers.
- Errors are direct and calm: “This page doesn't resolve.”

## 7. Assets

| Asset | Path |
|---|---|
| Mark (SVG master) | `static/images/brand/mark.svg` |
| Favicon (SVG, theme-aware) | `static/images/favicon.svg` |
| Favicon PNGs / ICO / touch icons | `static/favicon-*.png`, `static/favicon.ico`, `static/apple-touch-icon.png`, `static/android-chrome-*.png` |
| Social / OG card (1200×630) | `static/images/og.png` |
| Live design system | `layouts/partials/style.html` (tokens at top) |
| Sibling site: TIL | `~/work/pr/til` (`build-site.js` carries the same tokens, mark, nav line, ridgescape) → saurabh-kumar.com/til/ |

Regenerate icons: `rsvg-convert -w <size> -h <size> static/images/favicon.svg > out.png`;
ICO: `magick favicon-32x32.png favicon-16x16.png favicon.ico`.
