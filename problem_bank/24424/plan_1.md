# Plan 1 -- Problem 24424: 올바른 경로

## Problem Analysis

We are given:
1. A **Context-Free Grammar (CFG) in Chomsky Normal Form (CNF)** with nonterminals A-Z. Rules are either `X -> YZ` (binary) or `X -> c` (terminal, where c is a lowercase letter). Starting from empty sets for each nonterminal, we repeatedly apply the rules to build up the sets.
2. A **directed graph** with n <= 26 vertices and m <= n^2 edges, where each edge is labeled with a single lowercase letter.
3. Two vertices x, y.

**Goal**: Find the shortest path from x to y (not necessarily simple -- cycles allowed) such that the concatenation of edge labels along the path forms a string in set **S** (the nonterminal S). Output the length modulo 10^9+7, or -1 if no such path exists.

This is the classic **CFL-reachability** problem (finding shortest context-free-language-constrained paths in a graph).

## Key Observations

1. The grammar is already in Chomsky Normal Form: rules are either `N -> AB` (two nonterminals) or `N -> c` (single terminal). This is exactly the form needed for CYK-style parsing.

2. The state space is `(Nonterminal, start_vertex, end_vertex)`. For each state, we want the minimum length of a string derivable from that nonterminal that also labels a valid path from start to end in the graph. There are at most 26 * 26 * 26 = **17,576 states**.

3. Since all terminal rules contribute exactly length 1, and binary rules combine two sub-derivations additively, the distances are positive integers. This means **Dijkstra's algorithm** applies directly on the state space.

4. When we finalize state (N, u, v) with distance d, we can trigger relaxations:
   - For rule `M -> N B`: combine with finalized (B, v, w) to relax (M, u, w).
   - For rule `M -> A N`: combine with finalized (A, w, u) to relax (M, w, v).
   This ensures correctness because smaller distances are finalized first, so by the time we combine two states, the smaller one is already finalized.

5. A nonterminal is **productive** (its set is non-empty) only if it can derive a terminal string. We should precompute this to prune unproductive nonterminals.

6. The empty string is never in any set (terminal rules produce single chars, binary rules concatenate two non-empty strings), so we always need paths of length >= 1.

7. The answer could be very large (hence the mod 10^9+7 requirement), but Python handles arbitrary-precision integers natively, so exact comparisons in Dijkstra are correct regardless of magnitude.

## Algorithm Choice

**Dijkstra's algorithm on CFL-reachability state space.**

- State: `(N, u, v)` where N is a nonterminal (0-25), u and v are graph vertices (1-n).
- Distance: minimum length of a string derivable from N that labels a path from u to v.
- Dijkstra processes states in order of increasing distance, ensuring optimality.

**Why this fits the constraints:**
- State space: 26 * 26 * 26 = 17,576 (very small).
- Per state extraction: check at most R=100 rules, iterate over n=26 vertices each = 2,600 operations.
- Total operations: ~17,576 * 2,600 = ~45 million (feasible for PyPy in 30s, even with 28 test cases).
- Heap operations: O(17,576 * log(17,576)) extractions.

## Step-by-Step Approach

### Step 0: Precomputation -- Productive Nonterminals
- Mark a nonterminal N as productive if there exists a terminal rule `N -> c`.
- Iteratively: if there's a rule `N -> AB` where both A and B are productive, mark N as productive.
- Repeat until no new nonterminals are marked.
- If S is not productive, immediately output -1.

### Step 1: Parse Input
- Read the number of rules R.
- Parse each rule into either:
  - Terminal rule: `(N, c)` where N is a nonterminal index (0-25), c is a lowercase letter.
  - Binary rule: `(N, A, B)` where N, A, B are nonterminal indices.
- Read n, m, x, y.
- Read m edges `(u, v, c)`.

### Step 2: Precompute Rule Lookups
- For each nonterminal N, store:
  - `left_of[N]`: list of rules `(M, B)` where M -> N B (N is the left child).
  - `right_of[N]`: list of rules `(M, A)` where M -> A N (N is the right child).
- This allows O(1) lookup of which rules to trigger when state (N, u, v) is finalized.

