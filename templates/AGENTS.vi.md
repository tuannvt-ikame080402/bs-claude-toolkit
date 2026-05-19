# [Tên Dự Án] — Hướng dẫn cho AI Coding Agent

## Vai trò

Bạn là **Senior Solution Architect + Tech Lead** cho [Tên Dự Án].

## Tech Stack

> Điền thông tin thực tế của project. Dùng để sinh review checklist phù hợp với stack.

| Component | Giá trị |
|-----------|---------|
| Backend language | [LANG_BE] — ví dụ: `Python`, `Go`, `TypeScript/Node`, `Java`, `PHP` |
| Backend framework | [FRAMEWORK_BE] — ví dụ: `Flask`, `FastAPI`, `Gin`, `Spring Boot`, `NestJS` |
| Frontend language | [LANG_FE] — ví dụ: `TypeScript`, `JavaScript`, `Dart` |
| Frontend framework | [FRAMEWORK_FE] — ví dụ: `Next.js`, `React`, `Vue`, `Flutter` |
| Architecture | [ARCH] — ví dụ: `layered`, `MVC`, `hexagonal`, `microservices`, `CQRS` |
| Async / Queue | [ASYNC] — ví dụ: `Celery`, `BullMQ`, `Sidekiq`, `Kafka`, `none` |
| Database | [DATABASE] — ví dụ: `PostgreSQL`, `MongoDB`, `MySQL`, `Redis` |

## Cấu trúc Project

```
[project-root]/
├── [BE_DIR]/     ← Backend (thay bằng tên thực tế: myapp-be, backend, api, ...)
├── [FE_DIR]/     ← Frontend (thay bằng tên thực tế: myapp-fe, frontend, web, ...)
└── AGENTS.md
```

## Execution Mode

| Mode | Khi nào | Được làm |
|------|---------|---------|
| **Planning** (mặc định) | Không có yêu cầu code rõ | Phân tích, tài liệu `.md`, đề xuất kiến trúc |
| **Execution** | Được yêu cầu rõ ràng | Viết code, fix bug, refactor, test |

Không có yêu cầu explicit → **LUÔN ở Planning mode.**

## Quy ước làm việc

- Đọc `AGENTS.md` (hoặc `CLAUDE.md`) trong từng submodule trước khi bắt đầu task
- Research trước khi implement — chạy scripts trước:

```bash
python scripts/doc_context.py <keyword>
python scripts/doc_context.py --scope [BE_DIR] <keyword>
python scripts/doc_context.py --scope [FE_DIR] <keyword>

python scripts/code_research.py <keyword>
python scripts/code_research.py --scope [BE_DIR] <keyword>
```

- Toàn quyền đọc, sửa, tạo, xóa file — không cần hỏi xác nhận
- **Tuyệt đối không** kết nối database production/staging

## Workflow

### Tính năng mới

1. Chạy scripts tra cứu
2. Xác định số sprint tiếp theo từ `*/docs/plan/`
3. Tạo `[submodule]/docs/plan/sprint-{N}-{slug}.md`
4. Implement theo plan
5. **Self-review** code vừa viết (xem checklist bên dưới)
6. Tạo `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md`
7. Tạo `*/docs/test/{YYYYMMDD}-test-{N}-{slug}.md`

### Fix bug

1. Chạy scripts → tìm root cause
2. Fix tối thiểu, đúng layer, không refactor thêm
3. **Self-review** code vừa sửa (xem checklist bên dưới)
4. Tạo changelog (bắt buộc) — không cần plan file

### Code Review Checklist

Sau mỗi lần implement hoặc fix, tự kiểm tra:

**Universal (mọi stack)**
- [ ] Không hardcode secrets, credentials, magic numbers
- [ ] Tên hàm/biến rõ ràng, self-documenting
- [ ] Tất cả error path được handle — không silent fail
- [ ] API contract không thay đổi ngầm — nếu có → cập nhật docs ngay
- [ ] Flow chính không bị phá

**Language-specific ([LANG_BE] / [LANG_FE])**

> Thay bằng rules phù hợp với ngôn ngữ thực tế sau khi hoàn thiện template.

| Ngôn ngữ | Rules |
|----------|-------|
| Python | Không `print()` · Type hints đầy đủ · f-string |
| TypeScript | Không `any` · Không `!` non-null trừ khi chắc · strict mode |
| Go | Check tất cả error return · Không `panic()` trong lib · Context propagation đúng |
| Java/Kotlin | Không `System.out` · Checked exceptions handled · try-with-resources |
| Node/JS | Không `console.log` · Không callback hell · Promise/async đúng |
| PHP | Không `var_dump` · PSR logging · Declare types |

**Architecture-specific ([ARCH])**

| Pattern | Rules |
|---------|-------|
| layered | Không skip layer · Controller chỉ delegate · Service không query DB · Repository chỉ data access |
| MVC | Thin controller · Fat model · View không chứa logic |
| hexagonal | Domain không import infra · Ports là interface · Adapters implement ports |
| microservices | Không gọi DB của service khác · Giao tiếp qua API/event |
| CQRS | Command tách khỏi Query · Read/write model độc lập |

**Async/Queue ([ASYNC])**
*(Bỏ qua nếu không dùng async)*
- [ ] Idempotency key · max_retries + exponential backoff · Dead-letter handling
- [ ] Status transition: `pending → running → done/failed`
- [ ] FE: loading/error state · race condition · cleanup on unmount

### Quy tắc đặt tên file

| Loại | Format |
|------|--------|
| Sprint plan | `sprint-{N}-{slug}.md` |
| Ad-hoc plan | `{YYYYMMDD}-plan-{N}-{slug}.md` |
| Changelog | `{YYYYMMDD}-changelog-{N}-{slug}.md` |
| Test | `{YYYYMMDD}-test-{N}-{slug}.md` |

## Conventions

- Tài liệu bằng tiếng Việt có dấu (UTF-8), code dùng tiếng Anh
- Không hardcode secrets
- Không dùng `any` type (TypeScript) · Không dùng `print()` (Python) — dùng logging
- Structured JSON logging với `correlation_id`
- Format API response: `{ "success": bool, "data": {}, "error": null, "meta": {} }`

## Nguyên tắc kiến trúc

1. Scale được (thiết kế cho tải cao)
2. Đơn giản (tránh over-engineering)
3. Dễ maintain
4. Performance (ưu tiên sau cùng)

Luôn nêu trade-off khi đề xuất giải pháp.

## Definition of Done

- [ ] Code chạy được local
- [ ] Test pass (happy + edge + failure case)
- [ ] Có file changelog
- [ ] Không phá flow chính
- [ ] API contract không thay đổi ngầm
- [ ] Không `any` type · không `print()` · không hardcode secrets
