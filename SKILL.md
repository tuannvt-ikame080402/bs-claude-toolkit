---
description: Three modes — plan (research + create sprint doc), review (read git diff + apply checklist), brief (orientation). Load project context, detect stack, compute next sprint.
arguments: [plan [scope] task | review [scope] | [scope] [task]]
---

## Sub-commands

| Command | Who | What it does |
|---------|-----|--------------|
| `/bs-claude-toolkit plan [scope] task` | Claude | Research → create `sprint-N-slug.md` → stop |
| `/bs-claude-toolkit review [scope]` | Claude | Read git diff → apply checklist → output findings |
| `/bs-claude-toolkit [scope]` | Claude | Orientation brief only — no files, no scripts |

**Team split:**
- **Claude** → `plan` + `review`
- **Codex** → implement + changelog + test doc + testlog + run tests

---

## PHASE 0 — Config & Stack Cache

### 0a. Read project config
Check `.bs-toolkit.json` at the project root:
- If found → read `modules` (optional name mapping), `shared_files`, `stack_profile`
- If not found → continue with defaults

### 0b. Check Stack Profile Cache

**If `stack_profile` exists with at least `lang_be` or `lang_fe`:**
→ **⚡ FAST PATH** — use cache, skip Phase 1 entirely
  - Load: `lang_be`, `lang_fe`, `framework_be`, `framework_fe`, `arch`, `async_tech`, `database`, `custom_rules`, `main_flow`, `api_format`
  - Token cost: ~100 tokens

**If `stack_profile` is missing or empty:**
→ **🔍 FULL PATH** — run all of Phase 1
  - Token cost: ~1500–3000 tokens

### 0c. Parse sub-command and scope

First word of `$ARGUMENTS`:
- `plan`   → MODE = plan   · remaining words = `[scope?] task description`
- `review` → MODE = review · remaining word = `[scope?]`
- else     → MODE = brief  · all words = `[scope?] [task?]`

Scope resolution: if the first non-command word matches a known submodule name or alias in `.bs-toolkit.json` → set SCOPE to that submodule; otherwise SCOPE = all.

---

## PHASE 1 — Load Context  *(FULL PATH only)*

### 1a. Root context
- Read `./CLAUDE.md`
- Read `./Agents.md` if it exists

### 1b. Detect submodules

Find all immediate subdirectories that contain `CLAUDE.md`, `Agents.md`, or a `docs/` folder.

If `.bs-toolkit.json` has a `modules` mapping (e.g. `{"be": "myapp-be"}`), use it to resolve non-standard names. Otherwise rely on content-based detection.

Apply SCOPE filter.

### 1c. Load submodule files
- Read `{subdir}/CLAUDE.md`
- Read `{subdir}/Agents.md` if it exists

### 1d. Auto-detect stack profile

#### Source 1 — Project files (most accurate)

Scan files in each submodule root:

| File | Language | Framework hints |
|------|----------|-----------------|
| `requirements.txt` / `pyproject.toml` / `Pipfile` | Python | flask→Flask · fastapi→FastAPI · django→Django · celery→async:Celery · rq→async:RQ |
| `package.json` | TypeScript/JS | next→Next.js · nuxt→Nuxt · react→React · vue→Vue · @angular→Angular · @nestjs→NestJS · express→Express · bull/bullmq→async:BullMQ |
| `go.mod` | Go | gin-gonic→Gin · labstack/echo→Echo · gofiber→Fiber |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | Java/Kotlin | spring-boot→Spring Boot · quarkus→Quarkus |
| `composer.json` | PHP | laravel/framework→Laravel · symfony→Symfony |
| `Gemfile` | Ruby | rails→Rails |
| `pubspec.yaml` | Dart | flutter→Flutter |
| `Cargo.toml` | Rust | axum→Axum · actix-web→Actix |
| `*.csproj` / `*.sln` | C# | Microsoft.AspNetCore→ASP.NET Core |

**Database detection** (from deps):
`pymongo`/`motor` → MongoDB · `sqlalchemy`/`psycopg2` → PostgreSQL · `mysql2`/`pg` → MySQL · `redis`/`ioredis` → Redis

