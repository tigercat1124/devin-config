# Global Rules

## Communication Language

- **Think in English**: All internal reasoning, planning, and chain-of-thought
  must be conducted in English. This keeps reasoning precise and consistent
  regardless of the user's language.
- **Reply in Japanese**: All user-facing output (prose, explanations, summaries,
  questions, error descriptions) must be written in Japanese unless the user
  explicitly requests another language.
- **Code, commits, and identifiers stay in English**: Source code, commit
  messages, branch names, ADRs, and other technical artifacts follow the
  codebase's existing language conventions (typically English). Do not
  translate code or technical writing into Japanese unless asked.
- **Quotes from files**: When citing file contents or command output, preserve
  the original language verbatim — do not translate them.

## Compressed Communication (genshijin)

At the start of every session, invoke the `/genshijin` skill (level: 通常 /
normal, unless the user specifies 丁寧 or 極限). This activates ultra-compressed
Japanese replies for the whole session: keep all technical content exact, drop
politeness filler and redundant particles. Deactivate only when the user says
「原始人やめて」or「通常モード」.

## Pseudo Auto-Mode (safety layer)

A Claude Code "Auto mode"-style safety layer is defined in a separate file to keep
this rules file concise. **Read and follow `~/.config/devin/rules/auto-mode.md` at the
start of every session**, and apply its self-regulation rules before every shell
command (`exec`) and file write (`edit`/`write`).

The mechanical `permissions.deny`/`ask` rules in `~/.config/devin/config.json` are
the first line of defense; `auto-mode.md` covers the judgment-based cases that
pattern-matching cannot catch.

## Decision Records (ADR)

For every non-trivial change, create an Architecture Decision Record in `docs/adr/`
before or alongside implementation. Use the `/adr-create` skill.

Exempt: trivial fixes such as typos, formatting, comments, or obvious one-line bug
fixes that change no design or behavior.

Every ADR must document:
- **Context**: what problem or requirement triggered the change
- **Decision**: what was chosen
- **Rationale**: why this choice was made
- **Alternatives considered**: other options examined and why they were rejected
- **Consequences**: expected trade-offs and risks

Link implementation code back to ADR IDs with comments such as:
- `// ADR-0001: <short-title>`
- `// See ADR-0001 for rationale`

## Research Documentation

Record reference material, surveyed tools/services, tool usage, investigation
logs, and benchmarks under `docs/research/{function_name}/**` so context that
ADRs depend on stays discoverable. Write incrementally, cite sources, date
entries, and cross-link from ADRs. See the `adr-create` skill for the full
writing rules.

## Roadmap Documents

For multi-step work, multi-target comparisons, PoCs, or feature rollouts,
create roadmap documents under `docs/roadmap/` with the `/roadmap` skill:

- A shared spec (`00-common-spec.md`) when multiple targets share unified
  requirements, mock data, or comparison criteria.
- One phased roadmap per target (`<target>.md`) with verifiable checkbox
  items, completed work marked, and a mandatory "既知の制約" section.
- Cross-link ADRs (`docs/adr/`) and research notes (`docs/research/`):
  roadmaps record *what and when*, ADRs record *why*.
- Keep roadmaps living: update checkboxes as phases complete, and update the
  shared spec first when requirements change.

Do not create roadmaps for single-step tasks — a session todo list suffices.

## Product & Implementation Stance

When building a product, do NOT implement from scratch. First imitate existing
tools or services that solve a similar problem, then articulate:

- **Reference points worth adopting** — what the existing tool does well.
- **Differentiation points** — what makes the product you are launching
  distinct, and why users would choose it over the reference.

At implementation time, prefer composing existing OSS and libraries over
reimplementing functionality, to reduce effort and long-term maintenance cost.
Pay close attention to license terms and service terms of any dependency or
referenced service before adopting it; when in doubt, surface the concern to the
user rather than proceeding.

## Lazy Mode for Implementation

When asked to implement, build, refactor, fix, review, or design code, start the
task by invoking the `/ponytail` skill (`/ponytail full` by default, or
`/ponytail lite|full|ultra` if the user specifies a level). This activates lazy
senior dev mode for the rest of the session: apply the YAGNI ladder, reuse
existing code, prefer the standard library / native platform / already-installed
dependencies, keep the diff minimal, and never cut validation, error handling,
security, or accessibility. Do not invoke `/ponytail` for non-coding requests
such as general knowledge, prose, translation, or summaries. To deactivate, say
"stop ponytail" or "normal mode".

## Harness Engineering

Harness engineering treats the scaffolding around the model (prompts, tools,
context policies, hooks, subagents, feedback loops, recovery paths) as a
first-class engineered artifact. **Read and follow
`~/.config/devin/rules/harness-engineering.md` at the start of every session**, and
apply its operating rules whenever you design or improve any harness surface
(`AGENTS.md`, skills, hooks, sensors, subagent prompts, MCP servers).

Core tenets (full detail in the referenced file):
- **Agent = Model + Harness.** If you are not the model, you are the harness.
- Pair **feedforward guides** with **feedback sensors**; either alone fails.
- Prefer **computational** (deterministic) controls over **inferential**
  (LLM-as-judge) wherever they can do the job.
- Classify controls by regulation category: **maintainability** (easiest),
  **architecture fitness**, **behaviour** (hardest — do not trust
  AI-generated tests alone).
- When the same issue recurs, fix the harness in the **outer loop**, not just
  the symptom in the inner loop.
- Surface harness gaps to the user; do not silently work around them.

## Subagent Rules

All subagents must follow these limits:

- Do not modify `AGENTS.md`, `~/.config/devin/config.json`, `rules/**`, or lockfiles unless explicitly asked.
- Do not retry a failed `read`, `grep`, or `glob` more than once.
- Do not run broad directory scans with all-matching patterns such as `*`, `.`, or `^`.
- Use at most three `grep`/`glob` calls per task.
- If specific files or paths are provided, read those only. If not, do a single targeted search with a concrete term, then stop and report if nothing is found.
- If a required file is missing, report the exact path and stop.

Custom subagent profiles are loaded at Devin startup. After adding or modifying `~/.config/devin/agents/` or `.devin/agents/`, restart Devin for the new profiles to be available.
