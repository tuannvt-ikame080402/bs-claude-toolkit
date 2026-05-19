#!/usr/bin/env python3
"""
code_research.py — Tìm kiếm code theo từ khóa trong project.

Tự động phát hiện cấu trúc project — không cần cấu hình.
Hỗ trợ mọi naming convention: backend/, frontend/, myapp-be/, myapp-fe/, api/, web/, ...

Chạy từ root project (hoặc bất kỳ subdir nào):
    python scripts/code_research.py [--scope <dir>] <keyword> [keyword2 ...]

Options:
    --scope <dir>   Chỉ tìm trong submodule có tên chứa <dir> (case-insensitive)
                    Ví dụ: --scope be  →  chỉ tìm trong backend/, myapp-be/, ...

Ví dụ:
    python scripts/code_research.py video_pipeline max_retries
    python scripts/code_research.py --scope be video_pipeline celery
    python scripts/code_research.py --scope fe useAssets refetchInterval
    python scripts/code_research.py notification toast sonner
"""

import sys, io, re, argparse
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _find_root() -> Path:
    """
    Tìm project root.
    Ưu tiên CWD — cho phép script chạy từ bất kỳ đâu (kể cả từ toolkit location)
    và vẫn tìm đúng root của project đang làm việc.
    Fallback về vị trí script nếu CWD không có dấu hiệu project.
    """
    # Priority 1: walk up from CWD
    for p in [Path.cwd()] + list(Path.cwd().parents):
        if (p / ".git").exists() or (p / "CLAUDE.md").exists():
            return p
    # Priority 2: walk up from script location (fallback)
    candidate = Path(__file__).resolve().parent
    if candidate.name == "scripts":
        candidate = candidate.parent
    for p in [candidate] + list(candidate.parents):
        if (p / ".git").exists() or (p / "CLAUDE.md").exists():
            return p
    return Path.cwd()


ROOT = _find_root()

EXCLUDE_DIRS = frozenset(
    {"node_modules", "__pycache__", ".next", "venv", ".venv", "dist", "build", ".git", ".turbo", "coverage"}
)

# FE: tên thư mục phổ biến chứa source code frontend
FE_DIR_NAMES = ["features", "app", "pages", "src", "components", "hooks", "lib", "utils", "store", "views"]
FE_EXTS      = {".ts", ".tsx", ".js", ".jsx"}

# BE: tên thư mục phổ biến chứa source code backend
BE_DIR_NAMES = [
    "controllers", "services", "repositories", "tasks", "integrations",
    "schemas", "models", "routes", "api", "handlers", "middleware", "core", "pipelines",
]
BE_EXTS = {".py"}

# Tên thư mục trung gian phổ biến trong BE (Flask: app/, Django: app_name/, Celery: worker/)
BE_NESTED_CONTAINERS = ["app", "worker", "src", "core"]

CONTEXT_LINES  = 1
MAX_MATCH_FILE = 4
MAX_FILES_GRP  = 6
MAX_LINE_LEN   = 120


def _is_submodule(path: Path) -> bool:
    """Submodule = chứa CLAUDE.md, Agents.md, docs/, hoặc có code patterns."""
    if (path / "CLAUDE.md").exists() or (path / "Agents.md").exists() or (path / "docs").is_dir():
        return True
    # Fallback: thư mục chứa code trực tiếp (FE/BE patterns)
    for fe_dir in FE_DIR_NAMES[:4]:
        if (path / fe_dir).is_dir():
            return True
    for be_dir in BE_DIR_NAMES[:4]:
        if (path / be_dir).is_dir():
            return True
    return False


def _discover_search_groups(scope: str | None) -> list[tuple[str, Path, set[str]]]:
    """
    Auto-discover code search groups từ cấu trúc project thực tế.
    scope: nếu có, chỉ lấy subdirs có tên chứa scope (case-insensitive).
    """
    groups: list[tuple[str, Path, set[str]]] = []
    seen: set[Path] = set()

    def _add(label: str, path: Path, exts: set[str]) -> None:
        if path in seen or not path.exists() or not path.is_dir():
            return
        seen.add(path)
        groups.append((label, path, exts))

    subdirs = sorted(ROOT.iterdir())

    # Single-app fallback: nếu không có scope và root chứa code trực tiếp
    if scope is None:
        for fe_dir in FE_DIR_NAMES:
            _add(f"» {fe_dir}", ROOT / fe_dir, FE_EXTS)
        for be_dir in BE_DIR_NAMES:
            _add(f"» {be_dir}", ROOT / be_dir, BE_EXTS)

    for subdir in subdirs:
        if not subdir.is_dir():
            continue
        if subdir.name in EXCLUDE_DIRS or subdir.name.startswith("."):
            continue
        if not _is_submodule(subdir):
            continue
        if scope and scope.lower() not in subdir.name.lower():
            continue

        name = subdir.name

        # FE code patterns trực tiếp trong subdir
        for fe_dir in FE_DIR_NAMES:
            _add(f"{name} » {fe_dir}", subdir / fe_dir, FE_EXTS)

        # BE code patterns — thẳng hoặc qua nested container
        for be_dir in BE_DIR_NAMES:
            _add(f"{name} » {be_dir}", subdir / be_dir, BE_EXTS)
            for container in BE_NESTED_CONTAINERS:
                _add(f"{name} » {be_dir}", subdir / container / be_dir, BE_EXTS)

    # Nếu không tìm thấy gì: fallback toàn bộ src/
    if not groups:
        _add("src", ROOT / "src", FE_EXTS | BE_EXTS)
        _add("root", ROOT, FE_EXTS | BE_EXTS)

    return groups


