---
description: Load project context, detect task type, compute next sprint number, suggest research commands, and output a full action brief before starting any task.
arguments: [tên-submodule | mô-tả-task]
---

Thực hiện tuần tự các phase sau.

---

## PHASE 0 — Config & Stack Cache

### 0a. Đọc project config
Check `.bs-toolkit.json` ở root:
- Nếu tồn tại → đọc `modules` (mapping tên tùy chọn), `shared_files`, **`stack_profile`**
- Nếu không tồn tại → dùng mặc định

### 0b. Kiểm tra Stack Profile Cache

Bước này quyết định **tiêu thụ bao nhiêu token** cho lần chạy này.

**Nếu `stack_profile` tồn tại trong `.bs-toolkit.json` và có ít nhất `lang_be` hoặc `lang_fe`:**
→ **⚡ FAST PATH** — dùng cache, **bỏ qua Phase 1 hoàn toàn**
  - Nạp trực tiếp: `lang_be`, `lang_fe`, `framework_be`, `framework_fe`, `arch`, `async_tech`, `database`, `custom_rules`, `main_flow`, `api_format`
  - Token tiêu thụ: ~100 token
  - Nhảy thẳng đến Phase 2

**Nếu `stack_profile` không tồn tại hoặc rỗng:**
→ **🔍 FULL PATH** — chạy toàn bộ Phase 1
  - Token tiêu thụ: ~1500–3000 token

### 0c. Xác định scope

- Nếu `$ARGUMENTS` khớp tên submodule hoặc alias → chỉ load submodule đó
- Nếu không → load tất cả submodule

---

## PHASE 1 — Load Context  *(chỉ chạy ở FULL PATH)*

### 1a. Root context
- Read `./CLAUDE.md`
- Read `./Agents.md` nếu tồn tại

### 1b. Phát hiện submodule

Tìm tất cả thư mục con trực tiếp có chứa `CLAUDE.md`, `Agents.md`, hoặc thư mục `docs/`.

Nếu `.bs-toolkit.json` có `modules` mapping (ví dụ: `{"be": "myapp-be"}`), dùng để resolve tên không chuẩn. Nếu không, detect theo nội dung.

Áp dụng scope filter: nếu scope đã set ở Phase 0c, chỉ load submodule khớp.

### 1c. Load files từ submodule đã chọn
- Read `{subdir}/CLAUDE.md`
- Read `{subdir}/Agents.md` nếu tồn tại

### 1d. Auto-detect stack profile

Detect theo **hai nguồn**, ưu tiên từ trên xuống:

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

Hiển thị trong brief:
```
✓ Stack detected & cached → lần sau sẽ dùng cache.
```

---

## PHASE 2 — Sprint Intelligence

Scan `*/docs/plan/` trong submodule đang scope:
1. Liệt kê files khớp `sprint-{N}-*.md`
2. Extract số N lớn nhất
3. next = N_max + 1 (không có file → next = 1)
4. Ghi nhớ 3 sprint gần nhất để cho context

Nếu có nhiều submodule trong scope → hiển thị next sprint theo từng submodule.

---

## PHASE 3 — Phân tích Task

Chỉ chạy nếu có task description trong `$ARGUMENTS`.

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

## PHASE 5 — Output Action Brief

