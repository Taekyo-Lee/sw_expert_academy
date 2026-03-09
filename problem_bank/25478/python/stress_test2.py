"""
Stress test: compare solution_3.py (fast) vs brute_force.py (correct)
Focus on edge cases that might cause the 1/140 failure.
"""
import subprocess
import random
import sys
import os

SOLUTION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solution_3.py")
BRUTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brute_force.py")

def gen_random_proper_interval_graph(N, D, X_max=100):
    """Generate a random proper interval graph by placing receivers randomly."""
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
    """Generate a random symmetric matrix with 1s on diagonal."""
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i+1, N):
            v = random.randint(0, 1)
            A[i][j] = v
            A[j][i] = v
    return A

def gen_complete_graph(N):
    return [[1]*N for _ in range(N)]

def gen_path_graph(N):
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        if i+1 < N:
            A[i][i+1] = 1
            A[i+1][i] = 1
    return A

def gen_no_edges(N):
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
    return A

def gen_star(N):
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        if i > 0:
            A[0][i] = 1
            A[i][0] = 1
    return A

def format_input(cases):
    lines = [str(len(cases))]
    for N, X, D, A in cases:
        lines.append(f"{N} {X} {D}")
        for row in A:
            lines.append("".join(str(x) for x in row))
    return "\n".join(lines) + "\n"

