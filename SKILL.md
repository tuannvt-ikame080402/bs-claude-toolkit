---
description: Load project context (CLAUDE.md + Agents.md) và hướng dẫn dùng research scripts trước khi bắt đầu bất kỳ task nào.
arguments: [scope]
---

Load project context. Scope filter (tuỳ chọn): "$ARGUMENTS"

## Bước 1 — Luôn đọc root context

- Read `./CLAUDE.md`
- Read `./Agents.md` nếu tồn tại

## Bước 2 — Phát hiện submodule

Scan tất cả immediate subdirectories. Một subdir là **submodule** nếu chứa ít nhất một trong:
- `CLAUDE.md`
- `Agents.md`
- thư mục `docs/`

Không phụ thuộc tên thư mục — hoạt động với mọi convention:
`backend/`, `frontend/`, `myapp-be/`, `myapp-fe/`, `api/`, `web/`, `server/`, `client/`, v.v.

## Bước 3 — Filter theo scope (nếu có)

Nếu `$ARGUMENTS` không trống: chỉ load submodule mà tên **chứa** `$ARGUMENTS` (case-insensitive).

- `/bs-claude-toolkit be`  → match `backend`, `myapp-be`, `be`, `server`
- `/bs-claude-toolkit fe`  → match `frontend`, `myapp-fe`, `fe`, `web`, `client`
- `/bs-claude-toolkit`     → load TẤT CẢ submodule

## Bước 4 — Load context từng submodule

Với mỗi submodule phù hợp:
- Read `{subdir}/CLAUDE.md` nếu tồn tại
- Read `{subdir}/Agents.md` nếu tồn tại

## Bước 5 — Hướng dẫn research scripts

Sau khi load context xong, thông báo các lệnh có thể dùng để tra cứu.

Kiểm tra theo thứ tự:
1. Nếu `./scripts/doc_context.py` tồn tại trong project → dùng trực tiếp:
   ```
   python scripts/doc_context.py <keyword>
   python scripts/doc_context.py --scope <submodule> <keyword>
   ```
2. Nếu không → dùng từ toolkit (scripts đặt cùng chỗ với SKILL.md này):
   ```
   python <toolkit-path>/scripts/doc_context.py <keyword>
   ```
   Tương tự cho `code_research.py`.

## Bước 6 — Báo cáo tóm tắt

Sau khi hoàn tất, in 1 đoạn ngắn:
- Cấu trúc phát hiện: tên các submodule
- Execution mode hiện tại (Planning / Execution) từ root CLAUDE.md
- Workflow rule cần nhớ nhất (scripts cần chạy, quy tắc đặt tên file docs, v.v.)
