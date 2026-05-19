---
description: Load project context from CLAUDE.md and Agents.md before starting any task
arguments: [scope]
---

Load project context for scope: "$ARGUMENTS" (backend | frontend | all | auto).

## Instructions

1. **Đọc root context** — luôn luôn:
   - Read `./CLAUDE.md`
   - Read `./Agents.md` (nếu tồn tại)

2. **Detect scope** — nếu `$ARGUMENTS` trống hoặc là "auto":
   - Check xem `./backend/` có tồn tại không
   - Check xem `./frontend/` có tồn tại không
   - Load cả hai nếu có

3. **Load backend context** — nếu scope là "backend", "all", hoặc auto-detect thấy `./backend/`:
   - Read `./backend/CLAUDE.md` (nếu tồn tại)
   - Read `./backend/Agents.md` (nếu tồn tại)

4. **Load frontend context** — nếu scope là "frontend", "all", hoặc auto-detect thấy `./frontend/`:
   - Read `./frontend/CLAUDE.md` (nếu tồn tại)
   - Read `./frontend/Agents.md` (nếu tồn tại)

5. **Báo cáo** — sau khi đọc xong, tóm tắt ngắn:
   - Đã đọc file nào
   - Project này là loại gì (FE-only / BE-only / fullstack)
   - Execution mode (Planning / Execution) theo CLAUDE.md

## Usage examples

```
/ctx            → auto-detect và load tất cả
/ctx backend    → chỉ load root + backend
/ctx frontend   → chỉ load root + frontend
/ctx all        → load root + backend + frontend
```
