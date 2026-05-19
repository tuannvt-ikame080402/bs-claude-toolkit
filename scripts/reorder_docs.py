#!/usr/bin/env python3
"""
reorder_docs.py — Re-sequence doc files by creation time to fix merge conflicts.

After a git merge, two developers may have created files with the same
sequence number (e.g., both 20260519-changelog-1-*.md). This script
renumbers files in chronological order so the earliest commit keeps
the lowest number.

Uses git first-commit time when available, falls back to file mtime.

Usage:
    python scripts/reorder_docs.py              # scan from cwd
    python scripts/reorder_docs.py [target-dir]
    python scripts/reorder_docs.py --dry-run    # preview, no rename
    python scripts/reorder_docs.py --scope be   # limit to one subdir

File patterns handled:
    docs/changelog/{YYYYMMDD}-changelog-{N}-{slug}.md
    docs/test/{YYYYMMDD}-test-{N}-{slug}.md
    docs/test/{YYYYMMDD}-testlog-{N}-{slug}.md
    docs/plan/sprint-{N}-{slug}.md  (only when duplicate Ns exist)
"""

import argparse
import os
import re
import subprocess
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DATED_RE  = re.compile(r'^(\d{8})-(changelog|test|testlog)-(\d+)-(.+)\.md$')
SPRINT_RE = re.compile(r'^sprint-(\d+)-(.+)\.md$')


# ── Git time ──────────────────────────────────────────────────────────────────

def _git_first_commit_time(path: Path) -> Optional[float]:
    """Return the unix timestamp of the first (oldest) git commit for this file."""
    try:
        r = subprocess.run(
            ['git', 'log', '--follow', '--format=%at', '--', str(path)],
            capture_output=True, text=True, timeout=10,
        )
        times = [int(t) for t in r.stdout.strip().splitlines() if t.strip()]
        return float(min(times)) if times else None
    except Exception:
        return None


def _sort_key(path: Path) -> float:
    t = _git_first_commit_time(path)
    return t if t is not None else path.stat().st_mtime


# ── Discovery ─────────────────────────────────────────────────────────────────

def _find_doc_dirs(root: Path, scope: Optional[str]) -> List[Path]:
    search = (root / scope) if scope else root
    found: List[Path] = []
    for sub in ('changelog', 'test', 'plan'):
        found.extend(d for d in search.rglob(f'docs/{sub}') if d.is_dir())
    return found


# ── Grouping & rename computation ─────────────────────────────────────────────

def _compute_dated_renames(doc_dir: Path) -> List[Tuple[Path, Path]]:
    """
    For changelog/test dirs: group files by (date, type), sort each group by
    git time, renumber 1..N. Returns all renames needed.
    """
    groups: Dict[Tuple[str, str], List[Path]] = defaultdict(list)
    for f in doc_dir.iterdir():
        if not f.is_file() or f.suffix != '.md':
            continue
        m = DATED_RE.match(f.name)
        if m:
            date, type_ = m.group(1), m.group(2)
            groups[(date, type_)].append(f)

    renames: List[Tuple[Path, Path]] = []
    for (date, type_), files in sorted(groups.items()):
        sorted_files = sorted(files, key=_sort_key)
        for new_n, path in enumerate(sorted_files, start=1):
            m = DATED_RE.match(path.name)
            assert m
            old_n, slug = int(m.group(3)), m.group(4)
            if old_n != new_n:
                new_path = path.parent / f'{date}-{type_}-{new_n}-{slug}.md'
                renames.append((path, new_path))
    return renames


def _compute_sprint_renames(doc_dir: Path) -> List[Tuple[Path, Path]]:
    """
    For plan dirs: only renumber when duplicate sprint Ns exist after a merge.
    Keeps all non-duplicate sprint numbers untouched.
    """
    files: List[Path] = []
    for f in doc_dir.iterdir():
        if f.is_file() and f.suffix == '.md' and SPRINT_RE.match(f.name):
            files.append(f)

    if not files:
        return []

    ns = [int(SPRINT_RE.match(f.name).group(1)) for f in files]  # type: ignore[union-attr]
    if len(ns) == len(set(ns)):
        return []  # no duplicate sprint numbers — nothing to do

    # Duplicates exist: sort all by time, renumber starting from min(existing Ns)
    start_n = min(ns)
    sorted_files = sorted(files, key=_sort_key)
    renames: List[Tuple[Path, Path]] = []
    for new_n, path in enumerate(sorted_files, start=start_n):
        m = SPRINT_RE.match(path.name)
        assert m
        old_n, slug = int(m.group(1)), m.group(2)
        if old_n != new_n:
            renames.append((path, path.parent / f'sprint-{new_n}-{slug}.md'))
    return renames


# ── Apply ─────────────────────────────────────────────────────────────────────

def _apply(renames: List[Tuple[Path, Path]], dry_run: bool) -> None:
    if dry_run:
        for old, new in renames:
            print(f'  [dry]  {old.name}  →  {new.name}')
        return
    # Two-pass: temp rename first to avoid collisions (e.g., 2→1 when 1 still exists)
    staged: List[Tuple[Path, Path]] = []
    for old, new in renames:
        tmp = old.parent / f'_reorder_{uuid.uuid4().hex[:8]}_{old.name}'
        old.rename(tmp)
        staged.append((tmp, new))
        print(f'  {old.name}  →  {new.name}')
    for tmp, new in staged:
        tmp.rename(new)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('target', nargs='?', default=None, help='Project root (default: cwd)')
    ap.add_argument('--dry-run', '-n', action='store_true', help='Preview changes without renaming')
    ap.add_argument('--scope', default=None, metavar='SUBDIR', help='Limit scan to one subdirectory')
    args = ap.parse_args()

    root = Path(args.target).resolve() if args.target else Path(os.getcwd()).resolve()
    if not root.exists():
        print(f'Error: {root} not found')
        sys.exit(1)

    doc_dirs = _find_doc_dirs(root, args.scope)
    if not doc_dirs:
        print('No docs/changelog|test|plan directories found.')
        return

    total = 0
    for doc_dir in sorted(doc_dirs):
        rel = doc_dir.relative_to(root)
        dir_name = doc_dir.name  # changelog, test, or plan

        if dir_name == 'plan':
            renames = _compute_sprint_renames(doc_dir)
        else:
            renames = _compute_dated_renames(doc_dir)

        if not renames:
            continue

        print(f'\n[{rel}]')
        _apply(renames, args.dry_run)
        total += len(renames)

    if total == 0:
        print('All files already in order — nothing to rename.')
    elif args.dry_run:
        print(f'\n{total} file(s) would be renamed. Run without --dry-run to apply.')
    else:
        print(f'\n{total} file(s) renamed.')


if __name__ == '__main__':
    main()
