# GPU 低利用率问题定位教程 - LoongFlow General Evolve Agent

## 概述

本教程介绍如何使用 LoongFlow 的 General Evolve Agent 来定位 GPU 低利用率问题。通过现有的代码分析 demo，您将了解完整的 PES (Plan-Execute-Summary) 工作流程，并学会如何应用于 GPU 性能优化场景。

## 工作流程概述

LoongFlow 采用三阶段演进式问题解决方法：

```
Plan (规划) → Execute (执行) → Summary (总结)
```

### 1. Plan 阶段 - 制定诊断策略
- **输入**: 问题描述、历史解决方案
- **输出**: 包含假设和证据收集计划的详细策略
- **核心**: 设计系统的假设列表，每个假设都有明确的验证证据

### 2. Execute 阶段 - 执行验证
- **输入**: Plan 阶段的策略
- **输出**: 收集的证据和初步评分
- **核心**: 使用工具验证每个假设，收集支持或反驳的证据

### 3. Summary 阶段 - 总结分析
- **输入**: 执行结果和历史数据
- **输出**: 演进总结和改进建议
- **核心**: 评估整体进展，提取学习经验，指导下一次迭代

## 现有 Demo 分析示例

### 成功案例：Ctrl+C 间歇性卡顿问题
通过 Demo 可以看到一个完整的问题定位过程：

**Plan 阶段** (`best_plan.md`):
- 制定了 4 个系统性假设：进程组管理、异步任务竞争、阻塞 I/O、线程同步
- 每个假设都有明确的验证证据和权重分配
- 采用系统性多假设方法，避免单一原因假设的局限性

**Execute 阶段** (`best_solution.md`):
- 专注于"进程组管理失败"假设
- 收集 3 类证据：必要迹象、确认迹象、反指标
- 验证证据的存在性并计算对应的结果值

**Summary 阶段** (`best_summary.md`):
- 评估从 0.6 分提升到 1.0 分的改进
- 分析了成功因素和需要改进的地方
- 提供具体的下一步建议

## 如何应用于 GPU 低利用率问题

### 1. Task 描述编写指南

由于您提到不能操作线上环境且 GPU 低利用率是一个检测结果而非明确问题描述，以下是如何编写有效的 task 描述：

#### 优质 Task 描述的特征
- **基于观测数据**：从日志、监控指标等客观数据出发
- **包含上下文**：提供系统配置、负载情况、时间范围等背景信息
- **可验证性**：包含具体的指标阈值和异常现象描述
- **避免主观判断**：不预设结论，保持中立的问题陈述

#### Task 描述模板

```markdown
# GPU 利用率异常检测任务

## 问题现象
在 [时间段]，监控系统检测到 GPU 利用率低于预期阈值。

## 观测数据
- **时间范围**: 2024-01-15 14:00 至 2024-01-15 16:00
- **GPU 平均利用率**: 15% (预期 > 60%)
- **GPU 内存使用率**: 45% (峰值 80%)
- **系统负载**: CPU 利用率 25%，内存使用率 60%
- **应用场景**: [具体应用类型，如模型训练/推理]

## 相关日志摘要
- [关键错误日志或警告信息]
- [性能指标异常波动记录]

## 约束条件
- 仅基于日志和监控数据进行分析
- 不能修改线上环境或进行主动测试
- 需要识别根本原因并提供诊断建议
```

### 2. 数据源准备策略

#### 可用的数据源类型
1. **日志文件**：应用日志、系统日志、错误日志
2. **监控数据**：GPU 指标、系统指标、应用性能指标  
3. **配置信息**：系统配置、应用参数、环境变量
4. **代码分析**：相关代码逻辑、算法实现

#### 数据收集模板

```yaml
task_info: |
  分析以下监控数据，识别 GPU 利用率低下的根本原因：

  监控时间段: 2024-01-15 14:00-16:00
  异常指标:
    - GPU 利用率: 平均 15%，峰值 30%
    - GPU 内存: 平均使用 45%，未达到瓶颈
    - 批处理吞吐量: 降低 60%

  相关日志片段:
    - "WARNING: Data loading bottleneck detected"
    - "INFO: Batch processing time increased by 200%"

  系统配置:
    - GPU: NVIDIA A100 40GB
    - Batch Size: 32
    - 数据流水线: 单线程加载

data_sources:
  logs: 
    - "/var/log/application/gpu_perf.log"
    - "/var/log/system/gpu_monitor.log"
  metrics:
    - "gpu_utilization_20240115.csv"
    - "system_performance_20240115.json"
  code_reference:
    - "src/model_training.py"
    - "src/data_loader.py"
```

### 2. 设计 GPU 相关的假设模板

