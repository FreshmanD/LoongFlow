---
name: loongflow-architecture
description: "Reference guide for the three-tier independent agent architecture (simple/standard/advanced)"
user-invocable: false
---

# Agent Architecture Reference

## When to Use This Skill
Use this skill when deciding which architecture tier to recommend for a user's task, or when you need detailed information about each tier's capabilities and configuration.

## Architecture Tiers Overview

| Tier | Description | Examples | Run Command |
|------|-------------|---------|-------------|
| **simple** | Standalone tool-calling agent with ReAct loop and persistent memory | Chatbots, weather queries, format conversion | `pip install -r requirements.txt && python run/run_agent.py` |
| **standard** | Self-improving agent with memory, self-evaluation, and iterative improvement loop | Code review, document generation, data analysis pipelines | `pip install -r requirements.txt && python run/run_agent.py` |
| **advanced** | Evolutionary agent with plan-execute-evaluate-summarize loop, using loongflow-memory for solution management | Math puzzles, algorithm optimization, NP-hard problems | `pip install -r requirements.txt && python run/run_agent.py` |

## Complexity Assessment Matrix

Answer these questions to determine the right tier:

1. **Does the task require iterative optimization?**
   - Yes → standard or advanced
   - No → possibly simple

2. **Does the task have a clear numerical scoring metric?**
   - Yes → advanced (evolution-based optimization)
   - No → simple or standard

3. **Does the task involve code/file generation?**
   - Yes → standard
   - No → might be simple

4. **Does the task only need simple tool calls and conversation?**
   - Yes → simple
   - No → standard or advanced

## Decision Flowchart

```
Task Analysis
├── Only needs conversation + simple tools? → SIMPLE
├── Needs file operations or code generation?
│   ├── Has numerical evaluation metric? → ADVANCED
│   └── No numerical metric? → STANDARD
└── Needs iterative optimization?
    ├── Has clear scoring function? → ADVANCED
    └── Qualitative improvement? → STANDARD
```

## config.yaml Examples

### SIMPLE / STANDARD Tier Config
```yaml
llm:
  model: "openai/gpt-4o"
  api_key: "your-api-key"
  base_url: "https://api.example.com/v1"

agent:
  max_iterations: 10
  memory_path: "./data/memory.json"
```

### ADVANCED Tier Config
```yaml
llm:
  model: "openai/gpt-4o"
  api_key: "your-api-key"
  base_url: "https://api.example.com/v1"

agent:
  max_iterations: 200
  memory_path: "./data/memory.json"

eval:
  program: "eval/eval_program.py"
  metric: "score"
```

## Project Structure (All Tiers)

All tiers generate standalone Python projects with the following structure:

```
projects/<project_id>/
├── agent/
│   ├── core.py           # Core agent logic (varies by tier)
│   └── memory.py         # Persistent memory module
├── tools/                # Tool implementations
├── skills/               # Skill definitions
├── run/
│   └── run_agent.py      # CLI entry point
├── tests/                # Test suite
├── data/                 # Data directory
├── config.yaml           # Runtime configuration
└── requirements.txt      # Dependencies
```

**STANDARD** adds self-evaluation and iterative improvement logic in `agent/core.py`.
**ADVANCED** adds evolution loop in `agent/core.py` and `eval/eval_program.py` for numerical scoring.

## Key Differences Summary

| Feature | Simple | Standard | Advanced |
|---------|--------|----------|----------|
| Architecture | ReAct loop + memory | ReAct + self-evaluation + iterative improvement | Plan-execute-evaluate-summarize evolution loop |
| Self-Evaluation | No | Yes (in core.py) | Yes (via eval/eval_program.py) |
| Memory | Persistent file-based | Persistent with improvement tracking | loongflow-memory for solution management |
| Iterations | Single run | Iterative self-improvement | 200+ evolutionary |
| Output | Conversation/results | Improved files/code | Optimized solution |

## Related Skills

- **`loongflow`**: Main entry point for PEES iterative problem solving. Use this skill to start any iterative optimization task — it advises on mode selection and runs native PEES iterations.
- **`loongflow-engine`**: Orchestrates the full LoongFlow evolutionary engine for complex tasks. Automatically invoked by `loongflow` when the user chooses engine mode.
