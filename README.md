# bs-claude-toolkit

Bộ công cụ chuẩn hóa workflow **Claude Code** cho các dự án fullstack.

Tự động phát hiện cấu trúc project — không cần cấu hình, không phụ thuộc tên thư mục.

---

## Cài đặt (một lần duy nhất)

```bash
git clone https://github.com/your-org/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit
```

**Xong.** Từ đây `/bs-claude-toolkit` hoạt động trong mọi project trên máy.

> Muốn tên lệnh ngắn hơn:
> ```bash
> git clone https://github.com/your-org/bs-claude-toolkit.git ~/.claude/skills/ctx
> # → dùng /ctx thay vì /bs-claude-toolkit
> ```

---

## Cập nhật

```bash
cd ~/.claude/skills/bs-claude-toolkit && git pull
```

---

## Sử dụng trong Claude Code

```
/bs-claude-toolkit              → load root + tất cả submodule (auto-detect)
/bs-claude-toolkit be           → load root + submodule có "be" trong tên
/bs-claude-toolkit fe           → load root + submodule có "fe" trong tên
/bs-claude-toolkit myapp-be     → load root + submodule khớp "myapp-be"
```

---

## Research scripts

Scripts có thể chạy trực tiếp từ toolkit (không cần copy vào project):

```bash
# Tra cứu tài liệu plan/changelog/test
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py <keyword>
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py --scope be <keyword>
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py --scope fe <keyword>

# Tra cứu code
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py <keyword>
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py --scope be <keyword>
```

> Scripts dùng `CWD` để tìm project root — chạy từ đâu trong project cũng đúng.

### Copy scripts vào project (tuỳ chọn)

Hữu ích khi team không muốn cài toolkit trên mọi máy:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py /path/to/project
# → copy doc_context.py và code_research.py vào project/scripts/
```

Sau đó team dùng:
```bash
python scripts/doc_context.py <keyword>
python scripts/code_research.py <keyword>
```

---

## Cấu trúc repo

```
bs-claude-toolkit/
├── SKILL.md              ← Định nghĩa skill /bs-claude-toolkit
├── scripts/
│   ├── doc_context.py    ← Tra cứu plan/changelog/test theo keyword
│   ├── code_research.py  ← Tra cứu code theo keyword
│   └── install.py        ← Copy scripts vào project (tuỳ chọn)
└── templates/
    └── CLAUDE.md         ← Template CLAUDE.md cho project mới
```

---

## Naming convention được hỗ trợ

Skill và scripts phát hiện submodule dựa trên **nội dung** (có `CLAUDE.md` / `Agents.md` / `docs/`), không phụ thuộc tên thư mục.

| Convention | BE dir | FE dir |
|------------|--------|--------|
| Chuẩn | `backend/` | `frontend/` |
| Theo tên dự án | `myapp-be/` | `myapp-fe/` |
| Ngắn | `be/` | `fe/` |
| Theo role | `api/` | `web/` |
| Theo role | `server/` | `client/` |

### `--scope` filter

`--scope` khớp **một phần tên** (case-insensitive):

```bash
--scope be   → match: backend, myapp-be, be, server
--scope fe   → match: frontend, myapp-fe, fe, web, client
--scope api  → match: api, myapp-api
```

---

## Setup CLAUDE.md cho project mới

```bash
cp ~/.claude/skills/bs-claude-toolkit/templates/CLAUDE.md /path/to/project/CLAUDE.md
# Thay [BE_DIR] và [FE_DIR] bằng tên thư mục thực tế
```

---

## Yêu cầu

- Python 3.8+ (stdlib only, không cần cài thêm package)
- Claude Code CLI
