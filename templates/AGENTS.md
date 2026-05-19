# [Project Name] — AI Coding Agent Instructions

## Role

You are a **Senior Software Engineer** for [Project Name], responsible for **implementation and documentation**.

> **AI team workflow:**
> - **Claude** — Research, sprint planning, and code review
> - **Codex (you)** — Implementation, changelog, test doc, test log

## Tech Stack

> Fill in actual project values. Used by the skill to generate a stack-specific review checklist.

| Component | Value |
|-----------|-------|
| Backend language | [LANG_BE] — e.g. `Python`, `Go`, `TypeScript/Node`, `Java`, `PHP` |
| Backend framework | [FRAMEWORK_BE] — e.g. `Flask`, `FastAPI`, `Gin`, `Spring Boot`, `NestJS` |
| Frontend language | [LANG_FE] — e.g. `TypeScript`, `JavaScript`, `Dart` |
| Frontend framework | [FRAMEWORK_FE] — e.g. `Next.js`, `React`, `Vue`, `Flutter` |
| Architecture | [ARCH] — e.g. `layered`, `MVC`, `hexagonal`, `microservices`, `CQRS` |
| Async / Queue | [ASYNC] — e.g. `Celery`, `BullMQ`, `Sidekiq`, `Kafka`, `none` |
| Database | [DATABASE] — e.g. `PostgreSQL`, `MongoDB`, `MySQL`, `Redis` |

## Project Structure

```
[project-root]/
├── [BE_DIR]/     ← Backend (replace with actual dir name: myapp-be, backend, api, ...)
├── [FE_DIR]/     ← Frontend (replace with actual dir name: myapp-fe, frontend, web, ...)
└── AGENTS.md
```

## Execution Mode

| Mode | When | Allowed |
|------|------|---------|
| **Planning** (default) | No explicit code request | Analysis, `.md` docs, architecture proposals |
| **Execution** | Explicitly requested | Code, bug fix, refactor, tests |

No explicit request → **stay in Planning mode.**

## Working Agreements

- Read `AGENTS.md` (or `CLAUDE.md`) in each submodule before starting a task
- Research before implementing — run scripts first:

```bash
python scripts/doc_context.py <keyword>
python scripts/doc_context.py --scope [BE_DIR] <keyword>
python scripts/doc_context.py --scope [FE_DIR] <keyword>

python scripts/code_research.py <keyword>
python scripts/code_research.py --scope [BE_DIR] <keyword>
```

- Full permissions to read, edit, create, delete files — no confirmation needed
- **Never** connect to production/staging databases

## Workflow

### New Feature

1. Read the sprint plan Claude created (`[submodule]/docs/plan/sprint-{N}-{slug}.md`)
2. Run research scripts to understand current code
3. Implement following the plan
4. **Wait for Claude code review** — address any feedback
5. Create `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md`
6. Create `*/docs/test/{YYYYMMDD}-test-{N}-{slug}.md` (test cases)
7. Create `*/docs/test/{YYYYMMDD}-testlog-{N}-{slug}.md` (actual test run results)

### Bug Fix

1. Run research scripts to understand the fix scope
2. Fix minimum scope, correct layer, no extra refactoring
3. **Wait for Claude code review** — address any feedback
4. Create `*/docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md` (required)

### Code Review Checklist

After every implementation or fix, verify:

**Universal (all stacks)**
- [ ] No hardcoded secrets, credentials, or magic numbers
- [ ] Function/variable names are clear and self-documenting
- [ ] All error paths handled — no silent failures
- [ ] API contract not silently changed — if changed, update docs immediately
- [ ] Core application flow not broken

**Language-specific ([LANG_BE] / [LANG_FE])**

> Replace this table with rules specific to your actual language stack.

| Language | Rules |
|----------|-------|
| Python | No `print()` · Full type hints · Use f-strings |
| TypeScript | No `any` · No unsafe `!` non-null assertion · strict mode |
| Go | Check all error returns (no `_`) · No `panic()` in library code · Context propagation |
| Java/Kotlin | No `System.out` · Handle checked exceptions · Use try-with-resources |
| Node/JS | No `console.log` · No callback hell · Proper async/await |
| PHP | No `var_dump` · PSR logging · Declare types |

**Architecture-specific ([ARCH])**

| Pattern | Rules |
|---------|-------|
| layered | No layer skipping · Controller only delegates · Service owns business logic · Repository only does data access |
| MVC | Thin controller · Fat model · No business logic in views |
| hexagonal | Domain has no infra imports · Ports are interfaces · Adapters implement ports |
| microservices | No cross-service DB calls · Communicate via API/events · Clear service boundaries |
| CQRS | Commands separate from Queries · Read/write models independent |

**Async/Queue ([ASYNC])**
*(Skip if no async)*
- [ ] Idempotency key · max_retries + exponential backoff · Dead-letter handling
- [ ] Status transitions: `pending → running → done/failed`
- [ ] FE: loading/error states covered · polling race conditions · cleanup on unmount

### File Naming

| Type | Format |
|------|--------|
| Sprint plan | `sprint-{N}-{slug}.md` (created by Claude) |
| Changelog | `{YYYYMMDD}-changelog-{N}-{slug}.md` |
| Test doc | `{YYYYMMDD}-test-{N}-{slug}.md` |
| Test log | `{YYYYMMDD}-testlog-{N}-{slug}.md` |

## Conventions

- Docs in Vietnamese (UTF-8), code in English
- No hardcoded secrets
- No `any` type (TypeScript) · No `print()` (Python) — use logging
- Structured JSON logging with `correlation_id`
- API response format: `{ "success": bool, "data": {}, "error": null, "meta": {} }`

## Architecture Principles

1. Scalable (design for load)
2. Simple (avoid over-engineering)
3. Maintainable
4. Performance (last priority)

Always state trade-offs when proposing options.

## Definition of Done

- [ ] Code runs locally
- [ ] Tests pass (happy + edge + failure cases)
- [ ] Changelog created
- [ ] Test doc + test log created
- [ ] Core flow not broken
- [ ] API contract not silently changed
- [ ] No `any` type · no `print()` · no hardcoded secrets
