# Design tokens

The tokens that every page of saurabh-kumar.com draws from. They live in the `:root` block of `layouts/partials/style.html`. This file documents each one. `scripts/check-tokens.py` fails the build when a token here and in the CSS disagree, so change both together.

Brand concept, logo, motion and voice are in [`BRAND.md`](BRAND.md).

## Rules

1. **One reading style.** Everything people read (posts, TIL notes, Projects, Now, the About bio, page intros) uses `--font-sans` at `--text-body` with `--leading-body`. A Writing post and a TIL note read the same way.
2. **Serif is for display.** Newsreader sets titles, headings, list item titles, the wordmark, the big panel number and the italic post summary. It never sets a paragraph.
3. **Mono is for labels and code.** Geist Mono sets eyebrows, section labels, dates, meta rows, nav, buttons, tags and code. Uppercase is reserved for mono labels; everything else uses sentence case.
4. **Ember is a signal, not paint.** `--accent` marks the active nav item, eyebrows, hover states and the sun in the mark. If more than about 5% of a screen is ember, there is too much. Links stay ink with an underline.
5. **No literal sizes in components.** Use a `--text-*` token for font size, a `--space-*` step for new spacing in `rem` or `px`, and a `--radius*` token for corners. A genuine one-off font size (the wordmark, the panel number) carries a `/* one-off: reason */` comment on the same line; the check allows it. Relative sizes (`em`, `inherit`) are fine inside a token-sized parent.
6. **Text colors pass WCAG AA.** `--muted` is the lightest color for text. `--faint` is for lines, ticks and drawings only.
7. **Links that leave the site end in ↗.** The Markdown link render hook adds it to every `http` or `https` link, and `layouts/_default/projects.html` adds it to project names; both go through `layouts/partials/ext-tail.html`, which keeps the last word and the mark on one line. Internal links, `mailto:` links, the About social row, the footer and the TIL "Discuss" link stay plain: their text already names the place. The mark is decoration, so screen readers skip it.

## Layout

| Token | Value | Use |
|---|---|---|
| `--width` | `880px` | Page chrome: header, nav rule, footer |
| `--measure` | `720px` | Reading column |
| `--margin-col` | `7.5rem` | Mono date column beside TIL notes |
| `--margin-gap` | `2.2rem` | Gap between that column and the text |
| `--radius-sm` | `2px` | Corners on buttons, chips and highlighted text |
| `--radius` | `3px` | Corners on code, tags, panels and images |
| `--radius-lg` | `4px` | Corners on floating panels (the TOC panel) |

## Spacing

New margin, padding and gap in `rem` or `px` use a step. Spacing set in `em` stays `em`, so it scales with the text it belongs to (button padding, list indents, space around a blockquote). Older values more than 2px from a step (`1.2rem`, `1.6rem`, `10px`, `2.6rem` and a few others) are still literal; move one to a step when you next touch its rule and check the page.

| Token | Value | Use |
|---|---|---|
| `--space-1` | `0.25rem` | Hairline gaps: a tag's count, small nudges |
| `--space-2` | `0.5rem` | Gaps inside a row: chips, icon and label |
| `--space-3` | `0.75rem` | Gaps between small items |
| `--space-4` | `1rem` | Default gap between blocks in a component |
| `--space-5` | `1.4rem` | Panel padding, gaps between rows and items |
| `--space-6` | `2.2rem` | Between blocks |
| `--space-7` | `3rem` | Between page sections |

## Type

