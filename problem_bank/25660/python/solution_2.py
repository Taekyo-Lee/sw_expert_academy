def solve():
    N = int(input())
    A = []
    for i in range(N):
        row = list(map(int, input().split()))
        A.append(row)

    if N == 1:
        print(A[0][0])
        return

    # rank[i][g] = position of gift g in child i's preference (0-indexed, lower = better)
    rank = [[0] * (N + 1) for _ in range(N)]
    for i in range(N):
        for j in range(N):
            rank[i][A[i][j]] = j

    first_choice = [A[i][0] for i in range(N)]

    # f-items: gifts that are the first choice of at least one child
    f_items = set()
    for i in range(N):
        f_items.add(first_choice[i])

    # s-items: gifts NOT first choice of any child
    s_items = set(range(1, N + 1)) - f_items

    # Top s-item for each child (most preferred gift among s-items)
    top_s = [0] * N
    for i in range(N):
        for j in range(N):
            if A[i][j] in s_items:
                top_s[i] = A[i][j]
                break
        # If no s-item exists, top_s[i] stays 0 (child can only match first choice)

    # Build reduced graph edges for each child:
    #   - first_choice[i] (always an f-item)
    #   - top_s[i] (if it exists, i.e., top_s[i] != 0)
    # A popular matching exists iff this reduced graph has a perfect matching.
    # Every perfect matching in the reduced graph is popular.

    # edges[i] = sorted list of gifts child i can be matched to in reduced graph
    edges = [[] for _ in range(N)]
    for i in range(N):
        e = set()
        e.add(first_choice[i])
        if top_s[i] != 0:
            e.add(top_s[i])
        edges[i] = sorted(e)

    # Hopcroft-Karp for maximum bipartite matching
    def max_matching_size(adj, n_left, n_right):
        match_l = [-1] * n_left
        match_r = [-1] * n_right

        def bfs():
            dist = [0] * n_left
            queue = []
            for u in range(n_left):
                if match_l[u] == -1:
                    dist[u] = 0
                    queue.append(u)
                else:
                    dist[u] = float('inf')
            found = False
            qi = 0
            while qi < len(queue):
                u = queue[qi]
                qi += 1
                for v in adj[u]:
                    w = match_r[v]
                    if w == -1:
                        found = True
                    elif dist[w] == float('inf'):
                        dist[w] = dist[u] + 1
                        queue.append(w)
            return found, dist

        def dfs(u, dist):
            for v in adj[u]:
                w = match_r[v]
                if w == -1 or (dist[w] == dist[u] + 1 and dfs(w, dist)):
                    match_l[u] = v
                    match_r[v] = u
                    return True
            dist[u] = float('inf')
            return False

        result = 0
        while True:
            found, dist = bfs()
            if not found:
                break
            for u in range(n_left):
                if match_l[u] == -1:
                    if dfs(u, dist):
                        result += 1
        return result

    # Find lex-smallest perfect matching in reduced graph via greedy + feasibility
    # For each child i (0..N-1), try each gift g in edges[i] in ascending order.
    # Fix P[i] = g and check if remaining children can still form a perfect matching.
    # The feasibility check uses Hopcroft-Karp on the remaining subgraph.

    assignment = [-1] * N
    used = set()

    # Map gifts to indices for matching
    all_gifts = list(range(1, N + 1))
    gift_to_idx = {}
    for idx, g in enumerate(all_gifts):
        gift_to_idx[g] = idx

    success = True
    for i in range(N):
        assigned = False
        for g in edges[i]:
            if g in used:
                continue

            # Tentatively assign P[i] = g
            used.add(g)

            # Check feasibility: can children i+1..N-1 be matched to remaining gifts?
            remaining_children = list(range(i + 1, N))
            remaining_gifts = [gg for gg in all_gifts if gg not in used]
            rg_set = set(remaining_gifts)
            rg_to_idx = {}
            for idx2, gg in enumerate(remaining_gifts):
                rg_to_idx[gg] = idx2

            adj = []
            for c in remaining_children:
                adj_c = []
                for gg in edges[c]:
                    if gg in rg_to_idx:
                        adj_c.append(rg_to_idx[gg])
                adj.append(adj_c)

            n_left = len(remaining_children)
            n_right = len(remaining_gifts)
            size = max_matching_size(adj, n_left, n_right)

            if size == n_left:
                # Feasible - commit
                assignment[i] = g
                assigned = True
                break
            else:
                # Rollback
                used.discard(g)

        if not assigned:
            success = False
            break

    if not success:
        print(-1)
        return

    # Verify popularity using Hungarian algorithm
    # P is popular iff the max-weight perfect matching on the vote matrix has weight <= 0
    # vote(i, g, P) = sign(rank[i][P[i]] - rank[i][g])

    def hungarian_max_weight(w):
        n = len(w)
        u = [0] * (n + 1)
        v = [0] * (n + 1)
        p = [0] * (n + 1)
        way = [0] * (n + 1)

        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [float('inf')] * (n + 1)
            used_h = [False] * (n + 1)

            while True:
                used_h[j0] = True
                i0 = p[j0]
                delta = float('inf')
                j1 = -1

                for j in range(1, n + 1):
                    if not used_h[j]:
                        val = -w[i0 - 1][j - 1] - u[i0] - v[j]
                        if val < minv[j]:
                            minv[j] = val
                            way[j] = j0
                        if minv[j] < delta:
                            delta = minv[j]
                            j1 = j

                for j in range(n + 1):
                    if used_h[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta

                j0 = j1
                if p[j0] == 0:
                    break

            while j0:
                p[j0] = p[way[j0]]
                j0 = way[j0]

        total = 0
        for j in range(1, n + 1):
            total += w[p[j] - 1][j - 1]
        return total

    P = assignment
    w = [[0] * N for _ in range(N)]
    for i in range(N):
        ri = rank[i][P[i]]
        for g in range(1, N + 1):
            rg = rank[i][g]
            if rg < ri:
                w[i][g - 1] = 1
            elif rg > ri:
                w[i][g - 1] = -1
            else:
                w[i][g - 1] = 0

    if hungarian_max_weight(w) <= 0:
        print(' '.join(map(str, P)))
    else:
        print(-1)


TC = int(input())
for test_case in range(1, TC + 1):
    solve()
