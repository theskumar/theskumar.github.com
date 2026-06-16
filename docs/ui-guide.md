<!--
  Agent handoff + working guide for the saurabh-kumar.com UI.
  Read this BEFORE editing layouts/, CSS, or the homepage/about structure.
  Sections are wrapped in XML tags for quick targeting.
-->

# Website UI — Working Guide & Handoff

<overview>
Personal site + blog of Saurabh Kumar. Hugo static site, deployed to GitHub Pages
via `.github/workflows/hugo-deploy.yml` on push to `main`.

Brand: a senior backend/systems engineer who writes (author of `python-dotenv`,
8.6k★). Voice and visual design are **editorial minimalism**: warm monochrome,
serif display type, generous whitespace, flat 1px-bordered cards, color used
sparingly, subtle/procedural motion. No SaaS gloss, no heavy shadows, no gradients
as decoration, no emoji in chrome.

Information architecture (current):
- `/` → the Writing index (blog landing). Layout: `layouts/_default/home.html`.
- `/about/` → hero + bento intro + generative canvas. Layout: `layouts/_default/about.html`.
- `/projects/`, `/now/` → standalone pages via `layouts/_default/single.html`.
- `/articles/:year/:month/:slug/` → blog posts (permalink set in `hugo.toml`).
- `/blog/` → 301-style alias redirect to `/`.
</overview>

<stack>
- Hugo (extended) v0.161+. Theme: `hugo-bearblog` git submodule, but **nearly every
  layout is overridden** in the project's own `layouts/`. Hugo prefers project
  `layouts/` over the theme, so edit there — do not touch `themes/`.
- No Node build, no Tailwind, no SCSS pipeline. **All CSS is hand-written and inlined**
  into `<head>` via `layouts/partials/style.html`. Syntax highlighting CSS is in
  `layouts/partials/syntax.css` (a local override, injected by `style.html`).
- Fonts: Google Fonts — Newsreader (serif/display), Geist (sans/UI), Geist Mono.
- Content in Markdown under `content/`. Config in `hugo.toml` (TOML).
</stack>

<file_map>
Edit these; ignore `themes/`.

| File | Responsibility |
|------|----------------|
| `layouts/_default/baseof.html` | Page shell. `<head>`, `<header>`, `<main>`, `<footer class="site-footer">`, body partials. |
| `layouts/partials/style.html` | **The entire stylesheet** (design tokens + all component CSS). |
| `layouts/partials/syntax.css` | Chroma code-highlight theme (emacs light / catppuccin-frappe dark) via `light-dark()`. |
| `layouts/partials/custom_head.html` | Pre-paint theme init + `js` class + font `<link>`s. Runs in `<head>`. |
| `layouts/partials/custom_body.html` | IntersectionObserver scroll-reveal + generative dot-wave canvas. Runs end of `<body>`. |
| `layouts/partials/header.html` | Brand wordmark, nav (with active state), theme-toggle button + click handler. |
| `layouts/partials/footer.html` | Footer line + links. |
| `layouts/partials/post-entry.html` | **Shared** blog-index `<li class="entry">`. Used by home + list. |
| `layouts/partials/toc.html`, `toc-nodes.html` | Notion-style floating TOC (≥4 headings, ≥1080px). |
| `layouts/_default/home.html` | Writing index (landing). Ranges blog posts via `post-entry`. |
| `layouts/_default/about.html` | Hero + bento + `#fx-hero` canvas + `#contact`. Driven by `content/about.md` params. |
| `layouts/_default/list.html` | Section/taxonomy list (tags). Reuses `post-entry`. |
| `layouts/_default/single.html` | Blog post (editorial header) + standalone pages (plain content). |
| `hugo.toml` | Site config, menus, permalinks, params. |
| `content/_index.md` | Home masthead text + `aliases = ["/blog/"]`. |
| `content/about.md` | `layout = "about"` + `params.eyebrow` + `params.tagline` + bio prose. |
| `content/blog/_index.md` | `build.render/list = "never"` so `/blog/` doesn't render (alias wins). |
</file_map>

<design_system>
All tokens are CSS custom properties in `:root` in `style.html`, themed with the
CSS `light-dark()` function. `data-theme` (`light`/`dark`) on `<html>` selects the
scheme; it is always set explicitly (see <lessons>).

Color (light → dark):
- `--bg` #FBFBFA → #1A1917 (warm bone → warm charcoal; NOT pure white/black)
- `--surface` #FFF → #221F1C, `--surface-2` #F9F9F8 → #262320
- `--border` #EAEAEA → rgba(255,255,255,.09), `--border-strong` …
- `--heading` #1A1A1A → #F3F1EC, `--text` #2F3437 → #CFCDC7, `--muted` #787774 → #918E87
- `--accent` #9A3B2E (warm clay) → #E0876A. Used sparingly: link hover, eyebrow, active marks.
- `--code-bg` #F4F3F1 → #242220, `--code-color`, `--tag-bg`, `--tag-text`.

