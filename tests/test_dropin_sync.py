# Copyright (c) 2026 Martial Systems LLC. MIT.
"""Fail closed if a drop-in omits the laws the short surfaces must share."""

from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

SURFACES = (
    "VERIFY_BEFORE_DONE.md",
    "VERIFY_BEFORE_DONE.short.md",
    "AGENTS.md.drop-in",
    "SKILL.md",
    "PASTE_BLOCK.txt",
    ".cursor-rules-example.mdc",
)

REQUIRED = (
    "ahead and the tree is dirty",
    "force-push",
    "Missing source",
    "390x844",
    "promote general lessons",
    "vbd_gate",
    "glob-replace",
    "indirect verification",
    "vbd.runtime.json",
    "exact execution",
)


class DropinSyncTest(unittest.TestCase):
    def test_required_phrases_on_every_surface(self) -> None:
        missing = []
        for name in SURFACES:
            text = (ROOT / name).read_text(encoding="utf-8").lower()
            for phrase in REQUIRED:
                if phrase.lower() not in text:
                    missing.append("{0}: missing {1!r}".format(name, phrase))
        self.assertEqual(missing, [])

    def test_no_decorative_dashes_on_dropins(self) -> None:
        # VERIFY_BEFORE_DONE.md and punctuation-lists.md contain intentional
        # em-dash examples and are DASH_ALLOW in vbd_gate.
        dropins = (
            "VERIFY_BEFORE_DONE.short.md",
            "AGENTS.md.drop-in",
            "SKILL.md",
            "PASTE_BLOCK.txt",
            ".cursor-rules-example.mdc",
            "README.md",
            "LESSONS.md",
            "SYSTEM.md",
        )
        offenders = []
        for name in dropins:
            text = (ROOT / name).read_text(encoding="utf-8")
            if "\u2014" in text or "\u2013" in text:
                offenders.append(name)
        self.assertEqual(offenders, [])

    def test_lessons_catalog_has_phone_width(self) -> None:
        text = (ROOT / "LESSONS.md").read_text(encoding="utf-8").lower()
        self.assertIn("390x844", text)
        self.assertIn("skip when", text)
        self.assertIn("promote", text)

    def test_dash_replacement_grammar_in_full_law(self) -> None:
        needles = (
            "do not glob-replace",
            "the pipeline: which is already complex: needs gates",
            "still parse",
            "colon is not a universal substitute",
        )
        for name in ("VERIFY_BEFORE_DONE.md", "punctuation-lists.md"):
            text = (ROOT / name).read_text(encoding="utf-8").lower()
            for needle in needles:
                self.assertIn(needle, text, msg="{0} missing {1!r}".format(name, needle))

    def test_punctuation_lists_is_dash_allow(self) -> None:
        text = (ROOT / "vbd_gate.py").read_text(encoding="utf-8")
        self.assertIn('"punctuation-lists.md"', text)
        self.assertIn('"VERIFY_BEFORE_DONE.md"', text)


if __name__ == "__main__":
    unittest.main()
