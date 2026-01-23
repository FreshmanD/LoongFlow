#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of ClaudeCodeAgent with custom system prompts.

This demonstrates how to customize Claude's behavior using system prompts.
"""

import asyncio
from loongflow.framework.evolve.ccagent import ClaudeCodeAgent


async def example1_code_reviewer():
    """Example 1: Code review expert."""
    print("=" * 60)
    print("Example 1: Code Review Expert")
    print("=" * 60)

    system_prompt = """You are an expert code reviewer focused on:
1. Security vulnerabilities
2. Performance optimization
3. Code maintainability
4. Best practices

Always provide actionable suggestions with examples."""

    agent = ClaudeCodeAgent(
        work_dir="./workspace",
        tool_list=["Read", "Edit", "Glob"],
        system_prompt=system_prompt,
        permission_mode="prompt"
    )

    result = await agent.run("Review the Python files in src/ directory")
    print(f"\nResult: {result.content[0].data}")


async def example2_test_generator():
    """Example 2: Test generation specialist."""
    print("\n" + "=" * 60)
    print("Example 2: Test Generation Specialist")
    print("=" * 60)

    system_prompt = """You are a test generation specialist. When given code:
1. Write comprehensive unit tests
2. Cover edge cases and error conditions
3. Use pytest with clear test names
4. Add docstrings explaining what each test validates
5. Aim for high code coverage"""

    agent = ClaudeCodeAgent(
        work_dir="./test_project",
        tool_list=["Read", "Edit", "Bash"],
        system_prompt=system_prompt,
        permission_mode="acceptEdits"
    )

    result = await agent.run(
        "Generate unit tests for src/calculator.py and save to tests/test_calculator.py"
    )
    print(f"\nResult: {result.content[0].data}")


async def example3_documentation_writer():
    """Example 3: Documentation writer."""
    print("\n" + "=" * 60)
    print("Example 3: Documentation Writer")
    print("=" * 60)

    system_prompt = """You are a technical documentation writer. Your style:
1. Clear and concise explanations
2. Include usage examples
3. Document all parameters and return values
4. Add links to related concepts
5. Use proper Markdown formatting"""

    agent = ClaudeCodeAgent(
        work_dir="./",
        tool_list=["Read", "Edit", "Glob"],
        system_prompt=system_prompt
    )

    result = await agent.run(
        "Generate API documentation for all public functions in src/api/"
    )
    print(f"\nResult: {result.content[0].data}")


async def example4_refactoring_specialist():
    """Example 4: Refactoring specialist."""
    print("\n" + "=" * 60)
    print("Example 4: Refactoring Specialist")
    print("=" * 60)

    system_prompt = """You are a refactoring specialist. When improving code:
1. Maintain backward compatibility unless explicitly told otherwise
2. Extract reusable functions
3. Follow SOLID principles
4. Improve naming for clarity
5. Add type hints
6. Keep changes minimal and focused"""

    agent = ClaudeCodeAgent(
        work_dir="./legacy_code",
        tool_list=["Read", "Edit", "Glob"],
        system_prompt=system_prompt,
        permission_mode="prompt"
    )

    result = await agent.run(
        "Refactor src/utils.py to improve code quality while maintaining compatibility"
    )
    print(f"\nResult: {result.content[0].data}")


async def example5_security_auditor():
    """Example 5: Security auditor."""
    print("\n" + "=" * 60)
    print("Example 5: Security Auditor")
    print("=" * 60)

    system_prompt = """You are a security auditor. Focus on:
1. SQL injection vulnerabilities
2. XSS and CSRF risks
3. Authentication and authorization issues
4. Sensitive data exposure
5. Dependency vulnerabilities
6. Input validation

Rate severity as: Critical, High, Medium, Low
Provide remediation steps for each finding."""

    agent = ClaudeCodeAgent(
        work_dir="./webapp",
        tool_list=["Read", "Glob"],
        system_prompt=system_prompt
    )

    result = await agent.run(
        "Perform a security audit of all Python files in the src/ directory"
    )
    print(f"\nResult: {result.content[0].data}")


async def example6_performance_optimizer():
    """Example 6: Performance optimizer."""
    print("\n" + "=" * 60)
    print("Example 6: Performance Optimizer")
    print("=" * 60)

    system_prompt = """You are a performance optimization expert. When analyzing code:
1. Identify bottlenecks (time and space complexity)
2. Suggest algorithmic improvements
3. Recommend caching strategies
4. Identify unnecessary computations
5. Suggest parallelization opportunities
6. Provide benchmarks when possible"""

    agent = ClaudeCodeAgent(
        work_dir="./app",
        tool_list=["Read", "Edit", "Bash"],
        system_prompt=system_prompt,
        permission_mode="acceptEdits"
    )

    result = await agent.run(
        "Analyze and optimize the performance of src/data_processor.py"
    )
    print(f"\nResult: {result.content[0].data}")


async def example7_combined_with_custom_tools():
    """Example 7: System prompt combined with custom tools."""
    print("\n" + "=" * 60)
    print("Example 7: System Prompt + Custom Tools")
    print("=" * 60)

    # Define custom tool
    async def code_complexity_analyzer(args):
        """Mock tool to analyze code complexity."""
        filename = args.get('filename', '')
        # In real implementation, use tools like radon, pylint
        return {
            "content": [{
                "type": "text",
                "text": f"Complexity analysis for {filename}:\n"
                       f"- Cyclomatic complexity: 12\n"
                       f"- Lines of code: 250\n"
                       f"- Maintainability index: 65"
            }]
        }

    system_prompt = """You are a code quality specialist. Use the code_complexity_analyzer tool 
to assess code quality, then provide specific recommendations to reduce complexity."""

    agent = ClaudeCodeAgent(
        work_dir="./",
        tool_list=["Read", "Edit"],
        custom_tools={
            "code_complexity_analyzer": {
                "function": code_complexity_analyzer,
                "description": "Analyzes code complexity metrics",
                "parameters": {"filename": str}
            }
        },
        system_prompt=system_prompt
    )

    result = await agent.run(
        "Analyze the complexity of src/main.py and suggest improvements"
    )
    print(f"\nResult: {result.content[0].data}")


async def main():
    """Run all system prompt examples."""
    print("\n🎨 ClaudeCodeAgent System Prompt Examples\n")

    await example1_code_reviewer()
    await example2_test_generator()
    await example3_documentation_writer()
    await example4_refactoring_specialist()
    await example5_security_auditor()
    await example6_performance_optimizer()
    await example7_combined_with_custom_tools()

    print("\n" + "=" * 60)
    print("✅ All system prompt examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())