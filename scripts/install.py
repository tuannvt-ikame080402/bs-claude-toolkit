#!/usr/bin/env python3
"""
install.py — Cài đặt bs-claude-toolkit cho từng AI coding tool.

Chạy từ bất kỳ đâu (thường từ toolkit đã clone):
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py [OPTIONS] [target-dir]

Options:
    --tool <name>     Tool cần cài: claude | cursor | codex | windsurf | scripts | all
                      Mặc định: all
    --global          Cài global thay vì per-project (chỉ hỗ trợ: codex)
    target-dir        Thư mục project (mặc định: CWD)

Ví dụ:
    # Cài tất cả tools cho project hiện tại
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py

    # Chỉ cài Cursor rule
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool cursor

    # Cài Codex global (~/.codex/AGENTS.md)
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool codex --global

    # Cài vào project cụ thể
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py --tool all /path/to/project
"""

import sys, shutil, os, argparse
from pathlib import Path

TOOLKIT_ROOT    = Path(__file__).resolve().parent.parent
ADAPTERS_DIR    = TOOLKIT_ROOT / "adapters"
TEMPLATES_DIR   = TOOLKIT_ROOT / "templates"
SCRIPTS_DIR     = TOOLKIT_ROOT / "scripts"

SUPPORTED_TOOLS = ["claude", "cursor", "codex", "windsurf", "scripts", "all"]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✓  {dst}")


def _write(dst: Path, content: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    print(f"  ✓  {dst}")


# ── Per-tool installers ───────────────────────────────────────────────────────

def install_scripts(target: Path) -> None:
    """Copy doc_context.py và code_research.py vào target/scripts/."""
    print("\n[scripts]")
    for script in ["doc_context.py", "code_research.py"]:
        _copy(SCRIPTS_DIR / script, target / "scripts" / script)
    print(f"  Usage: python scripts/doc_context.py <keyword>")


def install_cursor(target: Path) -> None:
    """Tạo .cursor/rules/bs-claude-toolkit.mdc trong project."""
    print("\n[cursor]")
    dst = target / ".cursor" / "rules" / "bs-claude-toolkit.mdc"
    _copy(ADAPTERS_DIR / "cursor.mdc", dst)
    print(f"  Rule sẽ tự apply cho mọi session trong project này.")


def install_codex(target: Path, *, global_install: bool = False) -> None:
    """
    Cài AGENTS.md cho Codex.
    global_install=True  → ~/.codex/AGENTS.md
    global_install=False → target/AGENTS.md
    """
    print("\n[codex]")
    if global_install:
        dst = Path.home() / ".codex" / "AGENTS.md"
        src = TEMPLATES_DIR / "AGENTS.md"
        _copy(src, dst)
        print(f"  Global AGENTS.md installed. Áp dụng cho mọi project trên máy này.")
    else:
        dst = target / "AGENTS.md"
        if dst.exists():
            print(f"  AGENTS.md đã tồn tại tại {dst} — bỏ qua.")
            print(f"  Nếu muốn ghi đè: xóa file trước rồi chạy lại.")
        else:
            _copy(TEMPLATES_DIR / "AGENTS.md", dst)
            print(f"  Chỉnh sửa [BE_DIR] và [FE_DIR] trong file vừa tạo.")


def install_windsurf(target: Path) -> None:
    """Tạo .windsurf/rules/bs-claude-toolkit.md trong project."""
    print("\n[windsurf]")
    dst = target / ".windsurf" / "rules" / "bs-claude-toolkit.md"
    _copy(ADAPTERS_DIR / "windsurf.md", dst)
    print(f"  Rule sẽ tự apply cho mọi session trong project này.")


def install_claude(target: Path) -> None:
    """Hướng dẫn install Claude Code skill (global, không cần per-project)."""
    print("\n[claude]")
    skill_path = Path.home() / ".claude" / "skills" / "bs-claude-toolkit"
    if (TOOLKIT_ROOT / "SKILL.md").exists() and TOOLKIT_ROOT == skill_path:
        print(f"  ✓  Skill đã được cài tại {TOOLKIT_ROOT}")
        print(f"  Dùng: /bs-claude-toolkit trong Claude Code")
    else:
        print(f"  Skill chưa được cài global. Chạy lệnh sau:")
        print(f"    git clone <repo-url> {skill_path}")

    # Copy CLAUDE.md template nếu chưa có
    claude_dst = target / "CLAUDE.md"
    if not claude_dst.exists():
        _copy(TEMPLATES_DIR / "CLAUDE.md", claude_dst)
        print(f"  CLAUDE.md template đã được tạo. Chỉnh sửa [BE_DIR] và [FE_DIR].")
    else:
        print(f"  CLAUDE.md đã tồn tại tại {claude_dst} — bỏ qua.")


# ── Main ─────────────────────────────────────────────────────────────────────

def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tool", default="all", choices=SUPPORTED_TOOLS)
    parser.add_argument("--global", dest="global_install", action="store_true")
    parser.add_argument("target", nargs="?", default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    target = Path(args.target).resolve() if args.target else Path(os.getcwd()).resolve()
    if not target.exists():
        print(f"Error: directory not found: {target}")
        sys.exit(1)

    tool = args.tool
    print(f"\nInstalling bs-claude-toolkit [{tool}] → {target}")

    if tool == "all":
        install_scripts(target)
        install_claude(target)
        install_cursor(target)
        install_codex(target, global_install=args.global_install)
        install_windsurf(target)
    elif tool == "scripts":
        install_scripts(target)
    elif tool == "claude":
        install_claude(target)
    elif tool == "cursor":
        install_cursor(target)
    elif tool == "codex":
        install_codex(target, global_install=args.global_install)
    elif tool == "windsurf":
        install_windsurf(target)

    print(f"\nDone.\n")


if __name__ == "__main__":
    main()
