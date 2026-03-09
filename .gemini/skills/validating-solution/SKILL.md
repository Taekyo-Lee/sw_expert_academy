---
name: validating-solution
description: Static code review of a solution to catch issues that pass local tests but fail on the PyPy 3.7 judge.
argument-hint: <problem_id> <trial_number>
---

Validate the solution for SW Expert Academy problem **$0**, trial **$1**, before submission.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | Yes | Trial number matching the solution file. |

## Paths

- **Problem statement**: `./problem_bank/$0/problem.md`
- **Solution file**: `./problem_bank/$0/python/solution_$1.py`

Both files must exist. If either is missing, tell the user and stop.

## Checks

Read the solution file and the problem statement, then perform **all** of the following checks. Collect every issue found before reporting.

### 1. Prohibited imports

Flag any `import` or `from … import` of:
- `sys`, `os`, `io`
- Any external package (`numpy`, `pandas`, `scipy`, `itertools` from C extensions, etc.)

Allowed: `collections`, `heapq`, `bisect`, `math`, `functools`, `itertools`, `string`, `re`, `copy`, `operator`, `decimal`, `fractions`, `array`, `queue`, `typing`, and other pure-Python stdlib modules.

### 2. Forbidden syntax (Python 3.8+)

Flag any use of:
- **Walrus operator** — `:=`
- **`match` / `case` statements** — Python 3.10+
- **f-string `=` specifier** — e.g., `f"{var=}"` (Python 3.8+)
- **Positional-only parameter syntax** — `/` in function signatures (Python 3.8+)

### 3. Output format

Read the expected output section from `problem.md` (under `## Sample` → `### Output`). Then inspect every `print()` call in the solution and check:

- **Prefix mismatch**: If the expected output uses a prefix like `#1`, `#2`, etc., verify the solution produces the same prefix format. Flag if the solution uses a different prefix (e.g., `Case #1:` vs `#1`).
- **Debug-style prints**: Flag any `print()` whose output clearly does not match the expected format — e.g., `print(f"tc: {tc}, answer: {ans}")`, `print("DEBUG:", ...)`, `print(f"{var=}")`.
- **Extra whitespace or separators**: Flag if the solution adds extra spaces, tabs, or newlines not present in the expected output format.

### 4. Debug artifacts

Flag:
- `print()` calls that write to `stderr` (e.g., `print(..., file=sys.stderr)`)
- `assert` statements (will raise `AssertionError` on edge cases)
- Commented-out `print()` or debug lines that were left in (informational only — not an auto-fix target unless they are uncommented)

### 5. I/O structure

Verify the solution follows the standard judge pattern:
1. Reads `T` (number of test cases) with `input()`.
2. Loops `T` times (e.g., `for test_case in range(1, T + 1):`).
3. Uses `input()` for all input reads (not `sys.stdin`).
4. Uses `print()` for all output (not `sys.stdout.write`).

Flag deviations.

## Result

This skill is a **read-only checker**. It does NOT modify the solution file.

### If issues found

Report **Validate — FAIL** with every issue listed, grouped by check category. The orchestrator (`solving-problem`) will hand the solution back to the Write agent for correction.

### If clean

Report **Validate — pass (no issues found).** The orchestrator proceeds to Submit.
