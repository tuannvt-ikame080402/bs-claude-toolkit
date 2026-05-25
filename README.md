# bs-claude-toolkit

A Claude Code skill that runs a structured, 3-step AI-assisted sprint workflow — from planning (with test scaffold) through implementation to final review.

> 🇻🇳 [Đọc bằng tiếng Việt](README.vi.md)

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SPRINT WORKFLOW                                   │
├───┬─────────────────────────────────────────────────────────────────────────┤
│ 1 │  Claude  /bs-claude-toolkit plan [scope] <task>                         │
│   │          → Sprint plan · Impact analysis · Risk assessment              │
│   │          → Contract test scaffold · E2E scaffold · Test plan doc        │
├───┼─────────────────────────────────────────────────────────────────────────┤
│ 2 │  Codex   Implement · Fill test TODOs · Run tests                        │
│   │          → Create changelog + testlog                                   │
├───┼─────────────────────────────────────────────────────────────────────────┤
│ 3 │  Claude  /bs-claude-toolkit review [scope]                              │
│   │          → Code quality · Security · Regression check · Deliverables   │
└───┴─────────────────────────────────────────────────────────────────────────┘
```

> Type `/bs-claude-toolkit` with no arguments to see project health, active sprint status, and all available commands.

---

## Commands

| Command | Who | What it produces |
|---------|-----|-----------------|
| `/bs-claude-toolkit plan [scope] <task>` | Claude | `sprint-N-slug.md` + test scaffold — context, analysis, impact, risk, test cases |
| `/bs-claude-toolkit test [scope]` | Claude | Contract test scaffold + E2E scaffold + test plan doc *(standalone — optional)* |
| `/bs-claude-toolkit review [scope]` | Claude | Review report — plan compliance, code quality, security, regression, deliverables |
| `/bs-claude-toolkit [scope]` | Claude | Project brief — stack, sprint health, DoD status, next action |

**Scope** is optional. Omit for all submodules, or pass `be` / `fe` to focus on one.

---

## What each step does

### `/plan` — Sprint planning

Claude runs research scripts against your codebase, then writes a structured plan:

- **Context** — relevant past sprint decisions, existing patterns
- **Root cause / gap** — why this needs doing and what's missing
- **Impact analysis** — which other files call into the area being changed
- **Risk assessment** — low / medium / high with mitigation steps
- **Test cases** — happy, edge, and failure cases defined upfront
- **Definition of Done** — checklist Codex works against

**Example:**

```
/bs-claude-toolkit plan fix video retry not triggering
```

Claude creates `be/docs/plan/sprint-7-fix-video-retry.md`:

```
## Analysis
Root cause: VideoService.retry() does not check PENDING state before calling
File: be/services/video_service.py:143

## Impact Analysis
| Affected file              | Why                                    |
| be/tasks/video_tasks.py    | calls retry() inside Celery task       |
| be/api/video_views.py      | exposes /api/videos/:id/retry          |