**Architecture detection** (from directory structure):
- `controller(s)/` + `service(s)/` + `repositor*/` → `layered`
- `models/` + `views/` + `controllers/` → `MVC`
- `domain/` + `ports/` + `adapters/` → `hexagonal`
- `commands/` + `queries/` → `CQRS`
- Multiple independent service directories → `microservices`

**TypeScript detection**: `tsconfig.json` or `typescript` in devDependencies.

#### Source 2 — CLAUDE.md / Agents.md (fallback)

Read "Tech Stack", "Coding Conventions", "Architecture", "Worker" / "Queue" sections.

#### After detection — auto-cache

If at least `lang_be` or `lang_fe` was detected:
- Read `.bs-toolkit.json` (or create it)
- Add/update `stack_profile` with detected values, preserve other keys
- Write back

---

## PHASE 2 — Sprint Intelligence

Scan `*/docs/plan/` in the scoped submodule(s):
1. List files matching `sprint-{N}-*.md`
2. Extract the highest N
3. next = N_max + 1 (no files → next = 1)
4. Remember the 3 most recent sprints for context

---

## PHASE 3 — Task Analysis  *(plan + brief modes only)*

### 3a. Classify task type
| Type | Keywords |
|------|---------|
| **new-feature** | implement, add, create, build |
| **bug-fix** | fix, bug, broken, not working, error |
| **refactor** | refactor, optimize, clean, restructure |
| **question** | why, how, explain, what is, mechanism |
| **architecture** | design, plan, architecture, approach, strategy |

### 3b. Extract research keywords
Take noun/domain keywords, drop stop words.
Example: "fix video retry not triggering" → `video`, `retry`, `trigger`

---

## PHASE 4 — Resolve Script Path

1. `./scripts/doc_context.py` exists → `SCRIPT_CMD = "python scripts/"`
2. Not found → `SCRIPT_CMD = "python ~/.claude/skills/bs-claude-toolkit/scripts/"`

---

## PHASE 5 — Execute by Mode

---

### MODE: brief  *(orientation only — no files created, no scripts run)*

```
╔══════════════════════════════════════════════════════════════╗
  PROJECT BRIEF  [scope: all | submodule-name]
╚══════════════════════════════════════════════════════════════╝

  Scope:       [loaded submodule(s)]
  Stack:       [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
               [arch] · async: [async_tech] · db: [database]
  Stack src:   [⚡ cached | 🔍 detected from project files]
  Next Sprint: [N]  (last: sprint-[N-1]-[name])

──────────────────────────────────────────────────────────────
  WORKFLOW
──────────────────────────────────────────────────────────────

  1. Claude:  /bs-claude-toolkit plan [scope] [task]
              → researches + creates sprint-[N]-slug.md

  2. Codex:   tag plan → implement → changelog + test docs + run tests

  3. Claude:  /bs-claude-toolkit review [scope]
              → reviews Codex's git diff against checklist

══════════════════════════════════════════════════════════════
```

---

### MODE: plan  *(Claude researches + creates sprint plan doc)*

**Step 1 — Research**

Run both scripts and read their full output before writing anything:

```bash
[SCRIPT_CMD]doc_context.py [--scope SCOPE] [keywords]
[SCRIPT_CMD]code_research.py [--scope SCOPE] [keywords]
```

Internalize: relevant past decisions from plan history, existing code patterns and file paths, root cause (if bug-fix) or current gap (if feature).

**Step 2 — Create plan file**

Write to: `[submodule]/docs/plan/sprint-[N]-[slug].md`

```markdown
# Sprint [N] — [Task Title]

**Date:** [YYYYMMDD]
**Type:** [new-feature | bug-fix | refactor]
**Scope:** [submodule / key files]

## Context

[1–3 sentences from research — relevant past sprints, existing patterns, related decisions]

## Problem / Goal

[What needs to change and why. For bug-fix: what breaks and when. For feature: what is missing.]

## Analysis

[For bug-fix: root cause with file:line references.
 For feature: current gap, chosen approach, trade-offs.]

## Implementation Plan

### Files to modify

| File | Change |
|------|--------|
| `path/to/file.py` | what changes and why |

### Steps

1. [Concrete step]
2. [Concrete step]

## Code Review Checklist

[Paste the relevant checklist items for this task's stack + type]

## Definition of Done

- [ ] Code runs locally
- [ ] Tests pass: happy + edge + failure cases
- [ ] Changelog created
- [ ] Test doc + test log created
- [ ] Core flow not broken
- [ ] No language rule violations · No hardcoded secrets
```

