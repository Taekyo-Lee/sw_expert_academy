from bisect import bisect_left

MOD = 10**9 + 7

def solve():
    N, K = map(int, input().split())
    c = list(map(int, input().split()))

    # Special case: N = 1
    if N == 1:
        # Single node tree, effect = 0, and K >= 1 so always qualifies
        return 1

    # Separate meaningful and empty items
    meaningful = []
    for ci in c:
        if ci >= 0:
            meaningful.append(ci)
    m = len(meaningful)
    e = N - m  # number of empty items (c_i = -1)

    totalM = sum(meaningful)

    # Number of labeled trees on N nodes = N^(N-2)
    total_trees = pow(N, N - 2, MOD)

    # threshold: sum of isolated meaningful items' potentials >= threshold
    # effect = totalM - sum(S) <= K  =>  sum(S) >= totalM - K
    threshold = totalM - K

    # If threshold <= 0, all trees qualify
    if threshold <= 0:
        return total_trees

    # If m = 0: effect is always 0. Answer = total_trees.
    if m == 0:
        return total_trees

    # If m = 1: single meaningful item is always isolated (never has meaningful neighbor).
    # Effect = 0. Answer = total_trees.
    if m == 1:
        return total_trees

    # If e = 0: no meaningful item can be isolated (all neighbors are meaningful).
    # Effect = totalM for every tree.
    if e == 0:
        if totalM <= K:
            return total_trees
        else:
            return 0

    # Compute g(t) for t = 0..m
    # g(t) = number of trees where a specific set of t meaningful items are all isolated
    # e >= 1:
    #   t < m: g(t) = e^t * N^(e-1) * (N-t)^(m-t-1)
    #   t = m >= 1: g(m) = e^(m-1) * N^(e-1)
    g = [0] * (m + 1)
    Ne1 = pow(N, e - 1, MOD)
    for t in range(m):
        exp_mt = m - t - 1
        base_nt = N - t
        if base_nt == 0:
            if exp_mt == 0:
                g[t] = pow(e, t, MOD) * Ne1 % MOD
            else:
                g[t] = 0
        else:
            g[t] = pow(e, t, MOD) * Ne1 % MOD * pow(base_nt, exp_mt, MOD) % MOD
    g[m] = pow(e, m - 1, MOD) * Ne1 % MOD

    # Precompute binomial coefficients C(n, k) for n, k up to m
    comb = [[0] * (m + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        comb[i][0] = 1
        for j in range(1, i + 1):
            comb[i][j] = (comb[i - 1][j - 1] + comb[i - 1][j]) % MOD

    # Compute f(r) for r = 0..m
    # f(r) = sum_{t=r}^{m} g(t) * (-1)^(t-r) * C(m-r, t-r)
    # This is the weight for a subset of size r
    f = [0] * (m + 1)
    for r in range(m + 1):
        val = 0
        for t in range(r, m + 1):
            d = t - r
            sign = 1 if d % 2 == 0 else MOD - 1
            val = (val + g[t] * sign % MOD * comb[m - r][d]) % MOD
        f[r] = val

    # Meet-in-the-middle
    # Split meaningful potentials into two halves
    half = m // 2
    A = meaningful[:half]
    B = meaningful[half:]
    sA = len(A)
    sB = len(B)

    # Enumerate all subsets of A: record (sum, size)
    # Use incremental DP: subset mask differs from mask ^ lowbit by one element
    numA = 1 << sA
    a_sums = [0] * numA
    a_sizes = [0] * numA
    for mask in range(1, numA):
        lowbit = mask & (-mask)
        idx = lowbit.bit_length() - 1
        prev = mask ^ lowbit
        a_sums[mask] = a_sums[prev] + A[idx]
        a_sizes[mask] = a_sizes[prev] + 1

    # Sort A-subsets by sum
    order = sorted(range(numA), key=lambda x: a_sums[x])
    sorted_a_sums = [a_sums[order[i]] for i in range(numA)]
    sorted_a_sizes = [a_sizes[order[i]] for i in range(numA)]

    # Enumerate all subsets of B: record (sum, size)
    numB = 1 << sB
    b_sums = [0] * numB
    b_sizes = [0] * numB
    for mask in range(1, numB):
        lowbit = mask & (-mask)
        idx = lowbit.bit_length() - 1
        prev = mask ^ lowbit
        b_sums[mask] = b_sums[prev] + B[idx]
        b_sizes[mask] = b_sizes[prev] + 1

    # Group B-subsets by size
    b_by_size = [[] for _ in range(sB + 1)]
    for mask in range(numB):
        b_by_size[b_sizes[mask]].append(b_sums[mask])

    # For each B-size b, build suffix weighted-sum array over sorted A-subsets,
    # then process all B-subsets of that size.
    ans = 0
    for b in range(sB + 1):
        if not b_by_size[b]:
            continue
        # Build suffix_w: suffix_w[i] = sum of f(sorted_a_sizes[j] + b) for j = i..numA-1
        # Walk backward
        suffix_w = [0] * (numA + 1)
        for i in range(numA - 1, -1, -1):
            r = sorted_a_sizes[i] + b
            suffix_w[i] = (suffix_w[i + 1] + f[r]) % MOD

        # Process each B-subset of this size
        for sb_val in b_by_size[b]:
            need = threshold - sb_val
            # Find first index in sorted_a_sums >= need
            idx = bisect_left(sorted_a_sums, need)
            ans = (ans + suffix_w[idx]) % MOD

    return ans % MOD


T = int(input())
for test_case in range(1, T + 1):
    print(solve())
