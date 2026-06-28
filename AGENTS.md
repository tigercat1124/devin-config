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

## Product & Implementation Stance

When building a product, do NOT implement from scratch. First imitate existing
tools or services that solve a similar problem, then articulate:

- **Reference points worth adopting** — what the existing tool does well.
- **Differentiation points** — what makes the product you are launching
  distinct, and why users would choose it over the reference.

At implementation time, prefer composing existing OSS and libraries over
reimplementing functionality, to reduce effort and long-term maintenance cost.
Pay close attention to license terms and service terms of any dependency or
referenced service before adopting it; when in doubt, surface the concern to
the user rather than proceeding.

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
