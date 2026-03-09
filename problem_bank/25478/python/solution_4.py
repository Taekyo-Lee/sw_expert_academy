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

def lbfs_generic(adj, n, start, tiebreak=None):
    """LBFS using label-based approach.
    Each vertex gets a label (list of step numbers when neighbors were visited).
    At each step, choose the unvisited vertex with lexicographically largest label.
    Ties broken by tiebreak[v] (higher = chosen first), or by vertex index if None.
    """
    ordering = []
    visited = [False] * n
    label = [[] for _ in range(n)]

    for step in range(n):
        # Choose unvisited vertex with lexicographically largest label
        # Break ties by tiebreak (higher first) then by start preference
        best = -1
        best_key = None
        for v in range(n):
            if visited[v]:
                continue
            if tiebreak is not None:
                key = (label[v], tiebreak[v])
            else:
                # For first LBFS: prefer start vertex, then arbitrary
                key = (label[v], n if v == start else 0)
            if best == -1 or key > best_key:
                best = v
                best_key = key
        visited[best] = True
        ordering.append(best)

        # Update labels of unvisited neighbors
        # Prepend so most recent step is first (lexicographic comparison = decreasing order)
        for u in adj[best]:
            if not visited[u]:
                label[u].insert(0, step)

    return ordering

def find_proper_interval_ordering(comp, A_full):
    """Find a proper interval ordering using LBFS + LBFS+.
    comp: list of global indices in this component.
    Returns: list of local indices (0..n-1) in proper interval order.
    """
    n = len(comp)
    if n == 1:
        return [0]

    # Build local adjacency list
    adj = [[] for _ in range(n)]
    deg = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and A_full[comp[i]][comp[j]] == 1:
                adj[i].append(j)
                deg[i] += 1

    # Start from a vertex with minimum degree
    start = min(range(n), key=lambda x: (deg[x], x))

    # First LBFS from start
    sigma1 = lbfs_generic(adj, n, start)

    # Build tiebreak for LBFS+: position in sigma1 (later = higher priority)
    tiebreak1 = [0] * n
    for i, v in enumerate(sigma1):
        tiebreak1[v] = i

    # Second sweep: LBFS+ from the last vertex of sigma1
    sigma2 = lbfs_generic(adj, n, sigma1[-1], tiebreak1)

    # Build tiebreak for third sweep
    tiebreak2 = [0] * n
    for i, v in enumerate(sigma2):
        tiebreak2[v] = i

    # Third sweep: LBFS+ from the last vertex of sigma2
    sigma3 = lbfs_generic(adj, n, sigma2[-1], tiebreak2)

    return sigma3

def verify_ordering(sigma, A_local, n):
    """Verify that sigma is a valid proper interval ordering."""
    pos = [0] * n
    for i in range(n):
        pos[sigma[i]] = i

    for idx in range(n):
        v = sigma[idx]
        left_neighbors = []
        right_neighbors = []
        for j in range(n):
            if j != v and A_local[v][j] == 1:
                p = pos[j]
                if p < idx:
                    left_neighbors.append(p)
                else:
                    right_neighbors.append(p)

        if left_neighbors:
            left_neighbors.sort()
            expected_start = idx - len(left_neighbors)
            for k, p in enumerate(left_neighbors):
                if p != expected_start + k:
                    return False

        if right_neighbors:
            right_neighbors.sort()
            for k, p in enumerate(right_neighbors):
                if p != idx + 1 + k:
                    return False

    return True

def check_bandwidth(sigma, A_local, D, n):
    """Check that all friends in the ordering are within distance D."""
    pos = [0] * n
    for i in range(n):
        pos[sigma[i]] = i

    for i in range(n):
        for j in range(i + 1, n):
            if A_local[i][j] == 1:
                if abs(pos[i] - pos[j]) > D:
                    return False
    return True

