---
name: Verify before done
description: >-
  Use before telling the user any task is done, fixed, sent, shipped, built,
  saved, or ready to try, and at the start of any edit to a git tree (fetch
  before edit). Verify Before Done for Grok Bot: map every interaction path,
  check each one with a real tool (Read back, build and test, WebFetch links,
  desktop screenshot, send ids, re-read routines and memory), apply the quality
  defaults, run vbd_gate.py on the box when the pack is present, and report the
  true state with the Verify-before-done report. Also covers upgrade audit mode:
  when the user asks to audit their repos after a model upgrade, spawn auditor
  and verifier subagents, drive the pack's upgrade-audit walk-step from Shell,
  and write the PDF, read-only unless the user approves more.
---
# Verify before done (Grok Bot edition)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

Do not report success until this process is complete. In Grok Bot this is an
instruction-level rule: no Stop hook or pre-push hook fires for you. The only
enforceable step is running `vbd_gate.py` yourself from Shell (section 5).

## 1. Quality defaults

Override only when the user asks for a sketch, prototype, or lower bar.

- **Code:** top software architect with a PhD in CS: clear boundaries, right structure over a quick patch.
- **PDFs:** PhD / research-level register; no AI polishing. Date new or rewritten sections.
- **Prose / docs / messages you write:** lists use colons; em dashes only for ironic cut-off/swerve. Do not glob-replace dashes with colons or hyphens; rewrite so the sentence still parses. Write from the data we have; no `What it is not` section except legal/T&C.
- **After create:** same-rules second pass; fix bugs; re-pass until clean (or residual risk is explicit).

## 2. Git first (any git tree on the box or a user machine)

Fetch before editing. If origin is ahead and the tree is clean, pull before
editing. If origin is ahead and the tree is dirty: stash, commit, or report
both; never discard or `reset --hard` to take the pull. If origin is not ahead
and the tree is already edited: finish-later, do not discard. Never force-push
unless the user ordered it. Push completed work only when the user asked for
the push (pushing is externally visible; get approval). If you do not push, the
Git line says why.

## 3. Interaction map

Before checking, list every path that can still show the old or wrong result:
entry points, modes and toggles, empty and error states, fallbacks, caches,
mirrored files and copies (box vs user machine, bundled snapshots, skill
copies), deploys, side effects, id assignment / merge / dedupe, time/state
batching (N>1 items in one tick), prose surfaces, and git. For UI, layout, nav,
or in-page jumps: phone-width (390x844) and desktop (~1280) via a named
command or a sized screenshot, not a thought. Every `.skip-juicy` hash jump
must land the visual target, not a tall panel. At the start of implement or UI
work, apply every matching `LESSONS.md` row unless its Skip when matches.

## 4. Check each path with a real tool

Indirect verification is not verification: isolated unit tests, JSON-shape
checks, and source-list counts do not prove the production path. Name the
exact execution tool or script on the Verified line.

| Surface | Bot check |
|---------|-----------|
| Files, docs | `Read` the file back: exists, not truncated, every requested section present. Docs: scan added lines for decorative em dashes and en dashes. |
| PDFs | `pdftotext` and read it; render a page and look at it for layout. |
| Code | Build and run the tests or a smoke run of the production path in Shell. If the repo has `vbd.runtime.json`, run its argv commands (or `--claim-done`, section 5). Check the diff matches the ask; check CI if there is a PR. |
| Links and facts | `WebFetch` every link you report; drop or fix dead ones. Trace each claim to a source. A blocked fetch is not a dead page: retry with curl or the browser. |
| Browser surfaces (site, extension, board, GitHub Pages) | A real browser click-through in the desktop browser (desktop subagent), with the browser and URL named, plus a screenshot at 390x844 and ~1280 for layout changes. Headless Chrome dumps and CDP screenshots are not that click-through. GitHub depends: a source-only git push is not a browser surface. |
| Emails, messages, posts | Confirm the send tool returned an id, then read the sent item or thread. Name the real sender. A draft is reported as drafted. |
| Routines, memory, skills, settings | Re-read the saved item and confirm fields, schedule, and enabled state. |
| Subagent or cloud agent results | A lead, not proof: open the file, hit the URL, or rerun one test before relaying. |
| Deploys | Do not overwrite newer artifacts with older ones. Missing source keeps dest. Green CI does not prove the public surface is current. |

## 5. Enforceable gate on the box

When the box has the pack (`~/agent_laws_verify_before_done/vbd_gate.py`, else
`~/graphforge/bundled/verify-before-done/vbd_gate.py`) and the work is in a git
tree, run before claiming done:

