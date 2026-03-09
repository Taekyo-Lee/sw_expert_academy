# Plan 1: Problem 25841 - Sister City (자매 결연)

## Problem Analysis

We have a connected graph of N cities and M bidirectional roads with fuel costs. For Q queries, each query gives two cities X and Y that want to exchange delegations simultaneously (car A goes X->Y, car B goes Y->X). The two cars must never occupy the same city at the same time and must never traverse the same road in opposite directions at the same time. Cars can wait, revisit cities/roads, but cannot U-turn mid-road. Each city has a gas station, so the fuel tank capacity a car needs is the maximum fuel cost of any single road it uses. Minimize the maximum fuel tank capacity across both cars. If impossible, output -1.

## Key Observations

1. **Feasibility condition:** The swap is possible if and only if the connected component containing X and Y (using only edges up to some weight W) is NOT a simple path (i.e., it has a cycle or a branching vertex of degree >= 3). On a simple path, there is no "parking spot" for one car to step aside while the other passes, making the swap impossible.

2. **Answer characterization:** The answer is the minimum weight W such that in the subgraph G_W (edges with weight <= W), X and Y are connected AND their component is not a simple path.

3. **Kruskal Reconstruction Tree:** Process edges in sorted weight order (like Kruskal's). Each tree-edge merge creates an internal node in a reconstruction tree. The LCA of X and Y in this tree gives the weight at which they first become connected.

4. **Non-path events:** A component transitions from "simple path" to "not a simple path" when:
   - A non-tree edge is added within the component (creating a cycle), OR
   - Two path components merge at non-endpoint vertices (creating a degree-3 vertex / branch).

5. **Subtree minimum propagation:** For each Kruskal tree node N, compute `subtree_min_np(N)` = the minimum weight of any non-path event in N's subtree. This is computed bottom-up during tree construction.

6. **Answer propagation:** For each node N, the "answer weight" is:
   ```
   ans_weight(N) = min(max(w(N), subtree_min_np(N)), ans_weight(parent(N)))
   ```
   This captures: the earliest time the growing component containing N's vertices becomes non-path. Computed top-down from root to leaves.

7. **Query answering:** For query (X, Y), find LCA in the Kruskal tree, return `ans_weight(LCA)`. If infinity, return -1.

## Algorithm Choice

**Kruskal Reconstruction Tree + Binary Lifting LCA**

This approach processes all edges once and answers each query in O(log N) using LCA with binary lifting. Total complexity: O(M log M + N log N + Q log N), which is optimal for the given constraints.

## Step-by-Step Approach

### Step 1: Read input and sort edges
- Read N, M, edges, Q, queries.
- Sort all M edges by weight.

### Step 2: Build Kruskal Reconstruction Tree
- Initialize union-find with path tracking (for each component: is_path, endpoints).
- Process edges in sorted order:
  - **Same component (non-tree edge):** Record weight as a non-path event (cycle) on the Kruskal tree node of this component. Update `subtree_min_np`. Mark component as non-path.
  - **Different components (tree edge):** Create an internal Kruskal tree node.
    - If both children are paths and the merge connects at endpoints of both: merged is still a path. Track new endpoints.
    - Otherwise: this merge is a non-path event (branch). Record weight in `subtree_min_np`.
    - Propagate `subtree_min_np` from children: `subtree_min_np[node] = min(self_event, subtree_min_np[left], subtree_min_np[right])`.

### Step 3: Compute answer weights (top-down)
- Process Kruskal tree nodes from root to leaves (reverse creation order):
  - For internal node N:
    ```
    self_ans = max(w(N), subtree_min_np(N))  if subtree_min_np(N) < inf, else inf
    ans_weight(N) = min(self_ans, ans_weight(parent(N)))
    ```
  - For leaf node: `ans_weight(leaf) = ans_weight(parent)`.

### Step 4: Build LCA structure
- BFS/DFS from root to compute depths.
- Build binary lifting table: `up[k][v] = 2^k-th ancestor of v`.

### Step 5: Answer queries
- For each query (X, Y):
  - Find LCA L of X and Y in the Kruskal tree.
  - Answer = `ans_weight(L)`. If infinity, output -1.

### Step 6: Output
- Print all answers for the test case, space-separated.

## Edge Cases

1. **Graph is a simple path (tree with all degrees <= 2):** All queries return -1.
2. **X and Y are adjacent with a parallel edge:** The two edges form a cycle; answer is the max weight of the two edges.
3. **X and Y are in the same biconnected component:** Answer is related to the max edge weight in the component's cycle structure.
4. **Bridge separating X and Y, but parking available nearby:** The bridge weight contributes to the answer, but it's not -1 because the non-path structure elsewhere allows parking.
5. **All edges have the same weight:** Answer is that weight (if the component is not a simple path) or -1.
6. **N = 2, M = 1:** Only one edge, always -1 (simple path of 2 vertices).

## Complexity Analysis

- **Time:** O(M log M + N log N + Q log N) per test case.
  - Sorting: O(M log M).
  - Kruskal tree construction: O(M * alpha(N)).
  - ans_weight computation: O(N).
  - LCA preprocessing: O(N log N).
  - Q queries: O(Q log N).
- **Space:** O(N + M) for the graph, O(N log N) for binary lifting.
- With N = 100,000, M = Q = 200,000: approximately 4M log N ~ 70M operations total. Easily fits in 18 seconds for PyPy.
