# ADR-0003: Model Separation — Code Tasks Use Kimi K2.7, Conversation/Planning Stays GLM 5.2

## Status

Accepted

## Context

The global default model in `config.json` was changed to `kimi-k2-7` via a runtime
`/model` switch. The user wants this configuration to persist, but only for
code-related tasks. Casual conversation, planning, and non-code tasks should
continue using the previous default model (`glm-5-2-max-1m`).

Devin CLI provides no conditional model routing based on task type; only:

- A global `agent.model` in `config.json`.
- A per-skill `model` frontmatter override.
- A per-subagent-profile `model` frontmatter override.
- Manual `/model` switching during a session.

Therefore, model separation must be implemented through skill and subagent
profile configuration, not a single global switch.

## Decision

1. Keep `config.json` `agent.model` as `glm-5-2-max-1m` for general conversation
   and planning.
2. Add `model: kimi-k2-7` to the `simplify` skill (a code-review/cleanup skill)
   so that it runs on Kimi when invoked.
3. Create a custom subagent profile `agents/code-worker/` with `model: kimi-k2-7`
   and tool permissions scoped to code work. This profile is used for code-heavy
   tasks that benefit from Kimi.
4. Document the model separation in `README.md` so users know which surfaces use
   which model.

## Rationale

- **Kimi K2.7 is selected for code tasks** because the user explicitly requested
  it and Devin's own benchmark (FrontierCode) shows Kimi K2.7 is competitive on
  real-world engineering tasks.
- **GLM 5.2 remains the default** because it was already the established default
  for conversation and planning, and the user wants to preserve that experience.
- **Per-skill / per-profile overrides** are the only Devin mechanism that can
  route a specific task to a specific model without manual `/model` switching.
- **No new conditional logic** is introduced; the agent chooses to invoke a skill
  or spawn a code-worker subagent based on the task, and Devin handles the model
  switch automatically.

## Alternatives Considered

- **Leave `agent.model` as `kimi-k2-7` globally**: Simple, but contradicts the
  user's desire to keep conversation/planning on the current model.
- **Use `adaptive` router**: Could auto-route code vs. conversation, but the user
  explicitly asked for a fixed model separation (Kimi for code, GLM otherwise),
  and Adaptive's routing decisions are not directly controllable.
- **Only use manual `/model` switching**: Does not persist and is error-prone.
- **Override `model` on every individual skill**: Feasible, but adding a dedicated
  `code-worker` subagent profile is more flexible for tasks that are not covered
  by a single skill.

## Consequences

**Positive**
- Code tasks transparently run on Kimi K2.7 while the main session stays on GLM 5.2.
- The separation is declared in configuration (skill frontmatter + subagent profile)
  rather than relying on runtime prompts or memory.
- Existing non-code skills (`adr-create`, `dig`) remain on the default GLM model.

**Negative / Risks**
- The root agent still uses GLM 5.2. For code-heavy work, the root agent must
  explicitly delegate to a skill or the `code-worker` subagent; otherwise the task
  runs on GLM. This is a harness behavior issue, not a configuration issue.
- If a user forgets to invoke `/simplify` or ask for `code-worker`, code tasks will
  run on GLM 5.2. Future harness improvements (e.g., an AGENTS.md rule) could
  mitigate this.
- Per-request model billing and context-window behavior differ between GLM 5.2
  and Kimi K2.7; users should be aware of which surface uses which model.

## Related

- Config: `config.json`
- Skill: `skills/simplify/SKILL.md`
- Profile: `agents/code-worker/AGENT.md`
- ADR-0002: `docs/adr/0002-port-simplify-from-claude-code.md`
