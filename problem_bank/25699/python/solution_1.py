T = int(input())
for test_case in range(1, T + 1):
    H, W = map(int, input().split())
    grid = []
    for _ in range(H):
        grid.append(input().strip())

    # Encode grid as flat integer array
    grid_flat = [0] * (H * W)
    for r in range(H):
        for c in range(W):
            if grid[r][c] == '#':
                grid_flat[r * W + c] = 1

    # Precompute row d-periodicity
    # row_d_ok[d] = True if for all rows, shifting by d columns gives the same color
    row_d_ok = [True] * (W + 1)
    for d in range(1, W):
        ok = True
        for r in range(H):
            if not ok:
                break
            base = r * W
            for c in range(W - d):
                if grid_flat[base + c] != grid_flat[base + c + d]:
                    ok = False
                    break
        row_d_ok[d] = ok

    # Precompute valid period vectors
    # valid_vec[dr][dc + W - 1] for dr in [0, H), dc in [-(W-1), W-1]
    offset = W - 1
    valid_vec = [[True] * (2 * W - 1) for _ in range(H)]
    for dr in range(H):
        for dc in range(-(W - 1), W):
            ok = True
            r_lo = max(0, -dr)
            r_hi = min(H, H - dr)
            c_lo = max(0, -dc)
            c_hi = min(W, W - dc)
            for r in range(r_lo, r_hi):
                if not ok:
                    break
                for c in range(c_lo, c_hi):
                    if grid_flat[r * W + c] != grid_flat[(r + dr) * W + (c + dc)]:
                        ok = False
                        break
            valid_vec[dr][dc + offset] = ok

    # Search for minimum area
    answer = H * W
    for A in range(1, H * W + 1):
        found = False
        # Enumerate divisors: a * d = A
        for a in range(1, A + 1):
            if A % a != 0:
                continue
            d = A // a
            # Filter 1: row d-periodicity
            if d < W and not row_d_ok[d]:
                continue

            for b in range(d):
                # Filter 2: basis vector (a, b) validity
                if a < H and b < W and not valid_vec[a][b + offset]:
                    continue
                # Also check (a, b - d) if in range
                bd = b - d
                if a < H and b > 0 and bd >= -(W - 1):
                    if not valid_vec[a][bd + offset]:
                        continue

                # Full coset consistency check
                coset_color = [-1] * A
                valid = True
                for r in range(H):
                    if not valid:
                        break
                    r_mod = r % a
                    kb = (r // a) * b
                    base = r_mod * d
                    for c in range(W):
                        c_mod = (c - kb) % d
                        idx = base + c_mod
                        cell = grid_flat[r * W + c]
                        cc = coset_color[idx]
                        if cc == -1:
                            coset_color[idx] = cell
                        elif cc != cell:
                            valid = False
                            break

                if valid:
                    found = True
                    break
            if found:
                break
        if found:
            answer = A
            break

    print(answer)
