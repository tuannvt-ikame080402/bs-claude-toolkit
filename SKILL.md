---
description: Load project context, detect task type, compute next sprint number, suggest research commands, and output a full action brief before starting any task. Supports solo and split-team modes.
arguments: [scope | task-description]
---

Execute the following phases in order.

---

## PHASE 0 — Config & Stack Cache

### 0a. Read project config
Check `.bs-toolkit.json` at the project root:
- If found → read `team_mode`, `modules`, `shared_docs`, `shared_files`, **`stack_profile`**
- If not found → default `team_mode = "solo"`, no stack_profile

### 0b. Read personal config (override)
Check `.bs-toolkit.local.json` at the project root (gitignored — per-developer):
- If found → read `default_scope`, overrides all scope detection below

### 0c. Resolve final scope

Priority order:
1. `$ARGUMENTS` (if it matches a module name or short alias)
2. `default_scope` from `.bs-toolkit.local.json`
3. No scope (load everything)

If `team_mode = "split"` **and no scope is set** → **stop immediately**, display:
```
⚠️  Split team mode detected. Which module are you working on?

    /bs-claude-toolkit be      → load BE context ([BE_DIR])
    /bs-claude-toolkit fe      → load FE context ([FE_DIR])
    /bs-claude-toolkit all     → load everything (fullstack session)

Tip: Create .bs-toolkit.local.json with {"default_scope": "be"} to skip this prompt.
```

### 0d. Check Stack Profile Cache

This step determines **how many tokens** this run will consume.

**If `stack_profile` exists in `.bs-toolkit.json` with at least `lang_be` or `lang_fe`:**
→ **⚡ FAST PATH** — use cache, **skip Phase 1 entirely**
  - Load directly: `lang_be`, `lang_fe`, `framework_be`, `framework_fe`, `arch`, `async_tech`, `database`, `custom_rules`, `main_flow`, `api_format`
  - Token cost: ~100 tokens (reading a small JSON file)
  - Jump to Phase 2

**If `stack_profile` is missing or empty:**
→ **🔍 FULL PATH** — run all of Phase 1
  - Token cost: ~1500–3000 tokens (reading all CLAUDE.md files)

---

## PHASE 1 — Load Context  *(FULL PATH only)*

### 1a. Root context
- Read `./CLAUDE.md`
- Read `./Agents.md` if it exists

### 1b. Detect and filter submodules

**Solo mode:** Load all submodules found (subdirs with `CLAUDE.md` / `Agents.md` / `docs/`)

**Split mode with scope:** Load only the submodule matching the scope.
- Use mapping from config: `{ "be": "myapp-be" }` → scope "be" → load `myapp-be/`
- If no mapping → fallback to partial directory name match

**Split mode with scope = "all":** Load everything, label each module clearly.

### 1c. Load files from selected submodules
- Read `{subdir}/CLAUDE.md`
- Read `{subdir}/Agents.md` if it exists

### 1d. Auto-detect stack profile

Detect from **two sources**, in priority order:

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
- `pymongo`/`motor`/`mongoengine` → MongoDB
- `sqlalchemy`/`psycopg2`/`asyncpg` → PostgreSQL
- `mysql-connector`/`mysql2`/`pg` → MySQL/PostgreSQL
- `redis`/`ioredis` → Redis

**Architecture detection** (from directory structure):
- Has `controller(s)/` + `service(s)/` + `repositor*/` → `layered`
- Has `models/` + `views/` + `controllers/` → `MVC`
- Has `domain/` + `ports/` + `adapters/` → `hexagonal`
- Has `commands/` + `queries/` → `CQRS`
- Multiple independent service directories → `microservices`

**TypeScript detection**: check `tsconfig.json` or `typescript` in devDependencies.

#### Source 2 — CLAUDE.md / Agents.md (fallback)

If project files are not conclusive, also read:
- "Tech Stack" table
- "Coding Conventions" / "Architecture" sections
- "Worker" / "Queue" sections for async_tech

#### After detection — auto-cache

If at least `lang_be` or `lang_fe` was detected:

