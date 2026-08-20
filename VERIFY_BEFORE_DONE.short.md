# Verify before done (short)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

## Quality defaults

- **Code:** top software architect with a PhD in CS (clear design, precise implementation, right structure over quick hacks).  
- **PDFs:** PhD / research-level register; no AI polishing (no fluff, marketing gloss, or generic LLM prose).  
- **Prose / docs:** lists use colons; em dashes only for ironic cut-off/swerve (not for asides or polished rhythm). Do not glob-replace dashes with colons or hyphens; rewrite so the sentence still parses.  
- **After create:** pass over again with the same rules; fix bugs; re-pass until clean (or residual risk is explicit).  

Override only when the user asks for a sketch, prototype, or lower bar.

## Process

Do not report fixed, done, or ready to try until:

1. In a git tree: `git fetch`. If origin is ahead and the tree is clean, pull before editing. If origin is ahead and the tree is dirty: stash, commit, or report both; never discard or `reset --hard` to take the pull. If origin is not ahead and the tree is already edited, that is finish-later work: do not discard it.  
2. The change is implemented.  
3. Every interaction path is listed (entry points, modes, on/off, fallbacks, caches, mirrors, deploys, side effects, prose surfaces, git). For UI, layout, nav, or in-page jumps: include phone-width (390x844) and desktop (~1280).  
4. Each path is checked (tests, search, scripts, written audit; docs scanned for decorative em dashes). Phone-width must be a named command (martialsys boards: `python3 viewer/scripts/viewport_sanity.py`), not a thought. Run `vbd_gate.py check --claim-done` so fetch, dashes, and skip-landing cannot be forgotten.  
5. Failures are fixed and the full list is rechecked. Promote general lessons to the VBD pack (`LESSONS.md`); do not leave them only in this repo. Skip when the lesson is unique to this product.  
6. Completed work is pushed unless the user asked to hold it (forgot-to-push default). If you do not push, the Git line must say why.  
7. The report section below is filled in.

Do not check only the path you just edited. Do not invent checks that were not run.  
Do not implement on a local that is behind origin after a fetch was possible.  
Do not treat unchecked paths as probably fine; name them under residual risks and do not claim full completion.  
Never force-push unless the user ordered it. Never `reset --hard` or discard finish-later work to make a pull easy.

After any change, end with:

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

If another path still shows the old behavior, the work is not finished.  
For deploys: do not overwrite newer artifacts with older ones. Missing source keeps dest. Green CI does not prove the public surface is current. Do not change locked production or architecture only to refresh a stale public page.

---

<sub>© 2026 Martial Systems LLC · [Ko-fi](https://ko-fi.com/martialgames)</sub>
