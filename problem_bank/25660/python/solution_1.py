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

    # Hungarian algorithm for max-weight perfect matching
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
            used = [False] * (n + 1)

            while True:
                used[j0] = True
                i0 = p[j0]
                delta = float('inf')
                j1 = -1

                for j in range(1, n + 1):
                    if not used[j]:
                        val = -w[i0 - 1][j - 1] - u[i0] - v[j]
                        if val < minv[j]:
                            minv[j] = val
                            way[j] = j0
                        if minv[j] < delta:
                            delta = minv[j]
                            j1 = j

                for j in range(n + 1):
                    if used[j]:
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

    def is_popular(P):
        """Check if assignment P is popular using max-weight matching."""
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
        return hungarian_max_weight(w) <= 0

    # Hopcroft-Karp for maximum bipartite matching
    def max_matching(adj, n_left, n_right):
        """
        adj: list of lists, adj[u] = list of right nodes that left node u can match to.
        Left nodes: 0..n_left-1, Right nodes: 0..n_right-1
        Returns size of max matching.
        """
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
        return result, match_l, match_r

    # Strategy: Greedy search for lex-smallest popular matching.
    # For each child i (0..N-1), try the smallest gift g.
    # When child i is assigned gift g, all gifts child i prefers over g
    # must be "explained" - either matched to someone who prefers it as #1,
    # or the matching is not popular.
    #
    # Instead of the cascade approach, let me use a cleaner method:
    # Greedy assignment with feasibility check via max matching + popularity verification.
    #
    # For N<=50, we can try: for each child in order, try each gift in order,
    # check if a perfect matching exists on the remaining, and if the resulting
    # matching is popular.
    #
    # But trying all gifts for all children and running Hungarian each time is
    # O(N^2 * N^3) = O(N^5) which for N=50 is ~312M, tight but possibly feasible.
    #
    # Actually, let's be smarter. We build the assignment greedily:
    # P[0], P[1], ..., P[N-1]. For each position, try the smallest available gift.
    # Check if the remaining unassigned children/gifts can form a perfect matching
    # (this is just checking if a perfect matching exists in a bipartite graph).
    # If yes, tentatively assign and move on. At the end, verify popularity.
    # If not popular, backtrack.
    #
    # But backtracking over all N positions is too slow.
    #
    # Better approach: Use the popular matching structure.
    # A matching P is popular iff it can be decomposed using witness labels.
    # Let's directly enumerate via the cascade structure.

    # Let me try a completely different approach for robustness:
    # Build the "reduced" preference graph and find popular matchings via
    # the iterative cascade.

    first_choice = [A[i][0] for i in range(N)]

    # For a set S of "priority" gifts:
    # - Each S-gift must be matched to a child whose #1 choice is that gift (Phase 1)
    # - Each remaining child is matched to their top non-S gift (Phase 2)
    # - Phase 2 must be injective
    #
    # The cascade algorithm:
    # 1. Start with S = {}
    # 2. Each child points to top non-S gift
    # 3. If conflicts, the conflicted gift must join S
    # 4. Repeat
    #
    # When a gift g joins S, it must be matched to a child c with first_choice[c] = g.
    # If multiple such children exist, we need to try different choices (backtracking).
    # After matching c to g, remove both and continue cascade.

    best_result = [None]

    def try_cascade(S_set, phase1, used_children, used_gifts):
        """
        S_set: set of priority gifts
        phase1: dict {child: gift} for Phase 1 matches
        used_children: set of children used in Phase 1
        used_gifts: set of gifts used in Phase 1
        """
        remaining_children = [c for c in range(N) if c not in used_children]
        remaining_gifts_set = set(range(1, N + 1)) - used_gifts

        # S-gifts not yet assigned in Phase 1
        unmatched_S = S_set - used_gifts

        # Each child in remaining_children that has first_choice in unmatched_S
        # can potentially be used for Phase 1 matching of those S-gifts.
        # Also, remaining children need to find their top non-S gift.

        # First, handle unmatched S-gifts
        if unmatched_S:
            # For each unmatched S-gift, find candidate children
            s_list = sorted(unmatched_S)
            sg = s_list[0]  # Handle one at a time
            candidates = sorted([c for c in remaining_children if first_choice[c] == sg])
            if not candidates:
                return  # infeasible
            for c in candidates:
                new_phase1 = dict(phase1)
                new_phase1[c] = sg
                try_cascade(S_set, new_phase1, used_children | {c}, used_gifts | {sg})
            return

        # All S-gifts are matched. Now do Phase 2.
        # Each remaining child points to their top non-S gift among remaining gifts.
        top = {}
        for c in remaining_children:
            for j in range(N):
                g = A[c][j]
                if g not in S_set and g in remaining_gifts_set:
                    top[c] = g
                    break
            else:
                return  # infeasible

        # Check for conflicts
        gift_to_children = {}
        for c in remaining_children:
            g = top[c]
            if g not in gift_to_children:
                gift_to_children[g] = []
            gift_to_children[g].append(c)

        conflicts = [(g, cs) for g, cs in gift_to_children.items() if len(cs) > 1]

        if conflicts:
            # Pick the first conflicting gift and add it to S
            conflict_gift = min(g for g, _ in conflicts)
            # This gift must join S
            new_S = S_set | {conflict_gift}
            # Find children whose #1 choice is this gift (from ALL remaining, not just conflicting)
            candidates = sorted([c for c in remaining_children if first_choice[c] == conflict_gift])
            if not candidates:
                return  # infeasible
            for c in candidates:
                new_phase1 = dict(phase1)
                new_phase1[c] = conflict_gift
                try_cascade(new_S, new_phase1, used_children | {c}, used_gifts | {conflict_gift})
            return

        # No conflicts - Phase 2 is valid (each remaining child has unique top non-S gift)
        # But we need to check that the Phase 2 assignment actually covers all remaining gifts.
        # Actually, since each remaining child maps to a unique remaining non-S gift,
        # and the number of remaining children equals the number of remaining gifts,
        # we need: the set of top[] values has size == len(remaining_children)
        # We already checked no conflicts, so each gift is chosen by at most one child.
        # But do all remaining gifts get used? Not necessarily.
        # Actually, remaining_children and remaining_gifts_set may differ in size
        # if some gifts are in S but not all are matched... but we handled that above.
        # At this point: |remaining_children| = N - |used_children| and
        # |remaining_gifts_set| = N - |used_gifts| = N - |used_children| (since |used_gifts| = |used_children|)
        # So they're equal. And each child maps to a unique gift. So it's a valid injection,
        # and since sizes match, it's a bijection. But the gifts chosen might not cover
        # all remaining_gifts_set - some gifts might be left unassigned.
        # Wait, injection of same size sets = bijection. But the image might not equal
        # remaining_gifts_set. Some gifts in remaining_gifts_set might be S-gifts that
        # are not assigned. Actually no - we handled all S-gifts above. The remaining
        # gifts are all non-S gifts. And each child picks a non-S gift. So the image
        # is a subset of non-S remaining gifts, which equals remaining_gifts_set.
        # With equal sizes and injection, it's a bijection.

        # Build the full assignment
        full_assignment = dict(phase1)
        for c in remaining_children:
            full_assignment[c] = top[c]

        P = [full_assignment[i] for i in range(N)]

        # Verify popularity
        if is_popular(P):
            if best_result[0] is None or P < best_result[0]:
                best_result[0] = P

    # But the above cascade explores many branches. For lex-smallest, we need all
    # and take the smallest. This could be slow.
    #
    # Let me add pruning: once we find a result, we can prune branches that can't
    # produce a lex-smaller result. But that's complex.
    #
    # Alternative: since the cascade structure is fairly constrained (S grows
    # monotonically, and each S-gift can only be matched to children with it as #1),
    # the search tree is usually small.

    try_cascade(set(), {}, set(), set())

    if best_result[0] is None:
        print(-1)
    else:
        print(' '.join(map(str, best_result[0])))


TC = int(input())
for test_case in range(1, TC + 1):
    print('#%d' % test_case, end=' ')
    solve()
