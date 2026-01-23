#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of ClaudeCodeAgent in LoongFlow.

This demonstrates how to easily instantiate and use the Claude Code Agent
with both built-in tools and custom user-defined tools.
"""

import asyncio
import json
from loongflow.framework.evolve.ccagent import ClaudeCodeAgent


async def example_basic_usage():
    """Basic usage: Simple task with default settings."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Create agent with minimal configuration
    agent = ClaudeCodeAgent(
        work_dir="./workspace",
        tool_list=["Read", "Edit", "Glob"]
    )

    # Run a simple task
    result = await agent.run("List all Python files in the current directory")

    print(f"\nResult: {result.content[0].data}")
    print(f"Status: {result.metadata.get('status')}")
    print(f"Tools Used: {result.metadata.get('tools_used')}")


async def example_auto_approve_edits():
    """Auto-approve file edits for automated workflows."""
    print("\n" + "=" * 60)
    print("Example 2: Auto-approve File Edits")
    print("=" * 60)

    # Create agent with auto-approval for edits
    agent = ClaudeCodeAgent(
        work_dir="./test_project",
        tool_list=["Read", "Edit", "Glob", "Bash"],
        permission_mode="acceptEdits",  # Auto-approve file edits
        verbose=True
    )

    # Run a task that modifies files
    result = await agent.run(
        "Review src/utils.py for bugs and fix any issues you find"
    )

    print(f"\nResult: {result.content[0].data}")
    print(f"Status: {result.metadata.get('status')}")


async def example_complex_task():
    """Complex multi-step task."""
    print("\n" + "=" * 60)
    print("Example 3: Complex Task with Multiple Steps")
    print("=" * 60)

    # Create agent with full permissions
    agent = ClaudeCodeAgent(
        work_dir="./",
        tool_list=["Read", "Edit", "Glob", "Bash"],
        permission_mode="prompt",  # Ask before making changes
        verbose=True
    )

    # Run a complex task
    task = """
    Please do the following:
    1. Find all Python test files in the tests/ directory
    2. Check if they follow the naming convention test_*.py
    3. Create a summary report of the test coverage
    4. Save the report to tests/coverage_report.md
    """

    result = await agent.run(task)

    print(f"\nResult: {result.content[0].data}")
    print(f"Status: {result.metadata.get('status')}")
    print(f"Tools Used: {result.metadata.get('tools_used')}")


async def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)

    agent = ClaudeCodeAgent(
        work_dir="/nonexistent/directory",  # Invalid directory
        tool_list=["Read"]
    )

    try:
        result = await agent.run("List files in current directory")
        print(f"\nResult: {result.content[0].data}")
        print(f"Status: {result.metadata.get('status')}")
    except Exception as e:
        print(f"\nCaught error: {str(e)}")


async def main():
    """Run all examples."""
    print("\n🚀 ClaudeCodeAgent Usage Examples\n")

    # Run examples sequentially
    await example_basic_usage()
    await example_auto_approve_edits()
    await example_complex_task()
    await example_error_handling()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())