# Verify Before Done

Instructions for coding assistants: check every path that can touch a change before reporting that the work is finished.

Copyright (c) 2026 Martial Systems LLC. MIT license — see [LICENSE](./LICENSE).

<p align="right">
  <a href="https://ko-fi.com/martialgames"><img src="https://img.shields.io/badge/Donate-Ko--fi-ff5e5b?style=flat-square&logo=ko-fi&logoColor=white" alt="Donate on Ko-fi" /></a>
  &nbsp;
  <a href="https://martialgames.net/"><img src="https://img.shields.io/badge/Martial%20Games-site-1a3a2a?style=flat-square" alt="Martial Games" /></a>
</p>

---

## Purpose

Assistants often change one code path, confirm that path works, and report success while another entry point, deploy step, cache, or mirrored file still behaves the old way.

This repository is a short set of rules you attach to a project or chat so the assistant:

1. Lists every path that can hit the change  
2. Checks each of them  
3. Fixes gaps and rechecks  
4. Reports only after that  

There is nothing to install. Copy a markdown file into your tools.

---

## Quick start

| Tooling | File to use |
|---------|-------------|
| Blank chat | [PASTE_BLOCK.txt](./PASTE_BLOCK.txt) |
| Limited instruction space | [VERIFY_BEFORE_DONE.short.md](./VERIFY_BEFORE_DONE.short.md) |
| Full project rules | [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) |
| Cursor project rules | [.cursor-rules-example.mdc](./.cursor-rules-example.mdc) → `.cursor/rules/verify-before-done.mdc` |
| Skills-compatible tools | [SKILL.md](./SKILL.md) |
| Repo-level agent file | [AGENTS.md.drop-in](./AGENTS.md.drop-in) → `AGENTS.md` |

Session line (optional):

> Follow Verify Before Done. Do not report finished work without the report section.

---

## Required process

```text
implement → list interaction paths → check each path → fix failures → recheck all paths → report
```

Do not report “fixed”, “done”, or “try it” after checking only the path you just edited.

Every completion report must include:

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

---

## Repository layout

| File | Role |
|------|------|
| [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) | Full rule set |
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

These rules were written after failures where continuous integration and a primary path looked correct while a second publisher, mirror file, or cached asset still served old results. The interaction map and residual-risk line are meant to make that class of miss explicit.

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
