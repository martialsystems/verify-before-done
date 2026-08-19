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

### Prose and documentation (all assistant writing)

Applies to chat, README/docs, commit messages, PR text, comments, and generated user-facing text.

**Lists / labels:** use a **colon**, not an em dash or en dash.

- Do: `Channels: named state slots with reducers`
- Do not: `Channels — named state slots with reducers`

**Em dashes:** not default punctuation (not for asides, apposition, or polished rhythm). Prefer commas, periods, or colons.

Use an em dash **only for ironic cut-off / swerve** (you start one thought, stop, say something else):

- Do: `I was going to ship Friday—actually, scrap that.`
- Do not: `Never auto-posts — you paste yourself.` (use a colon)

Before reporting done on doc or prose edits: scan for decorative em/en dashes and fix them.

### Create → same-rules sanity pass → fix bugs

Whenever you **create** something (code, config, UI, PDF, docs, scripts, or other deliverables):

1. Build it to the applicable quality bar above.
2. **Pass over it again with the same rules** as a deliberate sanity check: design holes, edge cases, inconsistencies, regressions, broken paths, and decorative em dashes in prose.
3. **Fix every bug or defect found** before reporting done. Re-run the pass after fixes until clean (or residual risk is stated).

Creating without a same-rules sanity pass and bug-fix loop is incomplete. This stacks with the interaction-path process below.

---

## Process

For each change (or related batch of changes):

1. In a git working tree: fetch first (local without a fetch can be old). If origin is ahead and the tree is clean, pull before editing. If origin is ahead and the tree is dirty: stash, commit, or report both; never discard or `reset --hard` to take the pull. If origin is not ahead and the tree is already edited, that is finish-later work: do not discard it.  
2. Make the change at the quality defaults.  
3. List every path that can reach the change (interaction map).  
4. Check each path (tests, static review, scripts, or a written audit when a runtime check is not possible). For prose/docs: check punctuation defaults.  
5. If a check fails or is unclear, fix it and check the full list again (not only the failing item).  
6. Push completed work if the user did not ask to hold it (forgot-to-push default). If you do not push, the report must say why.  
7. Report what changed, what was checked, the git disposition, and any remaining risk.

### Do not

- Report success after a single edit without the checks above.  
- Check only the path you just modified.  
- Leave unchecked branches as “probably fine” without naming them as residual risk.  
- Claim verification that was not performed.  
- Ship README/docs full of decorative em dashes while quality defaults forbid them.  
- Implement on a local tree that is behind origin after a fetch was possible.  
- Leave finished work unpushed without saying why.  
- Discard finish-later local edits to make a pull easy.  
- Force-push unless the user ordered it.  
- `reset --hard` to take a pull or throw away finish-later work.

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
| Clients | Mobile vs desktop. For UI, layout, nav, or in-page jump changes: include phone-width (390x844) and desktop (~1280). The report must name the command that checked them. "I thought about mobile" is not a check. |
| Side effects | Other code that still runs in parallel with the new path |
| Prose surfaces | README, docs, commits, user-facing strings, generated drafts |
| Git | Fetch origin before edit; pull if ahead and clean; dirty+ahead: stash, commit, or report both; finish-later if dirty and not ahead; push or say why |

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
- For UI / layout / nav / hash jumps: run a phone-width (390x844) and desktop (~1280) command (martialsys boards: `python3 viewer/scripts/viewport_sanity.py`). Name that command in the report. If none ran, residual risk; do not claim full completion.  
- For docs/prose: search for decorative `—` / dash-asides; fix to colons or cut-off-only em dashes  
- For git: `git fetch`, then compare to `@{upstream}` (or `origin/HEAD`); pull if behind; do not treat an unfetched local as current  

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
- Git:
- Residual risks:
```

**Git line** (required in a git working tree; write `not a git repo` otherwise):

- Fetched; origin ahead → pulled `<sha>`
- No recent push; finish-later `<paths>` (uncommitted or unpushed unfinished work)
- Pushed `<remote/branch@sha>`
- Did not push: `<reason>` (finish later, user hold, no remote, diverged, offline, secrets, tests failed)

If a path could not be checked, list it under residual risks with a follow-up. Do not claim full completion.

---

## Git (local can be old)

This is part of verify-before-done, not a separate rule.

**Before editing** in a git working tree:

1. `git fetch` (tracking refs without a fetch are not current).
2. If origin is ahead: pull (`git pull --ff-only` when it will fast-forward). Work from that tree.
3. If origin is not ahead and the tree has uncommitted or unpushed edits: **finish later**. Continue that work or leave it and say so. Do not throw it away.
4. If origin is ahead **and** the tree is dirty: do not discard local work to take the pull. Stash, commit, or report both. Then integrate. Never `reset --hard` to make the pull easy.

**Before claiming done:**

- If the change is complete and the user did not ask to hold the push: **push**. Commit first when the work is finished and still uncommitted.
- If you do not push: state why on the Git line. Silent unpushed finished work is a failed verify.

**Forbidden:** force-push unless the user ordered it; `reset --hard` or discard of finish-later edits to make a pull easy.

---

## Common mistakes

| Mistake | Often missed |
|---------|----------------|
| One control changed; all options still look or behave the same | Shared asset or shared default |
| One HTML file fixed | Mirror under `…/index.html` or a deploy copy |
| Feature flag path updated | Default still forces old behavior |
| Deploy or CI reported success | Another publisher or cache still serving old files |
| Local and remote disagree | Surfaces were not listed separately |
| Implemented on local without fetch | Origin already had a newer push |
| Finished work left unpushed | Forgot-to-push default is to push, or say why not |
| Pulled over dirty finish-later work | Keep or stash; do not discard |
| Only the main success path tested | Overwrite, missing-source, and “off” cases |
| Created once and declared done | No same-rules second pass; defects left unfixed |
| Draft logic fixed for punctuation | README still full of decorative em dashes |

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

Missing source keeps dest. Do not change a locked production model or architecture solely to correct a stale public page.

---

## Priority

When reporting that work is complete, this process takes precedence over finishing quickly. Implementation may be fast; the completion claim may not skip the report. Quality defaults (code, PDFs, prose/punctuation, create sanity pass) apply for the whole session unless the user overrides them.

---

<p align="right"><sub>© 2026 Martial Systems LLC · <a href="https://ko-fi.com/martialgames">Ko-fi</a></sub></p>
