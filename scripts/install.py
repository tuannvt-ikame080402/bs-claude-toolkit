#!/usr/bin/env python3
"""
install.py — Cài đặt bs-claude-toolkit cho từng AI coding tool và team mode.

Chạy từ bất kỳ đâu (thường từ toolkit đã clone):
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py [OPTIONS] [target-dir]

Options:
    --tool <name>         claude | cursor | codex | windsurf | scripts | all  (mặc định: all)
    --mode <mode>         solo | split  (mặc định: hỏi interactive)
    --modules <mapping>   Chỉ dùng với --mode split. Ví dụ: be:myapp-be,fe:myapp-fe
    --scope <alias>       Personal default scope (ghi vào .bs-toolkit.local.json)
    --setup-stack         Setup stack profile cache (tiết kiệm ~90% token mỗi lần chạy skill)
    --lang <en|vi>        Ngôn ngữ template (mặc định: en)
    --global              Cài Codex global (~/.codex/AGENTS.md)
    target-dir            Thư mục project (mặc định: CWD)

Ví dụ:
    # Solo dev, tất cả tools
    python install.py --mode solo

    # Split team, tất cả tools
    python install.py --mode split --modules be:myapp-be,fe:myapp-fe

    # Setup stack profile (chạy 1 lần sau khi điền Tech Stack vào CLAUDE.md)
    python install.py --setup-stack

    # Cài personal scope (chạy riêng mỗi người)
    python install.py --scope be

    # Codex global
    python install.py --tool codex --global
"""

import sys, shutil, os, argparse, json
from pathlib import Path

TOOLKIT_ROOT  = Path(__file__).resolve().parent.parent
ADAPTERS_DIR  = TOOLKIT_ROOT / "adapters"
TEMPLATES_DIR = TOOLKIT_ROOT / "templates"
SCRIPTS_DIR   = TOOLKIT_ROOT / "scripts"

