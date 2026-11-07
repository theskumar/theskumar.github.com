#!/usr/bin/env python3
"""Check, preview and render the diagrams in assets/diagrams/.

  python3 scripts/diagrams.py check [FILE...]  # lint every SVG, or the files named (CI + pre-commit)
  python3 scripts/diagrams.py preview FILE...  # FILE-light.png, FILE-dark.png in /tmp/diagrams/
  python3 scripts/diagrams.py covers           # every cover.svg -> cover.png (commit the PNG)

A diagram is assets/diagrams/<content file name>/<name>.svg, drawn with the
classes in .agents/skills/diagram/SKILL.md. The site's CSS colors it, so the
file holds shapes and classes only. Colors for preview and covers come from
the light-dark() tokens in layouts/partials/style.html, the one source.

Needs rsvg-convert (brew install librsvg) for preview and covers.
"""
import re
import subprocess
import xml.etree.ElementTree as ET
import sys
import tempfile
from pathlib import Path

ROOT = Path("assets/diagrams")
STYLE = Path("layouts/partials/style.html")
OUT = Path("/tmp/diagrams")

CLASSES = {"line", "guide", "signal", "tint", "ink", "ember", "dash", "label", "label-signal",
           "step-1", "step-2", "step-3", "step-4", "draw", "flow"}
