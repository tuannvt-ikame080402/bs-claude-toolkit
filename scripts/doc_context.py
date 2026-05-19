#!/usr/bin/env python3
"""
doc_context.py — Tra cứu tài liệu (plan / changelog / test) theo từ khóa.

Tự động phát hiện cấu trúc project — không cần cấu hình.

Chạy từ root project:
    python scripts/doc_context.py <keyword> [keyword2 ...]

Ví dụ:
    python scripts/doc_context.py notification toast
    python scripts/doc_context.py assets pagination total_pages
    python scripts/doc_context.py video generation retry
"""

import sys, io, re
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _find_root() -> Path:
    """Tìm project root: thư mục chứa script, rồi đi lên cho đến khi thấy .git hoặc CLAUDE.md."""
    candidate = Path(__file__).resolve().parent
    # Nếu script nằm trong scripts/ thì root là parent
    if candidate.name == "scripts":
        candidate = candidate.parent
    # Walk up tìm .git hoặc CLAUDE.md
    for p in [candidate] + list(candidate.parents):
        if (p / ".git").exists() or (p / "CLAUDE.md").exists():
            return p
    return candidate


ROOT = _find_root()

EXCLUDE_DIRS = frozenset({"node_modules", "__pycache__", ".next", "venv", ".venv", "dist", "build", ".git"})

CONTEXT_LINES  = 1
MAX_EXCERPTS   = 2
MAX_LINE_LEN   = 120
MAX_PLAN_FILES = 99
MAX_CL_FILES   = 5
MAX_TEST_FILES = 3


def _discover_doc_dirs() -> list[tuple[str, str, Path]]:
    """Auto-discover tất cả */docs/{plan,changelog,test} trong project."""
    result: list[tuple[str, str, Path]] = []

    # Root-level docs/
    for doc_type in ("plan", "changelog", "test"):
        p = ROOT / "docs" / doc_type
        if p.exists():
            result.append(("root", doc_type, p))

    # Subdirectory docs/ (backend/, frontend/, packages/*, apps/*, ...)
    for subdir in sorted(ROOT.iterdir()):
        if not subdir.is_dir() or subdir.name in EXCLUDE_DIRS:
            continue
        if subdir.name.startswith("."):
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


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    keywords = sys.argv[1:]
    pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE | re.UNICODE)

    doc_dirs = _discover_doc_dirs()

    print(f"\n{'='*64}")
    print(f"  DOC CONTEXT: {' + '.join(repr(k) for k in keywords)}")
    print(f"  ROOT: {ROOT}")
    print(f"{'='*64}")

    buckets: dict[str, list[dict]] = {"plan": [], "changelog": [], "test": []}

    for side, doc_type, doc_dir in doc_dirs:
        for md in sorted(doc_dir.glob("*.md")):
            count, excerpts = search_file(md, pattern)
            if count:
                buckets[doc_type].append(
                    {
                        "path": md,
                        "side": side,
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

    all_shown = (
        [x["name"] for x in plans]
        + [x["name"] for x in changelogs]
        + [x["name"] for x in tests]
    )
    if all_shown:
        print(f"  → {', '.join(all_shown)}\n")

    for label, items in [
        ("PLAN", plans),
        ("CHANGELOG", changelogs),
        ("TEST", tests),
    ]:
        if not items:
            continue
        print(f"\n{'─'*64}\n  {label}  ({len(items)} file)\n{'─'*64}")
        for item in items:
            rel = item["path"].relative_to(ROOT)
            print(f"\n  [{item['side'].upper()}]  {item['name']}   ({item['count']} match)")
            print(f"  {rel}")
            for i, ex in enumerate(item["excerpts"]):
                if i > 0:
                    print(f"  {'·'*28}")
                print(ex)

    print(f"\n{'='*64}\n")


if __name__ == "__main__":
    main()
