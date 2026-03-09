---
name: solving-problem
description: Orchestrate the full solve loop for a SW Expert Academy problem with human-in-the-loop judge verdicts.
argument-hint: <problem_id> [--resume | --restart] [--auto | --manual]
---

Orchestrate the full plan → write → validate → submit → reflect loop for SW Expert Academy problem **$0**.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | No | `--resume` to continue from `progress.md`, or `--restart` to start fresh. If omitted, defaults to asking the user. |
| `$2` | third | No | `--auto` to submit and fetch verdicts automatically via Playwright, or `--manual` for the user to submit and report verdicts. If omitted, defaults to asking the user. |

## Invocation modes

| Command | Behavior |
|---------|----------|
| `/solving-problem 12345` | **Default.** Asks the user about resume/restart and submission mode. |
| `/solving-problem VH1234` | Same as above, using the company mirror's alphanumeric ID format. |
| `/solving-problem 12345 --resume` | **Resume.** Continue from `progress.md`. Reuses the saved `{submit_mode}`. |
| `/solving-problem 12345 --restart` | **Restart.** Start fresh from trial 1. Asks about submission mode. |
| `/solving-problem 12345 --restart --auto` | **Restart + Auto.** Start fresh; submit and fetch verdicts automatically via Playwright. |
| `/solving-problem 12345 --restart --manual` | **Restart + Manual.** Start fresh; user submits and reports verdicts. |
| `/solving-problem 12345 --resume --auto` | **Resume + Auto.** Continue from `progress.md`; override saved mode to auto. |

`--auto` and `--manual` can be combined with any invocation mode. If omitted, the user is asked.

This skill manages trial numbering automatically.

## Prerequisite

`./problem_bank/$0/problem.md` must already exist. If it does not, tell the user to run `/fetching-problem $0` first and stop.

## Critical: use fresh sub-task agents

Every sub-skill invocation below **MUST** be dispatched as a **fresh sub-task agent** to keep the main conversation context small. **Never resume a previous sub-task** — each call gets a brand-new agent instance, even if it is the same skill invoked for a different trial number. Do NOT expand the sub-skill inline.

This applies to every `/planning-solution`, `/writing-solution`, `/stress-testing`, `/validating-solution`, `/submitting-solution`, and `/diagnosing-failure` call, on every trial.

## Progress tracking

Maintain a progress log at `./problem_bank/$0/progress.md`. This file tracks every phase of the solve loop and serves as a persistent record for resumability and visibility.

### Initialize (before the trial loop)

Read `problem.md` and create `progress.md` with the problem info header:

```markdown
# Problem $0 — {title}

- **Difficulty**: {difficulty}
- **Time limit**: {time_limit} | **Memory limit**: {memory_limit}
- **Summary**: {one-line summary of what the problem asks}
- **Submit mode**: {submit_mode}

---
```

### Update after each phase

Append to `progress.md` as each phase completes. Use this format:

```markdown
## Trial {trial_number}
- [✅] Plan → plan_{trial_number}.md
- [✅] Write → solution_{trial_number}.py (local test: pass)
- [✅] Stress Test → pass
- [✅] Validate → pass
- [ ] Submit → awaiting verdict
```

Update the current trial's checklist in-place as phases complete:
- After **Plan**: add the `## Trial N` heading and mark Plan done.
- After **Write**: mark Write done, note local test result (pass/fail).
- After **Stress Test**: mark Stress Test done, note result (`pass`, `pass (warnings)`, or `FAIL — TLE`/`FAIL — RE`). On FAIL, revise plan and solution **within the same trial** (no trial increment).
- After **Stress Test Revise**: mark the revision, then re-run Write and Stress Test within the same trial.
- After **Validate**: mark Validate done, note result (`pass`, or `FAIL — {summary}`). On FAIL, the Write→Validate cycle repeats until pass.
- After **Submit** (user reports verdict): mark Submit done with the verdict in bold (e.g., `**Pass**`, `**WA**`, `**TLE**`).
- After **Reflect** (judge failure only): mark Reflect done, note the output file. This is the only place trial number increments.

