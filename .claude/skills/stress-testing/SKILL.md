---
name: stress-testing
description: Generate max-size stress test inputs and measure execution time to catch TLE/RE before submission.
argument-hint: <problem_id> <trial_number>
---

Stress-test the solution for SW Expert Academy problem **$0**, trial **$1**, with generated max-size inputs.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | Yes | Trial number matching the solution file. |

## Paths

- **Problem statement**: `./problem_bank/$0/problem.md`
- **Solution file**: `./problem_bank/$0/python/solution_$1.py`
- **Test output directory**: `./problem_bank/$0/tests/`

Both the problem statement and solution file must exist. If either is missing, tell the user and stop.

## Steps

### 1. Extract constraints

Read `problem.md` and extract **all numerical constraints** that define input size:

- Number of test cases T (and its range)
- Size parameters: N, M, Q, K, etc. (and their ranges)
- Value ranges for array elements, coordinates, weights, etc.
- Structural rules: "graph is a tree", "points are distinct", "string contains only lowercase letters", etc.

List these constraints explicitly before proceeding — they drive all test generation.

### 2. Generate test input files

Create 3 test input files in `./problem_bank/$0/tests/`. Each file must be **valid** per the problem's input specification (correct format, values within stated ranges, structural constraints satisfied).

**All tests use T=1** to isolate per-case timing.

#### `edge_max.txt` — Maximum size

All size parameters at their maximum values. Catches TLE on large inputs.

- Use the largest allowed N, M, Q, K, etc.
- Fill arrays/matrices with valid values (arbitrary, e.g., all same value or sequential).
- For strings, generate max-length strings with valid characters.

#### `edge_min.txt` — Minimum size

All size parameters at their minimum values. Catches RE on edge cases.

- Use the smallest allowed N, M, Q, etc. (often 1).
- Use boundary values (0, 1, minimum allowed).

#### `edge_adversarial.txt` — Worst-case patterns

Max size with adversarial patterns designed to trigger worst-case behavior. Catches TLE on pathological inputs.

Choose patterns based on the algorithm type:
- **Sorting/searching**: Already-sorted or reverse-sorted input.
- **Graph/tree**: Linear chain (depth = N), star graph, or fully connected.
- **String matching**: All same character, or patterns that maximize backtracking.
- **DP/optimization**: Values that maximize state space or force worst-case transitions.
- **Queries**: All queries targeting the same element/range, or queries in worst-case order.
- **General**: All identical values, extreme value ratios (all min or all max values), alternating patterns.

#### Generation approach

- For **simple inputs** (arrays, single values), write the test data directly as text.
- For **complex inputs** (trees, graphs, permutations, geometric constraints), write and execute a small inline Python generator script to produce valid input. Run the generator via Bash and capture its output to the test file.
- Always verify the generated file starts with `1` (T=1) on the first line.

### 3. Run stress tests

Run each test file through the runner script:

```
uv run --python 3.10 {skill_dir}/scripts/stress_test.py $0 $1 {test_file}
```

Where `{test_file}` is the **absolute path** to each of the 3 generated test files.

Run all 3 tests. Do not stop early on failure — run all tests so the full picture is available for diagnosis.

### 4. Analyze results

For each test, classify the result:

| Wall-clock time | Status | Meaning |
|-----------------|--------|---------|
| < 2 seconds | **PASS** | Comfortably within limits |
| 2–5 seconds | **WARNING** | Borderline — CPython is ~3-10x slower than PyPy, so 2s CPython ≈ 0.2-0.7s PyPy. May pass but risky. |
| >= 5 seconds | **FAIL** | Likely TLE on judge |
| Non-zero exit code | **FAIL** | Runtime error (RE) |
| Timeout (60s) | **FAIL** | Extreme TLE |

## Result

This skill is a **read-only checker** (it does not modify the solution file). It generates test inputs and measures performance.

### If any test FAILs

Report **Stress Test — FAIL** with:
- Each test file name, wall-clock time, and status
- For RE failures: include the error output
- For TLE failures: note the exact time to help estimate optimization needed

### If all tests PASS (warnings are acceptable)

Report **Stress Test — pass** with:
- Each test file name, wall-clock time, and status
- Note any warnings for awareness
