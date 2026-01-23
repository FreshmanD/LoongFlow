# General Agent for LoongFlow

## Overview
General Agent is a flexible, general-purpose agent framework built on LoongFlow's Plan-Execute-Summary (PES) paradigm. It supports skill-based execution and can handle a wide variety of tasks.

## Quick Start

### 1. Setup Environment
```bash
cd LoongFlow
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

### 2. Configure API Keys
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run a Task
```bash
# Run hello_world example
./run_general.sh hello_world

# Run in background
./run_general.sh hello_world --background

# With custom options
./run_general.sh hello_world --log-level DEBUG --max-iterations 100
```

### 4. Monitor Progress
- **Foreground**: Output appears in terminal
- **Background**: Check logs at `agents/general_agent/examples/hello_world/run.log`
- **Stop background task**: `./run_general.sh stop hello_world`

## Example Structure
Each example in `examples/` should have:
```
task_name/
├── task_config.yaml          # Main configuration
├── .claude/
│   └── skills/              # Claude skills (optional)
│       ├── skill1/
│       │   └── *.py         # Skill files
│       └── skill2/
└── run.log                  # Generated logs
```

## Features

### Skill System
Skills are loaded from `examples/{task}/.claude/skills/` and copied to the working directory. Skills referenced in the config are automatically loaded.

Example config:
```yaml
planners:
  general_planner:
    skills: ["file_io", "data_processing"]
```

### Example Name Propagation
The example name (task_name) is automatically added to the task description and available as `context.task.get("example_name")` in agents.

### Flexible Configuration
- Custom LLM providers (OpenAI, Gemini, DeepSeek)
- Adjustable iteration limits and target scores
- Configurable logging levels and output paths

## Creating New Examples

1. **Create directory**: `mkdir examples/new_task`
2. **Add config**: Create `examples/new_task/task_config.yaml`
3. **Add skills** (optional): `examples/new_task/.claude/skills/`
4. **Run**: `./run_general.sh new_task`

## Key Configuration Options

### LLM Configuration
```yaml
llm_config:
  url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key: "${OPENAI_API_KEY}"
```

### Evolution Settings
```yaml
evolve:
  task: "Your task description"
  max_iterations: 100
  target_score: 0.9
  concurrency: 5
```

### Skills Reference
Skills must be listed in the agent configuration to be automatically loaded:
```yaml
skills: ["file_io", "data_processing", "custom_tool"]
```

For more details, see the [LoongFlow documentation](AGENTS.md).