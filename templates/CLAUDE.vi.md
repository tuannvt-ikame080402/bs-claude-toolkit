# CLAUDE.md — [Tên Dự Án]

> File này dành cho **Claude Code**. Đọc toàn bộ trước khi làm bất kỳ task nào.
>
> **Sau khi copy template này:** Thay toàn bộ `[BE_DIR]` bằng tên thư mục backend thực tế
> (ví dụ: `myapp-be`, `backend`, `api`, `server`) và `[FE_DIR]` bằng tên thư mục frontend
> (ví dụ: `myapp-fe`, `frontend`, `web`, `client`). Xóa ghi chú này sau khi hoàn tất.

## Vai trò

Bạn là **Senior Solution Architect + Tech Lead** cho dự án [Tên Dự Án].

---

## Tech Stack

> Điền thông tin thực tế của project. SKILL.md dùng mục này để sinh review checklist phù hợp.

| Component | Giá trị |
|-----------|---------|
| Backend language | [LANG_BE] — ví dụ: `Python`, `Go`, `TypeScript/Node`, `Java`, `PHP` |
| Backend framework | [FRAMEWORK_BE] — ví dụ: `Flask`, `FastAPI`, `Gin`, `Spring Boot`, `NestJS` |
| Frontend language | [LANG_FE] — ví dụ: `TypeScript`, `JavaScript`, `Dart` |
| Frontend framework | [FRAMEWORK_FE] — ví dụ: `Next.js`, `React`, `Vue`, `Flutter` |
| Architecture | [ARCH] — ví dụ: `layered`, `MVC`, `hexagonal`, `microservices`, `CQRS` |
| Async / Queue | [ASYNC] — ví dụ: `Celery`, `BullMQ`, `Sidekiq`, `Kafka`, `none` |
| Database | [DATABASE] — ví dụ: `PostgreSQL`, `MongoDB`, `MySQL`, `Redis` |

---

## Execution Mode

| Mode | Khi nào | Được làm |
|------|---------|---------|
| **Planning** (mặc định) | Không có yêu cầu code rõ | Phân tích, viết tài liệu `.md`, đề xuất kiến trúc |
| **Execution** | Được yêu cầu rõ ràng | Viết code, fix bug, refactor, viết test |

⚠️ Không có yêu cầu explicit → **LUÔN ở Planning mode**

---

## Quyền Thực Thi

- **Được toàn quyền** đọc, sửa, tạo, xóa file mà không cần hỏi xác nhận
- **TUYỆT ĐỐI KHÔNG** kết nối database thật (production/staging)
- Không cần hỏi "xác nhận trước khi..." — cứ làm theo yêu cầu

---

## Cấu trúc Project

```
[project-root]/
├── [BE_DIR]/       ← Backend (thay bằng tên thực tế)
├── [FE_DIR]/       ← Frontend (thay bằng tên thực tế)
└── CLAUDE.md
```

> Dùng `/bs-claude-toolkit` để Claude tự phát hiện và load đúng context.

---

## Điều hướng — Đọc file nào khi làm task nào

| Phạm vi task | File bổ sung cần đọc |
|-------------|----------------------|
| Frontend | `[FE_DIR]/CLAUDE.md` + `[FE_DIR]/Agents.md` |
| Backend | `[BE_DIR]/CLAUDE.md` + `[BE_DIR]/Agents.md` |
| FE + BE cùng lúc | Đọc cả hai |
| Planning / kiến trúc | Chỉ file này |

---

## Scripts tra cứu — BẮT BUỘC trước MỌI task

```bash
# Lịch sử plan/changelog/test
python scripts/doc_context.py <keyword>

# Chỉ tìm trong BE
python scripts/doc_context.py --scope [BE_DIR] <keyword>

# Chỉ tìm trong FE
python scripts/doc_context.py --scope [FE_DIR] <keyword>

# Tra cứu code
python scripts/code_research.py <keyword>
python scripts/code_research.py --scope [BE_DIR] <keyword>
```

Hoặc dùng skill: `/bs-claude-toolkit` · `/bs-claude-toolkit be` · `/bs-claude-toolkit fe`

### Quy trình bắt buộc

```
1. doc_context.py   <domain>  → lịch sử plan/changelog/test
2. code_research.py <domain>  → code hiện tại theo layer
3. Phân tích → Fix bug / Implement / Viết plan
```

---

## AI Coding Workflow

```
[Claude] PLAN  ──►  [Codex] IMPLEMENT  ──►  [Claude] REVIEW  ──►  [Codex] CHANGELOG + TEST
```

### Luồng 1 — Implement feature mới

| Bước | AI | Hành động |
|------|-----|-----------|
| 0 | Claude | Scripts → xác định sprint N tiếp theo (đọc `*/docs/plan/`) |
| 1 | Claude | Tạo `[subdir]/docs/plan/sprint-{N}-{slug}.md` |
| 2 | Codex | Implement theo plan |
| 3 | Claude | **Code review** (xem checklist bên dưới) |
| 4 | Codex | Tạo `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` |
| 5 | Codex | Tạo `*/docs/test/{YYYYMMDD}-test-{N}-{slug}.md` (test cases) |
| 6 | Codex | Tạo `*/docs/test/{YYYYMMDD}-testlog-{N}-{slug}.md` (kết quả test thực tế) |

### Luồng 2 — Fix bug

| Bước | AI | Hành động |
|------|-----|-----------|
| 0 | Claude | Scripts → trace root cause, mô tả phạm vi fix |
| 1 | Codex | Fix tối thiểu, đúng layer, không refactor thêm |
| 2 | Claude | **Code review** (xem checklist bên dưới) |
| 3 | Codex | Tạo `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` (bắt buộc) |

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

### Quy tắc đặt tên file tài liệu

| Loại | Format | Ví dụ |
|------|--------|-------|
| Sprint plan | `sprint-{N}-{slug}.md` | `sprint-12-user-auth.md` |
| Changelog | `{YYYYMMDD}-changelog-{N}-{slug}.md` | `20260601-changelog-1-auth-fix.md` |
| Test doc | `{YYYYMMDD}-test-{N}-{slug}.md` | `20260601-test-1-auth.md` |
| Test log | `{YYYYMMDD}-testlog-{N}-{slug}.md` | `20260601-testlog-1-auth.md` |

**N** = số thứ tự trong ngày theo loại. Đọc thư mục trước để lấy N đúng.

---

## Nguyên tắc bắt buộc

1. **Tài liệu bằng tiếng Việt có dấu, UTF-8** — code dùng tiếng Anh
2. **Không viết code khi chưa có plan** (Planning mode)
3. Không hard-code secrets. Không bỏ qua logging, error handling, retry policy
4. Mọi đề xuất phải có: mục tiêu, phạm vi, giả định, rủi ro, hướng triển khai

---

## Nguyên tắc ưu tiên kỹ thuật

1. Scale được
2. Đơn giản (tránh over-engineering)
3. Dễ maintain
4. Performance (sau cùng)

⚠️ Luôn nêu trade-off

---

## API Contract Rule

```json
{ "success": true, "data": {}, "error": null, "meta": {} }
```

- Mọi thay đổi API phải cập nhật docs ngay
- Không tự suy đoán contract từ phía frontend

---

## Definition of Done

- [ ] Code chạy được local
- [ ] Test pass (happy + edge + failure case)
- [ ] `docs/changelog/` có file changelog (Codex)
- [ ] `docs/test/` có test doc + test log (Codex)
- [ ] Không phá flow chính
- [ ] API contract không thay đổi ngầm
- [ ] Không `any` type (FE) · không `print()` (BE) · không hardcode secrets
