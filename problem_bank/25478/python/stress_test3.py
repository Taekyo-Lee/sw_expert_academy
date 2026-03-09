"""
Targeted stress test for problem 25478, solution_3.py vs brute_force.py.
Focus on edge cases that random testing might miss.
"""
import subprocess
import random
import sys
import os
import itertools

SOLUTION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solution_3.py")
BRUTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brute_force.py")

def format_input(cases):
    lines = [str(len(cases))]
    for N, X, D, A in cases:
        lines.append(f"{N} {X} {D}")
        for row in A:
            lines.append("".join(str(x) for x in row))
    return "\n".join(lines) + "\n"

def run_solution(script, inp, timeout=120):
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

def run_batch(cases, desc="", timeout_sol=60, timeout_brute=120):
    if not cases:
        return 0, 0
    inp = format_input(cases)
    fast = run_solution(SOLUTION, inp, timeout=timeout_sol)
    brute = run_solution(BRUTE, inp, timeout=timeout_brute)

    if fast is None or brute is None:
        print(f"  TIMEOUT/ERROR in batch ({desc}): fast={'FAIL' if fast is None else 'OK'} brute={'FAIL' if brute is None else 'OK'}")
        return 0, len(cases)

    mismatches = 0
    for i in range(len(cases)):
        if i >= len(fast) or i >= len(brute):
            print(f"  Output length mismatch in {desc}")
            continue
        if fast[i] != brute[i]:
            mismatches += 1
            N, X, D, A = cases[i]
            print(f"  MISMATCH ({desc}): N={N} X={X} D={D} fast={fast[i]} brute={brute[i]}")
            for row in A:
                print(f"    {''.join(str(x) for x in row)}")
    return mismatches, 0

# ============== Helper generators ==============

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

def gen_proper_interval_from_positions(positions, D):
    """Generate proper interval graph from sorted positions and distance D."""
    N = len(positions)
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i+1, N):
            if abs(positions[i] - positions[j]) <= D:
                A[i][j] = 1
                A[j][i] = 1
    return A

def gen_random_proper_interval_graph(N, D, X_max=100):
    positions = sorted(random.sample(range(1, X_max + 1), N))
    return gen_proper_interval_from_positions(positions, D)

def gen_proper_interval_with_twins(N, D, twin_class_sizes):
    """Generate a proper interval graph with specific twin class structure.
    twin_class_sizes: list of sizes that sum to N.
    Twins must be consecutive and within distance D of each other,
    and have identical neighborhoods.
    """
    assert sum(twin_class_sizes) == N
    # Place twin classes with specific spacing
    positions = []
    pos = 1
    for sz in twin_class_sizes:
        # Place sz vertices at consecutive positions (gap = 1 between them)
        for k in range(sz):
            positions.append(pos + k)
        pos += sz + D  # Next class starts D+1 after last vertex of this class
    return gen_proper_interval_from_positions(positions, D)

def gen_caterpillar(N, D):
    """Generate a caterpillar interval graph: path spine with extra neighbors."""
    if N <= 2:
        return gen_complete_graph(N) if N > 0 else [[1]]
    # Spine of length ceil(N/2), with extra vertices hanging off
    spine_len = (N + 1) // 2
    extra = N - spine_len
    positions = []
    pos = 1
    for i in range(spine_len):
        positions.append(pos)
        pos += D  # spine vertices are exactly D apart
    # Add extra vertices close to spine vertices
    for i in range(extra):
        target = positions[i % spine_len]
        offset = random.randint(1, max(1, D - 1))
        new_pos = target + offset
        if new_pos not in positions:
            positions.append(new_pos)
        else:
            # Try other offsets
            for off in range(1, D+1):
                new_pos = target + off
                if new_pos not in positions:
                    positions.append(new_pos)
                    break
            else:
                positions.append(target + D + 1)
    positions.sort()
    positions = positions[:N]  # Ensure exactly N
    return gen_proper_interval_from_positions(positions, D)

def gen_clique_plus_isolated(clique_size, num_isolated, D):
    """Clique of given size plus isolated vertices."""
    N = clique_size + num_isolated
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
    for i in range(clique_size):
        for j in range(i+1, clique_size):
            A[i][j] = 1
            A[j][i] = 1
    return A

