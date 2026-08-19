# Copyright (c) 2026 Martial Systems LLC. MIT.
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from vbd_gate import (  # noqa: E402
    dash_errors,
    is_vbd_pack,
    log_path,
    main,
    publish_vbd_to_graphforge,
    skip_landing_errors,
)


@pytest.fixture(autouse=True)
def _isolate_vbd_log(tmp_path, monkeypatch):
    monkeypatch.setenv("VBD_GATE_LOG", str(tmp_path / "vbd_gate.jsonl"))


def test_skip_panel_containing_chart_fails():
    html = """
    <a class="skip-juicy" href="#panel">skip</a>
    <section id="panel" class="panel">
      <div class="chart-wrap" id="chart"></div>
    </section>
    """
    errs = skip_landing_errors(html)
    assert errs
    assert any("visual target" in e for e in errs)


def test_skip_direct_to_chart_ok():
    html = """
    <a class="skip-juicy" href="#chart">skip</a>
    <section id="panel" class="panel">
      <div class="chart-wrap" id="chart"></div>
    </section>
    """
    assert skip_landing_errors(html) == []


def test_no_skip_control_ok():
    assert skip_landing_errors("<p>no skip</p>") == []


def test_skip_evaluates_every_hash_not_only_first():
    html = """
    <a class="skip-juicy" href="#chart">skip chart</a>
    <a class="skip-juicy" href="#panel">skip panel</a>
    <section id="panel" class="panel">
      <div class="chart-wrap" id="chart"></div>
    </section>
    """
    errs = skip_landing_errors(html)
    assert errs
    assert any("#panel" in e for e in errs)
    assert not any("#chart" in e for e in errs)


def test_skip_two_panels_both_fail():
    html = """
    <a class="skip-juicy" href="#panel-a">a</a>
    <a class="skip-juicy" href="#panel-b">b</a>
    <section id="panel-a"><div class="chart-wrap" id="chart-a"></div></section>
    <section id="panel-b"><div class="chart-wrap" id="chart-b"></div></section>
    """
    errs = skip_landing_errors(html)
    assert len(errs) == 2
    assert any("#panel-a" in e for e in errs)
    assert any("#panel-b" in e for e in errs)


def test_dash_errors_on_md(tmp_path: Path):
    p = tmp_path / "NOTE.md"
    p.write_text("Channels — named slots\n", encoding="utf-8")
    errs = dash_errors([p])
    assert errs
    p.write_text("Channels: named slots\n", encoding="utf-8")
    assert dash_errors([p]) == []


def test_dash_scan_only_added_lines(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "HOWTO.md").write_text("Old — historical dash\n", encoding="utf-8")
    _git(tmp_path, "add", "HOWTO.md")
    _git(tmp_path, "commit", "-m", "init")
    (tmp_path / "HOWTO.md").write_text("Old — historical dash\nNew: colon line\n", encoding="utf-8")
    assert dash_errors([tmp_path / "HOWTO.md"], root=tmp_path) == []
    (tmp_path / "HOWTO.md").write_text("Old — historical dash\nNew — also bad\n", encoding="utf-8")
    assert dash_errors([tmp_path / "HOWTO.md"], root=tmp_path)


def test_claim_done_requires_promote_flag(tmp_path: Path):
    rc = main(["check", "--app-root", str(tmp_path), "--claim-done"])
    assert rc == 2


def _git(cwd: Path, *args: str) -> None:
    subprocess.check_call(["git", *args], cwd=str(cwd), stdout=subprocess.DEVNULL)


def test_check_clean_git_repo(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("Hello: world\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    rc = main(
        [
            "check",
            "--app-root",
            str(tmp_path),
            "--claim-done",
            "--not-promoted",
            "unique to this fixture",
        ]
    )
    assert rc == 0


def test_skip_if_clean_ignores_untracked_dash(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("Hello: world\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    (tmp_path / "WIP.md").write_text("Channels — later\n", encoding="utf-8")
    rc = main(
        ["check", "--app-root", str(tmp_path), "--tracked-only", "--skip-if-clean"]
    )
    assert rc == 0


def test_stop_hook_allows_clean_turn(tmp_path: Path):
    import json
    from vbd_stop_hook import main as stop_main

    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("Hello: world\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    payload = json.dumps({"reason": "end_turn", "cwd": str(tmp_path), "workspaceRoot": str(tmp_path)})
    import io

    old = sys.stdin
    try:
        sys.stdin = io.StringIO(payload)
        assert stop_main() == 0
    finally:
        sys.stdin = old


def test_check_fails_new_html_skip_panel(tmp_path: Path):
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    (tmp_path / "board.html").write_text(
        '<a class="skip-juicy" href="#panel">s</a>'
        '<section id="panel"><div class="chart-wrap" id="g"></div></section>\n',
        encoding="utf-8",
    )
    rc = main(["check", "--app-root", str(tmp_path)])
    assert rc == 2


def test_log_writes_pass_and_fail(tmp_path, monkeypatch):
    log = tmp_path / "steps.jsonl"
    monkeypatch.setenv("VBD_GATE_LOG", str(log))
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("Hello: world\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "init")
    assert (
        main(
            [
                "check",
                "--app-root",
                str(tmp_path),
                "--claim-done",
                "--not-promoted",
                "fixture",
            ]
        )
        == 0
    )
    (tmp_path / "NOTE.md").write_text("Channels — named\n", encoding="utf-8")
    assert main(["check", "--app-root", str(tmp_path)]) == 2
    recs = [json.loads(ln) for ln in log.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(recs) == 2
    assert recs[0]["ok"] is True
    assert recs[0]["event"] == "claim-done"
    assert recs[1]["ok"] is False
    assert recs[1]["event"] == "check"
    names = [g["name"] for g in recs[1]["gates"]]
    assert "dashes" in names
    assert log_path() == log


def test_is_vbd_pack_on_this_repo():
    assert is_vbd_pack(ROOT)
    assert not is_vbd_pack(Path("/tmp"))


def test_publish_gf_skipped_by_env(monkeypatch):
    monkeypatch.setenv("VBD_SKIP_GF_PUBLISH", "1")
    assert publish_vbd_to_graphforge(ROOT) == "skipped"
