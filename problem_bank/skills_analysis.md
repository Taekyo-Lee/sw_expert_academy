# Agent Skills 종합 분석

> **SWEA 문제 풀이 시스템의 8개 Skill을 세미나 핵심 개념으로 해부하기**
>
> 이 문서는 세미나의 이론(Agent Skills, Progressive Disclosure, Degrees of Freedom 등)이
> 실제 시스템에서 어떻게 구현되었는지를 보여주는 **케이스 스터디**입니다.

---

## 1. 시스템 전체 구조

### 1.1 한눈에 보기

```
┌──────────────────────────────────────────────────────────────────────────┐
│ solving-problem (Supervisor)                                             │
│ "전체 루프를 오케스트레이션하되, 직접 일하지 않는다"                          │
└────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
 fetching  planning  writing  validating  stress   submitting  diagnosing
 -problem  -solution -solution -solution  -testing -solution   -failure
 (수집)     (설계)    (구현)    (정적검증)  (성능검증) (제출)      (진단)
```

### 1.2 8개 Skill 요약

| # | Skill | 역할 | 자유도 | scripts/ | references/ |
|---|-------|------|--------|----------|-------------|
| 1 | **solving-problem** | Supervisor. 전체 루프 관리 | 낮음 | - | - |
| 2 | **fetching-problem** | 웹에서 문제 수집 | 낮음 | - | `.env` |
| 3 | **planning-solution** | 알고리즘 설계 | **높음** | - | - |
| 4 | **writing-solution** | 코드 구현 + 테스트 | 중간 | `test_solution.py` | - |
| 5 | **validating-solution** | 정적 코드 리뷰 | 낮음 | - | - |
| 6 | **stress-testing** | 최대 입력 성능 검증 | 중간 | `stress_test.py` | - |
| 7 | **submitting-solution** | 채점 제출 + 결과 파싱 | 낮음 | - | `.env` |
| 8 | **diagnosing-failure** | 실패 진단 + 수정 계획 | **높음** | - | - |

---

## 2. Skill Anatomy (해부)

### 2.1 YAML Frontmatter — Progressive Disclosure Level 1

모든 Skill은 동일한 frontmatter 구조를 따릅니다. 이 부분만 **상시 컨텍스트에 로드**됩니다.

```yaml
---
name: planning-solution
description: Plan a Python 3.7 algorithm for a SW Expert Academy coding problem and save it as plan_{trial_number}.md.
argument-hint: <problem_id> [trial_number]
---
```

| 필드 | 용도 | 토큰 비용 |
|------|------|----------|
| `name` | Skill 식별자. 사용자가 `/planning-solution`으로 호출 | ~3 tokens |
| `description` | LLM이 "이 Skill을 써야 하나?"를 판단하는 기준 | ~20-30 tokens |
| `argument-hint` | 사용자에게 필요한 인자를 알려주는 힌트 | ~5-10 tokens |

> **8개 Skill의 Level 1 총 비용: ~300 tokens**
> MCP로 동일 기능을 제공하면 schema 비용만 수천 tokens

### 2.2 Body (Markdown) — Progressive Disclosure Level 2

Skill이 **매칭되어 호출될 때만** 로드됩니다. 각 Skill의 instruction 크기:

| Skill | Body 길이 (줄) | 주요 섹션 | 특징 |
|-------|------------|---------|------|
| solving-problem | **240줄** | Arguments, Invocation modes, Progress tracking, Workflow (6단계) | 가장 큼. Supervisor로서 전체 흐름 명세 |
| fetching-problem | 97줄 | Playwright MCP 사용법, 5단계 워크플로우 | Tool 사용법을 Skill 안에 내장 |
| planning-solution | 47줄 | 3단계 (이해→설계→저장) | 가장 짧고 자유도 높음 |
| writing-solution | 65줄 | 4단계 (읽기→구현→저장→테스트) | scripts/ 참조 |
| validating-solution | 79줄 | 5가지 검증 항목 체크리스트 | 체크리스트 패턴 |
| stress-testing | 116줄 | 4단계 (제약 추출→생성→실행→분석) | scripts/ 참조, 분류 기준표 내장 |
| submitting-solution | 159줄 | 9단계 Playwright 워크플로우 | 가장 절차적. UI 인터랙션 상세 기술 |
| diagnosing-failure | **134줄** | 4단계 + Cross-trial 패턴 분석 | Stuck Detection 로직 내장 |

