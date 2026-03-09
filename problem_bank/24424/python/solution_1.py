from heapq import heappush, heappop

MOD = 10**9 + 7
INF = float('inf')

T = int(input())
for test_case in range(1, T + 1):
    R = int(input())

    terminal_rules = []   # (N_idx, char)
    binary_rules = []     # (M_idx, A_idx, B_idx)

    for _ in range(R):
        parts = input().split()
        # parts: [X, '->', ...]
        lhs = ord(parts[0]) - ord('A')
        rhs = parts[2]
        if len(rhs) == 1:
            if rhs.islower():
                terminal_rules.append((lhs, rhs))
            else:
                # Single uppercase: X -> Y means... not in problem spec
                # Actually problem says rules are either X -> YZ or X -> x
                # So single uppercase shouldn't happen, but just in case treat as binary?
                # This shouldn't occur per problem constraints.
                pass
        else:
            # rhs is two uppercase letters like "AB"
            a_idx = ord(rhs[0]) - ord('A')
            b_idx = ord(rhs[1]) - ord('A')
            binary_rules.append((lhs, a_idx, b_idx))

    line = input().split()
    n, m, x, y = int(line[0]), int(line[1]), int(line[2]), int(line[3])

    edges = []
    for _ in range(m):
        parts = input().split()
        u, v, c = int(parts[0]), int(parts[1]), parts[2]
        edges.append((u, v, c))

    # Check if S (index 18) is productive
    productive = [False] * 26
    for (nt, ch) in terminal_rules:
        productive[nt] = True
    changed = True
    while changed:
        changed = False
        for (m_idx, a_idx, b_idx) in binary_rules:
            if not productive[m_idx] and productive[a_idx] and productive[b_idx]:
                productive[m_idx] = True
                changed = True

    S_idx = ord('S') - ord('A')
    if not productive[S_idx]:
        print(-1)
        continue

    # Build rule lookups
    # left_of[N] = list of (M, B) where rule M -> N B
    # right_of[N] = list of (M, A) where rule M -> A N
    left_of = [[] for _ in range(26)]
    right_of = [[] for _ in range(26)]
    for (m_idx, a_idx, b_idx) in binary_rules:
        if productive[a_idx] and productive[b_idx]:
            left_of[a_idx].append((m_idx, b_idx))
            right_of[b_idx].append((m_idx, a_idx))

    # dist[N][u][v] = minimum length string derivable from N that labels path u->v
    # Using 1-indexed vertices: u, v in [1..n]
    # State: (N, u, v) where N in [0..25], u in [0..n-1], v in [0..n-1] (shift to 0-indexed)
    # Actually let's use 1-indexed for vertices to match input

    dist = [[[INF] * (n + 1) for _ in range(n + 1)] for _ in range(26)]
    finalized = [[[False] * (n + 1) for _ in range(n + 1)] for _ in range(26)]

    heap = []

    # Initialize with terminal rules
    for (nt, ch) in terminal_rules:
        for (u, v, c) in edges:
            if c == ch:
                if dist[nt][u][v] > 1:
                    dist[nt][u][v] = 1
                    heappush(heap, (1, nt, u, v))

    # Dijkstra
    while heap:
        d, N, u, v = heappop(heap)
        if finalized[N][u][v]:
            continue
        finalized[N][u][v] = True

        # N is left child: rules M -> N B
        for (M, B) in left_of[N]:
            for w in range(1, n + 1):
                if finalized[B][v][w]:
                    new_d = d + dist[B][v][w]
                    if new_d < dist[M][u][w]:
                        dist[M][u][w] = new_d
                        heappush(heap, (new_d, M, u, w))

        # N is right child: rules M -> A N
        for (M, A) in right_of[N]:
            for w in range(1, n + 1):
                if finalized[A][w][u]:
                    new_d = dist[A][w][u] + d
                    if new_d < dist[M][w][v]:
                        dist[M][w][v] = new_d
                        heappush(heap, (new_d, M, w, v))

    if finalized[S_idx][x][y]:
        print(dist[S_idx][x][y] % MOD)
    else:
        print(-1)
