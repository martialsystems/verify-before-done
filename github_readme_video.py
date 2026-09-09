#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. MIT.
"""Print a GitHub README video embed URL from an MP4.

GitHub README sanitizes HTML ``<video>``. A relative ``docs/demo.mp4`` tag is
stripped. The player is a bare ``https://github.com/user-attachments/assets/<uuid>``
URL on its own line. This script uploads via ``gh issue comment --attach``
(gh 2.99+) so the next README does not spend a session rediscovering that.

  python3 github_readme_video.py --repo owner/name --file docs/demo.mp4
  python3 github_readme_video.py --repo owner/name --file docs/demo.mp4 --issue 1
  python3 github_readme_video.py --repo owner/name --file docs/demo.mp4 --gh /path/to/gh

Paste the printed URL into the README with a blank line above and below.
Keep the repo file for clones. Verify the live GitHub HTML has ``<video`` or
``private-user-images``. Do not POST uploads.github.com by hand. Do not use an
HTML video tag.

If the clip has speech, two-pass loudnorm to I=-9 TP=-0.5 LRA=7 first.
ReplayKit system audio is often -27 LUFS and inaudible in GitHub's player.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple

ATTACH_MIN = (2, 99, 0)
ASSET_RE = re.compile(
    r"https://github\.com/user-attachments/assets/[0-9a-fA-F-]+"
)
VERSION_RE = re.compile(r"\bgh version (\d+)\.(\d+)\.(\d+)")
ISSUE_NUM_RE = re.compile(r"/issues/(\d+)\b")
DEFAULT_TITLE = "README demo video"


class GhError(RuntimeError):
    """gh missing, too old, or a call failed."""


def parse_gh_version(text: str) -> Tuple[int, int, int]:
    match = VERSION_RE.search(text)
    if not match:
        raise GhError("could not parse gh version from: {0}".format(text.strip()[:200]))
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def attach_help_has_flag(help_text: str) -> bool:
    return bool(re.search(r"--attach\b", help_text))


def parse_embed_url(text: str) -> Optional[str]:
    match = ASSET_RE.search(text)
    return match.group(0) if match else None


def parse_issue_number(create_stdout: str) -> int:
    match = ISSUE_NUM_RE.search(create_stdout)
    if not match:
        raise GhError("gh issue create did not print an issue URL:\n{0}".format(create_stdout))
    return int(match.group(1))


def run_gh(gh: str, args: Sequence[str], *, cwd: Optional[Path] = None) -> str:
    proc = subprocess.run(
        [gh, *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GhError(
            "gh {0} failed ({1}):\n{2}{3}".format(
                " ".join(args[:4]),
                proc.returncode,
                proc.stdout or "",
                proc.stderr or "",
            )
        )
    return proc.stdout


def resolve_gh(explicit: str) -> str:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise GhError("--gh is not a file: {0}".format(path))
        return str(path.resolve())
    found = shutil_which("gh")
    if not found:
        raise GhError("gh is not on PATH. Install GitHub CLI 2.99+ or pass --gh.")
    return found


def shutil_which(name: str) -> Optional[str]:
    from shutil import which

    return which(name)


def require_attach(gh: str) -> Tuple[int, int, int]:
    version_text = run_gh(gh, ["version"])
    version = parse_gh_version(version_text)
    help_text = run_gh(gh, ["issue", "comment", "--help"])
    if version < ATTACH_MIN or not attach_help_has_flag(help_text):
        raise GhError(
            "gh {0}.{1}.{2} cannot --attach (need 2.99+). Homebrew is often behind. "
            "Download a newer gh from https://github.com/cli/cli/releases and pass --gh. "
            "Do not POST uploads.github.com by hand.".format(*version)
        )
    return version


def find_issue(gh: str, repo: str, title: str) -> Optional[int]:
    raw = run_gh(
        gh,
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--search",
            title,
            "--json",
            "number,title",
        ],
    )
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GhError("gh issue list was not JSON: {0}".format(exc)) from exc
    for row in rows:
        if row.get("title") == title:
            return int(row["number"])
    return None


def create_issue(gh: str, repo: str, title: str) -> int:
    body = (
        "Asset host for the GitHub README video player. "
        "Keep this issue; deleting it drops the player."
    )
    out = run_gh(
        gh,
        ["issue", "create", "--repo", repo, "--title", title, "--body", body],
    )
    return parse_issue_number(out)


def latest_embed_url(gh: str, repo: str, issue: int) -> Optional[str]:
    raw = run_gh(gh, ["api", "repos/{0}/issues/{1}/comments".format(repo, issue)])
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GhError("gh api comments was not JSON: {0}".format(exc)) from exc
    url = None
    for row in rows:
        found = parse_embed_url(str(row.get("body") or ""))
        if found:
            url = found
    return url


def attach_video(gh: str, repo: str, issue: int, video: Path) -> str:
    run_gh(
        gh,
        [
            "issue",
            "comment",
            str(issue),
            "--repo",
            repo,
            "--attach",
            str(video),
            "--body",
            "README video attachment.",
        ],
        cwd=video.parent,
    )
    url = latest_embed_url(gh, repo, issue)
    if not url:
        raise GhError(
            "attached {0} to {1}#{2} but no user-attachments URL appeared".format(
                video.name, repo, issue
            )
        )
    return url


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--repo", required=True, help="owner/name")
    p.add_argument("--file", required=True, help="MP4 path")
    p.add_argument("--issue", type=int, default=0, help="existing issue number (else reuse/create)")
    p.add_argument("--title", default=DEFAULT_TITLE, help="issue title when creating or finding")
    p.add_argument("--gh", default="", help="gh binary (2.99+). Default: gh on PATH")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    video = Path(args.file).expanduser().resolve()
    if not video.is_file():
        print("github_readme_video: not a file: {0}".format(video), file=sys.stderr)
        return 2
    try:
        gh = resolve_gh(args.gh)
        require_attach(gh)
        issue = args.issue or find_issue(gh, args.repo, args.title)
        if issue is None:
            issue = create_issue(gh, args.repo, args.title)
        url = attach_video(gh, args.repo, issue, video)
    except GhError as exc:
        print("github_readme_video: {0}".format(exc), file=sys.stderr)
        return 2
    print(url)
    print("", file=sys.stderr)
    print("Paste on its own README line, blank line above and below.", file=sys.stderr)
    print("Keep the repo file. Do not wrap in an HTML video tag.", file=sys.stderr)
    print("Host issue: https://github.com/{0}/issues/{1}".format(args.repo, issue), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