Type:
- `--font-serif` Newsreader — display/hero/post titles, weight 400, tight tracking (-0.025em).
- `--font-sans` Geist — body/UI, base `--font-scale` 1.0625rem, line-height 1.65.
- `--font-mono` Geist Mono — `time`, `.eyebrow`, `.card-label`, code, kbd.

Components (class → intent):
- `.bento` 6-col grid + `.card` (1px border, 12px radius, hover lifts to a faint shadow).
  `.col-2/3/4/6` spans; collapses to 2-col ≤720px.
- `.btn-primary` (solid `--heading`), `.btn-ghost` (outline). `scale(0.98)` on `:active`.
- `.entry` / `.entry-title` (serif) / `.entry-meta` (mono) / `.entry-desc` — the writing index row.
- `.eyebrow` mono uppercase accent kicker; `.card-label` faint mono label.
- `kbd`, tag pills (`.article-tags a`), `.chip`.
- Floating TOC: `.toc-float` (dash rail → text panel on hover/focus).

Generative graphics / motion (all `prefers-reduced-motion`-guarded):
- `#fx-hero` canvas (`custom_body.html`): procedural sine dot-wave behind the About hero.
  Theme-aware (reads canvas `color`), DPR-capped(2), density-capped(700), paused offscreen/hidden.
- `body::after`: static SVG `feTurbulence` film grain (opacity .03 light / .016 dark).
- `body::before`: slow translate-only radial light drift.
- `.reveal` + IntersectionObserver: fade/translate-in on scroll (staggered via `--index`).
- Cross-document View Transitions: `@view-transition { navigation: auto }` — uniform root cross-fade.
- Theme switch: `.theme-anim` class on `<html>` enables a 0.45s color cross-fade for the toggle window only.
</design_system>

