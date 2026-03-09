"""Generate worst-case test: guaranteed proper interval graphs, N=50, X=100, D=8."""
import random

def generate_guaranteed_proper_interval(N, D):
    """Generate a proper interval graph by using unit intervals.
    The ordering is 0,1,...,N-1 and vertices i,j are connected iff |i-j| <= k
    for some k <= D. This guarantees a valid proper interval graph."""
    # Use varying connectivity: each pair connected if |i-j| <= bandwidth
    # bandwidth between 1 and D
    bandwidth = random.randint(max(1, D - 2), D)

    A = [[0] * N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        for j in range(i + 1, N):
            if j - i <= bandwidth:
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

def main():
    T = 140
    lines = [str(T)]

    for tc in range(T):
        N = 50
        X = 100
        D = 8
        A = generate_guaranteed_proper_interval(N, D)
        lines.append("%d %d %d" % (N, X, D))
        for row in A:
            lines.append("".join(str(x) for x in row))

    print("\n".join(lines))

if __name__ == "__main__":
    main()
