---
name: planning-solution
description: Plan a Python 3.7 algorithm for a SW Expert Academy coding problem and save it as plan_{trial_number}.md.
argument-hint: <problem_id> [trial_number]
---

Plan an algorithm for SW Expert Academy problem **$0**. The solution will be implemented in **Python 3.7 (PyPy 3.7)**. Do NOT write or run any code.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | No | Trial number for the plan file. If not provided, auto-increment from existing `plan_*.md` files in `./problem_bank/$0/` (or default to 1). |

## Step 1: Understand the problem

Read the problem statement from `./problem_bank/$0/problem.md` (saved by the `fetching-problem` skill). Identify:
- Input/output format
- Constraints — focus on the **Python** time/memory limits (typically the most generous)
- Sample test cases and expected outputs
- Edge cases and performance requirements implied by the constraints

## Step 2: Plan the algorithm

Think carefully and produce a plan covering:

1. **Problem analysis** — Restate the core problem in your own words. What is actually being asked?
2. **Key observations** — List mathematical properties, patterns, or invariants that simplify the problem.
3. **Algorithm choice** — Describe the algorithm and data structures you would use. Justify why this approach meets the Python 3.7 time/memory constraints (e.g., O(n log n) vs O(n^2)). Account for CPython/PyPy overhead when estimating feasibility.
4. **Step-by-step approach** — Break the solution into concrete implementation steps (pseudocode-level, not actual code).
5. **Edge cases** — List tricky inputs and how the algorithm handles them.
6. **Complexity analysis** — State time and space complexity and verify they fit within the Python constraints.

## Step 3: Save the plan

Determine the trial number: use `$1` if provided, otherwise find the next available number by checking existing `plan_*.md` files in `./problem_bank/$0/` (default to 1 if none exist).

Save the plan as Markdown:
- Path: `./problem_bank/$0/plan_{trial_number}.md`

[NOTE] DO NOT USE `import sys`. Instead use `input()` for reading input and `print()` for output.

[NOTE] DO NOT USE `import io`. Do NOT USE `import os`.

[NOTE] DO NOT import external packages like numpy, pandas, etc.
