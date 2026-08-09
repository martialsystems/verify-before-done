# Verify Before Done

Instructions for coding assistants: apply a high quality bar, check every path that can touch a change, pass over new work with the same rules, and fix bugs before reporting that the work is finished.

Copyright (c) 2026 Martial Systems LLC. MIT license — see [LICENSE](./LICENSE).

<p align="right">
  <a href="https://ko-fi.com/martialgames"><img src="https://img.shields.io/badge/Donate-Ko--fi-ff5e5b?style=flat-square&logo=ko-fi&logoColor=white" alt="Donate on Ko-fi" /></a>
  &nbsp;
  <a href="https://martialgames.net/"><img src="https://img.shields.io/badge/Martial%20Games-site-1a3a2a?style=flat-square" alt="Martial Games" /></a>
</p>

---

## Purpose

Assistants often change one code path, confirm that path works, and report success while another entry point, deploy step, cache, or mirrored file still behaves the old way. They also ship junior-default code, AI-polished PDF prose, or a first draft with no second pass.

This repository is a short set of rules you attach to a project or chat so the assistant:

1. Builds to the quality defaults (code and PDFs)  
2. Lists every path that can hit the change  
3. Checks each of them  
4. After creating something, re-passes with the same rules and fixes bugs  
5. Reports only after that  

There is nothing to install. Copy a markdown file into your tools.

---

## Quality defaults

| Surface | Default (override only if the user asks) |
|---------|------------------------------------------|
| **Code** | Top software architect with a PhD in CS: clear design, precise implementation, right structure over quick hacks |
| **PDFs** | PhD / research-level register; no AI polishing (no fluff, marketing gloss, or generic LLM prose) |
| **After create** | Same-rules sanity pass; fix defects; re-pass until clean (or residual risk is explicit) |

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

> Follow Verify Before Done (quality defaults + interaction paths). Do not report finished work without the report section.

---

## Required process

```text
implement at quality bar → list interaction paths → check each path
  → same-rules sanity pass on new work → fix failures → recheck all paths → report
```

Do not report “fixed”, “done”, or “try it” after checking only the path you just edited.  
Do not skip the second pass after creating something.

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
| [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) | Full rule set (quality defaults + verify process) |
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
