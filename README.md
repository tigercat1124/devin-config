# devin-config

A template configuration for [Devin CLI](https://devin.ai) with a structured harness engineering approach.

## What's Included

```
.
├── AGENTS.md                          # Global agent rules
├── config.json                        # Devin CLI configuration
├── agents/
│   ├── code-worker/                   # Code subagent profile
│   └── simplify-reviewer/             # Read-only cleanup reviewer
├── hooks/
│   └── deny-guard.py                  # PreToolUse hard-deny hook
├── rules/
│   └── harness-engineering.md         # Harness engineering principles
└── skills/
    ├── delegate/                      # Run a task in a fresh subagent
    ├── dig/                           # Deep exploratory interview skill
    ├── genshijin/                     # Compressed replies (ultra-terse Japanese)
    ├── roadmap/                       # Phased roadmap documents
    └── simplify/                      # Cleanup-only code review (4 parallel reviewers)
```

## Key Features

### Safety Layer (deny-guard)
`hooks/deny-guard.py` is a `PreToolUse` command hook registered in
`config.json`. It deterministically blocks catastrophic commands (`rm` on
root/home/`.git`/wildcards, fork bombs, `curl|sh`, block-device writes,
force-push/delete on `main`/`master`, credential-path writes) that the
prefix-matched `permissions.deny` list cannot express. Softer operations
stay governed by `permissions.ask`.

### Harness Engineering
`rules/harness-engineering.md` treats agent scaffolding (prompts, tools, skills, hooks) as a first-class engineered artifact. Key tenets:
- Pair **feedforward guides** with **feedback sensors**
- Prefer **computational** (deterministic) controls over **inferential** (LLM-as-judge)
- Fix recurring issues in the **outer loop** (harness), not just the symptom

### Simplify (Cleanup-Only Review)
Ported from Claude Code's `/simplify`. Reviews changed code for cleanup opportunities
with four parallel read-only reviewers (reuse, simplification, efficiency,
abstraction-level), then applies the reconciled fixes and auto-commits. Does not
hunt for correctness bugs. See `docs/adr/0002-port-simplify-from-claude-code.md`
for the port rationale (the `batch` skill was considered but dropped because
Devin has no worktree isolation).

### ADR (Architecture Decision Records)
Every non-trivial change is documented in `docs/adr/`; format requirements
live in `AGENTS.md`.

### Model Configuration
All agents (root and subagents) run on the session model — currently
**SWE-2 High** via `config.json` `agent.model`. Per-role model overrides were
removed on 2026-09-16; see `docs/adr/0003-model-separation-for-code-tasks.md`
(superseded) for the previous design.

**Important:** Custom subagent profiles are loaded at devin process startup.
Always restart devin after creating or modifying `agents/*/AGENT.md` files.

## Usage

### As a Template
1. Click **"Use this template"** on GitHub to create your own copy
2. Copy the files to `~/.config/devin/`
3. Run `devin` — the rules and skills load automatically

### Manual Setup
```bash
# Clone to your Devin config directory
git clone https://github.com/tigercat1124/devin-config ~/.config/devin
```

> **Note**: `config.json` contains personal settings (`org_id`, `theme_mode`, etc.). After copying, run Devin CLI once to let it populate your own `org_id`.

## Communication Language

This config sets Devin to:
- **Think** in English (internal reasoning)
- **Reply** in Japanese (user-facing output)
- Keep code, commits, and technical artifacts in English

Adjust the `Communication Language` section in `AGENTS.md` to match your preferred language.

## License

MIT
