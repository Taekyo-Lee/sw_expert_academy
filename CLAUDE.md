# SW Expert Academy

Solve coding problems from SW Expert Academy using Python 3.7 (PyPy 3.7).
Supports both https://swexpertacademy.com/ (home, ID/PW login) and https://swexpertacademy.samsung.com/ (company, SSO login). Set `SWEA_BASE_URL` in `.env` to choose. The company mirror uses alphanumeric problem IDs with a difficulty prefix (e.g., `VH1234`, `H1234`, `MH1234`) instead of plain numbers.

## Skills

| Skill | Purpose |
|-------|---------|
| `/fetching-problem <problem_id>` | Fetch problem statement from the website and save as `problem.md`. |
| `/solving-problem <problem_id> [--resume \| --restart] [--auto \| --manual]` | Full solve loop: plan → write → validate → submit → reflect. `--auto` submits via browser; `--manual` (default) pauses for user verdicts. Max 10 trials. |
| `/planning-solution <problem_id> [trial_number]` | Plan an algorithm and save as `plan_N.md`. Auto-increments if trial omitted. |
| `/writing-solution <problem_id> [trial_number]` | Implement a plan as `solution_N.py` and run local tests. Uses latest plan if trial omitted. |
| `/validating-solution <problem_id> <trial_number>` | Static code review to catch prohibited imports, forbidden syntax, and output format issues before submission. |
| `/stress-testing <problem_id> <trial_number>` | Generate max-size inputs and measure execution time to catch TLE/RE before submission. |
| `/submitting-solution <problem_id> <trial_number>` | Submit a solution via Playwright and return the judge verdict. |
| `/diagnosing-failure <problem_id> <trial_number> <verdict>` | Diagnose a failed submission and produce a revised plan. |

## Prerequisites

- **Playwright MCP** — Required by `fetching-problem`, `submitting-solution`, and `solving-problem --auto`. Enable the Playwright plugin in `~/.claude/settings.json` (`"playwright@claude-plugins-official": true`) and restart Claude Code.

## Project layout

```
problem_bank/{problem_id}/
  problem.md                          # Problem statement
  progress.md                         # Solve loop progress log
  plan_{trial_number}.md              # Algorithm plan per trial
  python/solution_{trial_number}.py   # Solution per trial
  tests/                              # Stress test input files
```

## Constraints

- **No `import sys`** — use `input()` / `print()` for I/O.
- **No external packages** (numpy, pandas, etc.).
- **No walrus operator** (`:=`) — requires Python 3.8+.
- Target the Python/PyPy time and memory limits.
