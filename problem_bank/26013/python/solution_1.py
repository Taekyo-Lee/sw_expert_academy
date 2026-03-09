def solve():
    MOD = 998244353
    g = 3

    def ntt(a, invert):
        n = len(a)
        j = 0
        for i in range(1, n):
            bit = n >> 1
            while j & bit:
                j ^= bit
                bit >>= 1
            j ^= bit
            if i < j:
                a[i], a[j] = a[j], a[i]
        length = 2
        while length <= n:
            if invert:
                w = pow(g, MOD - 1 - (MOD - 1) // length, MOD)
            else:
                w = pow(g, (MOD - 1) // length, MOD)
            half = length >> 1
            for i in range(0, n, length):
                wn = 1
                for jj in range(half):
                    u = a[i + jj]
                    v = a[i + jj + half] * wn % MOD
                    a[i + jj] = (u + v) % MOD
                    a[i + jj + half] = (u - v) % MOD
                    wn = wn * w % MOD
            length <<= 1
        if invert:
            inv_n = pow(n, MOD - 2, MOD)
            for i in range(n):
                a[i] = a[i] * inv_n % MOD

    def poly_mul(a, b):
        ra = len(a)
        rb = len(b)
        rc = ra + rb - 1
        n = 1
        while n < rc:
            n <<= 1
        fa = list(a) + [0] * (n - ra)
        fb = list(b) + [0] * (n - rb)
        ntt(fa, False)
        ntt(fb, False)
        for i in range(n):
            fa[i] = fa[i] * fb[i] % MOD
        ntt(fa, True)
        return fa[:rc]

    def build_rook_poly(sizes):
        if not sizes:
            return [1]
        m = len(sizes)
        poly = [0] * (m + 1)
        poly[0] = 1
        deg = 0
        md = MOD
        i = 0
        while i < m:
            if i + 1 < m and sizes[i] == sizes[i + 1]:
                s = sizes[i]
                new_deg = deg + 2
                # Tight inner loop for pair processing
                # new[k] = old[k] + 2*(s-k+1)*old[k-1] + (s-k+2)*(s-k+1)*old[k-2]
                # For PyPy performance, precompute s+1 = sp1
                sp1 = s + 1
                for k in range(new_deg, 1, -1):
                    t = sp1 - k  # = s - k + 1
                    # (t+1)*t = (s-k+2)*(s-k+1), precompute mod to keep small
                    sq = (t + 1) * t % md
                    poly[k] = (poly[k] + 2 * t * poly[k - 1] + sq * poly[k - 2]) % md
                # k = 1: t = s, only first-order term
                poly[1] = (poly[1] + 2 * s * poly[0]) % md
                deg = new_deg
                i += 2
            else:
                s = sizes[i]
                sp1 = s + 1
                new_deg = deg + 1
                for k in range(new_deg, 0, -1):
                    poly[k] = (poly[k] + (sp1 - k) * poly[k - 1]) % md
                deg = new_deg
                i += 1
        return poly[:deg + 1]

    T = int(input())
    out_parts = []
    for _ in range(T):
        N = int(input())
        if N == 1:
            out_parts.append('1')
            continue

        # Even parity: sorted sizes [1,1,3,3,...,N-1,N-1] for N even, plus N if N odd
        even_sizes = []
        half = N >> 1
        for j in range(1, half + 1):
            v = 2 * j - 1
            even_sizes.append(v)
            even_sizes.append(v)
        if N & 1:
            even_sizes.append(N)

        # Odd parity: sorted sizes
        odd_sizes = []
        if N & 1:
            half2 = (N - 1) >> 1
            for j in range(1, half2 + 1):
                v = 2 * j
                odd_sizes.append(v)
                odd_sizes.append(v)
        else:
            half2 = (N - 2) >> 1
            for j in range(1, half2 + 1):
                v = 2 * j
                odd_sizes.append(v)
                odd_sizes.append(v)
            odd_sizes.append(N)

        even_poly = build_rook_poly(even_sizes)
        odd_poly = build_rook_poly(odd_sizes)
        conv = poly_mul(even_poly, odd_poly)

        max_k = 2 * N - 1
        parts = []
        lc = len(conv)
        for k in range(1, max_k + 1):
            if k < lc:
                parts.append(str(conv[k] % MOD))
            else:
                parts.append('0')
        out_parts.append(' '.join(parts))

    print('\n'.join(out_parts))

solve()
