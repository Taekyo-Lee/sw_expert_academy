# Plan 3 — Problem 24399

## Changes from Trial 2

Trial 1 failed: `#T` output prefix not expected by judge.
Trial 2 failed: `open(0)` is blocked by the judge environment.

## Fix

Combine trial 1's `input()`/`print()` I/O with trial 2's no-prefix output format.

- Use `input()` for reading (proven to work in trial 1)
- Use `print()` for output with NO `#T` prefix (just space-separated floats)
- Keep the MM algorithm unchanged (verified correct)
- Add early stopping (from trial 2) to save time