### 2.3 scripts/ — Progressive Disclosure Level 3

2개의 Skill만 실행 스크립트를 가집니다:

| Skill | 스크립트 | 역할 |
|-------|---------|------|
| writing-solution | `scripts/test_solution.py` (147줄) | problem.md에서 샘플 추출 → 솔루션 실행 → 출력 비교 |
| stress-testing | `scripts/stress_test.py` (113줄) | 테스트 입력으로 솔루션 실행 → 시간 측정 → PASS/WARNING/FAIL 분류 |

**왜 스크립트인가?**

이 작업들은 "정확한 프로세스 실행"이 핵심이므로, LLM에게 매번 코드를 작성하게 하면:
- 매번 미묘하게 다른 테스트 러너를 생성 → 일관성 없음
- subprocess 타임아웃, 출력 파싱 등 boilerplate를 매번 재작성 → 토큰 낭비
- 한번 검증된 코드를 반복 사용하는 것이 안정적

> **패턴:** 창의적 판단이 필요한 부분은 LLM에게 (SKILL.md instruction), 반복 실행은 스크립트에게 (scripts/)

### 2.4 references/ — Progressive Disclosure Level 3

2개의 Skill이 references를 가집니다:

| Skill | 파일 | 내용 |
|-------|------|------|
| fetching-problem | `references/.env` | SWEA 계정 정보 (SWEA_BASE_URL, SWEA_ID, SWEA_PW) |
| submitting-solution | `references/.env` | 동일 — 제출 시 로그인용 |

> **패턴:** 민감 정보(credentials)를 Skill 본문에 하드코딩하지 않고, 외부 파일로 분리. Skill은 "`.env`를 읽어라"고만 지시.

---

## 3. Progressive Disclosure 작동 원리

세미나의 핵심 개념인 Progressive Disclosure가 이 시스템에서 어떻게 작동하는지:

### 3.1 Level별 토큰 비용

```
[Level 1] 상시 로드 — Skill 목록
  solving-problem:    "Orchestrate the full solve loop..." (~40 tokens)
  fetching-problem:   "Fetch a problem statement..."       (~30 tokens)
  planning-solution:  "Plan a Python 3.7 algorithm..."     (~35 tokens)
  writing-solution:   "Write a Python 3.7 solution..."     (~30 tokens)
  validating-solution:"Static code review..."              (~35 tokens)
  stress-testing:     "Generate max-size stress test..."   (~30 tokens)
  submitting-solution:"Submit a solution via Playwright..."(~30 tokens)
  diagnosing-failure: "Reflect on a failed submission..."  (~30 tokens)
  ─────────────────────────────────────────────────────
  총 Level 1 비용:                                    ~260 tokens

[Level 2] 매칭 시 로드 — SKILL.md body
  planning-solution을 호출하면 47줄의 instruction 로드    ~500 tokens
  solving-problem을 호출하면 240줄의 instruction 로드    ~2,500 tokens

[Level 3] 필요 시 로드 — scripts/, references/
  test_solution.py 실행 (코드 자체는 로드 불필요, 실행만)   0 tokens
  .env 파일 읽기                                         ~20 tokens
```

### 3.2 시나리오별 실제 토큰 소비

**시나리오: `/solving-problem 25699` 실행 (1회에 Pass)**

| 단계 | 로드되는 Skill | 추가 토큰 | 누적 |
|------|-------------|----------|------|
| 대기 중 | Level 1 (8개 목록) | ~260 | 260 |
| Supervisor 시작 | solving-problem body | ~2,500 | 2,760 |
| → fetching-problem 호출 | fetching-problem body (새 에이전트) | ~1,000 | — (별도 컨텍스트) |
| → planning-solution 호출 | planning-solution body (새 에이전트) | ~500 | — (별도 컨텍스트) |
| → writing-solution 호출 | writing-solution body (새 에이전트) | ~600 | — (별도 컨텍스트) |
| → stress-testing 호출 | stress-testing body (새 에이전트) | ~1,000 | — (별도 컨텍스트) |
| → validating-solution 호출 | validating-solution body (새 에이전트) | ~800 | — (별도 컨텍스트) |
| → submitting-solution 호출 | submitting-solution body (새 에이전트) | ~1,500 | — (별도 컨텍스트) |

