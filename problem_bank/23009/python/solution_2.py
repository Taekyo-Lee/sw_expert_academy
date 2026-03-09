from bisect import bisect_right

MOD = 998244353

LEAF = 0
ASC = 1
DESC = 2
PRIME = 3


def count_crossing(children_sizes, X):
    """
    Count ordered crossing pairs for a linear node with given children sizes.
    Returns the count (not yet multiplied by 2 for order).

    For a linear node with k children of sizes s1..sk:
    Two intervals cross if [l1,r1] spans children a1..b1 and [l2,r2] spans a2..b2
    with a1 < a2 <= b1 < b2 (or symmetric). The intersection size is
    S[b1+1] - S[a2] where S is the prefix sum of sizes.

    We need intersection >= X.

    Fix b1 = j (0-indexed, j from 1 to k-2):
      a2 = j (same as b1's child index, 0-indexed)
      Actually, let's use 1-indexed children for clarity with prefix sums.

    With 1-indexed children and prefix sums S[0..k]:
      S[i] = s1 + s2 + ... + si

    Fix b1 = j (1-indexed, j from 2 to k-1):
      a2 ranges from a1+1 to j (must be > a1, <= b1=j)
      b2 ranges from j+1 to k (must be > b1=j)
      a1 ranges from 1 to a2-1

    Intersection = S[j] - S[a2-1]  (children a2 through j)
    Need S[j] - S[a2-1] >= X  =>  S[a2-1] <= S[j] - X

    Let m = a2-1. Then m ranges from 1 to j-1, and a1 ranges from 1 to m.
    So for each valid m, the number of (a1, b2) pairs = m * (k - j).

    Total for this j = (k - j) * sum_{m=1}^{M} m  where M is the largest m
    such that S[m] <= S[j] - X.

    = (k - j) * M*(M+1)//2
    """
    k = len(children_sizes)
    if k < 3:
        return 0

    # Prefix sums
    S = [0] * (k + 1)
    for i in range(k):
        S[i + 1] = S[i] + children_sizes[i]

    contrib = 0
    for j in range(2, k):
        target = S[j] - X
        if target < S[1]:
            continue
        M = bisect_right(S, target, 1, j) - 1
        if M >= 1:
            contrib = (contrib + (k - j) * M * (M + 1) // 2) % MOD

    return contrib


def solve():
    line1 = input().split()
    N = int(line1[0])
    X = int(line1[1])
    p = list(map(int, input().split()))

    if N <= 2:
        return 0

    answer = 0

    # Stack entries: [min_val, max_val, size, node_type, children_sizes]
    # children_sizes is a list of ints for unfinalized linear nodes, None otherwise.
    # Using lists (mutable) instead of tuples for efficiency.
    stack = []

    # Cumulative sizes for pruning
    cum_size = []

    for i in range(N):
        # Current entry: a new leaf
        entry = [p[i], p[i], 1, LEAF, None]

        while stack:
            c_min = entry[0]
            c_max = entry[1]
            c_len = entry[2]
            merged = False

            depth = len(stack) - 1
            while depth >= 0:
                se = stack[depth]
                if se[0] < c_min:
                    c_min = se[0]
                if se[1] > c_max:
                    c_max = se[1]
                c_len += se[2]
                gap = (c_max - c_min + 1) - c_len

                if gap == 0:
                    # Merge: stack[depth:] + entry form a consecutive interval
                    popped = stack[depth:]
                    del stack[depth:]
                    del cum_size[depth:]
                    children = popped + [entry]
                    num_ch = len(children)

                    # Determine type
                    is_asc = True
                    is_desc = True
                    for ci in range(num_ch - 1):
                        c1 = children[ci]
                        c2 = children[ci + 1]
                        if c1[1] + 1 != c2[0]:
                            is_asc = False
                        if c1[0] - 1 != c2[1]:
                            is_desc = False

                    if is_asc:
                        ntype = ASC
                    elif is_desc:
                        ntype = DESC
                    else:
                        ntype = PRIME

                    if ntype == PRIME:
                        # Finalize any unfinalized linear children
                        for ch in children:
                            if ch[4] is not None:
                                answer = (answer + count_crossing(ch[4], X)) % MOD
                        entry = [c_min, c_max, c_len, PRIME, None]
                    else:
                        # Linear node (ASC or DESC)
                        # Build children_sizes by absorbing same-type, finalizing others
                        #
                        # Optimization: find the first same-type child with a
                        # children_sizes list; reuse that list and extend it.
                        # This avoids creating new lists and achieves O(N) total work
                        # for cases like identity permutation.

                        # Find a same-type child with the largest children_sizes
                        # to reuse, but we must maintain order.
                        # Strategy: iterate left to right. For the first same-type
                        # child with children_sizes, reuse its list. For everything
                        # before it, prepend. For everything after, append.

                        # Actually simpler: check if the leftmost child is same-type
                        # with a list. If so, reuse it. Otherwise create new.

                        # Even simpler for the common case (2 children: big linear
                        # node on left + leaf on right): leftmost child IS same-type
                        # with a list. Just append the leaf's size.

                        reuse_idx = -1
                        for ci in range(num_ch):
                            ch = children[ci]
                            if ch[3] == ntype and ch[4] is not None:
                                reuse_idx = ci
                                break  # take the first one (leftmost)

                        if reuse_idx >= 0:
                            # Reuse this list. Process elements before and after.
                            new_sizes = children[reuse_idx][4]

                            # Elements before reuse_idx: need to prepend
                            prefix = []
                            for ci in range(reuse_idx):
                                ch = children[ci]
                                if ch[3] == ntype and ch[4] is not None:
                                    # same-type linear child (shouldn't happen
                                    # since we took the first one, but just in case)
                                    prefix.extend(ch[4])
                                else:
                                    if ch[4] is not None:
                                        answer = (answer + count_crossing(ch[4], X)) % MOD
                                    prefix.append(ch[2])

                            if prefix:
                                # Prepend is expensive but rare for multi-way merges
                                # with the reuse not at index 0
                                prefix.extend(new_sizes)
                                new_sizes = prefix

                            # Elements after reuse_idx: append
                            for ci in range(reuse_idx + 1, num_ch):
                                ch = children[ci]
                                if ch[3] == ntype and ch[4] is not None:
                                    new_sizes.extend(ch[4])
                                else:
                                    if ch[4] is not None:
                                        answer = (answer + count_crossing(ch[4], X)) % MOD
                                    new_sizes.append(ch[2])

                            entry = [c_min, c_max, c_len, ntype, new_sizes]
                        else:
                            # No same-type child with a list; build from scratch
                            new_sizes = []
                            for ch in children:
                                if ch[4] is not None:
                                    # Different-type linear child: finalize it
                                    answer = (answer + count_crossing(ch[4], X)) % MOD
                                new_sizes.append(ch[2])
                            entry = [c_min, c_max, c_len, ntype, new_sizes]

                    merged = True
                    break

                # Pruning: check if enough elements remain below depth
                if depth > 0:
                    remaining = cum_size[depth - 1]
                else:
                    remaining = 0
                if gap > remaining:
                    break

                depth -= 1

            if not merged:
                break

        if cum_size:
            cum_size.append(cum_size[-1] + entry[2])
        else:
            cum_size.append(entry[2])
        stack.append(entry)

    # Finalize any remaining unfinalized linear nodes on stack
    for se in stack:
        if se[4] is not None:
            answer = (answer + count_crossing(se[4], X)) % MOD

    # Multiply by 2 for ordered pairs (each unordered crossing pair counted once,
    # but we need ordered 4-tuples (l1,r1,l2,r2) and (l2,r2,l1,r1))
    answer = (answer * 2) % MOD
    return answer


T = int(input())
for test_case in range(1, T + 1):
    print(solve())
