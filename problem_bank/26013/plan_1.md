# Plan 1: Non-Attacking Bishops on N x N Board

## Problem Analysis

Given an N x N chessboard, for each k from 1 to 2N-1, count the number of ways to place k non-attacking bishops (no two share any diagonal), modulo 998244353.

**Key Output Format:** No `#N` prefix. Each test case outputs 2N-1 space-separated integers on one line. No trailing space.

## Key Observations

1. **Diagonal parity decomposition:** Bishops attack along "/" diagonals (r+c = const) and "\" diagonals (r-c = const). Since r+c and r-c have the same parity, cells where r+c is even form one independent group, and cells where r+c is odd form another. Bishops on different parity groups never attack each other.

2. **Reducing to non-attacking rooks:** For each parity group, placing k non-attacking bishops is equivalent to placing k non-attacking rooks on a bipartite graph where left vertices are the "/" diagonals of that parity and right vertices are the "\" diagonals of that parity.

3. **Nested interval structure:** For each parity, every "/" diagonal connects to a contiguous interval of "\" diagonals, and these intervals are nested (all centered at 0). This means the bipartite graph can be rearranged into a Ferrers board.

4. **Product formula for nested intervals:** For sorted diagonal sizes a_1 <= a_2 <= ... <= a_m, the number of ways to place k non-attacking bishops on one parity group is:

   r_k = sum over all k-subsets {i_1 < ... < i_k} of [m] of: product_{j=1}^{k} (a_{i_j} - (j-1))

   This follows from the fact that in a nested interval bipartite graph, when assigning bishops to "\" diagonals in order of "/" diagonal size, the j-th bishop has exactly (a_{i_j} - (j-1)) available "\" diagonals (because all j-1 previously chosen "\" diags are contained within the current interval).

5. **DP recurrence:** Processing diagonals one at a time (sorted by size), the rook polynomial satisfies:

   r_k^{new} = r_k^{old} + (a_i - k + 1) * r_{k-1}^{old}

   Or equivalently: P_i(z) = (1 + a_i * z) * P_{i-1}(z) - z^2 * P'_{i-1}(z)

6. **Grouping identical sizes:** Each diagonal size appears exactly twice (except possibly one middle size appearing once). Processing a pair (size s, multiplicity 2) in one pass:

   r_k^{new} = r_k + 2*(s-k+1)*r_{k-1} + (s-k+2)*(s-k+1)*r_{k-2}

## Diagonal Size Sequences

For even parity (r+c even), "/" diags have sums 0, 2, 4, ..., 2(N-1). Their sizes are:
- N even: [1, 1, 3, 3, 5, 5, ..., N-1, N-1] (N diags, N/2 distinct sizes, all multiplicity 2)
- N odd: [1, 1, 3, 3, ..., N-2, N-2, N] (N diags, (N-1)/2 pairs + 1 single)

For odd parity (r+c odd), "/" diags have sums 1, 3, 5, ..., 2N-3. Their sizes are:
- N even: [2, 2, 4, 4, ..., N-2, N-2, N] (N-1 diags, (N-2)/2 pairs + 1 single)
- N odd: [2, 2, 4, 4, ..., N-1, N-1] (N-1 diags, (N-1)/2 pairs)

## Algorithm Choice

**O(N^2) DP per parity with group processing, plus O(N^2) convolution.**

This is sufficient given the constraints (N <= 100,000, Python/PyPy 30s for 50 test cases combined).

## Step-by-Step Approach

1. **Read input:** Read T test cases, each with one integer N.

2. **Compute diagonal sizes for each parity:**
   - Even parity: for s = 0, 2, 4, ..., 2(N-1), compute size = min(s+1, N, 2N-1-s). Sort.
   - Odd parity: for s = 1, 3, 5, ..., 2N-3, compute size = min(s+1, N, 2N-1-s). Sort.

3. **Group consecutive identical sizes** into (size, multiplicity) pairs.

4. **Compute rook polynomial for each parity via DP:**
   - Initialize poly = [1] (representing R(z) = 1).
   - For each group (s, c):
     - If c == 2: extend poly by 2 slots, then for k from high to low:
       `poly[k] += 2*(s-k+1)*poly[k-1] + (s-k+2)*(s-k+1)*poly[k-2]`
     - If c == 1: extend poly by 1 slot, then for k from high to low:
       `poly[k] += (s-k+1)*poly[k-1]`
     - Take mod 998244353 at each step.

5. **Convolve the two rook polynomials:**
   - result[k] = sum_{j=0}^{k} even_poly[j] * odd_poly[k-j], for k = 0, 1, ..., 2N-1.
   - Take mod 998244353.

6. **Output result[1], result[2], ..., result[2N-1]** separated by spaces.

## Edge Cases

- **N = 1:** Even poly = [1, 1], Odd poly = [1]. Convolution: [1, 1]. Output: "1".
- **N = 2:** Even poly = [1, 2], Odd poly = [1, 2]. Convolution: [1, 4, 4]. Output: "4 4 0" (need result[1..3] = [4, 4, 0]).
  Wait: 2N-1 = 3, and result[3] = 0 since max bishops on 2x2 is 2.
- **k = 2N-1:** Always 0 for N >= 2 (can't place that many non-attacking bishops).
- **Large N:** The polynomial has degree up to N (even parity) and N-1 (odd parity). The convolution result has degree up to 2N-1, but result[2N-1] = 0 for N >= 2.
- **Negative factors in DP:** When (s - k + 1) < 0, the factor is negative. This is handled correctly by modular arithmetic (Python handles negative mod correctly).

## Complexity Analysis

- **Time per test case:** O(N^2/4) for each parity DP (due to grouping and incremental degree growth) + O(N^2) for convolution = O(N^2).
- **Space:** O(N) for the polynomials.
- **Feasibility:** For N = 100,000 in PyPy, O(N^2) ~ 10^10 operations. This is tight (~25-30s) but should be feasible with careful optimization in PyPy. The group-of-2 processing halves the constant factor for the DP.

## Verification

For N = 6:
- Even sizes sorted: [1, 1, 3, 3, 5, 5]. DP gives [1, 18, 98, 184, 100, 8].
- Odd sizes sorted: [2, 2, 4, 4, 6]. DP gives [1, 18, 98, 184, 100, 8].
- Convolution for k=1: 18*1 + 1*18 = 36. Matches expected output.
- Convolution for k=2: 98 + 18*18 + 98 = 520. Matches expected output.
