# bs-claude-toolkit

Bộ công cụ chuẩn hóa workflow **Claude Code** cho các dự án fullstack.

Tự động phát hiện cấu trúc project — không cần cấu hình, không phụ thuộc tên thư mục.

---

## Nội dung

```
bs-claude-toolkit/
├── .claude/
│   └── skills/
│       └── ctx/
│           └── SKILL.md        ← Skill /ctx cho Claude Code
├── scripts/
│   ├── doc_context.py          ← Tra cứu plan/changelog/test theo keyword
│   ├── code_research.py        ← Tra cứu code theo keyword
│   └── install.py              ← Setup vào project mới
└── templates/
    └── CLAUDE.md               ← Template CLAUDE.md cho project mới
```

---

## Cài đặt nhanh

```bash
git clone https://github.com/your-org/bs-claude-toolkit.git
cd bs-claude-toolkit

# Cài vào project (copy scripts + install global skill)
python scripts/install.py /path/to/your-project
```

Hoặc thủ công:

```bash
# Copy scripts vào project
cp scripts/doc_context.py   /path/to/your-project/scripts/
cp scripts/code_research.py /path/to/your-project/scripts/

# Cài /ctx skill globally (dùng được trong mọi project)
cp -r .claude/skills/ctx ~/.claude/skills/ctx
```

---

## Sử dụng

### Scripts

```bash
# Từ root project — tra cứu tài liệu
python scripts/doc_context.py video generation retry
python scripts/doc_context.py notification toast

# Lọc theo submodule (--scope khớp một phần tên thư mục)
python scripts/doc_context.py --scope be  video retry
python scripts/doc_context.py --scope fe  notification

# Tra cứu code
python scripts/code_research.py video_pipeline max_retries
python scripts/code_research.py --scope be  celery task
python scripts/code_research.py --scope fe  useAssets refetchInterval
```

### Skill Claude Code

```
/ctx              → load root + tất cả submodule (auto-detect)
/ctx be           → load root + submodule có "be" trong tên
/ctx fe           → load root + submodule có "fe" trong tên
/ctx myapp-be     → load root + submodule tên chứa "myapp-be"
/ctx api          → load root + submodule tên chứa "api"
```

---

## Naming convention được hỗ trợ

Toolkit tự phát hiện submodule dựa trên **nội dung** (CLAUDE.md / Agents.md / docs/), không phải tên thư mục.

| Convention | BE dir | FE dir |
|------------|--------|--------|
| Chuẩn | `backend/` | `frontend/` |
| Theo tên dự án | `myapp-be/` | `myapp-fe/` |
| Ngắn | `be/` | `fe/` |
| Theo role | `api/` | `web/` |
| Theo role | `server/` | `client/` |
| Monorepo | `apps/api/` | `apps/web/` |

### Ví dụ cấu trúc project thực tế

```
# iCreative
icreative/
├── backend/         ✓ có CLAUDE.md
├── frontend/        ✓ có CLAUDE.md
└── CLAUDE.md

# Dự án A
project-a/
├── project-a-be/    ✓ có docs/
├── project-a-fe/    ✓ có docs/
└── CLAUDE.md

# Single-app
myapp/
├── docs/plan/       ✓ phát hiện trực tiếp
├── src/
└── CLAUDE.md
```

---

## Quy ước tài liệu

| Loại file | Format tên |
|-----------|-----------|
| Sprint plan | `sprint-{N}-{slug}.md` |
| Ad-hoc plan | `{YYYYMMDD}-plan-{N}-{slug}.md` |
| Changelog | `{YYYYMMDD}-changelog-{N}-{slug}.md` |
| Test | `{YYYYMMDD}-test-{N}-{slug}.md` |

Đặt trong: `{submodule}/docs/{plan|changelog|test}/`

---

## Setup CLAUDE.md cho project mới

```bash
cp templates/CLAUDE.md your-project/CLAUDE.md
```

Sau đó thay `[BE_DIR]` và `[FE_DIR]` bằng tên thư mục thực tế trong project.

---

## Yêu cầu

- Python 3.8+ (stdlib only, không cần cài thêm package)
- Claude Code (cho `/ctx` skill)
