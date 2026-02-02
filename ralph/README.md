# RALPH v2 — Autonomous Coding Loop

Single Claude Code skill (`/ralph`) that guides you from project init through autonomous execution.

## Installation

Copy `ralph.md` to the marketplace repo:

```bash
cp ralph.md /Users/work1618/code/_mararn1618-claude-marketplace/ralph.md
```

Then install as a Claude Code command:

```bash
cp ralph.md ~/.claude/commands/ralph.md
```

## Usage

```bash
cd my-project
claude

> /ralph          # auto-detects state, routes to correct phase
```

### Phases

| Phase | What happens | Output |
|-------|-------------|--------|
| **Init** | Creates `.ralph/` directory + templates | `.ralph/*` |
| **Research** | Interactive requirements discovery | `.ralph/requirements.md` |
| **Context** | Distill background knowledge | `.ralph/context.md` + sub-contexts |
| **Plan** | Atomic task breakdown | `.ralph/plan.md` |
| **Run** | Finalize agent instructions, print launch command | `.ralph/agent-instructions.md` |

Each `/ralph` invocation detects where you left off and picks up from there.

### Redo a Phase

```
> /ralph          # type "redo research", "redo context", "redo plan", or "redo run"
```

### Run the Loop

```bash
./.ralph/loop.sh
```

## Project Structure Created

```
project/
├── .ralph/
│   ├── to-human/              # AI -> Human (loop blocks if non-empty)
│   ├── to-ai/                 # Human -> AI (drop files, processed next iteration)
│   ├── originals/             # Raw files preserved after triage
│   ├── done/                  # Archive of processed items
│   ├── logs/                  # Per-iteration logs
│   ├── context/
│   │   ├── summaries/         # Distilled knowledge files
│   │   └── refs/              # Pointer files to originals
│   ├── requirements.md
│   ├── context.md
│   ├── plan.md
│   ├── agent-instructions.md
│   ├── loop.sh
│   └── progress.md
└── CLAUDE.md                  # Updated with .ralph/ pointer
```
