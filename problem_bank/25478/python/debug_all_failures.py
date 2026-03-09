"""Test the LBFS+ fix on all stress test failure cases."""

MOD = 10**9 + 7

def verify_ordering(sigma, A_local, n):
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

def lbfs(adj, n, start):
    ordering = []
    visited = [False] * n
    partitions = [[start] + [v for v in range(n) if v != start]]
    for _ in range(n):
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

def lbfs_plus(adj, n, start, prev_order):
    """LBFS with tie-breaking: within each partition, process vertices in
    decreasing order of their position in prev_order."""
    ordering = []
    visited = [False] * n

    # Priority: position in prev_order (higher = earlier to pick)
    priority = [0] * n
    for i, v in enumerate(prev_order):
        priority[v] = i

    # Initialize: sort by decreasing priority (later in prev_order = higher priority)
    initial = [start] + sorted([v for v in range(n) if v != start], key=lambda v: -priority[v])
    partitions = [initial]

    for _ in range(n):
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
            # Within each sub-partition, preserve the order from the parent partition
            # (which was already sorted by priority)
            if neighbors:
                new_partitions.append(neighbors)
            if non_neighbors:
                new_partitions.append(non_neighbors)
        partitions = new_partitions

    return ordering

def find_proper_interval_ordering_fixed(adj, n):
    """Find proper interval ordering using LBFS+ (3-sweep)."""
    if n == 1:
        return [0]

    deg = [len(adj[v]) for v in range(n)]
    start = min(range(n), key=lambda x: (deg[x], x))

    # First LBFS
    sigma1 = lbfs(adj, n, start)
    # LBFS+ from last vertex, tie-breaking by sigma1
    sigma2 = lbfs_plus(adj, n, sigma1[-1], sigma1)

    return sigma2

# Test on failing cases from stress test
failing_cases = [
    # (N, X, D, A_rows)
    (4, 12, 4, ["1001", "0111", "0111", "1111"]),
    (5, 13, 3, ["10101", "01011", "10111", "01111", "11111"]),
    (4, 14, 4, ["1010", "0111", "1111", "0111"]),
    (4, 13, 2, ["1001", "0111", "0111", "1111"]),
    (5, 12, 4, ["11100", "11110", "11111", "01111", "00111"]),
    (4, 14, 2, ["1100", "1111", "0111", "0111"]),
    (5, 12, 2, ["11011", "11110", "01110", "11111", "10011"]),
    (6, 13, 2, ["100110", "010000", "001011", "100100", "101011", "001011"]),
    (5, 13, 3, ["11111", "11010", "10101", "11010", "10101"]),
    (5, 10, 4, ["11111", "11011", "10101", "11011", "11111"]),
]

for idx, (N, X, D, A_rows) in enumerate(failing_cases):
    A = [[int(c) for c in row] for row in A_rows]
    n = N

    # Find components
    visited = [False] * n
    components = []
    for i in range(n):
        if not visited[i]:
            comp = []
            stack = [i]
            while stack:
                u = stack.pop()
                if visited[u]:
                    continue
                visited[u] = True
                comp.append(u)
                for v in range(n):
                    if not visited[v] and A[u][v] == 1 and u != v:
                        stack.append(v)
            components.append(comp)

    print("Case {}: N={}, X={}, D={}".format(idx+1, N, X, D))
    all_ok = True
    for comp in components:
        nc = len(comp)
        if nc <= 1:
            continue

        # Build local adjacency
        A_local = [[0]*nc for _ in range(nc)]
        for i in range(nc):
            for j in range(nc):
                A_local[i][j] = A[comp[i]][comp[j]]

        adj = [[] for _ in range(nc)]
        for i in range(nc):
            for j in range(nc):
                if i != j and A_local[i][j] == 1:
                    adj[i].append(j)

        # Old method
        deg = [len(adj[v]) for v in range(nc)]
        start = min(range(nc), key=lambda x: (deg[x], x))
        s1_old = lbfs(adj, nc, start)
        s2_old = lbfs(adj, nc, s1_old[-1])
        old_valid = verify_ordering(s2_old, A_local, nc)

        # New method
        sigma_new = find_proper_interval_ordering_fixed(adj, nc)
        new_valid = verify_ordering(sigma_new, A_local, nc)

        if not old_valid or not new_valid:
            print("  Comp {} (size {}): OLD={} (valid={}), NEW={} (valid={})".format(
                comp, nc, s2_old, old_valid, sigma_new, new_valid))
            if not new_valid:
                all_ok = False

    if all_ok:
        print("  All components valid with LBFS+ fix")
    else:
        print("  STILL BROKEN with LBFS+ fix!")