> **핵심:** Supervisor 컨텍스트에는 ~2,760 tokens만 존재. 각 서브 Skill은 자신의 body만 가진 **별도 컨텍스트**에서 실행. 이것이 "컨텍스트 격리"의 실체.

### 3.3 MCP 대비 비교

만약 동일 기능을 MCP tool로 구현했다면:

| 항목 | MCP 방식 | Skills 방식 |
|------|---------|------------|
| 상시 로드 | 8 tools × ~350 tokens/schema = **~2,800 tokens** | 8 skills × ~33 tokens/desc = **~260 tokens** |
| 호출 시 | tool 실행 + 결과 반환 (같은 컨텍스트) | Skill body 로드 (별도 컨텍스트) |
| 컨텍스트 오염 | tool schema가 항상 컨텍스트 차지 | name+desc만 상시 존재 |
| 상시 비용 비율 | **~10.8x** | **1x** |

---

## 4. Degrees of Freedom (자유도) 분석

### 4.1 자유도 스펙트럼

```
낮은 자유도 ◄───────────────────────────────────────────► 높은 자유도
(절차적, 단계별)                                            (목표 중심, 방법 위임)

submitting  fetching  solving  validating  writing  stress   planning  diagnosing
-solution   -problem  -problem -solution  -solution -testing -solution -failure
  │           │         │        │          │         │         │         │
  ▼           ▼         ▼        ▼          ▼         ▼         ▼         ▼
 9단계       5단계     6단계    5체크      4단계     4단계     3단계    4단계+
 UI조작     UI조작    루프관리  체크리스트  구현+테스트 생성+측정  설계     패턴분석
```

### 4.2 낮은 자유도 Skills — "이렇게 해라"

#### submitting-solution (자유도: 최저)

**왜 낮은 자유도인가:**
- 9단계의 순차적 UI 인터랙션. 클릭 순서, 대기 시간, 결과 파싱까지 모두 명세
- "제출" 버튼의 `ref`를 찾고 → 클릭하고 → 확인 다이얼로그에서 "확인"을 클릭하는 과정을 한 치의 오차 없이 수행해야 함
- LLM이 창의성을 발휘할 여지가 전혀 없음 — 오히려 있으면 안 됨

```markdown
# SKILL.md에서 발췌
## Step 6: Paste the solution code
The code editor is a **CodeMirror** instance. The underlying `<textarea>` is
hidden behind CodeMirror's overlay and cannot be clicked directly.
Use `browser_run_code` to set the code via the CodeMirror API:
```

> **교훈:** UI 자동화, API 호출, 외부 시스템 연동처럼 **"정확성이 생명"인 작업**은 자유도를 극도로 낮춰야 한다. LLM이 "더 나은 방법"을 시도하면 오히려 깨진다.

#### validating-solution (자유도: 낮음)

**왜 낮은 자유도인가:**
- 5가지 검증 항목이 **체크리스트**로 명확히 정의
- "Prohibited imports", "Forbidden syntax", "Output format", "Debug artifacts", "I/O structure" — 각각 무엇을 검사할지 구체적으로 나열
- 판단 기준이 이진적 (위반 or 통과)

```markdown
# SKILL.md에서 발췌
### 1. Prohibited imports
Flag any `import` or `from … import` of:
- `sys`, `os`, `io`
- Any external package (`numpy`, `pandas`, `scipy`...)
```

> **패턴: Checklist Pattern** — 검증/리뷰 작업은 체크리스트로 정의하면 누락 없이 수행 가능

### 4.3 높은 자유도 Skills — "이것을 달성해라"

#### planning-solution (자유도: 최고)

