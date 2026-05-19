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

**New feature:** research → `docs/plan/sprint-{N}-{slug}.md` → implement → **self-review** → changelog → test doc

**Bug fix:** research → trace root cause → minimal fix → **self-review** → changelog (no plan file needed)

## Code Review

After every implementation or fix, verify against the stack declared in `CLAUDE.md` (Tech Stack section):

**Universal**
- No hardcoded secrets, credentials, or magic numbers · Clear naming
- All error paths handled — no silent failures
- API contract not silently changed → update docs if changed
- Core flow not broken

**Language** (match rules to your stack in `CLAUDE.md`)
- Python → No `print()` · type hints · f-strings
- TypeScript → No `any` · no unsafe `!` · strict mode
- Go → Check all errors (no `_`) · no `panic()` in lib · context propagation
- Java/Kotlin → No `System.out` · handle checked exceptions · try-with-resources
- Node/JS → No `console.log` · proper async/await
- PHP → No `var_dump` · PSR logging · declare types

**Architecture** (match rules to your pattern in `CLAUDE.md`)
- layered → No layer skipping · controller only delegates · service owns logic · repo only accesses data
- MVC → Thin controller · fat model · no logic in views
- hexagonal → Domain has no infra imports · ports are interfaces · adapters implement ports
- microservices → No cross-service DB calls · communicate via API/events
- CQRS → Commands separate from queries · read/write models independent

**Async/Queue** (if applicable)
- Idempotency key · max_retries + exponential backoff · dead-letter handling
- Status: `pending → running → done/failed`
- FE: loading/error states · polling race conditions · cleanup on unmount

## Hard Rules

- Docs in Vietnamese (UTF-8), code in English
- No direct DB connections to production/staging
- No hardcoded secrets · No `any` type (TS) · No `print()` (Python)
- API contract changes must update docs immediately
