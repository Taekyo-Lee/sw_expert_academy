import io
import os
from collections import deque

_input_data = io.BytesIO(os.read(0, 32 * 1024 * 1024))
def _readline():
    return _input_data.readline()

def solve():
    INF = 10**18

    TC = int(_readline())
    out_parts = []

    for tc in range(1, TC + 1):
        N, M = map(int, _readline().split())
        edges = []
        for _ in range(M):
            line = _readline().split()
            u = int(line[0])
            v = int(line[1])
            w = int(line[2])
            edges.append((w, u, v))

        Q = int(_readline())
        queries = []
        for _ in range(Q):
            line = _readline().split()
            x = int(line[0])
            y = int(line[1])
            queries.append((x, y))

        # Sort edges by weight
        edges.sort()

        # Kruskal Reconstruction Tree
        # Nodes 0..N-1 are leaves. Internal nodes start from N.
        # Total nodes up to 2*N - 1 (at most N-1 merges).

        max_nodes = 2 * N
        parent_uf = list(range(N))  # Union-Find parent
        rank_uf = [0] * N           # Union-Find rank

        # Per-component info (indexed by UF root)
        comp_is_path = [True] * N     # Single vertex is a path
        # endpoints stored as flat arrays for speed
        comp_ep0 = list(range(N))
        comp_ep1 = list(range(N))
        comp_kruskal = list(range(N))  # kruskal tree node for this component

        # Kruskal tree
        kruskal_weight = [0] * max_nodes     # weight of internal node
        kruskal_left = [-1] * max_nodes
        kruskal_right = [-1] * max_nodes
        kruskal_parent = [-1] * max_nodes
        subtree_min_np = [INF] * max_nodes    # min non-path event weight in subtree

        next_node = N  # next internal node ID

        def find(x):
            while parent_uf[x] != x:
                parent_uf[x] = parent_uf[parent_uf[x]]
                x = parent_uf[x]
            return x

        for w, u, v in edges:
            ru = find(u)
            rv = find(v)

            if ru == rv:
                # Same component - non-tree edge (cycle) -> non-path event
                knode = comp_kruskal[ru]
                if w < subtree_min_np[knode]:
                    subtree_min_np[knode] = w
                comp_is_path[ru] = False
            else:
                # Different components - merge
                new_node = next_node
                next_node += 1

                knode_u = comp_kruskal[ru]
                knode_v = comp_kruskal[rv]

                kruskal_weight[new_node] = w
                kruskal_left[new_node] = knode_u
                kruskal_right[new_node] = knode_v
                kruskal_parent[knode_u] = new_node
                kruskal_parent[knode_v] = new_node

                # Propagate subtree_min_np from children
                mn = subtree_min_np[knode_u]
                if subtree_min_np[knode_v] < mn:
                    mn = subtree_min_np[knode_v]
                subtree_min_np[new_node] = mn

                # Check if merged component is still a path
                merged_is_path = False
                new_ep0 = 0
                new_ep1 = 0

                if comp_is_path[ru] and comp_is_path[rv]:
                    eu0 = comp_ep0[ru]
                    eu1 = comp_ep1[ru]
                    ev0 = comp_ep0[rv]
                    ev1 = comp_ep1[rv]

                    u_is_ep = (u == eu0 or u == eu1)
                    v_is_ep = (v == ev0 or v == ev1)

                    if u_is_ep and v_is_ep:
                        merged_is_path = True
                        new_ep0 = eu1 if u == eu0 else eu0
                        new_ep1 = ev1 if v == ev0 else ev0

                if not merged_is_path:
                    if w < subtree_min_np[new_node]:
                        subtree_min_np[new_node] = w

                # Union by rank
                if rank_uf[ru] < rank_uf[rv]:
                    ru, rv = rv, ru
                parent_uf[rv] = ru
                if rank_uf[ru] == rank_uf[rv]:
                    rank_uf[ru] += 1

                comp_is_path[ru] = merged_is_path
                comp_ep0[ru] = new_ep0
                comp_ep1[ru] = new_ep1
                comp_kruskal[ru] = new_node

        total_nodes = next_node

        # Compute ans_weight top-down
        ans_weight = [INF] * total_nodes

        # Process internal nodes in reverse creation order (last created = root first)
        for node in range(total_nodes - 1, N - 1, -1):
            par = kruskal_parent[node]
            parent_ans = ans_weight[par] if par != -1 else INF

            smnp = subtree_min_np[node]
            if smnp < INF:
                self_ans = kruskal_weight[node] if kruskal_weight[node] > smnp else smnp
            else:
                self_ans = INF

            ans_weight[node] = self_ans if self_ans < parent_ans else parent_ans

        # For leaf nodes: inherit from parent
        for node in range(N):
            par = kruskal_parent[node]
            if par != -1:
                ans_weight[node] = ans_weight[par]

        # Build LCA with binary lifting
        LOG = 1
        while (1 << LOG) < total_nodes:
            LOG += 1

        depth = [0] * total_nodes
        up = [[0] * total_nodes for _ in range(LOG)]

        # BFS from roots
        queue = deque()
        visited = bytearray(total_nodes)

        for node in range(total_nodes):
            if kruskal_parent[node] == -1:
                visited[node] = 1
                queue.append(node)
                up[0][node] = node

        while queue:
            node = queue.popleft()
            d = depth[node] + 1
            left = kruskal_left[node]
            if left != -1 and not visited[left]:
                visited[left] = 1
                depth[left] = d
                up[0][left] = node
                queue.append(left)
            right = kruskal_right[node]
            if right != -1 and not visited[right]:
                visited[right] = 1
                depth[right] = d
                up[0][right] = node
                queue.append(right)

        # Build sparse table
        for k in range(1, LOG):
            up_k = up[k]
            up_km1 = up[k - 1]
            for v in range(total_nodes):
                up_k[v] = up_km1[up_km1[v]]

        # Answer queries
        results = []
        append = results.append
        for x, y in queries:
            a, b = x, y
            da, db = depth[a], depth[b]
            if da < db:
                a, b = b, a
                da, db = db, da
            diff = da - db
            for k in range(LOG):
                if (diff >> k) & 1:
                    a = up[k][a]
            if a == b:
                aw = ans_weight[a]
                if aw >= INF:
                    append('-1')
                else:
                    append(str(aw))
                continue
            for k in range(LOG - 1, -1, -1):
                if up[k][a] != up[k][b]:
                    a = up[k][a]
                    b = up[k][b]
            l = up[0][a]
            aw = ans_weight[l]
            if aw >= INF:
                append('-1')
            else:
                append(str(aw))

        out_parts.append(' '.join(results))

    print('\n'.join(out_parts))

solve()
