# SW Expert Academy 솔버

[SW Expert Academy](https://swexpertacademy.com/) 코딩 문제를 Python 3.7 (PyPy 3.7)로 자동 풀이하는 AI 도구입니다. 공개 사이트와 [삼성 사내 사이트](https://swexpertacademy.samsung.com/)를 모두 지원합니다.

## 설정

`env.example`을 `.env`로 복사한 뒤 값을 채워 넣으세요:

```bash
cp env.example .env
```

| 변수 | 설명 |
|------|------|
| `SWEA_BASE_URL` | `https://swexpertacademy.com` (일반) 또는 `https://swexpertacademy.samsung.com` (사내) |
| `SWEA_ID` | 로그인 이메일 (일반 사이트 전용 — 사내는 SSO 사용) |
| `SWEA_PW` | 로그인 비밀번호 (일반 사이트 전용) |

사내 사이트(`swexpertacademy.samsung.com`)에서는 SSO가 자동으로 인증을 처리하므로 `SWEA_ID`와 `SWEA_PW`가 필요하지 않습니다.

### Playwright MCP

`fetching-problem`, `submitting-solution` (및 `solving-problem --auto`)은 브라우저 자동화를 위해 **Playwright MCP 서버**가 필요합니다. 사용 전에 에이전트의 MCP 설정에서 활성화하세요. 미설정 시 안내 메시지가 표시됩니다.

## 빠른 시작

```
fetching-problem 24399        # 문제 가져오기 (사내 사이트에서는 VH1234 등)
solving-problem 24399          # 전체 풀이 루프 시작
```

또는 자연어로 요청하세요: *"24399번 문제를 처음부터 끝까지 풀어줘."*

## 작동 방식

**계획 → 구현 → 스트레스 테스트 → 검증 → 제출 → 분석** 과정을 반복하며, 사용자가 온라인 저지에 제출한 뒤 결과를 입력하면 다음 단계로 진행합니다. 각 스킬은 별도의 sub agent로 실행되어 context를 분리하고, orchestrator가 작업을 위임할 수 있게 합니다.

### 흐름도

```
                 ┌─────────┐
                 │  계획    │  알고리즘 계획 생성 (plan_N.md)
                 └────┬─────┘
                      │
                 ┌────▼─────┐
            ┌───►│  구현     │  solution_N.py 작성 + 로컬 테스트
            │    └────┬──────┘
            │         │
            │    로컬 테스트 실패?──── Yes ──► plan_N.md 수정 (덮어쓰기) ──┐
            │         │ No                                                │
            │    ┌────▼──────┐                                            │
            │◄───│스트레스    │◄───────────────────────────────────────────┘
            │    │테스트      │
        수정 │    └────┬──────┘
      plan_N.md  실패 (TLE/RE)?──── Yes ──► plan_N.md 수정 (덮어쓰기) ──► 구현 ──► 스트레스 테스트
     (덮어쓰기)      │ No
            │    ┌────▼──────┐
            └────│  검증      │  정적 코드 리뷰
                 └────┬──────┘
                      │ Pass
                 ┌────▼──────┐
                 │  제출      │  온라인 저지에 제출 후 결과 입력
                 └────┬──────┘
                      │
               통과? ─┤
              Yes     │ No
               │ ┌────▼──────┐
               │ │  분석      │  실패 원인 분석 → plan_{N+1}.md
               │ └────┬──────┘
               │      │
               │      └──► 다음 시도 (N+1) ──► 구현
               │
              완료!
```

### 핵심 설계: 시도 번호는 언제 증가하는가?

**저지 판정 실패 후에만 증가합니다.** 그 외에는 동일 시도 내에서 재시도합니다:

| 실패 유형 | 처리 방법 | 시도 N 변경 여부 |
|-----------|-----------|------------------|
| 로컬 테스트 실패 | `plan_N.md` 수정, `solution_N.py` 재작성 | 아니오 (동일 N) |
| 스트레스 테스트 실패 | `plan_N.md` 수정, `solution_N.py` 재작성 | 아니오 (동일 N) |
| 검증 실패 | `solution_N.py` 재작성 | 아니오 (동일 N) |
| **저지 실패 (WA/TLE/...)** | **원인 분석 → `plan_{N+1}.md` 생성** | **예 (N → N+1)** |

즉, 시도 번호 하나가 실제 제출 한 건에 대응합니다.

### 재시도 제한

- 시도당 **3회** 구현 재시도 (로컬 테스트 실패)
- 시도당 **3회** 스트레스 테스트 시도 (TLE/RE)
- 시도당 **3회** 검증-구현 사이클
- 총 **10회** 시도 (저지 제출)

## 스킬

| 스킬 | 용도 |
|------|------|
| `fetching-problem <id>` | 문제 가져오기 → `problem.md` |
| `solving-problem <id> [--resume\|--restart]` | 전체 풀이 루프 실행 |
| `planning-solution <id> [trial]` | 알고리즘 계획 → `plan_N.md` |
| `writing-solution <id> [trial]` | 계획 구현 → `solution_N.py` + 로컬 테스트 |
| `stress-testing <id> <trial>` | 최대 크기 입력으로 성능 테스트 |
| `validating-solution <id> <trial>` | 제출 전 코드 리뷰 |
| `diagnosing-failure <id> <trial> <verdict> [output_trial]` | 실패 원인 분석 → 수정된 계획 |

## 프로젝트 구조

```
.env                                    # 인증 정보 (git 추적 제외)
env.example                             # .env 템플릿
problem_bank/{problem_id}/
  problem.md                          # 문제 설명
  progress.md                         # 진행 로그
  plan_{trial_number}.md              # 시도별 풀이 계획
  python/solution_{trial_number}.py   # 시도별 풀이 코드
  tests/                              # 테스트 입력 파일
```

## 진행 상황 추적

각 시도는 `progress.md`에 기록됩니다. 아래는 스트레스 테스트 재시도 후 통과한 예시입니다:

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

`solving-problem <id> --resume`으로 중단된 지점부터 이어서 진행할 수 있습니다.

## 제약 조건

- **`import sys` 금지** — I/O는 `input()` / `print()` 사용
- **외부 패키지 금지** (numpy, pandas 등)
- **walrus operator 금지** (`:=`) — Python 3.8 이상 필요
