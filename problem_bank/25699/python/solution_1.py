def solve():
    H, W = map(int, input().split())
    grid = []
    for _ in range(H):
        grid.append(input().strip())

    # Precompute: for each candidate 'a' (horizontal period), check validity
    # grid[r][c] == grid[r][c+a] for all r, c where c+a < W
    valid_a = [True] * (W + 1)
    for a in range(1, W + 1):
        ok = True
        for r in range(H):
            row = grid[r]
            for c in range(W - a):
                if row[c] != row[c + a]:
                    ok = False
                    break
            if not ok:
                break
        valid_a[a] = ok

    # Enumerate areas in increasing order
    max_area = H * W
    for area in range(1, max_area + 1):
        # Enumerate all factorizations area = a * d
        for a in range(1, min(area, W) + 1):
            if area % a != 0:
                continue
            d = area // a
            if d > H * max_area:  # d can be anything, but practically bounded
                continue
            if not valid_a[a]:
                continue

            for b in range(a):
                # Check full lattice consistency
                # Canonical rep of (r, c) is (r mod d, (c - (r // d) * b) mod a)
                color_map = {}
                consistent = True
                for r in range(H):
                    q, rem = divmod(r, d)
                    offset = q * b
                    row = grid[r]
                    for c in range(W):
                        canon = (rem, (c - offset) % a)
                        ch = row[c]
                        prev = color_map.get(canon)
                        if prev is not None:
                            if prev != ch:
                                consistent = False
                                break
                        else:
                            color_map[canon] = ch
                    if not consistent:
                        break
                if consistent:
                    return area
    return max_area


T = int(input())
for _ in range(T):
    print(solve())