**왜 높은 자유도인가:**
- 47줄밖에 되지 않는 가장 짧은 Skill
- "어떤 알고리즘을 선택할지"는 완전히 LLM에게 위임
- 6가지 섹션(문제 분석, 핵심 관찰, 알고리즘 선택, 단계별 접근, 엣지 케이스, 복잡도)의 **구조만** 지정하고, **내용**은 LLM이 채움

```markdown
# SKILL.md에서 발췌
## Step 2: Plan the algorithm
Think carefully and produce a plan covering:
1. **Problem analysis** — Restate the core problem in your own words.
2. **Key observations** — List mathematical properties...
3. **Algorithm choice** — Describe the algorithm... Justify why...
```

> **교훈:** 알고리즘 설계처럼 **"창의적 사고가 핵심"인 작업**은 자유도를 높여야 한다. 구조(무엇을 포함할지)만 지정하고, 내용(어떤 알고리즘을 선택할지)은 LLM의 강점에 맡긴다.

#### diagnosing-failure (자유도: 높음, 구조화된)

**특이점:** 자유도가 높지만, **구조화된 분석 프레임워크**를 제공

```markdown
# SKILL.md에서 발췌
### A. Verdict pattern classification
| Pattern     | Definition |
|-------------|------------|
| Plateaued   | Same verdict repeating... |
| Oscillating | Alternating between two verdicts... |
| Regressing  | Fewer test cases passed... |
| Progressing | Strictly more test cases passed... |
```

> **패턴: Structured Freedom** — 자유롭게 사고하되, 사고의 프레임워크를 제공. "무엇을 분석해야 하는지"는 정해주고, "분석 결과 무엇을 할지"는 LLM에게 맡김.

### 4.4 자유도 설계 가이드라인

| 작업 특성 | 적절한 자유도 | 이 시스템의 예 |
|----------|-------------|-------------|
| UI 인터랙션, API 호출 | **최저** — 클릭 순서까지 명세 | submitting-solution, fetching-problem |
| 검증, 리뷰 | **낮음** — 체크리스트 제공 | validating-solution |
| 코드 구현 | **중간** — 패턴과 제약은 주되, 구현은 위임 | writing-solution |
| 테스트 생성 | **중간** — 유형별 가이드 제공, 구체적 값은 위임 | stress-testing |
| 알고리즘 설계 | **높음** — 출력 구조만 지정 | planning-solution |
| 실패 진단 | **높음** (프레임워크 제공) — 분석 틀은 주되 결론은 위임 | diagnosing-failure |

---

## 5. Context Engineering 원칙의 구현

### 5.1 원칙 1: 컨텍스트 격리

**구현 방법:** solving-problem SKILL.md의 "Critical: use fresh sub-task agents" 규칙

```markdown
# solving-problem SKILL.md에서 발췌
## Critical: use fresh sub-task agents
Every sub-skill invocation below **MUST** be dispatched as a **fresh sub-task
agent** to keep the main conversation context small. **Never resume a previous
sub-task** — each call gets a brand-new agent instance, even if it is the same
skill invoked for a different trial number.
```

**왜 중요한가:**
- Trial 1의 writing-solution과 Trial 2의 writing-solution은 같은 Skill이지만, **완전히 다른 에이전트 인스턴스**에서 실행
- Trial 1의 실패한 코드, 디버깅 로그, 에러 메시지가 Trial 2의 컨텍스트를 오염시키지 않음
- 각 서브에이전트는 SKILL.md instruction + 입력 파일만 가진 깨끗한 상태에서 시작

### 5.2 원칙 2: 파일 기반 인터페이스

**구현 방법:** 모든 Skill은 파일을 읽고, 파일을 쓴다. 에이전트 간 직접 통신은 없다.

```
fetching-problem  ──▶  problem.md
                            │
planning-solution ◀─────────┘ (읽기)
planning-solution ──▶  plan_{n}.md
                            │
writing-solution  ◀─────────┘ (읽기) ◀── problem.md (읽기)
writing-solution  ──▶  solution_{n}.py
                            │
validating-solution ◀───────┘ (읽기) ◀── problem.md (읽기)
stress-testing    ◀─────────┘ (읽기) ◀── problem.md (읽기)
submitting-solution ◀───────┘ (읽기)
                            │
diagnosing-failure ◀────────┘ (읽기) ◀── problem.md + 모든 이전 plan/solution (읽기)
diagnosing-failure ──▶  plan_{n+1}.md
```

