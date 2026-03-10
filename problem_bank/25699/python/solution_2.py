def solve():
    H, W = map(int, input().split())
    grid = []
    for _ in range(H):
        grid.append(input().strip())

    # Precompute valid horizontal periods using bitmasks for speed.
    # valid_horiz[a] = True iff grid[r][c] == grid[r][c+a] for all r, 0 <= c < W-a.
    # For a > W, the check is vacuously true (no overlapping pairs).
    row_masks = []
    for r in range(H):
        mask = 0
        row = grid[r]
        for c in range(W):
            if row[c] == '#':
                mask |= 1 << c
        row_masks.append(mask)

    valid_horiz = [True] * (W + 1)
    for a in range(1, W + 1):
        overlap = (1 << (W - a)) - 1
        ok = True
        for rm in row_masks:
            if (rm ^ (rm >> a)) & overlap:
                ok = False
                break
        valid_horiz[a] = ok

    # Enumerate lattices in HNF by increasing area.
    # HNF basis: v1 = (a, 0), v2 = (b, d), area = a * d.
    # Iterate d from 1 to min(area, H). d > H is never optimal.
    # a = area / d can exceed W — this is the key fix over trial 1.
    max_area = H * W
    for area in range(1, max_area + 1):
        for d in range(1, min(area, H) + 1):
            if area % d != 0:
                continue
            a = area // d

            if a <= W and not valid_horiz[a]:
                continue

            for b in range(a):
                ok = True

                for rem in range(d):
                    # Check all rows with r % d == rem
                    expected = {}
                    r = rem
                    while r < H:
                        q = r // d
                        off = q * b
                        row = grid[r]
                        for c in range(W):
                            cc = (c - off) % a
                            ch = row[c]
                            prev = expected.get(cc)
                            if prev is None:
                                expected[cc] = ch
                            elif prev != ch:
                                ok = False
                                break
                        if not ok:
                            break
                        r += d
                    if not ok:
                        break

                if ok:
                    return area
    return max_area


T = int(input())
for _ in range(T):
    print(solve())
