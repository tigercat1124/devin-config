# ADR-0004: team-work as Team Collaboration Workflow

## Status

Accepted

## Context

The `team-code` skill was originally designed as a feature-implementation
workflow: a coordinator receives a feature description, runs sequential phases
(research, plan, implement, review, verify, quality gate), and reports a single
commit. The role names, plan artifacts, and phase language all assume the user
is building a software feature.

The user wants a team-working workflow with a name that clearly signals
collaboration rather than only code: multiple agents working in parallel,
reviewing each other's output, and collaborating as a team on any task, not just
implementation. This means the skill must handle general tasks (documentation,
configuration, research, planning, etc.) in addition to implementation, and it
must make parallel execution and peer review first-class concerns.

## Decision

Rename the skill from `team-code` to `team-work` and generalize it from a
feature-implementation workflow into a team collaboration workflow:

1. Rename the skill to `team-work` and update `AGENTS.md` and the subagent
   prompts to reference `/team-work`.
2. Keep the existing subagent profile names (`team-researcher`,
   `team-architect`, `team-implementer`, `team-reviewer`, `team-verifier`,
   `team-quality-manager`) to avoid breaking references and requiring profile
   reloads.
3. Replace feature-specific language with task-specific language throughout the
   skill and subagent prompts (`feature` → `task`, `feature-name` → `task-name`).
4. Rename the `Implement` phase to `Work` and broaden `team-implementer` to
   execute any planned task (code, docs, config, etc.) and produce tests or
   verification where applicable.
5. Emphasize parallel execution: after the plan is ready, the coordinator may
   run independent work packages and reviews in parallel when their file scopes
   are provably disjoint.
6. Allow the review phase to be run by multiple reviewers or lenses in parallel
   so the team can perform peer review from several perspectives.
7. Update `AGENTS.md` so the team-collaboration rules are task-agnostic and
   mention parallel work and peer review.
8. Keep the existing quality gate and amendment proposal mechanics; they already
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
- **Name clarity**: `team-work` better communicates that the skill is for team
  collaboration, not just coding. Keeping the subagent profile names unchanged
  avoids the churn of renaming every reference and forcing a Devin restart.

## Alternatives Considered

- **Keep the skill name `team-code` and only update descriptions**: Rejected
  because the name still strongly signals "code," which is narrower than the
  intended collaboration workflow.
- **Rename `team-code` to `team-work` and also rename subagent profiles to
  `team-worker-*`**: Rejected because it breaks every existing reference in
  `AGENTS.md`, ADRs, and skill prompts, and requires a Devin restart to reload
  profiles.
- **Create a separate `team-review` or `team-collab` skill**: Rejected because it
  fragments the workflow and duplicates the coordinator logic. The existing
  structure already supports the requested behavior once the language is
  generalized and the skill is renamed.
- **Keep the skill unchanged**: Rejected because it does not satisfy the user
  request and continues to frame every invocation as a code feature.

## Consequences

**Positive**
- `team-work` can now orchestrate arbitrary team tasks, not just code features.
- The skill name clearly signals collaboration rather than implementation.
- Parallel work and peer review are explicit parts of the workflow.
- Existing subagent profile names and tooling continue to work without renaming
  or profile reloads.

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

- `skills/team-work/SKILL.md` — main skill definition
- `agents/team-*/AGENT.md` — subagent role profiles
- `AGENTS.md` — global team-collaboration rules
- `docs/adr/0003-model-separation-for-code-tasks.md` — model assignment for code
  roles

---

## Update (2026-07-11): auto-dispatch rule added to `AGENTS.md`

### Change

Added an explicit auto-dispatch rule in `AGENTS.md` (`Team-Based Agent Collaboration` → `Auto-dispatch rule`). The root agent now must decide whether to invoke `/team-work` before starting a task, using the same criteria that previously lived only in the "When to use team-based work" list.

### Rationale

Previously, the root agent had to remember or infer when to call `/team-work`. The decision criteria were present but not framed as a harness-level dispatch rule. By promoting them to an auto-dispatch rule, the harness loads `team-work` automatically when the task is non-trivial, spans multiple files, requires an ADR, or is explicitly team-oriented. This keeps the decision in the outer-loop harness instead of relying on the inner-loop model prompt.

### Consequences

- Trivial fixes (typos, one-line fixes, formatting) still use a single agent for speed.
- Non-trivial work is more consistently routed through `/team-work`.
- The root agent must perform the dispatch check before acting, which adds a small feedforward step but reduces uncoordinated single-agent work.
