# Punctuation (all assistant writing)

**Copyright (c) 2026 Martial Systems LLC.** MIT.

**Scope:** every surface the assistant writes: chat replies, README/docs, commit
messages, PR text, code comments, config comments, generated drafts, and PDF
prose. Home-global and this pack. Project rules may tighten; they may not loosen
this unless the user explicitly asks.

## Lists and labels: colons, not dashes

When writing a list of items with a short label and explanation, use a **colon**,
not an em dash (—) or en dash.

**Do:**

- Channels: named state slots with reducers
- Laws: predicates that fail closed after a node

**Do not:**

- Channels — named state slots with reducers
- Laws — predicates that fail closed after a node

Same idea in tables and definition-style bullets: `Term: explanation`.

## Em dashes in prose

Do **not** use em dashes as default punctuation (not for asides, apposition, or
“polished” rhythm). Prefer commas, periods, or colons **according to the role
below**. A colon is not a universal substitute.

Use an em dash **only ironically**: when you cut yourself off mid-thought to say
something else instead.

**Do (cut-off / swerve):**

- I was going to ship it Friday—actually, scrap that, it’s not ready.
- We could add another agent—no, typed handoffs first.

**Do not (generic aside / AI polish):**

- The pipeline—which is already complex—needs gates.
- Fail closed—not best effort—after every node.
- Never auto-posts — you paste yourself.  (use a colon)

## Replacing a dash: classify, then rewrite

**Do not glob-replace** `—` or `–` with `:`, `,`, or `-` across a file. That is
how ungrammatical copy is produced. Each dash has a role. Choose the replacement
for **that** role, then reread the whole sentence. If it would not pass a
copy-editor, rewrite the sentence. Do not swap a character and move on.

### Role to rewrite

| What the dash was doing | Rewrite | Not |
|-------------------------|---------|-----|
| Label + definition (list, table, `Term — meaning`) | colon: `Term: meaning` | hyphen; a comma |
| Paired aside / nonrestrictive (`The pipeline—which is already complex—needs gates`) | commas: `The pipeline, which is already complex, needs gates`. Or parentheses. Or two sentences. | colons on both sides; hyphen-minus asides |
| Mid-sentence apposition (`the gate—a fail-closed predicate—runs last`) | commas or recast: `the gate, a fail-closed predicate, runs last` | colon |
| Contrast (`Fail closed—not best effort`) | comma or recast: `Fail closed, not best effort` / `Fail closed rather than best effort` | colon |
| Result / namely (`the output—a stale board`) | recast: `the output is a stale board` or `the output, a stale board, ...` | hyphen |
| Range (`10–12`, `2024–2026`) | `to` (`10 to 12`) or an ASCII hyphen only in a true compound (`pre-commit`) | colon, em dash |
| Attribution | comma | colon unless introducing a block quote |
| Ironic cut-off / swerve | **keep** the em dash, no spaces: `Friday—actually, scrap that.` | colon |

### Colon is not a universal substitute

A colon is legal only when what follows **defines, lists, or elaborates** what
precedes, and the words before the colon are a complete setup (a noun phrase, or
a clause that can introduce that elaboration).

- Do: `Channels: named state slots with reducers`
- Do: `Three gates: fetch, dashes, skip-landing.`
- Do not: `The pipeline: which is already complex: needs gates.`
- Do not: `We prefer: speed.` (colon after a verb with a single object; write `We prefer speed.`)
- Do not: `Fail closed: not best effort: after every node.`

### After the rewrite, the sentence must still parse

Reject the edit if any of these hold:

- No finite verb left in the main clause
- Double punctuation (`,:`, `:.`, `,,`, `::`)
- A relative clause (`which`, `that`, `who`) glued on with a colon
- Hyphen-minus standing in for an em dash (`pipeline-which is already complex-needs`)
- A fragment on either side of a colon that is not a label or a list item
- Two unrelated clauses welded together

If the only way to drop the dash is an ugly splice, rewrite the sentence.
Deleting the dash without choosing a grammatical replacement is also a fail.

Worked examples:

- `The pipeline—which is already complex—needs gates.` → `The pipeline, which is already complex, needs gates.`
- `Fail closed—not best effort—after every node.` → `Fail closed, not best effort, after every node.`
- `Never auto-posts — you paste yourself.` → `Never auto-posts: you paste yourself.`
- `Windows 10–11` → `Windows 10 to 11`

## Before reporting done

If you created or edited prose/docs in the change set, scan for decorative em/en
dashes **and** for dash-to-colon or dash-to-hyphen splices that no longer parse
(except intentional cut-off/swerve). Shipping a README full of AI-polish dashes,
or of colon splices that used to be dashes, is a failed verify pass.
