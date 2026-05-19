# bs-claude-toolkit

A Claude Code skill that enforces a consistent, structured coding workflow across any project.

> 🇻🇳 [Đọc bằng tiếng Việt](README.vi.md)

---

## What it does

When you type `/bs-claude-toolkit` in Claude Code, the skill runs automatically before any task:

1. **Loads project context** — reads config and submodule structure. On repeat runs, uses a cached stack profile instead of re-reading files (~90% fewer tokens).

2. **Auto-detects your tech stack** — scans `package.json`, `requirements.txt`, `go.mod`, `composer.json`, directory structure, etc. to determine language, framework, architecture pattern, async tech, and database. Writes the result to `.bs-toolkit.json` automatically so future runs use the cache.

3. **Computes the next sprint number** — scans `*/docs/plan/` to find the latest sprint and suggests the correct next number.

4. **Classifies your task** — detects whether it's a new feature, bug fix, refactor, or architecture question from the arguments you pass.

5. **Outputs an action brief** — execution mode, detected stack, next sprint, research commands to run, exact workflow steps, and a stack-specific code review checklist.

The enforced workflow for every task:

```
Research → Plan → Implement → Self-Review → Changelog → Test doc
```

Code review checklist adapts to your stack automatically:
- **Language rules**: Python, TypeScript, Go, Java/Kotlin, Node, PHP, Ruby
- **Architecture rules**: layered, MVC, hexagonal, microservices, CQRS
- **Async rules**: retry, idempotency, dead-letter, status transitions

**Solo and split-team modes** — two developers can work on BE and FE independently without conflicting sprint numbers or shared files.

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
/bs-claude-toolkit                    ← full context + action brief
/bs-claude-toolkit be                 ← focus on backend only
/bs-claude-toolkit fe                 ← focus on frontend only
/bs-claude-toolkit fix login bug      ← context + task classification
```

---

## Components

### `SKILL.md`

The core skill file at the repo root. Claude Code loads this automatically when you clone to `~/.claude/skills/`. Contains all the logic for the 6 phases: config loading, stack detection, sprint intelligence, task classification, action brief output, and proactive warnings.

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

## Requirements

- Python 3.8+ (stdlib only)
- Claude Code CLI
