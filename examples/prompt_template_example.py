#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of Prompt Template System.

This demonstrates how to use the declarative prompt template system
for configurable, reusable prompts.
"""

from loongflow.framework.evolve.prompt import (
    PromptTemplate,
    PromptRole,
    PromptRegistry,
    get_global_registry,
    get_prompt,
    register_prompt,
)


def example1_basic_usage():
    """Example 1: Basic template definition and rendering."""
    print("=" * 60)
    print("Example 1: Basic Template Usage")
    print("=" * 60)

    # Define a simple template
    greeting = PromptTemplate(
        name="greeting_template",
        role=PromptRole.SYSTEM,
        template="Hello {{name}}! Welcome to {{system}}.",
        input_schema={
            "type": "object",
            "properties": {"name": {"type": "string"}, "system": {"type": "string"}},
            "required": ["name", "system"],
        },
        description="A simple greeting template",
    )

    # Render with variables
    rendered = greeting.render(name="Alice", system="LoongFlow")

    print(f"Template: {greeting.template}")
    print(f"Rendered: {rendered}")
    print("\n✅ Basic usage completed")


def example2_builtin_prompts():
    """Example 2: Using built-in prompts from global registry."""
    print("\n" + "=" * 60)
    print("Example 2: Built-in Prompts")
    print("=" * 60)

    # Get the global registry (auto-loaded with built-in prompts)
    registry = get_global_registry()

    # List all registered prompts
    print(f"Total prompts: {len(registry)}")
    print(
        f"Planner prompts: {registry.list_prompts(role=PromptRole.SYSTEM, tags=['planner'])}"
    )
    print(f"Executor prompts: {registry.list_prompts(tags=['executor'])}")

    # Get a specific prompt
    planner_user = get_prompt("evolve_planner_user")

    print(f"\nPrompt name: {planner_user.name}")
    print(f"Required variables: {planner_user.get_required_variables()}")
    print(f"All variables: {planner_user.get_all_variables()}")

    # Render with actual values
    rendered = planner_user.render(
        task_info="Optimize packing circles in a unit square",
        parent_solution='{"solution": "...", "score": 0.85}',
        workspace="./workspace/planner",
        island_num=4,
        parent_island=0,
        best_plan_path="./workspace/planner/best_plan.txt",
    )

    print(f"\nRendered prompt (first 200 chars):")
    print(rendered[:200] + "...")
    print("\n✅ Built-in prompts demonstrated")


def example3_custom_prompt():
    """Example 3: Create and register custom prompts."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Prompt Registration")
    print("=" * 60)

    # Create a domain-specific prompt
    code_review = PromptTemplate(
        name="code_review_system",
        role=PromptRole.SYSTEM,
        template="""You are a {{language}} code reviewer specialized in {{focus_area}}.

Review Guidelines:
{{guidelines}}

Focus on:
- Code quality and maintainability
- Performance optimization
- Security vulnerabilities
- Best practices for {{language}}
""",
        input_schema={
            "type": "object",
            "properties": {
                "language": {"type": "string"},
                "focus_area": {"type": "string"},
                "guidelines": {"type": "string"},
            },
            "required": ["language", "focus_area", "guidelines"],
        },
        description="System prompt for code review",
        tags=["code_review", "custom"],
    )

    # Register to global registry
    register_prompt(code_review)

    # Use it
    rendered = code_review.render(
        language="Python",
        focus_area="algorithmic efficiency",
        guidelines="PEP 8 compliance, type hints, docstrings",
    )

    print(f"Custom prompt registered: {code_review.name}")
    print(f"Rendered:\n{rendered}")
    print("\n✅ Custom prompt created and used")


def example4_prompt_validation():
    """Example 4: Template validation and error handling."""
    print("\n" + "=" * 60)
    print("Example 4: Validation and Error Handling")
    print("=" * 60)

    template = PromptTemplate(
        name="validated_template",
        role=PromptRole.USER,
        template="Process {{input}} with {{method}}",
        input_schema={
            "type": "object",
            "properties": {"input": {"type": "string"}, "method": {"type": "string"}},
            "required": ["input", "method"],
        },
    )

    # Valid rendering
    try:
        result = template.render(input="data.csv", method="analysis")
        print(f"✅ Valid render: {result}")
    except ValueError as e:
        print(f"❌ Error: {e}")

    # Missing required variable
    try:
        result = template.render(input="data.csv")
        print(f"Result: {result}")
    except ValueError as e:
        print(f"✅ Caught missing variable: {e}")

    # Type mismatch (will warn but not fail in basic validation)
    try:
        result = template.render(input=123, method="analysis")
        print(f"Result: {result}")
    except ValueError as e:
        print(f"✅ Caught type error: {e}")

    print("\n✅ Validation demonstrated")


