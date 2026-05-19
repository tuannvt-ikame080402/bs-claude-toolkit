---
description: Load project context, detect task type, compute next sprint number, suggest research commands, and output a full action brief before starting any task. Supports solo and split-team modes.
arguments: [scope | task-description]
---

Thực hiện tuần tự các phase sau.

---

## PHASE 0 — Đọc cấu hình team

### 0a. Đọc project config
Check `.bs-toolkit.json` ở root:
- Nếu tồn tại → đọc `team_mode` ("solo" | "split"), `modules`, `shared_docs`, `shared_files`
- Nếu không tồn tại → mặc định `team_mode = "solo"`

### 0b. Đọc personal config (override)
Check `.bs-toolkit.local.json` ở root (file này gitignored — per-developer):
- Nếu tồn tại → đọc `default_scope`, override mọi scope detection phía dưới

### 0c. Xác định scope cuối cùng

Ưu tiên theo thứ tự:
1. `$ARGUMENTS` (nếu khớp tên module / alias ngắn)
2. `default_scope` từ `.bs-toolkit.local.json`
3. Không scope (load tất cả)

Nếu `team_mode = "split"` **và không có scope nào** → **dừng ngay**, hiện:
```
⚠️  Split team mode detected. Bạn đang làm việc ở module nào?

    /bs-claude-toolkit be      → load BE context ([BE_DIR])
    /bs-claude-toolkit fe      → load FE context ([FE_DIR])
    /bs-claude-toolkit all     → load tất cả (fullstack session)

Tip: Tạo .bs-toolkit.local.json với {"default_scope": "be"} để không cần gõ mỗi lần.
```

---

## PHASE 1 — Load Context

### 1a. Root context (luôn luôn)
- Read `./CLAUDE.md`
- Read `./Agents.md` nếu tồn tại

### 1b. Phát hiện và filter submodule

**Solo mode:** Load tất cả submodule tìm được (subdir có `CLAUDE.md` / `Agents.md` / `docs/`)

**Split mode với scope:** Chỉ load submodule khớp scope.
- Dùng mapping từ `modules` trong config: `{ "be": "myapp-be" }` → scope "be" → load `myapp-be/`
- Nếu không có mapping → fallback partial match trên tên thư mục (như trước)

**Split mode với scope = "all":** Load tất cả, đánh dấu rõ module nào của ai.

### 1c. Load files từ submodule đã chọn
- Read `{subdir}/CLAUDE.md`
- Read `{subdir}/Agents.md` nếu tồn tại

### 1d. Extract và ghi nhớ
- Execution mode, tech stack, coding conventions, flow chính, API contract format
- Shared files (từ config `shared_files`) — sẽ dùng để cảnh báo conflict

---

## PHASE 2 — Sprint Intelligence

**Solo mode:** Scan TẤT CẢ `*/docs/plan/` → tìm N_max toàn project → next sprint = N_max + 1

**Split mode với scope:** Chỉ scan `{scoped-submodule}/docs/plan/`:
- Sprint numbers **độc lập** per-submodule
- BE có thể đang ở sprint-15, FE đang ở sprint-12 — đây là bình thường, không phải conflict
- Hiện: "BE next sprint: 16 · FE next sprint: 13" (nếu scope=all)

**Lấy N_max:**
1. Liệt kê files khớp `sprint-{N}-*.md` trong scoped dirs
2. Extract số N lớn nhất
3. next = N_max + 1 (nếu không có file nào → next = 1)
4. Ghi nhớ 3 sprint gần nhất để cho context

---

## PHASE 3 — Phân tích Task

Chỉ thực hiện nếu có task description trong `$ARGUMENTS` (phần còn lại sau scope filter).

### 3a. Phân loại task
| Loại | Keywords |
|------|---------|
| **new-feature** | implement, add, create, build, tạo, thêm |
| **bug-fix** | fix, bug, lỗi, sửa, broken, không hoạt động |
| **refactor** | refactor, optimize, clean, tái cấu trúc |
| **question** | tại sao, how, explain, giải thích, cơ chế |
| **architecture** | design, plan, kiến trúc, approach, strategy |

### 3b. Trích keywords cho research
Lấy noun/domain keywords, bỏ stop words.
Ví dụ: "fix video retry không trigger" → `video`, `retry`, `trigger`

