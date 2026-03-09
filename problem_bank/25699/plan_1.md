# Plan 1 — Problem 25699: 타일링

## 1. Problem Analysis

We have an infinite 2D grid where every cell is black (`#`) or white (`.`). The grid is tiled by translating a single **simple rectilinear polygon** (no rotation/reflection). Given an H x W rectangular window of the grid (1 <= H, W <= 16), find the **minimum possible area** of the tiling block.

- **Input**: T test cases (up to 201). Each: H, W, then H rows of W characters (`#`/`.`).
- **Output**: For each test case, the minimum block area.
- **Limits**: Python 30 seconds total for all 201 test cases. Memory 256 MB.

## 2. Key Observations

### Observation 1: Lattice Tiling

A tiling of the plane by translating a single block is equivalent to a **lattice tiling**. There exist two linearly independent integer vectors v1, v2 forming a lattice L such that:
- The block is a fundamental domain of L (one cell per coset of Z^2 / L).
- The block area equals |det(v1, v2)|.

### Observation 2: Hermite Normal Form (HNF)

Every rank-2 integer lattice has a unique **Hermite Normal Form**:

```
v1 = (a, b),  v2 = (0, d)
```

where a > 0, d > 0, 0 <= b < d, and the lattice determinant (= block area) is A = a * d.

### Observation 3: Coset Consistency Check

For a candidate lattice with HNF (a, d, b), cell (r, c) belongs to the coset labeled by:
- `r_class = r mod a`
- `c_class = (c - (r // a) * b) mod d`
- Combined label: `r_class * d + c_class` (an index in [0, A))

The lattice is **valid** if and only if all cells in the same coset have the same color in the observed window.

### Observation 4: Simple Rectilinear Polygon Always Exists

For any 2D integer lattice, a connected, hole-free polyomino fundamental domain always exists. Thus the lattice determinant directly gives the minimum block area — no need to separately verify block shape.

### Observation 5: Necessary Condition — Row d-periodicity

The lattice contains (0, d), which means shifting the grid right by d columns preserves it. Within the window, this requires every row to be d-periodic: `grid[r][c] == grid[r][c + d]` for all valid r, c. This can be precomputed for all d and used as a fast filter.

### Observation 6: Upper Bound

The lattice always contains (H, 0) and (0, W) (unverifiable vectors are unconstrained), so the answer is at most H * W. We iterate A from 1 upward and return the first valid A.

## 3. Algorithm

Enumerate candidate lattice areas A from 1 to H*W. For each A, enumerate all HNF triples (a, d, b) with a*d = A and 0 <= b < d. For each triple, check coset consistency. Return the first valid A.

### Filters for Speed

1. **d-periodicity prefilter**: Precompute `row_d_ok[d]` — True if ALL rows are d-periodic with column period d. If `d < W` and `row_d_ok[d]` is False, skip the entire (a, d) pair.
2. **Basis vector prefilter**: Precompute `valid_vec[dr][dc]` — True if (dr, dc) is a valid period vector in the window. Before the full coset check, verify that the basis vector (a, b) passes (if `a < H` and `b < W`).
3. **Early termination**: Break as soon as any valid triple is found for area A.

## 4. Step-by-Step Approach

