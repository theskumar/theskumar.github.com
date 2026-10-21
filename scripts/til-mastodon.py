#!/usr/bin/env python3
"""Post new TIL notes to Mastodon, and edit the toot when a note changes.

Each note is a file, content/til/<unix-ts>.md, with TOML front matter:

    +++
    title = "EmbeddingGemma 2"
    date = 2026-10-19T12:00:00Z
    tags = ["ai", "rag"]
    mastodon = "117465622405124446"   # set by this script after posting
    toot = "optional hand-written short form"
    +++
    Note body in markdown.

Run by .github/workflows/til-mastodon.yml from the repo root after a push.
It looks at the note files changed by the last commit (HEAD~1..HEAD):

- added, no `mastodon` ID, not a backfill: post, then write the status ID
  into the file's front matter (the workflow commits it);
- modified, with a `mastodon` ID: edit that toot in place.

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


def read_note(path: Path) -> tuple[dict, str]:
    """Return (front matter, body) of a note file."""
    _, fm, body = path.read_text(encoding="utf-8").split("+++", 2)
    return tomllib.loads(fm), body.strip()


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


def format_toot(path: Path) -> str:
    fm, body = read_note(path)
    text = fm.get("toot") or body
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)  # [a](u) -> a (u)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    suffix = "\n\n" + " ".join(f"#{t}" for t in ["TIL", *fm.get("tags", [])])
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


def changed_notes() -> list[tuple[str, Path]]:
    """(status, path) for note files changed by the last commit; status is
    "A" (added) or "M" (modified)."""
    out = subprocess.run(
        ["git", "diff", "--name-status", "--no-renames", "HEAD~1", "HEAD", "--", NOTES_DIR],
        capture_output=True, text=True, check=True,
    ).stdout
    notes = []
    for line in out.splitlines():
        status, name = line.split("\t", 1)
        if status in ("A", "M") and NOTE_FILE.match(name):
            notes.append((status, Path(name)))
    return notes


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    paths = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    token = os.environ.get("MASTODON_ACCESS_TOKEN", "")

    notes = [("A", p) for p in paths] if paths else changed_notes()
    if not notes:
        print("No changed TIL notes.")
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=BACKFILL_DAYS)
    for status, path in notes:
        fm, _ = read_note(path)
        status_id = fm.get("mastodon")
        toot = format_toot(path)
        if status == "A" and not status_id:
            if fm["date"] < cutoff:
                print(f"{path}: backfill dated {fm['date']:%Y-%m-%d}, not posting.")
                continue
            action = "post"
        elif status == "M" and status_id:
            action = "edit"
        else:
            continue  # added with an ID (moved or migrated), or modified but never posted
        print(f"--- {action} {path} ({len(toot)} chars) ---\n{toot}\n---")
        if dry_run:
            continue
        if not token:
            print("MASTODON_ACCESS_TOKEN not set", file=sys.stderr)
            return 1
        if action == "post":
            result = mastodon("POST", "/api/v1/statuses", token, {"status": toot, "visibility": "public"})
            set_status_id(path, result["id"])
            print(f"Posted: {result.get('url', '')}")
        else:
            mastodon("PUT", f"/api/v1/statuses/{status_id}", token, {"status": toot})
            print(f"Edited status {status_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
