from bisect import bisect_right

MOD = 998244353

LEAF = 0
ASC = 1
DESC = 2
PRIME = 3


def solve():
    line1 = input().split()
    N = int(line1[0])
    X = int(line1[1])
    p = list(map(int, input().split()))

    if N <= 2:
        return 0

    # Node pool: each node is [min_val, max_val, size, type, children_indices]
    pool_min = []
    pool_max = []
    pool_size = []
    pool_type = []
    pool_children = []

    def new_leaf(val):
        idx = len(pool_min)
        pool_min.append(val)
        pool_max.append(val)
        pool_size.append(1)
        pool_type.append(LEAF)
        pool_children.append(None)
        return idx

    def new_node(mn, mx, sz, ntype, child_indices):
        idx = len(pool_min)
        pool_min.append(mn)
        pool_max.append(mx)
        pool_size.append(sz)
        pool_type.append(ntype)
        pool_children.append(child_indices)
        return idx

    stack = []  # stack of node indices
    # Maintain cumulative size of stack entries for pruning
    stack_cum_size = []  # stack_cum_size[i] = sum of pool_size for stack[0..i]

    for i in range(N):
        node_idx = new_leaf(p[i])

        while stack:
            c_min = pool_min[node_idx]
            c_max = pool_max[node_idx]
            c_len = pool_size[node_idx]
            merged = False

            depth = len(stack) - 1
            while depth >= 0:
                si = stack[depth]
                if pool_min[si] < c_min:
                    c_min = pool_min[si]
                if pool_max[si] > c_max:
                    c_max = pool_max[si]
                c_len += pool_size[si]
                gap = (c_max - c_min + 1) - c_len

                if gap == 0:
                    popped = stack[depth:]
                    del stack[depth:]
                    del stack_cum_size[depth:]
                    child_nodes = popped + [node_idx]

                    # Determine type
                    is_asc = True
                    is_desc = True
                    for ci in range(len(child_nodes) - 1):
                        c1 = child_nodes[ci]
                        c2 = child_nodes[ci + 1]
                        if pool_max[c1] + 1 != pool_min[c2]:
                            is_asc = False
                        if pool_min[c1] - 1 != pool_max[c2]:
                            is_desc = False

                    if is_asc:
                        ntype = ASC
                    elif is_desc:
                        ntype = DESC
                    else:
                        ntype = PRIME

                    # Flatten same-type linear children
                    if ntype == ASC or ntype == DESC:
                        flat_children = []
                        for ci2 in child_nodes:
                            if pool_type[ci2] == ntype:
                                flat_children.extend(pool_children[ci2])
                            else:
                                flat_children.append(ci2)
                        node_idx = new_node(c_min, c_max, c_len, ntype, flat_children)
                    else:
                        node_idx = new_node(c_min, c_max, c_len, ntype, child_nodes)

                    merged = True
                    break

                # Pruning: remaining capacity below depth
                if depth > 0:
                    remaining = stack_cum_size[depth - 1]
                else:
                    remaining = 0
                if gap > remaining:
                    break

                depth -= 1

            if not merged:
                break

        if stack_cum_size:
            stack_cum_size.append(stack_cum_size[-1] + pool_size[node_idx])
        else:
            stack_cum_size.append(pool_size[node_idx])
        stack.append(node_idx)

    # Traverse the tree and count crossing pairs for all linear nodes.
    answer = 0

    visit_stack = list(stack)

    while visit_stack:
        ni = visit_stack.pop()
        ntype = pool_type[ni]

        if ntype == LEAF:
            continue

        children = pool_children[ni]

        # Add children to visit stack
        for ci3 in children:
            visit_stack.append(ci3)

        if ntype == ASC or ntype == DESC:
            k = len(children)
            if k < 3:
                continue

            # Compute prefix sums of children sizes
            S = [0] * (k + 1)
            for j in range(k):
                S[j + 1] = S[j] + pool_size[children[j]]

            # Count crossing pairs.
            # Fix b1 = j (1-indexed, j from 2 to k-1):
            #   a2-1 = m ranges from 1 to j-1, need S[m] <= S[j] - X.
            #   Contribution = (k - j) * M*(M+1)//2 where M = largest valid m.
            for j in range(2, k):
                target = S[j] - X
                if target < S[1]:
                    continue
                M = bisect_right(S, target, 1, j) - 1
                if M >= 1:
                    answer = (answer + (k - j) * M * (M + 1) // 2) % MOD

    answer = (answer * 2) % MOD
    return answer


T = int(input())
for test_case in range(1, T + 1):
    print(solve())
