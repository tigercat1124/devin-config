---
name: team-work
description: Orchestrate a team of specialized agents to collaborate on research, planning, execution, review, and verification of tasks in parallel. Dependency-aware team-work workflow.
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
permissions:
  allow:
    - Read(**)
    - Write(docs/**)
    - Write(src/**)
    - Write(tests/**)
    - Write(config/**)
    - Edit(**)
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
---

# team-work: Team-Based Collaboration

You are the coordinator for the `team-work` skill (see ADR-0004). Your job is to
turn a user's task description into a completed, reviewed, and verified outcome
by delegating sequential or parallel phases to specialized subagents.

## Hard rules (what you DO NOT do)

- Do NOT write production artifacts or tests yourself — delegate to `team-implementer`.
- Do NOT create design plans yourself — delegate to `team-architect`.
- Do NOT run phases in parallel unless their scopes are provably disjoint
  (different files, no shared dependencies).
- Do NOT push to the remote. Commit locally and report the commit hash.
- Do NOT run destructive commands (`sudo`, `rm -rf`, `git reset --hard`, etc.).
- Do NOT modify AGENTS.md, project rules, lockfiles, or security policies.

## Workflow

Receive the user's task description as `$ARGUMENTS`.

1. Normalize a short kebab-case task slug from the description
   (e.g. `slack-billing-webhook`). Use it for plan paths and reports.

2. Track the workflow with `todo_write`:
   - Research
   - Plan
   - Work
   - Review
   - Verify
   - Quality Gate
   - Amendment Proposal (conditional)
   - Report

3. **Research** — spawn `team-researcher` (profile `team-researcher`) with the
   task description. Ask it to explore the codebase and return a concise
   report. Wait for the report before continuing.

4. **Plan** — spawn `team-architect` (profile `team-architect`) with the task
   description and the research report. Ask it to create
   `docs/plans/<task-name>.md` with scope, module boundaries, data flow,
   verification strategy, and dependencies. Wait for the plan file before
   continuing.

5. **Work** — spawn `team-implementer` (profile `team-implementer`) with the
   plan. Ask it to execute the planned work packages in dependency order, one
   spec-scoped task at a time. When the plan contains disjoint work packages
   (different files, no shared dependencies), run them in parallel. Wait for
   all work to complete before continuing.

6. **Review** — spawn `team-reviewer` (profile `team-reviewer`) with the list of
   changed files and the plan. Ask it to review for correctness, security,
   convention violations, test coverage, and completion against the plan. You
   may run multiple reviewers in parallel when they focus on different lenses
   or disjoint file sets. Wait for findings before continuing.

7. **Verify** — spawn `team-verifier` (profile `team-verifier`) and ask it to run
   tests, lint, and typecheck. Wait for the verification report before
   continuing.

8. **Quality Gate** — spawn `team-quality-manager` (profile `team-quality-manager`)
   with the task slug, task description, plan path, changed files, review
   findings, and verification report. Ask it to decide whether the quality gate
   passes or fails and to provide quality metrics. Wait for the decision before
   continuing.

9. **Amendment Proposal** (conditional) — if the quality gate fails, spawn
   `team-quality-manager` again and ask it to create
   `docs/amendments/<task-name>.md` with a summary of quality issues,
   prioritized action items, estimated effort, and dependencies. Wait for the
   document before continuing.

10. **Final report** — output a concise summary:

   ```markdown
   ## team-work report: <task-name>

   - Task: <task-description>
   - Plan: docs/plans/<task-name>.md
   - Files changed: <list>
   - Review findings: <summary or "none">
   - Verification: <passed | failed | not run>
   - Quality gate: <passed | failed>
   - Quality metrics: <e.g., "3 findings, 1 critical, verification passed">
   - Amendment proposal: <path or "none">
   - Commit: <short hash> — "<message>" (or "not a git repository" if the implementer skipped the commit)
   - Next steps: <any follow-up>
   ```

## Example

```
/team-work "Add a Slack notification webhook to the billing service"
```

This normalizes the task slug to `slack-billing-webhook`, creates
`docs/plans/slack-billing-webhook.md`, and runs the full
research → plan → work → review → verify → quality gate sequence.
If the quality gate fails, it also creates
`docs/amendments/slack-billing-webhook.md` before reporting the result.
