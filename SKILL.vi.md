---
description: Load project context, detect task type, compute next sprint number, suggest research commands, and output a full action brief before starting any task. Supports solo and split-team modes.
arguments: [scope | task-description]
---

Thực hiện tuần tự các phase sau.

---

## PHASE 0 — Config & Stack Cache

### 0a. Đọc project config
Check `.bs-toolkit.json` ở root:
- Nếu tồn tại → đọc `team_mode`, `modules`, `shared_docs`, `shared_files`, **`stack_profile`**
- Nếu không tồn tại → mặc định `team_mode = "solo"`, không có stack_profile

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

### 0d. Kiểm tra Stack Profile Cache

Đây là bước quyết định **đọc bao nhiêu token** cho lần chạy này.

**Nếu `stack_profile` tồn tại trong `.bs-toolkit.json` và có ít nhất `lang_be` hoặc `lang_fe`:**
→ **⚡ FAST PATH** — dùng cache, **bỏ qua Phase 1 hoàn toàn**
  - Nạp trực tiếp: `lang_be`, `lang_fe`, `framework_be`, `framework_fe`, `arch`, `async_tech`, `database`, `custom_rules`, `main_flow`, `api_format`
  - Token tiêu thụ: ~100 token (chỉ đọc JSON nhỏ)
  - Nhảy thẳng đến Phase 2

**Nếu `stack_profile` không tồn tại hoặc rỗng:**
→ **🔍 FULL PATH** — chạy toàn bộ Phase 1
  - Token tiêu thụ: ~1500–3000 token (đọc tất cả CLAUDE.md files)
  - Sau Phase 1d, hiển thị:
    ```
    💡 Stack chưa được cache. Chạy lệnh sau để lưu vào .bs-toolkit.json:
       python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
    Các lần sau sẽ bỏ qua đọc CLAUDE.md → tiết kiệm ~90% token context loading.
    ```

---

## PHASE 1 — Load Context  *(chỉ chạy ở FULL PATH)*

### 1a. Root context
- Read `./CLAUDE.md`
- Read `./Agents.md` nếu tồn tại

### 1b. Phát hiện và filter submodule

**Solo mode:** Load tất cả submodule tìm được (subdir có `CLAUDE.md` / `Agents.md` / `docs/`)

**Split mode với scope:** Chỉ load submodule khớp scope.
- Dùng mapping từ `modules` trong config: `{ "be": "myapp-be" }` → scope "be" → load `myapp-be/`
- Nếu không có mapping → fallback partial match trên tên thư mục

**Split mode với scope = "all":** Load tất cả, đánh dấu rõ module nào của ai.

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
- `pymongo`/`motor`/`mongoengine` → MongoDB
- `sqlalchemy`/`psycopg2`/`asyncpg` → PostgreSQL
- `mysql-connector`/`mysql2`/`pg` → MySQL/PostgreSQL
- `redis`/`ioredis` → Redis

**Architecture detection** (từ directory structure):
- Có `controller(s)/` + `service(s)/` + `repositor*/` → `layered`
- Có `models/` + `views/` + `controllers/` → `MVC`
- Có `domain/` + `ports/` + `adapters/` → `hexagonal`
- Có `commands/` + `queries/` → `CQRS`
- Nhiều service directory độc lập → `microservices`

**TypeScript detection**: check `tsconfig.json` hoặc `typescript` trong devDependencies.

#### Nguồn 2 — CLAUDE.md / Agents.md (fallback)

Nếu project files không đủ rõ, đọc thêm từ:
- Mục "Tech Stack" table
- Mục "Coding Conventions" / "Architecture"
- Mục "Worker" / "Queue" cho async_tech

#### Sau khi detect xong — tự động cache

Nếu detect được ít nhất `lang_be` hoặc `lang_fe`:

1. **Tự động ghi cache** vào `.bs-toolkit.json`:
   - Đọc `.bs-toolkit.json` (hoặc tạo mới nếu chưa có)
   - Thêm/cập nhật key `stack_profile` với tất cả giá trị detect được
   - Ghi lại file (giữ nguyên các key khác như `team_mode`, `modules`, v.v.)

2. **Thông báo ngắn** trong action brief:
   ```
   ✓ Stack detected & cached: [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
                               [arch] · async: [async_tech] · db: [database]
     Lần sau sẽ dùng cache — không detect lại.
   ```

Nếu `.bs-toolkit.json` chưa có `team_mode` → tạo file mới với `team_mode: "solo"` và `stack_profile`.

