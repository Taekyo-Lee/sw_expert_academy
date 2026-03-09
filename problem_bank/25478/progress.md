# Problem 25478 — 수신기 배정 (D7)

- **Difficulty**: D7
- **Time limit**: 16s (Python) | **Memory limit**: 256MB
- **Summary**: Place N receivers in X lockers (1m apart); count assignments where communication (distance ≤ D) matches a given N×N matrix A, mod 10^9+7.

---

## Trial 1
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [✅] Submit → **MLE**
- [✅] Reflect → plan_2.md (root cause: 2^N bitmask infeasible for N=50; new approach: proper interval ordering + gap DP with O(2^D) states)

---

## Trial 2
- [✅] Plan → plan_2.md
- [✅] Write → solution_2.py (local test: pass)
- [✅] Submit → **WA** (93/140 pass)
- [✅] Reflect → plan_3.md (root cause: plain LBFS produces invalid orderings; fix: use LBFS+ for second sweep)

---

## Trial 3
- [✅] Plan → plan_3.md
- [✅] Write → solution_3.py (local test: pass, stress test: 0/500 mismatches)
- [✅] Submit → **WA** (139/140 pass)
- [✅] Reflect → plan_4.md (root cause: LBFS+ still fails for N≥20; fix: use proper priority-based LBFS+)

---

## Trial 4
- [✅] Plan → plan_4.md
- [✅] Write → solution_4.py (local test: pass, LBFS stress: 0/40565 failures, brute-force stress: 0/2000 mismatches, exhaustive: 0/4211 mismatches)
- [✅] Submit → **Pass**

