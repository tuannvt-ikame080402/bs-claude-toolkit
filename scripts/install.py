#!/usr/bin/env python3
"""
install.py — Copy scripts vào project để team members dùng mà không cần toolkit.

Chạy từ toolkit hoặc từ project:
    python ~/.claude/skills/bs-claude-toolkit/scripts/install.py [target-dir]

Nếu không có target-dir, copy vào thư mục hiện tại.

Việc sẽ làm:
    Copy doc_context.py và code_research.py vào target/scripts/
"""

import sys, shutil, os
from pathlib import Path

TOOLKIT_SCRIPTS = Path(__file__).resolve().parent


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.getcwd())
    target = target.resolve()

    if not target.exists():
        print(f"Error: directory not found: {target}")
        sys.exit(1)

    dst = target / "scripts"
    dst.mkdir(parents=True, exist_ok=True)

    for script in ["doc_context.py", "code_research.py"]:
        shutil.copy2(TOOLKIT_SCRIPTS / script, dst / script)
        print(f"Copied → {dst / script}")

    print(f"\nDone. Usage in your project:")
    print(f"  python scripts/doc_context.py <keyword>")
    print(f"  python scripts/code_research.py <keyword>")
    print(f"  python scripts/doc_context.py --scope <dir> <keyword>")


if __name__ == "__main__":
    main()
