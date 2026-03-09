"""Generate worst-case test input: N=50, X=100, D=8, 140 test cases.
The graph is a single connected component where all receivers within distance D
in the proper interval ordering are connected (a "path-like" proper interval graph).
"""
import random

def generate_worst_case(N, X, D):
    """Generate a proper interval graph with N vertices, max connectivity within D."""
    # Create a proper interval ordering: vertex i is at position i
    # Connect i and j if |i - j| <= D
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i + 1, N):
            if j - i <= D:
                A[i][j] = 1
                A[j][i] = 1
    return A

def main():
    N = 50
    X = 100
    D = 8
    T = 140

    lines = [str(T)]
    # Generate a few different graph structures
    for tc in range(T):
        A = generate_worst_case(N, X, D)
        # Randomly permute vertex labels to make it harder
        perm = list(range(N))
        random.shuffle(perm)
        A_perm = [[0] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                A_perm[perm[i]][perm[j]] = A[i][j]

        lines.append("%d %d %d" % (N, X, D))
        for row in A_perm:
            lines.append("".join(str(x) for x in row))

    print("\n".join(lines))

if __name__ == "__main__":
    main()
