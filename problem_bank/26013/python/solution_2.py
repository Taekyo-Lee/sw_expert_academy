def solve():
    MOD = 998244353
    G = 3

    MAXN = 200002
    fact = [1] * MAXN
    for i in range(1, MAXN):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * MAXN
    inv_fact[MAXN - 1] = pow(fact[MAXN - 1], MOD - 2, MOD)
    for i in range(MAXN - 2, -1, -1):
        inv_fact[i] = inv_fact[i + 1] * (i + 1) % MOD

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
                w = pow(G, MOD - 1 - (MOD - 1) // length, MOD)
            else:
                w = pow(G, (MOD - 1) // length, MOD)
            half = length >> 1
            # Pre-compute twiddle factors for this level
            ws = [1] * half
            for idx in range(1, half):
                ws[idx] = ws[idx - 1] * w % MOD
            for i in range(0, n, length):
                for jj in range(half):
                    u = a[i + jj]
                    v = a[i + jj + half] * ws[jj] % MOD
                    a[i + jj] = (u + v) % MOD
                    a[i + jj + half] = (u - v) % MOD
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

    def compute_rook_poly(a_val, p_exp, b_val, q_exp, n_col):
        n = n_col
        if n == 0:
            return [1]

        # f_i = P(i) / i! for i = 0..n
        f = [0] * (n + 1)
        for i in range(n + 1):
            val = pow(i + a_val, p_exp, MOD) * pow(i + b_val, q_exp, MOD) % MOD
            f[i] = val * inv_fact[i] % MOD

        # g_i = (-1)^i / i! for i = 0..n
        g = [0] * (n + 1)
        for i in range(n + 1):
            if i & 1:
                g[i] = MOD - inv_fact[i]
            else:
                g[i] = inv_fact[i]

        conv = poly_mul(f, g)

        # r_j = conv[n - j] for j = 0..n
        rook = [0] * (n + 1)
        lc = len(conv)
        for j in range(n + 1):
            idx = n - j
            if idx < lc:
                rook[j] = conv[idx] % MOD
        return rook

    T = int(input())
    out_parts = []
    for _ in range(T):
        N = int(input())
        if N == 1:
            out_parts.append('1')
            continue

        # Even parity diagonals
        if N % 2 == 0:
            n_even = N - 1
            a_even, p_even = 2, N // 2
            b_even, q_even = 1, N // 2 - 1
        else:
            n_even = N
            a_even, p_even = 1, (N + 1) // 2
            b_even, q_even = 0, (N - 1) // 2

        # Odd parity diagonals
        if N % 2 == 0:
            n_odd = N
            a_odd, p_odd = 1, N // 2
            b_odd, q_odd = 0, N // 2
        else:
            n_odd = N - 1
            a_odd, p_odd = 2, (N - 1) // 2
            b_odd, q_odd = 1, (N - 1) // 2

        even_rook = compute_rook_poly(a_even, p_even, b_even, q_even, n_even)
        odd_rook = compute_rook_poly(a_odd, p_odd, b_odd, q_odd, n_odd)

        conv = poly_mul(even_rook, odd_rook)

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