## Risk Assessment
| Risk              | Level  | Mitigation                  |
| Race condition    | medium | Use DB-level locking        |
```

---

### `/test` — Integration test generation *(standalone)*

> **In the main workflow, test scaffold is generated automatically at the end of `/plan`.** Use `/test` as a standalone command when you need to regenerate scaffolds after implementation (e.g. scope changed, endpoints evolved).

Claude reads the diff, extracts the API contract surface, and writes scaffold files Codex fills in:

```
Contract tests  →  backend/tests/integration/test_{slug}.{ext}
E2E tests       →  frontend/tests/e2e/{slug}.spec.{ext}
Test plan doc   →  {submodule}/docs/test/{YYYYMMDD}-{HHMM}-test-{slug}.md
```

**Example** — standalone regeneration after scope change:

```
/bs-claude-toolkit test
```

Claude writes `backend/tests/integration/test_fix_video_retry.py`:

```python
class TestVideoRetry:
    def test_retry_succeeds_when_pending(self, client, auth_headers, pending_video):
        # TODO: Codex — call retry endpoint and verify status change
        response = client.post(f"/api/videos/{pending_video.id}/retry",
                               headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "running"

    def test_retry_rejected_when_already_running(self, client, auth_headers, running_video):
        # TODO: Codex — verify 409 when video is already running
        response = client.post(f"/api/videos/{running_video.id}/retry",
                               headers=auth_headers)
        assert response.status_code == 409

    def test_unauthorized(self, client):
        response = client.post("/api/videos/1/retry")
        assert response.status_code == 401
```

And `frontend/tests/e2e/fix-video-retry.spec.ts`:

```typescript
test.describe("Video retry flow", () => {
  test("user can retry a failed video", async ({ page }) => {
    // TODO: Codex — navigate to video detail page
    await page.goto("/videos/failed-video-id");
    // TODO: Codex — click retry button and verify UI state
    await page.click("[data-testid=retry-btn]");
    await expect(page.locator("[data-testid=status]")).toHaveText("Processing...");
  });

  test("retry button disabled when video is running", async ({ page }) => {
    // TODO: Codex — verify button is disabled for running video
    await page.goto("/videos/running-video-id");
    await expect(page.locator("[data-testid=retry-btn]")).toBeDisabled();
  });
});
```

- **Contract tests** verify every BE endpoint returns the exact shape FE expects — run without a browser
- **E2E tests** simulate full user flows from UI through to BE response
- Scaffold uses your project's actual test framework (auto-detected from deps)
- `# TODO: Codex` marks every place Codex needs to fill in logic

---

### `/review` — Final code review

Claude reads the full diff and applies a multi-section checklist:

| Section | Checks |
|---------|--------|
| 📋 Plan compliance | Every planned file implemented · Every step has evidence · No scope creep |
| 🔍 Code quality | No dead code · No silent errors · Self-documenting names |
| 🔒 Security | Input validation · SQL injection · XSS · Auth/authz · IDOR · PII exposure |
| ⚡ Performance | N+1 queries · Unbounded queries · Loop complexity · Cache invalidation |
| 🧪 Tests | Happy + edge + failure covered · No tests deleted · Meaningful names |
| 🔁 Regression | Callers of changed functions checked for compatibility |
| 🔗 BE↔FE sync | API contract consistent between BE changes and FE changes |
| 📦 Deliverables | Changelog · Test doc · Testlog — exist and are not stubs |

**Example output:**

```
╔══════════════════════════════════════════════════════════════╗
  CODE REVIEW  sprint-7-fix-video-retry
╚══════════════════════════════════════════════════════════════╝

  Scope:   be · fe
  Changed: 8 files  ·  +142 / -37 lines

  📋 PLAN COMPLIANCE
  ✓  be/services/video_service.py — implemented
  ✓  be/api/video_views.py — implemented
  ✗  Step 3: "Add DB-level lock" — no evidence in diff

  🔒 SECURITY
  ✓  Auth enforced on /api/videos/:id/retry
  ✗  be/api/video_views.py:67 — video ownership not checked (IDOR risk)

  📦 DELIVERABLES
  ✓  changelog — complete
  ✓  test doc  — complete
  ✗  testlog   — missing

  VERDICT
  ✗ 2 blocking issues — return to Codex before merging.
    1. be/services/video_service.py — add DB lock (planned but missing)
    2. be/api/video_views.py:67 — add ownership check
```

Output: `✓ LGTM` or a prioritised list of blocking issues for Codex to fix.

---

## Setup (one-time per machine)

### Step 1 — Clone the toolkit

```bash
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit
```

Claude Code auto-discovers the skill. Use `/bs-claude-toolkit` from any project.

---

### Step 2 — Install into your project

Run from your project root:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py
```

Creates `CLAUDE.md` (project context template) and `.bs-toolkit.json` (team config).
Replace `[BE_DIR]` / `[FE_DIR]` in `CLAUDE.md` with your actual directory names.

---

### Step 3 — Run the skill

```
/bs-claude-toolkit
```

The skill auto-detects your stack from project files and caches it into `.bs-toolkit.json`. All future runs use the cache — no re-detection needed.

---

## Usage examples

```
# Plan a task
/bs-claude-toolkit plan fix video retry not triggering
/bs-claude-toolkit plan be add pagination to orders API
/bs-claude-toolkit plan fe refactor asset upload flow

# Regenerate tests standalone (optional — plan already generates scaffold)
/bs-claude-toolkit test
/bs-claude-toolkit test be          ← contract tests for BE only
/bs-claude-toolkit test fe          ← E2E tests for FE only

# Review after Codex implements, runs tests, and creates docs
/bs-claude-toolkit review
/bs-claude-toolkit review be        ← focus review on backend

# Brief — project health check
/bs-claude-toolkit                  ← stack + sprint status + next action
/bs-claude-toolkit be               ← scope to backend only
```

---

## Components

### `SKILL.md`

The core skill file. Claude Code loads this automatically. Contains logic for 6 phases: config loading, stack detection, sprint intelligence, task classification, mode execution (`plan` / `test` / `review` / `brief`), and proactive warnings.

---

### `scripts/`

| Script | What it does |
|--------|-------------|
| `doc_context.py` | Search past sprint plans, changelogs, and test docs by keyword. Supports `--scope be/fe`. |
| `code_research.py` | Search current code by keyword, grouped by layer. Supports `--scope`. |
| `reorder_docs.py` | Re-sequence doc files by git commit time after a merge conflict. |
| `install.py` | Full setup — installs rules for each AI tool, generates config files, runs the stack wizard (`--setup-stack`). |

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py pagination
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py --scope be retry
python ~/.claude/skills/bs-claude-toolkit/scripts/reorder_docs.py --dry-run
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
```

---

### `adapters/`

Rules files for AI coding tools other than Claude Code. Teaches each tool the same workflow: context loading, research-before-coding, planning vs execution mode, and the review checklist.

| File | Tool |
|------|------|
| `cursor.mdc` / `cursor.vi.mdc` | Cursor |
| `windsurf.md` / `windsurf.vi.md` | Windsurf |

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
```

---

### `templates/`

Starting-point files copied into your project during `install.py`.

| File | Purpose |
|------|---------|
| `CLAUDE.md` / `CLAUDE.vi.md` | Project context for Claude Code |
| `AGENTS.md` / `AGENTS.vi.md` | Project context for Codex (OpenAI) |
| `.bs-toolkit.json` | Team config — `stack_profile` and `modules` name mapping |

---

## Updating

```bash
git -C ~/.claude/skills/bs-claude-toolkit pull --ff-only
```

Then re-run the installer to sync adapter rules:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
```

> Your `.bs-toolkit.json` and `CLAUDE.md` are not overwritten — only adapter rules in `.cursor/rules/` and `.windsurf/rules/` are updated.

---

## Requirements

- Python 3.8+ (stdlib only)
- Claude Code CLI
