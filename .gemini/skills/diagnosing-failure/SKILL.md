---
name: diagnosing-failure
description: Reflect on a failed submission, diagnose the cause, and produce a revised plan.md.
argument-hint: <problem_id> <trial_number> <verdict> [output_trial_number]
---

Reflect on a failed submission for SW Expert Academy problem **$0** and update the plan. Do NOT write or run any code.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | Yes | The trial number that failed (e.g., `1`). |
| `$2` | third | Yes | The judge verdict: `WA`, `TLE`, `MLE`, or `RE`. |
| `$3` | fourth | No | Output trial number for the revised plan. Defaults to `$1 + 1` if omitted. Use the **same** trial number as `$1` when revising within a trial (e.g., after stress test failure). |

## Step 1: Gather context

Read all of the following:
- `./problem_bank/$0/problem.md` — the original problem statement.
- **If $1 ≤ 4**: read **all** plans (`plan_1.md` … `plan_$1.md`) and solutions (`solution_1.py` … `solution_$1.py`).
- **If $1 > 4**: read `plan_1.md` (original approach), plus the last 3 plans and solutions (`plan_{$1-2}.md` … `plan_$1.md` and `solution_{$1-2}.py` … `solution_$1.py`). This keeps context manageable while retaining the original approach and recent history.

Reading the history avoids repeating past mistakes and reveals patterns across attempts.

## Step 1.5: Cross-trial pattern analysis

> **Skip this step entirely when $1 < 3** (i.e., this is the first or second trial reflection). Only activate from trial 3 onward.

Perform the following four checks using the full history gathered in Step 1:

### A. Verdict pattern classification

Look at the verdict sequence across all trials and classify the pattern:

| Pattern | Definition |
|---------|------------|
| **Plateaued** | Same verdict repeating with roughly the same number of test cases passed. |
| **Oscillating** | Alternating between two verdicts (e.g., MLE → TLE → MLE or TLE → MLE → TLE). |
| **Regressing** | Fewer test cases passed than earlier trials, or new verdict type that is worse. |
| **Progressing** | Strictly more test cases passed, or verdict improving (e.g., RE → WA → WA with more passes). |

### B. Algorithm continuity check

Has the **fundamental algorithm** stayed the same across trials? The following count as "same algorithm":
- Encoding changes (tuple → int, dict → array)
- Data structure swaps (list → deque, dict → defaultdict)
- Micro-optimizations (inlining, local variable caching, reducing constant factors)
- I/O changes (input method, output buffering)

A **different algorithm** means a different time-complexity class or a fundamentally different problem decomposition (e.g., DP → greedy, brute-force → divide-and-conquer, BFS → binary search).

### C. Feasibility sanity check

Estimate actual resource usage for the current algorithm against the problem's constraints:

- **Time**: ~10^7 operations/sec for CPython, ~10^8 for PyPy. Multiply the algorithm's Big-O by the actual constant factors (inner loop operations, dictionary lookups, etc.).
- **Memory**: 28 bytes/int, 56 bytes/tuple, 50–100 bytes/dict entry, 56 bytes/list overhead + 8 bytes/pointer per element.

If the estimate exceeds **50% of either the time or memory limit**, flag the algorithm as **infeasible**.

### D. Stuck verdict

Declare **STUCK** if ANY of the following hold:
1. Pattern is **Plateaued** or **Oscillating**.
2. The fundamental algorithm has been **unchanged for 3+ consecutive trials** without the pattern being Progressing.
3. The feasibility check flags the current algorithm as **infeasible**.

If the pattern is **Progressing**, do NOT declare STUCK — the current approach is improving and should be continued.

Record the verdict (STUCK or NOT STUCK) and carry it forward to Step 2 and Step 3.

## Step 2: Diagnose the failure

The verdict is **$2**. Analyze the failed solution against the problem statement. Focus your diagnosis based on the verdict:

| Verdict | Focus areas |
|---------|-------------|
| **WA** (Wrong Answer) | Logic errors, off-by-one, misread problem constraints, wrong output format, missed edge cases. |
| **TLE** (Time Limit Exceeded) | Algorithm complexity too high, redundant computation, slow I/O, unnecessary data structure overhead. |
| **MLE** (Memory Limit Exceeded) | Excessive data structure sizes, recursion depth, unnecessary copies. |
| **RE** (Runtime Error) | Index out of bounds, division by zero, recursion limit, integer overflow, wrong input parsing. |

Clearly state:
1. **What went wrong** — the specific bug or bottleneck.
2. **Why** — root cause tied back to the problem constraints or edge cases.
3. **What the previous plan missed** — which assumption or step was flawed.

### Stuck-mode diagnosis

> Only applies when Step 1.5 declared **STUCK**. Skip this subsection otherwise.

When STUCK is declared, the standard diagnosis above is insufficient. Additionally:

1. **Prohibit further optimization** of the current algorithm. No more encoding changes, data structure swaps, constant-factor reductions, or inlining. These have been tried and have failed.
2. **State the fundamental limitation** explicitly with concrete numbers (e.g., "A sliding-window DP over N=10^5 states with K=10^3 transitions requires 10^8 operations and 800 MB — both exceed limits").
3. **Brainstorm 2+ fundamentally different algorithms** — each must have a different complexity class or problem decomposition. For each candidate:
   - Describe the approach in 1–2 sentences.
   - Run the feasibility sanity check (Step 1.5C) against it.
   - State whether it passes or fails feasibility.
4. **Select the most promising alternative** that passes the feasibility check. If no candidate passes feasibility in Python/PyPy, explicitly recommend the user consider a different language.

## Step 3: Produce a revised plan

Write an updated plan that fixes the diagnosed issue. The revised plan must include:

1. **Reflection summary** — verdict, what failed, and why (from Step 2).
2. **Problem analysis** — corrected understanding if the previous one was wrong; otherwise keep it.
3. **Key observations** — add any new observations; mark corrected ones.
4. **Algorithm choice** — keep or replace. If replacing, justify why the new approach avoids the previous failure. **If Step 1.5 declared STUCK, you MUST choose a different algorithm. Justify why it avoids the previous failure mode and passes the feasibility check.**
5. **Step-by-step approach** — updated implementation steps.
6. **Edge cases** — add any newly identified edge cases.
7. **Complexity analysis** — verify the revised approach fits within constraints.

[NOTE] DO NOT USE `import sys`. Instead use `input()` for reading input and `print()` for output.

[NOTE] DO NOT USE `import io`. Do NOT USE `import os`.

[NOTE] DO NOT import external packages like numpy, pandas, etc.

## Step 4: Save the revised plan

Determine the output trial number:
- If `$3` is provided, use `{output_trial}` = $3.
- Otherwise, use `{output_trial}` = $1 + 1.

Save the revised plan:
- Path: `./problem_bank/$0/plan_{output_trial}.md`

If `{output_trial}` equals `$1` (same trial — revising in place), **overwrite** the existing plan file.

After saving, the user should run `/writing-solution $0 {output_trial}` to implement the revised plan.
