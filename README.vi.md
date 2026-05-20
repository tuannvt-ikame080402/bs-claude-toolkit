# bs-claude-toolkit

Skill Claude Code chạy quy trình sprint 5 bước có cấu trúc — từ planning qua integration testing đến review cuối.

> 🇬🇧 [Read in English](README.md)

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SPRINT WORKFLOW                                   │
├───┬─────────────────────────────────────────────────────────────────────────┤
│ 1 │  Claude  /bs-claude-toolkit plan [scope] <task>                         │
│   │          → Sprint plan · Impact analysis · Risk assessment              │
├───┼─────────────────────────────────────────────────────────────────────────┤
│ 2 │  Codex   Implement theo plan                                            │
├───┼─────────────────────────────────────────────────────────────────────────┤
│ 3 │  Claude  /bs-claude-toolkit test [scope]                                │
│   │          → Contract tests (BE↔FE) · E2E scaffold · Test plan doc        │
├───┼─────────────────────────────────────────────────────────────────────────┤
│ 4 │  Codex   Điền test logic · Chạy tests · Tạo changelog + testlog        │
├───┼─────────────────────────────────────────────────────────────────────────┤
│ 5 │  Claude  /bs-claude-toolkit review [scope]                              │
│   │          → Code quality · Security · Regression check · Deliverables   │
└───┴─────────────────────────────────────────────────────────────────────────┘
```

> Gõ `/bs-claude-toolkit` không có argument để xem project health, trạng thái sprint đang mở, và tất cả lệnh có sẵn.

---

## Các lệnh

| Lệnh | Ai chạy | Kết quả |
|------|---------|---------|
| `/bs-claude-toolkit plan [scope] <task>` | Claude | `sprint-N-slug.md` — context, phân tích, impact, risk, test cases |
| `/bs-claude-toolkit test [scope]` | Claude | Contract test scaffold + E2E scaffold + test plan doc |
| `/bs-claude-toolkit review [scope]` | Claude | Review report — plan compliance, code quality, security, regression, deliverables |
| `/bs-claude-toolkit [scope]` | Claude | Project brief — stack, sprint health, DoD status, next action |

**Scope** là tuỳ chọn. Bỏ qua để áp dụng toàn bộ submodule, hoặc truyền `be` / `fe` để focus vào một.

---

## Từng bước làm gì

### `/plan` — Lập kế hoạch sprint

Claude chạy research scripts trên codebase, rồi viết plan có cấu trúc:

- **Context** — quyết định từ sprint trước, pattern hiện tại
- **Root cause / gap** — tại sao cần làm và đang thiếu gì
- **Impact analysis** — file nào khác đang gọi vào vùng sẽ thay đổi
- **Risk assessment** — thấp / trung / cao kèm cách giảm thiểu
- **Test cases** — happy, edge, và failure case định nghĩa trước
- **Definition of Done** — checklist Codex làm theo

**Ví dụ:**

```
/bs-claude-toolkit plan fix video retry not triggering
```

Claude tạo ra `be/docs/plan/sprint-7-fix-video-retry.md`:

```
## Phân tích
Root cause: VideoService.retry() không check trạng thái PENDING trước khi gọi
File: be/services/video_service.py:143

## Impact Analysis
| File bị ảnh hưởng       | Lý do                              |
| be/tasks/video_tasks.py | gọi retry() trong Celery task      |
| be/api/video_views.py   | expose /api/videos/:id/retry       |

