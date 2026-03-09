# Problem 25660 — 산타의 선물

- **Difficulty**: D7
- **Time limit**: C: 1s / C++: 1s / Java: 2s / Python: 3s | **Memory limit**: 256MB heap+static, 1MB stack
- **Summary**: Given N children's preference orderings over N gifts, find a "best" assignment P such that no other assignment q is preferred by a strict majority over P (i.e., no q > P), and output the lexicographically smallest such P, or -1 if none exists.

---

## Trial 1
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [✅] Submit → **WA** (0/77)
- [✅] Reflect → plan_2.md

## Trial 2
- [✅] Plan → (from reflect)
- [✅] Write → solution_2.py (local test: pass)
- [✅] Submit → **WA** (0/77, caused by wrong output format in problem.md — #T prefix)
- [✅] Fix → removed #T prefix from output; local test now matches corrected sample
- [✅] Submit → **Pass** (77/77)
