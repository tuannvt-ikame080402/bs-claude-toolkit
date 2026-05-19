# bs-claude-toolkit

Bộ công cụ chuẩn hóa workflow AI coding cho các dự án fullstack.
Hỗ trợ **Claude Code · Cursor · Codex · Windsurf**.

---

## Cài đặt nhanh

### Bước 1 — Clone toolkit (một lần duy nhất)

```bash
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit
```

> Claude Code tự nhận `/bs-claude-toolkit` ngay sau khi clone xong — không cần thêm bước nào.

Muốn tên lệnh ngắn hơn:
```bash
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/ctx
# → dùng /ctx
```

### Bước 2 — Cài vào project (chạy từ thư mục project)

```bash
# Tất cả tools
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py

# Hoặc từng tool
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool scripts  # chỉ copy research scripts
```

---

## Hỗ trợ theo tool

### Claude Code

| Scope | Cách dùng |
|-------|-----------|
| Global | Clone vào `~/.claude/skills/bs-claude-toolkit/` |
| Invoke | `/bs-claude-toolkit` trong chat |
| Filter | `/bs-claude-toolkit be` · `/bs-claude-toolkit fe` |

Skill tự phát hiện submodule dựa trên nội dung (có `CLAUDE.md` / `Agents.md` / `docs/`), không phụ thuộc tên thư mục.

---

### Codex (OpenAI)

| Scope | File | Cách install |
|-------|------|-------------|
| Global | `~/.codex/AGENTS.md` | `install.py --tool codex --global` |
| Per-project | `[project]/AGENTS.md` | `install.py --tool codex` |
| Per-submodule | `[subdir]/AGENTS.md` | Copy thủ công |

Codex đọc theo thứ tự: `~/.codex/AGENTS.md` → root `AGENTS.md` → subdirectory `AGENTS.md`.

Cài global (áp dụng cho mọi project trên máy):
```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex --global
```

---

### Cursor

| Scope | File | Cách install |
|-------|------|-------------|
| Per-project | `.cursor/rules/bs-claude-toolkit.mdc` | `install.py --tool cursor` |
| Global | Settings UI → Rules | Paste nội dung `adapters/cursor.mdc` |

Rule dùng `alwaysApply: true` — tự apply cho mọi session trong project.

---

### Windsurf

| Scope | File | Cách install |
|-------|------|-------------|
| Per-project | `.windsurf/rules/bs-claude-toolkit.md` | `install.py --tool windsurf` |

---

## Solo vs Split Team

### Solo — 1 người code cả BE + FE

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --mode solo
```

`/bs-claude-toolkit` load toàn bộ context, sprint numbers tính chung.

---

### Split — 2 người code riêng

```bash
# Project lead chạy một lần, commit .bs-toolkit.json
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py \
  --mode split --modules be:myapp-be,fe:myapp-fe
```

**Mỗi developer** chạy riêng để set personal scope (không commit):

```bash
# Dev BE
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --scope be

# Dev FE
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --scope fe
```

Từ đó `/bs-claude-toolkit` tự động load đúng scope mà không cần gõ thêm.

#### Conflict prevention trong split mode

| Zone | Files | Rule |
|------|-------|------|
| ✏️ **Your zone** | `{module}/` code + `{module}/docs/` | Tự do edit |
| 🤝 **Shared zone** | `CLAUDE.md`, `docs/api-contract.md` | Cần sync với team trước |

- Sprint numbers **độc lập per-submodule** — BE sprint-15, FE sprint-12 là bình thường
- Changelog/test files trong `{module}/docs/` riêng — không conflict
- API contract thay đổi → cần cả 2 bên đồng thuận

#### Khi không có `default_scope`

Skill sẽ nhắc:
```
⚠️  Split team mode detected. Bạn đang làm việc ở module nào?
    /bs-claude-toolkit be
    /bs-claude-toolkit fe
    /bs-claude-toolkit all   ← fullstack session
```

---

## Cập nhật toolkit

```bash
cd ~/.claude/skills/bs-claude-toolkit && git pull
```

---

## Cài đặt đầy đủ cho máy mới

```bash
# 1. Clone một lần duy nhất
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit

# 2. Codex global — áp dụng cho mọi project trên máy (tuỳ chọn)
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex --global

# 3. Với từng project mới — chạy trong thư mục project
cd /path/to/your-project
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py
```

Per-project files (`.cursor/rules/`, `AGENTS.md`, v.v.) cần chạy lại `install.py` để cập nhật.

---

## Research scripts

Chạy trực tiếp từ toolkit (không cần copy vào project):

```bash
# Tra cứu plan/changelog/test
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py <keyword>
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py --scope be <keyword>
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py --scope fe <keyword>

# Tra cứu code
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py <keyword>
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py --scope be <keyword>
```

Scripts dùng `CWD` để tìm project root — chạy từ bất kỳ thư mục nào trong project đều đúng.

Muốn scripts nằm trong project (cho team không có toolkit):
```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool scripts
```

---

## Cấu trúc repo

```
bs-claude-toolkit/
├── SKILL.md                           ← Claude Code global skill
├── adapters/
│   ├── cursor.mdc                     ← Cursor rule (alwaysApply)
│   └── windsurf.md                    ← Windsurf rule
├── scripts/
│   ├── doc_context.py                 ← Tra cứu docs (auto-detect, --scope)
│   ├── code_research.py               ← Tra cứu code (auto-detect, --scope)
│   └── install.py                     ← Installer cho từng tool
└── templates/
    ├── CLAUDE.md                      ← Template cho Claude Code projects
    └── AGENTS.md                      ← Template cho Codex projects
```

---

## Naming convention được hỗ trợ

Toolkit phát hiện submodule bằng **nội dung** (có `CLAUDE.md` / `Agents.md` / `docs/`), không phụ thuộc tên.

| Convention | BE | FE |
|------------|----|----|
| Chuẩn | `backend/` | `frontend/` |
| Theo tên dự án | `myapp-be/` | `myapp-fe/` |
| Ngắn | `be/` | `fe/` |
| Theo role | `api/` | `web/` |
| Theo role | `server/` | `client/` |

`--scope` khớp một phần tên (case-insensitive): `--scope be` match `backend`, `myapp-be`, `be`, `server`.

---

## Yêu cầu

- Python 3.8+ (stdlib only)
- Claude Code CLI (cho `/bs-claude-toolkit`)
