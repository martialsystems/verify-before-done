# Copyright (c) 2026 Martial Systems LLC. MIT License, see LICENSE.
import subprocess

import pytest

from upgrade_audit.github import GitHubError, clone_repo


def fake(results):
    calls = []

    def run(cmd, **_kw):
        calls.append(list(cmd))
        r = results[len(calls) - 1]
        if isinstance(r, Exception):
            raise r
        return subprocess.CompletedProcess(cmd, r, "", "err" if r else "")
    return run, calls


def test_gh_success_no_fallback():
    run, calls = fake([0])
    clone_repo("o/r", "/d", runner=run)
    assert calls == [["gh", "repo", "clone", "o/r", "/d"]]


def test_gh_signed_out_falls_back_to_git_https():
    """Bug 4: public repos must clone without gh auth."""
    run, calls = fake([1, 0])
    clone_repo("o/r", "/d", runner=run)
    assert calls[1] == ["git", "clone", "https://github.com/o/r.git", "/d"]


def test_gh_missing_falls_back():
    run, calls = fake([FileNotFoundError("gh"), 0])
    clone_repo("o/r", "/d", runner=run)
    assert calls[1][0] == "git"


def test_both_fail_reports_both():
    run, _ = fake([1, 128])
    with pytest.raises(GitHubError) as e:
        clone_repo("o/r", "/d", runner=run)
    assert "gh:" in str(e.value) and "git:" in str(e.value)
