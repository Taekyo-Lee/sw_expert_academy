from collections import defaultdict

MOD = 10**9 + 7

def modinv(a, m=MOD):
    return pow(a, m - 2, m)

def comb(n, r):
    if r < 0 or r > n:
        return 0
    if r == 0 or r == n:
        return 1
    r = min(r, n - r)
    num = 1
    den = 1
    for i in range(r):
        num = num * ((n - i) % MOD) % MOD
        den = den * ((i + 1) % MOD) % MOD
    return num * modinv(den) % MOD

def find_components(N, A):
    visited = [False] * N
    components = []
    for i in range(N):
        if not visited[i]:
            comp = []
            stack = [i]
            while stack:
                u = stack.pop()
                if visited[u]:
                    continue
                visited[u] = True
                comp.append(u)
                for v in range(N):
                    if not visited[v] and A[u][v] == 1 and u != v:
                        stack.append(v)
            components.append(comp)
    return components

def solve_component_spans(comp, D, A_full):
    n = len(comp)
    if n == 1:
        return {0: 1}

    # Build local adjacency
    # friend_mask[r] = bitmask of friends of r (excluding r itself)
    friend_mask = [0] * n
    # adj_mask[r] = bitmask of r and all friends of r (including r)
    adj_mask = [0] * n
    for i in range(n):
        adj_mask[i] = 1 << i
        for j in range(n):
            if i != j and A_full[comp[i]][comp[j]] == 1:
                friend_mask[i] |= (1 << j)
                adj_mask[i] |= (1 << j)

    all_placed = (1 << n) - 1
    max_span = (n - 1) * D

    # DP state: (window_tuple, placed_bitmask) -> count
    # window_tuple has D entries: window[0] = most recent, window[D-1] = oldest
    # Each entry is receiver local index or n (empty sentinel, to avoid -1)
    EMPTY = n  # sentinel for empty slot

    dp = defaultdict(int)
    for r in range(n):
        window = [EMPTY] * D
        window[0] = r
        dp[(tuple(window), 1 << r)] += 1

    span_counts = defaultdict(int)

    # Precompute: for each receiver r, which receivers are compatible to be in same window
    # (i.e., friends). Build a set of "window_mask" -> set of receivers that can be placed
    # alongside that window.

    for p in range(2, max_span + 2):
        new_dp = defaultdict(int)
        for (window, placed), count in dp.items():
            # Compute bitmask of receivers in current window
            win_mask = 0
            for k in range(D):
                w = window[k]
                if w != EMPTY:
                    win_mask |= (1 << w)

            exiting = window[D - 1]

            # Option 1: skip this position (place nothing)
            new_placed_skip = placed
            # Exit check for skip
            skip_ok = True
            if exiting != EMPTY:
                if (friend_mask[exiting] & new_placed_skip) != friend_mask[exiting]:
                    skip_ok = False
            if skip_ok:
                new_window_skip = (EMPTY,) + window[:D - 1]
                new_dp[(new_window_skip, new_placed_skip)] = (
                    new_dp[(new_window_skip, new_placed_skip)] + count) % MOD

            # Option 2: place an unplaced receiver r
            # r must be friend of all receivers in window
            # So r's adj_mask must contain win_mask
            unplaced = all_placed ^ placed
            r_bit = 1
            for r in range(n):
                if unplaced & r_bit:
                    # Check: all receivers in window must be friends of r
                    if (adj_mask[r] & win_mask) == win_mask:
                        new_placed_r = placed | r_bit
                        # Exit check
                        exit_ok = True
                        if exiting != EMPTY:
                            if (friend_mask[exiting] & new_placed_r) != friend_mask[exiting]:
                                exit_ok = False
                        if exit_ok:
                            if new_placed_r == all_placed:
                                # All receivers placed, record span
                                span_counts[p - 1] = (span_counts[p - 1] + count) % MOD
                            else:
                                new_window_r = (r,) + window[:D - 1]
                                new_dp[(new_window_r, new_placed_r)] = (
                                    new_dp[(new_window_r, new_placed_r)] + count) % MOD
                r_bit <<= 1

        dp = new_dp

    return span_counts

def solve():
    T = int(input())
    for tc in range(1, T + 1):
        line = input().split()
        N, X, D = int(line[0]), int(line[1]), int(line[2])

        A = []
        for i in range(N):
            row_str = input().strip()
            A.append([int(c) for c in row_str])

        if N == 1:
            print("#{} {}".format(tc, X % MOD))
            continue

        # Find connected components
        components = find_components(N, A)
        K = len(components)

        # Solve each component
        comp_spans = []
        for comp in components:
            g = solve_component_spans(comp, D, A)
            comp_spans.append(g)

        # Check if any component has empty span_counts (impossible embedding)
        impossible = False
        for g in comp_spans:
            if not g:
                impossible = True
                break

        if impossible:
            print("#{} 0".format(tc))
            continue

        # Convolve all component span dictionaries
        h = comp_spans[0]
        for i in range(1, K):
            new_h = defaultdict(int)
            for s1, c1 in h.items():
                for s2, c2 in comp_spans[i].items():
                    new_h[s1 + s2] = (new_h[s1 + s2] + c1 * c2) % MOD
            h = new_h

        # Count placements
        factorial_K = 1
        for i in range(1, K + 1):
            factorial_K = factorial_K * i % MOD

        answer = 0
        for S, cnt in h.items():
            T_val = X - 1 - S - (K - 1) * (D + 1)
            if T_val >= 0:
                answer = (answer + cnt * comb(T_val + K, K)) % MOD

        answer = answer * factorial_K % MOD
        print("#{} {}".format(tc, answer))

solve()