1. **Auto-write cache** to `.bs-toolkit.json`:
   - Read `.bs-toolkit.json` (or create it if missing)
   - Add/update the `stack_profile` key with all detected values
   - Write back (preserve existing keys like `team_mode`, `modules`, etc.)

2. **Short notice** in action brief:
   ```
   ✓ Stack detected & cached: [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
                               [arch] · async: [async_tech] · db: [database]
     Future runs will use the cache — no re-detection needed.
   ```

If `.bs-toolkit.json` did not exist → create it with `team_mode: "solo"` and `stack_profile`.

Shared files (from `shared_files` config) — used for conflict warnings.

---

## PHASE 2 — Sprint Intelligence

**Solo mode:** Scan ALL `*/docs/plan/` → find N_max across the project → next sprint = N_max + 1

**Split mode with scope:** Scan only `{scoped-submodule}/docs/plan/`:
- Sprint numbers are **independent per submodule**
- BE on sprint-15, FE on sprint-12 is normal — not a conflict
- Display: "BE next sprint: 16 · FE next sprint: 13" (if scope=all)

**Finding N_max:**
1. List files matching `sprint-{N}-*.md` in scoped dirs
2. Extract the highest N
3. next = N_max + 1 (if no files found → next = 1)
4. Remember the 3 most recent sprints for context

---

## PHASE 3 — Task Analysis

Only runs if a task description is present in `$ARGUMENTS` (the part after scope filtering).

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

### 3c. Conflict check (split mode only)
If the task description or keywords touch:
- Root `CLAUDE.md` or files in `shared_files` config → warn about coordination needed
- API contract → warn that both BE and FE devs must agree before changing

---

## PHASE 4 — Resolve Script Path

Check in order:
1. `./scripts/doc_context.py` exists → `SCRIPT_CMD = "python scripts/"`
2. Not found → `SCRIPT_CMD = "python ~/.claude/skills/bs-claude-toolkit/scripts/"`

---

## PHASE 5 — Output Action Brief

