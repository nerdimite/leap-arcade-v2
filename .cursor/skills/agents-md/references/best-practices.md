# AGENTS.md Best Practices — Research & Sources

Reference material for the agents-md skill. Read this when you need to explain *why* a rule exists.

## Key Findings

Source: [HumanLayer — Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

### Auto-generated files hurt

- Auto-generated context files **reduce success rates by ~3%** while **increasing inference cost by 20%+**
- Stronger models don't generate better context files
- LLM-generated files are redundant with existing documentation the agent can already find

### Instruction following degrades uniformly

- Frontier thinking LLMs follow ~150-200 instructions with reasonable consistency
- Agent harness system prompts already consume ~50 instruction slots
- As instruction count increases, **all instructions are followed less** — not just the newer ones
- Smaller models show exponential decay in instruction-following; frontier models show linear decay

### What actually helps

- Tools mentioned in AGENTS.md get used **160x more often** than unmentioned tools
- Human-written files improve benchmark performance by ~4% (modest but real)
- Instructions ARE followed — but unnecessary ones make tasks harder by consuming instruction budget

### What doesn't help

- Codebase overviews don't help agents navigate faster
- Code style guidelines are better handled by linters (faster, cheaper, deterministic)
- Directory listings add tokens without improving agent performance

## The 300-Line Rule

General consensus: keep AGENTS.md under 300 lines. HumanLayer's production file is under 60 lines. Every line goes into every session — it's the highest-leverage file in the codebase, for better or worse.

## Progressive Disclosure

Instead of putting everything in AGENTS.md, keep task-specific docs in separate files and list them with brief descriptions. The agent reads them only when relevant, keeping the base context lean.

## LLM Context Window Dynamics

- LLMs bias toward instructions at the **peripheries** of the prompt (system message and most recent user message)
- Middle-of-context instructions get less attention
- Focused, relevant context outperforms large amounts of irrelevant context
- Claude Code injects a system reminder telling the model it may ignore CLAUDE.md contents if not relevant to the current task — overstuffed files get ignored more
