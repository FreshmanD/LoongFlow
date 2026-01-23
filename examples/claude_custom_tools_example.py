#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of ClaudeCodeAgent with Custom Tools.

This demonstrates how to create and use custom tools with the Claude Code Agent.
"""

import asyncio
import json
import requests
from typing import Dict, Any
from loongflow.framework.evolve.ccagent import ClaudeCodeAgent


# ==================== Custom Tool Definitions ====================

async def calculator_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    A simple calculator tool that evaluates mathematical expressions.

    Args:
        args: Dictionary with 'expression' key

    Returns:
        Tool response with the calculation result
    """
    try:
        expression = args.get('expression', '')
        # Safe evaluation (in production, use a proper math parser)
        result = eval(expression, {"__builtins__": {}}, {})

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Calculation result: {expression} = {result}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error in calculation: {str(e)}"
                }
            ]
        }


async def weather_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    A mock weather tool that returns weather information.

    Args:
        args: Dictionary with 'city' key

    Returns:
        Tool response with weather data
    """
    city = args.get('city', 'Unknown')

    # Mock weather data (in production, call a real weather API)
    weather_data = {
        "Beijing": {"temp": 15, "condition": "Sunny", "humidity": 45},
        "Shanghai": {"temp": 22, "condition": "Cloudy", "humidity": 70},
        "Shenzhen": {"temp": 28, "condition": "Rainy", "humidity": 85},
    }

    data = weather_data.get(city, {"temp": 20, "condition": "Unknown", "humidity": 50})

    return {
        "content": [
            {
                "type": "text",
                "text": f"Weather in {city}:\n"
                       f"- Temperature: {data['temp']}°C\n"
                       f"- Condition: {data['condition']}\n"
                       f"- Humidity: {data['humidity']}%"
            }
        ]
    }


async def data_analyzer_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a list of numbers and returns statistics.

    Args:
        args: Dictionary with 'numbers' key (list of numbers as string)

    Returns:
        Tool response with statistical analysis
    """
    try:
        numbers_str = args.get('numbers', '')
        numbers = [float(x.strip()) for x in numbers_str.split(',')]

        if not numbers:
            return {
                "content": [
                    {"type": "text", "text": "No numbers provided"}
                ]
            }

        stats = {
            "count": len(numbers),
            "sum": sum(numbers),
            "mean": sum(numbers) / len(numbers),
            "min": min(numbers),
            "max": max(numbers),
        }

        result_text = f"Data Analysis Results:\n"
        result_text += f"- Count: {stats['count']}\n"
        result_text += f"- Sum: {stats['sum']:.2f}\n"
        result_text += f"- Mean: {stats['mean']:.2f}\n"
        result_text += f"- Min: {stats['min']:.2f}\n"
        result_text += f"- Max: {stats['max']:.2f}\n"

        return {
            "content": [
                {"type": "text", "text": result_text}
            ]
        }
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Error analyzing data: {str(e)}"}
            ]
        }


