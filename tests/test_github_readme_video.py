# Copyright (c) 2026 Martial Systems LLC. MIT.
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from github_readme_video import (  # noqa: E402
    ATTACH_MIN,
    GhError,
    attach_help_has_flag,
    parse_embed_url,
    parse_gh_version,
    parse_issue_number,
)


def test_parse_embed_url_from_comment_body():
    body = (
        "README demo video attachment.\n\n"
        "https://github.com/user-attachments/assets/796cd394-dda2-4fa0-9cc7-15c19465914b"
    )
    assert parse_embed_url(body) == (
        "https://github.com/user-attachments/assets/796cd394-dda2-4fa0-9cc7-15c19465914b"
    )


def test_parse_embed_url_ignores_html_video_tag():
    html = '<video src="docs/demo.mp4" controls></video>'
    assert parse_embed_url(html) is None


def test_parse_gh_version_and_old_brew():
    assert parse_gh_version("gh version 2.100.0 (2026-01-01)\n") == (2, 100, 0)
    assert parse_gh_version("gh version 2.96.0 (2025-12-01)\n") < ATTACH_MIN
    with pytest.raises(GhError):
        parse_gh_version("not a version string")


def test_attach_help_flag():
    assert attach_help_has_flag("  --attach string   Upload a file\n")
    assert not attach_help_has_flag("  --body string\n")


def test_parse_issue_number():
    assert parse_issue_number(
        "https://github.com/martialsystems/amadeus-overlay/issues/1\n"
    ) == 1
    with pytest.raises(GhError):
        parse_issue_number("created")
