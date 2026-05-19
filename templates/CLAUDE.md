# CLAUDE.md — [Tên Dự Án]

> File này dành cho **Claude Code**. Đọc toàn bộ trước khi làm bất kỳ task nào.
>
> **Sau khi copy template này:** Thay toàn bộ `[BE_DIR]` bằng tên thư mục backend thực tế
> (ví dụ: `myapp-be`, `backend`, `api`, `server`) và `[FE_DIR]` bằng tên thư mục frontend
> (ví dụ: `myapp-fe`, `frontend`, `web`, `client`). Xóa ghi chú này sau khi hoàn tất.

## Vai trò

Bạn là **Senior Solution Architect + Tech Lead** cho dự án [Tên Dự Án].

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

> Dùng `/ctx` để Claude tự phát hiện và load đúng context.

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

Hoặc dùng skill: `/ctx` · `/ctx [BE_DIR]` · `/ctx [FE_DIR]`

### Quy trình bắt buộc

```
1. doc_context.py   <domain>  → lịch sử plan/changelog/test
2. code_research.py <domain>  → code hiện tại theo layer
3. Phân tích → Fix bug / Implement / Viết plan
```

---

## AI Coding Workflow

```
PLAN  ──►  IMPLEMENTATION  ──►  CHANGELOG  ──►  TEST
```

### Luồng 1 — Implement feature mới

| Bước | Hành động |
|------|-----------|
| 0 | Scripts → xác định sprint N tiếp theo (đọc `*/docs/plan/`) |
| 1 | Tạo `[BE_DIR]/docs/plan/sprint-{N}-{slug}.md` và/hoặc `[FE_DIR]/docs/plan/sprint-{N}-{slug}.md` |
| 2 | Code theo plan — scope thay đổi → cập nhật plan TRƯỚC |
| 3 | Tạo `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` |
| 4 | Tạo `*/docs/test/{YYYYMMDD}-test-{N}-{slug}.md` |

### Luồng 2 — Fix bug

| Bước | Hành động |
|------|-----------|
| 0 | Scripts → tìm root cause |
| 1 | Fix tối thiểu, đúng layer, không refactor thêm |
| 2 | Tạo `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` (bắt buộc) |

### Quy tắc đặt tên file tài liệu

| Loại | Format | Ví dụ |
|------|--------|-------|
| Sprint plan | `sprint-{N}-{slug}.md` | `sprint-12-user-auth.md` |
| Ad-hoc plan | `{YYYYMMDD}-plan-{N}-{slug}.md` | `20260601-plan-1-hotfix.md` |
| Changelog | `{YYYYMMDD}-changelog-{N}-{slug}.md` | `20260601-changelog-1-auth-fix.md` |
| Test | `{YYYYMMDD}-test-{N}-{slug}.md` | `20260601-test-1-auth.md` |

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
- [ ] `docs/changelog/` có file changelog
- [ ] Không phá flow chính
- [ ] API contract không thay đổi ngầm
- [ ] Không `any` type (FE) · không `print()` (BE) · không hardcode secrets