CHAR_W, ASCENT, DESCENT = 8.9, 11, 4  # Geist Mono at 14.72 units
ELEMENTS = {"svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "tspan"}
FIGURE_WIDTH = 480
COVER_SIZE = (500, 320)

# Literal sizes match the site at 1rem = 16px: --text-small is 0.92rem.
STROKES = {"line": 1.5, "guide": 1, "signal": 1.75, "tint": 1.75}
COVER_STROKE = 2  # covers are seen at ~40% size in feeds


def tokens():
    """Light and dark values of the tokens the diagrams use."""
    text = STYLE.read_text()
    out = {}
    for name in ("heading", "text", "faint", "accent", "accent-soft", "bg"):
        m = re.search(rf"--{name}:\s*light-dark\((.*)\);", text)
        if not m:
            sys.exit(f"{STYLE}: --{name} has no light-dark() value")
        depth, parts, cur = 0, [], ""
        for ch in m.group(1):
            depth += ch == "("
            depth -= ch == ")"
            if ch == "," and depth == 0:
                parts.append(cur.strip())
                cur = ""
            else:
                cur += ch
        parts.append(cur.strip())
        out[name] = parts
    return out


def stylesheet(mode, stroke_scale=1.0):
    i = 0 if mode == "light" else 1
    t = {k: v[i] for k, v in tokens().items()}
    s = {k: round(v * stroke_scale, 2) for k, v in STROKES.items()}
    return f"""
* {{ fill: none; stroke-linecap: round; stroke-linejoin: round; }}
.line {{ stroke: {t['heading']}; stroke-width: {s['line']}; }}
.guide {{ stroke: {t['faint']}; stroke-width: {s['guide']}; }}
.signal {{ stroke: {t['accent']}; stroke-width: {s['signal']}; }}
.tint {{ stroke: {t['accent']}; stroke-width: {s['tint']}; fill: {t['accent-soft']}; }}
.ink {{ stroke: none; fill: {t['heading']}; }}
.ember {{ stroke: none; fill: {t['accent']}; }}
.dash {{ stroke-dasharray: 5 4; }}
.label, .label-signal {{ stroke: none; fill: {t['text']}; font-family: 'Geist Mono', 'SF Mono', monospace; font-size: 14.72px; }}
.label-signal {{ fill: {t['accent']}; }}
""", t["bg"]


def check_file(path):
    errors = []
    src = path.read_text()
    body = re.sub(r"^\s*(<\?xml[^>]*>\s*)?", "", src)
    if not body.startswith("<svg"):
        errors.append("must start with <svg")
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', src)
    is_cover = path.stem == "cover"
    if not m:
        errors.append('needs viewBox="0 0 W H"')
    elif is_cover and (float(m[1]), float(m[2])) != COVER_SIZE:
        errors.append(f"cover viewBox must be 0 0 {COVER_SIZE[0]} {COVER_SIZE[1]}")
    elif not is_cover and float(m[1]) != FIGURE_WIDTH:
        errors.append(f"viewBox width must be {FIGURE_WIDTH}")
    for tag in set(re.findall(r"<([a-zA-Z][\w:-]*)", src)):
        if tag not in ELEMENTS:
            errors.append(f"<{tag}> is not allowed (use {', '.join(sorted(ELEMENTS))})")
    for attr in ("id", "style", "fill", "stroke", "stroke-width", "font-size", "font-family", "opacity", "color", "transform"):
        if re.search(rf'\s{attr}="', src):
            errors.append(f"{attr}= is not allowed: color and weight come from classes")
    for cls in re.findall(r'class="([^"]*)"', src):
        for c in cls.split():
            if c not in CLASSES:
                errors.append(f'class "{c}" is unknown (use {", ".join(sorted(CLASSES))})')
    if re.search(r'class="[^"]*\bdraw\b', src) and not re.search(r'class="[^"]*\bdraw\b[^"]*"[^>]*pathLength="1"|pathLength="1"[^>]*class="[^"]*\bdraw\b', src):
        errors.append('a "draw" shape needs pathLength="1"')
    if m:
        errors += label_errors(src, float(m[1]), float(m[2]))
    if is_cover and "<text" in src:
        errors.append("a cover has no text: labels vanish at feed size")
    if is_cover and not path.with_suffix(".png").exists():
        errors.append("cover.png is missing: run python3 scripts/diagrams.py covers")
    return sorted(set(errors))


def label_errors(src, width, height):
    """Labels inside the canvas, clear of each other and of box edges."""
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.fromstring(src)
    boxes, rects = [], []
    for el in root.iter():
        tag = el.tag.replace(ns, "")
        if tag == "text":
            text = "".join(el.itertext())
            x, y = float(el.get("x", 0)), float(el.get("y", 0))
            w = len(text) * CHAR_W
            anchor = el.get("text-anchor", "start")
            x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
            boxes.append((text, x0, y - ASCENT, x0 + w, y + DESCENT))
        elif tag == "rect":
            x, y = float(el.get("x", 0)), float(el.get("y", 0))
            rects.append((x, y, x + float(el.get("width", 0)), y + float(el.get("height", 0))))
    errors = []
    for t, a, b, c, d in boxes:
        if a < 4 or b < 0 or c > width - 4 or d > height:
            errors.append(f'label "{t}" runs off the canvas (keep 8 units clear)')
        for (rx0, ry0, rx1, ry1) in rects:
            inside = rx0 <= a and c <= rx1 and ry0 <= b and d <= ry1
            apart = c <= rx0 or a >= rx1 or d <= ry0 or b >= ry1
            if not inside and not apart:
                errors.append(f'label "{t}" crosses a box edge (needs {round(c - a)} units wide inside, plus 12 each side)')
    for i, (t, a, b, c, d) in enumerate(boxes):
        for (u, e, f, g, h) in boxes[i + 1:]:
            if a < g and e < c and b < h and f < d:
                errors.append(f'labels "{t}" and "{u}" overlap')
    return errors


def check(files=None):
    failed = False
    for path in map(Path, files) if files else sorted(ROOT.glob("*/*.svg")):
        for e in check_file(path):
            print(f"{path}: {e}")
            failed = True
    for path in [] if files else sorted(ROOT.glob("*")):
        if path.is_file():
            print(f"{path}: diagrams go in assets/diagrams/<content file name>/")
            failed = True
    sys.exit(1 if failed else 0)


def render(svg, png, css, bg=None, width=None):
    with tempfile.NamedTemporaryFile("w", suffix=".css", delete=False) as f:
        f.write(css)
    cmd = ["rsvg-convert", "-s", f.name, "-o", str(png)]
    if bg:
        cmd += ["-b", bg]
    if width:
        cmd += ["-w", str(width)]
    subprocess.run(cmd + [str(svg)], check=True)


def preview(files):
    OUT.mkdir(parents=True, exist_ok=True)
    for f in map(Path, files):
        for e in check_file(f):
            if "cover.png is missing" not in e:  # expected until `covers`
                print(f"{f}: {e}")
        for mode in ("light", "dark"):
            css, bg = stylesheet(mode, COVER_STROKE / 1.5 if f.stem == "cover" else 1)
            png = OUT / f"{f.parent.name}-{f.stem}-{mode}.png"
            render(f, png, css, bg, width=960)  # 2x, so labels are legible
            print(png)


def covers():
    for svg in sorted(ROOT.glob("*/cover.svg")):
        css, _ = stylesheet("light", COVER_STROKE / 1.5)
        png = svg.with_suffix(".png")
        render(svg, png, css)  # transparent, 500x320: card.html places it
        print(png)


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["check"]
    if cmd == "check":
        check(args)
    elif cmd == "preview" and args:
        preview(args)
    elif cmd == "covers":
        covers()
    else:
        sys.exit(__doc__)
