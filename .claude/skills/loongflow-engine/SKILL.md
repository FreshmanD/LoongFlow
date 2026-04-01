---
name: loongflow-engine
description: "Orchestrates the LoongFlow evolutionary engine for complex tasks. Downloads LoongFlow, configures general_agent, launches background evolution, and monitors progress via cron. Invoked by the loongflow skill when user chooses engine mode."
---

# LoongFlow Engine Orchestrator

This skill sets up and runs the LoongFlow evolutionary optimization engine for complex tasks that benefit from population-based evolution, multi-island diversity, and many iterations.

**Important:** `general_agent` only supports Anthropic models. Ensure `ANTHROPIC_API_KEY` is set.

## Step 1: Check Prerequisites

Before proceeding, verify:

1. **Python 3.12+** is available:
   ```bash
   python3 --version
   ```
   If not available, tell the user to install Python 3.12+.

2. **ANTHROPIC_API_KEY** is set:
   ```bash
   echo $ANTHROPIC_API_KEY | head -c 10
   ```
   If empty, tell the user:
   > LoongFlow's general_agent requires an Anthropic API key. Please set it:
   > `export ANTHROPIC_API_KEY="your-key-here"`

3. **uv** is available (preferred) or fall back to pip:
   ```bash
   which uv || echo "uv not found, will use pip"
   ```

## Step 2: Download and Install LoongFlow

Check if LoongFlow is already installed locally. If not, download and install:

```bash
# Choose install location
LOONGFLOW_DIR="${HOME}/.loongflow/engine"

# Clone if not already present
if [ ! -d "$LOONGFLOW_DIR" ]; then
    git clone https://github.com/baidu-baige/LoongFlow "$LOONGFLOW_DIR"
fi

# Create virtual environment and install
cd "$LOONGFLOW_DIR"
git pull origin main

# Prefer uv, fall back to pip
if command -v uv &> /dev/null; then
    uv venv .venv --python 3.12
    source .venv/bin/activate
    uv pip install -e .
else
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
fi
```

## Step 3: Configure the Task

Create a task directory and generate `task_config.yaml`:

```bash
TASK_SLUG="<task-slug>"  # kebab-case name from user's task
TASK_DIR="$LOONGFLOW_DIR/agents/general_agent/examples/$TASK_SLUG"
mkdir -p "$TASK_DIR"
```

### Generate task_config.yaml

Adapt the following template based on the user's task. Key fields to customize:
- `evolve.task`: The user's detailed task description
- `evolve.max_iterations`: Higher for harder problems (default: 50)
- `evolve.target_score`: The target quality threshold (default: 0.9)
- `evolve.evaluator.timeout`: Longer for complex evaluations (default: 600s)

```yaml
workspace_path: "./output-<task-slug>"

llm_config:
  model: "anthropic/claude-sonnet-4-20250514"

planners:
  general_planner:
    permission_mode: "acceptEdits"
    max_turns: 30

executors:
  general_executor:
    permission_mode: "acceptEdits"
    max_turns: 50

summarizers:
  general_summarizer:
    permission_mode: "acceptEdits"
    max_turns: 30

evolve:
  task: |
    <INSERT USER'S TASK DESCRIPTION HERE>
  planner_name: "general_planner"
  executor_name: "general_executor"
  summary_name: "general_summarizer"
  max_iterations: 50
  target_score: 0.9
  concurrency: 1
  evaluator:
    timeout: 600
    agent:
      permission_mode: "acceptEdits"
      max_turns: 30
  database:
    storage_type: "in_memory"
    num_islands: 1
    population_size: 50
    checkpoint_interval: 5
    sampling_weight_power: 2
```

### Copy User Files

If the user has source code, data files, or evaluation scripts relevant to the task, copy them into the task directory:

```bash
# Copy user's files if provided
cp -r <user-files> "$TASK_DIR/"
```

If the user provides a custom evaluation script, save it as `eval_program.py` in the task directory. It must implement:

```python
def evaluate(solution_path: str) -> dict:
    return {
        "status": "success",
        "score": 0.0,  # 0.0 to 1.0
        "summary": "Description of evaluation result",
        "metrics": {},
        "artifacts": {}
    }
```

## Step 4: Launch Evolution

```bash
cd "$LOONGFLOW_DIR"
source .venv/bin/activate
./run_general.sh "$TASK_SLUG" --background
```

Confirm launch by checking:
```bash
cat "$LOONGFLOW_DIR/agents/general_agent/examples/$TASK_SLUG/.run.pid"
tail -20 "$LOONGFLOW_DIR/agents/general_agent/examples/$TASK_SLUG/run.log"
```

Tell the user:
> LoongFlow evolution started in background for task `<task-slug>`.
> PID: `<pid>`, Log: `<log-path>`

## Step 5: Set Up Monitoring

Create a cron task that checks progress every 5 minutes. The monitoring script should:

1. **Check if the process is still running** via PID file
2. **Read the latest log entries** for progress updates
3. **Check checkpoints** for best score
4. **Report to user** when:
   - Evolution completes (process exits)
   - Target score is reached
   - A significant score improvement occurs (delta > 0.1)
   - An error occurs

### Monitoring Script Logic

```bash
TASK_SLUG="<task-slug>"
LOONGFLOW_DIR="${HOME}/.loongflow/engine"
TASK_DIR="$LOONGFLOW_DIR/agents/general_agent/examples/$TASK_SLUG"
PID_FILE="$TASK_DIR/.run.pid"
LOG_FILE="$TASK_DIR/run.log"

# Check if process is still running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "COMPLETED: Evolution process finished"
        # Read final results from log
        tail -50 "$LOG_FILE"
        exit 0
    fi
fi

# Check latest progress from log
tail -20 "$LOG_FILE" | grep -E "(best_score|iteration|completed|error)"
```

### On Completion

When evolution finishes, report to the user:
- **Best score** achieved
- **Solution location**: path to best solution files
- **Iteration count**: total iterations completed
- **Cost**: total token cost if available
- **How to view**: `tail -100 <log-path>` for full details

### Stopping a Task

If the user wants to stop the evolution:
```bash
cd "$LOONGFLOW_DIR"
./run_general.sh stop "$TASK_SLUG"
```
