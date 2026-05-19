# bs-claude-toolkit

Skill Claude Code giúp áp dụng quy trình coding có cấu trúc, nhất quán cho mọi project.

> 🇬🇧 [Read in English](README.md)

---

## Skill này làm gì?

Khi bạn gõ `/bs-claude-toolkit` trong Claude Code, skill tự động chạy trước mọi task:

1. **Load context project** — đọc `CLAUDE.md` và config submodule. Ở các lần sau, dùng stack profile đã cache → tiết kiệm ~90% token.

2. **Detect tech stack** — ngôn ngữ, framework, kiến trúc, async tech — từ cache hoặc parse `CLAUDE.md`.

3. **Tính số sprint tiếp theo** — scan `*/docs/plan/` để tìm sprint mới nhất và đề xuất số đúng.

4. **Phân loại task** — detect task là feature mới, bug fix, refactor hay câu hỏi kiến trúc.

5. **Output action brief** — bản tóm tắt có cấu trúc gồm: execution mode, stack, sprint tiếp theo, lệnh research cần chạy, workflow cần theo (plan → implement → review → changelog → test), và review checklist phù hợp với stack.

Skill enforce quy trình này cho mọi task, với mọi ngôn ngữ và kiến trúc:

```
Research → Plan → Implement → Self-Review → Changelog → Test doc
```

**Review checklist tự động thích nghi theo stack:**
- Language rules: Python, TypeScript, Go, Java/Kotlin, Node, PHP, Ruby
- Architecture rules: layered, MVC, hexagonal, microservices, CQRS
- Async rules: retry, idempotency, dead-letter, status transitions

**Solo và split-team mode** — hai developer có thể làm việc độc lập trên BE và FE mà không conflict số sprint hay shared files.

---

## Cài đặt (một lần mỗi máy)

### Bước 1 — Clone toolkit

```bash
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit
```

Claude Code tự nhận diện skill. Dùng `/bs-claude-toolkit` từ bất kỳ project nào.

---

### Bước 2 — Cài vào project

Chạy từ thư mục gốc project:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py
```

Tạo ra:
- `CLAUDE.md` — template context cho project
- `.bs-toolkit.json` — config team

---

### Bước 3 — Điền Tech Stack

Mở `CLAUDE.md` và điền bảng **Tech Stack**:

```markdown
| Backend language  | Python          |
| Backend framework | FastAPI         |
| Frontend language | TypeScript      |
| Frontend framework| Next.js         |
| Architecture      | layered         |
| Async / Queue     | Celery          |
| Database          | PostgreSQL      |
```

Đồng thời thay `[BE_DIR]` và `[FE_DIR]` bằng tên thư mục thực tế.

---

### Bước 4 — Cache stack profile

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
```

Lưu stack vào `.bs-toolkit.json` để skill không cần đọc lại `CLAUDE.md` mỗi lần chạy (~90% tiết kiệm token).

---

## Sử dụng

```
/bs-claude-toolkit                    ← load full context + action brief
/bs-claude-toolkit be                 ← chỉ tập trung backend
/bs-claude-toolkit fe                 ← chỉ tập trung frontend
/bs-claude-toolkit fix login bug      ← context + phân loại task
```

---

## Split team (2 developers)

```bash
# Project lead — chạy 1 lần, commit .bs-toolkit.json
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py \
  --mode split --modules be:myapp-be,fe:myapp-fe

# Mỗi developer — set personal scope (không commit)
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --scope be
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --scope fe
```

---

## Các tool khác (tuỳ chọn)

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --lang vi   # template tiếng Việt
```

---

## Yêu cầu

- Python 3.8+ (stdlib only)
- Claude Code CLI
