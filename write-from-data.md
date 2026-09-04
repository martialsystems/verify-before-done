# Write from the data we have

**Copyright (c) 2026 Martial Systems LLC.** MIT.

**Scope:** every surface the assistant writes: chat replies, README/docs, site
copy, PDFs, reports, commit messages, and generated drafts. Home-global and
the Verify Before Done pack. Project rules may tighten; they may not loosen
this unless the user explicitly asks.

## Hard rule

Describe what the project **is**, what it **does**, and what the **data we
have** shows. Do not define a project by what it is not.

A "What it is not" section is a poor default. It makes the reader process
absences instead of the product, the method, or the measurements.

Do **not** copy this law into other product READMEs. One home rule is enough.

## Do

- Write from files, counts, dates, methods, and results that exist in the tree
- Use positive headings
- State a measured gap as data when that gap **is** the finding (example:
  "13 rows dropped for missing coordinates")
- Measured quantities at or above 1,000 take thousands separators (tons, RMSE,
  counts). Identifiers do not: SHAs, facility IDs, years, gist ids. JSON stays
  raw.

Positive headings (use these, not negation):

- What this is
- What it does
- Data
- How to run
- Current results
- Inputs and outputs

## Do not

- Headings: `What it is not`, `What this is not`, `What it is NOT`
- Identity by absence: "this is not a trading bot", "this is not advice",
  "unlike X, this project…"
- RFP leftover: an "Out of scope" block used to pad or to draw a boundary
  the features list should have stated
- Invent missing capabilities as framing when the data simply does not
  mention them

Those patterns are lazy categorization, RFP "out of scope" overfitting, and
padding. They are not documentation.

## Allowed negation

Negation is for **legal and operational** surfaces, not product copy.

| Allowed | Why |
|---------|-----|
| Terms, conditions, privacy, risk, "not investment advice" | Actual legal text |
| Ops gates already in **that** repo's `AGENTS.md` (example: first Kalshi research watcher, no live orders) | Fail-closed safety, not a README identity section |
| Claim-ban scanners | Fail the banned **token**. Do not write "this is not a casualty estimate" |
| The user asked "what isn't this?" | Direct answer |
| VBD residual-risk line | Process, not product identity |

The first Kalshi research watcher may keep "no live orders" as an ops rule.
Do not copy that "what it isn't" framing onto other product READMEs or
martialsys **site** pages.

Site pages that already used the pattern: leave them unless the user asks to
rewrite. Do not add new ones.

## After writing

Re-read the draft. If a paragraph exists only to say what the work is not,
delete it and replace it with what the data shows, or delete it.
