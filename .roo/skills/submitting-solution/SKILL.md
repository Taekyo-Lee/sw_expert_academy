---
name: submitting-solution
description: Submit a solution to SW Expert Academy via Playwright and return the judge verdict.
argument-hint: <problem_id> <trial_number>
---

Submit the solution for SW Expert Academy problem **$0**, trial **$1**, via Playwright MCP and return the judge verdict.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem ID (e.g., `12345` or `VH1234`). |
| `$1` | second | Yes | Trial number matching the solution file. |

## Paths

- **Solution file**: `./problem_bank/$0/python/solution_$1.py`

The solution file must exist. If it is missing, tell the user and stop.

## Prerequisites: Configuration

Read configuration from the `.env` file at:
`@./references/.env`

The file contains `SWEA_BASE_URL`, `SWEA_ID`, and `SWEA_PW`. Use `SWEA_BASE_URL` as `{base_url}` throughout this skill (all URLs below use this prefix). Never hardcode credentials or URLs.

## Step 0: Ensure Playwright MCP is connected

Playwright MCP is normally kept **disabled** to save memory. Before using this skill, ensure it is connected.

1. Attempt to call any Playwright MCP tool (e.g., `browser_snapshot`).
2. If the tool call **succeeds**, Playwright is already connected — proceed to Step 1.
3. If the tool call **fails** (tool not found / MCP server not connected):
   a. Inform the user: "The Playwright MCP server is not connected. Please enable it in your agent's MCP settings and restart, then re-run this skill."
   b. **Stop here** — do not proceed until the user restarts and re-invokes the skill.

> **Headless mode:** The Playwright MCP server is configured to run with `--headless`. Do not remove this flag.

## How to use Playwright MCP

This skill uses the **Playwright MCP server** (`mcp__playwright__*` tools) to control a headless browser.
Key tools and their usage:

| Tool | Purpose |
|------|---------|
| `mcp__playwright__browser_navigate` | Navigate to a URL (`url` param) |
| `mcp__playwright__browser_snapshot` | Get an accessibility snapshot of the current page (returns structured text, not HTML) |
| `mcp__playwright__browser_click` | Click an element by its `ref` number from a snapshot |
| `mcp__playwright__browser_type` | Type text into a focused/clicked element (`text` param, optional `submit: true` to press Enter) |
| `mcp__playwright__browser_wait_for` | Wait for a specified time in seconds (`time` param) or for text to appear (`text` param) |
| `mcp__playwright__browser_select_option` | Select an option from a dropdown (`ref` and `value` params) |
| `mcp__playwright__browser_tabs` | List, create, close, or select browser tabs |
| `mcp__playwright__browser_run_code` | Execute arbitrary Playwright JavaScript code |

General workflow:
1. `browser_navigate` to a URL.
2. `browser_snapshot` to see the page content and element `ref` numbers.
3. `browser_click` on a `ref` to interact with an element (input field, button, link).
4. `browser_type` to enter text into the focused element.
5. Repeat snapshot → click/type as needed.

## Step 1: Read the solution code

Read the solution file at `./problem_bank/$0/python/solution_$1.py` and store its contents. This will be pasted into the code editor.

## Step 2: Log in

**If `{base_url}` is `https://swexpertacademy.samsung.com`** (company SSO):
- Skip login entirely — SSO handles authentication automatically.
- `browser_navigate` to `{base_url}` and `browser_snapshot` to verify the page loads successfully.

**Otherwise** (default ID/PW login):
1. `browser_navigate` to `{base_url}/main/identity/anonymous/loginPage.do`.
2. `browser_snapshot` to find the ID input field, password input field, and login button.
3. `browser_click` on the ID input `ref`, then `browser_type` with the `SWEA_ID` value.
4. `browser_click` on the password input `ref`, then `browser_type` with the `SWEA_PW` value.
5. `browser_click` on the login button `ref`.
6. `browser_wait_for` for 2 seconds, then `browser_snapshot` to confirm login succeeded (URL should no longer contain `loginPage`).

## Step 3: Navigate to the problem

1. `browser_navigate` to `{base_url}/main/code/problem/problemList.do`.
2. `browser_snapshot` to find the search input (placeholder: "문제 번호, 키워드").
3. `browser_click` on the search input `ref`, then `browser_type` with the problem ID `$0` and `submit: true`.
4. `browser_wait_for` for 2 seconds, then `browser_snapshot` to see search results.
5. Find the link for problem $0 and `browser_click` on it.
6. `browser_wait_for` for 2 seconds to let the problem detail page load.

## Step 4: Open the solving page

1. `browser_snapshot` to find the "문제 풀기" (or "문제 풀러 가기" on company mirror) link on the problem detail page (upper-right area, calls `javascript:goProblem()`).
2. `browser_click` on it. This opens a **new tab** at `/main/solvingProblem/solvingProblem.do`.
3. `browser_tabs` with `action: "select"` and `index: 1` to switch to the new solving tab.
4. `browser_wait_for` for 2 seconds to let the solving page fully load.

## Step 5: Select Python language

1. `browser_snapshot` to find the Language combobox.
2. Check if "Python 3.7 (PyPy 7.3.9)" is already selected.
3. If not, `browser_select_option` on the Language combobox to select the Python option.

## Step 6: Paste the solution code

The code editor is a **CodeMirror** instance. The underlying `<textarea>` is hidden behind CodeMirror's overlay and cannot be clicked directly. Use `browser_run_code` to set the code via the CodeMirror API:

```js
async (page) => {
  const code = `<solution_code_here>`;
  await page.evaluate((codeStr) => {
    const cm = document.querySelector('.CodeMirror').CodeMirror;
    cm.setValue(codeStr);
  }, code);
}
```

**Important:** Escape backticks and `${` sequences in the solution code before embedding it in the JavaScript template literal. Alternatively, pass the code as a variable to `page.evaluate()`.

After setting the code, `browser_snapshot` to verify the editor shows the correct code (check the first and last lines).

## Step 7: Submit

1. `browser_snapshot` to find the "제출" (Submit) link at the bottom right.
2. `browser_click` on the "제출" link.
3. A **confirmation dialog** appears: "제출 가능 횟수가 1회 감소합니다. 정말로 제출하시겠습니까?"
4. `browser_snapshot` to find the "확인" (OK) button.
5. `browser_click` on "확인" to confirm submission.

## Step 8: Read the verdict

After confirming, the judge runs and a **result dialog** appears with the verdict. `browser_snapshot` to read the dialog text.

Parse the verdict from the dialog:

| Dialog text contains | Verdict |
|----------------------|---------|
| "Pass" or "정답" | **Pass** |
| "오답" (wrong answer) | **WA** |
| "Runtime error" or "런타임 에러" | **RE** |
| "Time limit" or "시간 초과" | **TLE** |
| "Memory limit" or "메모리 초과" | **MLE** |

The dialog may also contain details like "N개의 테스트케이스 중 M개가 맞았습니다" (M out of N test cases passed). Extract this information if available.

Click "확인" to dismiss the result dialog.

## Step 9: Clean up

1. Close the solving tab: `browser_tabs` with `action: "close"`.
2. Call `browser_close` to shut down the browser.

## Result

Report the verdict back to the orchestrator in this format:

> **Submit — {verdict}** (details: {M}/{N} test cases passed, if available)

The orchestrator (`solving-problem`) will use this verdict to decide the next step (congratulate on Pass, or proceed to Reflect on failure).