**파일 의존성 매트릭스:**

| Skill | 읽는 파일 | 쓰는 파일 |
|-------|----------|----------|
| fetching-problem | `.env` | `problem.md`, `problem_screenshot.png` |
| planning-solution | `problem.md` | `plan_{n}.md` |
| writing-solution | `problem.md`, `plan_{n}.md` | `solution_{n}.py` |
| validating-solution | `problem.md`, `solution_{n}.py` | (없음 — read-only) |
| stress-testing | `problem.md`, `solution_{n}.py` | `tests/edge_*.txt` |
| submitting-solution | `solution_{n}.py`, `.env` | (없음 — 외부 제출) |
| diagnosing-failure | `problem.md`, 모든 `plan_*.md`, 모든 `solution_*.py` | `plan_{n+1}.md` |
| solving-problem | `problem.md`, `progress.md` | `progress.md` |

### 5.3 원칙 3: 최소 컨텍스트

**구현 방법:** 각 Skill은 자신에게 필요한 파일만 읽도록 명시적으로 지정

**writing-solution의 예:**
```markdown
## Step 1: Read the problem and plan
1. Read the problem statement from `./problem_bank/$0/problem.md`
2. Read the plan from `./problem_bank/$0/plan_{trial_number}.md`
```

- 이전 trial의 실패한 solution은 읽지 않음
- diagnosing-failure의 분석 결과는 `plan_{n+1}.md`에 이미 반영되어 있으므로, writing-solution은 plan만 읽으면 됨
- 이것이 "정보 요약 전달"이 아닌 "원본 파일 직접 전달"의 실체

**diagnosing-failure의 예 (대비):**
```markdown
## Step 1: Gather context
- **If $1 ≤ 4**: read **all** plans and solutions
- **If $1 > 4**: read plan_1.md (original approach), plus the last 3 plans and solutions
```

- 이 Skill은 **의도적으로 많이 읽음** — 같은 실수를 반복하지 않기 위해 히스토리가 필요
- 하지만 무한정 읽지 않고, trial > 4이면 **원본 + 최근 3개**로 제한 → 컨텍스트 관리

### 5.4 원칙 4: 명시적 지식 외재화

**구현 방법:** diagnosing-failure가 생성하는 `plan_{n+1}.md`의 구조

```markdown
## Step 3: Produce a revised plan
1. **Reflection summary** — verdict, what failed, and why
2. **Problem analysis** — corrected understanding
3. **Key observations** — add new, mark corrected
4. **Algorithm choice** — keep or replace, with justification
5. **Step-by-step approach** — updated implementation steps
6. **Edge cases** — newly identified
7. **Complexity analysis** — verify fits within constraints
```

- "이전에 MLE가 났으니 메모리를 줄여라"라는 암묵적 지시가 아님
- 구체적으로 무엇이 왜 실패했고, 수정된 알고리즘이 왜 이전 실패를 피하는지를 **문서화**
- writing-solution은 이 문서만 읽으면 됨 — 이전 대화 히스토리 불필요

---

## 6. Supervisor Pattern 심층 분석

### 6.1 solving-problem의 역할

solving-problem은 이 시스템의 **Supervisor Skill**입니다. 특징:

| 특성 | 설명 |
|------|------|
| **직접 일하지 않음** | 알고리즘을 설계하거나 코드를 쓰지 않음. 서브 Skill을 호출할 뿐 |
| **상태 관리** | `progress.md`를 통해 전체 진행 상황을 추적 |
| **흐름 제어** | Plan→Write→Stress→Validate→Submit→Reflect 루프를 관리 |
| **에러 핸들링** | 각 단계의 실패를 감지하고 적절한 재시도/에스컬레이션 결정 |
| **재개 가능** | `--resume`으로 중단 지점부터 재시작 |

