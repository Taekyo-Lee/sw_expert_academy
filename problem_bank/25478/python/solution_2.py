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

def lbfs(adj, n, start):
    """Lexicographic BFS. Returns ordering of vertices.
    adj: adjacency list (local indices).
    n: number of vertices.
    start: starting vertex.
    """
    # Each vertex has a label (list of negative visit-times of visited neighbors,
    # sorted in decreasing order). We pick the vertex with the lexicographically
    # largest label at each step.
    # Simpler implementation: maintain partition refinement.

    # Simple LBFS: maintain sets. At each step, pick from the first non-empty set
    # the vertex that appeared earliest (or any). When we visit a vertex, we refine
    # all sets by splitting: neighbors of the visited vertex get moved to a new set
    # placed before their current set.

    # Implementation using lists of sets (partition refinement)
    ordering = []
    visited = [False] * n
    # Start: all vertices in one set, but start vertex first
    # Use a list of lists (partitions)
    partitions = [[start] + [v for v in range(n) if v != start]]
    in_partition = list(range(n))  # Not used in simple version

    for _ in range(n):
        # Find first non-empty partition with an unvisited vertex
        v = -1
        for part in partitions:
            while part and visited[part[0]]:
                part.pop(0)
            if part:
                v = part.pop(0)
                break
        if v == -1:
            break
        visited[v] = True
        ordering.append(v)

        # Refine partitions: for each partition, split into
        # (neighbors of v) and (non-neighbors of v)
        neighbor_set = set(adj[v])
        new_partitions = []
        for part in partitions:
            neighbors = []
            non_neighbors = []
            for u in part:
                if not visited[u]:
                    if u in neighbor_set:
                        neighbors.append(u)
                    else:
                        non_neighbors.append(u)
            if neighbors:
                new_partitions.append(neighbors)
            if non_neighbors:
                new_partitions.append(non_neighbors)
        partitions = new_partitions

    return ordering

def find_proper_interval_ordering(comp, A_full):
    """Find a proper interval ordering using double LBFS.
    comp: list of global indices in this component.
    A_full: full adjacency matrix.
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
    sigma1 = lbfs(adj, n, start)

    # Second LBFS from the last vertex of the first LBFS
    sigma2 = lbfs(adj, n, sigma1[-1])

    return sigma2

def verify_ordering(sigma, A_local, n):
    """Verify that sigma is a valid proper interval ordering.
    A_local[i][j] for local indices i, j.
    """
    # Position of each local index in the ordering
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

        # Check left neighbors are consecutive ending at idx-1
        if left_neighbors:
            left_neighbors.sort()
            expected_start = idx - len(left_neighbors)
            for k, p in enumerate(left_neighbors):
                if p != expected_start + k:
                    return False

        # Check right neighbors are consecutive starting at idx+1
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

    Optimized: separate CDV from span tracking. For each step k, pre-compute
    valid (cdv, gap) -> new_cdv transitions to avoid redundant work.
    """
    FAR = D + 1

    # dp[cdv] = {span: count}
    init_cdv = tuple([FAR] * D)
    dp = {init_cdv: {0: 1}}

    for k in range(n - 1):
        next_receiver = sigma[k + 1]
        # Number of valid previous receivers to check
        check_count = min(D, k + 1)

        # Pre-compute valid transitions for each CDV
        # For a given cdv, determine which gaps are valid and what new_cdv they produce
        new_dp = {}
        for cdv, span_dict in dp.items():
            # Try each gap
            for g in range(1, D + 1):
                # Compute new cdv
                new_cdv_list = [g]
                for i in range(D - 1):
                    val = cdv[i] + g
                    if val > FAR:
                        new_cdv_list.append(FAR)
                    else:
                        new_cdv_list.append(val)
                new_cdv = tuple(new_cdv_list)

                # Check constraints
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

    # Collect span counts
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
    # Twin class: group of vertices with identical neighbor sets (including self)
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
    # For each position p: sigma[p] and sigma[n-1-p] must be twins
    for p in range(n):
        u = sigma[p]
        v = sigma[n - 1 - p]
        # Check if u and v have identical adjacency rows
        if u != v:
            for j in range(n):
                if A_local[u][j] != A_local[v][j]:
                    return False
    return True

def solve_component(comp, D, A_full):
    """Solve a single connected component.
    comp: list of global indices.
    D: distance parameter.
    A_full: full N x N adjacency matrix.
    Returns: dict mapping span -> count.
    """
    n = len(comp)
    if n == 1:
        return {0: 1}

    # Build local adjacency matrix
    A_local = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            A_local[i][j] = A_full[comp[i]][comp[j]]

    # Find proper interval ordering
    sigma = find_proper_interval_ordering(comp, A_full)

    # Verify ordering
    if not verify_ordering(sigma, A_local, n):
        return {}

    # Check bandwidth
    if not check_bandwidth(sigma, A_local, D, n):
        return {}

    # Run gap DP for forward and reverse orderings
    forward = gap_dp(sigma, A_local, D, n)
    rev_sigma = sigma[::-1]
    reverse = gap_dp(rev_sigma, A_local, D, n)

    # Compute twin factor
    twin_factor = compute_twin_factor(A_local, n)

    # Check palindromic symmetry
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

        # Find connected components
        components = find_components(N, A)
        K = len(components)

        # Solve each component
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

        # Convolve all component span dictionaries
        h = comp_spans[0]
        for i in range(1, K):
            new_h = defaultdict(int)
            for s1, c1 in h.items():
                for s2, c2 in comp_spans[i].items():
                    new_h[s1 + s2] = (new_h[s1 + s2] + c1 * c2) % MOD
            h = new_h

        # Count placements on the line
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
