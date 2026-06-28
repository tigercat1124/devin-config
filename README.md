# devin-config

A template configuration for [Devin CLI](https://devin.ai) with a structured harness engineering approach.

## What's Included

```
.
├── AGENTS.md                          # Global agent rules
├── config.json                        # Devin CLI configuration
├── rules/
│   ├── auto-mode.md                   # Pseudo Auto-Mode safety layer
│   └── harness-engineering.md         # Harness engineering principles
└── skills/
    ├── adr-create/                    # Create Architecture Decision Records
    ├── dig/                           # Deep exploratory interview skill
    ├── kiro-debug/                    # Root-cause-first debugging
    ├── kiro-discovery/                # Entry point for new work decomposition
    ├── kiro-impl/                     # TDD implementation with subagent dispatch
    ├── kiro-review/                   # Adversarial task review
    ├── kiro-spec-batch/               # Batch spec generation
    ├── kiro-spec-design/              # Technical design generation
    ├── kiro-spec-init/                # Spec initialization
    ├── kiro-spec-quick/               # Quick spec generation
    ├── kiro-spec-requirements/        # Requirements generation
    ├── kiro-spec-status/              # Spec progress status
    ├── kiro-spec-tasks/               # Implementation task generation
    ├── kiro-steering/                 # Persistent project knowledge (.kiro/steering/)
    ├── kiro-steering-custom/          # Custom steering documents
    ├── kiro-validate-design/          # Design quality review
    ├── kiro-validate-gap/             # Implementation gap analysis
    ├── kiro-validate-impl/            # Post-implementation integration check
    └── kiro-verify-completion/        # Completion verification with fresh evidence
```

## Key Features

### Safety Layer (Pseudo Auto-Mode)
`rules/auto-mode.md` implements a Claude Code "Auto mode"-style safety layer on top of Devin CLI's permission system. It defines a 4-category hard-deny list and classifier-style judgment rules the agent applies before every shell command or file write.

### Harness Engineering
`rules/harness-engineering.md` treats agent scaffolding (prompts, tools, skills, hooks) as a first-class engineered artifact. Key tenets:
- Pair **feedforward guides** with **feedback sensors**
- Prefer **computational** (deterministic) controls over **inferential** (LLM-as-judge)
- Fix recurring issues in the **outer loop** (harness), not just the symptom

### Kiro Spec Workflow
A full spec-driven development workflow adapted from the Kiro IDE:

```
@kiro-discovery       # Discover and decompose work
    ↓
@kiro-spec-init       # Initialize spec
    ↓
@kiro-spec-requirements   # Generate requirements (EARS format)
    ↓
@kiro-spec-design         # Generate technical design
    ↓
@kiro-spec-tasks          # Generate implementation tasks
    ↓
@kiro-impl                # TDD implementation with subagent dispatch
    ↓
@kiro-validate-impl       # GO/NO-GO integration gate
```

### ADR (Architecture Decision Records)
Every non-trivial change is documented in `docs/adr/` using the `adr-create` skill.

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
