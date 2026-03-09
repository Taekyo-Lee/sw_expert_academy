# Plan 1 — Problem 25660: Santa's Gifts (산타의 선물)

## Problem Analysis

We have N children and N gifts (N <= 50). Each child has a strict preference ordering (permutation) over all N gifts. An assignment P is a permutation where child i receives gift P_i.

For two assignments P and Q, Q "beats" P if more children prefer Q over P than prefer P over Q. We need to find an assignment P that is **unbeatable** — no other assignment Q satisfies Q > P. If such P exists, output the lexicographically smallest one; otherwise output -1.

This is the **popular matching** (or Condorcet winner) problem in a one-sided bipartite assignment setting.

## Key Observations

### 1. Popularity Check via Max-Weight Matching

For a given assignment P, define vote weights: `v[i][g] = +1` if child i prefers gift g over P_i, `-1` if prefers P_i over g, `0` if g = P_i. The matching P itself has total weight 0 under these weights. P is popular (unbeatable) if and only if the **maximum weight perfect matching** under these vote weights equals 0. If any matching achieves positive weight, it beats P.

### 2. Dual Characterization (Label Structure)

By LP duality of the assignment problem, P is popular iff there exist integer labels `u[i]` (for children) and `v[g]` (for gifts) from {-1, 0, 1} satisfying:
- `u[i] + v[P_i] = 0` for all i (complementary slackness on matched edges)
- `u[i] + v[g] >= vote(i,g)` for all i, g (dual feasibility)

This leads to a clean classification of gifts into labels {-1, 0, 1}. Analysis of feasible label combinations shows that **the label set must be either {0}, {0,1}, or {0,-1}** (mixing +1 and -1 labels is impossible because a child matched to a label-1 gift requires all other gifts to have label >= 0).

### 3. Two-Phase Matching Structure

Both {0,1} and {0,-1} label types yield the **same matching structure**:

- **Set S** = "priority" gifts (label 1 in {0,1} type, label 0 in {0,-1} type).
- **Phase 1**: Each gift in S is matched to a child whose **overall #1 choice** is that gift.
- **Phase 2**: Each remaining child is matched to their **top non-S gift** (the highest-ranked gift in their preference that is not in S).
- The Phase 2 mapping must be injective (no two remaining children share the same top non-S gift).

### 4. Cascade Algorithm for Finding S

S is determined iteratively:
1. Start with S = {} (or with forced initial elements). Each remaining child points to their top non-S gift.
2. If no two children point to the same gift, the Phase 2 matching is valid. Done.
3. If gift g is pointed to by multiple children (conflict), add g to S. Match g to a child whose overall #1 choice is g. If no such child exists, the configuration is infeasible.
4. Adding g to S removes it from the non-S pool, forcing conflicting children to recalculate their top non-S gift.
5. Repeat until stable or infeasible.

When multiple children have the same gift as #1 (step 3), **the choice of which child gets matched to g affects subsequent conflicts**, so backtracking may be needed.

## Algorithm Choice

**Greedy + Cascade with Backtracking**, running in O(N^2) outer iterations x O(N^2) cascade cost = O(N^4) to O(N^5), feasible for N <= 50 in PyPy.

## Step-by-Step Approach

### Preprocessing
1. Read N and the preference matrix A (1-indexed gifts).
2. Compute `rank[i][g]` = position of gift g in child i's preference list (0-indexed, lower is better).
3. Compute `first_choice[i]` = child i's #1 gift (= A[i][0]).

### Finding the Lexicographically Smallest Popular Matching

Use a **greedy outer loop** over children 0..N-1, trying the smallest gift first:

```
For child i = 0 to N-1:
    For gift g = 0 to N-1 (ascending):
        If g is already assigned, skip.

        # Determine constraints from assigning P_i = g
        k = rank[i][g]
        forced_S = {A[i][j] for j in 0..k-1}  # gifts ranked above g by child i

        # Run cascade on remaining children/gifts with forced_S additions
        If cascade finds a valid completion:
            Commit P_i = g, update state, break

    If no gift works for child i: output -1
```

### Cascade Algorithm (inner procedure)

```
function cascade(S, remaining_children, remaining_gifts):
    while True:
        # Each remaining child finds top non-S gift
        for each child c in remaining_children:
            top[c] = first gift in c's preference not in S and in remaining_gifts
            if no such gift exists: return INFEASIBLE

        # Detect conflicts
        conflicts = {g : children mapping to g if count > 1}

        if no conflicts:
            # Check S-coverage: each S-gift in remaining_gifts must be
            # matchable to a remaining child with it as #1
            if S-coverage is satisfiable (bipartite matching check):
                return FEASIBLE (construct matching)
            else:
                return INFEASIBLE

        # Resolve smallest conflict
        g = pick a conflicting gift
        candidates = remaining children with overall #1 choice = g

        if no candidates: return INFEASIBLE

        # Try each candidate (backtrack if needed)
        for c in candidates:
            Add g to S, match c to g, remove c and g from remaining
            result = cascade(S, remaining_children, remaining_gifts)
            if result is FEASIBLE: return result
            Undo changes (backtrack)

        return INFEASIBLE
```

### S-Coverage Check

After the cascade stabilizes (no more conflicts), verify that all S-gifts still in the remaining pool can be matched to remaining children whose #1 choice is that gift. This is a bipartite maximum matching check (Hall's condition / Hopcroft-Karp on the "S-gift to #1-choice child" subgraph).

### Verification Step

After constructing a candidate popular matching P, **verify** it is truly popular by computing the max-weight matching under vote weights `v[i][g] = sign(rank[i][P_i] - rank[i][g])`. If the max weight is 0, P is popular. This serves as a safety check.

The verification uses the **Hungarian algorithm** in O(N^3).

## Edge Cases

1. **N = 1**: Only one assignment (gift 1 to child 1). Always popular. Output: `1`.
2. **All children have the same preference**: If their #1 choice can only go to one child, others are forced to worse gifts. A popular matching often doesn't exist (as in sample 3). The cascade will detect infeasibility.
3. **All children have distinct #1 choices**: Everyone gets their #1 choice. This is trivially popular. Output the identity-like matching.
4. **No popular matching exists**: The cascade fails for all configurations. Output `-1`.

## Complexity Analysis

- **Time**: O(N^2) outer iterations (children x gifts) x O(N^2) cascade x O(N) backtracking depth = O(N^5) worst case. For N = 50: ~312M operations. With the O(N^3) Hungarian verification: additional O(N^3) per candidate. Total fits within 3 seconds on PyPy.
- **Space**: O(N^2) for the preference matrix and rank matrix. Fits within 256MB.

## Summary

The core idea is that popular matchings (unbeatable assignments) have a clean two-phase structure: "priority" gifts go to children as their top choice, and remaining children get their best available non-priority gift. The cascade algorithm discovers the priority set S, and a greedy search over children/gifts in order finds the lexicographically smallest solution. A final verification step using the Hungarian algorithm confirms correctness.
