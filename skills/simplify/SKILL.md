---
name: simplify
description: Review changed code for cleanup opportunities and apply fixes. Four parallel reviewers cover reuse, simplification, efficiency, and abstraction-level. Does not hunt for correctness bugs.
argument-hint: "[target]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - edit
  - grep
  - glob
  - exec
  - run_subagent
  - read_subagent
  - todo_write
permissions:
  allow:
    - Exec(git diff)
    - Exec(git status)
    - Exec(git log)
    - Exec(git commit)
  ask:
    - Exec(git push)
---

# Simplify: Cleanup-Only Review and Apply

<!-- ADR-0002: Ported from Claude Code's /simplify. batch was dropped because Devin has no worktree isolation. -->

You are running the `simplify` skill, ported from Claude Code (see ADR-0002).
Your job: review recently changed code for **cleanup** opportunities and apply
the fixes. You do **NOT** hunt for correctness bugs — that is `/code-review`'s
job in the original toolchain, and is out of scope here.

## Scope

Determine the target file set:

1. If the user passed an argument (`$ARGUMENTS`), treat it as the target
   (a path, a glob, or a PR/branch reference). Use `git diff --name-only`
   against the appropriate base if a branch/PR ref is given; for a path/glob,
   list matching files directly.
2. Otherwise, run `git diff --name-only main...HEAD` to list changed files.
   If that returns nothing, fall back to `git status --short` (staged + unstaged).
   **Untracked directories** appear as `??` — expand them with `find` or `glob`
   to list the actual files inside before passing to reviewers.
3. If there is no diff and no changed files, respond with
   "simplify: no cleanup target — working tree is clean" and stop.

## Process

### Step 1 — Identify target files

Run the scope determination above. Record the file list with `todo_write`.

Filter out non-code files (images, binaries, lockfiles, generated files) before
passing the list to reviewers.

### Step 2 — Launch four parallel reviewers

In a **single message block**, spawn four background subagents via `run_subagent`
with `profile: "subagent_explore"` and `is_background: true`. All four must be
launched in the same message so they run in parallel.

Each reviewer gets the **same target file list** but a distinct lens. Use the
prompt template below for each, substituting `<LENS>` and `<LOOKS_FOR>`:

```
You are a code cleanup reviewer. Your lens: <LENS>.

Target files (review ONLY these):
<FILE_LIST>

What to look for: <LOOKS_FOR>

Instructions:
- READ each file with the read tool. Do NOT edit, do NOT run exec, do NOT
  use run_subagent. Report only.
- Ignore correctness bugs (logic errors, off-by-one, null deref, etc.) —
  those are out of scope. Only report cleanup opportunities.
- For each finding, report in this exact format (English only — the root
  will translate the final report to the user's language):
  <file>:<line> — <issue> — <suggested fix>
  Use a single line number when possible (e.g. <file>:42). Use a range
  (e.g. <file>:42-48) only when the finding spans multiple lines.
- If you find nothing to report, respond with "No findings." — that is a
  valid outcome.
- Be concrete: cite the exact line and give a specific fix, not vague advice.
```

The four lenses:

| # | `<LENS>` | `<LOOKS_FOR>` |
|---|----------|---------------|
| 1 | Reuse of existing helpers | (a) Duplicated logic that an existing helper/util **in this codebase** already covers — search with grep first. (b) Reinvented standard patterns that the language's stdlib or a well-known library already provides (e.g. chunk, debounce, throttle, deep-clone) even if not present in the codebase. Report both. |
| 2 | Simplification | Unnecessary nesting, dead branches, redundant conditions, convoluted control flow, boolean expressions that can be simplified. |
| 3 | Efficiency | Obvious O(n^2) where O(n) is trivial, repeated work in loops, wasteful allocations, unnecessary recomputation. Only flag if the fix is obvious and low-risk. |
| 4 | Abstraction level | Code at the wrong layer — low-level detail leaking into high-level modules, high-level policy embedded in low-level utilities, leaky abstractions. |

**Do NOT nest.** These are direct children of the root. Devin disables
`run_subagent` inside subagents, so this root-inline launch is the only way to
get four parallel reviewers.

