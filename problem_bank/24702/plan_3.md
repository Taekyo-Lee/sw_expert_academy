# Plan 3: Problem 24702 - 2의 거듭제곱 (Powers of 2)

## Reflection Summary

- **Verdict**: WA — only 4400 out of 12190 test cases pass.
- **What failed**: The algorithm produces mathematically correct answers that are verifiable on CPython, but the judge rejects about 64% of them. Exhaustive local testing (X=1..10000 and thousands of random cases up to 10^11) reveals zero correctness bugs in the discrete log or target construction.
- **Root cause diagnosis**: The most likely explanation is that with K=71, the produced N values are extremely large (~10^49, up to 50 digits). If the SWEA special judge's verification code uses fixed-width integers (e.g., 64-bit or 128-bit) to read or process N, it would overflow and compute the wrong `2^N mod 10^100`, causing false WA. Alternatively, the judge might have a string-length limit on the answer. Another possibility is that the large N values cause the judge's modular exponentiation to time out or lose precision in the checker's language.
- **What the previous plan missed**: Using K=71 produces N values far larger than necessary. The problem only requires N < 10^50, but there is no reason to use a K that produces N values near 10^50 when a much smaller K suffices and gives N values that comfortably fit in standard integer types.

## Problem Analysis

Given a natural number X (1 <= X <= 10^11), find any N (1 <= N < 10^50) such that X appears as a **substring** of f(N), where f(N) is the last 100 digits of 2^N (or 2^N itself if it has fewer than 100 digits).

- Up to ~12190 test cases, combined time limit 30s (Python).
- Memory limit: 256MB.

## Key Observations

1. **Structure of the last digits of 2^N**: For N >= K, 2^N mod 10^K is always divisible by 2^K. Via CRT with 10^K = 2^K * 5^K, the non-trivial part is 2^N mod 5^K.

2. **Primitive root**: 2 is a primitive root modulo 5^k for all k >= 1. The order of 2 mod 5^k is 4 * 5^(k-1).

3. **Use K=20 instead of K=71** (KEY CHANGE):
   - Order of 2 mod 5^20 is 4 * 5^19 = 76,293,945,312,500 (~7.6 * 10^13).
   - Maximum N (after adjustment) is at most 2 * order - 1 ~ 1.53 * 10^14.
   - This fits in a standard 64-bit integer (~9.2 * 10^18 max).
   - N values have at most 15 digits instead of 50 digits.
   - The p-adic loop runs 19 iterations instead of 70 (2.7x fewer).
   - All intermediate big-integer values are ~14 digits instead of ~50 digits, dramatically reducing computation.

4. **Constructive approach**: With K=20 and offset=8, construct T_val = X * 10^8 + L (at most 20 digits) such that:
   - T_val is divisible by 2^20 = 1,048,576.
   - T_val is coprime to 5.
   - X appears as a substring of T_val (it's placed at digit position 8 from the right).
   - L is always valid: max L = 5 * 2^20 - 1 = 5,242,879 < 10^8.

5. **P-adic discrete log**: Same Hensel-style lifting, but only 19 steps instead of 70.

6. **I/O restrictions**: No `import sys`, no `import io`. Use `input()` / `print()`.

## Algorithm Choice

**Discrete logarithm via p-adic lifting** (Hensel-style) with **K=20** instead of K=71.

The algorithm itself is unchanged from Plans 1-2. The critical change is reducing K from 71 to 20, which:
- Makes all intermediate integers small (~14 digits instead of ~50 digits).
- Produces much smaller N values (~10^14 instead of ~10^49).
- Avoids potential checker overflow/precision/size-limit issues.
- Runs faster (fewer loop iterations, smaller numbers).

## Step-by-Step Approach

### Precomputation (done once)

1. Set K = 20, mod5 = 5^20, pow2K = 2^20 = 1048576, order = 4 * 5^19.
2. Set offset = 8, pow10_offset = 10^8.
3. Compute h = pow(2, 4, mod5) -- generator of the 5-Sylow subgroup.
4. Build h_powers[j] = h^(5^j) mod mod5 for j = 0..20 iteratively.
5. Build h_powers_inv[j] = modinv(h_powers[j], mod5) for j = 0..20, using iterative extended GCD.
6. Precompute pow5[j] = 5^j for j = 0..K+1.
7. For each level j (0..K-2), precompute inv_ej[j] from the p-adic structure.
8. Precompute g_inv = modinv(2, mod5) and g_inv_table[k] for k = 0..3.
9. Precompute h_inv_pow[j][c] = h_powers_inv[j]^c mod mod5 for j=0..K-1, c=0..4.
10. Precompute inv_pow2K_mod5 for the CRT step.

### Per Test Case

**Step A: Construct target T_val**

Given X (as integer):
- base = X * 10^8
- a = (-base) mod 2^20
- Compute t (in {0,1,2,3,4}, t != t_bad) so that T_val = base + a + 2^20 * t is not divisible by 5.
- L = a + 2^20 * t (guaranteed L < 10^8 since max L = 5,242,879).
- T_val = base + L.

**Step B: Discrete log (p-adic lifting, 19 iterations)**

Find N such that 2^N ≡ T_val (mod 5^20):
1. r = T_val mod 5^20.
2. Find n0 in {0,1,2,3} from r mod 5 (lookup table).
3. r1 = r * 2^{-n0} mod 5^20.
4. Find m_partial via p-adic lifting (19 steps).
5. N = n0 + 4 * m_partial.

**Step C: Adjust N**

If N < 20 or N < 1, add order (= 4 * 5^19).

**Step D: Output N**

### I/O

- No imports at all.
- Read input using `input()`.
- Collect all answers in a list.
- Output with a single `print('\n'.join(out))` at the end.

## Edge Cases

1. **X = 1**: T_val = 1 * 10^8 + L. '1' is in T_val at position 8. Valid.
2. **X = 10^11** (12 digits, maximum): T_val = 10^11 * 10^8 + L = 10^19 + L. T_val has 20 digits. Fits in K=20.
3. **X contains digit 5 or 0**: X is placed at position 8+, so the last digit of T_val is determined by L (which is coprime-to-5 enforced via CRT). No issue.
4. **Small X (X=2)**: T_val = 2 * 10^8 + L. 9-digit number. Zero-padded to 20 digits in f(N), but '2' is still there.
5. **N = 0 from discrete log**: Adding order makes N ~ 7.6 * 10^13 >> 20 and > 1.
6. **L overflow**: max L = 5,242,879 < 10^8. Always safe. No need for L overflow handling.

## Complexity Analysis

- **Time**: Precomputation O(K) = O(20) operations on ~14-digit numbers. Essentially instant. Per test case: O(K) = O(19) multiplications on ~14-digit integers. For 12000 cases: ~228K small-integer multiplications. Well under 1 second even on PyPy.
- **Space**: O(K) = O(20) precomputed tables. Negligible.

## Changes from Plan 2

1. **K reduced from 71 to 20**: Dramatically reduces N size (~10^14 vs ~10^49), avoids potential checker issues with very large N.
2. **offset reduced from 50 to 8**: Matching smaller K. X is placed at position 8 from the right.
3. **All intermediate values are ~14-digit integers** instead of ~50-digit integers, making computation faster and more robust on PyPy 3.7.
4. **Same I/O**: Still uses `input()` / `print()`, no imports.
5. **Algorithm logic unchanged**: Same CRT target construction, same p-adic discrete log, same adjustment step.
