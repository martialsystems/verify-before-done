# Verify Before Done

**A one-file rule that stops AI coding agents from saying “fixed” after only the happy path.**

Copyright (c) 2026 **Martial Systems LLC**. MIT licensed — see [LICENSE](./LICENSE).

<p align="right">
  <a href="https://ko-fi.com/martialgames"><img src="https://img.shields.io/badge/Donate-Ko--fi-ff5e5b?style=flat-square&logo=ko-fi&logoColor=white" alt="Donate on Ko-fi" /></a>
  &nbsp;
  <a href="https://martialgames.net/"><img src="https://img.shields.io/badge/Martial%20Games-site-1a3a2a?style=flat-square" alt="Martial Games" /></a>
</p>

---

## The problem

Coding agents often:

1. Change one path  
2. See that path work  
3. Say **done**  

…while another button, deploy script, file mirror, or cache still shows the **old** behavior.

This pack is a short, portable **operating law** you attach to Claude, Cursor, Codex, ChatGPT, Gemini, Grok, or any other agent: **map every interaction, check all of them, then report.**

No install. No GraphForge. No SDK. Copy a markdown file.

---

## 60-second install

| You use | What to do |
|---------|------------|
| **Any chat** | Paste [PASTE_BLOCK.txt](./PASTE_BLOCK.txt) at the start of the session |
| **Short custom instructions** | Copy [VERIFY_BEFORE_DONE.short.md](./VERIFY_BEFORE_DONE.short.md) |
| **Full project rule** | Copy [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) into project instructions / `AGENTS.md` / `CLAUDE.md` |
| **Cursor** | Copy [.cursor-rules-example.mdc](./.cursor-rules-example.mdc) → `.cursor/rules/verify-before-done.mdc` |
| **Claude Code / skills** | Copy [SKILL.md](./SKILL.md) into a skills folder as `verify-before-done/SKILL.md` |
| **Repo default** | Copy [AGENTS.md.drop-in](./AGENTS.md.drop-in) → `AGENTS.md` at repo root |

Then say once:

> Follow Verify Before Done. Do not claim done without the report block.

---

## What the agent must do

```text
implement → map all paths → check all paths → patch if needed → re-check full map → report
```

**Forbidden:** “fixed / done / try it” after only the path they just edited.

**Required closing block:**

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

---

## Files in this repo

| File | Purpose |
|------|---------|
| [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) | Full law (upload this for serious use) |
| [VERIFY_BEFORE_DONE.short.md](./VERIFY_BEFORE_DONE.short.md) | Condensed (~token budget friendly) |
| [PASTE_BLOCK.txt](./PASTE_BLOCK.txt) | One paste into a blank chat |
| [SKILL.md](./SKILL.md) | Skill frontmatter for skill-capable tools |
| [AGENTS.md.drop-in](./AGENTS.md.drop-in) | Drop-in `AGENTS.md` fragment |
| [.cursor-rules-example.mdc](./.cursor-rules-example.mdc) | Cursor always-on rule example |

---

## Product tips (by tool)

<details>
<summary><b>Claude</b> (Projects / Code / custom instructions)</summary>

- Project knowledge or custom instructions: short or full `.md`
- Claude Code: `~/.claude/skills/verify-before-done/SKILL.md` (or project skills path)

</details>

<details>
<summary><b>Cursor</b></summary>

- Project Rules with `alwaysApply: true` (see the `.mdc` example)
- Or User Rules → paste the short version

</details>

<details>
<summary><b>ChatGPT / Codex</b></summary>

- Custom instructions or project system prompt: short version  
- Workspace: put full law in `AGENTS.md`

</details>

<details>
<summary><b>Grok Build</b></summary>

- Skill: `SKILL.md` under user skills  
- Or attach the full markdown as a rule file

</details>

---

## Why this exists

Built after real multi-agent / multi-publisher failures: green CI and a good local path while a **secondary** path still shipped old behavior. The law forces an **interaction map** and an honest residual-risk line so “probably fine” is not an acceptable finish.

---

## License & copyright

| | |
|---|---|
| **License** | [MIT](./LICENSE) |
| **Copyright** | © 2026 Martial Systems LLC |
| **NOTICE** | [NOTICE](./NOTICE) |

You may fork, embed, and ship the text. Bring your own product name if you rebrand a fork; do not present a fork as an official Martial Systems product without permission.

---

<p align="right">
  <sub>
    Optional support:
    <a href="https://ko-fi.com/martialgames">Ko-fi</a>
    ·
    <a href="https://martialgames.net/">martialgames.net</a>
  </sub>
</p>
