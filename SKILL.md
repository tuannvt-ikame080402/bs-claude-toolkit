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

Before rendering the brief, silently check project health:
1. Find the latest sprint plan in each scoped submodule (`docs/plan/sprint-*.md`)
2. Read it — scan DoD checkboxes (`- [x]` vs `- [ ]`)
3. Check if changelog / test doc / testlog exist for that sprint slug

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
  🏥 PROJECT HEALTH
──────────────────────────────────────────────────────────────

  Active sprint: sprint-[N-1]-[slug]  ([date])
  DoD:  [checked/total] items done
    [ ] [unchecked item 1]
    [ ] [unchecked item 2]

  Deliverables:
    changelog  [✓ exists | ✗ missing]
    test doc   [✓ exists | ✗ missing]
    testlog    [✓ exists | ✗ missing]

  → Next action: [one specific action — e.g. "Run /review be" or "Codex: create changelog"]
  [If all DoD done + all deliverables present]: ✓ Sprint [N-1] complete — ready for sprint [N]

──────────────────────────────────────────────────────────────
  COMMANDS
──────────────────────────────────────────────────────────────

  /bs-claude-toolkit                          → this brief (all scopes)
  /bs-claude-toolkit be                       → brief for BE only
  /bs-claude-toolkit fe                       → brief for FE only

  /bs-claude-toolkit plan [scope] <task>      → research + create sprint plan
  /bs-claude-toolkit plan fix video retry     → plan for a bug fix (all scopes)
  /bs-claude-toolkit plan be add upload api   → plan scoped to BE

  /bs-claude-toolkit review                   → review diff in all submodules
  /bs-claude-toolkit review be                → review BE diff only
  /bs-claude-toolkit review fe                → review FE diff only

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

**Step 1.5 — Impact analysis**

Before writing the plan, identify what else will be affected by this change:

1. From the research output, note the target files/functions/classes/endpoints.
2. Grep for usages of those symbols in files *outside* the target files:
   ```bash
   grep -r "[symbol]" {submodule} --include="*.py" -l   # adjust extension per lang
   ```
3. Build a list: **AFFECTED** = files that call into or depend on the target area.
4. For each affected file, briefly note: why it's affected and whether the change could break it.
5. Assess risk level: **thấp** (no interface change), **trung** (interface change but backward-compatible), **cao** (breaking change to callers).

**Step 2 — Create plan file**

**Slug rule:** derive slug from the task description in `$ARGUMENTS` — take noun/verb keywords, kebab-case, max 5 words, English only.
Examples: `fix video retry not triggering` → `fix-video-retry` · `add upload api for avatars` → `add-upload-avatar-api`
The slug is locked at plan creation. Changelog, test doc, and testlog filenames for this sprint **must use the exact same slug**.

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

## Impact Analysis

| File bị ảnh hưởng | Lý do |
|-------------------|-------|
| `path/to/caller.py` | gọi function X sẽ thay đổi signature |

## Risk Assessment

| Rủi ro | Mức độ | Cách giảm thiểu |
|--------|--------|-----------------|
| [mô tả rủi ro] | thấp / trung / cao | [cách xử lý] |

## Kế hoạch Implement

### Các file cần sửa

| File | Thay đổi |
|------|----------|
| `path/to/file.py` | thay đổi gì và tại sao |

### Các bước

1. [Bước cụ thể]
2. [Bước cụ thể]

## Test Cases

| Case | Input | Expected output |
|------|-------|-----------------|
| Happy path | [input bình thường] | [kết quả đúng] |
| Edge case | [input biên] | [kết quả đúng] |
| Failure case | [input lỗi] | [error/exception đúng] |

## Code Review Checklist

[Dán các checklist item phù hợp với stack + loại task này]

## Definition of Done

- [ ] Code chạy được local
- [ ] Tests pass: happy + edge + failure case
- [ ] Không có regression ở AFFECTED files
- [ ] Changelog tạo xong
- [ ] Test doc + test log tạo xong
- [ ] Flow chính không bị phá
- [ ] Không vi phạm language rules · Không hardcode secrets
```

**Step 3 — Output**

```
✓ Plan created: [submodule]/docs/plan/sprint-[N]-[slug].md

Impact: [N] file(s) affected — [thấp | trung | cao] risk
  [list AFFECTED files if risk is trung/cao]

Next → Codex:
  1. Tag [plan path] in your context
  2. Implement following the plan
  3. Verify no regression in affected files
  4. Create docs/changelog/[YYYYMMDD]-[HHMM]-changelog-[slug].md
  5. Create docs/test/[YYYYMMDD]-[HHMM]-test-[slug].md
  6. Create docs/test/[YYYYMMDD]-[HHMM]-testlog-[slug].md

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
- **Sprint slug** — from filename: `sprint-[N]-[slug].md` → SPRINT_SLUG = `[slug]`
- **Task type** (new-feature / bug-fix / refactor)
- **Files to change** — table from "Các file cần sửa"
- **Implementation steps** — list from "Các bước"
- **Review checklist** — items from "Code Review Checklist" in the plan

