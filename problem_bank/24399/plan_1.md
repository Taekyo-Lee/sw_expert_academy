# Plan 1 — Problem 24399: Probability and Statistics

## Problem Summary

- N types of balls (1..N), type i has F_i in {1,2} copies, total 30 balls.
- Each type has an unknown weight W_i in (0, 1].
- Q = 30000 experiments, each drawing all 30 balls without replacement.
- Draw probability at each step: P(type i) = (c_i * W_i) / sum_j(c_j * W_j), where c_i = remaining copies of type i.
- Goal: estimate weights C_i such that for all pairs (i,j) with W_i <= W_j: |C_i/C_j - W_i/W_j| < 0.02.
- Output C_i in [1e-300, 1]. Only ratios matter.

## Model Analysis

This is a **Plackett-Luce ranking model** with multiplicities. Each experiment produces a
full ranking of 30 ball draws. The likelihood of observing draw sequence b_1, b_2, ..., b_30
in one experiment is:

```
P(sequence) = product_{t=1}^{30} [ c_{b_t}^{(t)} * W_{b_t} ] / [ sum_j c_j^{(t)} * W_j ]
```

where c_i^{(t)} is the count of type-i balls remaining before step t.

The log-likelihood over all Q experiments:

```
L(W) = sum_{q=1}^{Q} sum_{t=1}^{30} [ log(c_{b_t}^{(q,t)} * W_{b_t}) - log(sum_j c_j^{(q,t)} * W_j) ]
```

## Algorithm: MM (Minorization-Maximization) Fixed-Point Iteration

### Derivation

Setting dL/dW_i = 0 yields the first-order optimality condition:

```
Q * F_i / W_i = sum_{q,t} c_i^{(q,t)} / S^{(q,t)}
```

where S^{(q,t)} = sum_j c_j^{(q,t)} * W_j is the weighted sum at step t of experiment q.

Rearranging gives the **Hunter (2004) MM update**:

```
W_i^{new} = Q * F_i / [ sum_{q,t} c_i^{(q,t)} / S^{(q,t)} ]
```

This update monotonically increases the log-likelihood and converges to the MLE.

### Why MM over gradient descent

- No learning rate to tune (parameter-free).
- Monotone convergence guaranteed.
- Typically converges in 15-30 iterations for well-conditioned problems.
- Same per-iteration cost as gradient descent but more stable.

## Implementation Plan

### Step 1: Input Parsing

```
Read T test cases.
For each test case:
    Read Q, N
    Read F_1, ..., F_N
    Read Q lines, each with 30 integers (the draw sequence)
    Store sequences as a list of Q lists of 30 ints (0-indexed ball types).
```

Use `input().split()` and convert to int. Store draw sequences as a flat list or list-of-lists
for cache friendliness.

### Step 2: MM Iteration

```python
W = [1.0] * N          # initial weights (uniform)

for iteration in range(NUM_ITERS):  # NUM_ITERS = 30
    denom = [0.0] * N  # accumulator: sum_{q,t} c_i^{(q,t)} / S^{(q,t)}

    for q in range(Q):  # for each experiment
        c = list(F)     # reset counts to initial

        for t in range(30):  # for each draw step
            # Compute S = sum(c_j * W_j)
            S = 0.0
            for j in range(N):
                S += c[j] * W[j]

            # Accumulate denom[i] += c[i] / S for all i with c[i] > 0
            inv_S = 1.0 / S
            for j in range(N):
                if c[j] > 0:
                    denom[j] += c[j] * inv_S

            # Remove drawn ball from counts
            drawn = sequences[q][t]  # 0-indexed type
            c[drawn] -= 1

    # MM update: W_i = Q * F_i / denom_i
    for i in range(N):
        W[i] = Q * F[i] / denom[i]

    # Normalize: divide all W by max(W) to keep in (0, 1]
    max_w = max(W)
    for i in range(N):
        W[i] /= max_w
```

### Step 3: Output

```python
# Output C_i = W_i (already normalized to (0, 1])
print(' '.join(f'{W[i]:.15g}' for i in range(N)))
```

## Performance Analysis

### Per-iteration cost

- Q * 30 = 900,000 step evaluations per iteration.
- At each step: compute S (N mults + adds), accumulate denoms (N conditional adds).
- Total per iteration: ~900,000 * 2 * N = ~54M operations (for N=30).

### Total cost

- 30 iterations * 54M ops = ~1.6 billion operations.
- PyPy 3.7 executes tight float loops at ~100-200M ops/sec.
- Estimated time: **8-16 seconds** per test case. Within the 30s limit.

### Memory

- Storing 30000 sequences of 30 ints: 900,000 ints = ~7.2 MB. Well within 256 MB.

## Optimizations for Speed

1. **Pre-convert sequences to 0-indexed int lists** during parsing.
2. **Use local variables** in the inner loop (Python/PyPy accesses local vars faster than global).
3. **Inline the inner loop** as much as possible; avoid function call overhead.
4. **Skip types with c[j] == 0** in the S computation and denom accumulation.
5. **Wrap the main logic in a function** (PyPy optimizes function-level code much better than module-level).
6. **Use `1.0 / S` once** instead of dividing by S multiple times.
7. **Consider reducing iterations**: monitor convergence; 20 iterations may suffice given
   30000 experiments provide very strong signal for only 30 parameters.
8. **Pre-store sequences as a flat list** (single list of Q*30 ints) for better cache locality,
   accessing via `seq[q*30 + t]`.

## Convergence Justification

With Q = 30000 experiments and only N <= 30 parameters, the Fisher information per
parameter is enormous. The statistical error in the MLE is O(1/sqrt(Q*30)) which is
~O(0.001), far below the 0.02 tolerance. The MM algorithm converges geometrically;
30 iterations should bring the iterates well within the convergence basin.

## Edge Cases

- **N = 1**: Only one ball type. Output 1.0. (Though sum(F_i)=30 must hold, so F_1=30 is impossible since F_i<=2. Actually N >= 15 since each F_i <= 2 and sum=30. Wait, N can be up to 30 with all F_i=1. N >= 15 with all F_i=2. The constraint says 1 <= N <= 30.)
- **All weights equal**: W_i = 1 for all i. Algorithm should converge to uniform weights.
- **Very small weights**: Some W_i could be very small. The MM update handles this naturally since denom_i will be large (type i is rarely drawn early), making W_i small.
- **F_i = 2 (duplicate balls)**: The count c_i starts at 2 and decreases to 0 as both copies are drawn. The MM formula accounts for this via the c_i factor.

## Output Format

- Print N space-separated floats.
- Use sufficient precision (15+ significant digits) via `:.15g` format.
- Normalize so max weight = 1.0 (ensures all values in (0, 1]).

## Complexity Summary

| Aspect | Value |
|--------|-------|
| Time per test case | ~10-15 seconds (PyPy) |
| Memory | ~10 MB |
| Iterations | 30 |
| Algorithm | MM fixed-point (Hunter 2004) |
| Convergence | Monotone, geometric rate |
