#!/usr/bin/env python3
"""
generate_readme.py — Regenerate root README.md for Leetcode-Daily.

Usage:
    python scripts/generate_readme.py

Optionally run sync_topics.py first to refresh topics.json:
    python scripts/sync_topics.py && python scripts/generate_readme.py

Edit the CONFIG block below to personalise.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
GITHUB_USERNAME   = "parth10march"
LEETCODE_USERNAME = "REPLACE_ME"   # TODO: replace with your LeetCode handle (e.g. "parth10march")
LINKEDIN_USERNAME = "REPLACE_ME"   # TODO: replace with your LinkedIn handle
DISPLAY_NAME      = "Parth Arjun Shukla"
ACCENT_COLOR      = "00b8a3"       # hex, no leading '#'  — LeetCode Easy teal
REPO_NAME         = "Leetcode-Daily"
# ──────────────────────────────────────────────────────────────────────────────

REPO_ROOT   = Path(__file__).resolve().parent.parent
STATS_FILE  = REPO_ROOT / "stats.json"
TOPICS_FILE = REPO_ROOT / "topics.json"
README_FILE = REPO_ROOT / "README.md"

FOLDER_RE = re.compile(r"^(\d{1,4})-([a-z0-9-]+)$")

EXT_TO_LANG: dict[str, str] = {
    ".java":  "Java",
    ".py":    "Python",
    ".cpp":   "C++",
    ".js":    "JavaScript",
    ".c":     "C",
    ".kt":    "Kotlin",
    ".go":    "Go",
    ".ts":    "TypeScript",
    ".rs":    "Rust",
    ".swift": "Swift",
    ".rb":    "Ruby",
    ".cs":    "C#",
    ".scala": "Scala",
}

# Roman numerals (word-boundary match only; must be full slug word)
ROMAN: dict[str, str] = {
    "i": "I", "ii": "II", "iii": "III", "iv": "IV", "v": "V",
    "vi": "VI", "vii": "VII", "viii": "VIII", "ix": "IX", "x": "X",
}

DIFF_COLOR: dict[str, str] = {
    "easy": "00b8a3", "medium": "ffc01e", "hard": "ff375f", "unknown": "8b949e",
}
DIFF_EMOJI: dict[str, str] = {
    "easy": "🟢", "medium": "🟡", "hard": "🔴", "unknown": "⚪",
}

AUTO_START = "<!-- AUTO:START -->"
AUTO_END   = "<!-- AUTO:END -->"

# LeetHub uses <!---LeetCode Topics Start--> (3 dashes) or <!--...-> (2 dashes)
LEETHUB_START_RE = re.compile(r"<!-{2,3}LeetCode Topics Start-{2,3}>")
LEETHUB_END_RE   = re.compile(r"<!-{2,3}LeetCode Topics End-{2,3}>")


# ── HELPERS ───────────────────────────────────────────────────────────────────

def slug_to_title(slug: str) -> str:
    """Convert a problem slug to Title Case, keeping Roman numerals uppercase."""
    parts = slug.split("-")
    result = []
    for p in parts:
        lo = p.lower()
        if lo in ROMAN:
            result.append(ROMAN[lo])
        else:
            result.append(p.capitalize() if p else p)
    return " ".join(result)


def load_stats() -> dict:
    """Load and validate stats.json. Exit with a clear message on malformed input."""
    if not STATS_FILE.exists():
        print(f"ERROR: {STATS_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    try:
        with open(STATS_FILE, encoding="utf-8-sig") as f:
            raw = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: stats.json is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    if "leetcode" not in raw:
        print("ERROR: stats.json missing top-level 'leetcode' key.", file=sys.stderr)
        sys.exit(1)
    return raw["leetcode"]


def load_topics() -> dict[str, list[str]]:
    """Load topics.json if present; return empty dict on missing or malformed."""
    if not TOPICS_FILE.exists():
        return {}
    try:
        with open(TOPICS_FILE, encoding="utf-8-sig") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("root must be a JSON object")
        return data
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"WARNING: topics.json is malformed ({exc}), ignoring tags.", file=sys.stderr)
        return {}


def git_first_date(folder: Path) -> str:
    """Return YYYY-MM-DD of the first commit that added this folder. mtime fallback."""
    rel = folder.relative_to(REPO_ROOT).as_posix()
    try:
        out = subprocess.check_output(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", rel],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
        )
        lines = [ln.strip() for ln in out.strip().splitlines() if ln.strip()]
        if lines:
            # Last line = earliest commit
            return lines[-1][:10]
    except Exception:
        pass
    # Fallback: folder mtime
    try:
        mtime = folder.stat().st_mtime
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return "\u2014"


def pbar(count: int, total: int, width: int = 20) -> str:
    """Unicode progress bar using filled/empty block characters."""
    if total <= 0:
        return "\u2591" * width  # light shade when no data
    filled = round(count / total * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def compute_streaks(problems: list[dict]) -> tuple[int, int]:
    """Return (current_streak_days, longest_streak_days) from problem dates."""
    raw_dates: list[date] = []
    for p in problems:
        d = p.get("date", "")
        if d and d != "\u2014":
            try:
                raw_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
            except ValueError:
                pass

    if not raw_dates:
        return 0, 0

    unique_dates = sorted(set(raw_dates))
    date_set = set(unique_dates)

    today = datetime.now(timezone.utc).date()

    # Current streak: consecutive days ending today (or yesterday)
    current = 0
    check = today
    while check in date_set:
        current += 1
        check -= timedelta(days=1)
    if current == 0 and (today - timedelta(days=1)) in date_set:
        # Allow streak that ended yesterday
        check = today - timedelta(days=1)
        while check in date_set:
            current += 1
            check -= timedelta(days=1)

    # Longest streak: scan all dates
    longest = 1
    run = 1
    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i - 1]).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    return current, max(longest, current if current else 1)


def discover_problems(stats: dict, topics: dict[str, list[str]]) -> list[dict]:
    """Scan repo root for problem folders and collect metadata."""
    shas = stats.get("shas", {})
    problems: list[dict] = []

    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        m = FOLDER_RE.match(entry.name)
        if not m:
            continue

        prob_id  = int(m.group(1))
        slug     = m.group(2)
        folder   = entry.name

        # Difficulty: try both "difficulty" and "difficult" keys (LeetHub version variance)
        sha_entry  = shas.get(folder, {})
        difficulty = (
            sha_entry.get("difficulty")
            or sha_entry.get("difficult")
            or "unknown"
        ).lower()

        # Find first solution file (alphabetical; skips README.md)
        lang         = "\u2014"
        line_count   = 0
        sol_filename = None
        for f in sorted(entry.iterdir()):
            ext = f.suffix.lower()
            if ext in EXT_TO_LANG:
                lang = EXT_TO_LANG[ext]
                sol_filename = f.name
                try:
                    with open(f, encoding="utf-8", errors="replace") as fh:
                        line_count = sum(1 for _ in fh)
                except Exception:
                    line_count = 0
                break

        sol_url = (
            f"./{folder}/{sol_filename}"
            if sol_filename
            else f"./{folder}/"
        )

        problems.append({
            "id":         prob_id,
            "slug":       slug,
            "folder":     folder,
            "title":      slug_to_title(slug),
            "lc_url":     f"https://leetcode.com/problems/{slug}/",
            "sol_url":    sol_url,
            "difficulty": difficulty,
            "lang":       lang,
            "lines":      line_count,
            "date":       git_first_date(entry),
            "topics":     topics.get(folder, []),
        })

    return problems


# ── README BUILDER ────────────────────────────────────────────────────────────

def _streak_label(n: int) -> str:
    return f"{n} day{'s' if n != 1 else ''}"


def _diff_badge(label: str, count: int) -> str:
    color = DIFF_COLOR.get(label.lower(), "8b949e")
    encoded = label.replace(" ", "%20")
    return (
        f"![{label}](https://img.shields.io/badge/{encoded}-{count}-{color}"
        f"?style=flat-square&labelColor=1a1a2e)"
    )


def build_auto_block(problems: list[dict], stats: dict) -> str:
    """Assemble the full <!-- AUTO:START --> … <!-- AUTO:END --> content."""

    # ── Stats ────────────────────────────────────────────────────────────────
    easy   = stats.get("easy",   0)
    medium = stats.get("medium", 0)
    hard   = stats.get("hard",   0)
    total  = stats.get("solved", easy + medium + hard)
    if total == 0 and (easy + medium + hard) > 0:
        total = easy + medium + hard

    current_streak, longest_streak = compute_streaks(problems)

    by_id_desc   = sorted(problems, key=lambda p: p["id"], reverse=True)
    by_date_desc = sorted(
        [p for p in problems if p["date"] != "\u2014"],
        key=lambda p: p["date"],
        reverse=True,
    )
    recent = by_date_desc[:5]

    # Language badge label (all unique languages found)
    all_langs = sorted({p["lang"] for p in problems if p["lang"] != "\u2014"})
    lang_label = "%20%7C%20".join(all_langs) if all_langs else "Java"

    parts: list[str] = []

    # ── SECTION 1 : Hero ─────────────────────────────────────────────────────
    banner = (
        f"https://capsule-render.vercel.app/api"
        f"?type=waving&color={ACCENT_COLOR}&height=120&section=header"
        f"&text=LeetCode+Daily&fontSize=36&fontColor=ffffff&animation=fadeIn"
    )
    typing_svg = (
        f"https://readme-typing-svg.demolab.com"
        f"?font=Fira+Code&weight=500&size=20&pause=1000&color={ACCENT_COLOR}"
        f"&center=true&vCenter=true&repeat=true&width=500"
        f"&lines=LeetCode+%E2%80%A2+One+problem+a+day"
        f"%3BBuilding+algorithms%2C+one+commit+at+a+time"
    )

    repo_url    = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}"
    stars_b     = f"https://img.shields.io/github/stars/{GITHUB_USERNAME}/{REPO_NAME}?style=flat-square&color={ACCENT_COLOR}&labelColor=1a1a2e&label=Stars"
    commit_b    = f"https://img.shields.io/github/last-commit/{GITHUB_USERNAME}/{REPO_NAME}?style=flat-square&color={ACCENT_COLOR}&labelColor=1a1a2e&label=Last+Commit"
    lang_b      = f"https://img.shields.io/badge/Language-{lang_label}-{ACCENT_COLOR}?style=flat-square&labelColor=1a1a2e"
    license_b   = f"https://img.shields.io/github/license/{GITHUB_USERNAME}/{REPO_NAME}?style=flat-square&color={ACCENT_COLOR}&labelColor=1a1a2e"
    auto_b      = f"https://img.shields.io/badge/Auto--Updated-Daily-{ACCENT_COLOR}?style=flat-square&labelColor=1a1a2e&logo=github-actions&logoColor=white"

    parts.append(
        f'<div align="center">\n\n'
        f'<img src="{banner}" width="100%" alt="banner"/>\n\n'
        f'<img src="{typing_svg}" alt="Typing SVG"/>\n\n'
        f'<br/>\n\n'
        f'[![Stars]({stars_b})]({repo_url}/stargazers) '
        f'[![Last Commit]({commit_b})]({repo_url}/commits/main) '
        f'[![Language]({lang_b})]({repo_url}) '
        f'[![License]({license_b})](./LICENSE) '
        f'[![Auto-Updated]({auto_b})]({repo_url}/actions)\n\n'
        f'</div>\n'
    )

    # ── SECTION 2 : LeetCode Stats Card ──────────────────────────────────────
    placeholder_note = (
        "<!-- ℹ️  The card below only renders once LEETCODE_USERNAME is set "
        "in scripts/generate_readme.py -->\n"
        if LEETCODE_USERNAME == "REPLACE_ME"
        else ""
    )
    card_dark  = f"https://leetcard.jacoblin.cool/{LEETCODE_USERNAME}?theme=dark&font=Baloo%202&ext=heatmap"
    card_light = f"https://leetcard.jacoblin.cool/{LEETCODE_USERNAME}?theme=light&font=Baloo%202&ext=heatmap"

    parts.append(
        f"---\n\n"
        f"{placeholder_note}"
        f'<div align="center">\n'
        f"<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{card_dark}"/>\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{card_light}"/>\n'
        f'  <img src="{card_dark}" alt="LeetCode Stats" height="200"/>\n'
        f"</picture>\n"
        f"</div>\n"
    )

    # ── SECTION 3 : Dashboard ─────────────────────────────────────────────────
    def pct(n: int) -> str:
        return f"{n / total * 100:.0f}%" if total > 0 else "0%"

    parts.append(
        f"---\n\n"
        f"## \U0001f4ca Dashboard\n\n"
        f'<div align="center">\n\n'
        f"| Total Solved | {_diff_badge('Easy', easy)} | {_diff_badge('Medium', medium)} | {_diff_badge('Hard', hard)} |\n"
        f"|:---:|:---:|:---:|:---:|\n"
        f"| **{total}** | **{easy}** | **{medium}** | **{hard}** |\n\n"
        f"| Difficulty | Progress | Share |\n"
        f"|:---|:---|:---:|\n"
        f"| \U0001f7e2 Easy   | `{pbar(easy,   total)}` | {pct(easy)} |\n"
        f"| \U0001f7e1 Medium | `{pbar(medium, total)}` | {pct(medium)} |\n"
        f"| \U0001f534 Hard   | `{pbar(hard,   total)}` | {pct(hard)} |\n\n"
        f"| \U0001f525 Current Streak | \U0001f3c6 Longest Streak |\n"
        f"|:---:|:---:|\n"
        f"| **{_streak_label(current_streak)}** | **{_streak_label(longest_streak)}** |\n\n"
        f"</div>\n"
    )

    # ── SECTION 4 : Recently Solved ───────────────────────────────────────────
    if recent:
        rows = "\n".join(
            f"| [{p['title']}]({p['lc_url']}) "
            f"| {DIFF_EMOJI.get(p['difficulty'], chr(9898))} {p['difficulty'].capitalize()} "
            f"| {p['lang']} "
            f"| {p['date']} |"
            for p in recent
        )
        parts.append(
            f"---\n\n"
            f"## \U0001f550 Recently Solved\n\n"
            f"| Problem | Difficulty | Language | Date |\n"
            f"|:--------|:----------:|:--------:|:----:|\n"
            f"{rows}\n"
        )

    # ── SECTION 5 : All Solutions ─────────────────────────────────────────────
    def sol_row(p: dict) -> str:
        emoji   = DIFF_EMOJI.get(p["difficulty"], chr(9898))
        topics  = ", ".join(p["topics"]) if p["topics"] else "\u2014"
        return (
            f"| {p['id']:04d} "
            f"| [{p['title']}]({p['lc_url']}) "
            f"| {emoji} {p['difficulty'].capitalize()} "
            f"| {topics} "
            f"| {p['lang']} "
            f"| [\u2197]({p['sol_url']}) "
            f"| {p['lines']} "
            f"| {p['date']} |"
        )

    header  = "| # | Problem | Difficulty | Topics | Language | Solution | Lines | Date |\n"
    divider = "|:---:|:--------|:----------:|:-------|:--------:|:--------:|:-----:|:----:|\n"
    all_rows_str = "\n".join(sol_row(p) for p in by_id_desc)
    full_table = header + divider + all_rows_str

    if len(problems) > 25:
        table_block = (
            f"<details>\n"
            f"<summary><b>\U0001f4cb All Solutions ({len(problems)} problems)</b></summary>\n\n"
            f"{full_table}\n\n"
            f"</details>"
        )
    else:
        table_block = full_table

    parts.append(f"---\n\n## \U0001f4cb All Solutions\n\n{table_block}\n")

    # ── SECTION 6 : Browse by Topic ───────────────────────────────────────────
    topic_map: dict[str, list[dict]] = {}
    for p in problems:
        for t in p["topics"]:
            topic_map.setdefault(t, []).append(p)

    if topic_map:
        blocks: list[str] = []
        for topic in sorted(topic_map):
            probs = sorted(topic_map[topic], key=lambda x: x["id"])
            inner_rows = "\n".join(
                f"  | {p['id']:04d} "
                f"| [{p['title']}]({p['lc_url']}) "
                f"| {DIFF_EMOJI.get(p['difficulty'], chr(9898))} {p['difficulty'].capitalize()} "
                f"| {p['date']} |"
                for p in probs
            )
            inner_table = (
                "  | # | Problem | Difficulty | Date |\n"
                "  |:---:|:--------|:----------:|:----:|\n"
                + inner_rows
            )
            blocks.append(
                f"<details>\n"
                f"<summary><b>\U0001f3f7\ufe0f {topic} ({len(probs)})</b></summary>\n\n"
                f"{inner_table}\n\n"
                f"</details>"
            )
        parts.append(f"---\n\n## \U0001f3f7\ufe0f Browse by Topic\n\n" + "\n\n".join(blocks) + "\n")

    # ── SECTION 7 : Repo Structure ────────────────────────────────────────────
    parts.append(
        f"---\n\n"
        f"## \U0001f5c2\ufe0f Repo Structure\n\n"
        f"```\n"
        f"{REPO_NAME}/\n"
        f"\u251c\u2500\u2500 <id>-<slug>/              # One folder per problem\n"
        f"\u2502   \u251c\u2500\u2500 <id>-<slug>.java       # Solution (Java / Python / C++ / \u2026)\n"
        f"\u2502   \u2514\u2500\u2500 README.md              # Problem statement (LeetHub)\n"
        f"\u251c\u2500\u2500 scripts/\n"
        f"\u2502   \u251c\u2500\u2500 generate_readme.py     # \U0001f504 README generator (this script)\n"
        f"\u2502   \u251c\u2500\u2500 sync_topics.py         # \U0001f4d1 Topic-cache builder\n"
        f"\u2502   \u2514\u2500\u2500 README.md              # Local usage guide\n"
        f"\u251c\u2500\u2500 .github/workflows/\n"
        f"\u2502   \u2514\u2500\u2500 update-readme.yml      # \u26a1 Runs after every push\n"
        f"\u251c\u2500\u2500 topics.json                # \U0001f3f7\ufe0f  Durable topic-tag cache\n"
        f"\u251c\u2500\u2500 stats.json                 # \U0001f4ca LeetHub statistics (do not edit)\n"
        f"\u2514\u2500\u2500 README.md                  # \U0001f31f This file (auto-regenerated)\n"
        f"```\n"
    )

    # ── SECTION 8 : How This Works ────────────────────────────────────────────
    parts.append(
        f"---\n\n"
        f"## \u2699\ufe0f How This Works\n\n"
        f"1. **LeetHub v2** pushes each solution automatically after you submit on LeetCode \u2014 no copy-pasting.\n"
        f"2. A **GitHub Action** triggers on every push and runs `scripts/generate_readme.py`.\n"
        f"3. The script reads `stats.json` and `topics.json`, scans the problem folders, and regenerates this README.\n"
        f"4. **Nothing here is hand-written.** Every count, table row, and progress bar is derived from the actual files in the repo.\n"
    )

    # ── SECTION 9 : Footer ────────────────────────────────────────────────────
    footer_wave = (
        f"https://capsule-render.vercel.app/api"
        f"?type=waving&color={ACCENT_COLOR}&height=80&section=footer"
    )

    parts.append(
        f"---\n\n"
        f'<div align="center">\n\n'
        f"[![GitHub](https://img.shields.io/badge/GitHub-{GITHUB_USERNAME}-{ACCENT_COLOR}?style=flat-square&logo=github&labelColor=1a1a2e)](https://github.com/{GITHUB_USERNAME})\n"
        f"[![LeetCode](https://img.shields.io/badge/LeetCode-{LEETCODE_USERNAME}-ffc01e?style=flat-square&logo=leetcode&logoColor=fff&labelColor=1a1a2e)](https://leetcode.com/{LEETCODE_USERNAME}/)\n"
        f"[![LinkedIn](https://img.shields.io/badge/LinkedIn-{LINKEDIN_USERNAME}-0a66c2?style=flat-square&logo=linkedin&labelColor=1a1a2e)](https://linkedin.com/in/{LINKEDIN_USERNAME})\n\n"
        f'<img src="{footer_wave}" width="100%" alt="footer"/>\n\n'
        f"</div>\n"
    )

    return "\n".join(parts)


# ── README WRITER ─────────────────────────────────────────────────────────────

def update_readme(auto_content: str) -> bool:
    """
    Splice the auto block into README.md.
    Returns True if the file changed, False if already up-to-date.
    """
    existing = README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else ""

    # Locate existing AUTO markers (if any)
    auto_start_idx = existing.find(AUTO_START)

    # Locate LeetHub section (may or may not be present)
    leethub_m = LEETHUB_START_RE.search(existing)

    # Determine preamble
    if auto_start_idx != -1:
        preamble = existing[:auto_start_idx]
    elif leethub_m:
        preamble = existing[: leethub_m.start()]
    else:
        preamble = existing

    # Determine LeetHub section (preserved verbatim)
    leethub_section = existing[leethub_m.start():] if leethub_m else ""

    # Normalise preamble: strip trailing whitespace, ensure single trailing newline
    preamble = preamble.rstrip("\r\n")
    if preamble:
        preamble += "\n"

    # Assemble
    body = auto_content.rstrip("\n") + "\n"
    if leethub_section:
        leethub_section = "\n" + leethub_section.lstrip("\r\n")

    new_content = (
        preamble
        + AUTO_START + "\n"
        + body
        + AUTO_END + "\n"
        + leethub_section
    )

    # Normalise to LF
    new_content = new_content.replace("\r\n", "\n")

    if README_FILE.exists():
        old_content = README_FILE.read_bytes()
        new_bytes   = new_content.encode("utf-8")
        if old_content == new_bytes:
            return False

    README_FILE.write_text(new_content, encoding="utf-8", newline="\n")
    return True


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> None:
    stats   = load_stats()
    topics  = load_topics()
    problems = discover_problems(stats, topics)

    if not problems:
        print("WARNING: No problem folders found. README will have empty tables.")

    auto_content = build_auto_block(problems, stats)
    changed = update_readme(auto_content)

    if changed:
        print(f"README.md updated ({len(problems)} problem(s) found).")
    else:
        print("README.md is already up-to-date (no changes).")

    # ── Suggested repo settings (printed, not committed) ──────────────────────
    print()
    print("=" * 60)
    print("SUGGESTED REPO SETTINGS (paste manually into GitHub):")
    print("=" * 60)
    print()
    print("Description:")
    print(f"  Daily LeetCode grind \u2014 solutions auto-pushed by LeetHub, README auto-generated by GitHub Actions.")
    print()
    print("Topics (comma-separated for GitHub repo topics):")
    print("  leetcode, competitive-programming, java, algorithms,")
    print("  data-structures, dynamic-programming, daily-challenge,")
    print("  leetcode-solutions, problem-solving, github-profile")
    print()


if __name__ == "__main__":
    main()