def _trunc(s: str, n: int = MAX_LINE_LEN) -> str:
    return s if len(s) <= n else s[:n] + "…"


def _skip(path: Path) -> bool:
    return any(p in EXCLUDE_DIRS for p in path.parts)


def _scope_name(lines: list[str], block_start: int) -> str:
    """Tìm tên function/class chứa block (scan ngược tối đa 25 dòng)."""
    for i in range(block_start - 1, max(-1, block_start - 25), -1):
        s = lines[i].lstrip()
        if s.startswith(("def ", "async def ", "class ")):
            return s.split("(")[0].split(":")[0].strip()[:70]
        m = re.match(
            r"(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)|"
            r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(",
            s,
        )
        if m:
            return f"{(m.group(1) or m.group(2))}()"[:70]
    return ""


def search_file(path: Path, pattern: re.Pattern) -> list[list[str]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []

    hits = [i for i, ln in enumerate(lines) if pattern.search(ln)]
    if not hits:
        return []

    raw = [
        (max(0, i - CONTEXT_LINES), min(len(lines), i + CONTEXT_LINES + 1), i)
        for i in hits[: MAX_MATCH_FILE * 2]
    ]

    merged: list[tuple[int, int, frozenset]] = []
    s, e, hset = raw[0][0], raw[0][1], {raw[0][2]}
    for ns, ne, nh in raw[1:]:
        if ns <= e:
            e = max(e, ne)
            hset.add(nh)
        else:
            merged.append((s, e, frozenset(hset)))
            s, e, hset = ns, ne, {nh}
    merged.append((s, e, frozenset(hset)))

    blocks = []
    for s, e, hset in merged[:MAX_MATCH_FILE]:
        scope = _scope_name(lines, s)
        block: list[str] = []
        if scope:
            block.append(f"    ↳ {scope}")
        block += [
            f"    {'>>>' if j in hset else '   '} {j+1:4d}: {_trunc(lines[j])}"
            for j in range(s, e)
        ]
        blocks.append(block)

    return blocks


def _parse_args() -> tuple[str | None, list[str]]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--scope", default=None)
    parsed, rest = parser.parse_known_args()
    if not rest:
        print(__doc__)
        sys.exit(1)
    return parsed.scope, rest


def main() -> None:
    scope, keywords = _parse_args()
    pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE | re.UNICODE)

    search_groups = _discover_search_groups(scope)

    print(f"\n{'='*64}")
    print(f"  CODE RESEARCH: {' + '.join(repr(k) for k in keywords)}")
    if scope:
        print(f"  SCOPE: {scope}")
    print(f"  ROOT: {ROOT}")
    print(f"{'='*64}")

    total_files = total_matches = 0

    for group_name, search_dir, exts in search_groups:
        if not search_dir.exists():
            continue
        hits = []
        for path in sorted(search_dir.rglob("*")):
            if _skip(path) or path.is_dir() or path.suffix not in exts:
                continue
            blocks = search_file(path, pattern)
            if blocks:
                hits.append((path, blocks))
                if len(hits) >= MAX_FILES_GRP:
                    break

        if not hits:
            continue

        match_sum = sum(len(b) for _, b in hits)
        print(f"\n{'─'*64}\n  [{group_name}]  — {len(hits)} file, {match_sum} block\n{'─'*64}")

        for path, blocks in hits:
            rel = path.relative_to(ROOT)
            print(f"\n  {rel}  ({len(blocks)} block)")
            for i, block in enumerate(blocks[:3]):
                if i > 0:
                    print(f"    {'·'*26}")
                print("\n".join(block))
            if len(blocks) > 3:
                print(f"    … (+{len(blocks)-3} block nữa)")

        total_files += len(hits)
        total_matches += match_sum

    if total_files == 0:
        print(f"\n  Không tìm thấy code nào liên quan: {keywords}\n")
    else:
        print(f"\n{'='*64}")
        print(f"  Tổng kết: {total_files} file  |  {total_matches} block")
        print(f"{'='*64}\n")


if __name__ == "__main__":
    main()
