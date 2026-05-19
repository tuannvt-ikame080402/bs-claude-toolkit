# bs-claude-toolkit — AI Coding Workflow Rules

## Context Loading

Before starting any task, read these files in order:
1. `CLAUDE.md` at project root (always)
2. `CLAUDE.md` and `Agents.md` inside any immediate subdirectory that contains `docs/` or its own `CLAUDE.md` — works with any naming convention (`backend/`, `myapp-be/`, `api/`, `web/`, etc.)

## Research Before Implementing

Run these scripts before fixing bugs or implementing features:

```bash
python scripts/doc_context.py <keyword>
python scripts/doc_context.py --scope <submodule-name> <keyword>
python scripts/code_research.py <keyword>
python scripts/code_research.py --scope <submodule-name> <keyword>
```

If scripts are not local, use toolkit path:
```bash
python ~/.claude/skills/bs-claude-toolkit/scripts/doc_context.py <keyword>
```

## Execution Mode

- **Planning (default):** No explicit code request → analysis, `.md` docs, architecture proposals only
- **Execution:** Only when explicitly requested → code, bug fix, refactor, tests

## Workflow

**New feature:** research → `docs/plan/sprint-{N}-{slug}.md` → implement → changelog → test doc

**Bug fix:** research → trace root cause → minimal fix → changelog (no plan file needed)

## Hard Rules

- Docs in Vietnamese (UTF-8), code in English
- No direct DB connections to production/staging
- No hardcoded secrets · No `any` type (TS) · No `print()` (Python)
- API contract changes must update docs immediately
