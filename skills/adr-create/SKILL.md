---
name: adr-create
description: Create an Architecture Decision Record (ADR) in docs/adr/
argument-hint: "<title>"
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - glob
  - write
  - edit
permissions:
  allow:
    - Read(docs/adr/**)
    - Write(docs/adr/**)
---

Create an Architecture Decision Record (ADR) in `docs/adr/` for the requested change.

## Steps

1. **List existing ADRs** using `glob docs/adr/*.md` (or `ls docs/adr/`).
2. **Choose the next ADR number**: find the highest existing number and add 1, formatted as 4 digits (e.g., `0001`).
3. **Create the file** at `docs/adr/<NNNN>-<kebab-title>.md`.
4. **Fill in the template below**.
5. **After implementation**, add code comments near relevant code referencing `ADR-<NNNN>`.

## Template

```markdown
# ADR-<NNNN>: <Title>

## Status

Accepted

## Context

What problem, requirement, or constraint triggered this decision?

## Decision

What was chosen?

## Rationale

Why was this option selected? Include quantitative or qualitative reasoning.

## Alternatives Considered

- **Option A**: description — rejected because ...
- **Option B**: description — rejected because ...

## Consequences

Positive and negative trade-offs, risks, and follow-up work.

## Related

- Code comments: `ADR-<NNNN>`
- Links to issues, PRs, or other ADRs
```

## Guidelines

- Keep the ADR concise but complete. One to two pages of markdown is usually enough.
- Record the **decision and the reasoning**, not just the outcome.
- Always document alternatives that were seriously considered and why they were rejected.
- Use the ADR ID consistently in code comments, e.g.:
  - `// ADR-0001: use event-driven message queue`
  - `// See ADR-0001 for rationale on queue selection`

## Research Documentation

ADRs capture *decisions*; research notes capture *context*. Keep them as
separate artifacts and cross-reference them so the ADR stays concise while the
supporting evidence remains discoverable.

### Where to write research notes

Place research material under `docs/research/{function_name}/**`, scoped by the
feature or module the research supports. Use `kebab-case` for the directory
name, matching the codebase's naming for that function.

```
docs/research/
└── sprite-pipeline/
    ├── references.md        # external tools/services surveyed
    ├── tooling.md           # how tools we already use behave
    ├── benchmarks.md        # measurements, comparisons
    └── notes.md             # free-form investigation log
```

### What to record

- **Reference material**: docs, articles, man pages, and specs the project
  relies on, with the source URL and access date.
- **Surveyed tools/services**: name, version, license, what it does well, and
  where it falls short for our use case.
- **Tool usage**: how tools already in the project are invoked, configured, and
  extended — especially non-obvious flags, gotchas, and exit codes.
- **Investigation log**: hypotheses tested, results, and dead ends. Keep failed
  attempts; they prevent re-investigation.
- **Benchmarks / measurements**: numbers, commands to reproduce them, and the
  environment they were taken in.

### Writing rules

- **Write incrementally.** Append small notes as you learn rather than producing
  a large document at the end. Stale context is worse than no context.
- **One topic per file.** Split by concern (references, tooling, benchmarks,
  notes) so readers can find what they need without scrolling past unrelated
  material.
- **Cite sources.** Every external fact needs a link or a citation. Uncited
  claims are treated as opinion.
- **Date entries.** Prefix log entries with `YYYY-MM-DD` so the timeline of
  understanding is visible.
- **Link from ADRs.** When an ADR depends on research, reference it:
  `See docs/research/sprite-pipeline/benchmarks.md for the comparison that
  motivated this choice.`
- **Do not duplicate code.** Research notes describe *why* and *how we found
  out*; the code remains the source of truth for *what it does*.
- **Prune obsolete notes.** When a tool is removed or a conclusion is
  superseded, mark the note as outdated (`> **Outdated (YYYY-MM-DD):** ...`)
  rather than deleting it, so the reasoning history survives.
