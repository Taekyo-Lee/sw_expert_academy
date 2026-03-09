# Plan 2 — Problem 24399: Probability and Statistics

## Diagnosis of Trial 1 Failure (WA 0/20)

### Root Cause: Wrong Output Format

**The `#T` prefix must be removed.** The solution outputs `#1 0.123 0.456 ...` but the judge expects `0.123 0.456 ...` (no prefix).

Evidence:
- The problem statement's output section says: "각 테스트 케이스에 대해 N개의 실수 C_1, C_2, ..., C_N을 출력한다." No mention of `#T` format.
- The sample output is `0.1 1e-3 1 0.5` with no prefix.
- Problem 25660 in this repository had the **exact same bug**: 0/77 WA caused by `#T` prefix, fixed by removing it (see `problem_bank/25660/progress.md`).

The `#T` prefix causes the special judge to fail parsing every test case, which perfectly explains the 0/20 complete failure.

### Algorithm Correctness: Verified

The MM (Minorization-Maximization) fixed-point iteration and the cumsum optimization are both **mathematically correct**. Verified by:

1. **Analytical derivation**: The MM update `W_i = Q * F_i / sum_{q,t}(c_i^{q,t} / S^{q,t})` is correct for the Plackett-Luce model with multiplicities.

2. **Cumsum formula verification**:
   - For F=1 type drawn at step p: `denom[j] += cumsum[p+1]` (contributes `c_j=1` from step 0 to step p).
   - For F=2 type drawn at steps p1 < p2: `denom[j] += cumsum[p1+1] + cumsum[p2+1]`. This correctly computes `sum_{t=0}^{p1}(2/S_t) + sum_{t=p1+1}^{p2}(1/S_t) = 2*cumsum[p1+1] + (cumsum[p2+1] - cumsum[p1+1]) = cumsum[p1+1] + cumsum[p2+1]`.

3. **Numerical test**: Naive (O(Q*M*N) per iteration) and optimized (cumsum) implementations produce identical results on synthetic data with known ground truth.

4. **S update correctness**: `S -= W[a_t]` correctly subtracts `W[a_t]` regardless of the current count `c_{a_t}` (since going from count `c` to `c-1` reduces the weighted sum by exactly `W[a_t]`).

### Secondary Concern: Performance

With 20 test cases of Q=30000 each, the 30s Python limit is tight. Per test case:
- Input parsing: ~30000 calls to `input().split()` plus int conversion (~2-3s in PyPy)
- MM iterations: 30 iters * 30000 exps * (30 cumsum steps + ~20-30 denom updates) ≈ 54M ops (~0.5-1.5s in PyPy)
- Total per test case: ~3-4.5s
- For 20 test cases: ~60-90s in PyPy (EXCEEDS 30s limit)

This will likely cause TLE (not WA), which is a separate problem. We need I/O optimization.

---

## Revised Algorithm

The algorithm from Plan 1 is correct. Changes are:

### Change 1: Remove `#T` Output Prefix

Replace:
```python
print('#%d %s' % (tc, ' '.join(out_parts)))
```
With:
```python
print(' '.join(out_parts))
```

### Change 2: Optimize I/O to Avoid TLE

Since `import sys` is prohibited, we use buffered reading via `open(0)` which reads from stdin as a file object. This avoids the overhead of repeated `input()` calls. The technique:

```python
import io
data = io.BytesIO(open(0, 'rb').read()).read().split()
```

This reads ALL input at once into a byte buffer, then splits into tokens. Accessing tokens via an index pointer is much faster than repeated `input()` calls.

Note: `open(0)` opens file descriptor 0 (stdin) as a file. This is standard Python and does NOT require `import sys`. The `io` module is a built-in module (not an external package).

### Change 3: Reduce Iterations if Converged

Instead of always doing 30 iterations, check for convergence after each iteration. If the maximum relative change in weights is below a threshold (e.g., 1e-6), stop early. This can save significant time when the algorithm converges quickly (often in 15-20 iterations with Q=30000).

### Change 4: Use Fewer Iterations

With Q=30000 experiments and the 0.02 tolerance on ratios, 20 iterations should suffice. The Fisher information per parameter is very high (Q*30 observations for N<=30 parameters), and the MM algorithm converges geometrically.

