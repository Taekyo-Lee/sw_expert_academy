# Plan -- Problem 25478 (Trial 2)

## Changes from Trial 1
- **Root cause of MLE**: The DP state `(window_tuple, placed_bitmask)` uses a bitmask over all N receivers in each connected component. For components with n > ~20 receivers, `2^n` explodes (e.g., 2^50 for n=50). This makes the state space astronomically large, causing MLE on all 140 test cases even though the window tuple itself is small.
- **Key change**: Eliminate the `placed_bitmask` entirely. Instead, exploit the theory of **proper interval graphs**: find a canonical ordering of receivers such that the exit check (all friends placed before a receiver leaves the window) is **automatically satisfied by the ordering structure**. Replace the window+bitmask DP with a lightweight **gap DP** over the canonical ordering, where the state is just the capped cumulative distances (2^D possible vectors) plus the total span. This makes memory O(2^D * N * D) which is tiny.

## Key Challenge

Counting injective placements of N receivers on X positions such that the communication matrix (distance <= D iff A[i][j]=1) is exactly satisfied. The main difficulty is efficiently enforcing *both* directions:
1. A[i][j]=1 implies distance <= D (friends must be close).
2. A[i][j]=0 implies distance > D (non-friends must be far).

Trial 1 enforced (2) via the window check and (1) via an exit check requiring a placed-set bitmask. The new approach enforces both automatically through the proper interval ordering.

## Approach

### Core idea

A graph G is realizable as a D-unit interval graph (vertices are points on a line, edges = distance <= D) if and only if G is a **proper interval graph** with bandwidth <= D. For such graphs, there exists an essentially unique **canonical ordering** sigma where:
- Neighbors of each vertex form a consecutive block in the ordering.
- Consecutive vertices in the ordering are always adjacent.
- Any two vertices more than D apart in the ordering are non-adjacent.

Given this ordering, the placement problem reduces to choosing **gaps** between consecutive receivers. The gap DP state is just the vector of cumulative distances to the last D receivers, capped at D+1. Since these form a strictly-increasing-then-capped sequence, there are exactly 2^D = 256 possible vectors for D=8.

The overall algorithm:
1. Decompose A into connected components.
2. For each component, find the canonical ordering, verify it, and run the gap DP.
3. Combine components via convolution and stars-and-bars placement.

### Data structures

- **Ordering**: a list of receiver indices in proper interval order.
- **Gap DP table**: `dict` mapping `(capped_distance_vector, span)` to count (mod 10^9+7). At most `2^D * n*D` entries per step.
- **Span counts**: `dict` mapping span to arrangement count for each component.
- **Convolution**: dictionary-based polynomial multiplication for combining components.

### Time complexity

Per component of size n:
- Ordering + verification: O(n^2).
- Gap DP: O(n * 2^D * n*D * D) = O(n^2 * D^2 * 2^D). For n=50, D=8: ~5M ops.
- Twin class computation: O(n^2).
- Two orderings (forward + reverse): factor 2.

Per test case: O(N^2 * D^2 * 2^D + K * (N*D)^2) for convolution.

Total: extremely fast for N=50, D=8.

### Space complexity

Gap DP table: O(2^D * n * D) entries. For D=8, n=50: ~100K entries.
Span counts: O(n * D) entries per component.
Convolution: O(N * D) entries.

Total: well under 1MB per test case. **Memory is not an issue.**

### Why this will pass

- The 2^50 bitmask is completely eliminated.
- State space is O(2^D) = O(256), independent of N.
- Gap DP is O(n^2 * D^2 * 2^D) per component, which is ~5M for worst case.
- Total across 140 test cases: under 1 billion operations.
- Memory: under 10MB total.

### Memory estimate

- Gap DP dict: ~100K entries * ~100 bytes = ~10MB peak.
- Span counts + convolution: ~50K entries * ~50 bytes = ~2.5MB.
- Total peak: ~15MB. Well within 256MB.

## Detailed Steps

### 1. Input parsing

Read T test cases. For each: N, X, D, then the N x N matrix A.

