#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of PES Factory with ClaudeCodeAgent.

This demonstrates how to create and use Planner-Executor-Summary workers
using the ClaudeCodeAgent as the core implementation.
"""

import asyncio


async def example1_simple_factory():
    """Example 1: Using the simple factory function."""
    print("=" * 60)
    print("Example 1: Simple Factory Usage")
    print("=" * 60)

    # Note: In real usage, you need to provide actual database and evaluator
    # This is just to show the API

    print(
        """
# Create workers with default configuration
planner, executor, summary = create_simple_claude_pes(
    work_dir="./workspace",
    database=my_database,
    evaluator=my_evaluator
)

# Register with PESAgent
agent.register_planner_worker("claude_planner", ClaudePlannerWorker)
agent.register_executor_worker("claude_executor", ClaudeExecutorWorker)
agent.register_summary_worker("claude_summary", ClaudeSummaryWorker)
"""
    )

    print("\n✅ Workers created with default configuration")


async def example2_custom_prompts():
    """Example 2: Using custom system prompts for each worker."""
    print("\n" + "=" * 60)
    print("Example 2: Custom System Prompts")
    print("=" * 60)

    custom_prompts = {
        "planner": """You are a mathematical optimization expert specializing in:
        - Analytical bounds and inequalities
        - Geometric optimization
        - Algebraic transformations

        Generate concrete, actionable improvement plans.""",
        "executor": """You are a Python algorithm implementation expert.

        Focus on:
        - Clean, efficient code
        - Numerical stability
        - Edge case handling
        - Comprehensive comments

        Always save solutions to the specified path.""",
        "summary": """You are an analytical expert who learns from experiments.

        Extract:
        - What worked and why
        - What failed and why
        - Generalizable patterns
        - Recommendations for future iterations
        """,
    }

    print(f"Custom Prompts Configured:")
    print(f"- Planner: Mathematical optimization expert")
    print(f"- Executor: Python implementation expert")
    print(f"- Summary: Analytical learning expert")

    print("\n✅ Workers configured with specialized roles")


async def example3_advanced_configuration():
    """Example 3: Advanced configuration with custom settings."""
    print("\n" + "=" * 60)
    print("Example 3: Advanced Configuration")
    print("=" * 60)

    planner_config = {
        "work_dir": "./workspace",
        "tool_list": ["Read", "Edit", "Glob"],
        "system_prompt": "You are a strategic planner...",
        "permission_mode": "prompt",  # Ask before changes
        "verbose": True,
    }

    executor_config = {
        "work_dir": "./workspace",
        "tool_list": ["Read", "Write", "Edit", "Bash", "Glob"],
        "max_rounds": 5,  # Allow more iteration rounds
        "system_prompt": "You are an implementation expert...",
        "permission_mode": "acceptEdits",  # Auto-approve for efficiency
        "verbose": True,
    }

    summary_config = {
        "work_dir": "./workspace",
        "tool_list": ["Read"],  # Read-only for safety
        "system_prompt": "You are an insightful analyzer...",
        "permission_mode": "prompt",
        "verbose": True,
    }

    print(f"Configuration Summary:")
    print(f"- Planner: prompt mode, standard tools")
    print(f"- Executor: acceptEdits mode, 5 rounds, full tools")
    print(f"- Summary: prompt mode, read-only")

    print("\n✅ Advanced configuration applied")


async def example4_with_custom_tools():
    """Example 4: Adding custom tools to workers."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Tools Integration")
    print("=" * 60)

    # Define custom tools
    async def algorithm_complexity_analyzer(args):
        """Analyzes algorithm time/space complexity."""
        code = args.get("code", "")
        # Mock analysis
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Time Complexity: O(n^2)\nSpace Complexity: O(n)",
                }
            ]
        }

    async def benchmark_runner(args):
        """Runs performance benchmarks."""
        solution_path = args.get("solution_path", "")
        # Mock benchmark
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Benchmark: 0.23s for n=1000",
                }
            ]
        }

    # Configuration with custom tools
    executor_config = {
        "work_dir": "./workspace",
        "tool_list": ["Read", "Write", "Edit", "Bash"],
        "custom_tools": {
            "complexity_analyzer": {
                "function": algorithm_complexity_analyzer,
                "description": "Analyzes algorithm complexity",
                "parameters": {"code": str},
            },
            "benchmark_runner": {
                "function": benchmark_runner,
                "description": "Runs performance benchmarks",
                "parameters": {"solution_path": str},
            },
        },
        "max_rounds": 3,
        "system_prompt": """You are an implementation expert.

        Use complexity_analyzer to assess solution complexity.
        Use benchmark_runner to measure performance.
        """,
    }

    print(f"Custom Tools Added:")
    print(f"- complexity_analyzer: Analyzes O(n) complexity")
    print(f"- benchmark_runner: Measures execution time")

    print("\n✅ Custom tools integrated successfully")


async def example5_mathematical_domain():
    """Example 5: Domain-specific configuration for mathematics."""
    print("\n" + "=" * 60)
    print("Example 5: Mathematical Domain Configuration")
    print("=" * 60)

    math_prompts = {
        "planner": """You are a mathematical proof strategist.

Your focus:
1. Identify applicable theorems and lemmas
2. Design proof strategies (direct, contradiction, induction)
3. Suggest mathematical transformations
4. Leverage known inequalities

Generate plans that guide toward elegant mathematical solutions.""",
        "executor": """You are a mathematical algorithm implementer.

Your focus:
1. Translate mathematical proofs into code
2. Ensure numerical precision
3. Handle boundary conditions carefully
4. Validate results against analytical bounds

Write clear code with mathematical reasoning in comments.""",
        "summary": """You are a mathematical learning analyst.

Your focus:
1. Identify successful proof strategies
2. Recognize mathematical patterns
3. Extract reusable techniques
4. Build intuition for future problems

Summarize both successful and failed mathematical approaches.""",
    }

    print(f"Mathematical Domain Configuration:")
    print(f"- Focus: Proof strategies, numerical precision")
    print(f"- Tools: Standard file operations")
    print(f"- Style: Mathematical rigor + code quality")

    print("\n✅ Domain-specific configuration ready")


async def example6_integration_workflow():
    """Example 6: Complete integration workflow."""
    print("\n" + "=" * 60)
    print("Example 6: Complete Integration Workflow")
    print("=" * 60)

    workflow = """
Step 1: Load Configuration
  - Parse task_config.yaml
  - Initialize database and evaluator

Step 2: Create Workers
  - Use create_simple_claude_pes() or create_claude_pes_workers()
  - Customize system prompts if needed

Step 3: Initialize PESAgent
  - Create PESAgent with config
  - Register Planner, Executor, Summary workers

Step 4: Run Evolution
  - await agent()
  - Monitor logs for progress
  - Check workspace for outputs

Step 5: Analyze Results
  - Review best solution
  - Study evolutionary history
  - Extract learned patterns
"""

    print(workflow)
    print("\n✅ Integration workflow outlined")


async def main():
    """Run all examples."""
    print("\n🏭 PES Factory Examples\n")

    await example1_simple_factory()
    await example2_custom_prompts()
    await example3_advanced_configuration()
    await example4_with_custom_tools()
    await example5_mathematical_domain()
    await example6_integration_workflow()

    print("\n" + "=" * 60)
    print("✅ All PES Factory examples completed!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review pes_factory.py implementation")
    print("2. Read PES_FACTORY_README.md for detailed docs")
    print("3. Create your own custom PES configuration")
    print("4. Integrate with PESAgent in your project")


if __name__ == "__main__":
    asyncio.run(main())