#### 常见的 GPU 低利用率原因假设

```json
{
  "assumptions": [
    {
      "assumption": "GPU 内存瓶颈导致利用率低下",
      "evidences": [
        {
          "evidence_type": "NecessarySign",
          "description": "GPU 内存使用率接近上限",
          "detect_tool": "GPUStat",
          "tool_params": {
            "metric": "memory_used_percent",
            "threshold": 85
          }
        }
      ]
    },
    {
      "assumption": "CPU-GPU 数据传输成为瓶颈",
      "evidences": [
        {
          "evidence_type": "NecessarySign",
          "description": "数据传输时间占比较大",
          "detect_tool": "NvProf",
          "tool_params": {
            "metric": "data_transfer_time_ratio",
            "threshold": 0.3
          }
        }
      ]
    }
  ]
}
```

### 3. 配置 Agent 参数

```python
# 在运行配置中设置 GPU 特定的参数
gpu_config = {
    "llm_config": {
        "model": "gpt-4",
        "api_key": "your-api-key",
        "url": "https://api.openai.com/v1"
    },
    "max_rounds": 10,
    "max_turns": 5,
    "skills": ["gpu_analysis", "performance_profiling"],
    "gpu_specific_params": {
        "monitoring_interval": 1.0,
        "metrics_to_track": ["utilization", "memory", "power"]
    }
}
```

## 针对非线上环境的调试方法

### 1. 基于日志和监控数据的诊断策略

由于不能在线上环境进行实时监控，采用以下替代方案：

#### 日志分析方法
```python
def analyze_gpu_logs(log_files):
    """分析 GPU 相关日志文件"""
    insights = []

    for log_file in log_files:
        with open(log_file, 'r') as f:
            for line in f:
                # 分析关键模式
                if 'GPU' in line and ('utilization' in line or 'memory' in line):
                    insights.append(parse_gpu_metrics(line))
                elif 'bottleneck' in line.lower() or 'slow' in line.lower():
                    insights.append(identify_bottleneck(line))

    return insights

def parse_gpu_metrics(log_line):
    """从日志行中解析 GPU 指标"""
    # 实现日志解析逻辑，提取利用率、内存使用等指标
    pass
```

#### 监控数据处理
```python
def process_historical_metrics(metric_files):
    """处理历史监控数据"""
    trends = {}

    for file_path in metric_files:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            trends.update(analyze_metric_trends(df))
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                trends.update(extract_anomalies(data))

    return trends
```

### 2. 代码静态分析方法

通过分析相关代码来识别潜在性能问题：

```python
def analyze_gpu_related_code(code_files):
    """分析 GPU 相关代码的潜在问题"""
    issues = []

    for code_file in code_files:
        with open(code_file, 'r') as f:
            content = f.read()

            # 检查常见 GPU 性能问题模式
            if 'cudaMemcpy' in content and 'async' not in content:
                issues.append("同步内存拷贝可能阻塞 GPU")

            if 'for loop' in content and 'gpu' in content.lower():
                issues.append("GPU 上的串行循环可能导致利用率低下")

            if 'small batch' in content.lower():
                issues.append("小批量大小可能导致 GPU 利用率不足")

    return issues
```

### 3. 评估指标定制

根据 GPU 问题的特殊性，定制评估指标：

```python
gpu_evaluation_metrics = {
    "memory_efficiency": {
        "weight": 0.3,
        "calculation": "actual_memory_used / total_memory"
    },
    "utilization_consistency": {
        "weight": 0.4,
        "calculation": "1 - std(utilization_over_time) / mean(utilization_over_time)"
    },
    "bottleneck_identification": {
        "weight": 0.3,
        "calculation": "number_of_identified_bottlenecks / total_possible_bottlenecks"
    }
}
```

## Prompt 调整策略

### 1. GPU 特定的 Planner Prompt 调整

在 `gpu_utilize_prompt.py` 基础上，针对 GPU 问题进行定制：

```python
GPU_SPECIFIC_PROMPT_ADDITIONS = """
# GPU 问题特定的指导原则

## GPU 性能分析的特殊性
1. **实时性要求**: GPU 状态变化快速，需要实时监控数据
2. **多维度指标**: 考虑利用率、内存、温度、功耗等多维度指标
3. **瓶颈识别**: 重点识别数据传输、内核启动、内存访问等瓶颈

## 假设设计指南
- 优先考虑硬件相关的假设（内存瓶颈、PCIe 带宽）
- 其次考虑软件层面的假设（内核优化、并行度）
- 最后考虑系统层面的假设（调度策略、资源竞争）

## 证据收集策略
- 使用专用 GPU 性能分析工具（nvprof, nsight）
- 结合系统监控工具（top, iostat）
- 采用对比实验方法（改变参数观察效果）
"""
```