**Step 3 — Output**

```
✓ Plan created: [submodule]/docs/plan/sprint-[N]-[slug].md

Next → Codex:
  1. Tag [plan path] in your context
  2. Implement following the plan
  3. Create docs/changelog/[YYYYMMDD]-[HHMM]-changelog-[slug].md
  4. Create docs/test/[YYYYMMDD]-[HHMM]-test-[slug].md
  5. Create docs/test/[YYYYMMDD]-[HHMM]-testlog-[slug].md

When Codex is done → Claude: /bs-claude-toolkit review [scope]
```

---

### MODE: review  *(Claude reads git diff + applies checklist)*

**Step 1 — Read changes**

```bash
git log --oneline -10
git diff main...HEAD --stat
git diff main...HEAD
```

If `main...HEAD` is empty (working on main directly), fall back to:
```bash
git diff HEAD~1 --stat
git diff HEAD~1
```

Read the full diff. Note every changed file and what changed.

**Step 2 — Apply checklist to the actual diff**

For each changed file, evaluate:

**Universal**
- [ ] No hardcoded secrets, credentials, or magic numbers
- [ ] Clear, self-documenting names
- [ ] All error paths handled — no silent failures
- [ ] API contract not silently changed
- [ ] Core application flow not broken

**Language: [lang_be] / [lang_fe]**
```
Python     → No print() · Full type hints · f-strings
TypeScript → No `any` · No unsafe `!` · strict mode
Go         → Check all errors (no `_`) · No panic() in lib · Context propagation
Java/Kotlin→ No System.out · Checked exceptions · try-with-resources
PHP        → No var_dump() · PSR logging · Declare types
Ruby       → No puts/p · Exception handling · frozen_string_literal
Node/JS    → No console.log · Proper async/await
```

**Architecture: [arch]**
```
layered      → No layer skipping · Controller delegates · Service owns logic · Repo = data only
MVC          → Thin controller · Fat model · No logic in views
hexagonal    → Domain ≠ infra imports · Ports = interfaces · Adapters implement ports
microservices→ No cross-service DB calls · Communicate via API/events
CQRS         → Commands ≠ Queries · Read/write models independent
```

**Async/Queue: [async_tech]**  *(skip if none)*
```
[ ] Idempotency key · max_retries + exponential backoff · Dead-letter handling
[ ] Status: pending → running → done/failed
[ ] FE: loading/error states · Polling race conditions · Cleanup on unmount
```

**Step 3 — Output review report**

```
╔══════════════════════════════════════════════════════════════╗
  CODE REVIEW  sprint-[N]-[slug]
╚══════════════════════════════════════════════════════════════╝

  Changed: [N files]  ·  [+added / -removed lines]

  ✓  [checklist item] — OK
  ⚠  [checklist item] — [file:line]  [description]
  ✗  [checklist item] — [file:line]  [blocking issue]

──────────────────────────────────────────────────────────────

  [If all pass]:
  LGTM — [N] checks passed.
  Next → Codex: create changelog + test docs if not done yet.

  [If issues found]:
  [N] issue(s) found — return to Codex to fix before documenting.
  [Each issue: file:line + what to fix]

══════════════════════════════════════════════════════════════
```

---

## PHASE 6 — Proactive Warnings

- **Missing `.bs-toolkit.json`** → auto-created with `stack_profile` after first detection
- **`stack_profile` may be stale** → "💡 Stack changed recently? Run `install.py --setup-stack` to refresh."
- **Task touches `shared_files`** → "⚠️ This file is shared — coordinate with teammates before editing."
- **Task touches API contract** → "⚠️ API contract change — update docs and notify all consumers."
- **Missing `docs/plan/`** in submodule → "⚠️ Create docs/plan/ before running plan mode."

---

## Notes

- `plan` mode → **creates a file and stops**. Never start implementing.
- `review` mode → **outputs findings only**. Never fix code — that is Codex's job.
- `brief` mode → **outputs the brief and stops**. No files, no scripts.
- Use the actual system date for `[YYYYMMDD]`
- `.bs-toolkit.json` should be committed; it is shared config for the whole team
