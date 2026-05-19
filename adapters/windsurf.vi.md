# bs-claude-toolkit — Quy tắc Workflow AI Coding

## Load Context

Trước khi bắt đầu bất kỳ task nào, đọc các file theo thứ tự:
1. `CLAUDE.md` ở thư mục gốc (luôn luôn)
2. `CLAUDE.md` và `Agents.md` bên trong các thư mục con trực tiếp có chứa `docs/` hoặc `CLAUDE.md` riêng — hoạt động với mọi quy ước đặt tên (`backend/`, `myapp-be/`, `api/`, `web/`, v.v.)

## Research trước khi implement

Chạy scripts này trước khi fix bug hoặc implement tính năng:

```bash
python scripts/doc_context.py <keyword>
python scripts/doc_context.py --scope <submodule-name> <keyword>
python scripts/code_research.py <keyword>
python scripts/code_research.py --scope <submodule-name> <keyword>
```

Nếu scripts chưa có local, dùng toolkit path:
```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py <keyword>
```

## Execution Mode

- **Planning (mặc định):** Không có yêu cầu code rõ → phân tích, tài liệu `.md`, đề xuất kiến trúc
- **Execution:** Chỉ khi được yêu cầu rõ ràng → viết code, fix bug, refactor, test

## Workflow

**Tính năng mới:** research → `docs/plan/sprint-{N}-{slug}.md` → implement → **self-review** → changelog → test doc

**Fix bug:** research → trace root cause → fix tối thiểu → **self-review** → changelog (không cần plan file)

## Code Review

Sau mỗi lần implement hoặc fix, kiểm tra theo stack khai báo trong `CLAUDE.md` (mục Tech Stack):

**Universal**
- Không hardcode secrets, credentials, magic numbers · Tên rõ ràng
- Tất cả error path được handle — không silent fail
- API contract không thay đổi ngầm → cập nhật docs nếu có
- Flow chính không bị phá

**Language** (áp dụng rules theo ngôn ngữ trong `CLAUDE.md`)
- Python → Không `print()` · type hints · f-string
- TypeScript → Không `any` · không `!` unsafe · strict mode
- Go → Check tất cả error return · không `panic()` trong lib · context propagation đúng
- Java/Kotlin → Không `System.out` · checked exceptions · try-with-resources
- Node/JS → Không `console.log` · async/await đúng
- PHP → Không `var_dump` · PSR logging · declare types

**Architecture** (áp dụng rules theo pattern trong `CLAUDE.md`)
- layered → Không skip layer · controller chỉ delegate · service chứa logic · repo chỉ data access
- MVC → Thin controller · fat model · view không chứa logic
- hexagonal → Domain không import infra · ports là interface · adapters implement ports
- microservices → Không gọi DB service khác · giao tiếp qua API/event
- CQRS → Command tách Query · read/write model độc lập

**Async/Queue** (nếu có)
- Idempotency key · max_retries + exponential backoff · dead-letter handling
- Status: `pending → running → done/failed`
- FE: loading/error state · race condition polling · cleanup on unmount

## Quy tắc bắt buộc

- Tài liệu bằng tiếng Việt có dấu (UTF-8), code dùng tiếng Anh
- Không kết nối DB thật (production/staging)
- Không hardcode secrets · Không `any` type (TS) · Không `print()` (Python)
- Thay đổi API contract phải cập nhật docs ngay lập tức