If no plan file exists → note "⚠ No sprint plan found — skipping plan compliance check." Set SPRINT_SLUG = "unknown".

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

**Diff size guard:** count total changed lines (all `+` and `-` lines across all submodules).
If total > 500 lines → prepend this warning to the final report:
`⚠ Large diff ([N] lines total) — coverage may be incomplete. Consider re-running per scope: review be / review fe.`
Continue processing regardless.

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

**Step 6 — Regression check**

Build **DEPENDENT_FILES**: files *not* in CHANGED_FILES that import or call into any changed file.

```bash
grep -r "[changed_module_name]" {submodule} --include="*.py" -l   # adjust per lang
```

For each changed function/method/class visible in the diff:
- Extract old signature (from `-` lines) and new signature (from `+` lines)
- Search DEPENDENT_FILES for call sites using the old signature
- For each call site found: assess compatibility with the new signature

| Finding | Action |
|---------|--------|
| Call site is compatible | ✓ no regression |
| Call site passes removed/renamed arg | ✗ regression — flag file:line |
| Call site expects old return shape | ✗ regression — flag file:line |
| Call site not found (unused code) | ⚠ note only |

Limit: check at most 10 dependent files to control token usage. Prioritize files closest in the call chain.

**Step 7 — BE↔FE contract sync**  *(skip if SCOPE ≠ all, or only one submodule present)*

From the **BE diff**, extract:
- New or changed API endpoints: HTTP method + URL pattern + request/response shape
- New or changed events/messages published

From the **FE diff**, extract:
- API calls added or updated (fetch / axios / api client calls): URL + method + payload shape
- Event consumers added or updated

Cross-check:

| Scenario | Check | Flag |
|----------|-------|------|
| BE adds endpoint | FE calls it in diff | ⚠ if no FE call found (may be intentional) |
| BE changes endpoint path/method/params | FE call updated to match | ✗ if FE still calls old contract |
| FE calls endpoint | BE defines it | ✗ if no matching BE route found |
| BE changes response shape | FE destructures/uses that shape | ✗ if FE expects old shape |
| BE publishes event | FE consumer updated | ⚠ if consumer not touched |

Limit: only flag mismatches that are clearly visible in the diff. Do not infer from files outside the diff.

**Step 8 — Verify deliverables (with quality check)**

Check existence using SPRINT_SLUG extracted in Step 1:
```bash
ls {submodule}/docs/changelog/*-changelog-{SPRINT_SLUG}*.md
ls {submodule}/docs/test/*-test-{SPRINT_SLUG}*.md
ls {submodule}/docs/test/*-testlog-{SPRINT_SLUG}*.md
```

If SPRINT_SLUG = "unknown", check for any files created/modified today matching the patterns above.

If a file **exists**, read it and check quality:

**changelog** — must have:
- [ ] Date header or date in filename
- [ ] At least one bullet point describing a real change (not just template text)
- [ ] No placeholder text left (`[mô tả]`, `TODO`, etc.)

**test doc** — must have:
- [ ] At least one test case with input + expected output
- [ ] Happy / edge / failure cases present
- [ ] No placeholder text left

**testlog** — must have:
- [ ] Actual pass/fail results (not just template)
- [ ] Total passed / failed count

| File | Status | Quality |
|------|--------|---------|
| changelog | ✓ / ✗ | ✓ complete / ⚠ stub |
| test doc  | ✓ / ✗ | ✓ complete / ⚠ stub |
| testlog   | ✓ / ✗ | ✓ complete / ⚠ stub |

**Step 9 — Output review report**

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
  🔁 REGRESSION RISK
──────────────────────────────────────────────────────────────

  Dependents checked: [N files]
  ✓  No regression risk found
  ✗  [file:line] — calls [old_signature], now incompatible

──────────────────────────────────────────────────────────────
  🔗 BE↔FE SYNC  (only shown when scope = all)
──────────────────────────────────────────────────────────────

  ✓  All API/event contracts consistent
  ⚠  [BE endpoint] — FE integration not found in diff (may be deferred)
  ✗  [FE call:line] — calls [old path/shape], BE contract changed

──────────────────────────────────────────────────────────────
  📦 DELIVERABLES
──────────────────────────────────────────────────────────────

  changelog  [✓ complete | ⚠ stub | ✗ missing]
  test doc   [✓ complete | ⚠ stub | ✗ missing]
  testlog    [✓ complete | ⚠ stub | ✗ missing]

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