```
read T
for each test case:
    read H, W
    read H rows of W characters
    encode grid as flat integer array: grid_flat[r*W + c] = 1 if '#', else 0

    # Precompute row d-periodicity
    row_d_ok = array of size W+1, initialized to True
    for d from 1 to W-1:
        for r from 0 to H-1:
            for c from 0 to W-d-1:
                if grid_flat[r*W + c] != grid_flat[r*W + c + d]:
                    row_d_ok[d] = False
                    break (both inner loops)

    # Precompute valid period vectors
    # valid_vec[dr][dc + W] = True/False for dr in [0, H), dc in [-(W-1), W-1]
    # (store with offset to handle negative dc)
    valid_vec = 2D array [H][2*W-1], default True
    for dr from 0 to H-1:
        for dc from -(W-1) to W-1:
            for r from max(0, -dr) to min(H, H-dr) - 1:
                for c from max(0, -dc) to min(W, W-dc) - 1:
                    if grid_flat[r*W + c] != grid_flat[(r+dr)*W + (c+dc)]:
                        valid_vec[dr][dc + W - 1] = False
                        break (both inner loops)
            # Note: dr=0 and dc=0 is trivially valid

    # Search for minimum area
    answer = H * W  # fallback upper bound
    for A from 1 to H*W:
        found = False
        # Enumerate divisors: a * d = A
        for a from 1 to A:
            if A % a != 0:
                continue
            d = A // a
            # Filter 1: row d-periodicity
            if d < W and not row_d_ok[d]:
                continue
            # d >= W means d-periodicity is vacuously true (no same-row coset overlaps)

            for b from 0 to d-1:
                # Filter 2: basis vector (a, b) validity
                if a < H and b < W and not valid_vec[a][b + W - 1]:
                    continue
                # Also check (a, b - d) if b - d is in range (another lattice vector)
                if a < H and 0 < b and (b - d) >= -(W-1):
                    if not valid_vec[a][(b - d) + W - 1]:
                        continue

                # Full coset consistency check
                coset_color = [-1] * A
                valid = True
                for r from 0 to H-1:
                    r_mod = r % a
                    kb = (r // a) * b
                    base = r_mod * d
                    for c from 0 to W-1:
                        c_mod = (c - kb) % d
                        idx = base + c_mod
                        cell = grid_flat[r * W + c]
                        cc = coset_color[idx]
                        if cc == -1:
                            coset_color[idx] = cell
                        elif cc != cell:
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
            answer = A
            break

    print(answer)
```

## 5. Edge Cases

| Case | Handling |
|------|----------|
| All cells same color | Answer = 1 (trivially, A=1 with any lattice works) |
| H=1 or W=1 | Works naturally — row periodicity or column periodicity only |
| H=W=1 | Answer = 1 always |
| Checkerboard pattern (e.g., "#.#/.#.") | Answer = 2 (diagonal lattice) |
| Full grid is the block (answer = H*W) | Falls through to A = H*W; the identity lattice always works |
| Prime answer (e.g., 13) | Only factorizations a=1,d=A and a=A,d=1 are possible |

## 6. Complexity Analysis

### Time Complexity

- **Precomputation**: O(H * W * (H + W)) for row-d-periodicity and valid-vec.
- **Main loop**: For each area A, enumerate sigma_1(A) = sum_{d|A} d HNF triples. For each triple, the coset check is O(H * W).
  - Total triples up to area N: sum_{A=1}^{N} sigma_1(A) ~ N^2 * pi^2 / 12.
  - For N = H*W = 256: ~54,000 triples.
  - Total coset check work: ~54,000 * 256 ~ 13.8M operations (worst case).
- With d-periodicity and basis-vector filters, most triples are pruned quickly (O(1) per pruned triple).
- **Per test case**: ~0.1-0.5 seconds in PyPy (worst case).
- **201 test cases**: ~20-100 seconds worst case. With early termination (small answers), likely well under 30 seconds.

### Space Complexity

- O(H * W) for the grid and precomputed arrays.
- O(H * W) for the coset_color array.
- Total: O(H * W) = O(256). Well within 256 MB.

### Feasibility Notes

- The algorithm iterates A from small to large, so test cases with small answers (common in practice) terminate quickly.
- PyPy 3.7's JIT compilation makes tight inner loops ~10x faster than CPython, bringing worst-case performance within the 30-second limit.
- The d-periodicity filter eliminates a large fraction of candidates at O(1) cost, significantly reducing the constant factor.
- If needed, further optimization: represent each row as a bitmask and check d-periodicity via bitwise XOR. This makes the precomputation and filter even faster.
