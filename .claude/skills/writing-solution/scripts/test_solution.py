"""Run a solution against sample test cases from problem.md.

Usage: python test_solution.py <problem_id> <trial_number>

Set UV_PYTHON to override the Python version (default: 3.10).
"""
import os
import re
import subprocess
import sys

UV_PYTHON = os.environ.get("UV_PYTHON", "3.10")


def find_project_root(script_path):
    """Go 4 directories up from the script to reach the project root."""
    root = os.path.dirname(os.path.abspath(script_path))
    for _ in range(4):
        root = os.path.dirname(root)
    return root


def parse_sample(problem_md_path):
    """Extract sample input and output from problem.md.

    Looks for ## Sample -> ### Input -> fenced block, ### Output -> fenced block.
    """
    with open(problem_md_path, "r", encoding="utf-8") as f:
        text = f.read()

    sample_match = re.search(r"^## Sample\b", text, re.MULTILINE)
    if not sample_match:
        print("ERROR: No '## Sample' section found in problem.md")
        sys.exit(1)

    sample_text = text[sample_match.end():]

    input_match = re.search(
        r"^### Input\s*\n```\n(.*?)\n```",
        sample_text,
        re.MULTILINE | re.DOTALL,
    )
    if not input_match:
        print("ERROR: No '### Input' fenced block found under ## Sample")
        sys.exit(1)

    output_match = re.search(
        r"^### Output\s*\n```\n(.*?)\n```",
        sample_text,
        re.MULTILINE | re.DOTALL,
    )
    if not output_match:
        print("ERROR: No '### Output' fenced block found under ## Sample")
        sys.exit(1)

    return input_match.group(1), output_match.group(1)


def compare_output(expected, actual):
    """Compare expected vs actual output, tolerant of trailing whitespace.

    Returns (passed, diff_lines).
    """
    expected_lines = [line.rstrip() for line in expected.rstrip("\n").split("\n")]
    actual_lines = [line.rstrip() for line in actual.rstrip("\n").split("\n")]

    max_len = max(len(expected_lines), len(actual_lines))
    diff_lines = []
    passed = True

    for i in range(max_len):
        exp = expected_lines[i] if i < len(expected_lines) else "<missing>"
        act = actual_lines[i] if i < len(actual_lines) else "<missing>"
        if exp == act:
            diff_lines.append("  line %d: %s" % (i + 1, exp))
        else:
            passed = False
            diff_lines.append("- line %d (expected): %s" % (i + 1, exp))
            diff_lines.append("+ line %d (actual)  : %s" % (i + 1, act))

    return passed, diff_lines


def main():
    if len(sys.argv) != 3:
        print("Usage: python test_solution.py <problem_id> <trial_number>")
        sys.exit(1)

    problem_id = sys.argv[1]
    trial_number = sys.argv[2]

    project_root = find_project_root(__file__)
    problem_dir = os.path.join(project_root, "problem_bank", problem_id)
    problem_md = os.path.join(problem_dir, "problem.md")
    solution_py = os.path.join(
        problem_dir, "python", "solution_%s.py" % trial_number
    )

    if not os.path.isfile(problem_md):
        print("ERROR: %s not found" % problem_md)
        sys.exit(1)
    if not os.path.isfile(solution_py):
        print("ERROR: %s not found" % solution_py)
        sys.exit(1)

    sample_input, expected_output = parse_sample(problem_md)

    cmd = ["uv", "run", "--python", UV_PYTHON, solution_py]
    print("Running: %s" % " ".join(cmd))
    print("---")

    try:
        result = subprocess.run(
            cmd,
            input=sample_input,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("FAIL: Solution timed out after 30 seconds")
        sys.exit(1)

    if result.returncode != 0:
        print("FAIL: Solution exited with code %d" % result.returncode)
        if result.stderr.strip():
            print("stderr:")
            print(result.stderr.strip())
        sys.exit(1)

    actual_output = result.stdout
    passed, diff_lines = compare_output(expected_output, actual_output)

    if passed:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL: Output mismatch")
        print()
        for line in diff_lines:
            print(line)
        sys.exit(1)


if __name__ == "__main__":
    main()
