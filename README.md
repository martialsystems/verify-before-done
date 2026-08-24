<p align="center">
  <img src="icons/icon128.png" width="96" height="96" alt="Verify Before Done" />
</p>

# Verify Before Done

Current system (research register, 2026-08-24): [SYSTEM.md](./SYSTEM.md).

Instructions for coding assistants: apply a high quality bar, check every path that can touch a change, pass over new work with the same rules, and fix bugs before reporting that the work is finished. Agents default to the fastest plausible stop. Polite phrasing ("please test your code") is not enough. VBD is two layers: structural report rules in the always-on prompt, and a harness that actually runs named commands when the repo opts in.

Copyright (c) 2026 Martial Systems LLC. MIT license: see [LICENSE](./LICENSE).

<p align="right">
  <a href="https://ko-fi.com/martialgames"><img src="https://img.shields.io/badge/Donate-Ko--fi-ff5e5b?style=flat-square&logo=ko-fi&logoColor=white" alt="Donate on Ko-fi" /></a>
  &nbsp;
  <a href="https://martialgames.net/"><img src="https://img.shields.io/badge/Martial%20Games-site-1a3a2a?style=flat-square" alt="Martial Games" /></a>
</p>

---

## Purpose

Assistants often change one code path, confirm that path works, and report success while another entry point, deploy step, cache, or mirrored file still behaves the old way. They also ship junior-default code, AI-polished PDF prose, decorative em dashes in docs, dash-to-colon splices that no longer parse, or a first draft with no second pass.

This repository is a short set of rules you attach to a project or chat so the assistant:

1. Builds to the quality defaults (code and PDFs)  
2. Fetches git before editing; pulls if origin is ahead and clean; if dirty+ahead, stash, commit, or report both (never discard); treats dirty local with no new remote as finish-later  
3. Lists every path that can hit the change (for UI: phone-width 390x844 and desktop ~1280, via a named command)  
4. Checks each of them  
5. Promotes general lessons to this pack (`LESSONS.md`) so the next project inherits them; skips when the lesson is unique to this product  
6. After creating something, re-passes with the same rules and fixes bugs  
7. Pushes completed work (or says why not)  
8. Reports only after that; `vbd_gate.py check --claim-done` must have passed  

You do not run this by hand before closing a chat. Grok's **Stop** hook runs
`vbd_gate` when the agent tries to finish a turn. Git **pre-push** runs it if
the chat never claimed done. Install once:

```bash
python3 vbd_gate.py grok-hook-install
python3 vbd_gate.py hook-install --app-root ~/your_product
```

Manual (agents, or you if you want):

```bash
python3 vbd_gate.py check --app-root ~/your_product --claim-done --not-promoted 'unique to this product'
```

`vbd_gate` fetches, refuses origin-ahead+dirty (does not discard), scans changed docs for decorative dashes, and fails a skip jump that lands on a panel instead of the chart. Pre-push runs the same gates so a forgotten check blocks the push. This pack does **not** install a pre-commit hook: finish-later commits stay allowed.

If the repo has [`vbd.runtime.json`](./vbd.runtime.json), `--claim-done` and pre-push also **execute** those argv commands (cwd is the repo, no shell). Optional `paths` globs: skip that command when the change set does not match. Missing file skips. Isolated unit tests, JSON-shape checks, and source-list counts are indirect verification, not verification of the production path. Name the exact execution tool or script in the report.

