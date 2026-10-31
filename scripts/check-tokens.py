#!/usr/bin/env python3
"""Check that the design tokens in CSS and in docs/brand/design-tokens.md agree.

Fails (exit 1) when:
- a token in the :root block of layouts/partials/style.html is missing from
  the doc, or the doc lists a token that the CSS does not define;
- a token has a different value in the two places;
- a component outside :root sets font-family to anything but var(--font-*);
- a component sets a literal font-size without a "/* one-off: ... */" comment
  on the same line. var(--text-*), var(--link-ext-size), inherit and em units
  are allowed.

Run from the repository root. CI runs it before the build.
"""
import re
import sys
from pathlib import Path

CSS = Path("layouts/partials/style.html")
DOC = Path("docs/brand/design-tokens.md")


def norm(value):
    """Compare values without caring about spacing: `a,  b` equals `a, b`."""
    return re.sub(r"\s*,\s*", ",", re.sub(r"\s+", " ", value)).strip()


def css_tokens(text):
    root = re.search(r":root\s*\{(.*?)\n  \}", text, re.S)
    if not root:
        sys.exit(f"{CSS}: no :root block found")
    body = re.sub(r"/\*.*?\*/", "", root.group(1), flags=re.S)
    tokens = {}
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", body):
        tokens[name] = norm(value)
    return tokens, root.end()


def doc_tokens(text):
    tokens = {}
    for name, value in re.findall(r"^\|\s*`(--[a-z0-9-]+)`\s*\|\s*`([^`]+)`\s*\|", text, re.M):
        tokens[name] = norm(value)
    return tokens


def main():
    css_text = CSS.read_text()
    css, root_end = css_tokens(css_text)
    doc = doc_tokens(DOC.read_text())
    errors = []

    for name in sorted(css.keys() - doc.keys()):
        errors.append(f"{name} is in {CSS} but not documented in {DOC}")
    for name in sorted(doc.keys() - css.keys()):
        errors.append(f"{name} is documented in {DOC} but not defined in {CSS}")
    for name in sorted(css.keys() & doc.keys()):
        if css[name] != doc[name]:
            errors.append(f"{name}: CSS has `{css[name]}`, doc has `{doc[name]}`")

    first_line = css_text.count("\n", 0, root_end) + 1
    for lineno, line in enumerate(css_text.splitlines()[first_line:], start=first_line + 1):
        for value in re.findall(r"font-family\s*:\s*([^;]+);", line):
            if not re.fullmatch(r"\s*(var\(--font-(serif|sans|mono)\)|inherit)\s*", value):
                errors.append(f"{CSS}:{lineno}: font-family `{value.strip()}` must be var(--font-*)")
        for value in re.findall(r"font-size\s*:\s*([^;]+);", line):
            value = value.strip()
            if re.fullmatch(r"var\(--text-[a-z0-9-]+\)|var\(--link-ext-size\)|inherit|[0-9.]+em", value):
                continue
            if "/* one-off:" in line:
                continue
            errors.append(f"{CSS}:{lineno}: font-size `{value}` needs a --text-* token or a /* one-off: reason */ comment")

    if errors:
        print("Design tokens are out of step:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"tokens ok: {len(css)} tokens match {DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