### 3c. Conflict check (chỉ split mode)
Nếu task description hoặc keywords liên quan đến:
- Root `CLAUDE.md` hoặc files trong `shared_files` config → cảnh báo cần coordination
- API contract → cảnh báo phải sync với dev còn lại trước khi thay đổi

---

## PHASE 4 — Resolve Script Path

Kiểm tra theo thứ tự:
1. `./scripts/doc_context.py` tồn tại → `SCRIPT_CMD = "python scripts/"`
2. Không có → `SCRIPT_CMD = "python ~/.claude/skills/bs-claude-toolkit/scripts/"`

---

## PHASE 5 — Output Action Brief

```
╔══════════════════════════════════════════════════════════════╗
  PROJECT BRIEF  [{team_mode} mode{" · scope: "+scope if split}]
╚══════════════════════════════════════════════════════════════╝

  Mode:        [Planning | Execution]
  Scope:       [tên submodule đang load, hoặc "all"]
  Stack:       [BE: framework/lang] · [FE: framework/lang]
  Next Sprint: [N]  (last: sprint-[N-1]-[tên])
               [Split mode: hiển thị per-module nếu scope=all]

──────────────────────────────────────────────────────────────
  OWNERSHIP (split mode only)
──────────────────────────────────────────────────────────────

  ✏️  Your zone:    [scoped-submodule]/
                    → Tự do sửa code và docs trong này

  🤝  Shared zone:  [shared_files list]
                    → Cần sync với team trước khi sửa

──────────────────────────────────────────────────────────────
  RESEARCH — chạy trước khi bắt đầu
──────────────────────────────────────────────────────────────

  [SCRIPT_CMD]doc_context.py [keywords]
  [SCRIPT_CMD]doc_context.py --scope [module] [keywords]
  [SCRIPT_CMD]code_research.py [keywords]

──────────────────────────────────────────────────────────────
  WORKFLOW  [task-type]
──────────────────────────────────────────────────────────────

  new-feature:
    1. Research (doc + code)
    2. Tạo [module]/docs/plan/sprint-[N]-[slug].md
    3. Implement theo plan
    4. Tạo [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
    5. Tạo [module]/docs/test/[DATE]-test-[seq]-[slug].md

  bug-fix:
    1. Research → trace root cause
    2. Fix minimum scope, đúng layer
    3. Tạo [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md

  question / architecture:
    1. Research → phân tích → trả lời
    (không cần tạo file)

──────────────────────────────────────────────────────────────
  FILE NAMING  (today: [YYYYMMDD])
──────────────────────────────────────────────────────────────

  Plan:      [module]/docs/plan/sprint-[N]-[slug].md
  Changelog: [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
  Test:      [module]/docs/test/[DATE]-test-[seq]-[slug].md

  [seq] = đọc thư mục trước, đếm file có cùng ngày, +1

──────────────────────────────────────────────────────────────
  DEFINITION OF DONE
──────────────────────────────────────────────────────────────

  [ ] Code chạy được local
  [ ] Test pass: happy + edge + failure case
  [ ] Changelog tạo xong trong [module]/docs/changelog/
  [ ] Flow chính không bị phá
  [ ] API contract không thay đổi ngầm
  [ ] Không any (TS) · không print() (BE) · không hardcode secrets

══════════════════════════════════════════════════════════════
```

---

## PHASE 6 — Proactive Warnings

- **Thiếu `.bs-toolkit.json`** → "💡 Chưa có config. Chạy `install.py --mode split` để setup team mode."
- **Split mode, chạm shared_files** → "⚠️ File này là shared zone — cần sync với team trước."
- **Split mode, task liên quan API contract** → "⚠️ API contract thay đổi cần cả BE và FE đồng thuận."
- **Thiếu `docs/plan/`** trong module → "⚠️ Chưa có docs/plan/ — tạo thư mục trước khi viết plan."
- **Task là Execution nhưng mode mặc định Planning** → nhắc user confirm.

---

## Notes

- Sau khi in brief → **dừng, chờ user** — không tự bắt đầu implement
- Dùng ngày thực tế từ system date cho `[YYYYMMDD]`
- Split mode: sprint numbers per-submodule là bình thường, không phải bug
- `.bs-toolkit.local.json` không được commit vào git (phải có trong `.gitignore`)
