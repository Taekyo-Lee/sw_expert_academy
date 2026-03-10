# Problem 25699 — 타일링

- **Difficulty**: D7
- **Time limit**: Python 30초 (201 테스트케이스 합산)
- **Memory limit**: 256MB
- **Summary**: 2차원 격자판의 일부가 주어질 때, 평행이동만으로 무한 격자판을 타일링할 수 있는 블럭의 최소 크기(넓이)를 구하라.
- **Submit mode**: auto

---

## Trial 1

- **Plan**: `plan_1.md` — HNF lattice enumeration. Enumerate all 2D integer lattices in Hermite Normal Form (a, 0), (b, d) by increasing area a*d. For each lattice, check if the H x W window's coloring is consistent with the periodicity. First consistent lattice gives the answer. Pre-filter with horizontal period check on a for efficiency.
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [✅] Stress Test → pass (0.567s for 201 cases)
- [✅] Validate → pass
- [✅] Submit → **WA** (120/201 passed)
- [✅] Diagnose → Bug: `a` was capped at `W`, but valid lattices can have `a > W`. Counter-example: 2x2 grid `#. / ..` needs `a=3 > W=2` (area 3, not 4).

## Trial 2

- **Plan**: `plan_2.md` — Same HNF approach, but iterate `d` from 1 to `min(area, H)` instead of `a` from 1 to `min(area, W)`. This allows `a = area/d` to exceed `W`. Verified correct on all 74,954 grids up to 4x4 (zero mismatches vs brute force).
- [✅] Plan → plan_2.md
- [✅] Write → solution_2.py (local test: pass)
- [✅] Stress Test → pass (35.6s CPython, ~7-12s estimated PyPy)
- [✅] Validate → pass (same checks as trial 1, bug fix verified)
- [✅] Submit → **Pass**
