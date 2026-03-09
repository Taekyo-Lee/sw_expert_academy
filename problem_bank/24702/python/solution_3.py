# =====================================================================
# Precomputation
# =====================================================================

K = 20
mod5 = 5 ** K           # 5^20
pow2K = 2 ** K           # 2^20 = 1048576
order = 4 * (5 ** 19)    # order of 2 mod 5^20 = 4 * 5^19 = 76293945312500
offset = 8
pow10_offset = 10 ** offset  # 10^8 = 100000000


def modinv(a, m):
    """Modular inverse via iterative extended Euclidean algorithm."""
    a = a % m
    old_r, r = a, m
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:
        return None
    return old_s % m


# h = 2^4 mod 5^20  (generator of the 5-Sylow subgroup of (Z/5^20 Z)*)
h = pow(2, 4, mod5)

# h_powers[j] = h^(5^j) mod mod5
h_powers = [0] * (K + 1)
h_powers[0] = h
for j in range(K):
    h_powers[j + 1] = pow(h_powers[j], 5, mod5)

# h_powers_inv[j] = inverse of h_powers[j] mod mod5
h_powers_inv = [0] * (K + 1)
for j in range(K + 1):
    h_powers_inv[j] = modinv(h_powers[j], mod5)

# pow5[j] = 5^j for j = 0..K+1
pow5 = [0] * (K + 2)
pow5[0] = 1
for j in range(K + 1):
    pow5[j + 1] = pow5[j] * 5

# For each level j (0..K-2), precompute:
#   e_j = ((h_powers[j] mod 5^{j+2}) - 1) // 5^{j+1} mod 5
#   inv_e_j = inverse of e_j mod 5
inv5_table = {1: 1, 2: 3, 3: 2, 4: 4}
inv_ej = [0] * K
for j in range(K - 1):
    mod_level = pow5[j + 2]
    val = h_powers[j] % mod_level
    e_j = ((val - 1) // pow5[j + 1]) % 5
    inv_ej[j] = inv5_table[e_j]

# g_inv = modinv(2, mod5), g_inv_table[k] = g_inv^k mod mod5 for k=0..3
g_inv = modinv(2, mod5)
g_inv_table = [0] * 4
g_inv_table[0] = 1
for k in range(1, 4):
    g_inv_table[k] = g_inv_table[k - 1] * g_inv % mod5

# Lookup: 2^n0 mod 5 -> n0
# 2^0=1, 2^1=2, 2^2=4, 2^3=3 (mod 5)
dlog_mod5 = {1: 0, 2: 1, 4: 2, 3: 3}

# Precompute powers of h_powers_inv[j] for c_j = 1..4
# h_inv_pow[j][c] = h_powers_inv[j]^c mod mod5
h_inv_pow = [[0] * 5 for _ in range(K)]
for j in range(K):
    h_inv_pow[j][0] = 1
    for c in range(1, 5):
        h_inv_pow[j][c] = h_inv_pow[j][c - 1] * h_powers_inv[j] % mod5

# CRT helper: inverse of 2^20 mod 5
_tmp = pow2K % 5
inv_pow2K_mod5 = inv5_table[_tmp]


# =====================================================================
# Solve
# =====================================================================

def solve(X):
    # Step A: Construct target T
    # T = X * 10^8 + L, where L < 10^8
    # Constraints:
    #   T divisible by 2^20
    #   T mod 5 != 0
    base = X * pow10_offset
    a = (-base) % pow2K  # L ≡ a (mod 2^20)

    ba_mod5 = (base + a) % 5
    # Find t != t_bad so (base + a + pow2K * t) % 5 != 0
    t_bad = ((-ba_mod5) * inv_pow2K_mod5) % 5
    t = (t_bad + 1) % 5

    L = a + pow2K * t
    T_val = base + L

    # Step B: Discrete log
    # Find N such that 2^N ≡ T_val (mod 5^20)
    r = T_val % mod5

    # n0: 2^n0 ≡ r (mod 5)
    r_mod5 = r % 5
    n0 = dlog_mod5[r_mod5]

    # r1 = r * 2^{-n0} mod mod5, now r1 ≡ 1 (mod 5)
    r1 = r * g_inv_table[n0] % mod5

    # Find m such that h^m ≡ r1 (mod 5^20), 0 <= m < 5^19
    # p-adic lifting
    curr_inv = 1  # tracks h^{-m_partial} mod mod5
    m_partial = 0

    for j in range(K - 1):  # j = 0..18
        mod_level = pow5[j + 2]
        diff = (r1 * (curr_inv % mod_level)) % mod_level
        d_j = ((diff - 1) // pow5[j + 1]) % 5
        c_j = (d_j * inv_ej[j]) % 5
        if c_j > 0:
            m_partial += c_j * pow5[j]
            curr_inv = curr_inv * h_inv_pow[j][c_j] % mod5

    N = n0 + 4 * m_partial

    # Step C: Adjust - ensure N >= K and N >= 1
    if N < K or N < 1:
        N += order

    return N


# =====================================================================
# I/O
# =====================================================================

T = int(input())
out = []
for _ in range(T):
    X = int(input())
    out.append(str(solve(X)))

print('\n'.join(out))