### Step 3 — Collect and reconcile

Wait for all four reviewers to complete. Use `read_subagent` with `block: true`
on each, or rely on completion notifications if you continued other work.

Merge their findings into a single deduplicated list.

**Reconciliation rules:**

1. **Overlap**: If multiple reviewers flag the same issue on the same line,
   merge into one finding. Note which reviewers agreed.
2. **Contradiction**: If two reviewers give conflicting advice on the same line
   (e.g., one says "extract to helper", another says "inline for clarity"),
   apply this precedence:
   - **Conservative = fewer lines changed, deletion over addition, preserves
     existing structure.** Pick the conservative one.
   - Log the conflict in the final report: `<file>:<line> — chose <X> over <Y>`.
3. **Out of scope**: Drop any finding that would change public API, behavior,
   or add/remove tests. `simplify` is cleanup-only — if a fix could alter
   runtime behavior, skip it and note as "skipped: behavior-changing".

### Step 4 — Apply

Apply the reconciled findings with `edit`.

**Ordering rule**: within a single file, apply edits from **bottom to top**
(highest line number first) so earlier line references stay valid. If a file
has many edits, re-read it after every 3-4 edits to refresh line numbers.

If a finding is unclear or the fix is risky, skip it and note it in the report
as "skipped: <reason>".

### Step 5 — Lightweight verification

Detect the project's fast verification command:

- `package.json` with `lint` or `test` script → `npm run lint` or `npm test`
- `Makefile` with `lint`/`check`/`test` target → `make <target>`
- `pytest`, `go test`, `cargo check`, `ruff`, `eslint` available

Run **one** fast command (prefer lint/typecheck over full tests — speed matters).
If it fails:

- **Do NOT revert.** (ADR-0002: auto-priority — keep the work, surface the breakage.)
- Note the failure in the final report.
- The user can `git revert <hash>` easily because the cleanup is a single commit.

If no verification command exists, skip this step silently.

### Step 6 — Commit

Commit all applied changes with:

```
git add -A && git commit -m "simplify: <short summary of cleanups applied>"
```

**Do NOT push.** `git push` is `ask` in `config.json` and `rules/auto-mode.md`
forbids auto-push. The user pushes when ready.

If no findings were applied (all skipped or none found), do NOT create an empty
commit. Report "no changes applied" and stop.

### Step 7 — Final report

Output a concise summary:

```
## simplify report

- Reviewers: 4 (reuse, simplify, efficiency, abstraction)
- Findings: <N> total, <M> applied, <K> skipped
- Verification: <passed | failed | not run>
- Commit: <short hash> — "simplify: ..."
- Skipped findings:
  - <file:line> — <reason>
- Conflicts resolved:
  - <file:line> — chose <X> over <Y> (more conservative)
```

If verification failed, append:

```
⚠ Verification failed after cleanup. Inspect commit <hash> and revert if needed:
  git revert <hash>
```

If no changes were applied:

```
## simplify report

- Reviewers: 4 (reuse, simplify, efficiency, abstraction)
- Findings: <N> total, 0 applied, <K> skipped
- No commit created (nothing to commit).
```

## Failure Modes (recap)

| Situation | Action |
|-----------|--------|
| No diff / clean tree | Stop with "no cleanup target" |
| Reviewer finds nothing | Valid — "No findings." is a normal result |
| Reviewer contradiction | Root picks conservative (fewer lines changed), logs conflict |
| Verification breaks | Keep commit, surface in report, suggest `git revert` |
| All findings skipped | No commit, report "no changes applied" |
| Subagent nesting attempted | Not possible — Devin disables `run_subagent` inside subagents. Root must launch all four. |

## Examples

```
/simplify                                    # review main...HEAD
/simplify src/auth/                          # review specific path
/simplify "focus on the new validators"      # review with guidance
```

## Notes

- This skill does **not** find correctness bugs. Use a separate review pass for that.
- The four reviewers are read-only (`subagent_explore`); only the root edits.
- All file edits happen in one place (the root), so there is no concurrent-edit conflict.
- See ADR-0002 for the design rationale and the reason `batch` was not ported.
