# bs-claude-toolkit

A Claude Code skill that enforces a consistent, structured coding workflow across any project.

> 🇻🇳 [Đọc bằng tiếng Việt](README.vi.md)

---

## What it does

Three sub-commands, each doing real work:

| Command | What happens |
|---------|-------------|
| `/bs-claude-toolkit plan [scope] task` | Claude runs research scripts, then **creates** `sprint-N-slug.md` with context, analysis, and implementation steps |
| `/bs-claude-toolkit review [scope]` | Claude reads `git diff`, then **applies** the stack-specific checklist to the actual changes and outputs findings |
| `/bs-claude-toolkit [scope]` | Orientation only — shows stack, next sprint number, and the workflow |

**Team split:**
```
Claude:  /plan  →  [Codex: implement + docs + tests]  →  Claude: /review
```

On every run the skill also:

- **Loads project context** — reads config and submodule structure. On repeat runs, uses a cached stack profile instead of re-reading files (~90% fewer tokens).
- **Auto-detects your tech stack** — scans `package.json`, `requirements.txt`, `go.mod`, etc. Writes the result to `.bs-toolkit.json` so future runs use the cache.
- **Computes the next sprint number** — scans `*/docs/plan/` to find the latest sprint.

Code review checklist adapts to your stack automatically:
- **Language rules**: Python, TypeScript, Go, Java/Kotlin, Node, PHP, Ruby
- **Architecture rules**: layered, MVC, hexagonal, microservices, CQRS
- **Async rules**: retry, idempotency, dead-letter, status transitions

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

Creates `CLAUDE.md` (project context template) and `.bs-toolkit.json` (team config).
Replace `[BE_DIR]` / `[FE_DIR]` in `CLAUDE.md` with your actual directory names.

---

### Step 3 — Run the skill

Open Claude Code in your project and type:

```
/bs-claude-toolkit
```

The skill auto-detects your stack from project files and caches it into `.bs-toolkit.json`. All future runs use the cache — no re-detection needed.

---

## Usage

```
# Plan — Claude researches and creates the sprint plan doc
/bs-claude-toolkit plan fix video retry not triggering
/bs-claude-toolkit plan be add pagination to orders API
/bs-claude-toolkit plan fe refactor asset upload flow

# Review — Claude reads git diff and applies the checklist
/bs-claude-toolkit review
/bs-claude-toolkit review be          ← focus review on backend

# Brief — orientation only, no files created
/bs-claude-toolkit                    ← show stack + next sprint + workflow
/bs-claude-toolkit be                 ← scope to backend only
```

---

## Components

### `SKILL.md`

The core skill file at the repo root. Claude Code loads this automatically when you clone to `~/.claude/skills/`. Contains the logic for 6 phases: config loading, stack detection, sprint intelligence, task classification, mode execution (`plan` / `review` / `brief`), and proactive warnings.

---

### `scripts/`

Utility scripts for research and setup. Can run directly from the toolkit path or be copied into a project.

| Script | What it does |
|--------|-------------|
| `doc_context.py` | Search past sprint plans, changelogs, and test docs by keyword. Run before any task to understand history. Supports `--scope be/fe`. |
| `code_research.py` | Search current code by keyword, grouped by layer (controller, service, repository, etc.). Supports `--scope`. |
| `reorder_docs.py` | Re-sequence doc files by git commit time after a merge conflict. When two developers create files with the same sequence number, renumbers them so the earliest commit keeps the lowest number. |
| `install.py` | Full setup tool. Installs rules for each AI tool, generates config files, and runs the stack profile wizard (`--setup-stack`). |

```bash
# Example usage
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py pagination
python ~/.claude/skills/bs-claude-toolkit/scripts/code_research.py --scope be retry
python ~/.claude/skills/bs-claude-toolkit/scripts/reorder_docs.py --dry-run
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --setup-stack
```

---

### `adapters/`

Rules files for AI coding tools other than Claude Code. Each file teaches the tool the same workflow: context loading order, research-before-coding habit, planning mode vs execution mode, and the code review checklist.

| File | Tool | Applied when |
|------|------|-------------|
| `cursor.mdc` | Cursor | `alwaysApply: true` — every session in the project |
| `cursor.vi.mdc` | Cursor | Vietnamese version |
| `windsurf.md` | Windsurf | Every session in the project |
| `windsurf.vi.md` | Windsurf | Vietnamese version |

Install with:
```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
```

---

### `templates/`

Starting-point files copied into your project during `install.py`. Edit after copying — they contain `[BE_DIR]`, `[FE_DIR]` placeholders to replace with actual directory names.

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context for Claude Code — role, execution mode, workflow, conventions, DoD |
| `CLAUDE.vi.md` | Vietnamese version |
| `AGENTS.md` | Project context for Codex (OpenAI) — same content, plain markdown format |
| `AGENTS.vi.md` | Vietnamese version |
| `.bs-toolkit.json` | Team config — `stack_profile` and optional `modules` name mapping |

---

## Other tools (optional)

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --lang vi   # Vietnamese templates
```

---

## Updating the skill

When a new version is released, pull the latest changes:

```bash
git -C ~/.claude/skills/bs-claude-toolkit pull --ff-only
```

Then re-run the installer in your project to sync any updated adapter rules or templates:

```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor
python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool windsurf
```

> Your `.bs-toolkit.json` and `CLAUDE.md` are not overwritten — only the adapter rules in `.cursor/rules/` and `.windsurf/rules/` are updated.

---

## Requirements

- Python 3.8+ (stdlib only)
- Claude Code CLI
