# ✨ PESAgent

PESAgent 是一个面向通用算法任务设计的进化范式，借鉴人类研究员的探索性工作模式，将单轮进化抽象为“Planner-Executor-Summary”三个阶段，通过进化记忆引导模型进行多轮迭代式探索，持续积累经验并驱动改进，有效提升新解决方案的质量与进化过程的确定性，缓解无效评估与随机试错问题，自动实现复杂任务高效率、低成本的持续进化。

<p align="center">
<img src="https://evolux-pub.bj.bcebos.com/share/evolve_agent_fr_v1.png" alt="LoongFlow Evolve Framework" width="80%"/>
</p>

- Planner：负责充分理解任务和全局进化状态，结合采样和相关历史进化经验，生成当前迭代的改进指导方案，为当前迭代生成专家级指导。
- Executor：负责实施生成新的解决方案，并进行方案评估、错误调试和针对性充分线性优化，产出规划方案指导下的最优解。
- Summary：负责对新产生的解决方案进行全面分析，总结成功和失败经验，为下次进化提供导向，并将本轮进化信息发布到进化记忆。

## 🚀 Quick Start

PESAgent 内置了一个针对通用算法任务进化的实现示例 MathPESAgent，我们已 packing_circle_in_unit_square 示例，您可以直接运行：

```bash
# Run your first evolve task, the evolution results are in the ./output directory
./run_math.sh packing_circle_in_unit_square --background

# Stop task
./run_math.sh stop packing_circle_in_unit_square
```

### 🛠️ Self-defined Task

在`agents/math_agent/examples`目录下，您可以新建文件夹创建自定义进化任务。对于一个进化任务，必须要包含 3 个文件。

- `task_config.yaml` (任务配置文件)：定义了任务目标、LLM 配置、三阶段设置、评估器设置等。
- `initial_program.py` (初始程序)：定义了任务初始的解决方案，为后续进化生成的新解决方案提供初始输入，包括必要的评估入口方法、固定不可进化的自测方法等。
- `eval_program.py` (评估程序)：定义了评估器，用于评估新生成的解决方案是否满足任务目标，并完成打分工作，系统会根据打分情况判断进化任务是否完成。

#### Examples of task configuration

**Simple task config**：
从 examples 中随机挑选一个 task_config.yaml，你只需要修改 LLM 配置和任务描述即可。

```yaml
# 全局 LLM 配置 (可选)。
# 如果 evaluator 或其他组件没有自己的 llm_config，将使用此配置。
llm_config:
  url: "http://xxx/v1"
  api_key: "xxx"
  model: "deepseek-r1-250528"
  temperature: 0.8
  context_length: 128000
  max_tokens: 32768
  top_p: 1.0
  timeout: 1200
# ------------------------------------------------------------------------------
# 定义主进化流程的配置
# ------------------------------------------------------------------------------
evolve:
  # 任务描述，是整个进化过程的核心目标
  task: |
    Problem Statement: xxx
```

**Complex task config**：
你可以根据任务情况选择更适合的 Executor、评估超时时间、最大进化迭代次数等。

```yaml
# 本次运行选择使用的组件名称
planner_name: "evolve_planner"
executor_name: "evolve_executor_fuse"
summary_name: "evolve_summary"

# 进化过程的核心参数
max_iterations: 1000
target_score: 1.0
concurrency: 1

# 评估器配置
evaluator:
  timeout: 3600
```

#### Examples of initial_program

你必须要给你的进化任务准备一个起始程序，它必须要包含一个可以被评估器调用的测试入口函数，以及输入输出结构。至于他的实现甚至可以是个空函数。PESAgent 会根据你的任务描述，自动填充这个测试入口函数，这就是进化的魅力 👏

```python
import numpy as np


def search_coefficients():
    """Find the coefficients of the problem."""
    best_coefficients = np.array([1, 2, 3])
    return best_coefficients
```

#### Examples of eval_program

评估器是整个进化任务的核心，它决定了新生成的解决方案是否满足任务目标，并完成打分工作。你只需要修改 evaluate 函数。
**好的评估反馈会让 LLM 生成更加优质的解决方案，加速进化效率。**

具体可以参考：[minimum_overlap_problem](../../../../agents/math_agent/examples/minimum_overlap_problem/eval_program.py)

### 📂 Directory Structure

```
.
├── agents
│   ├── math_agent
│   │   ├── examples
│   │   │   ├── packing_circle_in_unit_square
│   │   │   │   ├── eval_program.py
│   │   │   │   ├── initial_program.py
│   │   │   │   └── task_config.yaml
│   │   │   ├── ...
│   │   │   └── uncertainty_inequality
│   │   │       ├── eval_program.py
│   │   │       ├── initial_program.py
│   │   │
```

## 🎩 Advance Usage

您可以根据任务需求，自定义 Planner、Executor、Summary 组件，最后通过 register 方法将其注入到 PESAgent 中，从而创建出您自定义的「PESAgent」。

```python
from loongflow.framework.evolve import PESAgent

# Config evolve agent
agent = PESAgent(
    config=config,
    checkpoint_path=checkpoint_path,
)

# Register worker（Implement the Planner, Executor, and Summary interfaces）
agent.register_planner_worker("planner", PlanAgent)
agent.register_executor_worker("executor", ExecuteAgent)
agent.register_summary_worker("summary", SummaryAgent)

# Run agent
result = await agent()
```

### 🔧 Custom Components

Planner、Executor、Summary 三个组件都是继承自 Worker，您只需要实现 run 方法即可。run 的实现既可以是确定函数，也可以是子 Agent，具体可以参考：[planner](../../../../agents/math_agent/planner/plan_agent.py)
