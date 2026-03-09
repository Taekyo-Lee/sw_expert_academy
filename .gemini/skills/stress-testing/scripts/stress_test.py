"""Run a solution against a stress test input and report timing.

Usage: python stress_test.py <problem_id> <trial_number> <test_input_path>

Set UV_PYTHON to override the Python version (default: 3.10).
"""
import os
import subprocess
import sys
import time

UV_PYTHON = os.environ.get("UV_PYTHON", "3.10")


def find_project_root(script_path):
    """Go 4 directories up from the script to reach the project root."""
    root = os.path.dirname(os.path.abspath(script_path))
    for _ in range(4):
        root = os.path.dirname(root)
    return root


def main():
    if len(sys.argv) != 4:
        print("Usage: python stress_test.py <problem_id> <trial_number> <test_input_path>")
        sys.exit(1)

    problem_id = sys.argv[1]
    trial_number = sys.argv[2]
    test_input_path = sys.argv[3]

    project_root = find_project_root(__file__)
    solution_py = os.path.join(
        project_root, "problem_bank", problem_id, "python",
        "solution_%s.py" % trial_number,
    )

    if not os.path.isfile(solution_py):
        print("ERROR: %s not found" % solution_py)
        sys.exit(1)
    if not os.path.isfile(test_input_path):
        print("ERROR: %s not found" % test_input_path)
        sys.exit(1)

    with open(test_input_path, "r", encoding="utf-8") as f:
        test_input = f.read()

    test_name = os.path.basename(test_input_path)
    cmd = ["uv", "run", "--python", UV_PYTHON, solution_py]

    print("TEST: %s" % test_name)

    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            input=test_input,
            capture_output=True,
            text=True,
            timeout=60,
        )
        elapsed = time.monotonic() - start
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        print("TIME: %.3fs" % elapsed)
        print("EXIT: timeout")
        print("OUTPUT_LINES: 0")
        print("OUTPUT_PREVIEW: (timed out after 60s)")
        print("STATUS: FAIL")
        sys.exit(1)

    print("TIME: %.3fs" % elapsed)
    print("EXIT: %d" % exit_code)

    if exit_code != 0:
        output_lines = 0
        preview = result.stderr.strip() if result.stderr.strip() else "(no output)"
        # Truncate long error output
        if len(preview) > 500:
            preview = preview[:500] + "..."
        print("OUTPUT_LINES: %d" % output_lines)
        print("OUTPUT_PREVIEW: %s" % preview)
        print("STATUS: FAIL")
        sys.exit(1)

    output = result.stdout
    output_line_list = output.rstrip("\n").split("\n") if output.strip() else []
    output_lines = len(output_line_list)

    # Show first few lines of output as preview
    preview_lines = output_line_list[:5]
    if output_lines > 5:
        preview_lines.append("... (%d more lines)" % (output_lines - 5))
    preview = "\n".join(preview_lines)

    print("OUTPUT_LINES: %d" % output_lines)
    print("OUTPUT_PREVIEW: %s" % preview)

    # Classify result
    if elapsed < 2.0:
        print("STATUS: PASS")
        sys.exit(0)
    elif elapsed < 5.0:
        print("STATUS: WARNING")
        sys.exit(0)
    else:
        print("STATUS: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