```
╔══════════════════════════════════════════════════════════════╗
  PROJECT BRIEF  [scope: all | tên-submodule]
╚══════════════════════════════════════════════════════════════╝

  Mode:        [Planning | Execution]
  Scope:       [submodule(s) đang load]
  Stack:       [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
               [arch] · async: [async_tech] · db: [database]
  Stack src:   [⚡ cached | 🔍 detected from project files]
  Next Sprint: [N]  (last: sprint-[N-1]-[tên])

──────────────────────────────────────────────────────────────
  RESEARCH — chạy trước khi bắt đầu
──────────────────────────────────────────────────────────────

  [SCRIPT_CMD]doc_context.py [keywords]
  [SCRIPT_CMD]doc_context.py --scope [submodule] [keywords]
  [SCRIPT_CMD]code_research.py [keywords]

──────────────────────────────────────────────────────────────
  WORKFLOW  [task-type]
──────────────────────────────────────────────────────────────

  new-feature:
    [Claude — Planning]
    1. Research (doc + code)
    2. Tạo [submodule]/docs/plan/sprint-[N]-[slug].md

    [Codex — Implementation]
    3. Implement theo plan

    [Claude — Review]
    4. Code review (xem CODE REVIEW bên dưới)

    [Codex — Documentation]
    5. Tạo [submodule]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
    6. Tạo [submodule]/docs/test/[DATE]-test-[seq]-[slug].md
    7. Tạo [submodule]/docs/test/[DATE]-testlog-[seq]-[slug].md

  bug-fix:
    [Claude — Planning]
    1. Research → trace root cause
    2. Mô tả phạm vi và cách fix

    [Codex — Implementation]
    3. Fix minimum scope, đúng layer

    [Claude — Review]
    4. Code review (xem CODE REVIEW bên dưới)

    [Codex — Documentation]
    5. Tạo [submodule]/docs/changelog/[DATE]-changelog-[seq]-[slug].md

  question / architecture:
    1. Research → phân tích → trả lời  (không cần tạo file)

──────────────────────────────────────────────────────────────
  CODE REVIEW  (sau mỗi lần implement/fix)
──────────────────────────────────────────────────────────────

  ── Universal ──
  [ ] Không hardcode secrets, credentials, magic numbers
  [ ] Tên hàm/biến rõ ràng, self-documenting
  [ ] Tất cả error path được handle — không silent fail
  [ ] API contract không thay đổi ngầm → cập nhật docs nếu có
  [ ] Flow chính không bị phá

  ── Language: [lang_be] · [lang_fe] ──
  Python     → [ ] Không print() · Type hints đầy đủ · f-string
  TypeScript → [ ] Không `any` · Không `!` unsafe · strict mode
  Go         → [ ] Check tất cả error (không `_`) · Không panic() trong lib · Context propagation
  Java/Kotlin → [ ] Không System.out · Checked exceptions · try-with-resources
  PHP        → [ ] Không var_dump() · PSR logging · Declare types
  Ruby       → [ ] Không puts/p · Exception handling · frozen_string_literal
  Node/JS    → [ ] Không console.log · async/await đúng

  ── Architecture: [arch] ──
  layered     → [ ] Không skip layer · Controller chỉ delegate · Service chứa logic · Repo = data only
  MVC         → [ ] Thin controller · Fat model · View không chứa logic
  hexagonal   → [ ] Domain ≠ import infra · Ports = interface · Adapters implement ports
  microservices → [ ] Không gọi DB service khác · Giao tiếp qua API/event
  CQRS        → [ ] Command ≠ Query · Read/write model độc lập

  ── Async/Queue: [async_tech] ──  (bỏ qua nếu none)
  [ ] Idempotency key · max_retries + exponential backoff · Dead-letter handling
  [ ] Status: pending → running → done/failed
  [ ] FE: loading/error state · Race condition polling · Cleanup on unmount

──────────────────────────────────────────────────────────────
  FILE NAMING  (today: [YYYYMMDD])
──────────────────────────────────────────────────────────────

  Plan:      [submodule]/docs/plan/sprint-[N]-[slug].md
  Changelog: [submodule]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
  Test doc:  [submodule]/docs/test/[DATE]-test-[seq]-[slug].md
  Test log:  [submodule]/docs/test/[DATE]-testlog-[seq]-[slug].md

  [seq] = đọc thư mục trước, đếm file cùng ngày, +1

──────────────────────────────────────────────────────────────
  DEFINITION OF DONE
──────────────────────────────────────────────────────────────

  [ ] Code chạy được local
  [ ] Test pass: happy + edge + failure case
  [ ] Changelog tạo xong (Codex)
  [ ] Test doc + test log tạo xong (Codex)
  [ ] Flow chính không bị phá
  [ ] API contract không thay đổi ngầm
  [ ] Không vi phạm language rules · Không hardcode secrets

══════════════════════════════════════════════════════════════
```

---

## PHASE 6 — Proactive Warnings

- **Thiếu `.bs-toolkit.json`** → tự tạo với `stack_profile` sau lần detect đầu tiên
- **`stack_profile` có thể stale** → "💡 Vừa thay đổi stack? Chạy `install.py --setup-stack` để refresh."
- **Task chạm `shared_files`** → "⚠️ File này là shared — cần coordinate với teammates trước khi sửa."
- **Task liên quan API contract** → "⚠️ Thay đổi API contract cần cập nhật docs và thông báo tất cả consumer."
- **Thiếu `docs/plan/`** trong submodule → "⚠️ Tạo docs/plan/ trước khi viết sprint plan."
- **Task có vẻ là Execution nhưng chưa được yêu cầu rõ** → xác nhận với user trước khi viết code.

---

## Notes

- Sau khi in brief → **dừng, chờ user** — không tự bắt đầu implement
- Dùng ngày thực tế từ system date cho `[YYYYMMDD]`
- `.bs-toolkit.json` nên commit vào git — đây là config chung cho cả team