Final state of a failed trial (judge verdict):
```markdown
## Trial 1
- [✅] Plan → plan_1.md
- [✅] Write → solution_1.py (local test: pass)
- [✅] Stress Test → pass
- [✅] Validate → pass
- [✅] Submit → **WA**
- [✅] Reflect → plan_2.md
```

Trial with stress test retries (same trial number, no increment):
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

Final state of a passing trial:
```markdown
## Trial 2
- [✅] Plan → (from reflect)
- [✅] Write → solution_2.py (local test: pass)
- [✅] Stress Test → pass
- [✅] Validate → pass
- [✅] Submit → **Pass**
```

### On resume

When resuming (via `--resume` or user choosing "resume" at the default prompt):

1. Read `progress.md` to determine the last trial number and the last completed phase.
2. Resume from the **next incomplete phase** of that trial. For example:
   - If the last entry is `Plan → plan_2.md` (done), resume at **Write** for trial 2.
   - If the last entry is `Write → solution_2.py` (done) with no Stress Test, resume at **Stress Test** for trial 2.
   - If the last entry is `Stress Test → pass` (done) with no Validate, resume at **Validate** for trial 2.
   - If the last entry is `Stress Test → FAIL` with no Revise, resume at **Stress Test Revise** for the same trial (step 2.5 retry loop).
   - If the last entry is `Revise → plan_N.md (updated)` with no subsequent Write, resume at **Write** for the same trial.
   - If the last entry is `Validate → FAIL`, resume at **Write** for the same trial (to fix the validation issues).
   - If the last entry is `Validate → pass` (done) with `Submit → awaiting verdict`, resume at **Wait for user verdict** for trial 2.
   - If the last entry is `Submit → **WA**` (done) with no Reflect, resume at **Reflect** for trial 2.
   - If the last trial is fully complete (Reflect done), start the **next trial** at Write (since reflect already produced the plan).

## Workflow

### Startup

1. Check `$1` for `--resume` or `--restart` to determine the invocation mode (default if `$1` is empty).
2. Check that `problem.md` exists (see Prerequisite).
3. Determine starting state:
   - **`--restart`**: Delete `progress.md` if it exists. Set `{trial_number}` = 1. Initialize `progress.md`.
   - **`--resume`**: Read `progress.md`. If it does not exist, tell the user there is nothing to resume and stop. Otherwise, determine the resume point (see "On resume" above). Also read `{submit_mode}` from the progress header (see below).
   - **Default (no flag)**: If `progress.md` exists, ask the user: *"A previous session exists for problem $0. Resume where you left off, or start fresh?"* Then follow the user's choice. If `progress.md` does not exist, set `{trial_number}` = 1 and initialize `progress.md`.
4. **Choose submission mode:**
   - **`--auto`** (`$2`): Set `{submit_mode}` = `auto`.
   - **`--manual`** (`$2`): Set `{submit_mode}` = `manual`.
   - **`--resume`** (without `$2`): Reuse `{submit_mode}` from `progress.md`. If `$2` is provided, it overrides the saved mode.
   - **Default (no `$2`)**: Ask the user:

     > **How would you like to handle submission?**
     > 1. **Manual** — I'll tell you when to submit and you report the verdict back.
     > 2. **Auto** — I'll submit and check the verdict automatically using the browser.

   If the user's original request clearly implies full automation (e.g., "don't interrupt", "solve it end to end"), default to `auto` without asking.

### Trial loop

**Maximum 10 trials.** If trial 10 still fails, stop and summarize all attempts so far.

#### 1. Plan

Launch a fresh sub-task: `/planning-solution $0 {trial_number}`.

Update `progress.md`: add `## Trial {trial_number}` and mark Plan done.

#### 2. Write + local test

Launch a fresh sub-task: `/writing-solution $0 {trial_number}`.

Update `progress.md`: mark Write done with local test result.

If the Write sub-task reports that local tests could not be passed, **stay on the same trial number** and revise:
1. Update `progress.md`: mark Write as `❌ FAIL (local test: FAIL)`.
2. Launch a fresh sub-task: `/diagnosing-failure $0 {trial_number} WA {trial_number}` — 4th argument is the **same** trial number, so the revised plan **overwrites** `plan_{trial_number}.md`.
3. Update `progress.md`: mark `Revise → plan_{trial_number}.md (updated)`.
4. Retry **step 2** (Write) with the same `{trial_number}`.