def gen_two_cliques(size1, size2, D, connected=False):
    """Two cliques, possibly connected by an edge."""
    N = size1 + size2
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
    # First clique
    for i in range(size1):
        for j in range(i+1, size1):
            A[i][j] = 1
            A[j][i] = 1
    # Second clique
    for i in range(size1, N):
        for j in range(i+1, N):
            A[i][j] = 1
            A[j][i] = 1
    # Connect them
    if connected:
        A[size1-1][size1] = 1
        A[size1][size1-1] = 1
    return A

def gen_all_twins(N, D):
    """All vertices are twins (complete graph)."""
    return gen_complete_graph(N)

def gen_no_twins(N, D):
    """Proper interval graph with no twin vertices."""
    # Path graph has no twins (except endpoints might be twins for N <= 3)
    # Use positions 1, 2, ..., N with D=1 to get a path
    # For general D, use positions 1, 2, ..., N (each pair within D)
    # Actually, for a no-twin graph, we need each vertex to have a unique neighborhood
    # A path with D=1 achieves this for N >= 4
    if N <= 3 and D >= N-1:
        # Complete graph, all twins
        return gen_complete_graph(N)
    # Use positions spaced to create unique neighborhoods
    positions = list(range(1, N+1))
    return gen_proper_interval_from_positions(positions, D)