### Step 3: Initialize Distance Matrix and Heap
- `dist[N][u][v] = infinity` for all states (use a large sentinel or -1 to indicate unset).
- `finalized[N][u][v] = False` for all states.
- For each terminal rule `(N, c)` and each edge `(u, v, c_edge)` where `c == c_edge`:
  - If `dist[N][u][v] > 1`: set `dist[N][u][v] = 1`, push `(1, N, u, v)` onto the min-heap.

### Step 4: Dijkstra Main Loop
```
while heap is not empty:
    d, N, u, v = heappop(heap)
    if finalized[N][u][v]:
        continue
    finalized[N][u][v] = True

    # N is left child: rules M -> N B
    for (M, B) in left_of[N]:
        for w in 1..n:
            if finalized[B][v][w]:
                new_dist = d + dist[B][v][w]
                if new_dist < dist[M][u][w]:
                    dist[M][u][w] = new_dist
                    heappush(heap, (new_dist, M, u, w))

    # N is right child: rules M -> A N
    for (M, A) in right_of[N]:
        for w in 1..n:
            if finalized[A][w][u]:
                new_dist = dist[A][w][u] + d
                if new_dist < dist[M][w][v]:
                    dist[M][w][v] = new_dist
                    heappush(heap, (new_dist, M, w, v))
```

### Step 5: Extract Answer
- S_idx = ord('S') - ord('A') = 18.
- If `finalized[S_idx][x][y]` is True: output `dist[S_idx][x][y] % (10**9 + 7)`.
- Otherwise: output -1.

## Edge Cases

1. **S not productive**: No string can ever be derived from S. Output -1.
2. **No edges in graph** (m=0): No path of length >= 1 exists. Output -1.
3. **x == y**: Need a cycle from x back to x whose label is in S. Handled naturally by the algorithm.
4. **Self-loops in graph**: An edge (u, u, c) contributes dist[N][u][u] = 1 for terminal rule N -> c. Valid and handled.
5. **Multiple terminal rules for same nonterminal**: e.g., S -> s, S -> t. Both contribute initial states with distance 1.
6. **Unreachable vertex pairs**: Their dist stays at infinity, so they never propagate. Correct.
7. **Large minimum distances**: Python big integers handle exact comparisons. Final answer taken mod 10^9+7.
8. **Duplicate rules**: The problem doesn't say rules are unique. If the same rule appears multiple times, it has no effect (just redundant work). Handle by deduplication or simply processing them.

## Complexity Analysis

- **Time per test case**: O(S * R * n + H * log H) where S = 26 * n^2 states, R = 100 rules, n = 26 vertices, H = total heap insertions.
  - S * R * n = 17,576 * 100 * 26 ~ 45 million.
  - H <= S * R * n ~ 45 million (each relaxation pushes at most once).
  - Total: ~45 million * log(45 million) ~ 45M * 25 ~ 1.1 billion bit-level operations in worst case.
  - In practice, much less because most states are unreachable and the heap stays small.
  - **Feasible for PyPy within 30s for 28 test cases** (most test cases won't hit worst case).

- **Space**: O(26 * n^2) = O(17,576) for the distance matrix and finalized array. Plus heap. Well within 256MB.

## Verification with Samples

- **Sample 1**: S -> s | SS. Graph has 's' edges on path 1->2->3->4, but also 't' edges. Only 's' paths count for S. Shortest s-path from 1 to 4: 1->2->3->4, length 3. Answer: 3.
- **Sample 2**: S -> s | t | SS. Any lowercase letter sequence works. Shortest path 1->4: 1->3(t)->4(s), length 2. Answer: 2.
- **Sample 3**: S -> XA, X -> AB, A -> a|AA, B -> b|BB. S generates a+b+a+. On 5-node cycle (a-edges + one b-edge 5->1), minimum a+b+a+ path from 1 to 5 is aaaa-b-aaaa = length 9. Answer: 9.
- **Sample 4**: S -> BX. B needs 'b' edges but graph has none. B is unproductive on this graph (wait, B is productive as a nonterminal since B->b exists, but dist[B][u][v] = infinity for all u,v since no b-edges). So S never gets a finite distance. Answer: -1.

All samples verified.
