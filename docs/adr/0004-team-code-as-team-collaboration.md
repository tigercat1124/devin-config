# ADR-0004: team-code as Team Collaboration Workflow

## Status

Accepted

## Context

The `team-code` skill was originally designed as a feature-implementation
workflow: a coordinator receives a feature description, runs sequential phases
(research, plan, implement, review, verify, quality gate), and reports a single
commit. The role names, plan artifacts, and phase language all assume the user
is building a software feature.

The user wants `team-code` to support a broader team-working pattern: multiple
agents working in parallel, reviewing each other's output, and collaborating as a
team rather than only producing a code feature. This means the skill must handle
general tasks (documentation, configuration, research, planning, etc.) in
addition to implementation, and it must make parallel execution and peer review
first-class concerns.

## Decision

Generalize `team-code` from a feature-implementation workflow into a team
collaboration workflow:

1. Keep the skill name `team-code` and the existing subagent profile names to
   avoid breaking existing references and requiring profile reloads.
2. Replace feature-specific language with task-specific language throughout the
   skill and subagent prompts (`feature` → `task`, `feature-name` → `task-name`).
3. Rename the `Implement` phase to `Work` and broaden `team-implementer` to
   execute any planned task (code, docs, config, etc.) and produce tests or
   verification where applicable.
4. Emphasize parallel execution: after the plan is ready, the coordinator may
   run independent work packages and reviews in parallel when their file scopes
   are provably disjoint.
5. Allow the review phase to be run by multiple reviewers or lenses in parallel
   so the team can perform peer review from several perspectives.
6. Update `AGENTS.md` so the team-collaboration rules are task-agnostic and
   mention parallel work and peer review.
7. Keep the existing quality gate and amendment proposal mechanics; they already
   generalize to any artifact.

## Rationale

- **Task generality**: Not every team task is a feature. Configuration changes,
  documentation, ADRs, and research all benefit from the same research → plan →
  work → review → verify structure.
- **Parallelism**: Independent work packages can be executed concurrently,
  reducing wall-clock time. The existing "provably disjoint" rule is the right
  guardrail and is now made more explicit.
- **Peer review**: Running review in parallel with multiple lenses catches more
  issues than a single reviewer and mirrors how teams actually work.
- **Minimal churn**: Renaming the skill or profiles to `team-work` or
  `team-worker` would be cleaner semantically but would break every existing
  reference and require a Devin restart to reload profiles. The broader meaning
  is captured by updating descriptions and prompts instead.

## Alternatives Considered

- **Rename `team-code` to `team-work` and `team-implementer` to `team-worker`**:
  Rejected because it breaks existing references in `AGENTS.md`, ADRs, and user
  aliases, and requires a Devin restart to reload profiles.
- **Create a separate `team-review` or `team-collab` skill**: Rejected because it
  fragments the workflow and duplicates the coordinator logic. The existing
  `team-code` structure already supports the requested behavior once the
  language is generalized.
- **Keep the skill unchanged**: Rejected because it does not satisfy the user
  request and continues to frame every invocation as a code feature.

## Consequences

**Positive**
- `team-code` can now orchestrate arbitrary team tasks, not just code features.
- Parallel work and peer review are explicit parts of the workflow.
- Existing users and tooling continue to work without renaming or profile
  reloads.

**Negative / Risks**
- The role name `team-implementer` still has a code connotation. This is
  mitigated by broadening its description, but a future rename may be needed if
  non-code usage becomes dominant.
- Parallel execution requires the coordinator to verify scope disjointness; an
  incorrect parallelization decision could cause file conflicts.
- The quality gate still assumes code-style verification when available. For
  non-code tasks, verification may be "not run" and the gate must handle that
  gracefully.

## Related

- `skills/team-code/SKILL.md` — main skill definition
- `agents/team-*/AGENT.md` — subagent role profiles
- `AGENTS.md` — global team-collaboration rules
- `docs/adr/0003-model-separation-for-code-tasks.md` — model assignment for code
  roles
