---
name: verify-before-done
description: >
  Require a full interaction-path check before reporting work finished.
  Use when finishing code, config, UI, deploy, docs, or bugfix work, or when
  the user asks to verify, sanity-check, or mark work done. Prevents reporting
  success after checking only one path. Also enforces quality defaults:
  architect/PhD-level code, research-level PDFs with no AI polish, prose
  punctuation (colons; em dash only for ironic cut-off), a same-rules
  sanity pass after creating anything, and git remote-first (fetch/pull if
  origin is ahead; finish-later if local is edited; push or say why).
---

# Verify before done

**Copyright (c) 2026 Martial Systems LLC.** MIT.

Do not report success until this process is complete.

## Quality defaults

- **Code:** top software architect with a PhD in CS  
- **PDFs:** PhD / research-level; no AI polishing  
- **Prose / docs:** lists use colons; em dashes only for ironic cut-off/swerve  
- **Create:** same-rules second pass; fix bugs; re-pass until clean  

Override only when the user asks for a lower bar.

## Process

1. In a git tree: fetch. If origin is ahead, pull before editing. If not ahead and the tree is already edited: finish-later, do not discard.  
2. Implement the change.  
3. List all interaction paths (include prose surfaces when docs/strings change).  
4. Check each path (tests, static review, scripts, written audit; docs: no decorative em dashes).  
5. On failure, fix and recheck the full list.  
6. Push completed work unless the user asked to hold it. If you do not push, the Git line must say why.  
7. Report with the section below.  

## Interaction map

Entry points, parameters/modes, on/off and empty states, fallbacks, shared  
state and caches, mirrored files, client differences, side effects, prose  
surfaces (README, docs, commits, user-facing strings), and git (fetch /  
finish-later / push or why-not).

## Do not

- Report fixed or done without the report section  
- Check only the path just edited  
- Claim verification that was not run  
- Skip the same-rules sanity pass after creating something  
- Ship decorative em dashes in docs while quality defaults forbid them  
- Implement on a local that is behind origin after a fetch was possible  
- Leave finished work unpushed without saying why  

## Report section

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Git: fetched; origin ahead → pulled <sha> | no recent push; finish-later <paths> | pushed <ref@sha> | did not push: <reason> | not a git repo
- Residual risks:
```

## Deploys

Do not overwrite newer artifacts with older ones.  
Do not assume green CI means the public surface is current.

Full text: [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md).

---

<sub>© 2026 Martial Systems LLC · https://ko-fi.com/martialgames</sub>