### 6.2 Retry Policy의 세밀함

solving-problem의 retry 로직은 "어디서 실패했느냐"에 따라 다르게 동작합니다:

| 실패 지점 | 동작 | Trial 변경 | 최대 재시도 |
|----------|------|-----------|-----------|
| Write (샘플 테스트 실패) | diagnosing-failure → 같은 trial에서 plan 덮어쓰기 → Write 재시도 | 유지 | 3회 |
| Stress Test (TLE/RE) | diagnosing-failure → 같은 trial에서 plan 덮어쓰기 → Write+Stress 재시도 | 유지 | 3회 |
| Validate (정적 검증 실패) | Write 재호출 (이슈 목록 전달) → Validate 재시도 | 유지 | 3회 |
| Submit (채점 실패) | diagnosing-failure → **다음 trial로** plan 생성 | **증가** | 10 Trial |

> **핵심 설계:** 로컬 검증 실패는 같은 trial 내에서 해결 (trial 번호 미소비). 채점 실패만 trial을 소비. 이 구분이 10회 제출 제한 환경에서 효율성의 원천.

### 6.3 `$3` 인자의 설계 의도

diagnosing-failure의 4번째 인자 `$3 (output_trial_number)`는 이 retry 정책을 구현하기 위한 장치:

```
# 채점 실패 시 (trial 증가)
/diagnosing-failure 25478 1 WA        → plan_2.md 생성 (기본: $1+1)

# 스트레스 테스트 실패 시 (같은 trial)
/diagnosing-failure 25478 1 TLE 1     → plan_1.md 덮어쓰기 ($3=1로 지정)
```

---

## 7. 특수 설계 패턴

### 7.1 Stuck Detection (교착 감지) — diagnosing-failure

Trial 3부터 활성화되는 Cross-trial 패턴 분석은 이 시스템의 가장 정교한 부분입니다:

```
Trial 1: TLE → "최적화하자"
Trial 2: TLE → "더 최적화하자"
Trial 3: TLE → Stuck Detection 발동!
  → "같은 알고리즘을 3번 최적화했는데 여전히 TLE"
  → "이 알고리즘은 본질적으로 불가능"
  → "근본적으로 다른 알고리즘으로 전환 강제"
```

**4단계 판단 로직:**

1. **Verdict Pattern Classification** — Plateaued / Oscillating / Regressing / Progressing 중 하나로 분류
2. **Algorithm Continuity Check** — "encoding 변경"과 "알고리즘 변경"을 구분
3. **Feasibility Sanity Check** — 현재 알고리즘의 이론적 자원 사용량 추정
4. **Stuck 선언** — 위 3개 중 하나라도 해당하면 STUCK, 단 Progressing이면 면제

> **교훈:** LLM은 "비슷한 최적화를 반복"하는 경향이 있다. Stuck Detection은 이 경향을 감지하고 강제로 방향을 전환시키는 **가드레일**.

### 7.2 Read-Only Pattern — validating-solution

```markdown
## Result
This skill is a **read-only checker**. It does NOT modify the solution file.
```

validating-solution과 stress-testing은 둘 다 read-only입니다:
- 코드를 **수정하지 않음** — 문제를 발견하고 보고만 함
- 수정은 writing-solution의 책임 — Supervisor가 이슈 목록과 함께 writing-solution을 재호출

> **패턴:** 검증과 수정의 책임을 분리하면, 검증의 신뢰성이 높아진다. 자기가 쓴 코드를 자기가 검증하면 bias가 생기기 때문.

### 7.3 Playwright MCP Integration — fetching-problem, submitting-solution

이 두 Skill은 **Skill 안에 Tool 사용법을 가르치는** 패턴을 보여줍니다:

```markdown
## How to use Playwright MCP
| Tool                                  | Purpose |
|---------------------------------------|---------|
| mcp__playwright__browser_navigate     | Navigate to a URL |
| mcp__playwright__browser_snapshot     | Get accessibility snapshot |
| mcp__playwright__browser_click        | Click element by ref |
| mcp__playwright__browser_type         | Type text into element |
```