def example5_registry_operations():
    """Example 5: Advanced registry operations."""
    print("\n" + "=" * 60)
    print("Example 5: Registry Operations")
    print("=" * 60)

    # Create a local registry (separate from global)
    local_registry = PromptRegistry()

    # Register multiple prompts
    for i in range(3):
        prompt = PromptTemplate(
            name=f"test_prompt_{i}",
            role=PromptRole.SYSTEM,
            template=f"This is test prompt {i}",
            input_schema={"type": "object", "properties": {}},
            tags=["test", f"category_{i % 2}"],
        )
        local_registry.register(prompt)

    print(f"Registry size: {len(local_registry)}")
    print(f"All prompts: {local_registry.list_prompts()}")
    print(f"Category_0 prompts: {local_registry.list_prompts(tags=['category_0'])}")

    # Export and import
    export_data = local_registry.export_to_dict()
    print(f"\nExported {len(export_data)} prompts")

    # Create new registry and import
    new_registry = PromptRegistry()
    new_registry.load_from_dict(export_data)
    print(f"Imported to new registry: {len(new_registry)} prompts")

    print("\n✅ Registry operations completed")


def example6_pes_workflow():
    """Example 6: Complete PES workflow with templates."""
    print("\n" + "=" * 60)
    print("Example 6: PES Workflow Integration")
    print("=" * 60)

    # Simulate a PES workflow
    print("\n--- Phase 1: Planner ---")
    planner_system = get_prompt("evolve_planner_system")
    planner_user = get_prompt("evolve_planner_user")

    print(f"System prompt: {planner_system.name}")
    print(f"User prompt requires: {planner_user.get_required_variables()}")

    # Render planner prompts
    planner_system_text = planner_system.render()
    planner_user_text = planner_user.render(
        task_info="Optimize algorithm X",
        parent_solution='{"score": 0.9}',
        workspace="./workspace",
        island_num=4,
        parent_island=0,
        best_plan_path="./plan.txt",
    )

    print(
        f"✅ Planner prompts rendered ({len(planner_system_text + planner_user_text)} chars)"
    )

    print("\n--- Phase 2: Executor ---")
    executor_system = get_prompt("evolve_executor_system")
    executor_user = get_prompt("evolve_executor_user")

    executor_user_text = executor_user.render(
        task_info="Optimize algorithm X",
        improvement_plan="Improve time complexity from O(n^2) to O(n log n)",
        parent_score=0.9,
        parent_solution="def old_algo():\n    ...",
        previous_attempts="First attempt: O(n^2) → 0.85",
        solution_path="./solution.py",
    )

    print(f"✅ Executor prompts rendered ({len(executor_user_text)} chars)")

    print("\n--- Phase 3: Summary ---")
    summary_system = get_prompt("evolve_summary_system")
    summary_user = get_prompt("evolve_summary_user")

    summary_user_text = summary_user.render(
        task_info="Optimize algorithm X",
        parent_solution='{"score": 0.9, "solution": "..."}',
        child_solution='{"score": 0.95, "solution": "..."}',
        assessment_result="IMPROVEMENT",
        summary_path="./summary.txt",
    )

    print(f"✅ Summary prompts rendered ({len(summary_user_text)} chars)")

    print("\n✅ Complete PES workflow simulated")


def main():
    """Run all examples."""
    print("\n?? Prompt Template System Examples\n")

    example1_basic_usage()
    example2_builtin_prompts()
    example3_custom_prompt()
    example4_prompt_validation()
    example5_registry_operations()
    example6_pes_workflow()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)

    print("\nKey Takeaways:")
    print("1. PromptTemplate provides declarative prompt definition")
    print("2. Templates declare their required variables via schema")
    print("3. PromptRegistry manages all prompts centrally")
    print("4. Built-in prompts are auto-registered on import")
    print("5. Custom prompts can be easily added")
    print("6. Validation catches missing/incorrect variables early")

    print("\nNext Steps:")
    print("1. Define your own domain-specific prompts")
    print("2. Create YAML/JSON configs for prompt selection")
    print("3. Integrate with PES agents via configuration")
    print("4. Build prompt versioning and A/B testing")


if __name__ == "__main__":
    main()
