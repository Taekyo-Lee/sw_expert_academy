# Problem 24702 — 2의 거듭제곱

- **Difficulty**: D7
- **Time limit**: Python 30s (12190 test cases combined) | **Memory limit**: 256MB
- **Summary**: Given X, find any N < 10^50 such that X appears as a substring in the last 100 digits of 2^N.

---

## Trial 1
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [✅] Submit → **Error** (`import io` forbidden)
- [✅] Reflect → plan_2.md

## Trial 2
- [✅] Plan → (from reflect)
- [✅] Write → solution_2.py (local test: pass)
- [✅] Submit → **WA** (4400/12190 — K=71 produces N near 10^49, likely checker overflow)
- [✅] Reflect → plan_3.md

## Trial 3
- [✅] Plan → (from reflect)
- [✅] Write → solution_3.py (local test: pass)
- [✅] Submit → **Pass**

