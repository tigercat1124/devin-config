---
name: delegate
description: Core orchestration skill — run work in fresh subagents instead of the main context. You dispatch, supervise, verify, report; subagents do the work. Use for any task that should run in a separate agent.
argument-hint: "<task-description>"
triggers:
  - user
  - model
allowed-tools:
  - read
  - edit
  - write
  - grep
  - glob
  - exec
  - run_subagent
  - read_subagent
  - todo_write
  - ask_user_question
  - webfetch
  - web_search
permissions:
  allow:
    - Read(**)
    - Write(src/**)
    - Write(tests/**)
    - Write(docs/**)
    - Write(config/**)
    - Write(skills/**)
    - Write(agents/**)
    - Write(projects/**)
    - Edit(**)
    - Exec(mkdir -p)
    - Exec(backlog)
    - Exec(git diff)
    - Exec(git status)
    - Exec(git log)
    - Exec(git add)
    - Exec(git commit)
  ask:
    - Exec(git push)
  deny:
    - Exec(sudo)
    - Exec(rm -rf)
    - Exec(git reset --hard)
    - Exec(git branch -D)
    - Exec(git push --force)
    - Edit(AGENTS.md)
    - Edit(config.json)
    - Edit(rules/**)
---

# delegate: work runs in fresh agents

You are the dispatcher, not the worker. Delegated work runs in subagents with
their own context — not in this conversation. For non-trivial work this is the
default operating mode: you write the brief, the subagent executes.

## Hard rule

Do NOT perform the delegated task in this context. You may only:

- read files needed to write a good brief,
- spawn and supervise subagents (`run_subagent` / `read_subagent` / resume),
- apply small integration fixes the subagent cannot make itself
  (writes outside its allowed paths, missing directories),
- run Backlog writes (single-writer),
- verify outputs and report to the user.

If you catch yourself implementing, researching, or editing artifacts
directly: stop, put the work into the brief, and spawn.

## Pick a profile

| Work type | Profile | Notes |
|-----------|---------|-------|
| codebase exploration / research | `subagent_explore` | read-only + `web_search`; cheap default model; no `webfetch` |
| implementation / code changes | `code-worker` | read/write/exec; local commits allowed |
| cleanup review (reuse, simplification) | `simplify-reviewer` | read-only |
| anything needing full tools | `subagent_general` | inherits your model — expensive, last resort |

If none fits the required capability set (e.g. web fetch + write), create a
custom profile at `~/.config/devin/agents/<name>/AGENT.md` (active next
session) or run that piece yourself. Do not silently substitute a profile
that lacks the needed tools.

Before spawning, check the profile's `allowed-tools` and `permissions.allow`:
**background subagents auto-deny any tool call that is not pre-approved** and
cannot prompt the user. If the task needs a command the profile lacks, either
spawn foreground (approvals possible), fix the profile first, or perform that
one step yourself.

## Write the brief

Subagents see nothing from this conversation. The prompt must contain:

- **Goal** — one sentence.
- **Context** — decisions already made, user requirements, prior findings the
  subagent needs.
- **Paths** — absolute paths of files to read or write. Do not send read-only
  profiles on open-ended hunts; hand them the paths.
- **Constraints** — what NOT to do, conventions to follow.
- **Done definition** — concrete acceptance criteria.
- **Output** — files to create/update, plus what to report back.

Resolve user-facing questions BEFORE spawning — subagents cannot use
`ask_user_question`.

## Spawn

- Default `is_background: true`; you get a completion notification.
- Foreground only when the result immediately blocks your next step, or the
  task will need permission approvals.
- Parallel only when scopes are provably disjoint (different files or
  different review lenses). Cap at ~3 concurrent.
- Never `devin -p` — fire-and-forget, no mid-run visibility or resume.

## Stage non-trivial work

For anything bigger than a single focused change, chain phases instead of one
mega-agent:

1. **Research/explore** — gather context, report findings.
2. **Implement** — make the changes, run the project's fast verification.
3. **Review** — a read-only reviewer instructed to break the change, not to
   confirm it.
4. **Verify** — run tests/lint/build if they exist.

Rules:

- Feed each phase's output into the next brief — subagents share nothing.
- Skip phases the task does not need (e.g. doc-only work needs no verifier).
- Keep the task whole; split only along provably disjoint scopes.
- At most two implement→review→verify rounds, then stop and ask the user.

## Supervise

- `read_subagent` (block or peek) for progress and results.
- To correct course or approve a denied tool, `resume` — resumed agents run
  foreground.
- Never re-spawn an identical prompt after failure. Fix the brief or the
  permissions, then resume or spawn fresh.
- If a subagent reports a missing file or denied permission, create the file
  or fix the permission yourself — do not spawn another agent with the same
  instruction.
- A subagent that does a forbidden broad search or repeats a failed search:
  stop it; finish the bounded task directly or ask the user.
- Subagent search/file limits: see `AGENTS.md` → `## Subagent Rules`.

## Verify and close

- Read the produced artifacts yourself; check every acceptance criterion
  before reporting done.
- Backlog single-writer: only you run `backlog task edit` / status changes.
  Subagents may only `view` / `list` / `search` / `instructions`.
- Report: which profile ran, what it produced, verification result,
  remaining issues.

## When NOT to delegate

- Trivial lookups or questions answerable in one tool call.
- The user wants interactive back-and-forth on the task itself.
- Subagents are disabled (`subagents_enabled: false` or org policy) — say so
  and work directly.
