---
name: diagram
description: Draw explanatory SVG diagrams, with optional motion, and social-card cover art for saurabh-kumar.com posts and TIL notes. Use when adding a figure to an article, redrawing or animating one, or making a post's cover art.
---

# Diagrams for saurabh-kumar.com

A diagram proves one claim the prose makes. It sits right after the paragraph that makes the claim. Ink draws the structure; ember marks what the reader must notice. The site's CSS colors it, so it follows light and dark mode by itself.

## Steps

1. **Claim.** Read the post. Pick the sentence that has a shape: an order, a boundary, a before/after, a flow, a repeat, a trend. Write the alt text first: one sentence saying what the drawing shows. If you cannot write it, there is no diagram here. Most posts carry zero to two.
2. **Form.** Pick the form and its pattern from the table below. Read the pattern file; start from its coordinates.
3. **Draw** `assets/diagrams/<content file name>/<name>.svg` with the grammar below. `<content file name>` is the post's file name without `.md` (`how-prompt-caching-works`), or the TIL timestamp. Drafts and variants can live anywhere (`/tmp/…`); every command takes any path.
4. **Look.** Run `python3 scripts/diagrams.py preview <file>`: it lints the file, then prints a light and a dark PNG at 2× size. Read both. Fix every lint line. Done when: the lint prints nothing; describing the drawing from its labels and ember alone gives back the alt text; the ember marks the claim and nothing else.
5. **Place** it after the last paragraph of the claim (when the claim spans a list and a paragraph, after the paragraph):

   ```
   {{< diagram name="invalidation" alt="The earlier the edit, the more blocks are written again; appending rewrites only the new turn." >}}
   Blocks are conceptual, not token counts.
   {{< /diagram >}}
   ```

   The caption (optional, Markdown) holds what the drawing cannot: caveats, "not to scale", what is simplified.
6. **Motion** (only when it shows order, direction or change): see Motion.
7. **Cover** (when the post has a strong figure): see Cover art.
8. **Verify.** `python3 scripts/diagrams.py check` and `hugo --minify` both pass.

## Forms

Patterns are in `patterns/` beside this file: tested drawings to copy and adapt.

| Claim | Form | Pattern |
|---|---|---|
| The same thing repeats, a part changes | Rows stacked, the shared part aligned in ink, the changing part in `tint` | `rows.svg` |
| Two cases over time (blocked vs free, before vs after) | Two lanes on a shared time axis, row labels at the left | `lanes.svg` |
| Things happen in order; a later run differs | Rows, one per run, revealed with `step-N` | `sequence.svg` |
| Where something lives | `guide` boundary boxes labelled at top-left, parts inside, arrows across | `boundary.svg` |
| A decision or a data flow | Boxes left to right, arrows between, branch labels beside their arrow | `flow.svg` |
| One quantity changes with another | `guide` axes with arrowheads, a dashed `line` reference, the claim as a `signal` curve. No tick numbers unless the post states them | `plot.svg` |

## Grammar

- **Canvas** `viewBox="0 0 480 H"`, H as tall as the content (usually 160 to 360). It renders at most 480 px wide and about 340 px on a phone, so draw for 340: few parts, nothing dense. Keep 8 units clear at every edge. Snap coordinates to 4. Use absolute coordinates; `transform` is not available.
- **Classes** carry all color and weight. A shape has a class and geometry, nothing else.

  | Class | Draws | Use |
  |---|---|---|
  | `line` | ink stroke | Structure: boxes, arrows, rows, reference lines |
  | `guide` | faint stroke | Boundaries, brackets, axes, dividers: things to look past |
  | `signal` | ember stroke | The claim: an arrow, a curve, a marker line |
  | `tint` | ember stroke, soft ember fill | The changed, new or costly region |
  | `ink` / `ember` | solid fill | Dots, small marks |
  | `dash` | add to a stroke class | Absent, deferred, optional or reference |
  | `label` / `label-signal` | mono text, body / ember | Names; `label-signal` inside or beside ember shapes |

- **Ember is one idea.** Ember marks what the reader must notice: the thing that changes, costs or is new. A chain of shapes that carries one idea (a stale path: box, arrow, box) is one idea. In a contrast, ember goes on the side that carries the claim, usually the cost; draw an absent thing as a `guide dash` shape. If two unrelated things want ember, the drawing makes two claims: split it or cut one.
- **Labels.** Geist Mono at 14.72 units; each character is 8.9 units wide (`"psycopg pool"` is 107). Names of things or events, four words at most (`binary upgraded`, `1 box = 1 mention`); sentences go in the caption. Inside a box: 12 units clear each side, baseline at box top + height/2 + 5. Above a box: baseline 10 units above its top. Stacked labels: 24 units between baselines. Branch labels sit beside their arrow, 8 units clear. `text-anchor="middle"` or `"end"` centers or right-aligns a label. The lint checks labels against the canvas, each other, and box edges; it cannot check labels against lines, so look.
- **Shapes.** Rects get `rx="3"`. An arrow is a path with its head in the same `d`: `M x0 y H x M x-6 y-4 L x y L x-6 y+4`. Plain elements only: `g path rect circle ellipse line polyline polygon text tspan`.
- **Plain file.** No `id`, `style`, `fill`, `stroke`, `opacity`, font attributes or `transform`; no `<defs>`, markers, gradients or images. The SVG is inlined into the page, and the CSS owns the look.
- **Honest.** Lengths, widths and counts read as data. Counts that name positions (`Turn 3`, `5 mentions`) are fine. When sizes are illustrative, the caption says so. Never draw a value the post does not state.

## Motion

The SVG file is the finished drawing. Motion only decides how it appears; readers with reduced motion, RSS and the Markdown copy see the file as drawn. Animate only when motion shows something the still drawing cannot, and use one kind per drawing:

| Class | On | Effect | For |
|---|---|---|---|
| `step-1` … `step-4` | a `<g>` around each stage | Stages fade in in order, 0.8 s apart, when the figure scrolls into view; a Replay button appears | Order: run 1, run 2, then the run that differs |
| `draw` | a stroke, with `pathLength="1"` | The stroke draws on over 1.1 s | Direction or growth: a curve, a path taken |
| `flow` | a straight path without its arrowhead (draw the head as its own path) | Dashes move along it while on screen | Continuous traffic: connections, requests |

`sequence.svg` shows steps, `plot.svg` draw, `boundary.svg` flow. Check motion in a browser on `hugo server`; the preview PNGs show the final frame.

## Cover art

A post's social card (`layouts/partials/og/card.html`) puts cover art right of the title when `assets/diagrams/<content file name>/cover.svg` and its `cover.png` exist. Without one, the card stays as it is.

- `viewBox="0 0 500 320"`, **no text**: the card is seen at about 40% size, where labels turn to noise.
- Redraw the post's main figure with its labels removed and its shapes made larger and fewer; shapes and ember carry the meaning. When the post has no figure, draw an abstract echo of its idea in the same grammar (lines converging, rows repeating), always tied to the post.
- Draw with the normal classes; the cover render makes strokes heavier and uses the light palette only. The preview shows it that way.
- Same truths as a figure: a curve keeps its real shape against its reference line.
- After the preview, run `python3 scripts/diagrams.py covers` and commit `cover.png` with the SVG. Until then, `check` reports the PNG as missing. Hugo cannot rasterize SVG, so the PNG is what the card uses.