| Token | Value | Use |
|---|---|---|
| `--font-serif` | `'Newsreader', 'Lyon Text', Georgia, 'Times New Roman', serif` | Display only |
| `--font-sans` | `'Geist', 'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif` | Reading text and UI |
| `--font-mono` | `'Geist Mono', 'SF Mono', 'JetBrains Mono', ui-monospace, monospace` | Labels and code |
| `--text-display` | `clamp(1.9rem, 4.5vw, 2.55rem)` | Page, post and hero titles |
| `--text-h2` | `1.45rem` | Section headings in prose |
| `--text-h3` | `1.2rem` | Sub-headings, panel headings |
| `--text-title` | `1.3rem` | Item titles in lists: the Writing index, the TIL stream |
| `--text-lede` | `1.14rem` | Italic serif summary under a post title |
| `--text-body` | `1.0625rem` | All reading text (17 px) |
| `--text-small` | `0.92rem` | Secondary text: descriptions, panels, tables, pager, footnotes |
| `--text-code` | `0.86rem` | Code blocks |
| `--text-meta` | `0.76rem` | Mono rows: nav, buttons, post meta, "Tagged", "Markdown" |
| `--text-label` | `0.72rem` | Mono labels: eyebrows, section labels, dates, footer |
| `--text-tag` | `0.68rem` | Tags and chips |
| `--leading-display` | `1.14` | Titles |
| `--leading-heading` | `1.18` | Headings |
| `--leading-ui` | `1.62` | Default for UI text, panels, code |
| `--leading-body` | `1.7` | Every reading column |
| `--tracking-display` | `-0.02em` | Titles |
| `--tracking-heading` | `-0.015em` | Headings and item titles |
| `--tracking-body` | `-0.006em` | Sans text |
| `--tracking-caps` | `0.14em` | Uppercase mono labels, nav, buttons |
| `--tracking-meta` | `0.08em` | Dates and meta rows |
| `--tracking-mono` | `0.06em` | Mixed-case mono text |

## Color

Each color token holds a light and a dark value, through `light-dark()`.

| Token | Value | Use |
|---|---|---|
| `--bg` | `light-dark(#F7F4ED, #171411)` | Paper |
| `--bg-tint` | `light-dark(#F1EDE3, #1D1A15)` | Tinted paper |
| `--surface` | `light-dark(#FCFAF5, #1E1B16)` | Panels on hover, details, TOC panel |
| `--surface-2` | `light-dark(#F3F0E8, #242019)` | Hover rows in the TOC |
| `--border` | `light-dark(rgba(30,25,16,0.12), rgba(240,232,214,0.11))` | Quiet borders |
| `--border-strong` | `light-dark(rgba(30,25,16,0.22), rgba(240,232,214,0.2))` | Link underlines, buttons |
| `--hairline` | `light-dark(rgba(30,25,16,0.16), rgba(240,232,214,0.14))` | Rules between sections and rows |
| `--heading` | `light-dark(#1D1810, #F1EBDD)` | Ink: headings, links, strong text |
| `--text` | `light-dark(#3B352A, #C9C2B1)` | Body text |
| `--muted` | `light-dark(#736B5A, #8F8875)` | Secondary text; the lightest that passes AA |
| `--faint` | `light-dark(#A59C87, #6A6455)` | Lines, ticks, drawings; never text |
| `--accent` | `light-dark(#B4491F, #E08B54)` | Ember: the one signal color |
| `--accent-soft` | `light-dark(rgba(180,73,31,0.09), rgba(224,139,84,0.1))` | Text selection |
| `--code-bg` | `light-dark(#F0ECE2, #211E18)` | Code background |
| `--code-color` | `light-dark(#1D1810, #E7E1D2)` | Code text |
| `--tag-bg` | `light-dark(#EEEADF, #29251D)` | Tag and chip background |
| `--tag-text` | `light-dark(#5D584B, #B4AC99)` | Tag and chip text |

## Links

| Token | Value | Use |
|---|---|---|
| `--link-ext-mark` | `"↗"` | The mark after a link that leaves the site (rule 7) |
| `--link-ext-size` | `0.72em` | Its size, relative to the link text |
| `--link-ext-color` | `var(--muted)` | Its color at rest; it turns `--accent` on hover |

Syntax colors for code blocks are in `layouts/partials/syntax.css`, outside the token set; each passes 4.5:1 on `--code-bg`.

## Changing a token

1. Change the value in `:root` in `layouts/partials/style.html`.
2. Change the same row in this file.
3. Run `python3 scripts/check-tokens.py`.
4. Check a post, a TIL note, Projects and About in both themes. Text tokens also need a check at 320 px wide.
