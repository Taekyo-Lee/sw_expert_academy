# Plan 1 — Problem 23009: Number of Consecutive Overlapping Intervals

## Problem Analysis

Given a permutation p of 1..N, count ordered 4-tuples (l1, r1, l2, r2) such that:

1. Both [l1,r1] and [l2,r2] are **consecutive intervals** (the subarray values form a set of consecutive integers, i.e., max - min = r - l).
2. They **cross** (overlap but neither contains the other): WLOG l1 < l2 <= r1 < r2.
3. Their intersection has size >= X: r1 - l2 + 1 >= X.

Result modulo 998244353.

**Constraints**: N <= 300,000, T <= 12 test cases, Python 30s total.

## Key Observations

### 1. Substitution Decomposition (Modular Decomposition) of a Permutation

The consecutive intervals of a permutation form a **partitive family**: if two consecutive intervals cross, their union and intersection are also consecutive intervals. This means they can be organized into a **substitution decomposition tree** with O(N) nodes.

- **Strong consecutive interval**: one that does not cross any other consecutive interval. These form a laminar family (tree).
- Each internal node is classified as **ascending** (children values increase left to right), **descending** (children values decrease), or **prime** (quotient permutation is simple — no non-trivial consecutive sub-intervals).
- **Critical property**: ALL crossing pairs of consecutive intervals come from **linear nodes** (ascending or descending). Prime nodes contribute zero crossing pairs.

### 2. Counting at a Linear Node

For a linear node with k children of sizes s1, s2, ..., sk:
- Every contiguous range of children [a, b] forms a consecutive interval of size S[b] - S[a-1] (prefix sums).
- Two such ranges [a, b] and [c, d] cross iff (WLOG) a < c <= b < d.
- Their intersection [c, b] has size S[b] - S[c-1].
- For ordered pairs, multiply unordered count by 2.

### 3. Efficient Counting per Linear Node

Fix j (the right endpoint of the left interval among the crossing pair). The "left interval" is [..., j] and "right interval" is [i', ...] where i' <= j and extends past j.

For each j from 2 to k-1:
- Need i' in [2, j] with intersection size S[j] - S[i'-1] >= X, i.e., S[i'-1] <= S[j] - X.
- Since S is strictly increasing, binary search for M = min(largest m with S[m] <= S[j] - X, j - 1).
- For each valid i', the number of "outer" endpoint choices: left endpoint i has (i' - 1) choices, right endpoint j' has (k - j) choices.
- Contribution for fixed j = (k - j) * sum_{t=1}^{M} t = (k - j) * M * (M + 1) / 2.

This is O(k log k) per linear node (binary search per j). Total: O(N log N).

## Algorithm Choice

### Part 1: Build the Substitution Decomposition Tree (Stack-Based, O(N) Amortized)

Sweep positions left to right, maintaining a stack of tree nodes.

For each position i with value p[i]:
1. Create a leaf node.
2. Try merging with stack top: if combined max - min = combined length - 1, pop and merge.
3. If top alone doesn't merge, scan deeper into the stack (include 2nd, 3rd, ... elements from top, tracking cumulative min, max, length). If at any point the cumulative gap = 0, pop all included elements and merge.
4. **Pruning**: stop scanning when gap > total remaining positions below the scan point (merge becomes impossible).
5. Push the resulting node.

