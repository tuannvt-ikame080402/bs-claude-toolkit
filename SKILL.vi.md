---
description: "Ba mode: plan (research + tạo sprint doc), review (đọc git diff + apply checklist), brief (orientation). Load project context, detect stack, tính sprint tiếp theo."
arguments: "plan [scope] task | review [scope] | [scope] [task]"
---

## Sub-commands

| Lệnh | Ai chạy | Làm gì |
|------|---------|--------|
| `/bs-claude-toolkit plan [scope] task` | Claude | Research → tạo `sprint-N-slug.md` → dừng |
| `/bs-claude-toolkit review [scope]` | Claude | Đọc git diff → apply checklist → output findings |
| `/bs-claude-toolkit [scope]` | Claude | Chỉ orientation brief — không tạo file, không chạy script |

**Phân công:**
- **Claude** → `plan` + `review`
- **Codex** → implement + changelog + test doc + testlog + chạy tests

---

## PHASE 0 — Config & Stack Cache

### 0a. Đọc project config
Check `.bs-toolkit.json` ở root:
- Nếu tồn tại → đọc `modules` (mapping tên tùy chọn), `shared_files`, `stack_profile`
- Nếu không tồn tại → dùng mặc định

### 0b. Kiểm tra Stack Profile Cache

**Nếu `stack_profile` tồn tại và có ít nhất `lang_be` hoặc `lang_fe`:**
→ **⚡ FAST PATH** — dùng cache, bỏ qua Phase 1 hoàn toàn
  - Nạp trực tiếp: `lang_be`, `lang_fe`, `framework_be`, `framework_fe`, `arch`, `async_tech`, `database`, `custom_rules`, `main_flow`, `api_format`
  - Token tiêu thụ: ~100 token

**Nếu `stack_profile` không tồn tại hoặc rỗng:**
→ **🔍 FULL PATH** — chạy toàn bộ Phase 1
  - Token tiêu thụ: ~1500–3000 token

### 0c. Parse sub-command và scope

Từ đầu tiên của `$ARGUMENTS`:
- `plan`   → MODE = plan   · phần còn lại = `[scope?] mô tả task`
- `review` → MODE = review · phần còn lại = `[scope?]`
- khác     → MODE = brief  · tất cả = `[scope?] [task?]`

Xác định scope: nếu từ đầu tiên sau sub-command khớp tên submodule hoặc alias trong `.bs-toolkit.json` → SCOPE = submodule đó; nếu không → SCOPE = all.

---

## PHASE 1 — Load Context  *(chỉ chạy ở FULL PATH)*

### 1a. Root context
- Read `./CLAUDE.md`
- Read `./Agents.md` nếu tồn tại

### 1b. Phát hiện submodule

Tìm tất cả thư mục con trực tiếp có chứa `CLAUDE.md`, `Agents.md`, hoặc thư mục `docs/`.

Nếu `.bs-toolkit.json` có `modules` mapping (ví dụ: `{"be": "myapp-be"}`), dùng để resolve tên không chuẩn. Nếu không, detect theo nội dung.

Áp dụng SCOPE filter.

### 1c. Load files từ submodule đã chọn
- Read `{subdir}/CLAUDE.md`
- Read `{subdir}/Agents.md` nếu tồn tại

### 1d. Auto-detect stack profile

#### Nguồn 1 — Project files (chính xác nhất)

Scan các file trong submodule root:

| File | Language | Framework hints |
|------|----------|-----------------|
| `requirements.txt` / `pyproject.toml` / `Pipfile` | Python | flask→Flask · fastapi→FastAPI · django→Django · celery→async:Celery · rq→async:RQ |
| `package.json` | TypeScript/JS | next→Next.js · nuxt→Nuxt · react→React · vue→Vue · @angular→Angular · @nestjs→NestJS · express→Express · bull/bullmq→async:BullMQ |
| `go.mod` | Go | gin-gonic→Gin · labstack/echo→Echo · gofiber→Fiber |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | Java/Kotlin | spring-boot→Spring Boot · quarkus→Quarkus |
| `composer.json` | PHP | laravel/framework→Laravel · symfony→Symfony |
| `Gemfile` | Ruby | rails→Rails |
| `pubspec.yaml` | Dart | flutter→Flutter |
| `Cargo.toml` | Rust | axum→Axum · actix-web→Actix |
| `*.csproj` / `*.sln` | C# | Microsoft.AspNetCore→ASP.NET Core |

