#!/usr/bin/env python3
"""
sync_topics.py — Build/update topics.json from LeetHub's README section
and each problem's own README.md.

Usage:
    python scripts/sync_topics.py

This script is idempotent: running it multiple times produces the same
topics.json as long as the source files have not changed. Tags are only
ever added, never removed (additive merge).
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT    = Path(__file__).resolve().parent.parent
README_FILE  = REPO_ROOT / "README.md"
TOPICS_FILE  = REPO_ROOT / "topics.json"

FOLDER_RE = re.compile(r"^(\d{1,4})-([a-z0-9-]+)$")

# LeetHub section markers (2 or 3 leading dashes)
LEETHUB_START_RE = re.compile(r"<!-{2,3}LeetCode Topics Start-{2,3}>")
LEETHUB_END_RE   = re.compile(r"<!-{2,3}LeetCode Topics End-{2,3}>")

# ## Topic Heading
HEADING_RE = re.compile(r"^##\s+(.+)$")

# Folder link: [1143-longest-common-subsequence](url)
LINK_RE = re.compile(r"\[(\d{1,4}-[a-z0-9-]+)\]")


def parse_leethub_section(text: str) -> dict[str, list[str]]:
    """
    Extract { folder: [topics] } from the LeetHub auto-generated
    '# LeetCode Topics' section in root README.md.

    Structure (per LeetHub v2):
        ## Topic Name
        |  |
        | --- |
        | [folder-name](github-url) |
    """
    mapping: dict[str, list[str]] = {}

    start_m = LEETHUB_START_RE.search(text)
    end_m   = LEETHUB_END_RE.search(text)
    if not start_m or not end_m or start_m.start() >= end_m.start():
        return mapping

    section = text[start_m.end(): end_m.start()]
    current_topic: str | None = None

    for raw_line in section.splitlines():
        line = raw_line.strip()
        h = HEADING_RE.match(line)
        if h:
            current_topic = h.group(1).strip()
            continue
        if current_topic:
            lm = LINK_RE.search(line)
            if lm:
                folder = lm.group(1)
                if FOLDER_RE.match(folder):
                    mapping.setdefault(folder, [])
                    if current_topic not in mapping[folder]:
                        mapping[folder].append(current_topic)

    return mapping


def parse_problem_readme(folder: Path) -> list[str]:
    """
    Attempt to extract topic tags from a problem-level README.md.

    LeetHub v2 does not embed structured tags in per-problem READMEs,
    so this is a hook for future enhancements (e.g. scraping the Topics
    section if LeetHub ever adds it).
    """
    # Currently returns [] — extensible without breaking the rest of the pipeline.
    return []


def load_existing() -> dict[str, list[str]]:
    if not TOPICS_FILE.exists():
        return {}
    try:
        with open(TOPICS_FILE, encoding="utf-8-sig") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("root must be a JSON object")
        return data
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"WARNING: topics.json is malformed ({exc}); starting fresh.", file=sys.stderr)
        return {}


def merge(base: dict[str, list[str]], updates: dict[str, list[str]]) -> dict[str, list[str]]:
    """Additive merge: never drop known tags."""
    result = {k: list(v) for k, v in base.items()}
    for folder, tags in updates.items():
        result.setdefault(folder, [])
        for t in tags:
            if t not in result[folder]:
                result[folder].append(t)
    return result


def main() -> None:
    existing = load_existing()

    # Parse LeetHub topics section from root README
    readme_text = README_FILE.read_text(encoding="utf-8-sig") if README_FILE.exists() else ""
    from_readme  = parse_leethub_section(readme_text)

    # Parse per-problem READMEs (extensible hook)
    from_problems: dict[str, list[str]] = {}
    for entry in sorted(REPO_ROOT.iterdir()):
        if entry.is_dir() and FOLDER_RE.match(entry.name):
            extra = parse_problem_readme(entry)
            if extra:
                from_problems.setdefault(entry.name, []).extend(extra)

    # Merge all sources
    merged = merge(merge(existing, from_readme), from_problems)

    # Serialise: sorted keys, sorted tag lists, for deterministic output
    new_json = (
        json.dumps(
            {k: sorted(set(v)) for k, v in sorted(merged.items())},
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )

    current_json = (
        TOPICS_FILE.read_text(encoding="utf-8")
        if TOPICS_FILE.exists()
        else ""
    )

    if new_json == current_json:
        print(f"topics.json unchanged ({len(merged)} entr{'y' if len(merged)==1 else 'ies'}).")
    else:
        TOPICS_FILE.write_text(new_json, encoding="utf-8", newline="\n")
        print(f"topics.json updated ({len(merged)} entr{'y' if len(merged)==1 else 'ies'}).")


if __name__ == "__main__":
    main()