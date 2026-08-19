# Verify Before Done: system note (2026-08-19)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

This note describes the pack as implemented, not a roadmap. It is the
research-register description of process, gates, automatic invocation, and
logging. Operator paste files remain [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md)
and [README.md](./README.md).

## Revisions

- **2026-08-19:** First system note. Records quality bar vs interaction map,
  `vbd_gate`, Grok Stop hook, git pre-push, JSONL log, lesson promotion, host
  Pages publisher, and the boundary with GraphForge.

## 1. Object

Verify Before Done (VBD) is a finish protocol for coding assistants. The failure
mode it targets is: one path is checked, success is reported, another entry
point, viewport, deploy copy, or git remote still shows the previous behavior.

The pack is MIT text plus a small Python gate. It is not a plugin that the host
must execute. The host injects markdown. The model can ignore prose. Repeatable
misses are therefore also commands.

## 2. Layers

| Layer | Mechanism | Can the model skip it? |
|-------|-----------|------------------------|
| Quality bar | Prose defaults for code, PDFs, punctuation, second pass | Yes |
| Interaction map | Prose list of paths, then checks named in the report | Yes, if the list is incomplete or lied about |
| Lesson promotion | `LESSONS.md` plus drop-ins; report `Promoted:` | Yes, unless a later gate is added |
| `vbd_gate` | Python: fetch, origin-ahead, dashes, skip-landing, optional viewport | No, if Stop, pre-push, or deploy actually invoke it |
| JSONL log | One line per gate invocation | N/A (side effect of the gate) |

GraphForge’s `verify_before_report` law is a *fourth* layer when a project is
pinned: `claim_done` is refused unless verify channels are true. Those channels
are still set by the agent unless a command produced them. The law is not this
pack and is not a second copy of it. See GraphForge `docs/COMPANIONS.md`.

## 3. Quality bar

Override only when the user asks for a lower register (sketch, prototype, plain
summary).

| Surface | Default |
|---------|---------|
| Code | Top-architect / PhD CS: clear boundaries, no accidental complexity, right structure over a quick patch |
| PDFs | Research register, no AI polish. Date new or rewritten sections on the PDF. Keep a Revisions list. A “Generated …” stamp is not a change date |
| Prose | Label lists with colons. Em dashes only for ironic cut-off |
| After create | Same-rules second pass; fix defects; re-pass until clean or residual risk is explicit |

No automated scorer exists for this layer.

## 4. Interaction map

The map is the set of paths that can still emit the old or wrong result after
the change. Typical slots: entry points, modes (including phone-width 390x844
and desktop ~1280 for UI, layout, nav, or in-page jumps), empty and error
states, fallbacks, caches, mirrored files, deploy copies, side effects, prose
surfaces, git.

A named command is required for viewports. “I thought about mobile” is not a
check. Martialsys boards: `python3 viewer/scripts/viewport_sanity.py` (also
invoked from `vbd_gate` when HTML/CSS changed and that script exists).

The 2026-08 skip-to-graph defect was a map miss: desktop hash navigation worked;
phone-width landing on a tall panel was never listed.

## 5. Promotion

Grok session memory does not carry a repo fix into the next chat. `LESSONS.md`
does. At the start of implement or UI work, apply rows whose **When** matches
unless **Skip when** matches. If a miss is not unique to this product, add a
row and, if it is process law, update the drop-ins and the machine’s home Grok
rule and skill copies. Refresh GraphForge `bundled/verify-before-done` when that
checkout exists.

Do not promote: one product’s law, one market, one file, user-scoped “this repo
only”, or a row that already exists.

## 6. `vbd_gate`

Command: `python3 vbd_gate.py check --app-root DIR`. Wrapper: `bin/vbd`.