async def json_formatter_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats a JSON string for better readability.

    Args:
        args: Dictionary with 'json_string' key

    Returns:
        Tool response with formatted JSON
    """
    try:
        json_str = args.get('json_string', '')
        parsed = json.loads(json_str)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Formatted JSON:\n```json\n{formatted}\n```"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {"type": "text", "text": f"Error formatting JSON: {str(e)}"}
            ]
        }


# ==================== Examples ====================

async def example1_basic_custom_tools():
    """Example 1: Using custom tools defined at initialization."""
    print("=" * 60)
    print("Example 1: Basic Custom Tools")
    print("=" * 60)

    # Create agent with custom tools
    agent = ClaudeCodeAgent(
        work_dir="./",
        tool_list=["Read"],  # Keep some built-in tools
        custom_tools={
            "calculator": {
                "function": calculator_tool,
                "description": "Evaluates mathematical expressions",
                "parameters": {"expression": str}
            },
            "weather": {
                "function": weather_tool,
                "description": "Gets weather information for a city",
                "parameters": {"city": str}
            }
        }
    )

    # Test the calculator tool
    result = await agent.run("Calculate 25 * 4 + 100 using the calculator tool")
    print(f"\n[Calculator Test]")
    print(f"Result: {result.content[0].data}")
    print(f"Status: {result.metadata.get('status')}")

    # Test the weather tool
    result = await agent.run("Get the weather for Beijing using the weather tool")
    print(f"\n[Weather Test]")
    print(f"Result: {result.content[0].data}")


async def example2_dynamic_tool_addition():
    """Example 2: Adding tools dynamically after initialization."""
    print("\n" + "=" * 60)
    print("Example 2: Dynamic Tool Addition")
    print("=" * 60)

    # Create agent without custom tools
    agent = ClaudeCodeAgent(
        work_dir="./",
        tool_list=["Read"]
    )

    print("\nInitial custom tools:", agent.list_custom_tools())

    # Add tools dynamically
    agent.add_custom_tool(
        "data_analyzer",
        data_analyzer_tool,
        "Analyzes a comma-separated list of numbers",
        {"numbers": str}
    )

    agent.add_custom_tool(
        "json_formatter",
        json_formatter_tool,
        "Formats JSON strings for readability",
        {"json_string": str}
    )

    print("After adding tools:", agent.list_custom_tools())

    # Use the dynamically added tools
    result = await agent.run(
        "Use the data_analyzer tool to analyze these numbers: 10, 20, 30, 40, 50"
    )
    print(f"\n[Data Analyzer Test]")
    print(f"Result: {result.content[0].data}")


async def example3_tool_management():
    """Example 3: Managing custom tools (list, get info, remove)."""
    print("\n" + "=" * 60)
    print("Example 3: Tool Management")
    print("=" * 60)

    # Create agent with multiple tools
    agent = ClaudeCodeAgent(
        work_dir="./",
        tool_list=["Read"],
        custom_tools={
            "calculator": {
                "function": calculator_tool,
                "description": "Evaluates mathematical expressions",
                "parameters": {"expression": str}
            },
            "weather": {
                "function": weather_tool,
                "description": "Gets weather information",
                "parameters": {"city": str}
            }
        }
    )

    # List all custom tools
    print("\nRegistered custom tools:", agent.list_custom_tools())

    # Get info about a specific tool
    calc_info = agent.get_custom_tool_info("calculator")
    print(f"\nCalculator tool info:")
    print(f"  Description: {calc_info['description']}")
    print(f"  Parameters: {calc_info['parameters']}")

    # Remove a tool
    print("\nRemoving 'weather' tool...")
    agent.remove_custom_tool("weather")
    print("Remaining tools:", agent.list_custom_tools())


async def example4_mixed_tools():
    """Example 4: Using both built-in and custom tools together."""
    print("\n" + "=" * 60)
    print("Example 4: Mixed Built-in and Custom Tools")
    print("=" * 60)

    agent = ClaudeCodeAgent(
        work_dir="./workspace",
        tool_list=["Read", "Edit", "Glob"],  # Built-in tools
        custom_tools={
            "calculator": {
                "function": calculator_tool,
                "description": "Evaluates mathematical expressions",
                "parameters": {"expression": str}
            },
            "data_analyzer": {
                "function": data_analyzer_tool,
                "description": "Analyzes numeric data",
                "parameters": {"numbers": str}
            }
        },
        permission_mode="acceptEdits"
    )

    # Complex task using both types of tools
    task = """
    1. Use the calculator to compute 100 * 3.14
    2. Use data_analyzer to analyze: 5, 10, 15, 20, 25
    3. Read any Python files in the current directory (if any)
    """

    result = await agent.run(task)
    print(f"\nResult: {result.content[0].data}")
    print(f"Status: {result.metadata.get('status')}")
    print(f"Tools used: {result.metadata.get('tools_used')}")


async def example5_real_world_scenario():
    """Example 5: A realistic workflow with custom tools."""
    print("\n" + "=" * 60)
    print("Example 5: Real-world Scenario - Data Processing Pipeline")
    print("=" * 60)

    async def csv_reader_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates reading CSV data."""
        filename = args.get('filename', '')
        # Mock CSV data
        mock_data = "id,value,category\n1,100,A\n2,200,B\n3,150,A\n4,300,C"
        return {
            "content": [
                {"type": "text", "text": f"CSV Content of {filename}:\n{mock_data}"}
            ]
        }

    async def data_transform_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        """Transforms data based on rules."""
        rule = args.get('rule', '')
        return {
            "content": [
                {"type": "text", "text": f"Applied transformation: {rule}\nData transformed successfully."}
            ]
        }

    # Create specialized data processing agent
    agent = ClaudeCodeAgent(
        work_dir="./data",
        tool_list=["Read", "Write"],
        custom_tools={
            "csv_reader": {
                "function": csv_reader_tool,
                "description": "Reads CSV files",
                "parameters": {"filename": str}
            },
            "data_transform": {
                "function": data_transform_tool,
                "description": "Transforms data using rules",
                "parameters": {"rule": str}
            },
            "calculator": {
                "function": calculator_tool,
                "description": "Performs calculations",
                "parameters": {"expression": str}
            }
        },
        permission_mode="acceptEdits"
    )

    workflow = """
    Data Processing Pipeline:
    1. Use csv_reader to read 'sales_data.csv'
    2. Use calculator to compute average: (100 + 200 + 150 + 300) / 4
    3. Use data_transform to normalize values
    4. Summarize the results
    """

    result = await agent.run(workflow)
    print(f"\nWorkflow Result:")
    print(result.content[0].data)
    print(f"\nStatus: {result.metadata.get('status')}")


async def main():
    """Run all custom tools examples."""
    print("\n🔧 ClaudeCodeAgent Custom Tools Examples\n")

    await example1_basic_custom_tools()
    await example2_dynamic_tool_addition()
    await example3_tool_management()
    await example4_mixed_tools()
    await example5_real_world_scenario()

    print("\n" + "=" * 60)
    print("✅ All custom tools examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())