# SW Expert Academy Solver

An AI-powered solve loop for [SW Expert Academy](https://swexpertacademy.com/) coding problems, targeting Python 3.7 (PyPy 3.7). Supports both the public site and the [Samsung internal mirror](https://swexpertacademy.samsung.com/).

## Setup

Copy the example `.env` and fill in your values:

```bash
cp env.example .env
```

| Variable | Description |
|----------|-------------|
| `SWEA_BASE_URL` | `https://swexpertacademy.com` (home) or `https://swexpertacademy.samsung.com` (company) |
| `SWEA_ID` | Login email (home only — company uses SSO) |
| `SWEA_PW` | Login password (home only) |

At company (`swexpertacademy.samsung.com`), SSO handles authentication automatically — `SWEA_ID` and `SWEA_PW` are not needed.

### Playwright MCP

The `fetching-problem` and `submitting-solution` skills (and `solving-problem --auto`) require a **Playwright MCP server** to control a headless browser. Enable it in your agent's MCP settings before using these skills. The skills will detect if it is missing and prompt you to enable it.

## Quick Start

```
fetching-problem 24399        # Fetch the problem statement (or VH1234 on company mirror)
solving-problem 24399          # Start the full solve loop
```

Or simply ask in natural language: *"Solve problem 24399 end to end."*

## How It Works

The solver orchestrates a **plan → write → stress test → validate → submit → reflect** loop, with the human submitting to the online judge and reporting the verdict back. Each skill runs as a separate sub-agent, keeping context isolated and allowing the orchestrator to delegate work cleanly.

### Flow Diagram

```
                 ┌─────────┐
                 │  Plan    │  Generate algorithm plan (plan_N.md)
                 └────┬─────┘
                      │
                 ┌────▼─────┐
            ┌───►│  Write    │  Implement solution (solution_N.py) + local test
            │    └────┬──────┘
            │         │
            │    Local test fail?──── Yes ──► Revise plan_N.md (overwrite) ──┐
            │         │ No                                                   │
            │    ┌────▼──────┐                                               │
            │◄───│Stress Test│◄──────────────────────────────────────────────┘
            │    └────┬──────┘
        Revise        │
      plan_N.md  Fail (TLE/RE)?──── Yes ──► Revise plan_N.md (overwrite) ──► Write ──► Stress Test
     (overwrite)      │ No
            │    ┌────▼──────┐
            └────│ Validate  │  Static code review
                 └────┬──────┘
                      │ Pass
                 ┌────▼──────┐
                 │  Submit    │  User submits to judge and reports verdict
                 └────┬──────┘
                      │
               Pass? ─┤
              Yes     │ No
               │ ┌────▼──────┐
               │ │  Reflect   │  Diagnose failure → plan_{N+1}.md
               │ └────┬──────┘
               │      │
               │      └──► Next trial (N+1) ──► Write
               │
              Done!
```

### Key Design: When Does the Trial Number Increment?

**Only after a judge verdict failure.** Everything else retries within the same trial:

| Failure type       | What happens                                  | Trial N changes? |
|--------------------|-----------------------------------------------|-------------------|
| Local test fail    | Revise `plan_N.md`, rewrite `solution_N.py`   | No (same N)       |
| Stress test fail   | Revise `plan_N.md`, rewrite `solution_N.py`   | No (same N)       |
| Validation fail    | Rewrite `solution_N.py`                       | No (same N)       |
| **Judge fail (WA/TLE/...)** | **Reflect → create `plan_{N+1}.md`** | **Yes (N → N+1)** |

This means each trial number represents one actual submission to the judge.

### Retry Limits

- **3** write retries per trial (local test failures)
- **3** stress test attempts per trial (TLE/RE)
- **3** validate-write cycles per trial
- **10** total trials (judge submissions)

## Skills

| Skill | Purpose |
|-------|---------|
| `fetching-problem <id>` | Fetch problem statement → `problem.md` |
| `solving-problem <id> [--resume\|--restart]` | Full solve loop (orchestrator) |
| `planning-solution <id> [trial]` | Plan algorithm → `plan_N.md` |
| `writing-solution <id> [trial]` | Implement plan → `solution_N.py` + local test |
| `stress-testing <id> <trial>` | Max-size input stress tests |
| `validating-solution <id> <trial>` | Static code review for judge compatibility |
| `diagnosing-failure <id> <trial> <verdict> [output_trial]` | Diagnose failure → revised plan |

## Project Layout

```
.env                                    # Credentials (git-ignored)
env.example                             # Template for .env
problem_bank/{problem_id}/
  problem.md                          # Problem statement
  progress.md                         # Solve loop progress log
  plan_{trial_number}.md              # Algorithm plan per trial
  python/solution_{trial_number}.py   # Solution per trial
  tests/                              # Stress test input files
```

## Progress Tracking

Each trial is tracked in `progress.md`. Example of a trial with a stress test retry followed by a passing submission:

```markdown
## Trial 1
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [❌] Stress Test → FAIL — TLE (attempt 1)
- [✅] Revise → plan_1.md (updated)
- [✅] Write → solution_1.py (local test: pass)
- [✅] Stress Test → pass (attempt 2)
- [✅] Validate → pass
- [✅] Submit → **Pass**
```

Sessions are resumable — run `solving-problem <id> --resume` to pick up where you left off.

## Constraints

- **No `import sys`** — use `input()` / `print()` for I/O
- **No external packages** (numpy, pandas, etc.)
- **No walrus operator** (`:=`) — requires Python 3.8+