```bash
python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root <repo> --claim-done --not-promoted '<why>'
```

Use `--promoted '<lesson -> LESSONS.md>'` instead when you promoted a lesson.
This runs fetch, origin-ahead, dashes, skip-landing, the viewport script when
present, and `vbd.runtime.json` commands. A failing gate means not done. For a
repo on a user machine, run it there with that machine's Shell only with
local-tool approval; otherwise list it under residual risks.

## 6. Fix or downgrade

On failure, fix and recheck the full map, not only the failed path. If you
cannot fix it, report the actual state (drafted, partial, blocked, unverified)
and what is missing. Never round up. Promote general lessons to the VBD pack
(`LESSONS.md`); do not leave them only in this repo. Skip when the lesson is
unique to this product.

## 7. Report

Say done only when every check passed. Do not claim checks that were not run.
For code, repo, deploy, or docs work, end with:

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path -> exact execution tool/script -> pass/fail)
- Bugs found in verify pass:
- Git: fetched; origin ahead -> pulled <sha> | finish-later <paths> | pushed <ref@sha> | did not push: <reason> | not a git repo
- Promoted: <lesson -> LESSONS.md / pack> | not promoted: <why>
- Residual risks:
```

For small non-code tasks (one email, one saved setting), a single plain line
naming what was checked is enough. Keep checks cheap: the smallest check that
proves the outcome.

## 8. Upgrade audit mode

Use when the user asks for an upgrade audit: re-check shipped logic across
their repos after a new model generation ships. It is this skill applied to
code already shipped. The runner is `~/agent_laws_verify_before_done/audit`
(set `ROOT` to it; `export PATH="$ROOT/bin:$PATH"`). Protocol for every
auditor and verifier: `$ROOT/protocol/AUDIT.md`.

Defaults, unless the user says otherwise for this run:

- Mode `audit`: read-only. No edits to product trees, no branches.
- Kill `stall`: pass `--kill stall` to `walk-step`.
- Never push, open a PR, or merge without the user's explicit approval naming
  that repo. `fix` mode makes a local branch only. `pr` mode stops at a drafted
  PR description and asks; merge is never part of this mode.

Steps:

1. `upgrade-audit doctor`. A `WARN gh` line is fine for audit mode (public
   repos clone over git https). Any `FAIL` stops the run; report it.
2. Catalog: `upgrade-audit inventory --adopt` writes the user's catalog to
   `~/.config/upgrade-audit/repos.yaml`, never into the pack. Show the
   in-scope list and let the user drop rows before walking.
3. `upgrade-audit init-run --from <old> --to <new>` (add `--only <id>` to
   narrow). It prints the run directory and seeds `walk.json`.
4. Loop until `walk_complete` is true:
   - Write a snapshot JSON with `now` in UTC with a `Z` suffix
     (`date -u +%Y-%m-%dT%H:%M:%SZ`), `spawned` (every subagent you launched
     since the last step, with `repo`, `role`, `id`), and `agents` (each live
     subagent id with `status` running, completed, failed, or cancelled, plus
     its latest `output`).
   - Run `upgrade-audit walk-step --run-dir <run> --snapshot <file> --kill stall`.
   - Obey the actions: `collect` (for each repo: `upgrade-audit sync --only
     <id> --out <run>/sync-<id>.json`, then `upgrade-audit collect --repo <id>
     --sync <run>/sync-<id>.json`),
     `spawn` (one subagent per entry, one repo each; auditor gets AUDIT.md and
     the collected `read_path`; verifier gets the auditor report and tries to
     refute each finding), `kill` (stop that subagent), `unverify`, `validate`
     (`upgrade-audit validate <run>/<path>`).
   - Check subagents without blocking on all of them. Do not wait for the
     slowest one; step again as soon as any finishes.
   - A slot you reserved but never launched, or an agent missing from
     snapshots, is released after 10 minutes and retried once. Report every
     `skipped` and `fix_skipped` row.
5. `upgrade-audit pdf --run-dir <run> --from <old> --to <new>`. Verify the
   PDF with `pdftotext` and one rendered page, then send it to the user.
6. Only confirmed findings (second-agent `verifier_evidence`) count. Report
   unverified ones as unverified. The audit report replaces the section 7
   block with: repos walked, skipped with reasons, confirmed findings by
   severity, PDF path, and what (if anything) awaits approval.

`upgrade-audit send-grok` drives the macOS Grok terminal and is hidden on
other platforms; the bot never needs it.

---

<sub>© 2026 Martial Systems LLC · https://ko-fi.com/martialgames</sub>
