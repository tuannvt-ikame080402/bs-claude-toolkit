# CLAUDE.md — [Tên Dự Án]

> File này dành cho **Claude Code**. Đọc toàn bộ trước khi làm bất kỳ task nào.

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

## Điều hướng — Đọc file nào khi làm task nào

| Phạm vi task | File bổ sung cần đọc |
|-------------|----------------------|
| Frontend (UI, React, hooks) | `frontend/CLAUDE.md` |
| Backend (API, worker) | `backend/CLAUDE.md` |
| FE + BE cùng lúc | Đọc cả hai |
| Planning / kiến trúc | Chỉ file này |

---

## Scripts tra cứu — BẮT BUỘC trước MỌI task

```bash
# Lịch sử plan/changelog/test
python scripts/doc_context.py <keyword>

# Code hiện tại theo layer
python scripts/code_research.py <keyword>
```

Hoặc dùng skill: `/ctx` (Claude Code)

### Quy trình bắt buộc

```
1. doc_context.py   <domain>  → lịch sử plan/changelog/test
2. code_research.py <domain>  → code hiện tại theo layer
3. Phân tích → Fix bug / Implement / Viết plan
```

---

## AI Coding Workflow

```
PLAN → IMPLEMENTATION → CHANGELOG → TEST
```

### Luồng 1 — Implement feature mới

| Bước | Hành động |
|------|-----------|
| 0 | Scripts → xác định sprint N tiếp theo |
| 1 | Tạo `docs/plan/sprint-{N}-{slug}.md` |
| 2 | Code theo plan |
| 3 | Tạo `docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` |
| 4 | Tạo `docs/test/{YYYYMMDD}-test-{N}-{slug}.md` |

### Luồng 2 — Fix bug

| Bước | Hành động |
|------|-----------|
| 0 | Scripts → tìm root cause |
| 1 | Fix tối thiểu, đúng layer |
| 2 | Tạo `docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` |

---

## Nguyên tắc bắt buộc

1. **Tài liệu bằng tiếng Việt có dấu, UTF-8** — code dùng tiếng Anh
2. **Không viết code khi chưa có plan** (Planning mode)
3. Không hard-code secrets
4. Không bỏ qua logging, error handling, retry policy

---

## Nguyên tắc kỹ thuật

1. Scale được
2. Đơn giản (tránh over-engineering)
3. Dễ maintain
4. Performance (sau cùng)

---

## Definition of Done

- [ ] Code chạy được local
- [ ] Test pass (happy + edge + failure case)
- [ ] `docs/changelog/` có file changelog
- [ ] Không phá flow chính
- [ ] API contract không thay đổi ngầm
