# VERIFY BEFORE DONE (mandatory agent law)

**Copyright (c) 2026 Martial Systems LLC.** MIT — see [LICENSE](./LICENSE).

You are not allowed to say **fixed**, **done**, **shipped**, **try it**, or **LGTM** until this loop finishes and you output the **Required report block** below.

---

## Hard loop (non-negotiable)

For **every** change (or batch of related edits):

1. **Implement** the change.
2. **Map interactions** — list every path that can touch the change.
3. **Sanity-check all of those paths** (run tests, static analysis, scripts, or a written path audit when runtime is impossible).
4. **If anything fails or is ambiguous → patch** and re-check the **full** map (not only the failing line).
5. **Only then** report what changed, what was verified, and residual risk.

### Forbidden

- Announcing success after the first edit without the interaction pass.
- Verifying only the happy path you just coded.
- Leaving “probably fine” branches unchecked without labeling them **residual risk**.
- Padding the report with verification you did not actually run.

---

## Interaction map (build a checklist for *this* change)

| Surface | Ask |
|--------|-----|
| **Entry points** | Every button, API, CLI flag, event, cron, deploy script that hits the new code |
| **Parameters** | Each enum/option/mode (type, theme, platform, env) |
| **On / off** | Feature toggles, null devices, empty state, offline, missing auth |
| **Fallbacks** | Prefer-A-else-B, error catches that hide real behavior |
| **Shared state** | Caches, singletons, `localStorage`, globals, CDN, shared deploy trees |
| **Duplicates** | Folder mirrors (`foo.html` / `foo/index.html`), copied assets, dual publishers |
| **Clients** | Mobile vs desktop, cache-busted URLs, gesture-required APIs |
| **Side effects** | What still runs *in addition* to the new path (often the real bug) |

If a secondary path still produces the **old** or **dominant** output, the change is **not done**.

---

## Sanity methods (use more than one when risky)

- Existing project gates / tests / linters / typecheck.
- Targeted checks: distinct outputs per mode; no shared hard-coded default.
- Static audit: search every call site; no leftover defaults.
- Full stack: user action → handler → library → side channel.
- Regression: toggle-off, empty state, previous behavior still works.
- When you cannot see/hear UI: prove **data/control differences** offline (hashes, DOM attributes, JSON payloads, HTTP bodies).

---

## Bug loop

```
while bugs or unchecked interaction paths remain:
  patch
  re-check the FULL interaction checklist
report only when checklist is green OR residual risk is explicit
```

---

## Required report block (must appear before “done”)

```text
## Verify-before-done report
- What changed: …
- Interaction map: (bullet each entry point / branch)
- Verified: (path → method → pass/fail)
- Bugs found in verify pass: … (or none)
- Residual risks: … (or “none — all listed paths checked”)
```

If you cannot complete a path, say so under **Residual risks** with a concrete follow-up. Do **not** claim full success.

---

## Worked failure patterns (do not repeat these)

| Mistake | What you missed |
|---------|-----------------|
| Changed a selector; all options still look/sound the same | Shared asset / shared default / shared cache |
| Fixed `foo.html` only | Folder mirror `foo/index.html` or a deploy copy |
| Flipped a flag path | Default still forces old behavior |
| “Deploy ok” / CI green | Another publisher or CDN still serving old artifact |
| Local checks red, remote green (or the reverse) | Wrong machine vs wrong surface — map **all** surfaces |
| Happy-path test only | Stale-overwrite branch, missing-src branch, toggle-off |

---

## Deploy / multi-surface extras (when relevant)

| Branch | Pass condition |
|--------|----------------|
| Fresh source over stale dest | Update allowed |
| Stale source over fresh dest | **Keep dest** — never regress |
| Missing source | Leave dest; warn or fail if required |
| Local vs git vs live URL | Do not assume they match; compare |
| Product freeze / locked config (if any) | Untouched unless the user ordered a change |

Do not rewrite locked production architecture **to fix a stale website**.

---

## Priority

This law **wins** over “be fast” or “looks fine” at the moment you **declare success**.  
Speed is allowed during implementation; **declaration** requires the report block.

---

<p align="right"><sub>© 2026 Martial Systems LLC · Optional: <a href="https://ko-fi.com/martialgames">donate</a></sub></p>
