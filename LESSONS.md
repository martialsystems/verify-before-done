# Promoted lessons (cross-project)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

Grok does **not** remember a fix from one repo in the next chat. This file does.

At the start of implement or UI work: apply every row whose **When** matches, unless **Skip when** matches. If you discover a general miss, add a row here and on the drop-ins. Do not leave it only in the project that hit it.

| Date | Lesson | When | Skip when |
|------|--------|------|-----------|
| 2026-08-18 | Phone-width (390x844) and desktop (~1280) for UI, layout, nav, or in-page jumps. Named command, not a thought. Skip/hash must land the **visual** target (the chart), not a tall section header. Martialsys boards: `python3 viewer/scripts/viewport_sanity.py`. | Any HTML/CSS/nav/anchor change | No UI (pure backend, data, or docs-only with no layout) |
| 2026-08-16 | Fetch before edit. Dirty+ahead: stash, commit, or report both. Finish-later if local is edited and origin is not ahead. Push or say why. | Any git working tree | Not a git repo |
| 2026-08-16 | Do not overwrite a newer deploy artifact with an older one. Missing source keeps dest. | Site, Pages, board JSON, wrangler | No public/deploy copy |
| 2026-08-19 | `vbd_gate` is automatic: Grok Stop hook when the agent finishes a turn; git pre-push if the chat never claimed done. User does not run it by hand. | Any finish / push / deploy | Not a git repo and no tracked UI/docs change |
| 2026-08-19 | Hetzner is the martialsys Pages publisher. Host `deploy_viewer.sh` must find `vbd_gate.py` (clone `agent_laws_verify_before_done` at `$HOME` or `/root`, or set `VBD_GATE`). Missing pack is a hard fail, not warn-and-continue. Pre-push belongs on every product git, not only the research viewer. | Host or CI Pages publish; new product clone | Local preview that already has the pack |

Project-only scripts stay in that repo. Promote the **check**, not a one-off path, unless the same surface exists elsewhere.
