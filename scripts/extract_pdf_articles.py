#!/usr/bin/env python3
"""Extract PDF text into bookmark-bounded records, with a page fallback."""

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


def flatten_outline(reader):
    destinations = []

    def walk(items):
        for item in items:
            if isinstance(item, list):
                walk(item)
                continue
            try:
                page = reader.get_destination_page_number(item)
                title = str(getattr(item, "title", "")).strip()
            except Exception:
                continue
            if title and page >= 0:
                destinations.append((title, page))

    try:
        walk(reader.outline)
    except Exception:
        pass
    deduped = []
    for title, page in destinations:
        if not deduped or deduped[-1] != (title, page):
            deduped.append((title, page))
    return deduped


def clean(text):
    text = (text or "").replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def count_words(text):
    return len(re.findall(r"\b[A-Za-z]+(?:['’][A-Za-z]+)?\b", text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    reader = PdfReader(str(args.input))
    pages = [clean(page.extract_text() or "") for page in reader.pages]
    outline = flatten_outline(reader)
    records = []

    if len(outline) >= 3:
        for index, (title, start) in enumerate(outline, 1):
            end = outline[index][1] if index < len(outline) else len(pages)
            if end <= start:
                end = start + 1
            text = clean("\n".join(pages[start:min(end, len(pages))]))
            records.append({"index": index, "title": title, "start_page": start + 1,
                            "end_page": min(end, len(pages)), "word_count": count_words(text), "text": text})
        mode = "bookmarks"
    else:
        for index, text in enumerate(pages, 1):
            records.append({"index": index, "title": f"Page {index}", "start_page": index,
                            "end_page": index, "word_count": count_words(text), "text": text})
        mode = "pages"

    payload = {"source_pdf": str(args.input.resolve()), "page_count": len(pages),
               "extraction_mode": mode, "outline_count": len(outline), "records": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"page_count": len(pages), "mode": mode, "records": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