Shared files (từ config `shared_files`) — dùng để cảnh báo conflict.

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
  Stack:       [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
               [arch] · async: [async_tech]
  Stack src:   [⚡ cached (.bs-toolkit.json) | 🔍 extracted from CLAUDE.md]
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
    4. Self-review code vừa viết (xem CODE REVIEW bên dưới)
    5. Tạo [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
    6. Tạo [module]/docs/test/[DATE]-test-[seq]-[slug].md

  bug-fix:
    1. Research → trace root cause
    2. Fix minimum scope, đúng layer
    3. Self-review code vừa sửa (xem CODE REVIEW bên dưới)
    4. Tạo [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md

  question / architecture:
    1. Research → phân tích → trả lời
    (không cần tạo file)

──────────────────────────────────────────────────────────────
  CODE REVIEW  (sau mỗi lần implement/fix)
──────────────────────────────────────────────────────────────

  ── Universal (mọi stack) ──
  [ ] Không hardcode secrets, credentials, magic numbers
  [ ] Tên hàm/biến rõ ràng, self-documenting
  [ ] Tất cả error path được handle — không silent fail
  [ ] API contract không thay đổi ngầm → cập nhật docs nếu có
  [ ] Flow chính không bị phá

  ── Language: [lang_be] · [lang_fe] ──
  Áp dụng rule tương ứng với ngôn ngữ detect được:

  Python    → [ ] Không print() · Type hints đầy đủ · f-string
  TypeScript → [ ] Không `any` · Không `!` non-null trừ khi chắc · strict mode
  Go        → [ ] Tất cả error return check (không _ bỏ qua) · Không panic() trong lib · Context propagation đúng
  Java/Kotlin → [ ] Không System.out · Checked exceptions handled · try-with-resources
  PHP       → [ ] Không var_dump/dd() · PSR logging · Declare types
  Ruby      → [ ] Không puts/p · Exception handling rõ · frozen_string_literal
  Node/JS   → [ ] Không console.log · Không callback hell · Promise/async đúng

  ── Architecture: [arch_pattern] ──
  Áp dụng rule tương ứng với pattern detect được:

  layered (controller/service/repo)
    [ ] Không skip layer · Controller chỉ validate+delegate
    [ ] Service chứa business logic, không query DB trực tiếp
    [ ] Repository chỉ data access, không business logic

  MVC
    [ ] Thin controller · Fat model · View không chứa logic

  hexagonal / ports-and-adapters
    [ ] Domain không import infra · Ports là interface · Adapters implement ports

  microservices
    [ ] Không gọi DB của service khác · Giao tiếp qua API/event · Service boundary rõ

  CQRS
    [ ] Command tách khỏi Query · Read/write model độc lập

  ── Async/Queue: [async_tech] ──
  Bỏ qua nếu async_tech = "none"

  [ ] Idempotency key có mặt
  [ ] max_retries + exponential backoff
  [ ] Dead-letter / failed status handling
  [ ] Status transition rõ: pending → running → done/failed
  [ ] FE: loading/error state đủ · Race condition polling · Cleanup on unmount

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
  [ ] Không vi phạm language rules ([lang_be]/[lang_fe]) · Không hardcode secrets

══════════════════════════════════════════════════════════════
```

---

## PHASE 6 — Proactive Warnings

- **Thiếu `.bs-toolkit.json`** → "💡 Chưa có config. Chạy `install.py --mode solo` hoặc `--mode split` để setup."
- **`stack_profile` rỗng (FULL PATH đã chạy)** → "💡 Chạy `install.py --setup-stack` để cache stack → tiết kiệm ~90% token lần sau."
- **Split mode, chạm shared_files** → "⚠️ File này là shared zone — cần sync với team trước."
- **Split mode, task liên quan API contract** → "⚠️ API contract thay đổi cần cả BE và FE đồng thuận."
- **Thiếu `docs/plan/`** trong module → "⚠️ Chưa có docs/plan/ — tạo thư mục trước khi viết plan."
- **Task là Execution nhưng mode mặc định Planning** → nhắc user confirm.
- **`stack_profile` có thể stale** (CLAUDE.md vừa được update đáng kể) → "💡 Nếu vừa thay đổi Tech Stack, chạy `install.py --setup-stack` để refresh cache."

---

## Notes

- Sau khi in brief → **dừng, chờ user** — không tự bắt đầu implement
- Dùng ngày thực tế từ system date cho `[YYYYMMDD]`
- Split mode: sprint numbers per-submodule là bình thường, không phải bug
- `.bs-toolkit.local.json` không được commit vào git (phải có trong `.gitignore`)
