def solve():
    H, W = map(int, input().split())
    grid = []
    for _ in range(H):
        grid.append(input().strip())

    # Precompute compatibility table as flat list for speed
    # dr in [-(H-1), H-1], dc in [-(W-1), W-1]
    # Flat index: (dr + H - 1) * (2*W - 1) + (dc + W - 1)
    oh = H - 1
    ow = W - 1
    cw = 2 * W - 1  # width of compat table
    compat = [False] * ((2 * H - 1) * cw)

    for dr in range(-oh, H):
        r_lo = max(0, -dr)
        r_hi = min(H, H - dr)
        if r_lo >= r_hi:
            # No overlap in row dimension - trivially compatible
            base = (dr + oh) * cw + ow
            for dc in range(-ow, W):
                compat[base + dc] = True
            continue
        base_idx = (dr + oh) * cw
        for dc in range(-ow, W):
            c_lo = max(0, -dc)
            c_hi = min(W, W - dc)
            ok = True
            for r in range(r_lo, r_hi):
                gr = grid[r]
                gr2 = grid[r + dr]
                for c in range(c_lo, c_hi):
                    if gr[c] != gr2[c + dc]:
                        ok = False
                        break
                if not ok:
                    break
            compat[base_idx + dc + ow] = ok

    # Search for minimum area
    for A in range(1, H * W + 1):
        found = False
        # Enumerate HNF bases with determinant A
        for a in range(1, A + 1):
            if A % a != 0:
                continue
            d = A // a

            # Quick check: if d > 2*(W-1), then no non-zero lattice vectors
            # have dc in range, so only vectors with n=0 matter
            # (vectors of form (m*a, 0))
            # Similarly if a > 2*(H-1), only n != 0 vectors matter

            n_lo = -((W - 1) // d)
            n_hi = (W - 1) // d

            for b in range(a):
                valid = True
                for n in range(n_lo, n_hi + 1):
                    dc = n * d
                    # m*a in [-(H-1) - n*b, H-1 - n*b]
                    nb = n * b
                    lo = -oh - nb
                    hi = oh - nb
                    # ceil(lo / a) and floor(hi / a)
                    if lo >= 0:
                        m_lo = lo // a
                    else:
                        m_lo = -((-lo + a - 1) // a)
                    if hi >= 0:
                        m_hi = hi // a
                    else:
                        m_hi = -((-hi + a - 1) // a)

                    for m in range(m_lo, m_hi + 1):
                        if m == 0 and n == 0:
                            continue
                        dr = m * a + nb
                        if -oh <= dr <= oh and -ow <= dc <= ow:
                            if not compat[(dr + oh) * cw + dc + ow]:
                                valid = False
                                break
                    if not valid:
                        break
                if valid:
                    found = True
                    break
            if found:
                break
        if found:
            return A

    return H * W

T = int(input())
for tc in range(T):
    print(solve())
