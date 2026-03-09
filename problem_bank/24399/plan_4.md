# Plan 4 — Problem 24399

## Root Cause of Trial 3 WA (14/20)

The MM (Minorization-Maximization) MLE is **mathematically correct** but has inherent statistical variance with Q=30000, N=30. The MLE per-component std dev in log space is ~0.006, giving pairwise ratio std ~0.0085. The max over 435 pairs (N=30) reaches ~0.030, exceeding the 0.02 threshold ~85% of the time for uniform weights.

## Fix: Fisher-Based Local James-Stein Shrinkage

After MM convergence, reduce noise by shrinking similar weights toward their cluster mean.

### Algorithm

1. **Run MM iteration** (same as trial 3) to get MLE weights W_i.

2. **Compute Fisher information** in one extra pass over all experiments:
   - Compute `cumsum_sq[t+1] = cumsum_sq[t] + 1/S_t^2` alongside `cumsum[t+1]`
   - Accumulate `denom_sq[j]` (same structure as `denom[j]` but using `cumsum_sq`)
   - Fisher info: `I_ii = Q * F_i / W_i^2 - denom_sq_i`
   - Variance: `var_i = 1 / (W_i^2 * I_ii)` (variance of log W_i)

3. **Cluster types by proximity in log space:**
   - Sort types by log(W_i)
   - Compute average variance: `sigma2 = mean(var_i)`
   - Gap threshold: `3 * sqrt(sigma2)`
   - Sequential clustering: start new cluster when gap > threshold

4. **Within-cluster James-Stein shrinkage:**
   - For each cluster of size nc >= 3:
     - Cluster mean: `mu = mean(log W_j for j in cluster)`
     - Sum of squares: `ss = sum((log W_j - mu)^2)`
     - Shrinkage factor: `shrink = min(1, (nc - 2) * sigma2 / ss)`
     - Shrunk log weight: `log W_j = mu + shrink * (log W_j - mu)`
   - For clusters of size 1-2: keep MLE estimates unchanged

5. **Convert back**: `W_i = exp(shrunk_log_W_i)`, normalize so max = 1.

### Expected Improvement

| Distribution | MLE Pass Rate | Fisher-JS Pass Rate |
|---|---|---|
| Uniform | 15% | ~100% |
| Two groups | 15% | ~100% |
| Three groups | 20% | ~100% |
| Half 0.5/1.0 | 0% | ~100% |
| Geometric | 70% | ~70% |
| Near-uniform | 15% | ~30% |

Overall: 14/20 → estimated 17-19/20.

### Performance

Extra cost: one O(Q*M) pass for cumsum_sq + O(N^2) clustering. Negligible vs existing MM loop.

### Constraints

- No `import sys`, no `open(0)`, no external packages, no walrus operator
- Use `input()` / `print()`, no `#T` output prefix
- `import math` is allowed (for `log`, `exp`)
