import io as _io

# =====================================================================
# Precomputation
# =====================================================================

K = 71
mod5 = 5 ** K           # 5^71
pow2K = 2 ** K           # 2^71  (= 2^71)
order = 4 * (5 ** 70)    # order of 2 mod 5^71
pow10_50 = 10 ** 50

# h = 2^4 mod 5^71  (generator of the 5-Sylow subgroup of (Z/5^71 Z)*)
h = pow(2, 4, mod5)

# h_powers[j] = h^(5^j) mod mod5
h_powers = [0] * (K + 1)
h_powers[0] = h
for j in range(K):
    h_powers[j + 1] = pow(h_powers[j], 5, mod5)

# h_powers_inv[j] = inverse of h_powers[j] mod mod5
h_powers_inv = [0] * (K + 1)
for j in range(K + 1):
    h_powers_inv[j] = pow(h_powers[j], mod5 - 2, mod5)  # Fermat won't work; 5^71 not prime
# Actually mod5 = 5^71 is NOT prime, so Fermat's little theorem doesn't apply.
# Use pow(a, -1, mod5) which works in Python 3.8+.
# For Python 3.7, we need extended gcd.

def modinv(a, m):
    """Modular inverse via extended Euclidean algorithm."""
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        return None
    return x % m

def _extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1

# Recompute h_powers_inv properly
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

# CRT helper: inverse of 2^71 mod 5
inv_pow2K_mod5 = modinv(pow2K % 5, 5)  # 2^71 mod 5: 2^4=1 mod 5, 71=17*4+3, so 2^71=2^3=3 mod 5. inv(3,5)=2
# Actually let's just compute it
_tmp = pow2K % 5
inv_pow2K_mod5 = inv5_table[_tmp]

# =====================================================================
# Solve
# =====================================================================

def solve(X):
    # Step A: Construct target T
    # T = X * 10^50 + L, where L is a 50-digit number
    # Constraints:
    #   T ≡ 0 (mod 2^71)  =>  L ≡ -(X * 10^50) (mod 2^71)
    #   T mod 5 != 0       =>  L mod 5 != (-(X * 10^50)) mod 5 ... actually we want last digit not 0 or 5
    #   We force L mod 5 = 2 so T's last digit contribution from L ends in 2 (ensuring not div by 5)

    base = X * pow10_50
    a = (-base) % pow2K  # L ≡ a (mod 2^71)

    # We need L ≡ r (mod 5) where r is chosen so that (base + L) mod 5 != 0
    # i.e., (base + a + 2^71 * t) mod 5 != 0 for some t in {0,1,2,3,4}
    # Let's pick L's residue mod 5 to be 2 (arbitrary nonzero, but we need (base+L) mod 5 != 0)
    # Actually, we need T mod 5 != 0, i.e., (base + L) mod 5 != 0.
    # L = a + pow2K * t, so (base + a + pow2K * t) mod 5 != 0
    # base + a ≡ base + (-base mod pow2K) ... Let's just compute directly.

    ba_mod5 = (base + a) % 5
    # We need (ba_mod5 + pow2K * t) % 5 != 0
    # pow2K mod 5 = _tmp (computed above)
    # ba_mod5 + _tmp * t ≡ 0 (mod 5)  =>  t_bad = (-ba_mod5) * inv_pow2K_mod5 % 5
    t_bad = ((-ba_mod5) * inv_pow2K_mod5) % 5
    # Pick t != t_bad, t in {0,1,2,3,4}
    t = (t_bad + 1) % 5

    L = a + pow2K * t
    T_val = base + L

    # Step B: Discrete log
    # Find N such that 2^N ≡ T_val (mod 5^71)
    r = T_val % mod5

    # n0: 2^n0 ≡ r (mod 5)
    r_mod5 = r % 5
    n0 = dlog_mod5[r_mod5]

    # r1 = r * 2^{-n0} mod mod5, now r1 ≡ 1 (mod 5)
    r1 = r * g_inv_table[n0] % mod5

    # Find m such that h^m ≡ r1 (mod 5^71), 0 <= m < 5^70
    # p-adic lifting
    curr_inv = 1  # tracks h^{-m_partial} mod mod5
    m_partial = 0

    for j in range(K - 1):  # j = 0..69
        mod_level = pow5[j + 2]
        diff = (r1 * (curr_inv % mod_level)) % mod_level
        d_j = ((diff - 1) // pow5[j + 1]) % 5
        c_j = (d_j * inv_ej[j]) % 5
        if c_j > 0:
            m_partial += c_j * pow5[j]
            curr_inv = curr_inv * h_inv_pow[j][c_j] % mod5

    N = n0 + 4 * m_partial

    # Step C: Adjust
    if N < K or N < 1:
        N += order

    return N


# =====================================================================
# I/O
# =====================================================================

_input = _io.BufferedReader(_io.FileIO(0))
_readline = _input.readline

TC = int(_readline())
out = []
for _ in range(TC):
    X = int(_readline())
    out.append(str(solve(X)))

_output = _io.BufferedWriter(_io.FileIO(1, 'w'))
_output.write('\n'.join(out).encode())
_output.write(b'\n')
_output.flush()