<run_and_test>
Dev server (render to memory so cleanup can't break it — see lessons):
```
hugo server --bind 0.0.0.0 --baseURL "http://<host>" --port 1313 --disableFastRender --renderToMemory
```
For phone testing over Tailscale, set `--baseURL` to the tailnet hostname (Hugo appends the port).
Always `http://` (no TLS on the dev server). Tailnet IP works as a MagicDNS fallback.

Production build check:
```
hugo --gc --minify --logLevel warn
```
(Pre-existing, expected warning only: deprecated `languageCode` config key. Leave it.)

Visual + runtime verification (no browser MCP available; use headless Chrome):
- Screenshot: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu
  --hide-scrollbars --window-size=W,H --screenshot=/tmp/x.png --virtual-time-budget=3500 <url>`
  then Read the PNG. `--force-device-scale-factor=2` to inspect fine detail.
- Force color scheme reliably with CDP `Emulation.setEmulatedMedia` (the `--blink-settings=preferredColorScheme`
  flag is unreliable). Headless defaults to dark.
- Runtime assertions (computed styles, toggle behavior, canvas pixels, VT support): drive Chrome with
  `--remote-debugging-port` and a small Node script over the CDP WebSocket (`Runtime.evaluate`). See
  `<verification_recipes>`.
</run_and_test>

<verification_recipes>
Patterns proven useful this session (Node 24 has built-in WebSocket/fetch):
- Theme toggle correctness: emulate `prefers-color-scheme: dark`, read `data-theme` + `body` bg,
  `document.getElementById('theme-toggle').click()`, re-read. Light bg must be `rgb(251,251,250)`,
  dark `rgb(26,25,23)` — and clicking to light must produce the light bg even while OS is dark.
- Canvas: read `document.getElementById('fx-hero').getContext('2d').fillStyle` (must be the theme accent,
  not black) and count painted pixels; checksum two frames to confirm animation advances.
- View transitions: `'CSSViewTransitionRule' in window` and confirm the `@view-transition` rule parses
  (`[...document.styleSheets]…r.constructor.name==='CSSViewTransitionRule'`).
- Counting rendered entries: grep `class="entry"` (the attribute), NOT `entry-title` — the latter also
  appears as a CSS selector in the inlined stylesheet and inflates the count.
</verification_recipes>

<lessons>
Hard-won, ranked by how easily they bite again. Honor these.

1. **`light-dark()` is color-only.** Using it for a numeric property (e.g. `opacity: light-dark(.03,.016)`)
   is invalid, silently dropped → the property falls back (opacity → 1). This shipped a full-strength
   grain that washed dark mode to taupe. For non-color theme values use explicit
   `html[data-theme="dark"] …` overrides.

2. **Set the theme in `<head>` before first paint.** Theme init lives in `custom_head.html`, not in the
   body. Drive the toggle icon purely from CSS (`[data-theme] .sun-icon/.moon-icon`), never via JS
   `style.display` on `DOMContentLoaded` — that flashed both icons on every load.

3. **Toggle sets an explicit `data-theme`; never `removeAttribute`.** With `color-scheme: light dark`,
   removing the attribute means "follow OS", so switching to light while the OS is dark does nothing.
   Resolve to `'light'`/`'dark'` and always set it.

4. **Assigning `canvas.width`/`height` resets ALL 2D context state** (fillStyle, transform, alpha).
   Re-apply `fillStyle` (and `setTransform`) after every resize/layout, or dots render black.

5. **Hugo build options key is `build`, not `_build`** (renamed/removed in 0.145). And front-matter
   build-option changes need a **server restart** to take effect.

6. **Don't `rm -rf public/` while `hugo server` runs rendering to disk** — it serves those files and you
   get 404s. Start the server with `--renderToMemory`.

7. **View Transitions.** `@view-transition { navigation: auto }` enables cross-document transitions
   (progressive enhancement; no-op where unsupported). Two traps:
   - Naming a single persistent element (we tried `view-transition-name: site-header`) makes the
     transition read **differently across pages of different heights**. Prefer a uniform root cross-fade
     unless every page shares geometry.
   - Easing: `cubic-bezier(0.16,1,0.3,1)` is ease-*out* (fast start) and felt abrupt. Use ease-in-out
     (`cubic-bezier(0.4,0,0.2,1)`) with explicit overlapping fade-in/out keyframes.

8. **`getComputedStyle` on a custom property returns the unresolved `light-dark(...)` string**, not an
   rgb. To read a theme-resolved color in JS, read a real property — the canvas uses its own `color`
   (set in CSS) and JS reads `getComputedStyle(canvas).color`. Also: custom-property declarations are
   only valid inside a selector; a floating `--x: …` in the stylesheet body is invalid and dropped.

9. **Renaming a CSS var? Grep every file, including `syntax.css`.** Renaming `--code-background-color`
   → `--code-bg` orphaned a reference in `syntax.css` (a separate file), silently breaking code-block
   backgrounds.

10. **Performance: animate `transform`/`opacity` only.** `scale()` in a keyframe forces per-frame
    rasterization of a `fixed` gradient — use translate-only. The global theme cross-fade transitions
    **only paint-only color props** (`background-color,color,border-color`); adding `opacity`/`transform`
    there promotes every element to a layer and can stutter.

11. **Menus are defined once in `hugo.toml`.** Don't also set `menu = "main"` in page front matter —
    it produces "duplicate menu entry" warnings.

12. **`.Site.Title` is "Saurabh Kumar's Personal Site"** (overridden later in `hugo.toml`). The brand
    wordmark in `header.html` is therefore **hardcoded** "Saurabh Kumar" on purpose — don't "fix" it
    to `{{ .Site.Title }}`.

13. **`/blog/` duplicate content** is handled by `aliases = ["/blog/"]` on `content/_index.md` plus
    `build.render = "never"` on `content/blog/_index.md`. If the home page ever stops being the writing
    index, this alias becomes wrong — revisit it.

14. **`content/blog/markdown-syntax.md` is `draft = true`** (a demo). It won't appear in production
    builds — that's expected, not a bug. 10 published posts render.
</lessons>

<conventions>
- Keep changes surgical and match the existing inlined-CSS style. No build tooling, no frameworks.
- New blog-index markup goes through `partials/post-entry.html` — don't re-inline it.
- Every animation must have a `prefers-reduced-motion: reduce` fallback (there is a dedicated block in
  `style.html`).
- Color is scarce: reach for `--muted`/`--border` before `--accent`. No new accent colors without reason.
- No emoji in UI chrome, headings, or alt text. No `—`/`-` as sentence punctuation in prose/docs.
- Verify visually (screenshot) AND at runtime (CDP) for anything theme/animation/JS related before
  claiming done. Test light + dark + mobile width.
- Don't edit `themes/`. Override in `layouts/`.
</conventions>

<future_ideas>
Not requested, noted for context:
- The About card facts (python-dotenv stars, contact email, company chips) are hardcoded in
  `about.html`. Fine for a one-person site; move to front-matter params if they start changing.
- Pagination on `/` once posts outgrow a single screen.
- Self-hosting fonts (e.g. fontsource) to drop the render-blocking Google Fonts request, if FCP matters.
</future_ideas>