def run_solution(script, inp, timeout=60):
    try:
        result = subprocess.run(
            ["python3", script],
            input=inp, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip().split("\n")
    except subprocess.TimeoutExpired:
        return None

def run_batch(cases, desc=""):
    inp = format_input(cases)
    fast = run_solution(SOLUTION, inp)
    brute = run_solution(BRUTE, inp, timeout=120)

    if fast is None or brute is None:
        print(f"  ERROR in batch ({desc}): fast={'FAIL' if fast is None else 'OK'} brute={'FAIL' if brute is None else 'OK'}")
        return 0, len(cases)  # return mismatches=0, skipped=len

    mismatches = 0
    for i in range(len(cases)):
        if i >= len(fast) or i >= len(brute):
            print(f"  Output length mismatch")
            continue
        if fast[i] != brute[i]:
            mismatches += 1
            N, X, D, A = cases[i]
            print(f"  MISMATCH ({desc}): N={N} X={X} D={D} fast={fast[i]} brute={brute[i]}")
            for row in A:
                print(f"    {''.join(str(x) for x in row)}")
    return mismatches, 0

total_tests = 0
total_mismatches = 0

# ============== Phase 1: N=1 ==============
cases = []
for X in [1, 2, 50, 100]:
    for D in [1, 4, 8]:
        cases.append((1, X, D, [[1]]))
m, _ = run_batch(cases, "N=1")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 1 (N=1): {len(cases)} tests, {m} mismatches")

# ============== Phase 2: N=2 ==============
cases = []
for X in range(2, 30):
    for D in range(1, 9):
        cases.append((2, X, D, [[1,1],[1,1]]))
        cases.append((2, X, D, [[1,0],[0,1]]))
m, _ = run_batch(cases, "N=2")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 2 (N=2): {len(cases)} tests, {m} mismatches")

# ============== Phase 3: N=X (maximum density) ==============
cases = []
for N in range(2, 12):
    X = N
    for D in range(1, min(9, X)):
        cases.append((N, X, D, gen_random_proper_interval_graph(N, D, X)))
        cases.append((N, X, D, gen_complete_graph(N)))
        cases.append((N, X, D, gen_no_edges(N)))
        cases.append((N, X, D, gen_path_graph(N)))
m, _ = run_batch(cases, "N=X")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 3 (N=X): {len(cases)} tests, {m} mismatches")

# ============== Phase 4: D=1 ==============
cases = []
for N in range(2, 10):
    for X in range(N, min(N+15, 22)):
        cases.append((N, X, 1, gen_random_proper_interval_graph(N, 1, X)))
        cases.append((N, X, 1, gen_path_graph(N)))
        cases.append((N, X, 1, gen_no_edges(N)))
m, _ = run_batch(cases, "D=1")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 4 (D=1): {len(cases)} tests, {m} mismatches")

# ============== Phase 5: D=8 ==============
cases = []
for N in range(2, 11):
    for X in range(N, min(N+12, 22)):
        cases.append((N, X, 8, gen_random_proper_interval_graph(N, 8, X)))
        cases.append((N, X, 8, gen_complete_graph(N)))
m, _ = run_batch(cases, "D=8")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 5 (D=8): {len(cases)} tests, {m} mismatches")

# ============== Phase 6: Star graphs ==============
cases = []
for N in range(3, 10):
    for X in range(N, min(N+10, 18)):
        for D in [1, 2, 4, 8]:
            cases.append((N, X, D, gen_star(N)))
m, _ = run_batch(cases, "star")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 6 (star): {len(cases)} tests, {m} mismatches")

# ============== Phase 7: All singletons ==============
cases = []
for N in range(2, 12):
    for X in range(N, min(N+15, 22)):
        for D in [1, 2, 4, 8]:
            cases.append((N, X, D, gen_no_edges(N)))
m, _ = run_batch(cases, "singletons")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 7 (singletons): {len(cases)} tests, {m} mismatches")

# ============== Phase 8: Random matrices (many) ==============
cases = []
for _ in range(500):
    N = random.randint(2, 8)
    X = random.randint(N, min(N+15, 22))
    D = random.randint(1, 8)
    cases.append((N, X, D, gen_random_matrix(N)))
m, _ = run_batch(cases, "random")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 8 (random): {len(cases)} tests, {m} mismatches")

# ============== Phase 9: Larger N (7-12) proper interval ==============
cases = []
for _ in range(200):
    N = random.randint(7, 11)
    X = random.randint(N, min(N+15, 25))
    D = random.randint(1, 8)
    cases.append((N, X, D, gen_random_proper_interval_graph(N, D, X)))
m, _ = run_batch(cases, "larger proper interval")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 9 (larger N proper interval): {len(cases)} tests, {m} mismatches")

# ============== Phase 10: Larger N random matrices ==============
cases = []
for _ in range(200):
    N = random.randint(7, 10)
    X = random.randint(N, min(N+12, 22))
    D = random.randint(1, 8)
    cases.append((N, X, D, gen_random_matrix(N)))
m, _ = run_batch(cases, "larger random")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 10 (larger random): {len(cases)} tests, {m} mismatches")

# ============== Phase 11: Mixed components ==============
cases = []
for _ in range(300):
    N = random.randint(3, 10)
    X = random.randint(N, min(N+15, 22))
    D = random.randint(1, 8)
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
    nodes = list(range(N))
    random.shuffle(nodes)
    num_comp = random.randint(2, min(4, N))
    splits = sorted(random.sample(range(1, N), num_comp - 1))
    comps = []
    prev = 0
    for s in splits:
        comps.append(nodes[prev:s])
        prev = s
    comps.append(nodes[prev:])
    for comp in comps:
        if len(comp) <= 1:
            continue
        positions = sorted(random.sample(range(1, 30), len(comp)))
        for i in range(len(comp)):
            for j in range(i+1, len(comp)):
                if abs(positions[i] - positions[j]) <= D:
                    A[comp[i]][comp[j]] = 1
                    A[comp[j]][comp[i]] = 1
    cases.append((N, X, D, A))
m, _ = run_batch(cases, "mixed comp")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 11 (mixed comp): {len(cases)} tests, {m} mismatches")

# ============== Phase 12: X=100 with various N ==============
cases = []
for N in range(2, 12):
    for D in range(1, 9):
        cases.append((N, 100, D, gen_random_proper_interval_graph(N, D, 100)))
        cases.append((N, 100, D, gen_complete_graph(N)))
        cases.append((N, 100, D, gen_no_edges(N)))
m, _ = run_batch(cases, "X=100")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 12 (X=100): {len(cases)} tests, {m} mismatches")

# ============== Phase 13: Complete bipartite-like subgraphs ==============
# K_{a,b} subgraphs - these are NOT proper interval for a,b >= 2
# but let's test them
cases = []
for a in range(1, 5):
    for b in range(a, 5):
        N = a + b
        if N > 10:
            continue
        A = [[0]*N for _ in range(N)]
        for i in range(N):
            A[i][i] = 1
        for i in range(a):
            for j in range(a, N):
                A[i][j] = 1
                A[j][i] = 1
        for X in range(N, min(N+10, 22)):
            for D in [1, 2, 4, 8]:
                cases.append((N, X, D, A))
m, _ = run_batch(cases, "bipartite")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 13 (bipartite): {len(cases)} tests, {m} mismatches")

# ============== Phase 14: Graphs where N is large and X is large ==============
# Brute force is too slow for large N, but let's try moderate sizes with X up to 50
cases = []
for _ in range(100):
    N = random.randint(2, 7)
    X = random.randint(max(N, 20), 50)
    D = random.randint(1, 8)
    cases.append((N, X, D, gen_random_proper_interval_graph(N, D, X)))
    cases.append((N, X, D, gen_random_matrix(N)))
m, _ = run_batch(cases, "large X")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 14 (large X): {len(cases)} tests, {m} mismatches")

# ============== Phase 15: Specific edge cases: single large component ==============
cases = []
for _ in range(200):
    N = random.randint(3, 9)
    X = random.randint(N, min(N+15, 22))
    D = random.randint(1, 8)
    # Generate a connected proper interval graph
    # Place receivers close together to ensure connectivity
    positions = sorted(random.sample(range(1, min(N*D+1, 100)), N))
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i+1, N):
            if abs(positions[i] - positions[j]) <= D:
                A[i][j] = 1
                A[j][i] = 1
    cases.append((N, X, D, A))
m, _ = run_batch(cases, "connected")
total_tests += len(cases)
total_mismatches += m
print(f"Phase 15 (connected): {len(cases)} tests, {m} mismatches")

print(f"\n=== TOTAL: {total_tests} tests, {total_mismatches} mismatches ===")