## Risk Assessment
| Rủi ro           | Mức độ | Cách giảm thiểu              |
| Race condition   | trung  | Dùng DB-level locking        |
```

---

### `/test` — Tạo integration test

Claude đọc diff, trích xuất API contract, và viết scaffold file cho Codex điền:

```
Contract tests  →  backend/tests/integration/test_{slug}.{ext}
E2E tests       →  frontend/tests/e2e/{slug}.spec.{ext}
Test plan doc   →  {submodule}/docs/test/{YYYYMMDD}-{HHMM}-test-{slug}.md
```

**Ví dụ** — sau khi Codex implement fix video retry:

```
/bs-claude-toolkit test
```

Claude tạo `backend/tests/integration/test_fix_video_retry.py`:

```python
class TestVideoRetry:
    def test_retry_succeeds_when_pending(self, client, auth_headers, pending_video):
        # TODO: Codex — gọi endpoint retry và verify trạng thái thay đổi
        response = client.post(f"/api/videos/{pending_video.id}/retry",
                               headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "running"

    def test_retry_rejected_when_already_running(self, client, auth_headers, running_video):
        # TODO: Codex — verify 409 khi video đang chạy
        response = client.post(f"/api/videos/{running_video.id}/retry",
                               headers=auth_headers)
        assert response.status_code == 409

    def test_unauthorized(self, client):
        response = client.post("/api/videos/1/retry")
        assert response.status_code == 401
```

Và `frontend/tests/e2e/fix-video-retry.spec.ts`:

```typescript
test.describe("Video retry flow", () => {
  test("user can retry a failed video", async ({ page }) => {
    // TODO: Codex — navigate đến video detail page
    await page.goto("/videos/failed-video-id");
    // TODO: Codex — click retry button và verify UI state
    await page.click("[data-testid=retry-btn]");
    await expect(page.locator("[data-testid=status]")).toHaveText("Processing...");
  });

  test("retry button disabled when video is running", async ({ page }) => {
    // TODO: Codex — verify button bị disabled với running video
    await page.goto("/videos/running-video-id");
    await expect(page.locator("[data-testid=retry-btn]")).toBeDisabled();
  });
});
```

- **Contract tests** verify BE endpoint trả đúng shape FE expect — chạy không cần browser
- **E2E tests** simulate user flow từ UI đến BE
- Scaffold dùng framework thực tế của project (auto-detect từ deps)
- `# TODO: Codex` đánh dấu mọi chỗ cần điền logic

---

### `/review` — Review cuối

Claude đọc toàn bộ diff và apply checklist nhiều section:

| Section | Kiểm tra |
|---------|---------|
| 📋 Plan compliance | Mọi file trong plan đã implement · Mọi bước có bằng chứng · Không scope creep |
| 🔍 Code quality | Không dead code · Không silent error · Tên self-documenting |
| 🔒 Security | Input validation · SQL injection · XSS · Auth/authz · IDOR · PII exposure |
| ⚡ Performance | N+1 query · Unbounded query · Loop complexity · Cache invalidation |
| 🧪 Tests | Happy + edge + failure covered · Không xóa test · Tên có nghĩa |
| 🔁 Regression | Callers của function thay đổi được kiểm tra compatibility |
| 🔗 BE↔FE sync | API contract nhất quán giữa BE changes và FE changes |
| 📦 Deliverables | Changelog · Test doc · Testlog — tồn tại và không phải stub |

**Ví dụ output:**

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

Output: `✓ LGTM` hoặc danh sách blocking issues ưu tiên cho Codex fix.

---

## Cài đặt (một lần mỗi máy)

### Bước 1 — Clone toolkit

```bash
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit
```

Claude Code tự nhận diện skill. Dùng `/bs-claude-toolkit` từ bất kỳ project nào.

---

### Bước 2 — Cài vào project

Chạy từ thư mục gốc project:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py
```

Tạo ra `CLAUDE.md` (template context) và `.bs-toolkit.json` (config team).
Thay `[BE_DIR]` / `[FE_DIR]` trong `CLAUDE.md` bằng tên thư mục thực tế.

---

### Bước 3 — Chạy skill

```
/bs-claude-toolkit
```

Skill tự detect stack từ project files và cache vào `.bs-toolkit.json`. Mọi lần sau dùng cache — không detect lại.

---

## Ví dụ sử dụng

```
# Plan task
/bs-claude-toolkit plan fix video retry not triggering
/bs-claude-toolkit plan be thêm pagination cho orders API
/bs-claude-toolkit plan fe refactor luồng upload asset

# Tạo integration tests sau khi Codex implement
/bs-claude-toolkit test
/bs-claude-toolkit test be          ← chỉ contract tests cho BE
/bs-claude-toolkit test fe          ← chỉ E2E tests cho FE

# Review sau khi Codex điền tests và tạo docs
/bs-claude-toolkit review
/bs-claude-toolkit review be        ← chỉ review backend

# Brief — kiểm tra project health
/bs-claude-toolkit                  ← stack + trạng thái sprint + next action
/bs-claude-toolkit be               ← scope chỉ backend
```

---

## Các thành phần

### `SKILL.md`

File skill chính. Claude Code tự load khi clone vào `~/.claude/skills/`. Chứa logic 6 phase: load config, detect stack, sprint intelligence, phân loại task, thực thi theo mode (`plan` / `test` / `review` / `brief`), và proactive warnings.

---

### `scripts/`

| Script | Chức năng |
|--------|-----------|
| `doc_context.py` | Tìm trong sprint plan, changelog, test doc theo keyword. Hỗ trợ `--scope be/fe`. |
| `code_research.py` | Tìm trong code theo keyword, nhóm theo layer. Hỗ trợ `--scope`. |
| `reorder_docs.py` | Sắp xếp lại thứ tự doc files theo commit time sau merge conflict. |
| `install.py` | Setup đầy đủ — cài rules cho từng AI tool, tạo config, chạy stack wizard (`--setup-stack`). |

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py pagination
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py --scope be retry
python ~/.claude/skills/bs-claude-toolkit/scripts/reorder_docs.py --dry-run
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
```

---

### `adapters/`

Rules files cho AI coding tool khác ngoài Claude Code. Dạy tool đó cùng workflow: load context, research trước khi code, planning vs execution, và review checklist.

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

File mẫu được copy vào project khi chạy `install.py`.

| File | Mục đích |
|------|---------|
| `CLAUDE.md` / `CLAUDE.vi.md` | Context cho Claude Code |
| `AGENTS.md` / `AGENTS.vi.md` | Context cho Codex (OpenAI) |
| `.bs-toolkit.json` | Config team — `stack_profile` và `modules` name mapping |

---

## Cập nhật

```bash
git -C ~/.claude/skills/bs-claude-toolkit pull --ff-only
```

Sau đó chạy lại installer để sync adapter rules:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
```

> `.bs-toolkit.json` và `CLAUDE.md` không bị ghi đè — chỉ adapter rules trong `.cursor/rules/` và `.windsurf/rules/` được cập nhật.

---

## Yêu cầu

- Python 3.8+ (stdlib only)
- Claude Code CLI
