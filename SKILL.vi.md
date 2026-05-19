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

**Bước 1 — Đọc thay đổi**

```bash
git log --oneline -10
git diff main...HEAD --stat
git diff main...HEAD
```

Nếu `main...HEAD` rỗng (đang làm việc trực tiếp trên main), fallback sang:
```bash
git diff HEAD~1 --stat
git diff HEAD~1
```

Đọc toàn bộ diff. Ghi nhận từng file thay đổi và thay đổi cụ thể là gì.

**Bước 2 — Apply checklist vào code thực tế**

Với mỗi file thay đổi, kiểm tra:

**Universal**
- [ ] Không hardcode secrets, credentials, magic numbers
- [ ] Tên hàm/biến rõ ràng, self-documenting
- [ ] Tất cả error path được handle — không silent fail
- [ ] API contract không thay đổi ngầm
- [ ] Flow chính không bị phá

**Language: [lang_be] / [lang_fe]**
```
Python     → Không print() · Type hints đầy đủ · f-string
TypeScript → Không `any` · Không `!` unsafe · strict mode
Go         → Check tất cả error (không `_`) · Không panic() trong lib · Context propagation
Java/Kotlin→ Không System.out · Checked exceptions · try-with-resources
PHP        → Không var_dump() · PSR logging · Declare types
Ruby       → Không puts/p · Exception handling · frozen_string_literal
Node/JS    → Không console.log · async/await đúng
```

**Architecture: [arch]**
```
layered      → Không skip layer · Controller chỉ delegate · Service chứa logic · Repo = data only
MVC          → Thin controller · Fat model · View không chứa logic
hexagonal    → Domain ≠ import infra · Ports là interface · Adapters implement ports
microservices→ Không gọi DB service khác · Giao tiếp qua API/event
CQRS         → Command ≠ Query · Read/write model độc lập
```

**Async/Queue: [async_tech]**  *(bỏ qua nếu none)*
```
[ ] Idempotency key · max_retries + exponential backoff · Dead-letter handling
[ ] Status: pending → running → done/failed
[ ] FE: loading/error state · Race condition polling · Cleanup on unmount
```

**Bước 3 — Output review report**

```
╔══════════════════════════════════════════════════════════════╗
  CODE REVIEW  sprint-[N]-[slug]
╚══════════════════════════════════════════════════════════════╝

  Thay đổi: [N file]  ·  [+thêm / -xóa dòng]

  ✓  [checklist item] — OK
  ⚠  [checklist item] — [file:line]  [mô tả vấn đề]
  ✗  [checklist item] — [file:line]  [vấn đề blocking]

──────────────────────────────────────────────────────────────

  [Nếu pass hết]:
  LGTM — [N] check passed.
  Next → Codex: tạo changelog + test docs nếu chưa xong.

  [Nếu có vấn đề]:
  [N] vấn đề — quay lại Codex để fix trước khi tạo docs.
  [Từng vấn đề: file:line + cần fix gì]

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