**Database detection** (từ deps):
`pymongo`/`motor` → MongoDB · `sqlalchemy`/`psycopg2` → PostgreSQL · `mysql2`/`pg` → MySQL · `redis`/`ioredis` → Redis

**Architecture detection** (từ cấu trúc thư mục):
- `controller(s)/` + `service(s)/` + `repositor*/` → `layered`
- `models/` + `views/` + `controllers/` → `MVC`
- `domain/` + `ports/` + `adapters/` → `hexagonal`
- `commands/` + `queries/` → `CQRS`
- Nhiều service directory độc lập → `microservices`

**TypeScript detection**: `tsconfig.json` hoặc `typescript` trong devDependencies.

#### Nguồn 2 — CLAUDE.md / Agents.md (fallback)

Đọc mục "Tech Stack", "Coding Conventions", "Architecture", "Worker" / "Queue".

#### Sau khi detect xong — tự động cache

Nếu detect được ít nhất `lang_be` hoặc `lang_fe`:
- Đọc `.bs-toolkit.json` (hoặc tạo mới nếu chưa có)
- Thêm/cập nhật `stack_profile` với giá trị detect được, giữ nguyên các key khác
- Ghi lại file

---

## PHASE 2 — Sprint Intelligence

Scan `*/docs/plan/` trong submodule đang scope:
1. Liệt kê files khớp `sprint-{N}-*.md`
2. Extract số N lớn nhất
3. next = N_max + 1 (không có file → next = 1)
4. Ghi nhớ 3 sprint gần nhất để cho context

---

## PHASE 3 — Phân tích Task  *(chỉ chạy ở plan + brief mode)*

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

---

## PHASE 4 — Resolve Script Path

1. `./scripts/doc_context.py` tồn tại → `SCRIPT_CMD = "python scripts/"`
2. Không có → `SCRIPT_CMD = "python ~/.claude/skills/bs-claude-toolkit/scripts/"`

---

## PHASE 5 — Execute by Mode

---

### MODE: brief  *(chỉ orientation — không tạo file, không chạy script)*

```
╔══════════════════════════════════════════════════════════════╗
  PROJECT BRIEF  [scope: all | tên-submodule]
╚══════════════════════════════════════════════════════════════╝

  Scope:       [submodule(s) đang load]
  Stack:       [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
               [arch] · async: [async_tech] · db: [database]
  Stack src:   [⚡ cached | 🔍 detected from project files]
  Next Sprint: [N]  (last: sprint-[N-1]-[tên])

──────────────────────────────────────────────────────────────
  WORKFLOW
──────────────────────────────────────────────────────────────

  1. Claude:  /bs-claude-toolkit plan [scope] [task]
              → research + tạo sprint-[N]-slug.md

  2. Codex:   tag plan → implement → changelog + test docs + chạy tests

  3. Claude:  /bs-claude-toolkit review [scope]
              → review git diff của Codex theo checklist

══════════════════════════════════════════════════════════════
```

---

### MODE: plan  *(Claude research + tạo sprint plan doc)*

**Bước 1 — Research**

Chạy cả hai script và đọc toàn bộ output trước khi viết bất cứ thứ gì:

```bash
[SCRIPT_CMD]doc_context.py [--scope SCOPE] [keywords]
[SCRIPT_CMD]code_research.py [--scope SCOPE] [keywords]
```

Phân tích output: quyết định liên quan từ sprint cũ, code pattern hiện tại và đường dẫn file, root cause (nếu bug-fix) hoặc gap hiện tại (nếu feature).

**Bước 2 — Tạo file plan**

Ghi vào: `[submodule]/docs/plan/sprint-[N]-[slug].md`

