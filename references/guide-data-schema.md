# Guide data schema

Pass a UTF-8 JSON object to `render_reading_guide.py`:

```json
{
  "publication": "The Economist",
  "issue_date": "2026-09-05",
  "repository_url": "https://github.com/hehonghui/awesome-english-ebooks",
  "source_url": "https://raw.githubusercontent.com/.../issue.pdf",
  "source_pages": 337,
  "speed_wpm": 130,
  "editorial_overview": "用两三句话概括本期最值得注意的交叉主题。",
  "reading_routes": [
    {"name": "30 分钟速览", "items": "01 → 04 → 09 → 13"},
    {"name": "专题路线", "items": "04 → 13 → 24 → 53"}
  ],
  "articles": [
    {
      "number": 1,
      "section": "Leaders / 社论",
      "title": "Exact English title",
      "summary": "具体的中文内容概述。",
      "difficulty": "进阶 B2-C1",
      "minutes": 8,
      "word_count": 935,
      "page_start": 27,
      "page_end": 29
    }
  ]
}
```

Required top-level fields are `publication`, `issue_date`, and a non-empty `articles` array. Every article requires `number`, `section`, `title`, `summary`, `difficulty`, and `minutes`. Word count and page fields may be `null` only when the source does not expose them reliably.

Number articles continuously from 1 in publication order. Keep repeated section values on every article; the renderer groups consecutive records automatically. Use bilingual section names when a natural Chinese label is known, but never translate or rewrite the article title itself.

For magazines with essays spanning many pages, use the article's actual extracted word count rather than page count to estimate time. For cartoon or indicator entries with almost no running text, use one minute unless visual inspection reasonably requires more.
