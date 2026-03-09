---
name: writing-solution
description: Write a Python 3.7 solution for a SW Expert Academy coding problem.
argument-hint: <problem_id> [trial_number]
---

Write a Python 3.7 (PyPy 3.7) solution for SW Expert Academy problem **$0**.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | No | Trial number matching the plan file. If not provided, use the latest `plan_*.md` number in `./problem_bank/$0/`. |

## Step 1: Read the problem and plan

Determine the trial number: use `$1` if provided, otherwise find the latest `plan_*.md` number in `./problem_bank/$0/`.

1. Read the problem statement from `./problem_bank/$0/problem.md` (saved by the `fetching-problem` skill). Pay close attention to I/O format, constraints, and sample test cases.
2. Read the plan from `./problem_bank/$0/plan_{trial_number}.md` (saved by the `planning-solution` skill). The trial number determines the matching solution file name — `solution_{trial_number}.py`. If the specified plan does not exist, plan the algorithm yourself before proceeding.

## Step 2: Write the solution

1. Follow the algorithm described in the plan.
2. Implement the solution in **Python 3.7**.
3. Avoid the walrus operator (`:=`) — it requires Python 3.8+ and may behave differently from PyPy 3.7.

### I/O patterns

- SW Expert Academy typically provides `T` test cases. Output format varies per problem — read the problem statement carefully. Many problems use `#N answer`, but not all.
- The judge runs code using this template structure:
  ```python
  T = int(input())
  for test_case in range(1, T + 1):
      # your solution here
  ```
  Your solution must follow this pattern — read `T` with `input()`, then loop over each test case.
  `import sys` will raise an error.

## Step 3: Save the code

Save the code locally:
- Path: `./problem_bank/$0/python/solution_{trial_number}.py`
- The trial number **must match** the plan file number — `plan_{trial_number}.md` → `solution_{trial_number}.py`.

[NOTE] DO NOT USE `import sys`. Instead use `input()` for reading input and `print()` for output.

[NOTE] DO NOT USE `import io`. Do NOT USE `import os`.

[NOTE] DO NOT import external packages like numpy, pandas, etc.

## Step 4: Test the solution

Run the solution against the sample test cases from `problem.md`:

```
uv run --python 3.10 .gemini/skills/writing-solution/scripts/test_solution.py $0 {trial_number}
```

- If the test **passes**, you're done.
- If the test **fails**, read the diff output, fix the solution, re-save, and re-test until the sample passes.

> **Note:** The test runner uses CPython 3.10 by default (override via `UV_PYTHON` env var). Write Python 3.7-compatible code — avoid walrus operator (`:=`), `match`/`case`, and other 3.8+ features.
