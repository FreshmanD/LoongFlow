#!/usr/bin/env python3
"""
Test script to verify the solution's analysis about subprocess signal handling.
"""
import os
import sys
import signal
import multiprocessing
import time
import json
from typing import Dict, Any

# Add parent directory to path to import the evaluator
sys.path.insert(0, '/Users/daixunan/baidu/agent/LoongFlow/src')

from loongflow.framework.pes.evaluator.evaluator import Evaluator


def create_test_evaluator():
    """Create a test evaluator instance."""
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class MockConfig:
        workspace_path: str = "/tmp/test_workspace"
        timeout: float = 2.0
        evaluate_code: str = """
def evaluate(llm_file_path):
    return {"score": 1.0, "metrics": {"test": "passed"}}
"""
        llm_config: Optional[Dict] = None

    return Evaluator(MockConfig())


def test_subprocess_signal_propagation():
    """Test if subprocesses properly handle SIGINT signals."""
    print("Test 1: Checking subprocess creation in evaluator...")

    # Read the actual code to verify claims
    evaluator_path = "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py"
    with open(evaluator_path, 'r') as f:
        content = f.read()

    # Check for multiprocessing.Process usage
    if 'multiprocessing.Process' not in content:
        print("  ✗ FAIL: No multiprocessing.Process found in code")
        return False

    # Check how processes are created
    lines = content.split('\n')
    process_creation_lines = []
    for i, line in enumerate(lines):
        if 'multiprocessing.Process' in line:
            # Get context
            context_start = max(0, i-2)
            context_end = min(len(lines), i+3)
            context = '\n'.join(lines[context_start:context_end])
            process_creation_lines.append(context)

    print(f"  ✓ Found {len(process_creation_lines)} multiprocessing.Process creations")

    # Check for signal handling parameters
    signal_handling_issues = []
    for context in process_creation_lines:
        # Check for preexec_fn parameter
        if 'preexec_fn' not in context:
            signal_handling_issues.append("Missing preexec_fn parameter")
        # Check for start_new_session
        if 'start_new_session' not in context:
            signal_handling_issues.append("Missing start_new_session parameter")

    if signal_handling_issues:
        print(f"  ✗ Signal handling issues found: {signal_handling_issues}")
        return False

    print("  ✓ All multiprocessing.Process creations appear to have proper signal handling")
    return True


def test_interrupt_method() -> bool:
    """Test the interrupt method's signal handling."""
    print("\nTest 2: Checking interrupt method implementation...")

    evaluator_path = "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py"
    with open(evaluator_path, 'r') as f:
        content = f.read()

    # Check if interrupt method exists
    if 'def interrupt(self):' not in content:
        print("  ✗ FAIL: No interrupt method found")
        return False

    # Extract interrupt method
    lines = content.split('\n')
    interrupt_start = None
    interrupt_end = None
    brace_count = 0

    for i, line in enumerate(lines):
        if 'def interrupt(self):' in line:
            interrupt_start = i
        elif interrupt_start is not None:
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count <= 0:
                    interrupt_end = i + 1
                    break

    if interrupt_start is None or interrupt_end is None:
        print("  ✗ Could not extract interrupt method")
        return False

    interrupt_method = '\n'.join(lines[interrupt_start:interrupt_end])

    # Check for proper signal handling in interrupt
    checks = [
        ('process.terminate()', 'Has SIGTERM handling'),
        ('process.kill()', 'Has SIGKILL fallback'),
        ('grace_period', 'Has grace period for graceful termination'),
        ('if process.is_alive():', 'Checks process status'),
    ]

    all_passed = True
    for check_str, description in checks:
        if check_str in interrupt_method:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False

    return all_passed


