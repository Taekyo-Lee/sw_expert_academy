# Plan 2: Non-Attacking Bishops on N x N Board (O(N log N))

## Reflection Summary

**Verdict:** TLE (Time Limit Exceeded)

**What failed:** The O(N^2) DP in `build_rook_poly` is the bottleneck. For N = 100,000, this is ~10^10 operations, far too slow for PyPy's 30-second limit.

**Root cause:** The plan acknowledged O(N^2) as "tight" but it is actually infeasible. Python/PyPy handles ~10^7-10^8 arithmetic operations per second in tight loops, making 10^10 operations impossible within 30 seconds.

**What the previous plan missed:** An efficient mathematical reformulation exists that avoids the O(N^2) DP entirely, using the Ferrers board factorization theorem.

## Problem Analysis

Same as Plan 1: Given an N x N chessboard, for each k from 1 to 2N-1, count the number of ways to place k non-attacking bishops, modulo 998244353.

## Key Observations (New)

1. **Ferrers board structure:** After permuting rows (sorted by decreasing diagonal size) and columns (reindexed to make intervals left-justified), each parity's bipartite board becomes a proper Ferrers board.

2. **Ferrers board factorization theorem:** For a Ferrers board with column heights b_1 <= b_2 <= ... <= b_n (sorted non-decreasingly), the rook numbers satisfy:

   sum_{k=0}^{n} r_k * [x]_{n-k} = product_{i=1}^{n} (x + b_i - i + 1)

   where [x]_m = x(x-1)...(x-m+1) is the falling factorial.

3. **Product simplifies dramatically:** Due to the arithmetic structure of diagonal sizes, the linear factors c_i = b_i - i + 1 take only two distinct values. Specifically:

   | Parity | N parity | n_col | P(x) = product(x + c_i) |
   |--------|----------|-------|--------------------------|
   | Even   | Even     | N-1   | (x+2)^{N/2} * (x+1)^{N/2-1} |
   | Even   | Odd      | N     | (x+1)^{(N+1)/2} * x^{(N-1)/2} |
   | Odd    | Even     | N     | (x+1)^{N/2} * x^{N/2} |
   | Odd    | Odd      | N-1   | (x+2)^{(N-1)/2} * (x+1)^{(N-1)/2} |

4. **Extracting rook numbers via finite differences:** From the factorization theorem:

   r_j = Delta^{n-j} P(0) / (n-j)!

   where Delta^k P(0) = sum_{i=0}^{k} (-1)^{k-i} C(k,i) P(i).

   This can be computed as a **convolution**:

   c_k = sum_{i=0}^{k} f_i * g_{k-i}

   where f_i = P(i) / i! and g_i = (-1)^i / i! (all mod p), and r_j = c_{n-j}.

   The convolution is computable in O(n log n) using NTT.

## Algorithm Choice

**O(N log N) per test case** using the Ferrers board factorization + NTT convolution.

## Step-by-Step Approach

1. **Precompute** factorials and inverse factorials up to 100,001 (max N + 1).

2. **For each test case with N:**

   a. **Handle N = 1** specially: output "1".

   b. **For each parity (even, odd), determine the Ferrers board parameters:**
      - Identify (a, p, b, q, n) such that P(x) = (x+a)^p * (x+b)^q with n = n_col.

   c. **Compute P(i) for i = 0, 1, ..., n:**
      - P(i) = pow(i+a, p, MOD) * pow(i+b, q, MOD) % MOD.
      - O(n log n) total.

   d. **Compute the convolution to extract rook numbers:**
      - f_i = P(i) * inv_fact[i] % MOD.
      - g_i = (-1)^i * inv_fact[i] % MOD.
      - Convolve f and g using NTT: O(n log n).
      - r_j = conv[n - j] for j = 0, ..., n.

   e. **Convolve even and odd rook polynomials** using NTT: O(N log N).

   f. **Output** result[1], result[2], ..., result[2N-1], space-separated, no trailing space.

## Edge Cases

- **N = 1:** Output "1".
- **N = 2:** Even poly [1, 2], Odd poly [1, 2, 0]. Convolution gives [1, 4, 4, 0]. Output "4 4 0".
- **pow(0, 0, MOD):** Python returns 1, which is correct.
- **Large N:** O(N log N) handles N = 100,000 easily.
- **Multiple test cases:** Factorials precomputed once. NTT per test case is fast.

## Complexity Analysis

- **Time per test case:** O(N log N) for evaluating P, computing the convolution, and the final NTT-based polynomial multiplication.
- **Time for precomputation:** O(N_max) for factorials.
- **Space:** O(N) per test case.
- **Feasibility:** For N = 100,000 and 50 test cases, total work is ~50 * 10^5 * 17 ~ 10^8 operations. Well within PyPy's 30-second limit.

## Verification

For N = 6:
- Even parity: P(x) = (x+2)^3 (x+1)^2. n=5.
  - P values: [8, 108, 576, 2000, 5400, 12348].
  - After convolution: rook poly = [1, 18, 98, 184, 100, 8]. Matches Plan 1's DP result.
- Odd parity: P(x) = (x+1)^3 x^3. n=6.
  - After convolution: rook poly = [1, 18, 98, 184, 100, 8].
- Final convolution: result[1] = 18+18 = 36. Matches expected output.
- Full output: 36 520 3896 16428 39680 53744 38368 12944 1600 64 0. Matches expected output.
