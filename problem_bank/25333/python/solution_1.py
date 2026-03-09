from bisect import bisect_left
from collections import defaultdict

MOD = 10**9 + 7

def solve():
    N, K = map(int, input().split())
    c = list(map(int, input().split()))

    # Special case: N = 1
    if N == 1:
        # Single node tree, effect = 0 (no adjacent meaningful items possible)
        # 0 <= K always since K >= 1
        return 1

    # Separate meaningful and empty items
    meaningful = []
    for ci in c:
        if ci >= 0:
            meaningful.append(ci)
    m = len(meaningful)
    e = N - m  # number of empty items (c_i = -1)

    totalM = sum(meaningful)

    # Number of labeled trees on N nodes = N^(N-2) (Cayley's formula)
    total_trees = pow(N, N - 2, MOD)

    # threshold: we need sum(S) >= threshold where S is the set of isolated meaningful items
    # effect = totalM - sum(S) <= K  =>  sum(S) >= totalM - K
    threshold = totalM - K

    # If threshold <= 0, all trees qualify
    if threshold <= 0:
        return total_trees

    # If e = 0 (no empty items): no meaningful item can be isolated
    # (every neighbor of every node is meaningful since all nodes are meaningful)
    # So effect = totalM for all trees.
    if e == 0:
        # effect = totalM for every tree. Answer = total_trees if totalM <= K, else 0.
        if totalM <= K:
            return total_trees
        else:
            return 0

    # If m = 0: effect is always 0 (no meaningful items). Answer = total_trees.
    if m == 0:
        return total_trees

    # Compute g(t) for t = 0..m
    # g(t) = number of trees where a specific set of t meaningful items are all isolated
    # e >= 1:
    #   t < m: g(t) = e^t * N^(e-1) * (N-t)^(m-t-1) mod p
    #   t = m (and m >= 1): g(m) = e^(m-1) * N^(e-1) mod p
    g = [0] * (m + 1)
    Ne1 = pow(N, e - 1, MOD)
    for t in range(m):
        if m - t - 1 >= 0:
            if N - t == 0:
                # (N-t)^(m-t-1) when N-t=0 and m-t-1>=1 => 0
                if m - t - 1 == 0:
                    g[t] = pow(e, t, MOD) * Ne1 % MOD
                else:
                    g[t] = 0
            else:
                g[t] = pow(e, t, MOD) * Ne1 % MOD * pow(N - t, m - t - 1, MOD) % MOD
    if m >= 1:
        g[m] = pow(e, m - 1, MOD) * Ne1 % MOD

    # Meet-in-the-middle to compute N_r for r = 0..m
    # N_r = number of size-r subsets of meaningful items with sum >= threshold
    # Split meaningful into two halves
    half = m // 2
    A = meaningful[:half]
    B = meaningful[half:]
    sA = len(A)
    sB = len(B)

    # Enumerate all subsets of A, grouped by size
    # subA[size] = sorted list of sums
    subA = defaultdict(list)
    for mask in range(1 << sA):
        s = 0
        cnt = 0
        for i in range(sA):
            if mask & (1 << i):
                s += A[i]
                cnt += 1
        subA[cnt].append(s)
    for key in subA:
        subA[key].sort()

    # Enumerate all subsets of B, grouped by size
    subB = defaultdict(list)
    for mask in range(1 << sB):
        s = 0
        cnt = 0
        for i in range(sB):
            if mask & (1 << i):
                s += B[i]
                cnt += 1
        subB[cnt].append(s)
    for key in subB:
        subB[key].sort()

    # Compute N_r for each r
    Nr = [0] * (m + 1)
    for r in range(m + 1):
        count = 0
        for rA in range(min(r, sA) + 1):
            rB = r - rA
            if rB < 0 or rB > sB:
                continue
            listA = subA.get(rA)
            listB = subB.get(rB)
            if listA is None or listB is None:
                continue
            # For each sum_B in listB, count sum_A in listA where sum_A + sum_B >= threshold
            # i.e., sum_A >= threshold - sum_B
            for sB_val in listB:
                need = threshold - sB_val
                # Count elements in listA >= need
                idx = bisect_left(listA, need)
                count += len(listA) - idx
        Nr[r] = count

    # Precompute binomial coefficients C(n, k) for n, k up to m
    # We need C(m-r, t-r) where 0 <= r <= t <= m
    # So we need C(i, j) for i up to m, j up to m
    comb = [[0] * (m + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        comb[i][0] = 1
        for j in range(1, i + 1):
            comb[i][j] = (comb[i - 1][j - 1] + comb[i - 1][j]) % MOD

    # Compute H(t) for t = 0..m
    # H(t) = sum_{r=0}^{t} (-1)^(t-r) * C(m-r, t-r) * N_r
    H = [0] * (m + 1)
    for t in range(m + 1):
        val = 0
        for r in range(t + 1):
            sign = 1 if (t - r) % 2 == 0 else -1
            val += sign * comb[m - r][t - r] * Nr[r]
        H[t] = val % MOD

    # Compute final answer
    # answer = sum_{t=0}^{m} g(t) * H(t) mod p
    ans = 0
    for t in range(m + 1):
        ans = (ans + g[t] * H[t]) % MOD

    return ans % MOD


T = int(input())
for test_case in range(1, T + 1):
    print(solve())