### 2. Executor Prompt 优化

```python
GPU_EXECUTOR_ENHANCEMENTS = """
## GPU 证据收集的特殊方法

### 性能剖析证据
1. **时间剖析**: 使用 nvprof 分析内核执行时间
2. **内存分析**: 监控 GPU 内存分配和释放模式
3. **带宽测试**: 测量 PCIe 和内存带宽利用率

### 对比实验证据
1. **批量大小影响**: 测试不同批量大小对利用率的影响
2. **模型复杂度**: 比较简单和复杂模型的 GPU 使用模式
3. **数据流水线**: 分析数据预处理与 GPU 计算的 overlap

### 系统级证据
1. **多进程竞争**: 检查是否有其他进程竞争 GPU 资源
2. **电源管理**: 验证 GPU 功耗限制设置
3. **温度节流**: 监控 GPU 温度是否导致降频
"""
```

## 工具配备要求

### 必需的 GPU 分析工具

| 工具 | 用途 | 安装方法 |
|------|------|----------|
| nvidia-smi | 基础 GPU 状态监控 | NVIDIA 驱动自带 |
| gpustat | 实时 GPU 状态监控 | `pip install gpustat` |
| nvprof | NVIDIA 性能分析器 | CUDA Toolkit 自带 |
| PyTorch Profiler | 深度学习框架剖析 | `pip install torch` |
| Nsight Systems | 系统级性能分析 | NVIDIA 开发者工具 |

### 自定义工具开发

针对特定的 GPU 问题，可以开发定制工具：

```python
class GPUAnalysisTool:
    """GPU 分析专用工具"""

    def analyze_memory_pattern(self, process_id):
        """分析特定进程的 GPU 内存使用模式"""
        # 实现内存模式分析逻辑
        pass

    def detect_bottlenecks(self, trace_file):
        """从性能追踪文件中检测瓶颈"""
        # 实现瓶颈检测逻辑
        pass
```

## 性能调优提示

### 1. 迭代策略优化

- **第一轮**: 宽泛假设，快速排除明显错误方向
- **第二轮**: 基于第一轮结果，聚焦最有希望的假设
- **第三轮**: 深入验证，提供具体的优化建议

### 2. 证据质量评估

```python
def evaluate_gpu_evidence_quality(evidence):
    """评估 GPU 证据的质量"""
    quality_score = 0

    # 实时性得分
    if evidence.get('real_time', False):
        quality_score += 0.3

    # 多维度得分
    if len(evidence.get('dimensions', [])) >= 3:
        quality_score += 0.3

    # 可重现性得分
    if evidence.get('reproducible', False):
        quality_score += 0.4

    return quality_score
```

### 3. 结果验证方法

```python
def validate_gpu_solution(solution):
    """验证 GPU 问题解决方案的有效性"""

    # 1. 性能提升验证
    baseline_performance = get_baseline_performance()
    new_performance = measure_new_performance()
    improvement_ratio = new_performance / baseline_performance

    # 2. 稳定性验证
    stability_score = measure_performance_stability()

    # 3. 可推广性验证
    generalization_score = test_on_different_workloads()

    overall_score = (improvement_ratio * 0.5 + 
                    stability_score * 0.3 + 
                    generalization_score * 0.2)

    return overall_score
```

## 常见问题排查

### 1. Task 描述过于模糊

**症状**: Agent 无法理解具体问题，生成泛化的假设

**解决方案**:
- 提供具体的时间段、指标数值、日志片段
- 包含系统配置和应用场景信息
- 明确性能异常的具体表现

### 2. 日志数据质量不佳

**症状**: 日志信息不完整或格式混乱，无法提取有效证据

**解决方案**:
- 提前预处理日志文件，提取关键信息
- 提供日志格式说明和解析规则
- 使用正则表达式抽取结构化数据

### 3. 静态分析局限性

**症状**: 仅靠代码分析无法确定实际运行时性能问题

**解决方案**:
- 结合代码模式和日志数据进行综合分析
- 识别代码中的可疑模式并关联到监控数据
- 采用基于模式的假设验证而非确定性结论

## 最佳实践总结

1. **渐进式诊断**: 从系统级到代码级逐步深入
2. **多工具协同**: 结合多种 GPU 分析工具获取全面视角
3. **实证优先**: 基于实际测量数据而非理论推测
4. **迭代优化**: 通过多次 PES 循环持续改进诊断精度
5. **结果验证**: 确保提出的解决方案能实际改善 GPU 利用率

通过遵循本教程，您将能够有效利用 LoongFlow General Evolve Agent 来解决复杂的 GPU 性能优化问题。