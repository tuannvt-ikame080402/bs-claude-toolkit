# bs-claude-toolkit

Bộ công cụ chuẩn hóa workflow Claude Code cho các dự án fullstack.

## Nội dung

```
bs-claude-toolkit/
├── .claude/skills/ctx/SKILL.md   ← Skill /ctx cho Claude Code
├── scripts/
│   ├── doc_context.py            ← Tra cứu plan/changelog/test theo keyword
│   ├── code_research.py          ← Tra cứu code theo keyword
│   └── install.py                ← Script cài đặt vào project mới
└── templates/
    └── CLAUDE.md                 ← Template CLAUDE.md cho project mới
```

## Cài đặt vào project mới

```bash
# Clone toolkit
git clone https://github.com/your-org/bs-claude-toolkit.git
cd bs-claude-toolkit

# Cài vào project (copy scripts + cài global skill)
python scripts/install.py /path/to/your-project
```

Hoặc thủ công:

```bash
# 1. Copy scripts vào project
cp scripts/doc_context.py  your-project/scripts/
cp scripts/code_research.py your-project/scripts/

# 2. Cài skill globally (dùng được trong mọi project)
cp -r .claude/skills/ctx ~/.claude/skills/ctx
```

## Dùng trong project

### Scripts

```bash
# Tra cứu tài liệu theo keyword
python scripts/doc_context.py video generation retry

# Tra cứu code theo keyword
python scripts/code_research.py video_pipeline max_retries

# Có thể chạy từ subdir (scripts tự resolve ROOT)
cd backend && python scripts/doc_context.py auth token
```

### Skill Claude Code

```
/ctx            → auto-detect và load tất cả CLAUDE.md + Agents.md
/ctx backend    → chỉ load root + backend context
/ctx frontend   → chỉ load root + frontend context
/ctx all        → load root + backend + frontend
```

## Cấu trúc project được hỗ trợ

Scripts tự động detect, không cần config:

```
# Monorepo FE + BE
project/
├── frontend/docs/{plan,changelog,test}/
├── backend/docs/{plan,changelog,test}/
├── frontend/features/, components/, hooks/...
└── backend/app/{controllers,services,repositories}/...

# Single app
project/
├── docs/{plan,changelog,test}/
└── src/...

# Monorepo với nhiều packages
project/
├── apps/web/docs/
├── apps/api/docs/
└── packages/*/...
```

## Quy ước tên file tài liệu

| Loại | Format |
|------|--------|
| Sprint plan | `sprint-{N}-{slug}.md` |
| Ad-hoc plan | `{YYYYMMDD}-plan-{N}-{slug}.md` |
| Changelog | `{YYYYMMDD}-changelog-{N}-{slug}.md` |
| Test | `{YYYYMMDD}-test-{N}-{slug}.md` |

## Setup CLAUDE.md cho project mới

```bash
cp templates/CLAUDE.md your-project/CLAUDE.md
# Chỉnh sửa: tên dự án, flow chính, coding conventions
```
