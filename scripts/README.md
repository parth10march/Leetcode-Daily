# scripts/

Helper scripts for the [Leetcode-Daily](https://github.com/parth10march/Leetcode-Daily) repo.

## Quick start

```bash
# 1. Refresh the topic cache from the current README and problem folders
python scripts/sync_topics.py

# 2. Regenerate root README.md
python scripts/generate_readme.py
```

Both scripts require **Python 3.11+** and only use the standard library — no
`pip install` needed.

## Workflow

```
LeetHub push → GitHub Action → sync_topics.py → generate_readme.py → commit
```

## Personalisation

Open `scripts/generate_readme.py` and edit the CONFIG block at the top:

| Constant | Default | What it controls |
|---|---|---|
| `GITHUB_USERNAME` | `"parth10march"` | GitHub profile links and badges |
| `LEETCODE_USERNAME` | `"REPLACE_ME"` | LeetCard stats embed |
| `LINKEDIN_USERNAME` | `"REPLACE_ME"` | Footer LinkedIn badge |
| `DISPLAY_NAME` | `"Parth"` | (reserved for future greeting) |
| `ACCENT_COLOR` | `"00b8a3"` | Hex colour used across all badges and banners |
| `REPO_NAME` | `"Leetcode-Daily"` | Repo name in links |

After editing, run the generator locally and commit:

```bash
python scripts/sync_topics.py
python scripts/generate_readme.py
git add README.md topics.json
git commit -m "chore: personalise README"
git push
```

## How `topics.json` stays accurate

`sync_topics.py` reads the `# LeetCode Topics` section that LeetHub appends to
the root README and converts it into a committed `topics.json` file.  Tags are
**only ever added, never removed** (additive merge), so previously-seen tags
survive even if LeetHub temporarily strips a section.

## Running locally without git history

If you clone without `--depth 0`, problem dates fall back to file `mtime`.
For accurate "first-solved" dates, clone with full history:

```bash
git clone --depth=0 https://github.com/parth10march/Leetcode-Daily.git
```