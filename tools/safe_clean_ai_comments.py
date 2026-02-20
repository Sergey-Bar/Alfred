#!/usr/bin/env python3
"""
Safe AI Comment Removal Script
Removes AI attribution comments while preserving file structure.
"""

import os
import re
from pathlib import Path

# Build marker dynamically to avoid self-matching
_AI = "AI"
_GEN = "GENERATED"
AI_MARKER = f"[{_AI} {_GEN}"

# Patterns for AI comment lines (excluding marker line which is handled separately)
AI_LINE_PATTERNS = [
    r"^\s*#\s*Model:\s*.+$",
    r"^\s*#\s*Logic:\s*.+$",
    r"^\s*#\s*Why:\s*.+$",
    r"^\s*#\s*Root\s*Cause:\s*.+$",
    r"^\s*#\s*Context:\s*.+$",
    r"^\s*#\s*Model\s*Suitability:\s*.+$",
    r"^\s*#\s*Tier:\s*L[1-4].*$",
    r"^\s*//\s*Model:\s*.+$",
    r"^\s*//\s*Logic:\s*.+$",
    r"^\s*//\s*Why:\s*.+$",
    r"^\s*//\s*Root\s*Cause:\s*.+$",
    r"^\s*//\s*Context:\s*.+$",
    r"^\s*//\s*Model\s*Suitability:\s*.+$",
    r"^\s*//\s*Tier:\s*L[1-4].*$",
    r"^\s*\*\s*Model:\s*.+$",
    r"^\s*\*\s*Logic:\s*.+$",
    r"^\s*\*\s*Why:\s*.+$",
    r"^\s*\*\s*Root\s*Cause:\s*.+$",
    r"^\s*\*\s*Context:\s*.+$",
    r"^\s*\*\s*Model\s*Suitability:\s*.+$",
    r"^\s*\*\s*Tier:\s*L[1-4].*$",
    r"^\s*[#/*]+\s*─+.*$",
]

EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".yaml", ".yml", 
              ".md", ".css", ".scss", ".toml", ".json", ".sh", ".ps1", ".sql"}

SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", 
             "build", ".pytest_cache", ".mypy_cache"}

SKIP_FILES = {"safe_clean_ai_comments.py"}  # Exclude self


def is_ai_line(line: str) -> bool:
    for p in AI_LINE_PATTERNS:
        if re.match(p, line, re.IGNORECASE):
            return True
    return False


def clean_file(fpath: Path) -> tuple[bool, int]:
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  Error reading {fpath}: {e}")
        return False, 0

    new_lines = []
    removed = 0
    in_block = False
    empty_count = 0

    for line in lines:
        stripped = line.strip()

        # Check for AI block start
        if AI_MARKER in line:
            in_block = True
            removed += 1
            continue

        if in_block:
            if is_ai_line(line):
                removed += 1
                continue
            elif stripped in ("", '"""', "'''", "*/", "#"):
                if stripped in ('"""', "'''"):
                    new_lines.append(line)
                in_block = False
                continue
            else:
                in_block = False

        if is_ai_line(line):
            removed += 1
            continue

        # Limit consecutive empty lines
        if stripped == "":
            empty_count += 1
            if empty_count <= 2:
                new_lines.append(line)
        else:
            empty_count = 0
            new_lines.append(line)

    if removed > 0:
        try:
            with open(fpath, "w", encoding="utf-8", newline="") as f:
                f.writelines(new_lines)
            return True, removed
        except Exception as e:
            print(f"  Error writing {fpath}: {e}")
    return False, 0


def process_dir(root: Path, dry: bool = False) -> dict:
    stats = {"processed": 0, "modified": 0, "lines": 0, "errors": []}

    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]

        for fn in fns:
            if fn in SKIP_FILES:
                continue
            fp = Path(dp) / fn
            if fp.suffix.lower() not in EXTENSIONS:
                continue

            stats["processed"] += 1

            if dry:
                try:
                    content = fp.read_text(encoding="utf-8", errors="replace")
                    if AI_MARKER in content or any(
                        re.search(p, content, re.MULTILINE | re.IGNORECASE)
                        for p in AI_LINE_PATTERNS[:7]
                    ):
                        print(f"  Would modify: {fp}")
                        stats["modified"] += 1
                except Exception as e:
                    stats["errors"].append(f"{fp}: {e}")
            else:
                mod, cnt = clean_file(fp)
                if mod:
                    print(f"  Modified: {fp} ({cnt} lines)")
                    stats["modified"] += 1
                    stats["lines"] += cnt

    return stats


def main():
    import argparse
    p = argparse.ArgumentParser(description="Remove AI comments")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--path", default=".")
    args = p.parse_args()

    root = Path(args.path).resolve()
    print(f"Processing: {root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("-" * 60)

    stats = process_dir(root, args.dry_run)

    print("-" * 60)
    print(f"Files processed: {stats['processed']}")
    print(f"Files modified: {stats['modified']}")
    if not args.dry_run:
        print(f"Lines removed: {stats['lines']}")


if __name__ == "__main__":
    main()