```markdown
# Sprint [N] — [Tên Task]

**Ngày:** [YYYYMMDD]
**Loại:** [new-feature | bug-fix | refactor]
**Phạm vi:** [submodule / các file chính]

## Context

[1–3 câu từ research — sprint liên quan, pattern hiện tại, quyết định đã có]

## Vấn đề / Mục tiêu

[Cần thay đổi gì và tại sao. Bug-fix: cái gì bị lỗi và khi nào. Feature: đang thiếu gì.]

## Phân tích

[Bug-fix: root cause với file:line tham chiếu.
 Feature: gap hiện tại, approach được chọn, trade-off.]

## Kế hoạch Implement

### Files cần sửa

| File | Thay đổi |
|------|----------|
| `path/to/file.py` | thay đổi gì và tại sao |

### Các bước

1. [Bước cụ thể]
2. [Bước cụ thể]

## Code Review Checklist

[Dán các checklist item phù hợp với stack + loại task này]

## Definition of Done

- [ ] Code chạy được local
- [ ] Tests pass: happy + edge + failure case
- [ ] Changelog tạo xong
- [ ] Test doc + test log tạo xong
- [ ] Flow chính không bị phá
- [ ] Không vi phạm language rules · Không hardcode secrets
```

**Bước 3 — Output**

```
✓ Plan tạo xong: [submodule]/docs/plan/sprint-[N]-[slug].md

Next → Codex:
  1. Tag [đường dẫn plan] vào context
  2. Implement theo plan
  3. Tạo docs/changelog/[YYYYMMDD]-[HHMM]-changelog-[slug].md
  4. Tạo docs/test/[YYYYMMDD]-[HHMM]-test-[slug].md
  5. Tạo docs/test/[YYYYMMDD]-[HHMM]-testlog-[slug].md

Codex xong → Claude: /bs-claude-toolkit review [scope]
```

---

### MODE: review  *(Claude đọc git diff + apply checklist)*

**Bước 1 — Đọc sprint plan**

Tìm sprint plan mới nhất trong từng submodule trong SCOPE:
```bash
ls {submodule}/docs/plan/sprint-*.md   # lấy N lớn nhất
```

Đọc toàn bộ file plan. Ghi nhớ:
- **Loại task** (new-feature / bug-fix / refactor)
- **Các file cần sửa** — bảng trong "Các file cần sửa"
- **Các bước** — danh sách trong "Các bước"
- **Checklist** — các item trong "Code Review Checklist" của plan

Nếu không có file plan → ghi chú "⚠ Không tìm thấy sprint plan — bỏ qua plan compliance check."

**Bước 2 — Đọc thay đổi**

Chạy các lệnh này **bên trong từng thư mục submodule**, không chạy ở root ngoài.

Với mỗi submodule trong SCOPE:
```bash
git -C {submodule} log --oneline -10
git -C {submodule} diff main...HEAD --stat
git -C {submodule} diff main...HEAD
```

Nếu `main...HEAD` rỗng (đang làm trực tiếp trên main), fallback sang:
```bash
git -C {submodule} diff HEAD~1 --stat
git -C {submodule} diff HEAD~1
```

Đọc toàn bộ diff. Lập 2 danh sách:
- **CHANGED_FILES** — mọi file đã sửa/thêm/xóa
- **CHANGED_TESTS** — file test trong diff (pattern: `test_*.py`, `*.test.ts`, `*_test.go`, `spec/**`)

**Bước 3 — Đọc context dependency**

Với mỗi file trong CHANGED_FILES, quét import/require trong diff. Với module nội bộ nào được import:
- Đọc file đó để hiểu interface/contract
- Ghi chú nếu contract thay đổi vs caller kỳ vọng

Giới hạn: đọc tối đa 5 file dependency mỗi submodule. Ưu tiên file được import bởi nhiều file thay đổi nhất.

**Bước 4 — Cross-check plan vs diff**

So sánh CHANGED_FILES với "Các file cần sửa" trong plan:

| Trạng thái | Ý nghĩa |
|-----------|---------|
| ✓ Đã làm | File trong plan VÀ trong diff |
| ✗ Thiếu | File trong plan nhưng KHÔNG có trong diff |
| ⚠ Ngoài plan | File trong diff nhưng KHÔNG có trong plan |