**When merging multiple popped nodes + current into a new parent:**
- Determine type by checking if children's value ranges are ascending, descending, or neither (prime).
- **Flatten** any child that has the same type as the parent (e.g., if parent is descending and a child is also descending, absorb the child's children directly). This ensures the tree satisfies the decomposition invariant (no two adjacent nodes of the same linear type).

**Amortized O(N)**: each element is pushed and popped at most once. The scanning without merging is bounded by the pruning condition.

### Part 2: Count Crossing Pairs

For each linear node (ascending or descending) with k children of sizes s1, ..., sk:
- Compute prefix sums.
- For each j from 2 to k-1, binary search for M and add (k - j) * M * (M + 1) / 2 to the answer.
- Multiply the node's total by 2 (ordered pairs).

Sum over all linear nodes modulo 998244353.

## Step-by-Step Approach

### Step 1: Read Input
- Read T, then for each test case: N, X, and the permutation p[1..N].

### Step 2: Build Decomposition Tree
```
stack = []
for i in 0..N-1:
    node = Leaf(pos=i, val=p[i])
    while True:
        if stack is empty: break
        # Try merging current node with stack top(s)
        combined_min = node.min_val
        combined_max = node.max_val
        combined_len = node.size
        merged = False

        for depth from len(stack)-1 downto 0:
            combined_min = min(combined_min, stack[depth].min_val)
            combined_max = max(combined_max, stack[depth].max_val)
            combined_len += stack[depth].size
            gap = (combined_max - combined_min + 1) - combined_len

            if gap == 0:
                # Merge! Pop stack[depth..top] and combine with node
                popped = stack[depth:]
                stack = stack[:depth]
                node = create_parent(popped + [node])
                merged = True
                break

            # Pruning: remaining positions below depth
            if depth > 0:
                remaining = stack[depth].left - stack[0].left
            else:
                remaining = 0
            if gap > remaining:
                break

        if not merged:
            break
    stack.append(node)

# After processing all positions, stack should have one element (the root).
# If multiple remain, they can be combined (for the full permutation, the whole is always a consecutive interval, so this shouldn't happen).
```

### Step 3: Classify and Flatten Nodes
When creating a parent node from children [c1, c2, ..., cm] (left to right in position):
- Check if children values are ascending: c_i.max + 1 == c_{i+1}.min for all i.
- Check if descending: c_i.min - 1 == c_{i+1}.max for all i.
- Otherwise: prime.
- If ascending: flatten any child that is also ascending (replace with its children).
- If descending: flatten any child that is also descending.

### Step 4: Count Crossing Pairs
```
answer = 0
for each linear node with children sizes s[1..k]:
    S = prefix_sums(s)  # S[0]=0, S[j]=s[1]+...+s[j]
    for j in 2..k-1:
        target = S[j] - X
        if target < S[1]:  # Even the smallest i'-1 = 1 doesn't work
            continue
        # Binary search: largest m with S[m] <= target
        m = bisect_right(S, target, 1, j) - 1
        M = m  # already min(m, j-1) since we search up to j
        if M >= 1:
            answer += (k - j) * M * (M + 1) // 2
            answer %= MOD

answer = (answer * 2) % MOD  # ordered pairs
```

### Step 5: Output
Print the answer for each test case.

## Edge Cases

1. **N = 1**: No intervals of size >= 2. Answer = 0.
2. **X = 1**: Any crossing pair counts (intersection always >= 1 for crossing intervals).
3. **Identity permutation**: Every sub-interval is consecutive. Root is a single ascending linear node with N leaf children (all size 1). The formula reduces to counting crossing pairs of index ranges with intersection >= X.
4. **Reverse permutation**: Same as identity but descending.
5. **Random/prime permutation**: Few or no linear nodes. Answer likely 0 or small.
6. **X > N**: Answer = 0 (intersection can be at most N-1 for crossing intervals).
7. **Large linear nodes**: The O(k log k) counting per node handles this efficiently.

## Complexity Analysis

- **Time**: O(N log N) per test case. Tree construction is O(N) amortized (each element pushed/popped once, with pruning for scans). Counting is O(N log N) total (sum of k log k over all linear nodes, where sum of k = O(N)).
- **Space**: O(N) for the tree and stack.
- **Feasibility**: With N = 300,000 and 12 test cases, total work is about 12 * 300,000 * 18 ~ 6.5 * 10^7 operations. Well within PyPy's 30-second limit.