- MCP tool의 schema는 이미 로드되어 있지만, **어떤 순서로 사용해야 하는지**는 모름
- Skill이 "이 tool들을 이런 순서로, 이런 패턴으로 사용해라"고 가르침
- Tool은 **능력(capability)**, Skill은 **사용법(how-to)**

> **패턴: Tool Orchestration** — Skill은 개별 Tool들의 사용법과 조합 순서를 정의하는 상위 레이어

---

## 8. 폴더 구조 전체 맵

```
📁 ~/.claude/skills/
│
├── 📁 solving-problem/              ← Supervisor
│   └── 📄 SKILL.md (240줄)
│
├── 📁 fetching-problem/             ← 문제 수집 (Playwright)
│   ├── 📄 SKILL.md (97줄)
│   └── 📁 references/
│       └── 📄 .env                  ← 계정 정보
│
├── 📁 planning-solution/            ← 알고리즘 설계 (자유도 최고)
│   └── 📄 SKILL.md (47줄)
│
├── 📁 writing-solution/             ← 코드 구현
│   ├── 📄 SKILL.md (65줄)
│   └── 📁 scripts/
│       └── 📄 test_solution.py      ← 샘플 테스트 러너
│
├── 📁 validating-solution/          ← 정적 검증 (read-only)
│   └── 📄 SKILL.md (79줄)
│
├── 📁 stress-testing/               ← 성능 검증 (read-only)
│   ├── 📄 SKILL.md (116줄)
│   └── 📁 scripts/
│       └── 📄 stress_test.py        ← 스트레스 테스트 러너
│
├── 📁 submitting-solution/          ← 채점 제출 (Playwright)
│   ├── 📄 SKILL.md (159줄)
│   └── 📁 references/
│       └── 📄 .env                  ← 계정 정보
│
└── 📁 diagnosing-failure/           ← 실패 진단 + Stuck Detection
    └── 📄 SKILL.md (134줄)
```

**총 파일 수:** SKILL.md 8개 + scripts 2개 + references 2개 = **12개 파일**

---

## 9. 세미나 개념과의 매핑 요약

| 세미나 개념 | 이 시스템에서의 구현 |
|------------|-------------------|
| **Agent Skills** | 8개의 SKILL.md — 각각 하나의 폴더, 하나의 역할 |
| **Progressive Disclosure** | Level 1 (name+desc ~260 tokens) → Level 2 (SKILL.md body) → Level 3 (scripts/, references/) |
| **Degrees of Freedom** | submitting(최저) ~ planning(최고). 작업 특성에 맞춘 자유도 조절 |
| **Skill Calling = Tool Calling 패턴** | `/solving-problem 25699` → Harness가 SKILL.md 로드 → LLM이 instruction 수행 |
| **파일 기반 Harness Engineering** | 12개 파일만으로 D7 난이도 10/10 통과 시스템 구축 |
| **Scaffolding** | SKILL.md(instruction) + scripts/(실행) + references/(데이터) + progress.md(상태) |
| **Context Engineering** | 컨텍스트 격리 + 파일 인터페이스 + 최소 컨텍스트 + 지식 외재화 |
| **Harness Engineering** | Supervisor의 retry policy, 상태 관리, Stuck Detection |
| **MCP vs Skills** | Playwright는 MCP로 능력 제공, Skill이 사용법과 순서를 정의 |
| **Just files. Real power.** | SKILL.md 작성 = 마크다운 파일 만들기. 프로토콜, 서버, 복잡한 설정 없음 |

---

## 10. 핵심 메시지

이 시스템은 **마크다운 파일 12개**로 구축되었습니다.

- 서버 없음
- 프로토콜 없음
- 복잡한 설정 없음
- Python 스크립트 2개 + 환경변수 파일 2개 + SKILL.md 8개

그 결과: D7 난이도(정답률 4.49%) 문제를 포함해 **10/10 전문제 통과**.

> **"파일만 추가하면, 나머지는 Agent Harness가 알아서 합니다."**

---

*이 분석은 세미나 발표의 부록(Appendix) 또는 심화 자료로 활용할 수 있습니다.*
