# Verify before done

**Copyright (c) 2026 Martial Systems LLC.** Released under the MIT License (see [LICENSE](./LICENSE)).

Do not report work as fixed, done, shipped, or ready to try until the process below is finished and the report section is filled in.

---

## Quality defaults

Apply these whenever they match the work. Override only when the user explicitly asks for a lower bar (sketch, prototype, plain summary, consumer one-pager, etc.).

### Code

Write and change code at the level of a **top software architect with a PhD in computer science**.

- Design: clear abstractions, correct boundaries, failure modes considered, no accidental complexity
- Implementation: precise, maintainable, and intentional; not clever for its own sake; not junior-default scaffolding
- Defaults: prefer the right structure over the quickest patch unless the user asks for a throwaway

### PDFs

For **all PDFs** (create, edit, rewrite, or content authored for a PDF deliverable):

- **Register:** PhD / research-level writing and structure
- **Tone:** no AI polishing: no buzzword fluff, no marketing gloss, no generic LLM filler, no “smooth” synthetic prose

### Create → same-rules sanity pass → fix bugs

Whenever you **create** something (code, config, UI, PDF, docs, scripts, or other deliverables):

1. Build it to the applicable quality bar above.
2. **Pass over it again with the same rules** as a deliberate sanity check: design holes, edge cases, inconsistencies, regressions, and broken paths.
3. **Fix every bug or defect found** before reporting done. Re-run the pass after fixes until clean (or residual risk is stated).

Creating without a same-rules sanity pass and bug-fix loop is incomplete. This stacks with the interaction-path process below.

---

## Process

For each change (or related batch of changes):

1. Make the change.  
2. List every path that can reach the change (interaction map).  
3. Check each path (tests, static review, scripts, or a written audit when a runtime check is not possible).  
4. If a check fails or is unclear, fix it and check the full list again—not only the failing item.  
5. Report what changed, what was checked, and any remaining risk.

### Do not

- Report success after a single edit without the checks above.  
- Check only the path you just modified.  
- Leave unchecked branches as “probably fine” without naming them as residual risk.  
- Claim verification that was not performed.

---

## Interaction map

Build a short checklist for the current change.

| Area | What to cover |
|------|----------------|
| Entry points | Buttons, APIs, CLI flags, events, schedules, deploy scripts |
| Parameters | Modes, options, environments, platforms |
| Disabled / empty | Feature off, missing data, offline, unauthenticated |
| Fallbacks | Prefer-A-else-B paths; error handlers that hide behavior |
| Shared state | Caches, globals, local storage, CDNs, shared deploy trees |
| Duplicates | Mirrored pages (`foo.html` vs `foo/index.html`), copied assets, second publishers |
| Clients | Mobile vs desktop, cache-busted URLs, APIs that need a user gesture |
| Side effects | Other code that still runs in parallel with the new path |

If another path still produces the previous or dominant result, the work is not finished.

---

## How to check

Use more than one method when the change is risky:

- Existing tests, linters, and type checkers  
- Targeted checks for each mode (outputs must actually differ when they should)  
- Search for all call sites; remove leftover hard-coded defaults  
- Trace user action → handler → library → any extra side channel  
- Confirm prior behavior still works when the feature is off or empty  
- When UI cannot be observed: compare data (payloads, attributes, hashes, HTTP bodies)

---

## Until finished

```
while failures or unchecked paths remain:
  fix
  re-run the full checklist
report only when the checklist passes, or residual risk is stated clearly
```

---

## Report section (required before “done”)

```text
## Verify-before-done report
- What changed:
- Interaction map:
- Verified: (path → method → pass/fail)
- Bugs found in verify pass:
- Residual risks:
```

If a path could not be checked, list it under residual risks with a follow-up. Do not claim full completion.

---

## Common mistakes

| Mistake | Often missed |
|---------|----------------|
| One control changed; all options still look or behave the same | Shared asset or shared default |
| One HTML file fixed | Mirror under `…/index.html` or a deploy copy |
| Feature flag path updated | Default still forces old behavior |
| Deploy or CI reported success | Another publisher or cache still serving old files |
| Local and remote disagree | Surfaces were not listed separately |
| Only the main success path tested | Overwrite, missing-source, and “off” cases |
| Created once and declared done | No same-rules second pass; defects left unfixed |

---

## Deploys and multiple surfaces

When the work touches sites, static hosts, shared JSON, or more than one publisher:

| Case | Expectation |
|------|-------------|
| Newer source, older destination | Update allowed |
| Older source, newer destination | Keep destination; do not regress |
| Source missing | Keep destination; warn or fail if the source is required |
| Local vs git vs public URL | Compare; do not assume they match |
| Locked production configuration | Leave unchanged unless the user ordered a change |

Do not change a locked production model or architecture solely to correct a stale public page.

---

## Priority

When reporting that work is complete, this process takes precedence over finishing quickly. Implementation may be fast; the completion claim may not skip the report. Quality defaults (code, PDFs, create sanity pass) apply for the whole session unless the user overrides them.

---

<p align="right"><sub>© 2026 Martial Systems LLC · <a href="https://ko-fi.com/martialgames">Ko-fi</a></sub></p>
