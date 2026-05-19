---
description: Load project context (CLAUDE.md + Agents.md) before any task. Auto-detects all submodule dirs regardless of naming convention.
arguments: [scope]
---

Load project context. Scope filter (optional): "$ARGUMENTS"

## Bước 1 — Luôn đọc root context

- Read `./CLAUDE.md`
- Read `./Agents.md` nếu tồn tại

## Bước 2 — Phát hiện submodule dirs

Scan tất cả immediate subdirectories của root. Một subdir được coi là **submodule** nếu thỏa mãn ÍT NHẤT MỘT trong:
- Chứa `CLAUDE.md`
- Chứa `Agents.md`
- Chứa thư mục `docs/`

Không phụ thuộc vào tên thư mục — hoạt động với mọi convention:
`backend/`, `frontend/`, `myapp-be/`, `myapp-fe/`, `api/`, `web/`, `server/`, `client/`, v.v.

## Bước 3 — Filter theo scope (nếu có)

Nếu `$ARGUMENTS` không trống: chỉ load các submodule mà tên chứa chuỗi `$ARGUMENTS` (case-insensitive).

Ví dụ:
- `/ctx be` → match `backend`, `myapp-be`, `be`, `server`
- `/ctx fe` → match `frontend`, `myapp-fe`, `fe`, `web`, `client`
- `/ctx api` → match `api`, `myapp-api`
- `/ctx` (không arg) → load TẤT CẢ submodule tìm được

## Bước 4 — Load context từng submodule

Với mỗi submodule đã lọc:
- Read `{subdir}/CLAUDE.md` nếu tồn tại
- Read `{subdir}/Agents.md` nếu tồn tại

## Bước 5 — Báo cáo (ngắn gọn)

Sau khi đọc xong, in 1 đoạn tóm tắt:
- Cấu trúc phát hiện: tên các submodule và loại (BE/FE/unknown)
- Execution mode từ root CLAUDE.md (Planning / Execution)
- Workflow rule quan trọng nhất cần nhớ (scripts cần chạy, convention đặt tên file, v.v.)

## Ví dụ sử dụng

```
/ctx              → load root + tất cả submodule
/ctx be           → load root + submodule có "be" trong tên
/ctx fe           → load root + submodule có "fe" trong tên
/ctx myapp-be     → load root + submodule tên chứa "myapp-be"
/ctx api          → load root + submodule tên chứa "api"
```