def shuffle_vertices(A):
    """Randomly permute vertex labels."""
    N = len(A)
    perm = list(range(N))
    random.shuffle(perm)
    B = [[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            B[perm[i]][perm[j]] = A[i][j]
    return B

total_tests = 0
total_mismatches = 0
total_skipped = 0

# ============== Phase 1: Complete graphs K_n for n=2..15 ==============
print("Phase 1: Complete graphs K_n")
cases = []
for N in range(2, 14):
    for D in range(1, 9):
        for X in [N, N+1, N+D, N+2*D, min(N+20, 100)]:
            if X >= N:
                cases.append((N, X, D, gen_complete_graph(N)))
m, s = run_batch(cases, "complete K_n")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 2: Path graphs P_n for n=2..13 ==============
print("Phase 2: Path graphs P_n")
cases = []
for N in range(2, 12):
    for D in range(1, 9):
        for X in [N, N+1, N+D, min(N+15, 100)]:
            if X >= N:
                cases.append((N, X, D, gen_path_graph(N)))
m, s = run_batch(cases, "path P_n")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 3: Twin class structures ==============
print("Phase 3: Twin class structures")
cases = []
# Twin classes of size > 2
for D in range(1, 9):
    # One big twin class
    for N in range(3, 10):
        X_vals = [N, N+D, min(N+10, 100)]
        for X in X_vals:
            if X >= N:
                # All twins = complete graph (already tested)
                cases.append((N, X, D, gen_complete_graph(N)))

    # Two twin classes
    for s1 in range(2, 6):
        for s2 in range(2, 6):
            N = s1 + s2
            if N > 12:
                continue
            A = gen_proper_interval_with_twins(N, D, [s1, s2])
            for X in [N, N+D, min(N+10, 50)]:
                if X >= N:
                    cases.append((N, X, D, A))
                    cases.append((N, X, D, shuffle_vertices(A)))

    # Three twin classes
    for s1 in range(2, 4):
        for s2 in range(2, 4):
            for s3 in range(2, 4):
                N = s1 + s2 + s3
                if N > 12:
                    continue
                A = gen_proper_interval_with_twins(N, D, [s1, s2, s3])
                for X in [N, N+D, min(N+10, 50)]:
                    if X >= N:
                        cases.append((N, X, D, A))

    # One twin class of 3 + singletons
    for extra in range(0, 4):
        N = 3 + extra
        classes = [3] + [1]*extra
        if N > 12:
            continue
        A = gen_proper_interval_with_twins(N, D, classes)
        for X in [N, N+D, min(N+10, 50)]:
            if X >= N:
                cases.append((N, X, D, A))

m, s = run_batch(cases, "twin classes")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 4: D=1 comprehensive ==============
print("Phase 4: D=1 comprehensive")
cases = []
for N in range(2, 12):
    for X in range(N, min(N+20, 30)):
        # Path graph with D=1
        cases.append((N, X, 1, gen_path_graph(N)))
        # All singletons with D=1
        cases.append((N, X, 1, gen_no_edges(N)))
        # Random proper interval with D=1
        if X >= N:
            A = gen_random_proper_interval_graph(N, 1, X)
            cases.append((N, X, 1, A))
m, s = run_batch(cases, "D=1")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 5: X=N (minimal space) ==============
print("Phase 5: X=N (minimal space)")
cases = []
for N in range(2, 13):
    X = N
    for D in range(1, 9):
        cases.append((N, X, D, gen_complete_graph(N)))
        cases.append((N, X, D, gen_path_graph(N)))
        cases.append((N, X, D, gen_no_edges(N)))
        if N <= 10:
            cases.append((N, X, D, gen_random_proper_interval_graph(N, D, max(X, N+5))))
m, s = run_batch(cases, "X=N")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 6: X very large (X=100) ==============
print("Phase 6: X=100 with small N")
cases = []
for N in range(2, 10):
    for D in range(1, 9):
        cases.append((N, 100, D, gen_complete_graph(N)))
        cases.append((N, 100, D, gen_path_graph(N)))
        cases.append((N, 100, D, gen_no_edges(N)))
m, s = run_batch(cases, "X=100")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 7: Caterpillar graphs ==============
print("Phase 7: Caterpillar interval graphs")
cases = []
for N in range(3, 11):
    for D in range(1, 5):
        for X in [N, N+D, min(N+10, 30)]:
            if X >= N:
                for _ in range(3):
                    A = gen_caterpillar(N, D)
                    cases.append((N, X, D, A))
m, s = run_batch(cases, "caterpillar")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 8: Two cliques (connected and disconnected) ==============
print("Phase 8: Two cliques")
cases = []
for s1 in range(2, 7):
    for s2 in range(2, 7):
        N = s1 + s2
        if N > 12:
            continue
        for D in range(1, 9):
            for X in [N, N+D+1, min(N+15, 30)]:
                if X >= N:
                    # Disconnected cliques
                    cases.append((N, X, D, gen_two_cliques(s1, s2, D, connected=False)))
                    # Connected cliques
                    cases.append((N, X, D, gen_two_cliques(s1, s2, D, connected=True)))
m, s = run_batch(cases, "two cliques")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 9: Clique + isolated ==============
print("Phase 9: Clique + isolated vertices")
cases = []
for clique_sz in range(2, 8):
    for num_iso in range(1, 5):
        N = clique_sz + num_iso
        if N > 12:
            continue
        A = gen_clique_plus_isolated(clique_sz, num_iso, 1)
        for D in range(1, 9):
            for X in [N, N+D+1, min(N+15, 30)]:
                if X >= N:
                    cases.append((N, X, D, A))
                    cases.append((N, X, D, shuffle_vertices(A)))
m, s = run_batch(cases, "clique+isolated")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 10: Specific bandwidth-D graphs ==============
print("Phase 10: Bandwidth exactly D graphs")
cases = []
for D in range(1, 9):
    # Create graph where max edge distance = D in the ordering
    for N in range(D+1, min(D+8, 13)):
        # Place receivers at positions 1, 2, ..., N
        # This gives edges between vertices within distance D
        positions = list(range(1, N+1))
        A = gen_proper_interval_from_positions(positions, D)
        for X in [N, N+1, N+D, min(N+10, 30)]:
            if X >= N:
                cases.append((N, X, D, A))
m, s = run_batch(cases, "bandwidth=D")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 11: Palindromic vs non-palindromic ==============
print("Phase 11: Palindromic detection edge cases")
cases = []
for D in range(1, 9):
    # Symmetric graph: positions 1, ..., N mirrored
    for N in range(2, 10):
        # Symmetric positions: 1, 2, ..., N
        positions = list(range(1, N+1))
        A = gen_proper_interval_from_positions(positions, D)
        for X in [N, N+D, min(N+15, 30)]:
            if X >= N:
                cases.append((N, X, D, A))

        # Asymmetric positions
        if N >= 3:
            positions = [1]
            for i in range(1, N):
                positions.append(positions[-1] + random.choice([1, D]))
            A = gen_proper_interval_from_positions(positions, D)
            for X in [max(N, positions[-1]), min(positions[-1]+10, 40)]:
                if X >= N:
                    cases.append((N, X, D, A))

m, s = run_batch(cases, "palindromic")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 12: Many small components ==============
print("Phase 12: Many small components")
cases = []
for K in range(2, 8):  # Number of components
    N = K  # All singletons
    for D in range(1, 9):
        for X in range(N, min(N + K*(D+1) + 5, 30)):
            cases.append((N, X, D, gen_no_edges(N)))

    # K components, each of size 2 (edges)
    N = 2 * K
    if N <= 12:
        for D in range(1, 9):
            A = [[0]*N for _ in range(N)]
            for i in range(N):
                A[i][i] = 1
            for k in range(K):
                A[2*k][2*k+1] = 1
                A[2*k+1][2*k] = 1
            for X in range(N, min(N + K*(D+1) + 5, 30)):
                cases.append((N, X, D, A))

m, s = run_batch(cases, "many components")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 13: Larger N (13-15) with brute force feasible structures ==============
print("Phase 13: Larger N (feasible with brute force for small X)")
cases = []
# For N=13-15, brute force is very slow unless X is small
# C(X, N) * N! is the brute force complexity
# For N=13, X=13: C(13,13) * 13! = 1 * 6.2e9 -- too slow
# For N=10, X=10: C(10,10) * 10! = 3.6e6 -- feasible
# For N=10, X=12: C(12,10) * 10! = 66 * 3.6e6 = 2.4e8 -- borderline
# So let's test N=7-10 with small X
for N in range(7, 11):
    for X in [N, N+1, N+2]:
        for D in range(1, 9):
            # Complete graph
            cases.append((N, X, D, gen_complete_graph(N)))
            # Path graph
            cases.append((N, X, D, gen_path_graph(N)))
            # Random proper interval
            A = gen_random_proper_interval_graph(N, D, max(N+5, X))
            cases.append((N, X, D, A))
            # Shuffled proper interval
            cases.append((N, X, D, shuffle_vertices(A)))

m, s = run_batch(cases, "larger N small X", timeout_brute=300)
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 14: Specific edge cases with twin factor ==============
print("Phase 14: Twin factor edge cases")
cases = []
# Graphs with large twin classes
for D in range(1, 5):
    # 4 twins in one class
    for N in [4, 5, 6]:
        if N == 4:
            classes = [4]
        elif N == 5:
            classes = [4, 1]
        elif N == 6:
            classes = [4, 2]
        A = gen_proper_interval_with_twins(N, D, classes)
        for X in [N, N+D, min(N+10, 25)]:
            if X >= N:
                cases.append((N, X, D, A))
                cases.append((N, X, D, shuffle_vertices(A)))

    # 5 twins in one class
    for extra in range(0, 3):
        N = 5 + extra
        classes = [5] + [1]*extra
        A = gen_proper_interval_with_twins(N, D, classes)
        for X in [N, N+D, min(N+10, 25)]:
            if X >= N:
                cases.append((N, X, D, A))

m, s = run_batch(cases, "twin factor")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 15: All proper interval graphs on 4-6 vertices ==============
print("Phase 15: Exhaustive proper interval graphs (small N)")
cases = []
# For N=4, enumerate all possible proper interval graph structures
# by trying all distinct position vectors
for N in range(4, 7):
    for D in range(1, 5):
        # Generate various position patterns
        seen = set()
        for positions in itertools.combinations(range(1, N*D + 5), N):
            A = gen_proper_interval_from_positions(list(positions), D)
            key = tuple(tuple(row) for row in A)
            if key in seen:
                continue
            seen.add(key)
            for X in [N, N+D, min(N+8, 25)]:
                if X >= N:
                    cases.append((N, X, D, A))
        if len(cases) > 3000:
            break
    if len(cases) > 3000:
        break

# Limit to 3000
if len(cases) > 3000:
    cases = cases[:3000]

m, s = run_batch(cases, "exhaustive small N")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 16: Specific asymmetric proper interval graphs ==============
print("Phase 16: Asymmetric proper interval graphs")
cases = []
for D in range(1, 9):
    # Positions with specific patterns that create asymmetry
    for N in range(3, 10):
        # All at distance 1 except last pair at distance D
        positions = list(range(1, N))
        positions.append(positions[-1] + D)
        A = gen_proper_interval_from_positions(positions, D)
        for X in [N, max(N, positions[-1]), min(positions[-1]+5, 30)]:
            if X >= N:
                cases.append((N, X, D, A))

        # First pair at distance D, rest at distance 1
        positions = [1, 1 + D]
        for i in range(2, N):
            positions.append(positions[-1] + 1)
        A = gen_proper_interval_from_positions(positions, D)
        for X in [N, max(N, positions[-1]), min(positions[-1]+5, 30)]:
            if X >= N:
                cases.append((N, X, D, A))

        # Alternating gaps: 1, D, 1, D, ...
        positions = [1]
        for i in range(1, N):
            if i % 2 == 1:
                positions.append(positions[-1] + D)
            else:
                positions.append(positions[-1] + 1)
        A = gen_proper_interval_from_positions(positions, D)
        for X in [N, max(N, positions[-1]), min(positions[-1]+5, 30)]:
            if X >= N:
                cases.append((N, X, D, A))

m, s = run_batch(cases, "asymmetric")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 17: Graphs where palindromic might be borderline ==============
print("Phase 17: Borderline palindromic cases")
cases = []
for D in range(1, 6):
    for N in range(3, 9):
        # Almost symmetric: positions are 1, 2, ..., N (symmetric adjacency)
        positions = list(range(1, N+1))
        A = gen_proper_interval_from_positions(positions, D)
        for X in range(N, min(N+10, 25)):
            cases.append((N, X, D, A))

        # Break symmetry: positions 1, 2, ..., N-1, N+1 (last vertex farther)
        if N >= 3:
            positions = list(range(1, N))
            positions.append(N + 1)
            A = gen_proper_interval_from_positions(positions, D)
            for X in range(max(N, positions[-1]), min(positions[-1]+5, 25)):
                cases.append((N, X, D, A))

m, s = run_batch(cases, "borderline palindromic")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 18: Graphs with many components of mixed sizes ==============
print("Phase 18: Mixed component sizes")
cases = []
for _ in range(200):
    # Random number of components with random sizes
    num_comp = random.randint(2, 5)
    comp_sizes = [random.randint(1, 4) for _ in range(num_comp)]
    N = sum(comp_sizes)
    if N > 12:
        continue
    D = random.randint(1, 8)
    X = random.randint(N, min(N + num_comp * (D+1) + 10, 30))

    # Build block-diagonal adjacency matrix
    A = [[0]*N for _ in range(N)]
    offset = 0
    for sz in comp_sizes:
        if sz == 1:
            A[offset][offset] = 1
        else:
            # Make a proper interval subgraph
            positions = sorted(random.sample(range(1, sz*D + 5), sz))
            subA = gen_proper_interval_from_positions(positions, D)
            for i in range(sz):
                for j in range(sz):
                    A[offset+i][offset+j] = subA[i][j]
        offset += sz

    # Shuffle vertices to test component finding
    A = shuffle_vertices(A)
    cases.append((N, X, D, A))

m, s = run_batch(cases, "mixed components")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 19: D=8 specific tests ==============
print("Phase 19: D=8 edge cases")
cases = []
for N in range(2, 12):
    D = 8
    # All vertices within distance 8 = complete graph
    positions = list(range(1, N+1))
    A = gen_proper_interval_from_positions(positions, D)
    for X in [N, N+1, N+8, min(N+20, 40)]:
        if X >= N:
            cases.append((N, X, D, A))

    # Vertices spaced exactly 8 apart = path graph
    positions = list(range(1, N*8+1, 8))
    A = gen_proper_interval_from_positions(positions, D)
    for X in [max(N, positions[-1]), min(positions[-1]+10, 100)]:
        if X >= N:
            cases.append((N, X, D, A))

    # Mixed: some close, some far
    positions = [1]
    for i in range(1, N):
        positions.append(positions[-1] + random.choice([1, 4, 8]))
    A = gen_proper_interval_from_positions(positions, D)
    for X in [max(N, positions[-1]), min(positions[-1]+10, 100)]:
        if X >= N:
            cases.append((N, X, D, A))

m, s = run_batch(cases, "D=8")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 20: Non-proper-interval graphs (answer should be 0 or computed) ==============
print("Phase 20: Non-proper-interval graphs")
cases = []
for N in range(3, 8):
    for D in range(1, 5):
        # Cycle graph C_n (not proper interval for n >= 4)
        A = [[0]*N for _ in range(N)]
        for i in range(N):
            A[i][i] = 1
            A[i][(i+1)%N] = 1
            A[(i+1)%N][i] = 1
        for X in [N, N+D, min(N+10, 25)]:
            if X >= N:
                cases.append((N, X, D, A))

m, s = run_batch(cases, "non-proper-interval")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 21: Graph where K_n minus one edge ==============
print("Phase 21: K_n minus edge")
cases = []
for N in range(3, 10):
    for D in range(1, 9):
        # Remove edge between first and last
        A = gen_complete_graph(N)
        A[0][N-1] = 0
        A[N-1][0] = 0
        for X in [N, N+D, min(N+10, 25)]:
            if X >= N:
                cases.append((N, X, D, A))
m, s = run_batch(cases, "K_n minus edge")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 22: Intensive random with larger range ==============
print("Phase 22: Intensive random")
cases = []
for _ in range(500):
    N = random.randint(2, 10)
    D = random.randint(1, 8)
    X = random.randint(N, min(N + 20, 50))
    A = gen_random_proper_interval_graph(N, D, max(X, N+5))
    cases.append((N, X, D, A))
    # Also test shuffled version
    cases.append((N, X, D, shuffle_vertices(A)))

m, s = run_batch(cases, "intensive random")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 23: Graphs with specific structure where forward != reverse ==============
print("Phase 23: Forward != reverse (asymmetric span distributions)")
cases = []
for D in range(2, 9):
    for N in range(3, 9):
        # Create asymmetric proper interval graph
        # First half dense, second half sparse
        positions = []
        pos = 1
        for i in range(N // 2):
            positions.append(pos)
            pos += 1
        for i in range(N // 2, N):
            positions.append(pos)
            pos += D
        A = gen_proper_interval_from_positions(positions, D)
        for X in [max(N, positions[-1]), min(positions[-1]+5, 30)]:
            if X >= N:
                cases.append((N, X, D, A))
                cases.append((N, X, D, shuffle_vertices(A)))

m, s = run_batch(cases, "asymmetric spans")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 24: Systematic check of all N,D,X combinations with K_n ==============
print("Phase 24: Systematic K_n over all parameter ranges")
cases = []
for N in range(2, 12):
    for D in range(1, 9):
        for X in range(N, min(2*N + 2*D + 5, 35)):
            cases.append((N, X, D, gen_complete_graph(N)))
m, s = run_batch(cases, "systematic K_n")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

# ============== Phase 25: Graphs with X=N+1 (one extra position) ==============
print("Phase 25: X=N+1")
cases = []
for N in range(2, 12):
    X = N + 1
    for D in range(1, 9):
        cases.append((N, X, D, gen_complete_graph(N)))
        cases.append((N, X, D, gen_path_graph(N)))
        cases.append((N, X, D, gen_no_edges(N)))
        A = gen_random_proper_interval_graph(N, D, max(X, N+5))
        cases.append((N, X, D, A))

m, s = run_batch(cases, "X=N+1")
total_tests += len(cases)
total_mismatches += m
total_skipped += s
print(f"  {len(cases)} tests, {m} mismatches, {s} skipped")

print(f"\n{'='*60}")
print(f"TOTAL: {total_tests} tests, {total_mismatches} mismatches, {total_skipped} skipped")
print(f"{'='*60}")