```
╔══════════════════════════════════════════════════════════════╗
  PROJECT BRIEF  [{team_mode} mode{" · scope: "+scope if split}]
╚══════════════════════════════════════════════════════════════╝

  Mode:        [Planning | Execution]
  Scope:       [loaded submodule name, or "all"]
  Stack:       [BE: framework_be/lang_be] · [FE: framework_fe/lang_fe]
               [arch] · async: [async_tech]
  Stack src:   [⚡ cached (.bs-toolkit.json) | 🔍 extracted from project files]
  Next Sprint: [N]  (last: sprint-[N-1]-[name])
               [Split mode: show per-module if scope=all]

──────────────────────────────────────────────────────────────
  OWNERSHIP (split mode only)
──────────────────────────────────────────────────────────────

  ✏️  Your zone:    [scoped-submodule]/
                    → Edit code and docs freely

  🤝  Shared zone:  [shared_files list]
                    → Sync with team before editing

──────────────────────────────────────────────────────────────
  RESEARCH — run before starting
──────────────────────────────────────────────────────────────

  [SCRIPT_CMD]doc_context.py [keywords]
  [SCRIPT_CMD]doc_context.py --scope [module] [keywords]
  [SCRIPT_CMD]code_research.py [keywords]

──────────────────────────────────────────────────────────────
  WORKFLOW  [task-type]
──────────────────────────────────────────────────────────────

  new-feature:
    1. Research (doc + code)
    2. Create [module]/docs/plan/sprint-[N]-[slug].md
    3. Implement following the plan
    4. Self-review code just written (see CODE REVIEW below)
    5. Create [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
    6. Create [module]/docs/test/[DATE]-test-[seq]-[slug].md

  bug-fix:
    1. Research → trace root cause
    2. Fix minimum scope, correct layer
    3. Self-review code just changed (see CODE REVIEW below)
    4. Create [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md

  question / architecture:
    1. Research → analyze → answer
    (no files needed)

──────────────────────────────────────────────────────────────
  CODE REVIEW  (after every implement/fix)
──────────────────────────────────────────────────────────────

  ── Universal (all stacks) ──
  [ ] No hardcoded secrets, credentials, or magic numbers
  [ ] Function/variable names are clear and self-documenting
  [ ] All error paths handled — no silent failures
  [ ] API contract not silently changed → update docs if it is
  [ ] Core application flow not broken

  ── Language: [lang_be] · [lang_fe] ──
  Apply rules for the detected language(s):

  Python     → [ ] No print() · Full type hints · Use f-strings
  TypeScript → [ ] No `any` · No unsafe `!` non-null · strict mode
  Go         → [ ] Check all error returns (no `_`) · No panic() in lib · Context propagation
  Java/Kotlin → [ ] No System.out · Handle checked exceptions · try-with-resources
  PHP        → [ ] No var_dump/dd() · PSR logging · Declare types
  Ruby       → [ ] No puts/p · Clear exception handling · frozen_string_literal
  Node/JS    → [ ] No console.log · No callback hell · Proper async/await

  ── Architecture: [arch_pattern] ──
  Apply rules for the detected pattern:

  layered (controller/service/repo)
    [ ] No layer skipping · Controller only validates and delegates
    [ ] Service owns business logic, does not query DB directly
    [ ] Repository only does data access, no business logic

  MVC
    [ ] Thin controller · Fat model · No logic in views

  hexagonal / ports-and-adapters
    [ ] Domain does not import infra · Ports are interfaces · Adapters implement ports

  microservices
    [ ] No cross-service DB calls · Communicate via API/events · Clear service boundaries

  CQRS
    [ ] Commands separate from Queries · Read/write models are independent

  ── Async/Queue: [async_tech] ──
  Skip if async_tech = "none"

  [ ] Idempotency key present
  [ ] max_retries + exponential backoff
  [ ] Dead-letter / failed status handling
  [ ] Clear status transitions: pending → running → done/failed
  [ ] FE: sufficient loading/error states · Polling race conditions handled · Cleanup on unmount

──────────────────────────────────────────────────────────────
  FILE NAMING  (today: [YYYYMMDD])
──────────────────────────────────────────────────────────────

  Plan:      [module]/docs/plan/sprint-[N]-[slug].md
  Changelog: [module]/docs/changelog/[DATE]-changelog-[seq]-[slug].md
  Test:      [module]/docs/test/[DATE]-test-[seq]-[slug].md

  [seq] = read the directory first, count files with the same date, +1

──────────────────────────────────────────────────────────────
  DEFINITION OF DONE
──────────────────────────────────────────────────────────────

  [ ] Code runs locally
  [ ] Tests pass: happy + edge + failure cases
  [ ] Changelog created in [module]/docs/changelog/
  [ ] Core flow not broken
  [ ] API contract not silently changed
  [ ] No language rule violations ([lang_be]/[lang_fe]) · No hardcoded secrets

══════════════════════════════════════════════════════════════
```

---

## PHASE 6 — Proactive Warnings

- **Missing `.bs-toolkit.json`** → "💡 No config found. Run `install.py --mode solo` or `--mode split` to set up."
- **`stack_profile` empty (FULL PATH ran)** → "💡 Stack auto-cached. Future runs will be faster."
- **Split mode, touching shared_files** → "⚠️ This file is in the shared zone — sync with your team first."
- **Split mode, task touches API contract** → "⚠️ API contract changes require agreement from both BE and FE."
- **Missing `docs/plan/`** in module → "⚠️ No docs/plan/ directory — create it before writing a plan."
- **Task is Execution but default mode is Planning** → ask user to confirm.
- **`stack_profile` may be stale** (CLAUDE.md recently updated significantly) → "💡 If you changed the Tech Stack, run `install.py --setup-stack` to refresh the cache."

---

## Notes

- After printing the brief → **stop and wait for the user** — do not start implementing
- Use the actual system date for `[YYYYMMDD]`
- Split mode: independent sprint numbers per submodule is normal, not a bug
- `.bs-toolkit.local.json` must not be committed to git (must be in `.gitignore`)
