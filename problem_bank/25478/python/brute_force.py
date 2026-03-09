from itertools import permutations, combinations

MOD = 10**9 + 7

def solve():
    T = int(input())
    for tc in range(1, T + 1):
        line = input().split()
        N, X, D = int(line[0]), int(line[1]), int(line[2])

        A = []
        for i in range(N):
            row_str = input().strip()
            A.append([int(c) for c in row_str])

        # Enumerate all ways to choose N positions from X lockers
        # and assign N receivers to them
        count = 0
        for positions in combinations(range(1, X + 1), N):
            # Try all permutations of receivers in the chosen positions
            for perm in permutations(range(N)):
                # perm[i] = receiver index placed at positions[i]
                # Check if communication matrix matches A
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

        print(count % MOD)

solve()
