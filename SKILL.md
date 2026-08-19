---
name: verify-before-done
description: >
  Require a full interaction-path check before reporting work finished.
  Use at the start of implement or edit work (fetch before edit), when
  finishing code, config, UI, deploy, docs, or bugfix work, or when the
  user asks to verify, sanity-check, or mark work done. Prevents reporting
  success after checking only one path. Also enforces quality defaults:
  architect/PhD-level code, research-level PDFs with no AI polish, prose
  punctuation (colons; em dash only for ironic cut-off), a same-rules
  sanity pass after creating anything, and git remote-first (fetch; pull if
  ahead and clean; dirty+ahead: stash, commit, or report both; finish-later
  if local is edited and origin is not ahead; push or say why).
---

# Verify before done

**Copyright (c) 2026 Martial Systems LLC.** MIT.

Do not report success until this process is complete.

## Quality defaults

- **Code:** top software architect with a PhD in CS  
- **PDFs:** PhD / research-level; no AI polishing  
- **Prose / docs:** lists use colons; em dashes only for ironic cut-off/swerve  
- **Create:** same-rules second pass; fix bugs; re-pass until clean (or residual risk is explicit)  

Override only when the user asks for a lower bar.

## Process

1. In a git tree: fetch. If origin is ahead and the tree is clean, pull before editing. If origin is ahead and the tree is dirty: stash, commit, or report both; never discard or `reset --hard` to take the pull. If origin is not ahead and the tree is already edited: finish-later, do not discard.  
2. Implement the change.  
3. List all interaction paths (include prose surfaces when docs/strings change).  
4. Check each path (tests, static review, scripts, written audit; docs: no decorative em dashes). Run `python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done` with `--promoted` or `--not-promoted` before the report.  
5. On failure, fix and recheck the full list. Promote general lessons to the VBD pack (`LESSONS.md`); do not leave them only in this repo. Skip when the lesson is unique to this product. Apply matching `LESSONS.md` rows on this change unless Skip-when matches.  
6. Push completed work unless the user asked to hold it. If you do not push, the Git line must say why.  
7. Report with the section below.  

## Interaction map

Entry points, parameters/modes, on/off and empty states, fallbacks, shared  
state and caches, mirrored files, client differences (phone-width 390x844  
and desktop ~1280 for UI, layout, nav, or in-page jumps), side effects, prose  
surfaces (README, docs, commits, user-facing strings), and git (fetch /  
pull if ahead and clean / dirty+ahead / finish-later / push or why-not).  
Phone-width must be a named command (martialsys boards:  
`python3 viewer/scripts/viewport_sanity.py`). Thinking about mobile is not a check.

## Do not

- Report fixed or done without the report section  
- Check only the path just edited  
- Claim verification that was not run  
- Skip the same-rules sanity pass after creating something  
- Ship decorative em dashes in docs while quality defaults forbid them  
- Implement on a local that is behind origin after a fetch was possible  
- Leave finished work unpushed without saying why  
- Treat unchecked paths as probably fine without naming residual risk  
- Leave a general lesson only in the repo that hit it (promote general lessons)  
- Never force-push unless the user ordered it  
- `reset --hard` or discard finish-later work to make a pull easy  

## Report section

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Git: fetched; origin ahead → pulled <sha> | no recent push; finish-later <paths> | pushed <ref@sha> | did not push: <reason> | not a git repo
- Promoted: <lesson → LESSONS.md / pack> | not promoted: <why>
- Residual risks:
```

## Deploys

Do not overwrite newer artifacts with older ones. Missing source keeps dest.  
Do not assume green CI means the public surface is current.  
Do not change locked production or architecture only to refresh a stale public page.

Full text: [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md).  
Promoted cross-project defaults: [LESSONS.md](./LESSONS.md).

---

<sub>© 2026 Martial Systems LLC · https://ko-fi.com/martialgames</sub>
