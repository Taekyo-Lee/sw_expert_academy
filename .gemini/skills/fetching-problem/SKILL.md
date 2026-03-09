---
name: fetching-problem
description: Fetch a problem statement from SW Expert Academy and save it locally.
argument-hint: <problem_id>
---

Fetch problem **$0** from SW Expert Academy using Playwright MCP and save it as a local file.

## Arguments

| Argument | Position | Required | Description |
|----------|----------|----------|-------------|
| `$0` | first | Yes | The problem number (e.g., `12345` or `VH1234`). |

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

## How to use Playwright MCP

This skill uses the **Playwright MCP server** (`mcp__playwright__*` tools) to control a headless browser.
Key tools and their usage:

| Tool | Purpose |
|------|---------|
| `mcp__playwright__browser_navigate` | Navigate to a URL (`url` param) |
| `mcp__playwright__browser_snapshot` | Get an accessibility snapshot of the current page (returns structured text, not HTML) |
| `mcp__playwright__browser_click` | Click an element by its `ref` number from a snapshot |
| `mcp__playwright__browser_type` | Type text into a focused/clicked element (`text` param, optional `submit: true` to press Enter) |
| `mcp__playwright__browser_wait` | Wait for a specified time in ms (`time` param) — use to let pages load |

General workflow:
1. `browser_navigate` to a URL.
2. `browser_snapshot` to see the page content and element `ref` numbers.
3. `browser_click` on a `ref` to interact with an element (input field, button, link).
4. `browser_type` to enter text into the focused element.
5. Repeat snapshot → click/type as needed.

## Step 1: Log in

**If `{base_url}` is `https://swexpertacademy.samsung.com`** (company SSO):
- Skip login entirely — SSO handles authentication automatically.
- `browser_navigate` to `{base_url}` and `browser_snapshot` to verify the page loads successfully.

**Otherwise** (default ID/PW login):
1. `browser_navigate` to `{base_url}/main/identity/anonymous/loginPage.do`.
2. `browser_snapshot` to find the ID input field, password input field, and login button.
3. `browser_click` on the ID input `ref`, then `browser_type` with the `SWEA_ID` value.
4. `browser_click` on the password input `ref`, then `browser_type` with the `SWEA_PW` value.
5. `browser_click` on the login button `ref`.
6. `browser_wait` for 2000ms, then `browser_snapshot` to confirm login succeeded (URL should no longer contain `loginPage`).

## Step 2: Search for the problem

1. `browser_navigate` to `{base_url}/main/code/problem/problemList.do`.
2. `browser_snapshot` to find the search input (placeholder: "문제 번호, 키워드").
3. `browser_click` on the search input `ref`, then `browser_type` with `$0` and `submit: true`.
4. `browser_wait` for 2000ms, then `browser_snapshot` to see search results.
5. Find the link for problem $0 and `browser_click` on it.

## Step 3: Read the problem

1. `browser_wait` for 2000ms after navigating to the problem detail page.
2. `browser_snapshot` to read the full problem statement.
3. If the snapshot is truncated or incomplete, scroll down and snapshot again.
4. Extract:
   - Problem title and difficulty
   - Constraints (time limit, memory limit)
   - Full problem description
   - Input format
   - Output format
   - Sample test cases and expected outputs

## Step 4: Save the problem

1. **Create the directory first** using the Bash tool: `mkdir -p ./problem_bank/$0`
2. Save the extracted problem statement to: `./problem_bank/$0/problem.md`
3. Also save a full-page screenshot to: `./problem_bank/$0/problem_screenshot.png` (use `browser_take_screenshot` with `fullPage: true`) — this preserves diagrams/images that the accessibility snapshot cannot capture.

Use markdown formatting. Include all sections (title, constraints, description, I/O format, sample cases).

## Step 5: Close the browser

After saving the problem, call `browser_close` to shut down the browser instance. Leave Playwright MCP enabled — other skills may need it.
