---
name: verify-before-done
description: >
  Require a full interaction-path check before reporting work finished.
  Use when finishing code, config, UI, deploy, or bugfix work, or when the
  user asks to verify, sanity-check, or mark work done. Prevents reporting
  success after checking only one path. Also enforces quality defaults:
  architect/PhD-level code, research-level PDFs with no AI polish, and a
  same-rules sanity pass after creating anything.
---

# Verify before done

**Copyright (c) 2026 Martial Systems LLC.** MIT.

Do not report success until this process is complete.

## Quality defaults

- **Code:** top software architect with a PhD in CS  
- **PDFs:** PhD / research-level; no AI polishing  
- **Create:** same-rules second pass; fix bugs; re-pass until clean  

Override only when the user asks for a lower bar.

## Process

1. Implement the change.  
2. List all interaction paths.  
3. Check each path (tests, static review, scripts, or written audit).  
4. On failure, fix and recheck the full list.  
5. Report with the section below.  

## Interaction map

Entry points, parameters/modes, on/off and empty states, fallbacks, shared  
state and caches, mirrored files, client differences, and side effects.

## Do not

- Report fixed or done without the report section  
- Check only the path just edited  
- Claim verification that was not run  
- Skip the same-rules sanity pass after creating something  

## Report section

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

## Deploys

Do not overwrite newer artifacts with older ones.  
Do not assume green CI means the public surface is current.

Full text: [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md).

---

<sub>© 2026 Martial Systems LLC · https://ko-fi.com/martialgames</sub>