SUPPORTED_TOOLS = ["claude", "cursor", "codex", "windsurf", "scripts", "all"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✓  {dst}")


def _write(dst: Path, content: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    print(f"  ✓  {dst}")


def _append_gitignore(target: Path, entry: str) -> None:
    gi = target / ".gitignore"
    lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    if entry not in lines:
        with gi.open("a", encoding="utf-8") as f:
            f.write(f"\n{entry}\n")
        print(f"  ✓  .gitignore ← {entry}")


def _parse_modules(raw: str) -> dict[str, str]:
    """Parse 'be:myapp-be,fe:myapp-fe' → {'be': 'myapp-be', 'fe': 'myapp-fe'}"""
    result = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if ":" not in pair:
            continue
        alias, dirname = pair.split(":", 1)
        result[alias.strip()] = dirname.strip()
    return result


# ── Config generators ─────────────────────────────────────────────────────────

def generate_project_config(target: Path, *, mode: str, modules: dict[str, str]) -> None:
    """Tạo .bs-toolkit.json (commit vào git)."""
    print("\n[config]")
    dst = target / ".bs-toolkit.json"
    if dst.exists():
        print(f"  .bs-toolkit.json đã tồn tại — bỏ qua.")
        return

    if mode == "split":
        config = {
            "_comment": "bs-claude-toolkit project config. Commit this file.",
            "team_mode": "split",
            "modules": modules,
            "shared_docs": "docs",
            "shared_files": ["CLAUDE.md", "docs/api-contract.md"],
            "stack_profile": {},
        }
    else:
        config = {
            "_comment": "bs-claude-toolkit project config. Commit this file.",
            "team_mode": "solo",
            "modules": {},
            "shared_docs": None,
            "stack_profile": {},
        }

    _write(dst, json.dumps(config, indent=2, ensure_ascii=False) + "\n")

    # Tạo .bs-toolkit.local.json.example
    example = {
        "_comment": "Personal scope — copy to .bs-toolkit.local.json, DO NOT commit.",
        "default_scope": list(modules.keys())[0] if modules else "be",
    }
    _write(
        target / ".bs-toolkit.local.json.example",
        json.dumps(example, indent=2, ensure_ascii=False) + "\n",
    )
    _append_gitignore(target, ".bs-toolkit.local.json")

    print(f"\n  💡 Sau khi điền Tech Stack vào CLAUDE.md, chạy:")
    print(f"       python install.py --setup-stack")
    print(f"     để cache stack profile → /bs-claude-toolkit sẽ tiết kiệm ~90% token.")

    if mode == "split":
        print(f"\n  QUAN TRỌNG — mỗi dev chạy lệnh sau để set personal scope:")
        print(f"    python install.py --scope be   (dev BE)")
        print(f"    python install.py --scope fe   (dev FE)")


def generate_personal_scope(target: Path, *, scope: str) -> None:
    """Tạo .bs-toolkit.local.json (gitignored) cho developer hiện tại."""
    print("\n[personal scope]")
    dst = target / ".bs-toolkit.local.json"
    config = {
        "_comment": "Personal scope config — DO NOT commit (gitignored).",
        "default_scope": scope,
    }
    _write(dst, json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    _append_gitignore(target, ".bs-toolkit.local.json")
    print(f"  Từ nay /bs-claude-toolkit sẽ tự load scope '{scope}'.")


# ── Submodule setup ───────────────────────────────────────────────────────────

def setup_submodule_docs(target: Path, modules: dict[str, str]) -> None:
    """Tạo cấu trúc docs/ cho từng submodule trong split mode."""
    print("\n[submodule docs structure]")
    for alias, dirname in modules.items():
        subdir = target / dirname
        if not subdir.exists():
            print(f"  ⚠️  {dirname}/ không tồn tại — bỏ qua.")
            continue
        for doc_type in ("plan", "changelog", "test"):
            d = subdir / "docs" / doc_type
            d.mkdir(parents=True, exist_ok=True)
            gitkeep = d / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
            print(f"  ✓  {dirname}/docs/{doc_type}/")


# ── Per-tool installers ───────────────────────────────────────────────────────

def install_scripts(target: Path) -> None:
    print("\n[scripts]")
    for script in ["doc_context.py", "code_research.py"]:
        _copy(SCRIPTS_DIR / script, target / "scripts" / script)
    print(f"  Usage: python scripts/doc_context.py <keyword>")
    print(f"         python scripts/doc_context.py --scope be <keyword>")


def _lang_suffix(lang: str) -> str:
    return ".vi" if lang == "vi" else ""


def install_cursor(target: Path, *, lang: str = "en") -> None:
    print("\n[cursor]")
    src_name = f"cursor{_lang_suffix(lang)}.mdc"
    dst = target / ".cursor" / "rules" / "bs-claude-toolkit.mdc"
    _copy(ADAPTERS_DIR / src_name, dst)
    print(f"  Rule tự apply cho mọi session trong project này.")


def install_codex(target: Path, *, global_install: bool = False, lang: str = "en") -> None:
    print("\n[codex]")
    src_name = f"AGENTS{_lang_suffix(lang)}.md"
    if global_install:
        dst = Path.home() / ".codex" / "AGENTS.md"
        _copy(TEMPLATES_DIR / src_name, dst)
        print(f"  Global AGENTS.md installed → áp dụng mọi project.")
    else:
        dst = target / "AGENTS.md"
        if dst.exists():
            print(f"  AGENTS.md đã tồn tại — bỏ qua. Xóa file để ghi đè.")
        else:
            _copy(TEMPLATES_DIR / src_name, dst)
            print(f"  Chỉnh sửa [BE_DIR] và [FE_DIR] trong file vừa tạo.")


def install_windsurf(target: Path, *, lang: str = "en") -> None:
    print("\n[windsurf]")
    src_name = f"windsurf{_lang_suffix(lang)}.md"
    dst = target / ".windsurf" / "rules" / "bs-claude-toolkit.md"
    _copy(ADAPTERS_DIR / src_name, dst)


def install_claude(target: Path, *, lang: str = "en") -> None:
    print("\n[claude]")
    skill_path = Path.home() / ".claude" / "skills" / "bs-claude-toolkit"
    if TOOLKIT_ROOT == skill_path and (TOOLKIT_ROOT / "SKILL.md").exists():
        print(f"  ✓  Skill cài tại {TOOLKIT_ROOT}")
        print(f"  Dùng: /bs-claude-toolkit trong Claude Code")
    else:
        print(f"  Chưa cài global skill. Chạy:")
        print(f"    git clone https://github.com/tuannguyen-mk1/bs-claude-toolkit.git {skill_path}")

    src_name = f"CLAUDE{_lang_suffix(lang)}.md"
    claude_dst = target / "CLAUDE.md"
    if not claude_dst.exists():
        _copy(TEMPLATES_DIR / src_name, claude_dst)
        print(f"  CLAUDE.md template tạo xong. Chỉnh sửa [BE_DIR] và [FE_DIR].")
    else:
        print(f"  CLAUDE.md đã tồn tại — bỏ qua.")


# ── Stack Profile Cache ───────────────────────────────────────────────────────

_LANGS = [
    ("1", "Python"), ("2", "TypeScript"), ("3", "JavaScript/Node"),
    ("4", "Go"), ("5", "Java"), ("6", "Kotlin"), ("7", "PHP"),
    ("8", "Ruby"), ("9", "Dart"), ("10", "Rust"), ("11", "C#"), ("0", "none / không có"),
]

_FW_SUGGESTIONS: dict[str, list[str]] = {
    "Python":            ["Flask", "FastAPI", "Django"],
    "TypeScript":        ["Next.js", "NestJS", "Remix", "Hono"],
    "JavaScript/Node":   ["Express", "Fastify", "Koa"],
    "Go":                ["Gin", "Echo", "Fiber", "Chi"],
    "Java":              ["Spring Boot", "Quarkus", "Micronaut"],
    "Kotlin":            ["Spring Boot", "Ktor"],
    "PHP":               ["Laravel", "Symfony", "Lumen"],
    "Ruby":              ["Rails", "Sinatra"],
    "Dart":              ["Flutter"],
    "Rust":              ["Axum", "Actix-web"],
    "C#":                ["ASP.NET Core"],
}

_ARCHS = [
    ("1", "layered (controller/service/repository)"),
    ("2", "MVC"),
    ("3", "hexagonal (ports & adapters)"),
    ("4", "microservices"),
    ("5", "CQRS"),
    ("6", "other"),
]

_ASYNC_TECHS = [
    ("1", "none"), ("2", "Celery"), ("3", "BullMQ"), ("4", "Sidekiq"),
    ("5", "Kafka"), ("6", "RQ"), ("7", "Temporal"), ("8", "other"),
]


def _pick(prompt: str, options: list[tuple[str, str]], default_key: str = "1") -> str:
    for key, label in options:
        marker = " ←" if key == default_key else ""
        print(f"  [{key}] {label}{marker}")
    raw = input(f"\n{prompt} (mặc định {default_key}): ").strip() or default_key
    mapping = {k: v for k, v in options}
    return mapping.get(raw, mapping.get(default_key, ""))


def _ask_framework(lang: str, role: str) -> str:
    suggestions = _FW_SUGGESTIONS.get(lang, [])
    hint = ", ".join(suggestions) if suggestions else "e.g. Express, Spring Boot, ..."
    return input(f"  {role} framework [{hint}]: ").strip() or (suggestions[0] if suggestions else "")


def setup_stack_profile(target: Path) -> None:
    """
    Setup stack profile cache — lưu vào .bs-toolkit.json.
    Chạy 1 lần, skill sẽ dùng cache này → skip đọc CLAUDE.md → ~90% token savings.
    """
    print("\n[stack profile cache]")
    print("Setup 1 lần. Skill sẽ dùng cache này thay vì đọc CLAUDE.md mỗi lần.\n")

    # Load existing config
    cfg_path = target / ".bs-toolkit.json"
    config: dict = {}
    if cfg_path.exists():
        try:
            config = json.loads(cfg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    existing = config.get("stack_profile", {})
    if existing:
        print("  Stack profile hiện tại:")
        for k, v in existing.items():
            if k != "custom_rules":
                print(f"    {k}: {v}")
        overwrite = input("\n  Ghi đè? (y/N): ").strip().lower()
        if overwrite != "y":
            print("  Giữ nguyên stack profile.")
            return

    print("\n── Backend ─────────────────────────────────────────")
    lang_be = _pick("BE language", _LANGS, "1")
    fw_be = _ask_framework(lang_be, "BE") if lang_be != "none / không có" else ""

    print("\n── Frontend ────────────────────────────────────────")
    lang_fe = _pick("FE language", _LANGS, "2")
    fw_fe = _ask_framework(lang_fe, "FE") if lang_fe != "none / không có" else ""

    print("\n── Architecture ────────────────────────────────────")
    arch_raw = _pick("Architecture pattern", _ARCHS, "1")
    arch = arch_raw.split(" ")[0]  # lấy phần đầu trước dấu cách

    print("\n── Async / Queue ────────────────────────────────────")
    async_tech = _pick("Async/Queue tech", _ASYNC_TECHS, "1")

    database = input("\n  Database (e.g. PostgreSQL, MongoDB, MySQL — để trống nếu không rõ): ").strip()

    print("\n── Custom Rules (optional) ──────────────────────────")
    print("  Nhập các rule đặc thù của project (Enter để bỏ qua từng dòng, dòng trống để kết thúc):")
    custom_rules: list[str] = []
    while True:
        rule = input("  + ").strip()
        if not rule:
            break
        custom_rules.append(rule)

    main_flow = input("\n  Main flow của app (e.g. 'Login → Dashboard → Orders'): ").strip()
    api_format = input("  API response format (mặc định: { success, data, error, meta }): ").strip() \
                 or "{ success, data, error, meta }"

    profile: dict = {
        "lang_be": lang_be if lang_be != "none / không có" else "",
        "framework_be": fw_be,
        "lang_fe": lang_fe if lang_fe != "none / không có" else "",
        "framework_fe": fw_fe,
        "arch": arch,
        "async_tech": async_tech,
        "database": database,
        "main_flow": main_flow,
        "api_format": api_format,
    }
    if custom_rules:
        profile["custom_rules"] = custom_rules

    # Strip empty strings
    profile = {k: v for k, v in profile.items() if v or k == "custom_rules"}

    config["stack_profile"] = profile
    _write(cfg_path, json.dumps(config, indent=2, ensure_ascii=False) + "\n")

    print("\n  ✓  Stack profile saved → .bs-toolkit.json")
    print("  Từ nay /bs-claude-toolkit sẽ dùng cache này — không đọc lại CLAUDE.md.")
    print("  Để refresh: python install.py --setup-stack (chọn 'y' khi hỏi ghi đè).\n")


# ── Interactive setup ─────────────────────────────────────────────────────────

def _ask_mode() -> str:
    print("\nTeam setup:")
    print("  [1] solo   — 1 người code cả BE + FE")
    print("  [2] split  — 2 người code riêng BE và FE")
    choice = input("\nChọn (1/2, mặc định 1): ").strip() or "1"
    return "split" if choice == "2" else "solo"


def _ask_modules() -> dict[str, str]:
    print("\nNhập tên thư mục cho từng module (ví dụ: myapp-be, backend, api):")
    be = input("  BE directory name (mặc định: backend): ").strip() or "backend"
    fe = input("  FE directory name (mặc định: frontend): ").strip() or "frontend"
    return {"be": be, "fe": fe}


# ── Main ──────────────────────────────────────────────────────────────────────

def _parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tool",        default="all",  choices=SUPPORTED_TOOLS)
    p.add_argument("--mode",        default=None,   choices=["solo", "split"])
    p.add_argument("--modules",     default=None,   help="be:myapp-be,fe:myapp-fe")
    p.add_argument("--scope",       default=None,   help="Personal default scope")
    p.add_argument("--setup-stack", dest="setup_stack", action="store_true",
                                    help="Setup stack profile cache (tiết kiệm ~90% token)")
    p.add_argument("--lang",        default="en",   choices=["en", "vi"], help="Template language (default: en)")
    p.add_argument("--global",      dest="global_install", action="store_true")
    p.add_argument("target",        nargs="?",      default=None)
    return p.parse_args()


def main() -> None:
    args = _parse_args()

    target = Path(args.target).resolve() if args.target else Path(os.getcwd()).resolve()
    if not target.exists():
        print(f"Error: directory not found: {target}")
        sys.exit(1)

    print(f"\nInstalling bs-claude-toolkit → {target}")

    # Stack profile cache setup (standalone)
    if args.setup_stack:
        setup_stack_profile(target)
        print("Done.\n")
        return

    # Personal scope only
    if args.scope:
        generate_personal_scope(target, scope=args.scope)
        print("\nDone.\n")
        return

    # Determine mode
    mode = args.mode
    modules: dict[str, str] = {}

    if mode == "split":
        modules = _parse_modules(args.modules) if args.modules else _ask_modules()
    elif mode is None:
        mode = _ask_mode()
        if mode == "split":
            modules = _parse_modules(args.modules) if args.modules else _ask_modules()

    # Generate config files
    generate_project_config(target, mode=mode, modules=modules)
    if mode == "split":
        setup_submodule_docs(target, modules)

    # Install tools
    tool = args.tool
    lang = args.lang
    if tool == "all":
        install_scripts(target)
        install_claude(target, lang=lang)
        install_cursor(target, lang=lang)
        install_codex(target, global_install=args.global_install, lang=lang)
        install_windsurf(target, lang=lang)
    elif tool == "scripts":  install_scripts(target)
    elif tool == "claude":   install_claude(target, lang=lang)
    elif tool == "cursor":   install_cursor(target, lang=lang)
    elif tool == "codex":    install_codex(target, global_install=args.global_install, lang=lang)
    elif tool == "windsurf": install_windsurf(target, lang=lang)

    print(f"\nDone.\n")


if __name__ == "__main__":
    main()
