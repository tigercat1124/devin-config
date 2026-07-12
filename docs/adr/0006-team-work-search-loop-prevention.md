# ADR-0006: team-work search-loop prevention

## Status

Accepted

## Context

After redesigning `/team-work` in ADR-0005, subagents still hung while trying to
locate files. The redesign removed the rigid pipeline and made the plan
optional, but it did not remove the impulse for read-only roles to perform
broad, open-ended searches. In practice a subagent asked to plan or research
would repeatedly scan directories with all-matching patterns (`*`, `.`, `^`)
instead of stopping or asking the coordinator.

The missing-file/no-retry rule was also duplicated in every subagent profile.
Because the wording differed slightly, some profiles still allowed implicit
"search until found" behavior, and updates to the rule had to be applied in
multiple places.

## Decision

1. **Centralize subagent file-search and missing-file rules in `AGENTS.md`.**
   All subagents inherit a single set of hard limits:
   - Do not retry a failed `read` or search more than once.
   - Do not run broad directory scans with all-matching patterns (`*`, `.`, `^`).
   - Use at most three `grep`/`glob` calls per task.
   - If the coordinator provides specific files, read those; otherwise do a
     single targeted search and stop.
2. **Make `team-architect` a non-searching role.** It reads the task and any
   context the coordinator provides, then produces a design. If context is
   insufficient, it reports what is missing instead of exploring the repo.
3. **Strengthen `team-researcher` search limits.** It performs at most two
   targeted searches with concrete terms and stops if nothing relevant is found.
4. **Simplify and deduplicate per-agent hard rules.** Each profile references
   the global subagent rules for missing-file handling rather than restating
   them.
5. **Clean up the `team-work` skill definition.** Remove redundant permissions,
   clarify the loop limit, and tell the coordinator not to give read-only roles
   open-ended "find files" tasks.

## Rationale

- **Feedforward prevention**: A global, explicit search budget is easier for a
  subagent to follow than per-role reminders. It also removes the ambiguity that
  leads to all-matching scans.
- **Single source of truth**: Centralizing the missing-file rule makes the
  harness consistent and reduces the chance that an update is applied only to
  some profiles.
- **Architect does not need to search**: The coordinator already knows which
  files matter; the architect's job is design, not discovery. Removing its search
  step eliminates a common hang point.
- **Small profile cleanup**: Removing duplicated text and redundant permissions
  makes the profiles shorter and less likely to contradict each other.

## Alternatives Considered

- **Keep per-agent rules and add more "do not loop" reminders**: Rejected
  because duplication had already produced inconsistent rules, and more text
  had not prevented the hang.
- **Remove `glob`/`grep` from read-only roles entirely**: Rejected because
  `team-researcher` legitimately needs to search; the fix is to bound the
  searches, not eliminate them.
- **Trust the coordinator to avoid broad prompts**: Rejected because the
  coordinator is also an LLM and can issue ambiguous instructions; explicit
  subagent limits are a necessary safety net.

## Consequences

**Positive**
- Subagents stop searching after explicit limits, preventing the file-search
  hang.
- Missing-file handling is consistent across all `team-work` roles.
- The `team-work` skill and agent profiles are shorter and easier to maintain.

**Negative / Risks**
- Adding global subagent rules to `AGENTS.md` slightly couples `team-work`
  concerns to the global rule file. This is acceptable because the rules are
  generic enough to apply to any subagent.
- Profile changes only take effect after Devin restarts, so the user must
  restart to see the fix.

## Related

- `ADR-0005` — original peer-collaborative redesign.
- `skills/team-work/SKILL.md`
- `agents/team-*/AGENT.md`
