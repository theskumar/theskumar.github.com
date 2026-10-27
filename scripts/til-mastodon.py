#!/usr/bin/env python3
"""Post new TIL notes to Mastodon, and edit the toot when a note changes.

Each note is a file, content/til/<unix-ts>.md, with TOML front matter:

    +++
    title = "EmbeddingGemma 2"
    date = 2026-10-19T12:00:00Z
    tags = ["llm", "search"]
    mastodon = "117465622405124446"   # set by this script after posting
    toot = "optional hand-written short form"
    +++
    Note body in markdown.

Run by .github/workflows/til-mastodon.yml from the repo root after a push.
It looks at the note files changed by the whole push, from TIL_BASE (the
commit before the push) to HEAD; without TIL_BASE, from HEAD~1:

- added, no `mastodon` ID, not a backfill: post, then write the status ID
  into the file's front matter (the workflow commits it);
- modified, with a `mastodon` ID, and the toot text changed: edit that toot;
- anything else (an added note that already has an ID, an old note): skip.

A note that fails doesn't stop the others; the script exits 1 at the end,
after writing the IDs it did get.

Usage:
    python3 scripts/til-mastodon.py            # needs MASTODON_ACCESS_TOKEN
    python3 scripts/til-mastodon.py --dry-run  # print the toots, post nothing
    python3 scripts/til-mastodon.py --dry-run content/til/1760875200.md
"""

import json
import os
import re
import subprocess
import sys
import tomllib
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

MASTODON_INSTANCE = "https://mastodon.social"
SITE = "https://saurabh-kumar.com"
CHAR_LIMIT = 500
NOTES_DIR = "content/til"
NOTE_FILE = re.compile(r"^content/til/(\d+)\.md$")
# Notes dated further back than this are backfills (moved or restored
# notes), not new learnings, so they don't get a fresh toot.
BACKFILL_DAYS = 14


def parse_note(text: str) -> tuple[dict, str]:
    """Return (front matter, body) of a note's text."""
    _, fm, body = text.split("+++", 2)
    return tomllib.loads(fm), body.strip()


def read_note(path: Path) -> tuple[dict, str]:
    return parse_note(path.read_text(encoding="utf-8"))


def note_url(path: Path) -> str:
    return f"{SITE}/til/{path.stem}/"


def smart_truncate(text: str, limit: int) -> str:
    """Trim to a sentence boundary near the limit, else a word one. The
    caller appends the ellipsis."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for sep in (". ", "! ", "? ", ".\n", "\n"):
        idx = cut.rfind(sep)
        if idx >= limit * 0.6:
            return cut[: idx + 1].rstrip()
    idx = cut.rfind(" ")
    return (cut[:idx] if idx > 0 else cut).rstrip()


def hashtag(tag: str) -> str:
    """Mastodon hashtags stop at "-", so "open-source" becomes #opensource."""
    return "#" + tag.replace("-", "")


def format_toot(path: Path, fm: dict, body: str) -> str:
    text = fm.get("toot") or body
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)  # [a](u) -> a (u)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    suffix = "\n\n" + " ".join(hashtag(t) for t in ["TIL", *fm.get("tags", [])])
    available = CHAR_LIMIT - len(suffix)
    if len(text) <= available:
        return text + suffix
    # Too long: cut, and link the full note. Mastodon counts any URL as 23
    # characters, so reserving its real length never overflows.
    tail = f"…\n\nFull note: {note_url(path)}"
    return smart_truncate(text, available - len(tail)) + tail + suffix


def set_status_id(path: Path, status_id: str) -> None:
    """Add `mastodon = "<id>"` to the note's front matter."""
    text = path.read_text(encoding="utf-8")
    head, fm, body = text.split("+++", 2)
    fm = fm.rstrip("\n") + f'\nmastodon = "{status_id}"\n'
    path.write_text(head + "+++" + fm + "+++" + body, encoding="utf-8")


def mastodon(method: str, api_path: str, token: str, data: dict) -> dict:
    req = urllib.request.Request(
        f"{MASTODON_INSTANCE}{api_path}",
        data=json.dumps(data).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def push_base() -> str:
    """The commit before the push, or HEAD~1 when that's unknown (a manual
    run, or a new branch, where GitHub sends all zeros)."""
    base = os.environ.get("TIL_BASE", "")
    if base and set(base) != {"0"}:
        try:
            git("cat-file", "-e", f"{base}^{{commit}}")
            return base
        except subprocess.CalledProcessError:
            pass
    return "HEAD~1"


def changed_notes(base: str) -> list[tuple[str, Path]]:
    """(status, path) for note files changed between base and HEAD; status
    is "A" (added) or "M" (modified)."""
    out = git("diff", "--name-status", "--no-renames", base, "HEAD", "--", NOTES_DIR)
    notes = []
    for line in out.splitlines():
        status, name = line.split("\t", 1)
        if status in ("A", "M") and NOTE_FILE.match(name):
            notes.append((status, Path(name)))
    return notes


def old_toot(base: str, path: Path) -> str:
    """The toot text the note produced before this push."""
    try:
        fm, body = parse_note(git("show", f"{base}:{path.as_posix()}"))
    except subprocess.CalledProcessError:
        return ""
    return format_toot(path, fm, body)


def plan(status: str, path: Path, base: str, cutoff: datetime) -> str | None:
    """What to do with one changed note: "post", "edit", or None (skip)."""
    fm, body = read_note(path)
    if fm["date"].tzinfo is None:
        raise ValueError("date has no timezone; write it in UTC, ending in Z")
    if status == "A" and not fm.get("mastodon"):
        if fm["date"] < cutoff:
            print(f"{path}: backfill dated {fm['date']:%Y-%m-%d}, not posting.")
            return None
        return "post"
    if status == "M" and fm.get("mastodon"):
        if format_toot(path, fm, body) == old_toot(base, path):
            print(f"{path}: toot text unchanged, not editing.")
            return None
        return "edit"
    return None  # added with an ID (moved or migrated), or never posted


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    token = os.environ.get("MASTODON_ACCESS_TOKEN", "")
    base = push_base()
    notes = [("A", p) for p in paths] if paths else changed_notes(base)
    if not notes:
        print("No changed TIL notes.")
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=BACKFILL_DAYS)
    failed = 0
    for status, path in notes:
        try:
            action = plan(status, path, base, cutoff)
            if not action:
                continue
            fm, body = read_note(path)
            toot = format_toot(path, fm, body)
            print(f"--- {action} {path} ({len(toot)} chars) ---\n{toot}\n---")
            if dry_run:
                continue
            if not token:
                raise RuntimeError("MASTODON_ACCESS_TOKEN not set")
            if action == "post":
                result = mastodon("POST", "/api/v1/statuses", token, {"status": toot, "visibility": "public"})
                set_status_id(path, result["id"])
                print(f"Posted: {result.get('url', '')}")
            else:
                mastodon("PUT", f"/api/v1/statuses/{fm['mastodon']}", token, {"status": toot})
                print(f"Edited status {fm['mastodon']}")
        except Exception as e:  # one bad note mustn't lose the others' IDs
            failed += 1
            print(f"{path}: FAILED: {e}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
