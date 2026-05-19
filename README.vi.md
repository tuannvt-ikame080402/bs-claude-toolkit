# bs-claude-toolkit

Skill Claude Code giúp áp dụng quy trình coding có cấu trúc, nhất quán cho mọi project.

> 🇬🇧 [Read in English](README.md)

---

## Skill này làm gì?

Khi bạn gõ `/bs-claude-toolkit` trong Claude Code, skill tự động chạy trước mọi task:

1. **Load context project** — đọc config và cấu trúc submodule. Các lần sau dùng stack profile đã cache thay vì đọc lại file (~90% ít token hơn).

2. **Tự detect tech stack** — quét `package.json`, `requirements.txt`, `go.mod`, `composer.json`, cấu trúc thư mục, v.v. để xác định ngôn ngữ, framework, kiến trúc, async tech, database. Tự ghi kết quả vào `.bs-toolkit.json` để lần sau dùng cache.

3. **Tính số sprint tiếp theo** — scan `*/docs/plan/` để tìm sprint mới nhất và đề xuất số đúng.

4. **Phân loại task** — detect task là feature mới, bug fix, refactor hay câu hỏi kiến trúc từ argument bạn truyền vào.

5. **Output action brief** — execution mode, stack detect được, sprint tiếp theo, lệnh research cần chạy, các bước workflow cụ thể, và review checklist phù hợp với stack.

Workflow được enforce cho mọi task:

```
Research → Plan → Implement → Self-Review → Changelog → Test doc
```

Review checklist tự động thích nghi theo stack:
- **Language rules**: Python, TypeScript, Go, Java/Kotlin, Node, PHP, Ruby
- **Architecture rules**: layered, MVC, hexagonal, microservices, CQRS
- **Async rules**: retry, idempotency, dead-letter, status transitions

**Solo và split-team mode** — hai developer làm việc độc lập trên BE và FE mà không conflict số sprint hay shared files.

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

Tạo ra `CLAUDE.md` (template context) và `.bs-toolkit.json` (config team).
Thay `[BE_DIR]` / `[FE_DIR]` trong `CLAUDE.md` bằng tên thư mục thực tế.

---

### Bước 3 — Chạy skill

Mở Claude Code trong project và gõ:

```
/bs-claude-toolkit
```

Skill tự detect stack từ project files và cache vào `.bs-toolkit.json`. Mọi lần sau dùng cache — không detect lại.

---

## Sử dụng

```
/bs-claude-toolkit                    ← full context + action brief
/bs-claude-toolkit be                 ← chỉ tập trung backend
/bs-claude-toolkit fe                 ← chỉ tập trung frontend
/bs-claude-toolkit fix login bug      ← context + phân loại task
```

---

## Các thành phần

### `SKILL.md`

File skill chính ở root repo. Claude Code tự load khi clone vào `~/.claude/skills/`. Chứa toàn bộ logic 6 phase: load config, detect stack, sprint intelligence, phân loại task, output action brief, và proactive warnings.

---

### `scripts/`

Các script tiện ích để research và setup. Có thể chạy trực tiếp từ toolkit hoặc copy vào project.

| Script | Chức năng |
|--------|-----------|
| `doc_context.py` | Tìm kiếm trong sprint plan, changelog, test doc đã có theo keyword. Dùng trước mọi task để hiểu context lịch sử. Hỗ trợ `--scope be/fe`. |
| `code_research.py` | Tìm kiếm trong code hiện tại theo keyword, nhóm theo layer (controller, service, repository, v.v.). Hỗ trợ `--scope`. |
| `reorder_docs.py` | Sắp xếp lại thứ tự số của doc files theo thời gian tạo sau khi merge conflict. Khi 2 developer tạo file cùng số thứ tự, script đặt lại số dựa trên thứ tự commit — file được commit trước giữ số nhỏ hơn. |
| `install.py` | Tool setup đầy đủ. Cài rules cho từng AI tool, tạo config files, và chạy wizard setup stack profile (`--setup-stack`). |

```bash
# Ví dụ
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py pagination
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py --scope be retry
python ~/.claude/skills/bs-claude-toolkit/scripts/reorder_docs.py --dry-run
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
```

---

### `adapters/`

Các file rules cho AI coding tool khác ngoài Claude Code. Mỗi file dạy tool đó cùng một quy trình: thứ tự load context, thói quen research trước khi code, planning vs execution mode, và code review checklist.

| File | Tool | Áp dụng khi nào |
|------|------|-----------------|
| `cursor.mdc` | Cursor | `alwaysApply: true` — mọi session trong project |
| `cursor.vi.mdc` | Cursor | Phiên bản tiếng Việt |
| `windsurf.md` | Windsurf | Mọi session trong project |
| `windsurf.vi.md` | Windsurf | Phiên bản tiếng Việt |

Cài bằng:
```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
```

---

### `templates/`

Các file mẫu được copy vào project khi chạy `install.py`. Chỉnh sửa sau khi copy — có placeholder `[BE_DIR]`, `[FE_DIR]` cần thay bằng tên thư mục thực tế.

| File | Mục đích |
|------|---------|
| `CLAUDE.md` | Context cho Claude Code — vai trò, execution mode, workflow, conventions, DoD |
| `CLAUDE.vi.md` | Phiên bản tiếng Việt |
| `AGENTS.md` | Context cho Codex (OpenAI) — nội dung tương tự, định dạng plain markdown |
| `AGENTS.vi.md` | Phiên bản tiếng Việt |
| `.bs-toolkit.json` | Config team — `stack_profile` và optional `modules` name mapping |

---

## Các tool khác (tuỳ chọn)

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --lang vi   # template tiếng Việt
```

---

## Yêu cầu

- Python 3.8+ (stdlib only)
- Claude Code CLI