### 2. Connected components

Use DFS/BFS on graph A (edges where A[i][j]=1, i != j) to find connected components C_1, ..., C_K.

### 3. Process each component

For each component C with n receivers (local indices 0..n-1 mapped from global):

#### 3a. Special case: n = 1
span_counts = {0: 1}. Skip to next component.

#### 3b. Find proper interval ordering

Use BFS-based ordering:
1. Start from a vertex u with minimum degree in the component.
2. BFS from u with tie-breaking: among unvisited neighbors of the frontier, prefer the vertex with the most already-visited neighbors (ties broken by original index).
3. Result: ordering sigma[0], sigma[1], ..., sigma[n-1].

#### 3c. Verify proper interval ordering

For each vertex v at position p in the ordering:
- Let L = set of v's neighbor positions less than p, and R = set of v's neighbor positions greater than p.
- Check that L = {p - |L|, ..., p-1} (consecutive from left).
- Check that R = {p+1, ..., p + |R|} (consecutive from right).

If verification fails: the graph is NOT a proper interval graph. Set component count = 0.

#### 3d. Check bandwidth <= D

For each pair (i, j) with A[sigma[i]][sigma[j]] = 1 (friends): check |i - j| <= D.
If any violation: the graph is not a D-unit interval graph. Set component count = 0.

#### 3e. Gap DP for a given ordering

**Input**: ordering sigma, adjacency matrix A, parameter D.
**Output**: span_counts dict: span -> number of valid gap sequences.

**State**: `(cdv, span)` where:
- `cdv` = capped distance vector = tuple of D values representing cumulative distances from the latest receiver to each of the D previous receivers, capped at D+1. Values form a (non-strictly-)increasing sequence ending with D+1s.
- `span` = total span so far (sum of all gaps).

**Initialization** (after placing sigma[0]):
- cdv = (D+1, D+1, ..., D+1) [D entries, all far away since no previous receivers].
- span = 0.
- DP[(cdv, 0)] = 1.

Actually, better initialization: before placing any receiver, the DP is empty. After placing sigma[0], there are no previous receivers, so the capped distance vector is all D+1 (no relevant history). State: (all_far, 0) with count 1.

**Transition** (step k, placing sigma[k+1] with gap g from sigma[k]):

For each state (cdv, s) in current DP, for each gap g in [1, D]:
1. Compute new cdv: new_cdv = (g, min(cdv[0]+g, D+1), min(cdv[1]+g, D+1), ..., min(cdv[D-2]+g, D+1)).
2. Check constraints: for each i in [0, D-1] (distance to sigma[k+1-1-i] = sigma[k-i]):
   - If k-i < 0: skip (no such receiver).
   - Distance = new_cdv[i].
   - If new_cdv[i] <= D: require A[sigma[k+1]][sigma[k-i]] == 1.
   - If new_cdv[i] > D (== D+1): require A[sigma[k+1]][sigma[k-i]] == 0.
3. If all checks pass: add count to new state (new_cdv, s + g).

**Termination**: after step n-2 (placing sigma[n-1]), collect all states. For each (cdv, s), add count to span_counts[s].

#### 3f. Count arrangements for both orderings

- Run gap DP for sigma -> forward_span_counts.
- Run gap DP for reverse(sigma) -> reverse_span_counts.

#### 3g. Compute twin classes

Twin class: group of receivers with identical rows in the component's local adjacency matrix. For each receiver r, compute a hashable key = tuple of its neighbors (sorted). Group by key.

Let twin_factor = product of (|class_i|!) for all twin classes.

#### 3h. Check palindromic symmetry

Check if reverse(sigma) can be obtained from sigma by permuting within twin classes:
- For each position p: sigma[p] and sigma[n-1-p] must be in the same twin class.

If palindromic:
- component_span_counts = {s: forward_span_counts[s] * twin_factor % MOD} for each s.

If NOT palindromic:
- component_span_counts = {s: (forward_span_counts.get(s, 0) + reverse_span_counts.get(s, 0)) * twin_factor % MOD} for each s.

### 4. Handle impossible components

