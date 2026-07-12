---
name: team-work
description: Distribute the assistant's current work across a team of specialized agents that review each other.
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
permissions:
  allow:
    - Read(**)
    - Write(src/**)
    - Write(tests/**)
    - Write(docs/**)
    - Write(config/**)
    - Write(skills/**)
    - Write(agents/**)
    - Edit(**)
    - Exec(mkdir -p)
    - Exec(mkdir -p docs/plans docs/amendments)
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

# team-work: Team-as-Assistant Collaboration

<!-- ADR-0005: root-as-driver, no-file-loop, broader permissions. See ADR-0005 for rationale. -->

You are the coordinator. The team is not a separate project-management layer — the team is how you get the work done. Use the subagents to do the work you would do yourself, and have them review each other.

## Core rules

- Keep the task whole. Do not split it into independent work packages for different agents.
- When you would normally research, implement, review, or verify, delegate the concrete action to the right role.
- Run multiple agents in parallel only when they are reading different files or looking at different lenses.
- You are the final integrator; do not let the team run autonomously without your synthesis.
- Do not modify `AGENTS.md`, `config.json`, or `rules/**`.

## Roles

- `team-researcher`: read-only context gathering.
- `team-architect`: planning and design, writes `docs/plans/<task-name>.md` only if needed.
- `team-implementer`: makes the changes and writes tests.
- `team-reviewer`: correctness, security, style, completion review.
- `team-verifier`: runs tests, lint, typecheck.
- `team-quality-manager`: quality gate and amendment proposal.

## Workflow

1. Summarize the task in a short kebab-case slug.
2. If the task is complex or you lack context, spawn `team-researcher` and/or `team-architect`.
   A plan is optional. If a plan file is needed, ensure it exists (create it directly or ask `team-architect`) and include the content in the prompts you send to later agents.
3. Spawn `team-implementer` with the task description and any plan text. Let it make changes and commit locally.
4. Spawn `team-reviewer` to review the changes. Run multiple reviewers in parallel with different lenses (correctness, security, style, completion) when useful.
5. If tests/lint/typecheck exist, spawn `team-verifier`.
6. Loop implementer → reviewer → verifier as needed. Do not loop more than two rounds; if critical issues remain, stop and ask the user.
7. Optionally, spawn `team-quality-manager` to formalize the gate.
8. Report a concise summary.

## Avoiding hangs and file loops

- If a subagent needs a file, ensure it exists. If the subagent's role has write permission, it should create missing files and directories directly with `write` or `mkdir -p`.
- If the subagent cannot create the missing file (e.g., a read-only role, or the file is outside its allowed write paths), the coordinator should create it or ask the appropriate subagent to create it, then provide it in the prompt.
- Do not retry a failed `read`, `glob`, or `exec` more than once.
- If a subagent reports a missing file or permission error, do not spawn another agent with the same instruction. Create the file or ask the user.
- If the plan is not needed, skip it. If a subagent needs a plan, give the plan text in the prompt, or create the plan file first if you want one.

## Permissions

- The coordinator may read/write/edit files and run exec as needed.
- Subagents are bound by their own profile permissions. If a subagent needs a write outside its allowed paths, you may do that write directly or ask the user.
- Do not push to remote.

## No auto-push

Commit locally and report the commit hash. Do not push.
