"""Generate varied worst-case test inputs with diverse graph structures."""
import random

def generate_proper_interval_graph(N, D):
    """Generate a random proper interval graph with N vertices.
    Vertices have intervals of varying but similar sizes, placed on a line."""
    # Generate random proper interval model
    # Each vertex i has an interval [center_i - radius, center_i + radius]
    # For proper interval graphs, all intervals have the same length
    # Two vertices are adjacent iff their intervals overlap

    # Place centers at random positions, with interval half-length = D/2
    # To get interesting structure, space them out
    half_len = D  # interval half-length in "position units"
    centers = sorted(random.sample(range(1, N * 3), N))

    A = [[0] * N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i + 1, N):
            if abs(centers[i] - centers[j]) <= 2 * half_len:
                A[i][j] = 1
                A[j][i] = 1

    # Randomly permute vertex labels
    perm = list(range(N))
    random.shuffle(perm)
    A_perm = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            A_perm[perm[i]][perm[j]] = A[i][j]

    return A_perm

def generate_multi_component(N, D):
    """Generate graph with multiple components."""
    # Split N into 2-4 components
    num_comp = random.randint(2, min(4, N))
    sizes = []
    remaining = N
    for c in range(num_comp - 1):
        sz = random.randint(1, max(1, remaining - (num_comp - c - 1)))
        sizes.append(sz)
        remaining -= sz
    sizes.append(remaining)

    A = [[0] * N for _ in range(N)]
    offset = 0
    for sz in sizes:
        # Each component: full clique or path-like
        for i in range(offset, offset + sz):
            A[i][i] = 1
            for j in range(i + 1, offset + sz):
                if j - i <= min(D, sz - 1):
                    A[i][j] = 1
                    A[j][i] = 1
        offset += sz

    # Randomly permute vertex labels
    perm = list(range(N))
    random.shuffle(perm)
    A_perm = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            A_perm[perm[i]][perm[j]] = A[i][j]

    return A_perm

def main():
    T = 140
    lines = [str(T)]

    for tc in range(T):
        N = random.randint(30, 50)
        X = random.randint(N, 100)
        D = random.randint(4, 8)

        if tc % 3 == 0:
            A = generate_multi_component(N, D)
        else:
            A = generate_proper_interval_graph(N, D)

        lines.append("%d %d %d" % (N, X, D))
        for row in A:
            lines.append("".join(str(x) for x in row))

    print("\n".join(lines))

if __name__ == "__main__":
    main()
