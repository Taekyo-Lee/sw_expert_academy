# Plan 1 for Problem 25333 - Synergy Effect

## Problem Analysis

We have N labeled items (nodes), each with a potential c_i. Items with c_i = -1 are "empty" (meaningless); items with c_i >= 0 are "meaningful." We must form a labeled tree on all N nodes. In the tree, a meaningful item is "usable" if it has at least one adjacent meaningful item (i.e., it is not isolated among meaningful items). The "effect" of a tree is the sum of potentials of all usable meaningful items. We must count trees with effect <= K, modulo 10^9 + 7.

**Restatement:** Let M = set of meaningful items, E = set of empty items, m = |M|, e = |E|. For a given tree, let S be the set of meaningful items that are "isolated" (all neighbors in the tree are empty). Then effect = totalM - sum(S), where totalM = sum of all meaningful potentials. We want trees where totalM - sum(S) <= K, equivalently sum(S) >= threshold where threshold = totalM - K.

## Key Observations

1. **Effect only depends on which meaningful items are isolated.** A meaningful item is isolated iff all its tree neighbors are in E.

2. **g(t) depends only on |U|, not which specific nodes.** Due to symmetry in the Laplacian structure, the number of trees where a specific set U of meaningful items are all isolated (all their neighbors in E) depends only on t = |U|.

3. **Closed-form for g(t)** using the matrix-tree theorem with equitable partitions:
   - If e = 0: g(0) = N^(N-2), g(t) = 0 for t >= 1.
   - If e >= 1 and t < m: g(t) = e^t * N^(e-1) * (N-t)^(m-t-1).
   - If e >= 1 and t = m >= 1: g(m) = e^(m-1) * N^(e-1).

4. **Inclusion-exclusion** converts "exactly isolated" counts into "at least isolated" counts using g(t).

5. **Meet-in-the-middle** computes the required subset-sum counts efficiently for m up to 40.

## Algorithm Choice

**Meet-in-the-middle + inclusion-exclusion + closed-form tree counting.**

The answer is: sum over t from 0 to m of g(t) * H(t), where:

H(t) = sum over r from 0 to t of (-1)^(t-r) * C(m-r, t-r) * N_r

and N_r = number of subsets of M of size r with sum >= threshold.

N_r is computed via meet-in-the-middle on the potentials of meaningful items.

**Complexity:** O(2^(m/2) * m) per test case, with m <= 40. This is about 10^6 * 40 = 4 * 10^7 operations, well within the 30-second Python/PyPy limit.

## Step-by-Step Approach

### Step 0: Special Cases
- If N = 1: answer is always 1 (single-node tree has effect 0, and K >= 1).
- If threshold <= 0: all N^(N-2) trees qualify. Output N^(N-2) mod p.

### Step 1: Separate Meaningful and Empty Items
- Partition items into M (c_i >= 0) and E (c_i = -1).
- Compute m = |M|, e = |E|, totalM = sum of potentials in M, threshold = totalM - K.

### Step 2: Compute g(t) for t = 0 to m
Using the closed-form formula (mod 10^9+7):
- e = 0: g(0) = pow(N, N-2, p), g(t) = 0 for t >= 1.
- e >= 1, t < m: g(t) = pow(e, t, p) * pow(N, e-1, p) * pow(N-t, m-t-1, p) mod p.
- e >= 1, t = m >= 1: g(m) = pow(e, m-1, p) * pow(N, e-1, p) mod p.

### Step 3: Compute N_r via Meet-in-the-Middle
- Split M's potentials into two halves A and B (sizes ~m/2 each).
- Enumerate all subsets of A: for each, record (size, sum). Group by size and sort sums.
- Enumerate all subsets of B: for each, record (size, sum). Group by size.
- For each target size r (0 to m):
  - For each split (r_A, r_B) with r_A + r_B = r:
    - For each subset of B with size r_B and sum s_B, count subsets of A with size r_A and sum >= threshold - s_B using binary search on sorted list.
  - Sum up to get N_r.

### Step 4: Compute H(t) for t = 0 to m
H(t) = sum_{r=0}^{t} (-1)^(t-r) * C(m-r, t-r) * N_r

Precompute binomial coefficients C(n, k) for n, k up to m. Compute H(t) mod p for each t.

### Step 5: Compute Final Answer
answer = sum_{t=0}^{m} g(t) * H(t) mod p

## Edge Cases

1. **N = 1:** Exactly 1 tree, effect = 0. Answer = 1.
2. **m = 0 (all items empty):** Effect is always 0. Answer = N^(N-2) mod p.
3. **e = 0 (no empty items):** For N >= 2, no meaningful item can be isolated (every edge connects two meaningful items). So effect = totalM for all trees. Answer = N^(N-2) if totalM <= K, else 0.
4. **threshold <= 0:** All trees qualify. Answer = N^(N-2) mod p.
5. **threshold > totalM:** No subset S can have sum >= threshold (since max sum is totalM). No trees qualify... wait, actually threshold = totalM - K, and we need sum(S) >= threshold. The max sum(S) is sum of all potentials in M = totalM. So if threshold > totalM, it's impossible, meaning 0 trees qualify. But threshold = totalM - K <= totalM since K >= 1. So threshold <= totalM always. Actually threshold could equal totalM, meaning we need sum(S) = totalM, which means S = M (all meaningful items isolated). This is a valid edge case.
6. **All potentials are 0:** threshold = -K < 0, so all trees qualify. Answer = N^(N-2).
7. **N = 2, m = 2, e = 0:** One tree, effect = c_1 + c_2. Answer = 1 if c_1 + c_2 <= K, else 0.

## Complexity Analysis

- **Time:** O(2^(m/2) * m) per test case for the meet-in-the-middle step. With m <= 40, this is ~4 * 10^7 operations. With 68 test cases and PyPy, total is ~2.7 * 10^9, which should fit in 30 seconds on PyPy (PyPy handles simple loops at ~10^8-10^9 ops/sec).
  - Actually, worst case is 68 test cases each with m = 40, giving 68 * 4*10^7 = 2.7*10^9. This might be tight. But the actual inner loop involves simple integer comparisons and binary search, which PyPy handles efficiently.
  - Optimization: use `bisect` module for binary search and precompute sorted arrays.
- **Space:** O(2^(m/2)) per test case for storing subset sums, ~10^6 integers. Negligible.
