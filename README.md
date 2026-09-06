# Magazine Reading Guide Skill

A reusable Codex skill that downloads the latest issue of **The Economist**, **The New Yorker**, or **The Atlantic** from [`hehonghui/awesome-english-ebooks`](https://github.com/hehonghui/awesome-english-ebooks), extracts the complete PDF, and produces a polished Chinese reading-guide PDF.

The guide covers every editorial item and includes:

- Exact English article titles
- Specific Chinese summaries
- CEFR-oriented reading difficulty
- Estimated reading time
- Word counts and source page ranges when available
- Recommended quick-reading and topic routes
- Rendered PDF quality checks

## Install

Clone or download this repository into your Codex skills directory:

```text
~/.codex/skills/magazine-reading-guide/
```

The directory must contain `SKILL.md` at its root. Restart or refresh Codex if the skill is not discovered immediately.

## Use

```text
$magazine-reading-guide 下载最新一期 The Economist 并生成完整中文阅读导览
```

```text
$magazine-reading-guide 下载最新一期 New Yorker，按每分钟 110 词估算阅读时间
```

```text
$magazine-reading-guide 下载 2026-09-02 的 The Atlantic 并生成完整中文导览
```

## Supported publications

| Publication | Skill value | Repository directory |
|---|---|---|
| The Economist | `economist` | `01_economist` |
| The New Yorker | `new-yorker` | `02_new_yorker` |
| The Atlantic | `atlantic` | `04_atlantic` |

## Requirements

- Python 3.10+
- `pypdf`
- `reportlab`
- A PDF rendering tool such as Poppler for final visual verification
- Network access to GitHub and `raw.githubusercontent.com`

The downloader uses Python's standard library and GitHub's public contents API, so cloning the large source repository is unnecessary.

## Notes

This project contains workflow automation only. It does not redistribute magazine files. Downloaded issues remain subject to their respective rights holders and the source repository's terms.

## License

MIT
