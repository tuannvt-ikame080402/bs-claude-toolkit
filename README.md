# bs-claude-toolkit

A Claude Code skill that enforces a consistent, structured coding workflow across any project.

> 🇻🇳 [Đọc bằng tiếng Việt](README.vi.md)

---

## What it does

When you type `/bs-claude-toolkit` in Claude Code, the skill runs automatically before any task:

1. **Loads your project context** — reads `CLAUDE.md` and submodule configs. On repeat runs, uses a cached stack profile instead (~90% fewer tokens).

2. **Detects your tech stack** — language, framework, architecture pattern, async tech — from the cached profile or by parsing `CLAUDE.md`.

3. **Computes the next sprint number** — scans `*/docs/plan/` to find the latest sprint and suggests the correct next number.

4. **Classifies your task** — detects whether it's a new feature, bug fix, refactor, or architecture question.

5. **Outputs an action brief** — a structured plan showing: execution mode, stack, next sprint, research commands to run, the exact workflow to follow (plan → implement → review → changelog → test), and a stack-specific code review checklist.

The skill enforces this workflow for every task, across any language or architecture:

```
Research → Plan → Implement → Self-Review → Changelog → Test doc
```

**Code review checklist** adapts to your stack automatically:
- Language rules: Python, TypeScript, Go, Java/Kotlin, Node, PHP, Ruby
- Architecture rules: layered, MVC, hexagonal, microservices, CQRS
- Async rules: retry, idempotency, dead-letter, status transitions

**Solo and split-team modes** — two developers can work on BE and FE independently without stepping on each other's sprint numbers or shared files.

---

## Setup (one-time per machine)

### Step 1 — Clone the toolkit

```bash
git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git ~/.claude/skills/bs-claude-toolkit
```

Claude Code auto-discovers the skill. Use `/bs-claude-toolkit` from any project.

---

### Step 2 — Install into your project

Run from your project root:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py
```

This creates:
- `CLAUDE.md` — project context template
- `.bs-toolkit.json` — team config

---

### Step 3 — Fill in your Tech Stack

Open `CLAUDE.md` and fill in the **Tech Stack** table:

```markdown
| Backend language  | Python          |
| Backend framework | FastAPI         |
| Frontend language | TypeScript      |
| Frontend framework| Next.js         |
| Architecture      | layered         |
| Async / Queue     | Celery          |
| Database          | PostgreSQL      |
```

Also replace `[BE_DIR]` and `[FE_DIR]` with your actual directory names.

---

### Step 4 — Cache the stack profile

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
```

This saves the stack into `.bs-toolkit.json` so the skill doesn't re-read `CLAUDE.md` on every run (~90% token savings).

---

## Usage

```
/bs-claude-toolkit                    ← load full context + action brief
/bs-claude-toolkit be                 ← focus on backend only
/bs-claude-toolkit fe                 ← focus on frontend only
/bs-claude-toolkit fix login bug      ← context + task classification
```

---

## Split team (2 developers)

```bash
# Project lead — run once, commit .bs-toolkit.json
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py \
  --mode split --modules be:myapp-be,fe:myapp-fe

# Each developer — set personal scope (not committed)
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --scope be
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --scope fe
```

---

## Other tools (optional)

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --lang vi   # Vietnamese templates
```

---

## Requirements

- Python 3.8+ (stdlib only)
- Claude Code CLI
