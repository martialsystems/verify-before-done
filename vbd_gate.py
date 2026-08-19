#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. MIT.
"""Verify-before-done gates: checks an agent (or you) can forget.

Prose VBD cannot see a phone or remember to fetch. This command fails closed
on the repeatable misses. Judgment (quality bar, honest residuals) stays prose.

  python3 vbd_gate.py check --app-root DIR
  python3 vbd_gate.py check --app-root DIR --claim-done --not-promoted 'unique to this product'
  python3 vbd_gate.py hook-install --app-root DIR

Each run appends one JSON line to ~/.grok/logs/vbd_gate.jsonl (VBD_GATE_LOG).
Exit 0 pass, 2 fail. Does not discard local work. Does not pull.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

PACK_ROOT = Path(__file__).resolve().parent
HOOK_MARK = "vbd-gate-pre-push"
DASH_CHARS = ("\u2014", "\u2013")
UI_SUFFIX = {".html", ".css"}
PROSE_SUFFIX = {".md", ".txt", ".html"}
DASH_ALLOW = {"VERIFY_BEFORE_DONE.md"}
SKIP_CLASS = "skip-juicy"
CHART_HINT = re.compile(r"(chart-wrap|chart_wrap)", re.I)


class _SkipParser(HTMLParser):
    def __init__(self, skip_class: str) -> None:
        super().__init__()
        self.skip_class = skip_class
        self.href: Optional[str] = None
        self._stack: List[Tuple[str, Optional[str], Set[str]]] = []
        self._skip_open = False
        self.target_is_chart = False
        self.target_contains_chart = False
        self._in_target_depth = 0
        self._target_id: Optional[str] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        classes = set((ad.get("class") or "").split())
        eid = ad.get("id") or None
        self._stack.append((tag, eid, classes))
        if tag == "a" and self.skip_class in classes and not self.href:
            href = ad.get("href") or ""
            if href.startswith("#") and len(href) > 1:
                self.href = href
                self._target_id = href[1:]
        if self._target_id and eid == self._target_id:
            self._in_target_depth = 1
            if "chart-wrap" in classes or CHART_HINT.search(ad.get("class") or ""):
                self.target_is_chart = True
        elif self._in_target_depth:
            self._in_target_depth += 1
            if "chart-wrap" in classes or tag == "canvas" or CHART_HINT.search(
                (ad.get("class") or "") + " " + (eid or "")
            ):
                self.target_contains_chart = True

    def handle_endtag(self, tag: str) -> None:
        if self._in_target_depth:
            self._in_target_depth -= 1
        if self._stack:
            self._stack.pop()


def skip_landing_errors(html: str) -> List[str]:
    """Fail if a skip jump lands on a section that *contains* the chart."""
    p = _SkipParser(SKIP_CLASS)
    try:
        p.feed(html)
    except Exception as exc:
        return ["html parse failed: {0}".format(exc)]
    if not p.href:
        return []
    if p.target_contains_chart and not p.target_is_chart:
        return [
            "skip {0} lands on a section that contains a chart; "
            "point href at the visual target (the chart wrap), not the panel".format(p.href)
        ]
    return []


def _git(root: Path, args: Sequence[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=check,
    )


def is_git(root: Path) -> bool:
    return (root / ".git").exists() or _git(root, ["rev-parse", "--is-inside-work-tree"]).returncode == 0


def git_fetch(root: Path) -> Optional[str]:
    proc = _git(root, ["fetch"])
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        if "No remote" in err or "does not appear to be a git repository" in err:
            return None
        return "git fetch failed: {0}".format(err or proc.returncode)
    return None


def origin_ahead_errors(root: Path) -> List[str]:
    up = _git(root, ["rev-parse", "--abbrev-ref", "@{upstream}"])
    if up.returncode != 0:
        return []
    counts = _git(root, ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
    if counts.returncode != 0:
        return []
    parts = (counts.stdout or "0\t0").strip().split()
    behind = int(parts[1]) if len(parts) > 1 else 0
    if behind <= 0:
        return []
    dirty = _git(root, ["status", "--porcelain"])
    dirty_n = len([ln for ln in (dirty.stdout or "").splitlines() if ln.strip()])
    if dirty_n:
        return [
            "origin is ahead ({0} commit(s)) and the tree is dirty; "
            "stash, commit, or report both; do not discard or reset --hard".format(behind)
        ]
    return [
        "origin is ahead ({0} commit(s)) and the tree is clean; pull before claiming done".format(
            behind
        )
    ]


def changed_paths(
    root: Path,
    *,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
    tracked_only: bool = False,
) -> List[Path]:
    names: Set[str] = set()
    if from_ref and to_ref and to_ref != "0" * 40:
        if from_ref == "0" * 40:
            diff = _git(root, ["diff", "--name-only", to_ref])
        else:
            diff = _git(root, ["diff", "--name-only", from_ref, to_ref])
        names.update(ln.strip() for ln in (diff.stdout or "").splitlines() if ln.strip())
    else:
        cmds = (
            ["diff", "--name-only", "HEAD"],
            ["diff", "--cached", "--name-only"],
        )
        if not tracked_only:
            cmds = cmds + (["ls-files", "--others", "--exclude-standard"],)
        for args in cmds:
            proc = _git(root, args)
            names.update(ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip())
    out: List[Path] = []
    for n in sorted(names):
        p = root / n
        if p.is_file():
            out.append(p)
    return out


def dash_errors(paths: Iterable[Path]) -> List[str]:
    errs: List[str] = []
    for p in paths:
        if p.suffix.lower() not in PROSE_SUFFIX:
            continue
        if p.name in DASH_ALLOW:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if any(ch in text for ch in DASH_CHARS):
            errs.append("{0}: decorative em/en dash".format(p))
    return errs


def skip_path_errors(paths: Iterable[Path]) -> List[str]:
    errs: List[str] = []
    for p in paths:
        if p.suffix.lower() != ".html":
            continue
        try:
            html = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for e in skip_landing_errors(html):
            errs.append("{0}: {1}".format(p, e))
    return errs


def viewport_errors(root: Path, paths: Iterable[Path]) -> List[str]:
    ui = [p for p in paths if p.suffix.lower() in UI_SUFFIX]
    if not ui:
        return []
    vs = root / "viewer" / "scripts" / "viewport_sanity.py"
    if not vs.is_file():
        return []
    proc = subprocess.run(
        [sys.executable, str(vs)],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []
    tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
    return [
        "viewport_sanity exit {0}: {1}".format(
            proc.returncode, " | ".join(tail[-5:]) or "no output"
        )
    ]


def _gate(name: str, errs: List[str], *, skipped: bool = False, detail: str = "") -> Dict[str, Any]:
    rec: Dict[str, Any] = {"name": name, "ok": not errs, "detail": detail or "; ".join(errs)}
    if skipped:
        rec["skipped"] = True
        rec["ok"] = True
    return rec


def log_path() -> Path:
    env = os.environ.get("VBD_GATE_LOG", "").strip()
    if env:
        return Path(os.path.expanduser(env))
    return Path.home() / ".grok" / "logs" / "vbd_gate.jsonl"


def git_head(root: Path) -> Optional[str]:
    proc = _git(root, ["rev-parse", "HEAD"])
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip() or None


def append_log(record: Dict[str, Any]) -> None:
    """Best-effort. A full disk must not change the gate result."""
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    except OSError as exc:
        print("vbd_gate: log write failed: {0}".format(exc), file=sys.stderr)


def emit_log(
    *,
    event: str,
    root: Path,
    errs: List[str],
    gates: List[Dict[str, Any]],
    promoted: Optional[str] = None,
) -> None:
    append_log(
        {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": event,
            "cwd": str(root),
            "ok": not errs,
            "gates": gates,
            "promoted": promoted,
            "git_head": git_head(root) if is_git(root) else None,
        }
    )


def run_checks(
    root: Path,
    *,
    from_ref: Optional[str] = None,
    to_ref: Optional[str] = None,
    do_fetch: bool = True,
    tracked_only: bool = False,
    skip_if_clean: bool = False,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    gates: List[Dict[str, Any]] = []
    errs: List[str] = []
    if not is_git(root):
        gates.append(_gate("git", [], skipped=True, detail="not a git repo"))
        return errs, gates
    paths = changed_paths(
        root, from_ref=from_ref, to_ref=to_ref, tracked_only=tracked_only
    )
    if skip_if_clean and not paths:
        gates.append(_gate("skip_if_clean", [], skipped=True, detail="no changed files"))
        return errs, gates
    if do_fetch:
        fe = git_fetch(root)
        if fe:
            gates.append(_gate("fetch", [fe]))
            return [fe], gates
        gates.append(_gate("fetch", []))
        oa = origin_ahead_errors(root)
        gates.append(_gate("origin_ahead", oa))
        errs.extend(oa)
    else:
        gates.append(_gate("fetch", [], skipped=True, detail="not requested"))
    de = dash_errors(paths)
    gates.append(_gate("dashes", de))
    errs.extend(de)
    se = skip_path_errors(paths)
    gates.append(_gate("skip_landing", se))
    errs.extend(se)
    ve = viewport_errors(root, paths)
    ui = [p for p in paths if p.suffix.lower() in UI_SUFFIX]
    vs = root / "viewer" / "scripts" / "viewport_sanity.py"
    if not ui:
        gates.append(_gate("viewport_sanity", [], skipped=True, detail="no html/css in change set"))
    elif not vs.is_file():
        gates.append(_gate("viewport_sanity", [], skipped=True, detail="no viewer/scripts/viewport_sanity.py"))
    else:
        gates.append(_gate("viewport_sanity", ve))
        errs.extend(ve)
    return errs, gates


def hook_script(gate_path: Path) -> str:
    return (
        "#!/bin/sh\n"
        "# {0}\n"
        "set -e\n"
        "GATE=\"${{VBD_GATE:-{1}}}\"\n"
        "if [ ! -f \"$GATE\" ]; then\n"
        "  echo \"vbd_gate: missing $GATE\" >&2\n"
        "  exit 2\n"
        "fi\n"
        "exec python3 \"$GATE\" hook-run --app-root \"$(git rev-parse --show-toplevel)\"\n"
    ).format(HOOK_MARK, gate_path)


def hook_install(root: Path) -> None:
    hook_dir = root / ".git" / "hooks"
    if not hook_dir.is_dir():
        # gitdir file (worktree) or missing
        gitdir = _git(root, ["rev-parse", "--git-path", "hooks"])
        if gitdir.returncode != 0:
            raise SystemExit("hook-install: not a git repo: {0}".format(root))
        hook_dir = Path(gitdir.stdout.strip())
        if not hook_dir.is_absolute():
            hook_dir = root / hook_dir
        hook_dir.mkdir(parents=True, exist_ok=True)
    path = hook_dir / "pre-push"
    body = hook_script(PACK_ROOT / "vbd_gate.py")
    if path.is_file():
        old = path.read_text(encoding="utf-8")
        if HOOK_MARK not in old and old.strip():
            raise SystemExit(
                "hook-install: {0} exists and is not a VBD hook; "
                "leave it (finish-later). Install by hand if you want both.".format(path)
            )
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("installed {0}".format(path))


def grok_hook_install() -> None:
    dest_dir = Path.home() / ".grok" / "hooks"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "vbd-stop.json"
    stop_py = PACK_ROOT / "vbd_stop_hook.py"
    cmd = "{0} {1}".format(sys.executable, stop_py)
    payload = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": cmd,
                            "timeout": 90,
                        }
                    ]
                }
            ]
        }
    }
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("installed {0}".format(dest))


def parse_hook_refs(text: str) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        local_sha, remote_sha = parts[1], parts[3]
        pairs.append((remote_sha, local_sha))
    return pairs


def cmd_check(args: argparse.Namespace) -> int:
    root = args.app_root.resolve()
    print("=== vbd_gate check {0} ===".format(root))
    errs, gates = run_checks(
        root,
        tracked_only=bool(getattr(args, "tracked_only", False)),
        skip_if_clean=bool(getattr(args, "skip_if_clean", False)),
    )
    promoted: Optional[str] = None
    event = "check"
    if args.claim_done:
        event = "claim-done"
        if not (args.promoted or args.not_promoted):
            msg = (
                "--claim-done requires --promoted <lesson> or "
                "--not-promoted <why> (unique to this product / already in LESSONS.md)"
            )
            errs.append(msg)
            gates.append(_gate("claim_done", [msg]))
        elif args.promoted:
            promoted = args.promoted
            print("  promoted: {0}".format(args.promoted))
            gates.append(_gate("claim_done", []))
        else:
            promoted = "not promoted: {0}".format(args.not_promoted)
            print("  not promoted: {0}".format(args.not_promoted))
            gates.append(_gate("claim_done", []))
    emit_log(event=event, root=root, errs=errs, gates=gates, promoted=promoted)
    if errs:
        for e in errs:
            print("  [FAIL] {0}".format(e))
        return 2
    print("vbd_gate: PASS")
    return 0


def cmd_hook_run(args: argparse.Namespace) -> int:
    root = args.app_root.resolve()
    stdin = sys.stdin.read() if not sys.stdin.isatty() else ""
    pairs = parse_hook_refs(stdin)
    print("=== vbd_gate pre-push {0} ===".format(root))
    errs: List[str] = []
    gates: List[Dict[str, Any]] = []
    fe = git_fetch(root)
    if fe:
        gates.append(_gate("fetch", [fe]))
        emit_log(event="pre-push", root=root, errs=[fe], gates=gates)
        print("  [FAIL] {0}".format(fe))
        return 2
    gates.append(_gate("fetch", []))
    oa = origin_ahead_errors(root)
    gates.append(_gate("origin_ahead", oa))
    errs.extend(oa)
    if pairs:
        for remote_sha, local_sha in pairs:
            if local_sha == "0" * 40:
                continue
            more, more_gates = run_checks(
                root, from_ref=remote_sha, to_ref=local_sha, do_fetch=False
            )
            errs.extend(more)
            gates.extend(more_gates)
    else:
        more, more_gates = run_checks(root, do_fetch=False)
        errs.extend(more)
        gates.extend(more_gates)
    emit_log(event="pre-push", root=root, errs=errs, gates=gates)
    if errs:
        for e in errs:
            print("  [FAIL] {0}".format(e))
        print("vbd_gate: push blocked. Fix the gates (or do not claim done).")
        return 2
    print("vbd_gate: PASS")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd")

    def with_root(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--app-root", type=Path, default=Path("."))

    c = sub.add_parser("check", help="Run gates on the working tree")
    with_root(c)
    c.add_argument("--claim-done", action="store_true")
    c.add_argument("--promoted", default="")
    c.add_argument("--not-promoted", default="")
    c.add_argument(
        "--tracked-only",
        action="store_true",
        help="Ignore untracked files (Stop hook: finish-later dirt must not block Q&A)",
    )
    c.add_argument(
        "--skip-if-clean",
        action="store_true",
        help="Pass immediately when there are no changed files to gate",
    )
    h = sub.add_parser("hook-install", help="Install a pre-push hook in --app-root")
    with_root(h)
    sub.add_parser("grok-hook-install", help="Install the Grok Stop hook under ~/.grok/hooks")
    r = sub.add_parser("hook-run", help="Invoked by the pre-push hook")
    with_root(r)
    args = p.parse_args(argv)
    cmd = args.cmd or "check"
    if not hasattr(args, "app_root"):
        args.app_root = Path(".")
    if cmd == "check" and not hasattr(args, "claim_done"):
        args.claim_done = False
        args.promoted = ""
        args.not_promoted = ""
        args.tracked_only = False
        args.skip_if_clean = False
    if cmd == "hook-install":
        hook_install(args.app_root.resolve())
        return 0
    if cmd == "grok-hook-install":
        grok_hook_install()
        return 0
    if cmd == "hook-run":
        return cmd_hook_run(args)
    return cmd_check(args)


if __name__ == "__main__":
    raise SystemExit(main())
