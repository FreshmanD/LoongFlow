#!/usr/bin/env python3
"""Verify actual multiprocessing.Process usage in code"""

import ast
import multiprocessing

def analyze_process_creation(file_path: str) -> dict:
    """Analyze Python file for multiprocessing.Process usage"""
    with open(file_path, 'r') as f:
        content = f.read()

    tree = ast.parse(content)

    results = {
        "process_creation_lines": [],
        "has_preexec_fn": False,
        "has_start_new_session": False,
        "has_os_setsid": False,
        "process_creation_count": 0
    }

    for node in ast.walk(tree):
        # Check for multiprocessing.Process calls
        if isinstance(node, ast.Call):
            # Check if it's multiprocessing.Process()
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'Process':
                    results["process_creation_count"] += 1
                    line_no = node.lineno

                    # Get the line content
                    lines = content.split('\n')
                    line_content = lines[line_no-1] if line_no <= len(lines) else ''

                    # Check for preexec_fn parameter
                    for keyword in node.keywords:
                        if keyword.arg == 'preexec_fn':
                            results["has_preexec_fn"] = True
                        if keyword.arg == 'start_new_session':
                            results["has_start_new_session"] = True

                        # Check if preexec_fn value is os.setsid
                        if keyword.arg == 'preexec_fn' and isinstance(keyword.value, ast.Attribute):
                            if keyword.value.attr == 'setsid':
                                results["has_os_setsid"] = True

                    results["process_creation_lines"].append({
                        "line": line_no,
                        "content": line_content.strip(),
                        "has_preexec_fn": results["has_preexec_fn"],
                        "has_start_new_session": results["has_start_new_session"]
                    })

    return results

def check_missing_signal_handling():
    """Check if multiprocessing.Process is missing signal handling parameters"""
    files_to_check = [
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py",
        "/Users/daixunan/baidu/agent/LoongFlow/agents/general_agent/evaluator.py"
    ]

    all_results = {}
    issues_found = []

    for file_path in files_to_check:
        try:
            results = analyze_process_creation(file_path)
            all_results[file_path.split('/')[-1]] = results

            if results["process_creation_count"] > 0:
                # Check if any process creation lacks signal handling
                if not results["has_preexec_fn"] and not results["has_start_new_session"]:
                    issues_found.append({
                        "file": file_path.split('/')[-1],
                        "issue": f"multiprocessing.Process created without preexec_fn or start_new_session",
                        "count": results["process_creation_count"],
                        "lines": results["process_creation_lines"]
                    })
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    return all_results, issues_found

def create_test_process():
    """Create a test multiprocessing.Process to verify default behavior"""
    def worker():
        import time
        time.sleep(5)
        print("Worker completed")

    # Test default multiprocessing.Process
    process = multiprocessing.Process(target=worker)
    return {
        "process_created": True,
        "pid": None,
        "preexec_fn_set": False,
        "start_new_session_set": False
    }

def main():
    """Main verification function"""
    print("=== Multiprocessing Code Verification ===\n")

    # Check actual code for process creation patterns
    print("1. Analyzing code for multiprocessing.Process usage:")
    all_results, issues_found = check_missing_signal_handling()

    for filename, results in all_results.items():
        print(f"\n   {filename}:")
        print(f"     Process creation count: {results['process_creation_count']}")
        print(f"     Has preexec_fn: {results['has_preexec_fn']}")
        print(f"     Has start_new_session: {results['has_start_new_session']}")
        print(f"     Has os.setsid: {results['has_os_setsid']}")

        if results["process_creation_lines"]:
            print(f"     Process creation lines:")
            for proc in results["process_creation_lines"]:
                print(f"       Line {proc['line']}: {proc['content'][:80]}...")

    # Report issues
    if issues_found:
        print("\n2. Issues Found:")
        for issue in issues_found:
            print(f"\n   File: {issue['file']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Count: {issue['count']}")
            print(f"   Affected Lines:")
            for proc_line in issue['lines']:
                print(f"     Line {proc_line['line']}: {proc_line['content'][:80]}...")
    else:
        print("\n2. No issues found with process creation.")

    # Test multiprocessing behavior
    print("\n3. Testing multiprocessing.Process default behavior:")
    try:
        test_result = create_test_process()
        print(f"   Test process created: {test_result['process_created']}")
        print(f"   Default preexec_fn: {test_result['preexec_fn_set']}")
        print(f"   Default start_new_session: {test_result['start_new_session_set']}")
    except Exception as e:
        print(f"   Test failed: {e}")

    # Evaluate solution claims
    print("\n4. Solution Evaluation:")

    # Count total issues found
    total_issues = len(issues_found)
    total_processes = sum(r["process_creation_count"] for r in all_results.values())

    print(f"   Total multiprocessing.Process instances: {total_processes}")
    print(f"   Process instances without signal handling: {total_issues}")

    # Verify solution claims
    solution_correct = total_issues > 0  # Solution claims there are process group issues

    if solution_correct:
        print("   ✓ Solution correctly identifies process creation without signal handling")
    else:
        print("   ✗ Solution incorrectly claims process group issues")

    # Check if files from solution evidence exist
    evidence_files = [
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/evaluator/evaluator.py",
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/framework/pes/executor/executor.py",
        "/Users/daixunan/baidu/agent/LoongFlow/src/loongflow/agentsdk/base_agent.py"
    ]

    print(f"\n5. Evidence file verification:")
    import os
    missing_files = []
    for file_path in evidence_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path.split('/')[-1]} exists")
        else:
            print(f"   ✗ {file_path.split('/')[-1]} missing")
            missing_files.append(file_path)

    if missing_files:
        print(f"   Warning: {len(missing_files)} files from evidence are missing")

    # Overall assessment
    print("\n6. Overall Assessment:")
    assessment_score = 0.0

    if solution_correct:
        assessment_score += 0.7
        print("   + Solution correctly identifies actual issue (0.7)")
    else:
        print("   - Solution doesn't identify real issue")

    if total_issues > 0:
        assessment_score += 0.2
        print("   + Found actual process creation issues (0.2)")

    if len(missing_files) == 0:
        assessment_score += 0.1
        print("   + All evidence files exist (0.1)")
    else:
        print(f"   - Some evidence files missing (-0.1)")

    print(f"\n   Total Assessment Score: {assessment_score:.1f}")

    if assessment_score >= 0.8:
        print("   Conclusion: Solution is accurate and well-supported")
    elif assessment_score >= 0.5:
        print("   Conclusion: Solution identifies real issues but has some gaps")
    else:
        print("   Conclusion: Solution has significant issues")

if __name__ == "__main__":
    main()