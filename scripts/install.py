#!/usr/bin/env python3
"""
install.py — Cài đặt bs-claude-toolkit vào project hiện tại.

Chạy từ trong thư mục bs-claude-toolkit:
    python scripts/install.py [target-dir]

Nếu không có target-dir, dùng thư mục hiện tại của shell.

Việc sẽ làm:
  1. Copy scripts/ vào target/scripts/
  2. Copy .claude/skills/ctx/ vào ~/.claude/skills/ctx/  (global skill)
"""

import sys, shutil, os
from pathlib import Path

TOOLKIT_ROOT = Path(__file__).resolve().parent.parent


def copy_scripts(target: Path) -> None:
    src = TOOLKIT_ROOT / "scripts"
    dst = target / "scripts"
    dst.mkdir(parents=True, exist_ok=True)
    for script in ["doc_context.py", "code_research.py"]:
        shutil.copy2(src / script, dst / script)
        print(f"  Copied: {dst / script}")


def install_skill() -> None:
    src = TOOLKIT_ROOT / ".claude" / "skills" / "ctx"
    home = Path.home()
    dst = home / ".claude" / "skills" / "ctx"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"  Skill installed: {dst}")
    print(f"  Invoke with: /ctx or /ctx backend or /ctx frontend")


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.getcwd())
    target = target.resolve()

    if not target.exists():
        print(f"Error: target directory does not exist: {target}")
        sys.exit(1)

    print(f"\nInstalling bs-claude-toolkit into: {target}\n")

    copy_scripts(target)
    install_skill()

    print(f"\nDone.")
    print(f"\nUsage in your project:")
    print(f"  python scripts/doc_context.py <keyword>")
    print(f"  python scripts/code_research.py <keyword>")
    print(f"  /ctx          (in Claude Code)")


if __name__ == "__main__":
    main()