Với mỗi bước trong plan, quét diff tìm dấu hiệu bước đó đã được thực hiện. Nếu không có trace → đánh dấu thiếu.

**Bước 5 — Apply checklist**

Đánh giá từng item dựa trên dòng diff thực tế. Cite `file:line` cho mọi phát hiện.

**5a. Universal**
- [ ] Không hardcode secrets, credentials, token, magic numbers
- [ ] Tên rõ ràng, self-documenting — không `tmp`, `data2`, `flag`, `x`
- [ ] Tất cả error path được handle — không `except: pass`, `catch {}`, bỏ qua lỗi
- [ ] Không thêm dead code (block comment-out, import không dùng, nhánh không bao giờ chạy)
- [ ] Flow chính không bị phá

**5b. Security**
- [ ] Tất cả input từ user được validate/sanitize trước khi dùng
- [ ] Không nối string SQL — dùng parameterized query / ORM
- [ ] Không XSS — escape user content trước khi render
- [ ] Auth/authz được kiểm tra trên mọi endpoint hoặc mutation mới
- [ ] Không IDOR — kiểm tra ownership trước khi trả về/sửa resource
- [ ] Dữ liệu nhạy cảm (PII, token) không bị log hoặc lộ trong response
- [ ] Không deserialize dữ liệu không tin cậy theo kiểu unsafe

**5c. Breaking changes**
- [ ] Thay đổi DB schema có migration file — không drop column/table ngầm
- [ ] Shape của API response không đổi; nếu đổi → bump version hoặc cập nhật toàn bộ consumer
- [ ] Format event/message không đổi; nếu đổi → backward-compatible hoặc cập nhật consumer
- [ ] Biến môi trường / config key không đổi tên mà không có migration

**5d. Test coverage**
- [ ] Test được thêm hoặc cập nhật cho mọi behavior thay đổi
- [ ] Happy path được cover
- [ ] Ít nhất một edge case (input rỗng, zero, max boundary)
- [ ] Ít nhất một failure/error case
- [ ] Tên test mô tả behavior, không mô tả implementation
- [ ] Không xóa test mà không có test thay thế

**5e. Performance**
- [ ] Không N+1 query — bulk fetch hoặc eager-load nơi cần
- [ ] Tất cả DB query có LIMIT hoặc pagination — không `SELECT *` không giới hạn
- [ ] Không gọi operation nặng trong loop
- [ ] Cache được invalidate khi data thay đổi
- [ ] Không blocking I/O trên main/UI thread (FE)

**5f. Language: [lang_be] / [lang_fe]**
```
Python     → Không print() · Type hints đầy đủ · f-string · không bare except
TypeScript → Không `any` · Không `!` unsafe · strict mode · không implicit return
Go         → Check tất cả error (không `_`) · Không panic() trong lib · Context propagated
Java/Kotlin→ Không System.out · Checked exceptions · try-with-resources · nullable rõ ràng
PHP        → Không var_dump() · PSR logging · Typed properties · không global state
Ruby       → Không puts/p · Exception handling · frozen_string_literal: true
Node/JS    → Không console.log · async/await đúng · không unhandled promise rejection
```

**5g. Architecture: [arch]**
```
layered      → Không skip layer · Controller chỉ delegate · Service chứa logic · Repo = data only
MVC          → Thin controller · Fat model · Không business logic trong view
hexagonal    → Domain không import infra · Port là interface · Adapter implement port
microservices→ Không gọi trực tiếp DB service khác · Mọi giao tiếp qua API hoặc event
CQRS         → Command và query hoàn toàn tách biệt · Read/write model độc lập
```

**5h. Async/Queue: [async_tech]**  *(bỏ qua nếu none)*
```
[ ] Idempotency key có trên mọi job
[ ] max_retries đặt + exponential backoff cấu hình
[ ] Dead-letter queue / failure handler được định nghĩa
[ ] Job status chuyển đúng: pending → running → done/failed (không stuck)
[ ] FE: loading + error state render · polling cleanup on unmount · không race condition
```

**5i. Checklist từ plan**

