#!/usr/bin/env python3
"""Check TIL notes and post tags before a build.

Rules (see AGENTS.md, "TIL"):

- Each note is content/til/<unix-ts>.md with TOML front matter.
- `date` is a UTC datetime (ends in Z) equal to the filename timestamp.
  The week pages are built from the filename, the note page from `date`;
  if they differ, the note drops out of its week and the feed.
- `title` is set; only known keys are used.
- Every tag, on notes and on Writing posts, is in data/tags.json.

Run by the deploy workflow and the pre-commit hook. Exit 0 if clean, 1 with
one line per problem otherwise.

Usage:
    python3 scripts/check-til.py
"""

import json
import re
import sys
import tomllib
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "content/til"
BLOG = ROOT / "content/blog"
NOTE_KEYS = {"title", "date", "tags", "toot", "mastodon", "anchor", "aliases"}


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\+\+\+\n(.*?)\n\+\+\+\n", text, re.S)
    if not m:
        raise ValueError("no TOML front matter (+++)")
    return tomllib.loads(m.group(1))


def check_note(path: Path, vocab: set[str]) -> list[str]:
    fm = front_matter(path)
    errors = []
    if not isinstance(fm.get("title"), str) or not fm["title"].strip():
        errors.append("missing title")
    date = fm.get("date")
    if not isinstance(date, datetime) or date.utcoffset() != timedelta(0):
        errors.append(f"date must be a UTC datetime like 2026-10-19T12:00:00Z, got {date!r}")
    elif int(date.timestamp()) != int(path.stem):
        errors.append(f"date {date:%Y-%m-%dT%H:%M:%SZ} doesn't match the filename "
                      f"(expected {datetime.fromtimestamp(int(path.stem), timezone.utc):%Y-%m-%dT%H:%M:%SZ})")
    if unknown := set(fm) - NOTE_KEYS:
        errors.append(f"unknown keys: {sorted(unknown)}")
    if bad := [t for t in fm.get("tags", []) if t not in vocab]:
        errors.append(f"tags not in data/tags.json: {bad}")
    return errors


def main() -> int:
    vocab = set(json.loads((ROOT / "data/tags.json").read_text(encoding="utf-8")))
    problems = []
    for path in sorted(NOTES.glob("*.md")):
        if path.name == "_index.md":
            continue
        if not re.fullmatch(r"\d{10}", path.stem):
            problems.append(f"{path.relative_to(ROOT)}: name must be <unix-ts>.md")
            continue
        try:
            errors = check_note(path, vocab)
        except (ValueError, tomllib.TOMLDecodeError) as e:
            errors = [str(e)]
        problems += [f"{path.relative_to(ROOT)}: {e}" for e in errors]
    for path in sorted([*BLOG.glob("*.md"), *BLOG.glob("*/index.md")]):
        if path.name == "_index.md":
            continue
        try:
            tags = front_matter(path).get("tags", [])
        except (ValueError, tomllib.TOMLDecodeError) as e:
            problems.append(f"{path.relative_to(ROOT)}: {e}")
            continue
        if bad := [t for t in tags if t not in vocab]:
            problems.append(f"{path.relative_to(ROOT)}: tags not in data/tags.json: {bad}")
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
