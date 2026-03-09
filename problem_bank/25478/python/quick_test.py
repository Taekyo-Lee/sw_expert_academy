"""Quick targeted stress test - runs faster by testing one case at a time in-process."""
import sys
import os
import random
from itertools import permutations, combinations
from collections import defaultdict

MOD = 10**9 + 7

def brute_force(N, X, D, A):
    """Direct brute force computation."""
    count = 0
    for positions in combinations(range(1, X + 1), N):
        for perm in permutations(range(N)):
            valid = True
            for i in range(N):
                if not valid:
                    break
                for j in range(i + 1, N):
                    ri = perm[i]
                    rj = perm[j]
                    dist = abs(positions[i] - positions[j])
                    if dist <= D:
                        if A[ri][rj] != 1:
                            valid = False
                            break
                    else:
                        if A[ri][rj] != 0:
                            valid = False
                            break
            if valid:
                count += 1
    return count % MOD

# Copy all the functions from solution_3 directly
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
    ordering = []
    visited = [False] * n
    priority = [0] * n
    for i, v in enumerate(prev_order):
        priority[v] = i
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
            if neighbors:
                new_partitions.append(neighbors)
            if non_neighbors:
                new_partitions.append(non_neighbors)
        partitions = new_partitions
    return ordering

def find_proper_interval_ordering(comp, A_full):
    n = len(comp)
    if n == 1:
        return [0]
    adj = [[] for _ in range(n)]
    deg = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and A_full[comp[i]][comp[j]] == 1:
                adj[i].append(j)
                deg[i] += 1
    start = min(range(n), key=lambda x: (deg[x], x))
    sigma1 = lbfs(adj, n, start)
    sigma2 = lbfs_plus(adj, n, sigma1[-1], sigma1)
    return sigma2

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

def check_bandwidth(sigma, A_local, D, n):
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
    for p in range(n):
        u = sigma[p]
        v = sigma[n - 1 - p]
        if u != v:
            for j in range(n):
                if A_local[u][j] != A_local[v][j]:
                    return False
    return True

def solve_component(comp, D, A_full):
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

def fast_solve(N, X, D, A):
    if N == 1:
        return X % MOD
    components = find_components(N, A)
    K = len(components)
    comp_spans = []
    for comp in components:
        g = solve_component(comp, D, A)
        if not g:
            return 0
        comp_spans.append(g)
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
    return answer

def gen_random_proper_interval_graph(N, D, X_max=100):
    positions = random.sample(range(1, X_max + 1), N)
    positions.sort()
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i+1, N):
            if abs(positions[i] - positions[j]) <= D:
                A[i][j] = 1
                A[j][i] = 1
    return A

def gen_random_matrix(N):
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i+1, N):
            v = random.randint(0, 1)
            A[i][j] = v
            A[j][i] = v
    return A

count = 0
mismatches = 0

for trial in range(5000):
    N = random.randint(2, 8)
    X = random.randint(N, min(N + 15, 25))
    D = random.randint(1, 8)

    if random.random() < 0.5:
        A = gen_random_proper_interval_graph(N, D, X)
    else:
        A = gen_random_matrix(N)

    fast = fast_solve(N, X, D, A)
    brute = brute_force(N, X, D, A)

    count += 1
    if fast != brute:
        mismatches += 1
        print(f"MISMATCH #{mismatches}: N={N} X={X} D={D} fast={fast} brute={brute}")
        for row in A:
            print(f"  {''.join(str(x) for x in row)}")

    if count % 1000 == 0:
        print(f"  {count} tests, {mismatches} mismatches so far...")

print(f"\nDone: {count} tests, {mismatches} mismatches")
