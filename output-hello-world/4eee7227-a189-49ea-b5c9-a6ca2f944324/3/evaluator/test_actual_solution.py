#!/usr/bin/env python3
"""Test the actual solution provided for evaluation"""

import json

# The solution to evaluate
solution = {
  "assumption": "Process group management failures cause inconsistent SIGINT propagation to child processes, with timing dependencies affecting whether signals reach all processes",
  "evidences": [
    {
      "evidence_type": "NecessarySign",
      "description": "Multiple concurrent subprocesses or child processes in agent execution",
      "collected_evidence": [
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py",
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/executor/executor.py",
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/agentsdk/base_agent.py"
      ],
      "result": 1,
      "weight": "High"
    },
    {
      "evidence_type": "ConfirmingSign",
      "description": "Process creation patterns that vary based on agent state or task phase (explaining intermittency)",
      "collected_evidence": [
        "Found process creation logic in evaluator.py lines 224-231 that creates multiprocessing.Process instances",
        "The process creation occurs in an evaluation loop that may have different timing based on eval_id and task state",
        "Process creation uses multiprocessing.Process with target=self.__class__._run_evaluate_target, args=process_args",
        "No preexec_fn or start_new_session parameters found, indicating default process group inheritance",
        "Lines 200-250 show process startup sequence with logging that may complete quickly or slowly based on system load"
      ],
      "result": 1,
      "weight": "Medium"
    },
    {
      "evidence_type": "ContraIndicator",
      "description": "Consistent process group configuration using preexec_fn=os.setsid or start_new_session=True across all spawn sites",
      "collected_evidence": [],
      "result": 1,
      "weight": "High"
    }
  ]
}

def verify_solution() -> dict:
    """Verify the solution structure and claims"""
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "issues_found": [],
        "verifications_performed": []
    }

    # Test 1: Verify assumption is non-empty and relates to process groups
    results["verifications_performed"].append("Checking assumption validity")
    if not solution.get("assumption"):
        results["tests_failed"] += 1
        results["issues_found"].append("Empty assumption")
    elif "process group" in solution["assumption"].lower() and "SIGINT" in solution["assumption"]:
        results["tests_passed"] += 1
        results["verifications_performed"].append(f"Assumption addresses process group and SIGINT: {solution['assumption'][:80]}...")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append("Assumption doesn't address process group and SIGINT issues")

    # Test 2: Verify evidences list has 3 items
    results["verifications_performed"].append("Checking number of evidence items")
    if len(solution.get("evidences", [])) == 3:
        results["tests_passed"] += 1
        results["verifications_performed"].append("Found 3 evidence items as expected")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append(f"Expected 3 evidence items, found {len(solution.get('evidences', []))}")

    # Test 3: Check evidence types
    expected_types = ["NecessarySign", "ConfirmingSign", "ContraIndicator"]
    results["verifications_performed"].append("Checking evidence types")
    actual_types = [ev.get("evidence_type") for ev in solution.get("evidences", [])]
    if actual_types == expected_types:
        results["tests_passed"] += 1
        results["verifications_performed"].append(f"Evidence types match: {actual_types}")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append(f"Evidence types mismatch. Expected {expected_types}, got {actual_types}")

    # Test 4: Verify file paths in first evidence
    results["verifications_performed"].append("Verifying file paths in first evidence")
    first_evidence = solution["evidences"][0]
    file_paths = first_evidence.get("collected_evidence", [])
    if len(file_paths) == 3 and all(path.endswith('.py') for path in file_paths):
        results["tests_passed"] += 1
        results["verifications_performed"].append(f"Found 3 Python files: {[p.split('/')[-1] for p in file_paths]}")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append(f"File paths issue in first evidence: {file_paths}")

    # Test 5: Check second evidence contains process creation details
    results["verifications_performed"].append("Checking process creation evidence")
    second_evidence = solution["evidences"][1]
    evidence_text = ' '.join(str(item) for item in second_evidence.get("collected_evidence", []))
    if "multiprocessing.Process" in evidence_text and "process creation" in evidence_text.lower():
        results["tests_passed"] += 1
        results["verifications_performed"].append("Found multiprocessing.Process and process creation details")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append("Missing multiprocessing.Process details in second evidence")

    # Test 6: Check for preexec_fn/setsid mention in third evidence
    results["verifications_performed"].append("Checking for process group configuration evidence")
    third_evidence = solution["evidences"][2]
    third_text = ' '.join(str(item) for item in third_evidence.get("collected_evidence", []))
    if "preexec_fn" in third_text or "os.setsid" in third_text or "start_new_session" in third_text:
        results["tests_passed"] += 1
        results["verifications_performed"].append("Found preexec_fn/os.setsid/start_new_session references")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append("Missing process group configuration details")

    # Test 7: Verify result values are 1
    results["verifications_performed"].append("Checking result values")
    all_results_are_1 = all(ev.get("result") == 1 for ev in solution.get("evidences", []))
    if all_results_are_1:
        results["tests_passed"] += 1
        results["verifications_performed"].append("All evidence results are 1")
    else:
        results["tests_failed"] += 1
        results["issues_found"].append("Not all evidence results are 1")

    return results

def main():
    """Run verification and display results"""
    print("=== Solution Verification ===\n")

    print("Solution Summary:")
    print(f"  Assumption: {solution['assumption'][:150]}...")
    print(f"  Number of evidences: {len(solution['evidences'])}")
    for i, ev in enumerate(solution['evidences']):
        print(f"  Evidence {i+1}: {ev['evidence_type']} - {ev['description'][:80]}...")

    print("\n" + "="*50 + "\n")

    # Run verification
    results = verify_solution()

    print("Verification Results:")
    print(f"  Tests Passed: {results['tests_passed']}")
    print(f"  Tests Failed: {results['tests_failed']}")
    print(f"  Total Tests: {results['tests_passed'] + results['tests_failed']}")

    if results['issues_found']:
        print("\nIssues Found:")
        for issue in results['issues_found']:
            print(f"  - {issue}")

    print("\nVerifications Performed:")
    for verification in results['verifications_performed']:
        print(f"  - {verification}")

    # Determine overall score
    total_tests = results['tests_passed'] + results['tests_failed']
    if total_tests == 0:
        score = 0.0
    else:
        score = results['tests_passed'] / total_tests

    print(f"\nOverall Score: {score:.2f}")

    if score >= 0.8:
        print("Status: Solution is well-structured and addresses the problem")
    elif score >= 0.6:
        print("Status: Solution has some issues but addresses core aspects")
    else:
        print("Status: Solution has significant issues")

if __name__ == "__main__":
    main()