Product opt-in (do not copy this pack's pytest line unless that *is* the production path):

```json
{
  "runtime_checks": [
    {
      "id": "import-pipeline",
      "argv": ["python3", "scripts/test_import_e2e.py"],
      "timeout_s": 120,
      "paths": ["src/**", "scripts/**", "tests/**", "vbd.runtime.json"]
    }
  ]
}
```

Each run appends one JSON line to `~/.grok/logs/vbd_gate.jsonl` (override `VBD_GATE_LOG`). That is command evidence (fetch, dashes, skip, viewport), not the interaction-map essay.

```bash
tail -n 20 ~/.grok/logs/vbd_gate.jsonl
```

**Hardwiring into all chats:** put the short rule or [PASTE_BLOCK.txt](./PASTE_BLOCK.txt) into your tool’s always-on instructions (custom instructions, user rules, project rules with always-apply, or a root [AGENTS.md](./AGENTS.md.drop-in)). That way every new chat inherits the process without re-pasting. This is still a rule the host injects, not a plugin: the model can ignore it, but most tools will load it on every session once it is set there.

---

## Quality defaults

| Surface | Default (override only if the user asks) |
|---------|------------------------------------------|
| **Code** | Top software architect with a PhD in CS: clear design, precise implementation, right structure over quick hacks |
| **PDFs** | PhD / research-level register; no AI polishing (no fluff, marketing gloss, or generic LLM prose) |
| **Prose / docs** | Lists use colons; em dashes only for ironic cut-off/swerve (not for asides or polished rhythm). Do not glob-replace dashes with colons or hyphens; rewrite so the sentence still parses. |
| **After create** | Same-rules sanity pass; fix defects; re-pass until clean (or residual risk is explicit) |

---

## Quick start

| Tooling | File to use |
|---------|-------------|
| Blank chat | [PASTE_BLOCK.txt](./PASTE_BLOCK.txt) |
| Limited instruction space | [VERIFY_BEFORE_DONE.short.md](./VERIFY_BEFORE_DONE.short.md) |
| Full project rules | [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) |
| Punctuation (colons; no glob-replaced dashes) | [punctuation-lists.md](./punctuation-lists.md) |
| Cross-project lessons | [LESSONS.md](./LESSONS.md) |
| Cursor project rules | [.cursor-rules-example.mdc](./.cursor-rules-example.mdc) → `.cursor/rules/verify-before-done.mdc` |
| Skills-compatible tools | [SKILL.md](./SKILL.md) |
| Repo-level agent file | [AGENTS.md.drop-in](./AGENTS.md.drop-in) → `AGENTS.md` |
| Forgettable gates | [vbd_gate.py](./vbd_gate.py) / `bin/vbd` |
| Production-path argv (opt-in) | [vbd.runtime.json](./vbd.runtime.json) |

### Weak prompt vs VBD

| Area | Generic prompt | VBD |
|------|----------------|-----|
| Validation | "Make sure it works." | Named production path, exact execution command |
| Execution | Isolated unit test or JSON shape | Declared argv on `--claim-done` and pre-push when `vbd.runtime.json` exists |
| Edge cases | Ignored unless asked | Map includes merge/dedupe and time/state batching |
| Completion | "I fixed it, try it." | Report block with exact tool/script, Git, Promoted |

Session line (optional):

> Follow Verify Before Done (quality defaults + interaction paths). Do not report finished work without the report section. Indirect verification is not verification.

---

## Required process

```text
fetch git (pull if origin ahead and clean; dirty+ahead: stash/commit/report both; finish-later if dirty and not ahead)
  → implement at quality bar → list interaction paths → check each path
  → same-rules sanity pass on new work → fix failures → recheck all paths
  → push or say why not → report
```

Do not report “fixed”, “done”, or “try it” after checking only the path you just edited.  
Do not skip the second pass after creating something.

Every completion report must include:

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → exact execution tool/script → pass/fail)
- Bugs found in verify pass:
- Git:
- Promoted: <lesson → LESSONS.md / pack> | not promoted: <why>
- Residual risks:
```

---

## Repository layout

| File | Role |
|------|------|
| [SYSTEM.md](./SYSTEM.md) | Research-register description of the pack as implemented (2026-08-24) |
| [vbd.runtime.json](./vbd.runtime.json) | Opt-in argv list: `--claim-done` and pre-push execute these |
| [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) | Full rule set (quality defaults + verify process) |
| [punctuation-lists.md](./punctuation-lists.md) | Standalone punctuation law: classify each dash, rewrite so the sentence still parses |
| [VERIFY_BEFORE_DONE.short.md](./VERIFY_BEFORE_DONE.short.md) | Condensed rule set |
| [PASTE_BLOCK.txt](./PASTE_BLOCK.txt) | Single paste for a new chat |
| [SKILL.md](./SKILL.md) | Skill-format entry |
| [AGENTS.md.drop-in](./AGENTS.md.drop-in) | Drop-in for `AGENTS.md` |
| [.cursor-rules-example.mdc](./.cursor-rules-example.mdc) | Cursor rule example |

### Claude

Project instructions or custom instructions: short or full markdown.  
Skills: place `SKILL.md` under a `verify-before-done` skills directory.

### Cursor

Project Rules with `alwaysApply: true`, or user rules with the short file.

### ChatGPT / Codex / similar

Custom instructions: short file.  
Workspace: full file or `AGENTS.md`.

---

## Background

These rules were written after failures where continuous integration and a primary path looked correct while a second publisher, mirror file, or cached asset still served old results. The interaction map and residual-risk line are meant to make that class of miss explicit. Quality defaults and the create → re-pass loop address the related failure mode: acceptable-looking first drafts that never meet a real bar or get a bug-fix pass.

---

## License

| | |
|---|---|
| License | [MIT](./LICENSE) |
| Copyright | © 2026 Martial Systems LLC |
| Notice | [NOTICE](./NOTICE) |

Forks and reuse of the text are allowed under MIT. Do not present a fork as an official Martial Systems product without permission.

---

<p align="right">
  <sub>
    Support (optional):
    <a href="https://ko-fi.com/martialgames">Ko-fi</a>
    ·
    <a href="https://martialgames.net/">martialgames.net</a>
  </sub>
</p>