Apply thêm mọi item trong "Code Review Checklist" của sprint plan chưa được cover ở trên.

**Bước 6 — Kiểm tra deliverables**

Kiểm tra Codex đã tạo đủ docs cho sprint hiện tại:

```bash
ls {submodule}/docs/changelog/*-changelog-{slug}*.md
ls {submodule}/docs/test/*-test-{slug}*.md
ls {submodule}/docs/test/*-testlog-{slug}*.md
```

| File | Trạng thái |
|------|-----------|
| changelog | ✓ có / ✗ thiếu |
| test doc  | ✓ có / ✗ thiếu |
| testlog   | ✓ có / ✗ thiếu |

Nếu không biết slug, kiểm tra file được tạo/sửa hôm nay theo pattern trên.

**Bước 7 — Output review report**

```
╔══════════════════════════════════════════════════════════════╗
  CODE REVIEW  sprint-[N]-[slug]
╚══════════════════════════════════════════════════════════════╝

  Scope:      [submodule(s)]
  Thay đổi:   [N file]  ·  [+thêm / -xóa dòng]
  Plan:       [submodule]/docs/plan/sprint-[N]-[slug].md

──────────────────────────────────────────────────────────────
  📋 PLAN COMPLIANCE
──────────────────────────────────────────────────────────────

  ✓ / ✗  [file] — đã làm / thiếu
  ⚠       [file] — ngoài plan  [lý do ngắn]
  ✗       Bước [N]: "[nội dung bước]" — không có dấu vết trong diff

──────────────────────────────────────────────────────────────
  🔍 CODE QUALITY
──────────────────────────────────────────────────────────────

  ✓  [check] — OK
  ⚠  [check] — [file:line]  [vấn đề không blocking]
  ✗  [check] — [file:line]  [vấn đề blocking: cần fix gì]

──────────────────────────────────────────────────────────────
  🔒 SECURITY
──────────────────────────────────────────────────────────────

  ✓ / ⚠ / ✗  [từng security check kèm file:line nếu có vấn đề]

──────────────────────────────────────────────────────────────
  🧪 TESTS
──────────────────────────────────────────────────────────────

  ✓ / ⚠ / ✗  [từng test check]
  Test đã sửa: [danh sách test file]

──────────────────────────────────────────────────────────────
  📦 DELIVERABLES
──────────────────────────────────────────────────────────────

  changelog  ✓ / ✗
  test doc   ✓ / ✗
  testlog    ✓ / ✗

──────────────────────────────────────────────────────────────
  VERDICT
──────────────────────────────────────────────────────────────

  [Nếu có blocking (✗)]:
  ✗ [N] vấn đề blocking — quay lại Codex trước khi merge.
  Cần fix:
    1. [file:line] — [cần fix gì]
    2. ...

  [Nếu chỉ có warning hoặc pass hết]:
  ✓ LGTM — [N] check passed · [M] warning (không blocking).
  [Nếu thiếu docs]: Next → Codex: tạo docs còn thiếu.

══════════════════════════════════════════════════════════════
```

---

## PHASE 6 — Proactive Warnings

- **Thiếu `.bs-toolkit.json`** → tự tạo với `stack_profile` sau lần detect đầu tiên
- **`stack_profile` có thể stale** → "💡 Vừa thay đổi stack? Chạy `install.py --setup-stack` để refresh."
- **Task chạm `shared_files`** → "⚠️ File này là shared — cần coordinate với teammates trước khi sửa."
- **Task liên quan API contract** → "⚠️ Thay đổi API contract cần cập nhật docs và thông báo tất cả consumer."
- **Thiếu `docs/plan/`** trong submodule → "⚠️ Tạo docs/plan/ trước khi chạy plan mode."

---

## Notes

- `plan` mode → **tạo file và dừng**. Không bao giờ bắt đầu implement.
- `review` mode → **chỉ output findings**. Không fix code — đó là việc của Codex.
- `brief` mode → **output brief và dừng**. Không tạo file, không chạy script.
- Dùng ngày thực tế từ system date cho `[YYYYMMDD]`
- `.bs-toolkit.json` nên commit vào git — đây là config chung cho cả team
