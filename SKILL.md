---
description: "Three modes: plan (research + create sprint doc), review (read git diff + apply checklist), brief (orientation). Load project context, detect stack, compute next sprint."
arguments: "plan [scope] task | review [scope] | [scope] [task]"
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

## LANGUAGE RULE

**All generated `.md` files must be written in Vietnamese with full diacritical marks (tiếng Việt có dấu, UTF-8)** — plan, changelog, test doc, testlog.
Code identifiers, file paths, and technical terms (API names, library names, error messages) remain in English.

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

Write the entire file in Vietnamese with full diacritical marks (tiếng Việt có dấu). Technical terms (API names, library names, error messages, code identifiers) stay in English.

```markdown
# Sprint [N] — [Tên task]

**Ngày:** [YYYYMMDD]
**Loại:** [new-feature | bug-fix | refactor]
**Phạm vi:** [submodule / các file chính]

## Context

[1–3 câu từ research — sprint liên quan, pattern hiện tại, quyết định đã có]

## Vấn đề / Mục tiêu

[Cần thay đổi gì và tại sao. Bug-fix: cái gì bị lỗi và khi nào. Feature: đang thiếu gì.]

## Phân tích

[Bug-fix: root cause kèm file:line tham chiếu.
 Feature: gap hiện tại, approach được chọn, trade-off.]

## Kế hoạch Implement

### Các file cần sửa

| File | Thay đổi |
|------|----------|
| `path/to/file.py` | thay đổi gì và tại sao |

### Các bước

1. [Bước cụ thể]
2. [Bước cụ thể]

## Code Review Checklist

[Dán các checklist item phù hợp với stack + loại task này]

## Definition of Done

- [ ] Code chạy được local
- [ ] Tests pass: happy + edge + failure case
- [ ] Changelog tạo xong
- [ ] Test doc + test log tạo xong
- [ ] Flow chính không bị phá
- [ ] Không vi phạm language rules · Không hardcode secrets
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

**Step 1 — Load sprint plan context**

Find the latest sprint plan in each scoped submodule:
```bash
ls {submodule}/docs/plan/sprint-*.md   # pick the highest N
```

Read the full plan file. Extract and hold in memory:
- **Task type** (new-feature / bug-fix / refactor)
- **Files to change** — table from "Các file cần sửa"
- **Implementation steps** — list from "Các bước"
- **Review checklist** — items from "Code Review Checklist" in the plan

If no plan file exists → note "⚠ No sprint plan found — skipping plan compliance check."

**Step 2 — Read changes**

Run these commands **inside each scoped submodule directory**, not at the outer repo root.

For each submodule in SCOPE:
```bash
git -C {submodule} log --oneline -10
git -C {submodule} diff main...HEAD --stat
git -C {submodule} diff main...HEAD
```

If `main...HEAD` is empty (working on main directly), fall back to:
```bash
git -C {submodule} diff HEAD~1 --stat
git -C {submodule} diff HEAD~1
```

Read the full diff. Build two lists:
- **CHANGED_FILES** — every file that was modified/added/deleted
- **CHANGED_TESTS** — test files in the diff (pattern: `test_*.py`, `*.test.ts`, `*_test.go`, `spec/**`)

**Step 3 — Load dependency context**

For each file in CHANGED_FILES, scan its import/require statements in the diff. For any imported module that is *also* local (not a third-party package):
- Read that file to understand its interface/contract
- Note if the contract has changed vs what callers expect

Limit: read at most 5 dependency files per submodule to control token usage. Prioritize files that are imported by *multiple* changed files.

**Step 4 — Cross-check plan vs diff**

Compare CHANGED_FILES against the plan's "Các file cần sửa":

| Status | Meaning |
|--------|---------|
| ✓ Implemented | File in plan AND in diff |
| ✗ Missing | File in plan but NOT in diff |
| ⚠ Unplanned | File in diff but NOT in plan |

For each implementation step in the plan, scan the diff for evidence it was done. If a step has no trace in the diff → flag as missing.

**Step 5 — Apply checklist**

Evaluate every item against the actual diff lines. Cite `file:line` for every finding.

**5a. Universal**
- [ ] No hardcoded secrets, credentials, tokens, or magic numbers
- [ ] Clear, self-documenting names — no `tmp`, `data2`, `flag`, `x`
- [ ] All error paths handled — no silent `except: pass`, `catch {}`, ignored errors
- [ ] No dead code added (commented-out blocks, unused imports, unreachable branches)
- [ ] Core application flow not broken

**5b. Security**
- [ ] All user-supplied input validated/sanitized before use
- [ ] No SQL built by string concatenation — use parameterized queries / ORM
- [ ] No XSS — user content escaped before rendering
- [ ] Auth/authz enforced on every new endpoint or mutation
- [ ] No IDOR — ownership checked before returning/modifying resources
- [ ] Sensitive data (PII, tokens) not logged or exposed in responses
- [ ] No unsafe deserialization of untrusted data

**5c. Breaking changes**
- [ ] DB schema changes have a migration file — no silent column/table drops
- [ ] API response shape unchanged; if changed → version bumped or all consumers updated
- [ ] Event/message format unchanged; if changed → backward-compatible or consumers updated
- [ ] Environment variables / config keys not renamed without migration

**5d. Test coverage**
- [ ] Tests added or updated for every changed behavior
- [ ] Happy path covered
- [ ] At least one edge case covered (empty input, zero, max boundary)
- [ ] At least one failure/error case covered
- [ ] Test names describe behavior, not implementation (`test_should_return_404_when_not_found`, not `test_func`)
- [ ] No tests deleted without replacement

**5e. Performance**
- [ ] No N+1 queries — bulk fetch or eager-load where applicable
- [ ] All DB queries have a LIMIT or pagination — no unbounded `SELECT *`
- [ ] Expensive operations not called in a loop
- [ ] Cache invalidated where data changed
- [ ] No blocking I/O on the main/UI thread (FE)

**5f. Language: [lang_be] / [lang_fe]**
```
Python     → No print() · Full type hints · f-strings · no bare except
TypeScript → No `any` · No unsafe `!` · strict mode · no implicit returns
Go         → All errors checked (no `_`) · No panic() in lib code · Context propagated
Java/Kotlin→ No System.out · Checked exceptions · try-with-resources · nullability
PHP        → No var_dump() · PSR logging · Typed properties · no global state
Ruby       → No puts/p · Exception handling · frozen_string_literal: true
Node/JS    → No console.log · Proper async/await · No unhandled promise rejections
```

**5g. Architecture: [arch]**
```
layered      → No layer skipping · Controller only delegates · Service owns logic · Repo = data only
MVC          → Thin controller · Fat model · No business logic in views
hexagonal    → Domain has zero infra imports · Ports are interfaces · Adapters implement ports
microservices→ No direct cross-service DB access · All cross-service calls via API or events
CQRS         → Commands and queries fully separate · Read/write models independent
```

**5h. Async/Queue: [async_tech]**  *(skip if none)*
```
[ ] Idempotency key present on every job
[ ] max_retries set + exponential backoff configured
[ ] Dead-letter queue / failure handler defined
[ ] Job status transitions: pending → running → done/failed (no stuck states)
[ ] FE: loading + error states rendered · polling cleaned up on unmount · no race conditions
```

**5i. Plan checklist items**

Apply every item from the "Code Review Checklist" section of the sprint plan that is not already covered above.

**Step 6 — Verify deliverables**

Check that Codex has created all required docs for the current sprint slug:

```bash
ls {submodule}/docs/changelog/*-changelog-{slug}*.md
ls {submodule}/docs/test/*-test-{slug}*.md
ls {submodule}/docs/test/*-testlog-{slug}*.md
```

| File | Status |
|------|--------|
| changelog | ✓ exists / ✗ missing |
| test doc  | ✓ exists / ✗ missing |
| testlog   | ✓ exists / ✗ missing |

If slug is unknown, check for any files created/modified today matching the patterns above.

**Step 7 — Output review report**

```
╔══════════════════════════════════════════════════════════════╗
  CODE REVIEW  sprint-[N]-[slug]
╚══════════════════════════════════════════════════════════════╝

  Scope:   [submodule(s)]
  Changed: [N files]  ·  [+added / -removed lines]
  Plan:    [submodule]/docs/plan/sprint-[N]-[slug].md

──────────────────────────────────────────────────────────────
  📋 PLAN COMPLIANCE
──────────────────────────────────────────────────────────────

  ✓ / ✗  [file] — implemented / missing
  ⚠       [file] — unplanned change  [brief reason]
  ✗       Step [N]: "[step text]" — no evidence in diff

──────────────────────────────────────────────────────────────
  🔍 CODE QUALITY
──────────────────────────────────────────────────────────────

  ✓  [check] — OK
  ⚠  [check] — [file:line]  [non-blocking issue]
  ✗  [check] — [file:line]  [blocking issue: what to fix]

──────────────────────────────────────────────────────────────
  🔒 SECURITY
──────────────────────────────────────────────────────────────

  ✓ / ⚠ / ✗  [each security check with file:line if flagged]

──────────────────────────────────────────────────────────────
  🧪 TESTS
──────────────────────────────────────────────────────────────

  ✓ / ⚠ / ✗  [each test check]
  Tests changed: [list of test files touched]

──────────────────────────────────────────────────────────────
  📦 DELIVERABLES
──────────────────────────────────────────────────────────────

  changelog  ✓ / ✗
  test doc   ✓ / ✗
  testlog    ✓ / ✗

──────────────────────────────────────────────────────────────
  VERDICT
──────────────────────────────────────────────────────────────

  [If blocking issues (✗)]:
  ✗ [N] blocking issue(s) — return to Codex before merging.
  Priority fixes:
    1. [file:line] — [what to fix]
    2. ...

  [If only warnings (⚠) or all pass]:
  ✓ LGTM — [N] checks passed · [M] warnings (non-blocking).
  [If deliverables missing]: Next → Codex: create missing docs.

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
