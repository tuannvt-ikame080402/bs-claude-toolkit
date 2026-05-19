#!/usr/bin/env python3
"""
doc_context.py — Tra cứu tài liệu (plan / changelog / test) theo từ khóa.

Tự động phát hiện cấu trúc project — không cần cấu hình.
Hỗ trợ mọi naming convention: backend/, frontend/, myapp-be/, myapp-fe/, api/, web/, ...

Chạy từ root project (hoặc bất kỳ subdir nào):
    python scripts/doc_context.py [--scope <dir>] <keyword> [keyword2 ...]

Options:
    --scope <dir>   Chỉ tìm trong submodule có tên chứa <dir> (case-insensitive)
                    Ví dụ: --scope be  →  chỉ tìm trong backend/, myapp-be/, ...

Ví dụ:
    python scripts/doc_context.py video generation retry
    python scripts/doc_context.py --scope be video generation retry
    python scripts/doc_context.py --scope fe notification toast
    python scripts/doc_context.py assets pagination total_pages
"""

import sys, io, re, argparse
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _find_root() -> Path:
    """Tìm project root bằng cách đi lên đến khi gặp .git hoặc CLAUDE.md."""
    candidate = Path(__file__).resolve().parent
    if candidate.name == "scripts":
        candidate = candidate.parent
    for p in [candidate] + list(candidate.parents):
        if (p / ".git").exists() or (p / "CLAUDE.md").exists():
            return p
    return candidate


ROOT = _find_root()

EXCLUDE_DIRS = frozenset(
    {"node_modules", "__pycache__", ".next", "venv", ".venv", "dist", "build", ".git", ".turbo", "coverage"}
)

CONTEXT_LINES  = 1
MAX_EXCERPTS   = 2
MAX_LINE_LEN   = 120
MAX_PLAN_FILES = 99
MAX_CL_FILES   = 5
MAX_TEST_FILES = 3


def _is_submodule(path: Path) -> bool:
    """Submodule = chứa CLAUDE.md, Agents.md, hoặc docs/."""
    return (
        (path / "CLAUDE.md").exists()
        or (path / "Agents.md").exists()
        or (path / "docs").is_dir()
    )


def _discover_doc_dirs(scope: str | None) -> list[tuple[str, str, Path]]:
    """
    Auto-discover tất cả */docs/{plan,changelog,test} trong project.
    scope: nếu có, chỉ lấy subdirs có tên chứa scope (case-insensitive).
    """
    result: list[tuple[str, str, Path]] = []

    # Root-level docs/ (single-app project)
    if scope is None:
        for doc_type in ("plan", "changelog", "test"):
            p = ROOT / "docs" / doc_type
            if p.exists():
                result.append(("root", doc_type, p))

    # Submodule docs/ — bất kỳ tên thư mục nào
    for subdir in sorted(ROOT.iterdir()):
        if not subdir.is_dir():
            continue
        if subdir.name in EXCLUDE_DIRS or subdir.name.startswith("."):
            continue
        if not _is_submodule(subdir):
            continue
        if scope and scope.lower() not in subdir.name.lower():
            continue
        for doc_type in ("plan", "changelog", "test"):
            p = subdir / "docs" / doc_type
            if p.exists():
                result.append((subdir.name, doc_type, p))

    return result


def _trunc(s: str, n: int = MAX_LINE_LEN) -> str:
    return s if len(s) <= n else s[:n] + "…"


def _date_key(name: str) -> str:
    m = re.match(r"^(\d{8})-", name)
    if m:
        return m.group(1)
    m = re.match(r"^sprint-(\d+)", name)
    if m:
        return f"sprint-{int(m.group(1)):05d}"
    return "00000000"


def search_file(path: Path, pattern: re.Pattern) -> tuple[int, list[str]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return 0, []

    hits = [i for i, ln in enumerate(lines) if pattern.search(ln)]
    if not hits:
        return 0, []

    raw = [
        (max(0, i - CONTEXT_LINES), min(len(lines), i + CONTEXT_LINES + 1), i)
        for i in hits[: MAX_EXCERPTS * 3]
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

    excerpts = []
    for s, e, hset in merged[:MAX_EXCERPTS]:
        block = [
            f"  {'>>>' if j in hset else '   '} {j+1:4d}: {_trunc(lines[j])}"
            for j in range(s, e)
        ]
        excerpts.append("\n".join(block))

    return len(hits), excerpts


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

    doc_dirs = _discover_doc_dirs(scope)

    print(f"\n{'='*64}")
    print(f"  DOC CONTEXT: {' + '.join(repr(k) for k in keywords)}")
    if scope:
        print(f"  SCOPE: {scope}")
    print(f"  ROOT: {ROOT}")
    print(f"{'='*64}")

    if not doc_dirs:
        print(f"\n  Không tìm thấy docs/ trong project (scope={scope!r})\n")
        return

    buckets: dict[str, list[dict]] = {"plan": [], "changelog": [], "test": []}

    for label, doc_type, doc_dir in doc_dirs:
        for md in sorted(doc_dir.glob("*.md")):
            count, excerpts = search_file(md, pattern)
            if count:
                buckets[doc_type].append(
                    {
                        "path": md,
                        "label": label,
                        "name": md.name,
                        "date_key": _date_key(md.name),
                        "count": count,
                        "excerpts": excerpts,
                    }
                )

    total = sum(len(v) for v in buckets.values())
    if total == 0:
        print(f"\n  Không tìm thấy tài liệu nào liên quan: {keywords}\n")
        return

    plans      = sorted(buckets["plan"],      key=lambda x: x["date_key"])[:MAX_PLAN_FILES]
    changelogs = sorted(buckets["changelog"], key=lambda x: x["date_key"], reverse=True)[:MAX_CL_FILES]
    tests      = sorted(buckets["test"],      key=lambda x: x["date_key"], reverse=True)[:MAX_TEST_FILES]

    shown = len(plans) + len(changelogs) + len(tests)
    print(f"\n  Tìm thấy {total} file  (hiển thị {shown})\n")
    all_names = [x["name"] for x in plans + changelogs + tests]
    if all_names:
        print(f"  → {', '.join(all_names)}\n")

    for section_label, items in [("PLAN", plans), ("CHANGELOG", changelogs), ("TEST", tests)]:
        if not items:
            continue
        print(f"\n{'─'*64}\n  {section_label}  ({len(items)} file)\n{'─'*64}")
        for item in items:
            rel = item["path"].relative_to(ROOT)
            print(f"\n  [{item['label'].upper()}]  {item['name']}   ({item['count']} match)")
            print(f"  {rel}")
            for i, ex in enumerate(item["excerpts"]):
                if i > 0:
                    print(f"  {'·'*28}")
                print(ex)

    print(f"\n{'='*64}\n")


if __name__ == "__main__":
    main()
