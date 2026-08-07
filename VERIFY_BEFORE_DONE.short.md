# Verify before done (short)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

Do not report fixed, done, or ready to try until:

1. The change is implemented.  
2. Every interaction path is listed (entry points, modes, on/off, fallbacks, caches, mirrors, deploys, side effects).  
3. Each path is checked (tests, search, scripts, or written audit).  
4. Failures are fixed and the full list is rechecked.  
5. The report section below is filled in.

Do not check only the path you just edited. Do not invent checks that were not run.

After any change, end with:

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

If another path still shows the old behavior, the work is not finished.  
For deploys: do not overwrite newer artifacts with older ones; green CI does not prove the public surface is current.

---

<sub>© 2026 Martial Systems LLC · [Ko-fi](https://ko-fi.com/martialgames)</sub>
