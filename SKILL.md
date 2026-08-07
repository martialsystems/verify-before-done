---
name: verify-before-done
description: >
  Mandatory interaction-map and full-path verification before claiming fixed/done.
  Use when finishing any code, config, UI, deploy, or bugfix — and when the user
  says done, fixed, ship, verify, sanity, or /verify-before-done. Blocks happy-path-only
  completion reports. Portable; no GraphForge required.
---

# Verify Before Done

**Copyright (c) 2026 Martial Systems LLC.** MIT.

You must obey this skill before any success claim.

## Loop

1. Implement  
2. Map **all** interaction paths for the change  
3. Sanity-check **every** path (tests, static analysis, scripts, or written audit)  
4. On fail/ambiguity → patch → re-check the **full** map  
5. Only then report  

## Interaction map (minimum)

Entry points · parameters/modes · on/off · fallbacks · shared state/caches ·  
duplicate files/mirrors · clients (mobile/desktop/CDN) · side effects that still run  

## Forbidden

- “Fixed / done / try it” without the report block  
- Checking only the happy path  
- Inventing verification that was not run  

## Required closing block

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

## Deploy / multi-publisher work

- Never overwrite fresher artifacts with staler ones  
- Do not assume git/CI green means the public surface is current  

Full law: [VERIFY_BEFORE_DONE.md](./VERIFY_BEFORE_DONE.md) in this repo.

---

<sub>© 2026 Martial Systems LLC · Optional: https://ko-fi.com/martialgames</sub>
