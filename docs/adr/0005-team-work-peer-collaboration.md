# ADR-0005: team-work as a peer-collaborative assistant team

## Status

Accepted

## Context

The current `/team-work` skill (ADR-0004) is implemented as a rigid pipeline:
Research → Plan → Work → Review → Verify → Quality Gate. In practice, this
causes several problems:

1. **Hang / file-not-found loops**: Subagents are instructed to read
   `docs/plans/<task>.md` and other artifacts that may not exist or may be
   out of sync. When a file is missing, the subagent repeatedly searches or
   retries instead of stopping.
2. **Permission failures**: `team-implementer` is restricted to `src/**`,
   `tests/**`, and `docs/**`, so it cannot write to the `skills/` and
   `agents/` directories when the skill is invoked on the Devin harness repo
   itself, or to `config/` in normal projects.
3. **Wrong abstraction**: The user wants `/team-work` to be a way to spread the
   assistant's own work across a team and have the team review each other.
   Instead, the current skill splits the task into separate work packages and
   runs the coordinator as a project manager.

## Decision

Redesign `/team-work` so the root agent is the driver and the team is an
extension of its own reasoning:

1. The coordinator is the assistant. It delegates concrete, current actions to
   subagents (`team-researcher`, `team-architect`, `team-implementer`,
   `team-reviewer`, `team-verifier`, `team-quality-manager`) as needed.
2. The task stays whole. Do not split it into independent work packages for
   different agents. Parallel execution is allowed only when scopes are
   provably disjoint (different files or different lenses).
3. The plan is optional and is carried in the coordinator's prompt rather than
   forcing every subagent to read `docs/plans/<task>.md`. If the coordinator
   wants a plan file, it can ask `team-architect` to create one, and then it
   passes the content in the prompt.
4. Subagents must stop and report when a required file is missing; they must
   not loop on `read` or `glob`.
5. Update `team-implementer` permissions to include `config/**`, `skills/**`,
   and `agents/**` so it can write in the Devin harness repo and normal
   `config/` directories.

## Rationale

- **Root-as-driver**: The assistant is the only agent with full context of the
  user's intent and the conversation. A rigid pipeline forces the assistant to
  act as a project manager and loses the feeling of the assistant doing the
  work.
- **No missing-file loops**: Passing the plan in the prompt removes a whole
  class of "file not found" failures and makes the workflow more robust.
- **Permission coverage**: The Devin harness repo stores code under `skills/`
  and `agents/`. Normal projects also use `config/`. The implementer must be
  able to write there to be useful for the harness itself.
- **Peer review**: Reviewers still review implementers, and the coordinator can
  run multiple reviewers with different lenses, preserving the peer-review
  benefit.

## Alternatives Considered

- **Keep the pipeline but add retries and permissions**: Rejected because it
  keeps the wrong abstraction. The user wants team collaboration, not project
  management.
- **Create a new skill `/team-collab` and leave `/team-work` as-is**: Rejected
  because it fragments the harness and `team-work` is already the intended
  collaboration skill.
- **Remove all subagents and do everything as a single agent**: Rejected
  because the user explicitly wants a team that reviews and distributes work.

## Consequences

**Positive**
- `/team-work` can now be used on the Devin harness repo (`skills/`,
  `agents/`, `config/`).
- Subagents stop on missing files instead of looping.
- The coordinator can use the team organically, like extra pairs of hands,
  rather than as a fixed assembly line.
- The workflow is shorter and less likely to hang.

**Negative / Risks**
- The coordinator has more discretion, which requires the model to be good at
  deciding when to delegate and when to act directly.
- Broadening `team-implementer` write paths to `agents/**` and `skills/**`
  lets it modify agent profiles, which are security-related. This is mitigated
  by the hard rule that forbids editing `AGENTS.md`, `config.json`, and
  `rules/`, and by the fact that profile changes only take effect on the next
  Devin startup.
- `docs/plans/` and `docs/amendments/` become optional. Projects that want
  mandatory plan artifacts must enforce that outside of `/team-work`.

## Related

- `ADR-0004` — original team-work collaboration decision.
- `skills/team-work/SKILL.md` — main skill definition.
- `agents/team-*/AGENT.md` — subagent role profiles.