def gap_dp(sigma, A_local, D, n):
    """Run gap DP on the given ordering.
    Returns: dict mapping span -> count of valid gap sequences.
    """
    FAR = D + 1

    init_cdv = tuple([FAR] * D)
    dp = {init_cdv: {0: 1}}

    for k in range(n - 1):
        next_receiver = sigma[k + 1]
        check_count = min(D, k + 1)

        new_dp = {}
        for cdv, span_dict in dp.items():
            for g in range(1, D + 1):
                new_cdv_list = [g]
                for i in range(D - 1):
                    val = cdv[i] + g
                    if val > FAR:
                        new_cdv_list.append(FAR)
                    else:
                        new_cdv_list.append(val)
                new_cdv = tuple(new_cdv_list)

                valid = True
                for i in range(check_count):
                    prev_receiver = sigma[k - i]
                    dist = new_cdv[i]
                    if dist <= D:
                        if A_local[next_receiver][prev_receiver] != 1:
                            valid = False
                            break
                    else:
                        if A_local[next_receiver][prev_receiver] != 0:
                            valid = False
                            break

                if valid:
                    if new_cdv in new_dp:
                        target = new_dp[new_cdv]
                        for span, count in span_dict.items():
                            new_span = span + g
                            if new_span in target:
                                target[new_span] = (target[new_span] + count) % MOD
                            else:
                                target[new_span] = count
                    else:
                        target = {}
                        for span, count in span_dict.items():
                            target[span + g] = count
                        new_dp[new_cdv] = target
        dp = new_dp

    span_counts = {}
    for cdv, span_dict in dp.items():
        for span, count in span_dict.items():
            if span in span_counts:
                span_counts[span] = (span_counts[span] + count) % MOD
            else:
                span_counts[span] = count
    return span_counts

def compute_twin_factor(A_local, n):
    """Compute product of factorials of twin class sizes."""
    twin_key = {}
    for i in range(n):
        key = tuple(A_local[i][j] for j in range(n))
        if key not in twin_key:
            twin_key[key] = 0
        twin_key[key] += 1

    result = 1
    for sz in twin_key.values():
        for k in range(1, sz + 1):
            result = result * k % MOD
    return result

def check_palindromic(sigma, A_local, n):
    """Check if reverse(sigma) can be obtained from sigma by permuting within twin classes."""
    for p in range(n):
        u = sigma[p]
        v = sigma[n - 1 - p]
        if u != v:
            for j in range(n):
                if A_local[u][j] != A_local[v][j]:
                    return False
    return True

def solve_component(comp, D, A_full):
    """Solve a single connected component."""
    n = len(comp)
    if n == 1:
        return {0: 1}

    A_local = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            A_local[i][j] = A_full[comp[i]][comp[j]]

    sigma = find_proper_interval_ordering(comp, A_full)

    if not verify_ordering(sigma, A_local, n):
        return {}

    if not check_bandwidth(sigma, A_local, D, n):
        return {}

    forward = gap_dp(sigma, A_local, D, n)
    rev_sigma = sigma[::-1]
    reverse = gap_dp(rev_sigma, A_local, D, n)

    twin_factor = compute_twin_factor(A_local, n)
    palindromic = check_palindromic(sigma, A_local, n)

    result = {}
    if palindromic:
        for s, c in forward.items():
            result[s] = c * twin_factor % MOD
    else:
        all_spans = set(forward.keys()) | set(reverse.keys())
        for s in all_spans:
            val = (forward.get(s, 0) + reverse.get(s, 0)) % MOD
            result[s] = val * twin_factor % MOD

    return result

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
            print(X % MOD)
            continue

        components = find_components(N, A)
        K = len(components)

        comp_spans = []
        impossible = False
        for comp in components:
            g = solve_component(comp, D, A)
            if not g:
                impossible = True
                break
            comp_spans.append(g)

        if impossible:
            print(0)
            continue

        h = comp_spans[0]
        for i in range(1, K):
            new_h = defaultdict(int)
            for s1, c1 in h.items():
                for s2, c2 in comp_spans[i].items():
                    new_h[s1 + s2] = (new_h[s1 + s2] + c1 * c2) % MOD
            h = new_h

        factorial_K = 1
        for i in range(1, K + 1):
            factorial_K = factorial_K * i % MOD

        answer = 0
        for S, cnt in h.items():
            T_val = X - 1 - S - (K - 1) * (D + 1)
            if T_val >= 0:
                answer = (answer + cnt * comb(T_val + K, K)) % MOD

        answer = answer * factorial_K % MOD
        print(answer)

solve()
