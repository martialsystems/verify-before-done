# Verify Before Done: Grok Bot edition

**Copyright (c) 2026 Martial Systems LLC.** MIT: see [LICENSE](../../LICENSE).

Same policy as the pack (quality defaults, git first, interaction map, real
checks, lesson promotion, report block), translated to the actions a Grok Bot
in Cursor can take.

## Install

1. Save [SKILL.md](./SKILL.md) as a bot skill named `Verify before done`.
2. Add [MEMORY_LINE.txt](./MEMORY_LINE.txt) to shared memory as a standing instruction so every bot loads it.
3. Optional, for an enforceable check: clone the pack onto the box at `~/agent_laws_verify_before_done` so the bot can run `vbd_gate.py check --claim-done` from Shell.

## Enforcement

In Grok Bot this edition is instruction-level, not hook-enforced. Bots have no
Stop hook and no pre-push hook, so the bot follows the skill and the standing
instruction the same way it follows any rule, and it can still skip them. The
one hard check is `vbd_gate.py`, which runs only when the bot calls it.

## Differences from the terminal edition

| Terminal edition | Grok Bot edition |
|------------------|------------------|
| Stop hook runs `vbd_gate` when a turn ends | No hook; the skill tells the bot to run the gate from Shell |
| pre-push hook blocks a push | No hook; pushes need user approval, and the gate runs first |
| Push completed work by default | Push only when the user asked; otherwise the Git line says why not |
| Checks are commands and browser click-throughs | Adds bot checks: Read back, WebFetch links, desktop screenshots, send ids, re-read routines and memory, spot-check subagents |
| Report block on every finish | Report block for code, repo, deploy, and docs work; one plain line for small non-code tasks |
