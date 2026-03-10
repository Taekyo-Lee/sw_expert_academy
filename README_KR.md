# SW Expert Academy 솔버

[SW Expert Academy](https://swexpertacademy.com/) 코딩 문제를 Python 3.7 (PyPy 3.7) 기반으로 자동 풀이하는 AI 솔브 루프입니다. 공개 사이트와 [삼성 사내 미러](https://swexpertacademy.samsung.com/) 모두 지원합니다.

## 설정

`.env` 예시 파일을 복사한 뒤 값을 채워 넣으세요:

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

`fetching-problem`, `submitting-solution` 스킬(및 `solving-problem --auto`)은 헤드리스 브라우저를 제어하기 위해 **Playwright MCP 서버**가 필요합니다. 해당 스킬을 사용하기 전에 에이전트의 MCP 설정에서 활성화하세요. 미설정 시 스킬이 이를 감지하고 안내합니다.

## 빠른 시작

```
fetching-problem 24399        # 문제 가져오기 (사내 미러에서는 VH1234 등)
solving-problem 24399          # 전체 풀이 루프 시작
```

또는 자연어로 요청하세요: *"24399번 문제를 처음부터 끝까지 풀어줘."*

## 작동 방식

솔버는 **계획 → 구현 → 스트레스 테스트 → 검증 → 제출 → 분석** 루프를 실행하며, 사용자가 온라인 저지에 제출하고 결과를 보고합니다.

### 흐름도

```
                 ┌─────────┐
                 │  계획    │  알고리즘 계획 생성 (plan_N.md)
                 └────┬─────┘
                      │
                 ┌────▼─────┐
            ┌───►│  구현     │  솔루션 구현 (solution_N.py) + 로컬 테스트
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
                 │  제출      │  사용자가 저지에 제출 후 결과 보고
                 └────┬──────┘
                      │
               통과? ─┤
              Yes     │ No
               │ ┌────▼──────┐
               │ │  분석      │  실패 진단 → plan_{N+1}.md
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
| **저지 실패 (WA/TLE/...)** | **분석 → `plan_{N+1}.md` 생성** | **예 (N → N+1)** |

즉, 각 시도 번호는 저지에 대한 실제 제출 한 건을 의미합니다.

### 재시도 제한

- 시도당 **3회** 구현 재시도 (로컬 테스트 실패)
- 시도당 **3회** 스트레스 테스트 시도 (TLE/RE)
- 시도당 **3회** 검증-구현 사이클
- 총 **10회** 시도 (저지 제출)

## 스킬

| 스킬 | 용도 |
|------|------|
| `fetching-problem <id>` | 문제 가져오기 → `problem.md` |
| `solving-problem <id> [--resume\|--restart]` | 전체 풀이 루프 (오케스트레이터) |
| `planning-solution <id> [trial]` | 알고리즘 계획 → `plan_N.md` |
| `writing-solution <id> [trial]` | 계획 구현 → `solution_N.py` + 로컬 테스트 |
| `stress-testing <id> <trial>` | 최대 크기 입력 스트레스 테스트 |
| `validating-solution <id> <trial>` | 저지 호환성 정적 코드 리뷰 |
| `diagnosing-failure <id> <trial> <verdict> [output_trial]` | 실패 진단 → 수정된 계획 |

## 프로젝트 구조

```
.env                                    # 인증 정보 (git 추적 제외)
env.example                             # .env 템플릿
problem_bank/{problem_id}/
  problem.md                          # 문제 설명
  progress.md                         # 풀이 루프 진행 로그
  plan_{trial_number}.md              # 시도별 알고리즘 계획
  python/solution_{trial_number}.py   # 시도별 솔루션
  tests/                              # 스트레스 테스트 입력 파일
```

## 진행 상황 추적

각 시도는 `progress.md`에 기록됩니다. 스트레스 테스트 재시도 후 통과한 예시:

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

세션은 이어서 진행할 수 있습니다 — `solving-problem <id> --resume`으로 중단된 지점부터 재개하세요.

## 제약 조건

- **`import sys` 금지** — I/O는 `input()` / `print()` 사용
- **외부 패키지 금지** (numpy, pandas 등)
- **왈러스 연산자 금지** (`:=`) — Python 3.8 이상 필요