**Maximum 3 Write retry cycles per trial.** If Write still fails after 3 attempts, proceed to step 6 (Reflect) which will increment the trial number.

#### 2.5. Stress Test

Launch a fresh sub-task: `/stress-testing $0 {trial_number}`.

Update `progress.md`: mark Stress Test done with the result.

- **Pass** (or pass with warnings) → Proceed to step 3 (Validate).
- **Fail** → Performance failures need algorithmic changes. **Stay on the same trial number** and revise:
  1. Update `progress.md`: mark Stress Test as `❌ FAIL — TLE` (or `FAIL — RE`) with attempt number.
  2. Launch a fresh sub-task: `/diagnosing-failure $0 {trial_number} {TLE|RE} {trial_number}` — note the 4th argument is the **same** trial number, so the revised plan **overwrites** `plan_{trial_number}.md`.
  3. Update `progress.md`: mark `Revise → plan_{trial_number}.md (updated)`.
  4. Go back to **step 2** (Write) with the **same** `{trial_number}`. The solution file `solution_{trial_number}.py` will be overwritten.
  5. After Write, return here to step 2.5 (Stress Test) again.

**Maximum 3 stress test attempts per trial.** If the stress test still fails after 3 attempts, treat it as a failed trial with verdict `TLE` (or `RE`). Update `progress.md` accordingly and proceed to step 6 (Reflect) which will increment the trial number.

#### 3. Validate

Launch a fresh sub-task: `/validating-solution $0 {trial_number}`.

- **Pass** → Update `progress.md`: mark Validate done (`pass`). Proceed to step 4.
- **Fail** → Update `progress.md`: mark Validate done (`FAIL — {summary}`). Go back to **step 2** (Write) — launch a fresh `/writing-solution $0 {trial_number}` sub-task. In the sub-task prompt, include the full list of validation issues so the Write agent knows exactly what to fix. Then return to step 3 (Validate) to re-check.

**Maximum 3 Validate→Write cycles per trial.** If validation still fails after 3 attempts, treat it as a failed trial with verdict `RE` (the code has structural issues) and proceed to step 6 (Reflect). Update `progress.md` accordingly.

#### 4. Submit and get verdict

Update `progress.md`: add Submit line as `- [ ] Submit → awaiting verdict`.

**If `{submit_mode}` = `manual`:**

Tell the user:

> **Trial {trial_number} is ready.**
> Submit `./problem_bank/$0/python/solution_{trial_number}.py` on the website and report the verdict (e.g., Pass, WA, TLE, MLE, RE).

Then **stop and wait** for the user's response. Do not proceed until the user provides a verdict.

**If `{submit_mode}` = `auto`:**

Launch a fresh sub-task: `/submitting-solution $0 {trial_number}`.

The sub-task will submit the solution via Playwright MCP and return the judge verdict. Use the returned verdict to proceed to step 5 — no user interaction needed.

#### 5. Handle the verdict

Update `progress.md`: mark Submit done with the verdict (e.g., `**Pass**`, `**WA**`).

- **Pass / Accepted** → Congratulate the user and stop.
- **Fail (WA, TLE, MLE, RE, or other)** → If `{trial_number}` = 10, stop and summarize all attempts. Otherwise continue to step 6.

#### 6. Reflect and retry (judge failure only)

This step is reached **only** after a judge verdict failure (WA, TLE, MLE, RE from submission). This is the **only** place trial number increments.

Launch a fresh sub-task: `/diagnosing-failure $0 {trial_number} {verdict}`.

This creates `plan_{trial_number + 1}.md` (the default behavior when no 4th argument is passed). Update `progress.md`: mark Reflect done with output file (`plan_{trial_number + 1}.md`).

Increment `{trial_number}` by 1. Update `progress.md`: append `## Trial {trial_number}` heading and mark Plan done as `- [✅] Plan → (from reflect)`. Then go back to **step 2** (Write + local test) — the new plan is already written by reflect. After Write, continue through Stress Test (step 2.5), Validate (step 3), and then Submit (step 4) as usual.
