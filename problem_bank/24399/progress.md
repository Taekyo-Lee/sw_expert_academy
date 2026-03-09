# Problem 24399 — 확률과 통계 (Probability and Statistics)

- **Difficulty**: D7 (VH)
- **Time limit**: 30s (Python) | **Memory limit**: 256MB
- **Summary**: Given 30000 weighted-random draw sequences of 30 balls (without replacement), estimate the weights of each ball type so that pairwise weight ratios are within 2% error.

---

## Trial 1
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [✅] Stress Test → pass (warnings: ~4s CPython, est. ~1s PyPy per case)
- [✅] Validate → pass
- [✅] Submit → **WA (0/20)**
- [✅] Diagnose → plan_2.md (root cause: `#T` output prefix not expected by judge; algorithm is correct)

## Trial 2
- [✅] Plan → (from reflect)
- [✅] Write → solution_2.py (local test: pass)
- [✅] Stress Test → pass (CPython: 1.2–3.7s/case; est. PyPy: 0.25–0.74s/case; 20 cases worst ~15s/30s)
- [✅] Validate → pass
- [✅] Submit → **RE** (`open` is not allowed by judge)
- [✅] Reflect → plan_3.md (fix: revert to `input()`/`print()` I/O, keep no-prefix output)

## Trial 3
- [✅] Plan → plan_3.md (from reflect)
- [✅] Write → solution_3.py (local test: pass)
- [✅] Stress Test → pass (~1.3s CPython, est. <0.5s PyPy per case)
- [✅] Validate → pass
- [✅] Submit → **WA (14/20)**
- [✅] Reflect → plan_4.md (root cause: MLE statistical variance exceeds 0.02 threshold; fix: Fisher-based James-Stein shrinkage)

## Trial 4
- [✅] Plan → (from reflect)
- [✅] Write → solution_4.py (local test: pass, uniform error 0.024→0.001, groups error 0.026→0.006)
- [✅] Stress Test → pass (~1.5-3.8s CPython per case)
- [✅] Validate → pass (no import sys, no open(0), no #T prefix, no walrus)
- [ ] Submit → awaiting verdict