def test_subprocess_cleanup() -> bool:
    """Test cleanup logic for subprocesses."""
    print("\nTest 3: Checking subprocess cleanup in finally block...")

    evaluator_path = "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py"
    with open(evaluator_path, 'r') as f:
        content = f.read()

    # Look for finally block in _execute_evaluate_in_process
    if 'finally:' not in content:
        print("  ✗ No finally block found")
        return False

    # Check for cleanup
    checks = [
        ('process.terminate()', 'Has terminate in finally'),
        ('process.kill()', 'Has kill in finally'),
        ('process.is_alive()', 'Checks if process is alive'),
    ]

    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ Missing: {description}")
            all_passed = False

    return all_passed


def test_solution_assumptions() -> bool:
    """Test the specific assumptions in the solution."""
    print("\nTest 4: Verifying solution assumptions...")

    solution = {
        "assumption": "The agent creates child processes or subprocesses that don't properly propagate SIGINT signals, causing them to continue running after parent tries to exit",
        "evidences": [
            {
                "evidence_type": "NecessarySign",
                "description": "Agent code spawns subprocesses or child processes during execution",
                "collected_evidence": [
                    "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py:224:            f'[Parent] Preparing to spawn process for eval_id: {eval_id}'",
                    "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py:229-231:        process = multiprocessing.Process(target=self.__class__._run_evaluate_target, args=process_args)"
                ],
                "result": 1,
                "weight": "High"
            },
            {
                "evidence_type": "ConfirmingSign",
                "description": "Subprocess creation without proper signal handling or process group management",
                "collected_evidence": [
                    "Found multiprocessing.Process usage without preexec_fn, start_new_session, or process_group parameters",
                    "Process created with default parameters: multiprocessing.Process(target=self.__class__._run_evaluate_target, args=process_args)"
                ],
                "result": 1,
                "weight": "Medium"
            }
        ]
    }

    # Read the actual code at line 229-231
    with open('/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py', 'r') as f:
        lines = f.readlines()

    # Check lines 2285-231 (0-indexed)
    actual_lines = lines[228:232]  # Note: adjusting for 0-index
    print(f"  Checking lines 229-231: {''.join(actual_lines)}")

    # Verify the evidence
    expected_line = "process = multiprocessing.Process"
    if any(expected_line in line for line in actual_lines):
        print("  ✓ Evidence confirmed: Process creation found at line 229-231")
    else:
        print(f"  ✗ Evidence mismatch: Expected '{expected_line}' not found in lines")
        print(f"    Actual lines: {actual_lines}")
        return False

    # Check for signal handling parameters in all lines
    missing_params = []
    for line in actual_lines:
        if 'preexec_fn' not in line:
            missing_params.append('preexec_fn')
        if 'start_new_session' not in line:
            missing_params.append('start_new_session')
    # Remove duplicates
    missing_params = list(set(missing_params))

    if missing_params:
        print(f"  ✓ Confirming evidence: Missing signal handling parameters: {missing_params}")
        return True
    else:
        print("  ✗ Evidence refuted: Signal handling parameters are present")
        return False


def main() -> None:
    """Run all tests."""
    print("=" * 60)
    print("ACTIVE VERIFICATION OF SOLUTION")
    print("Solution: Analysis of subprocess signal handling issues")
    print("=" * 60)

    test_results = []

    # Run tests
    test_results.append(('Subprocess signal propagation', test_subprocess_signal_propagation()))
    test_results.append(('Interrupt method', test_interrupt_method()))
    test_results.append(('Subprocess cleanup', test_subprocess_cleanup()))
    test_results.append(('Solution assumptions', test_solution_assumptions()))

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    # Determine score based on verification
    if passed == total:
        print("\nScore: 1.0 (Objective fully verified)")
    elif passed >= 3:
        print("\nScore: 0.8 (Most assertions verified, minor gaps)")
    elif passed >= 2:
        print("\nScore: 0.6 (Partial verification, notable issues)")
    else:
        print("\nScore: 0.3 (Poor verification, major problems)")


if __name__ == "__main__":
    main()