| Check | Fail closed when |
|-------|------------------|
| `fetch` | `git fetch` fails (no remote is not a fail) |
| `origin_ahead` | Upstream is ahead. Dirty: stash, commit, or report both; never discard. Clean: pull before claiming done |
| `dashes` | **Added** lines (git diff) in changed `.md` / `.txt` / `.html` contain U+2014 or U+2013, except `VERIFY_BEFORE_DONE.md`. Untracked files are scanned in full. Historical dashes already on HEAD do not fail a later edit |
| `skip_landing` | A `.skip-juicy` hash target *contains* a chart wrap instead of *being* it |
| `viewport_sanity` | `viewer/scripts/viewport_sanity.py` exists, HTML/CSS changed, and that script exits non-zero (390x844 and ~1280 in-view when Chrome is present; static href check always) |
| `claim_done` | `--claim-done` without `--promoted` or `--not-promoted` |

The gate does not pull, does not discard, and does not score the quality bar.
`--tracked-only` ignores untracked files. `--skip-if-clean` returns pass when
there is nothing in the change set (used by the Stop hook so Q&A is not blocked).

## 7. Automatic invocation

The user does not run the gate by hand to close a chat.

| Event | What runs |
|-------|-----------|
| Grok Stop (`end_turn`) | `vbd_stop_hook.py` via `~/.grok/hooks/vbd-stop.json`. Tracked-only, skip-if-clean. Blocks the stop once on failure (`stopHookActive` then allows, so finish-later dirt cannot loop eight times). Pre-push remains the ship backstop |
| `git push` | `.git/hooks/pre-push` after `vbd_gate.py hook-install --app-root DIR` |
| Martialsys Pages deploy | `btc_15m_research/viewer/scripts/deploy_viewer.sh`: hard fail if `vbd_gate.py` is not found (`$VBD_GATE`, `$HOME/...`, `/root/...`, sibling clone). `--tracked-only` |

Install Stop: `python3 vbd_gate.py grok-hook-install`.  
Install pre-push: `python3 vbd_gate.py hook-install --app-root DIR`.

Hooks are local (`.git/hooks`, `~/.grok/hooks`). They are not in git.

## 8. JSONL log (2026-08-19)

Each invocation appends one JSON object to `~/.grok/logs/vbd_gate.jsonl`
(override `VBD_GATE_LOG`). A write failure is printed to stderr and does not
change the gate exit code.

| Field | Meaning |
|-------|---------|
| `ts` | UTC ISO |
| `event` | `check`, `stop`, `pre-push`, or `claim-done` |
| `cwd` | App root |
| `ok` | All gates that ran passed |
| `gates` | `{name, ok, detail, skipped?}` |
| `promoted` | `--promoted` / `not promoted: …` or null |
| `git_head` | `HEAD` sha or null |

This is command evidence. It is not a timestamped transcript of map bullets or
quality-bar judgment. It is not GraphForge’s hash-chained audit log.

```bash
tail -n 20 ~/.grok/logs/vbd_gate.jsonl
```

## 9. Host publisher

Hetzner (`/root/kalshi/…`) is the martialsys Pages publisher. The pack must
exist at `/root/agent_laws_verify_before_done` (or `VBD_GATE`). Missing pack is
a deploy hard fail. The host may lack Chrome: then `viewport_sanity` is
static-only (href identity), not a 390px click.

## 10. File map

| Path | Role |
|------|------|
| `VERIFY_BEFORE_DONE.md` | Full prose law |
| `VERIFY_BEFORE_DONE.short.md` | Condensed law |
| `PASTE_BLOCK.txt` | One-shot chat paste |
| `SKILL.md` | Grok/Claude skill |
| `AGENTS.md.drop-in` | Repo `AGENTS.md` |
| `LESSONS.md` | Cross-project rows |
| `vbd_gate.py` | Gates + JSONL |
| `vbd_stop_hook.py` | Grok Stop adapter |
| `bin/vbd` | CLI wrapper |
| `SYSTEM.md` | This note |

Home copies on a Grok machine: `~/.grok/rules/verify-before-report.md`,
`~/.grok/skills/verify-before-done/`. Those are install surfaces of this pack,
not a second product.
