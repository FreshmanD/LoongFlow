#!/usr/bin/env python3
"""Test script to verify the solution analysis"""

import json
import os

def verify_solution_structure(solution: dict) -> dict:
    """Verify the structure and claims of the solution analysis"""
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "test_details": []
    }

    # Test 1: Verify assumption exists and is non-empty
    if "assumption" in solution and solution["assumption"]:
        results["tests_passed"] += 1
        results["test_details"].append({"test": "assumption_exists", "status": "PASS", "note": f"Assumption: {solution['assumption'][:100]}..."})
    else:
        results["tests_failed"] += 1
        results["test_details"].append({"test": "assumption_exists", "status": "FAIL", "note": "Missing or empty assumption"})

    # Test 2: Verify evidences list exists and is non-empty
    if "evidences" in solution and isinstance(solution["evidences"], list) and len(solution["evidences"]) > 0:
        results["tests_passed"] += 1
        results["test_details"].append({"test": "evidences_exist", "status": "PASS", "note": f"Found {len(solution['evidences'])} evidence items"})
    else:
        results["tests_failed"] += 1
        results["test_details"].append({"test": "evidences_exist", "status": "FAIL", "note": "Missing or empty evidences list"})

    # Test 3: Verify each evidence has required structure
    required_fields = ["evidence_type", "description", "collected_evidence", "result", "weight"]
    for i, evidence in enumerate(solution.get("evidences", [])):
        all_fields_present = all(field in evidence for field in required_fields)
        if all_fields_present:
            results["tests_passed"] += 1
            results["test_details"].append({"test": f"evidence_{i}_structure", "status": "PASS", "note": f"Evidence {i} has all required fields"})
        else:
            results["tests_failed"] += 1
            missing = [field for field in required_fields if field not in evidence]
            results["test_details"].append({"test": f"evidence_{i}_structure", "status": "FAIL", "note": f"Evidence {i} missing fields: {missing}"})

    # Test 4: Check for multiprocessing.Process usage in evidence
    process_creation_found = False
    for evidence in solution.get("evidences", []):
        evidence_text = json.dumps(evidence)
        if "multiprocessing.Process" in evidence_text or "Process creation" in evidence_text:
            process_creation_found = True
            break

    if process_creation_found:
        results["tests_passed"] += 1
        results["test_details"].append({"test": "multiprocessing_mentioned", "status": "PASS", "note": "Found multiprocessing.Process references in evidence"})
    else:
        results["tests_failed"] += 1
        results["test_details"].append({"test": "multiprocessing_mentioned", "status": "FAIL", "note": "No multiprocessing.Process references found"})

    # Test 5: Check for process group/signal issues
    process_group_mentioned = False
    relevant_keywords = ["SIGINT", "signal", "process group", "session", "preexec_fn", "start_new_session"]
    for evidence in solution.get("evidences", []):
        evidence_text = json.dumps(evidence)
        if any(keyword in evidence_text for keyword in relevant_keywords):
            process_group_mentioned = True
            break

    if process_group_mentioned:
        results["tests_passed"] += 1
        results["test"].append({"test": "process_group_issue_mentioned", "status": "PASS", "note": "Process group/signal issues mentioned"})
    else:
        results["tests_failed"] += 1
        results["test"].append({"test": "process_group_issue_mentioned", "status": "FAIL", "note": "No process group/signal issues mentioned"})

    return results

def verify_file_exists(path: str) -> dict:
    """Verify that a file exists"""
    if os.path.exists(path):
        return {"exists": True, "size": os.path.getsize(path)}
    else:
        return {"exists": False}

def main():
    """Main verification function"""
    solution_path = "/Users/daixunan/baidu/agent/LoongFlow/output-hello-world/4eee7227-a189-49ea-b5c9-a6ca2f944324/3/evaluator/solution.json"

    # Check if solution file exists
    file_check = verify_file_exists(solution_path)
    print(f"File check: {json.dumps(file_check, indent=2)}")

    if not file_check["exists"]:
        print("\nError: Solution file does not exist")
        return

    # Load solution
    try:
        with open(solution_path, 'r') as f:
            solution = json.load(f)
    except json.JSONDecodeError as e:
        print(f"\nError: Failed to parse solution JSON: {e}")
        return

    print(f"\nSolution loaded successfully")
    print(f"Assumption length: {len(solution.get('assumption', ''))} characters")
    print(f"Number of evidences: {len(solution.get('evidences', []))}")

    # Verify solution structure
    verification_results = verify_solution_structure(solution)

    print(f"\nVerification Results:")
    print(f"Tests Passed: {verification_results['tests_passed']}")
    print(f"Tests Failed: {verification_results['tests_failed']}")
    print(f"Total Tests: {verification_results['tests_passed'] + verification_results['tests_failed']}")

    print(f"\nTest Details:")
    for test_detail in verification_results["test_details"]:
        print(f"  {test_detail['test']}: {test_detail['status']} - {test_detail['note']}")

if __name__ == "__main__":
    main()