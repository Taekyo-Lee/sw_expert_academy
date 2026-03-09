# Plan 2: Problem 24702 - 2의 거듭제곱 (Powers of 2)

## Reflection Summary

- **Verdict**: RE (Runtime Error) — `import io is prohibited`
- **What failed**: The solution used `import io as _io` for fast buffered I/O (`BufferedReader`, `FileIO`, `BufferedWriter`). The SW Expert Academy judge forbids importing the `io` module.
- **Root cause**: The I/O layer in `solution_1.py` (lines 1, 160-171) relied on the `io` module. The judge environment blocks this import, causing a runtime error before any computation begins.
- **What the previous plan missed**: The plan's I/O section mentioned using `input()` and joining outputs, but the implementation deviated by using `io`-based buffered I/O for speed. The project constraints also forbid `import sys`, and by extension the judge appears to block `import io` as well.

## Problem Analysis

(Unchanged from Plan 1 — the algorithm itself is correct.)

Given a natural number X (1 <= X <= 10^11), find any N (1 <= N < 10^50) such that X appears as a **substring** of f(N), where f(N) is the last 100 digits of 2^N (or 2^N itself if it has fewer than 100 digits).

- Up to ~12190 test cases, combined time limit 30s (Python).
- Memory limit: 256MB.

## Key Observations

(Unchanged from Plan 1.)

1. **Structure of the last digits of 2^N**: For N >= K, the value 2^N mod 10^K is always divisible by 2^K. The non-trivial part is 2^N mod 5^K, since 10^K = 2^K * 5^K and CRT applies.

2. **Primitive root**: 2 is a primitive root modulo 5^k for all k >= 1. The order of 2 mod 5^k is 4 * 5^(k-1).

3. **Bound on K**: We use K = 71. The order of 2 mod 5^71 is 4 * 5^70 ~ 3.4 * 10^49 < 10^50, so any valid N from the discrete log will be < 10^50.

4. **Constructive approach**: Construct a 71-digit target T containing X as a substring, with T divisible by 2^71 and coprime to 5. Then find N via discrete log mod 5^71.

5. **P-adic discrete log**: Iterative Hensel-style lifting from mod 5 to mod 5^71, O(K) big-integer operations per test case.

**New observation**:
6. **I/O restrictions**: The judge forbids `import io` and `import sys`. All I/O must use `input()` and `print()`. To handle ~12000 test cases efficiently, collect all outputs in a list and print with a single `print('\n'.join(out))` call at the end.

## Algorithm Choice

**Discrete logarithm via p-adic lifting** (Hensel-style) — same as Plan 1. The algorithm is correct; only the I/O layer needs to change.

## Step-by-Step Approach

### Precomputation (done once)

(Identical to Plan 1.)

1. Set K = 71, mod5 = 5^71, order = 4 * 5^70.
2. Compute h = pow(2, 4, mod5) — generator of the 5-Sylow subgroup.
3. Build h_powers[j] = h^(5^j) mod mod5 for j = 0..70 iteratively.
4. Build h_powers_inv[j] = modular inverse of h_powers[j] mod mod5, using iterative extended GCD (not recursive, to avoid any stack issues).
5. Precompute pow5[j] = 5^j for j = 0..K+1.
6. For each level j (0..K-2), precompute inv_ej[j] from the p-adic structure.
7. Precompute g_inv = modinv(2, mod5) and g_inv_table[k] for k = 0..3.
8. Precompute h_inv_pow[j][c] = h_powers_inv[j]^c mod mod5 for j=0..K-1, c=0..4.
9. Precompute pow2K = 2^71, pow10_50 = 10^50.

### Per Test Case

(Identical to Plan 1.)

**Step A: Construct target T** — place X at digit position 50, enforce divisibility by 2^71 and coprimality to 5.

**Step B: Discrete log** — find N such that 2^N ≡ T (mod 5^71) via p-adic lifting.

**Step C: Adjust N** — if N < 71, add order.

**Step D: Output N**.

### I/O (CHANGED)

- **No imports at all**. No `import sys`, no `import io`, no external packages.
- Read input using `input()`.
- Collect all answers in a list.
- Output with a single `print('\n'.join(out))` at the end.
- Use an **iterative** (not recursive) extended GCD to compute modular inverses, avoiding any potential recursion depth issues.

## Edge Cases

(Unchanged from Plan 1.)

1. X = 1: Valid; algorithm finds some N.
2. X = 10^11 (12 digits): Fits at position 50 within 71-digit T.
3. X contains digit 5: X is in the middle; last digit of T is forced != 0 or 5.
4. Small X (e.g., X = 2): Works fine.
5. N = 0 from discrete log: Adding the order makes N > 71 and > 1.

## Complexity Analysis

(Unchanged from Plan 1.)

- **Time**: Precomputation O(K) modular exponentiations. Per test case O(K) big-int ops on ~50-digit numbers. Total for ~12000 cases: ~840K big-int ops. Well within 30s on PyPy.
- **Space**: O(K) precomputed tables, each ~50-digit integers. Negligible.

## Changes from Plan 1

1. **Remove `import io`** — replace all `io`-based I/O with `input()` / `print()`.
2. **Use iterative extended GCD** instead of recursive `_extended_gcd`.
3. **No imports whatsoever** in the solution file.