If any component has empty span_counts, the overall answer is 0.

### 5. Convolve component span counts

Start with h = comp_spans[0]. For each subsequent component i:
- new_h[s1 + s2] += h[s1] * comp_spans[i][s2] for all s1, s2.
- h = new_h.

### 6. Count placements on the line

For K components with total span S, the components are placed left-to-right with mandatory gaps > D between consecutive component blocks.

For each combined span S in h:
- T = X - 1 - S - (K-1) * (D+1)
- If T < 0: skip.
- placements = C(T + K, K) (stars and bars: T extra slack distributed among K+1 gaps).

Multiply by K! for the K! orderings of components on the line.

answer = K! * sum_S (h[S] * C(T+K, K)) mod (10^9 + 7).

### 7. Output

Print `#{tc} {answer}`.

## Pseudocode

```python
def solve_component(comp, A_local, D):
    n = len(comp)
    if n == 1: return {0: 1}

    sigma = find_proper_interval_ordering(comp, A_local)
    if not verify_ordering(sigma, A_local): return {}
    if not check_bandwidth(sigma, A_local, D): return {}

    forward = gap_dp(sigma, A_local, D)
    reverse = gap_dp(sigma[::-1], A_local, D)

    twin_factor = compute_twin_factor(A_local)
    palindromic = check_palindromic(sigma, A_local)

    result = {}
    if palindromic:
        for s, c in forward.items():
            result[s] = c * twin_factor % MOD
    else:
        all_spans = set(forward) | set(reverse)
        for s in all_spans:
            result[s] = (forward.get(s,0) + reverse.get(s,0)) * twin_factor % MOD
    return result

def gap_dp(sigma, A_local, D):
    n = len(sigma)
    FAR = D + 1
    init_cdv = tuple([FAR] * D)
    dp = {(init_cdv, 0): 1}

    for k in range(n - 1):  # placing sigma[k+1]
        new_dp = {}
        for (cdv, span), count in dp.items():
            for g in range(1, D + 1):
                new_cdv = [g]
                for i in range(D - 1):
                    new_cdv.append(min(cdv[i] + g, FAR))
                new_cdv = tuple(new_cdv)

                valid = True
                for i in range(D):
                    prev_idx = k - i  # sigma[prev_idx]
                    if prev_idx < 0: break
                    dist = new_cdv[i]
                    if dist <= D:
                        if A_local[sigma[k+1]][sigma[prev_idx]] != 1:
                            valid = False; break
                    else:
                        if A_local[sigma[k+1]][sigma[prev_idx]] != 0:
                            valid = False; break

                if valid:
                    key = (new_cdv, span + g)
                    new_dp[key] = (new_dp.get(key, 0) + count) % MOD
        dp = new_dp

    span_counts = {}
    for (cdv, span), count in dp.items():
        span_counts[span] = (span_counts.get(span, 0) + count) % MOD
    return span_counts
```

## Edge Cases

- **N = 1**: Any of X positions. Answer = X.
- **All receivers friends (complete graph)**: Must fit in D+1 positions. If N > D+1, answer = 0. Otherwise, use gap DP with all gaps = 1.
- **All receivers isolated (A = identity)**: Each is its own component. Stars-and-bars placement with mandatory gap > D. Answer = N! * C(X - (N-1)*(D+1), N) if non-negative, else 0.
- **Component not a proper interval graph**: Some component has an induced C4 or asteroidal triple. Answer = 0.
- **Component is proper interval but bandwidth > D**: Friends are too far apart in any ordering. Answer = 0.
- **Palindromic component**: e.g., K_n with n <= D+1. Forward = reverse up to twin permutation. Don't double-count via palindromic check.
- **Large component (n=50) with valid structure**: e.g., a long path. The gap DP handles this in O(n * 2^D) states, well within limits.
- **D = 1**: Minimal range. Components are cliques of size <= 2 (edges or isolated vertices).
- **Multiple identical twin classes**: product of factorials accounts for all permutations.
- **Empty gap DP result**: No valid gap sequence exists for the component. Answer = 0.
