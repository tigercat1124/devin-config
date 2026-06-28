# Harness Engineering

**Agent = Model + Harness. If you are not the model, you are the harness.**
The harness is every piece of code, configuration, and execution logic wrapped
around the model so it can actually finish something: system prompts,
`AGENTS.md`, skills, subagent prompts, tools, MCP servers, hooks, sandboxes,
orchestration logic, observability, and recovery paths. Treat the harness as a
first-class engineered artifact — version it, name each surface, reason about
what it is for, and change it with the same discipline applied to source code.
It is NOT a pile of dotfiles.

References that shaped this document:
- Viv Trivedy, "Anatomy of an Agent Harness" (coined the term)
- Birgitta Böckeler, "Harness engineering for coding agent users"
  (martinfowler.com, 2026-04)
- Addy Osmani, "Agent Harness Engineering" (oreilly.com)
- Anthropic engineering, long-running agent harness design

---

## Two control directions

- **Guides (feedforward)** — anticipate unwanted outputs and steer the agent
  BEFORE it acts. Increase the probability of a correct first attempt.
  Examples: `AGENTS.md`, skills, reference docs, how-tos, codemods, LSP.
- **Sensors (feedback)** — observe AFTER the agent acts and help it
  self-correct. Most powerful when their output is optimized for LLM
  consumption (e.g. custom linter messages that include fix instructions — a
  positive form of prompt injection). Examples: tests, linters, type checkers,
  structural tests, AI code review, logs, browser.

Feedforward-only = rules encoded but never verified. Feedback-only = the agent
keeps repeating the same mistakes. You need BOTH.

## Two execution types

- **Computational** — deterministic, fast, CPU-bound. Tests, linters, type
  checkers, structural analysis. Run in ms–s; results are reliable. Cheap
  enough to run on every change. PREFER these wherever possible.
- **Inferential** — semantic, GPU/NPU-bound, non-deterministic. AI code
  review, "LLM as judge". Slower and more expensive. Use for judgments
  computational sensors cannot make; do not rely on them as the only sensor
  for high-stakes decisions.

## Three regulation categories

When designing or improving a harness, classify each control by what it
regulates. The categories have different harnessability and difficulty:

1. **Maintainability harness** — internal code quality. EASIEST; lots of
   existing tooling (linters, complexity, coverage, structural tests,
   dependency scanners). Computational sensors catch the structural problems
   reliably; inferential sensors partially catch semantic ones
   (semantically duplicate code, brute-force fixes, over-engineering).
2. **Architecture fitness harness** — architecture characteristics / fitness
   functions. Performance budgets, module-boundary rules, observability
   standards, logging conventions. Feedforward the requirements via skills;
   feed back via performance tests, ArchUnit-style structural tests, drift
   detection.
3. **Behaviour harness** — does the application functionally behave as
   required? HARDEST. Spec as feedforward; test suite (computational +
   inferential) plus human review as feedback. Do NOT blindly trust
   AI-generated tests — combine with approved fixtures, mutation testing, and
   manual verification. Correctness is outside any sensor's remit if the human
   did not clearly specify what they wanted.

## The steering loop (outer loop)

The harness is improved BETWEEN sessions, not only within them. Three nested
loops:

- **Inner loop** — the agent in the code: model calling tools, reading files,
  proposing edits.
- **Middle loop (supervisory)** — human steers the agent: reads diffs,
  redirects, approves.
- **Outer loop (harness engineering)** — human (or an evolution agent)
  changes the harness surfaces so the inner and middle loops go better next
  time.

**When the same issue recurs, fix the harness, not just the symptom.** Ask:
at which loop does the fix belong? A one-off prompt tweak is inner loop. A
recurring failure pattern belongs in a guide (feedforward) or sensor
(feedback) in the outer loop.

## Keep quality left

Distribute sensors across the lifecycle by cost and speed:

- **Before commit / before integration** — fast computational sensors
  (lint, type check, fast tests, basic review agent). Run on every change.
- **Post-integration pipeline** — repeat the fast sensors PLUS expensive ones
  (mutation testing, broad architecture review, full integration tests).
- **Continuous / ambient** — drift detection (dead code, coverage quality,
  dependency scanners) and runtime feedback (SLOs, log anomalies, response
  quality sampling) running outside the change lifecycle.

The earlier an issue is caught, the cheaper it is to fix.

## Harnessability

Not every codebase is equally harnessable. "Ambient affordances" — structural
properties that make the codebase legible, navigable, and tractable to agents
— determine what controls are even available:

- Strong typing → type checking as a free sensor.
- Clear module boundaries → architectural constraint rules.
- Frameworks that abstract away detail → fewer footguns for the agent.
- Greenfield can bake harnessability in from day one; legacy with high
  technical debt is hardest to harness but often needs it most.

When making technology decisions, factor in harnessability, not just
developer ergonomics or runtime performance.

## Ashby's Law (requisite variety)

A regulator must have at least as much variety as the system it governs, and
can only regulate what it has a model of. An LLM agent can produce almost
anything; committing to a topology (service template, tech stack, module
layout) narrows the output space and makes a comprehensive harness achievable.
Defining topologies is a variety-reduction move — prefer constrained,
well-modeled structures over unconstrained ones.

## Operating rules for this agent

1. **Treat every harness surface as engineered.** Name it, document its
   purpose, version it. Do not let `AGENTS.md`, skills, or hooks accrete
   without intent.
2. **Pair every recurring failure with a control.** If a failure mode repeats,
   add a feedforward guide (prevent it) or a feedback sensor (catch it), and
   record the decision in an ADR.
3. **Prefer computational over inferential.** Use deterministic sensors
   wherever they can do the job; reserve inferential sensors for judgments
   computation cannot make.
4. **Keep guides and sensors in sync.** A guide that contradicts a sensor (or
   vice versa) erodes trust in both. When updating one, check the other.
5. **Make sensor output LLM-consumable.** Custom linters and review tools
   should emit actionable instructions, not just error codes, so the agent
   can self-correct in the same loop.
6. **Do not trust AI-generated tests alone for behaviour.** Combine with
   approved fixtures, mutation testing, and human verification for any
   behaviour that matters.
7. **Improve harnessability when touching the codebase.** Prefer strongly
   typed, well-bounded, framework-backed structures that give future
   harness controls something to grip.
8. **Surface harness gaps to the user.** When a failure category has no
   matching control, say so and propose a guide or sensor to add — do not
   silently work around it.