---

## Implementation Plan

### Step 1: Fast Input Parsing

```python
import io

def main():
    data = io.BytesIO(open(0, 'rb').read()).read().split()
    ptr = 0

    def rd():
        nonlocal ptr
        ptr += 1
        return data[ptr - 1]

    T = int(rd())
    for tc in range(T):
        Q = int(rd())
        N = int(rd())
        F = [int(rd()) for _ in range(N)]
        M = sum(F)
        # Read Q*M ball draws (convert to 0-indexed)
        seq = [int(rd()) - 1 for _ in range(Q * M)]
```

### Step 2: Pre-compute Draw Positions

Same as Plan 1:
```python
first_draw = [0] * (Q * N)
second_draw = [0] * (Q * N)
draw_count = [0] * N

for q in range(Q):
    base_seq = q * M
    base_pos = q * N
    for j in range(N):
        draw_count[j] = 0
    for t in range(M):
        j = seq[base_seq + t]
        if draw_count[j] == 0:
            first_draw[base_pos + j] = t
        else:
            second_draw[base_pos + j] = t
        draw_count[j] += 1
```

### Step 3: MM Iteration with Cumsum Optimization

Same as Plan 1, but with early stopping:
```python
NUM_ITERS = 25
W = [1.0] * N
cumsum = [0.0] * (M + 1)

for iteration in range(NUM_ITERS):
    denom = [0.0] * N

    S0 = 0.0
    for j in range(N):
        S0 += F[j] * W[j]

    for q in range(Q):
        base_seq = q * M
        base_pos = q * N
        S = S0
        cs = 0.0
        cumsum[0] = 0.0
        for t in range(M):
            cs += 1.0 / S
            cumsum[t + 1] = cs
            S -= W[seq[base_seq + t]]

        for j in types_f1:
            denom[j] += cumsum[first_draw[base_pos + j] + 1]
        for j in types_f2:
            bp_j = base_pos + j
            denom[j] += cumsum[first_draw[bp_j] + 1] + cumsum[second_draw[bp_j] + 1]

    # MM update with convergence check
    max_change = 0.0
    for i in range(N):
        new_w = Q * F[i] / denom[i]
        if W[i] > 0:
            change = abs(new_w / W[i] - 1.0) if W[i] > 1e-300 else 0.0
            if change > max_change:
                max_change = change
        W[i] = new_w

    # Normalize
    max_w = max(W)
    for i in range(N):
        W[i] /= max_w

    if max_change < 1e-8:
        break
```

### Step 4: Output (No `#T` prefix)

```python
out_parts = []
for i in range(N):
    out_parts.append('%.15g' % W[i])
print(' '.join(out_parts))
```

### Step 5: Collect Output and Flush

To further optimize I/O, collect all test case outputs and print at the end:

```python
results = []
# ... inside loop:
results.append(' '.join(out_parts))
# After all test cases:
print('\n'.join(results))
```

---

## Performance Analysis (Revised)

### Per test case:
- Input parsing (fast I/O): ~0.5s in PyPy
- Pre-compute draw positions: ~0.1s
- MM iterations (25 iters): ~0.5-1.0s
- Total: ~1.0-1.5s

### For 20 test cases:
- Total: ~20-30s. Should fit within 30s limit.

### If still tight on time:
- Reduce to 20 iterations (sufficient for 0.02 tolerance with Q=30000).
- Use early stopping to skip iterations once converged.

---

## Summary of Changes from Plan 1

| Aspect | Plan 1 | Plan 2 |
|--------|--------|--------|
| Output format | `#T prefix + values` | **Values only (no prefix)** |
| I/O method | `input()` per line | **Bulk `open(0)` read** |
| Iterations | Fixed 30 | **25 with early stopping** |
| Algorithm | MM + cumsum | **Same (correct)** |
| Convergence check | None | **max relative change < 1e-8** |

## Complexity Summary

| Aspect | Value |
|--------|-------|
| Time per test case | ~1.0-1.5 seconds (PyPy) |
| Memory | ~30 MB (flat arrays for Q=30000, N=30) |
| Max iterations | 25 (with early stopping) |
| Algorithm | MM fixed-point (Hunter 2004) |
| Key fix | Remove `#T` output prefix |
