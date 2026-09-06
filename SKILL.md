---
name: magazine-reading-guide
description: Download the latest The Economist, The New Yorker, or The Atlantic issue from hehonghui/awesome-english-ebooks and create a complete Chinese PDF reading guide covering every article. Use when a user asks for the latest issue, a full-issue contents guide, article difficulty, or estimated reading times for one of these magazines.
---

# Magazine Reading Guide

Create one issue folder containing the downloaded source PDF, extracted article data, and a polished Chinese reading-guide PDF.

## Publication routing

Normalize the user's publication name to one of these script values:

- `economist`: The Economist, 经济学人
- `new-yorker`: The New Yorker, 纽约客, New Yorker
- `atlantic`: The Atlantic, 大西洋月刊, Atlantic. Treat “The Atlantics” as The Atlantic when the intent is clear.

If the publication is omitted, use The Economist only when context makes that choice clear; otherwise ask one concise question. Preserve a requested issue date instead of silently substituting the latest issue.

## Workflow

1. Use the PDF skill if available, and follow its artifact-generation and render-verification requirements. Otherwise use equivalent PDF extraction, creation, and visual QA tools.
2. Create a stable issue folder such as `outputs/the-economist_YYYY-MM-DD/`. Keep the source PDF, extraction JSON, guide-data JSON, rendered cover image, and final guide in that folder. Put temporary page renders in a subfolder and remove or exclude them from delivery.
3. Run `scripts/fetch_latest_issue.py` with the normalized publication and issue folder. This uses GitHub's public contents API and downloads the repository's PDF; do not clone the entire large repository.
4. Run `scripts/extract_pdf_articles.py` on the downloaded PDF. Prefer PDF bookmarks as article boundaries. If the PDF lacks useful bookmarks, inspect its contents pages and page text, then consolidate page-level extraction into true article records.
5. Read the complete extracted issue, not just its cover or table of contents. Build a record for every editorial item represented in the issue navigation, including news roundups, leaders, letters, columns, reviews, indicator pages, cartoons, and obituaries when present. Do not count advertisements, app promotions, blank pages, or section-divider pages as articles.
6. For each article, preserve the exact English title and write a specific one- or two-sentence Chinese overview. Add an editorially judged CEFR band and an estimated reading time. Base time on extracted English word count and the user's requested speed; otherwise use 130 words per minute, round up, and use at least one minute.
7. Create `guide-data.json` using [references/guide-data-schema.md](references/guide-data-schema.md). Before rendering, verify article count against both the PDF navigation and extracted boundaries, check numbering is continuous, and investigate discrepancies.
8. Render with `scripts/render_reading_guide.py`. Include an opening orientation page with issue themes, reading routes, timing assumptions, and a difficulty legend. Keep summaries compact enough that the complete issue remains scannable.
9. Reopen the final PDF, render every page to images, and inspect for missing glyphs, clipped text, stretched cover art, overlaps, broken cards, awkward section breaks, and inconsistent page numbers. Confirm the first and last article titles and all article numbers are present in extracted final-PDF text.
10. Deliver the issue folder or a ZIP of it. State the resolved issue date, number of source pages, number of guide entries, and guide page count. Link the repository page used to determine the issue.

## Quality rules

- “Latest” means the lexically greatest valid issue date currently present in the selected repository directory, not today's date and not a guessed publication schedule.
- Summaries must describe the article's actual argument or reporting, not merely translate its title.
- Difficulty combines syntax, abstraction, assumed background knowledge, specialist vocabulary, and length. Use consistent labels within an issue, such as `入门 B1-B2`, `进阶 B2-C1`, and `高阶 C1+`.
- Treat PDF metadata and bookmarks as evidence, not infallible truth. Visually inspect contents pages when title encoding is damaged or article boundaries look implausible.
- Do not invent missing issues, titles, authors, page ranges, or article content. Report repository or extraction failures clearly and retain any successfully downloaded source.
- When the user asks only to download an issue, stop after download; do not create a guide unless requested or clearly implied.
