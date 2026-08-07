# VERIFY BEFORE DONE (short)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

**Do not say fixed/done/try it until this finishes.**

1. Implement  
2. **Map every interaction path** (entry points, modes, on/off, fallbacks, caches, mirrors, deploys, side effects)  
3. **Check all of them** (tests, search, scripts, or written audit)  
4. Fail → patch → re-check **full** map  
5. Report only then  

**Forbidden:** happy-path-only verify; “probably fine”; fake verification.

**Every final answer after a change MUST end with:**

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

If a secondary path still shows old behavior, you are **not done**.  
Multi-surface: never overwrite fresher with staler; git/CI green does not mean the live site is current.

---

<sub>© 2026 Martial Systems LLC · [Ko-fi](https://ko-fi.com/martialgames)</sub>
