# Plan 1: Problem 24702 - 2의 거듭제곱 (Powers of 2)

## Problem Analysis

Given a natural number X (1 <= X <= 10^11), find any N (1 <= N < 10^50) such that X appears as a **substring** of f(N), where f(N) is the last 100 digits of 2^N (or 2^N itself if it has fewer than 100 digits).

- Up to ~12190 test cases, combined time limit 30s (Python).
- Memory limit: 256MB.

## Key Observations

1. **Structure of the last digits of 2^N**: For N >= K, the value 2^N mod 10^K is always divisible by 2^K. The non-trivial part is 2^N mod 5^K, since 10^K = 2^K * 5^K and CRT applies.

2. **Primitive root**: 2 is a primitive root modulo 5^k for all k >= 1. The order of 2 mod 5^k is 4 * 5^(k-1). This means 2^N mod 5^K cycles through all values coprime to 5, so any 100-digit number that is divisible by 2^K and coprime to 5 is achievable as f(N).

3. **Bound on K**: We need N < 10^50. The order of 2 mod 5^K is 4 * 5^(K-1). For K = 71, the order is 4 * 5^70 ~ 3.4 * 10^49 < 10^50. So we work with **K = 71** (last 71 digits), which is a subset of the last 100 digits.

4. **Constructive approach**: We construct a specific 71-digit target number T that contains X as a substring, satisfies T ≡ 0 (mod 2^71), and gcd(T, 5) = 1. Then we find N via discrete logarithm modulo 5^71.

5. **P-adic discrete log**: Since 2 is a primitive root mod 5^71, we can compute the discrete log by iteratively lifting from mod 5 to mod 5^2 to ... to mod 5^71. Each lifting step determines one base-5 digit of the exponent, costing O(1) big-integer operations.

## Algorithm Choice

**Discrete logarithm via p-adic lifting** (Hensel-style).

- Precomputation: O(K) modular exponentiations to set up tables.
- Per test case: O(K) big-integer operations with numbers of ~50 digits.
- Total: O(T_cases * K) = O(12000 * 70) ~ 840,000 big-integer ops on ~50-digit numbers.
- This fits comfortably within 30s on PyPy.

## Step-by-Step Approach

### Precomputation (done once)

1. Set K = 71, mod5 = 5^71, order = 4 * 5^70.
2. Compute h = pow(2, 4, mod5) — generator of the 5-Sylow subgroup (order 5^70).
3. Build h_powers[j] = h^(5^j) mod mod5 for j = 0..70, iteratively:
   - h_powers[0] = h
   - h_powers[j+1] = h_powers[j]^5 mod mod5
4. Build h_powers_inv[j] = modular inverse of h_powers[j] mod mod5, for j = 0..70.
5. Precompute pow5[j] = 5^j for j = 0..72.
6. For each level j (0..69), precompute:
   - e_j = ((h_powers[j] mod 5^{j+2}) - 1) // 5^{j+1} mod 5
   - inv_e_j = modular inverse of e_j mod 5 (from lookup table {1:1, 2:3, 3:2, 4:4})
7. Precompute g_inv = modinv(2, mod5) and g_inv_table[k] = g_inv^k mod mod5 for k = 0..3.
8. Precompute pow2_K = 2^71, pow10_50 = 10^50.

### Per Test Case

**Step A: Construct target T**

Given X (as integer), let d = number of digits of X.

- Place X at digit position 50 (from the right) within a 71-digit number.
- T = X * 10^50 + L, where L is a 50-digit number satisfying:
  - T ≡ 0 (mod 2^71): L ≡ -(X * 10^50) (mod 2^71)
  - T's last digit is 2 (not divisible by 5): L ≡ 2 (mod 5)
- Compute:
  - a = (-(X * 10^50)) mod 2^71
  - t = (2 * (2 - a mod 5)) mod 5     (CRT to satisfy L mod 5 = 2)
  - L = a + 2^71 * t
  - T = X * 10^50 + L

**Step B: Compute discrete logarithm**

Find N such that 2^N ≡ T (mod 10^71), i.e., 2^N ≡ T (mod 5^71) with N >= 71.

1. Let r = T mod 5^71.
2. Find n0 in {0,1,2,3} such that 2^n0 ≡ r (mod 5). Use lookup table: {1:0, 2:1, 4:2, 3:3}.
3. Compute r1 = r * 2^{-n0} mod 5^71. Now r1 ≡ 1 (mod 5), so r1 is in the 5-Sylow subgroup.
4. Find m (0 <= m < 5^70) such that h^m ≡ r1 (mod 5^71), by p-adic lifting:
   - Initialize m_partial = 0, curr_inv = 1 (tracks h^{-m_partial} mod 5^71).
   - For j = 0, 1, ..., 69:
     - mod_level = 5^{j+2}
     - diff = (r1 * (curr_inv mod mod_level)) mod mod_level
     - d_j = ((diff - 1) // 5^{j+1}) mod 5
     - c_j = (d_j * inv_e_j) mod 5
     - m_partial += c_j * 5^j
     - If c_j > 0: curr_inv = curr_inv * h_powers_inv[j]^{c_j} mod 5^71
5. N = n0 + 4 * m_partial.

**Step C: Adjust N**

- If N < 71 or N < 1, add order (= 4 * 5^70) to N.
- N is guaranteed < 10^50 (since worst case N < 2 * order ~ 6.8 * 10^49 < 10^50).

**Step D: Output N**

### I/O

- Read T (number of test cases) and each X using `input()`.
- Collect all outputs in a list and print with `'\n'.join(...)` at the end for efficiency.

## Edge Cases

1. **X = 1**: Very common substring; algorithm finds some valid N.
2. **X = 10^11** (12 digits): Fits at position 50 within 71-digit T (50 + 12 = 62 <= 71).
3. **X contains digit 5**: X is placed in the middle of T (position 50), so the last digit of T is 2 (not 5). No issue.
4. **Small X (e.g., X = 2)**: Simple case; f(1) = "2" works, but our algorithm finds a (potentially larger) valid N.
5. **N = 0 from discrete log**: Adding the order once makes N ~ 3.4 * 10^49 > 71 and > 1.

## Complexity Analysis

- **Time**: Precomputation O(K) modular exponentiations ~ O(71 * log(5^71) * M(50_digits)). Per test case O(K) big-int ops. Total for 12000 test cases: ~840K big-int ops on ~50-digit numbers. Well within 30s on PyPy.
- **Space**: Precomputed tables of ~70 entries, each a ~50-digit integer. Negligible (a few KB).
