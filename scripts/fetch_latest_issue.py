#!/usr/bin/env python3
"""Resolve and download the latest supported magazine PDF from GitHub."""

import argparse
import json
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

REPO = "hehonghui/awesome-english-ebooks"
BRANCH = "master"
PUBLICATIONS = {
    "economist": {"name": "The Economist", "directory": "01_economist"},
    "new-yorker": {"name": "The New Yorker", "directory": "02_new_yorker"},
    "atlantic": {"name": "The Atlantic", "directory": "04_atlantic"},
}
DATE_RE = re.compile(r"(?P<year>20\d{2})[._-](?P<month>\d{2})[._-](?P<day>\d{2})")


def api_json(path):
    quoted = urllib.parse.quote(path, safe="/")
    url = f"https://api.github.com/repos/{REPO}/contents/{quoted}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={"User-Agent": "magazine-reading-guide", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def issue_date(name):
    match = DATE_RE.search(name)
    if not match:
        return None
    value = "-".join(match.group(k) for k in ("year", "month", "day"))
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None
    return value


def download(url, destination):
    req = urllib.request.Request(url, headers={"User-Agent": "magazine-reading-guide"})
    tmp = destination.with_suffix(destination.suffix + ".part")
    with urllib.request.urlopen(req, timeout=90) as response, tmp.open("wb") as stream:
        shutil.copyfileobj(response, stream, length=1024 * 1024)
    tmp.replace(destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publication", required=True, choices=sorted(PUBLICATIONS))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--issue-date", help="YYYY-MM-DD; omit for latest")
    parser.add_argument("--metadata-name", default="issue-metadata.json")
    args = parser.parse_args()

    config = PUBLICATIONS[args.publication]
    dirs = [item for item in api_json(config["directory"]) if item.get("type") == "dir" and issue_date(item.get("name", ""))]
    if not dirs:
        raise SystemExit(f"No dated issue directories found in {config['directory']}")
    if args.issue_date:
        matches = [item for item in dirs if issue_date(item["name"]) == args.issue_date]
        if not matches:
            raise SystemExit(f"Issue {args.issue_date} not found for {config['name']}")
        selected = matches[-1]
    else:
        selected = max(dirs, key=lambda item: (issue_date(item["name"]), item["name"]))

    date = issue_date(selected["name"])
    files = api_json(selected["path"])
    pdfs = [item for item in files if item.get("type") == "file" and item.get("name", "").lower().endswith(".pdf")]
    if not pdfs:
        raise SystemExit(f"No PDF found in {selected['path']}")
    pdf = max(pdfs, key=lambda item: item.get("size", 0))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / pdf["name"]
    if not destination.exists() or destination.stat().st_size != pdf.get("size"):
        download(pdf["download_url"], destination)

    metadata = {
        "publication_key": args.publication,
        "publication": config["name"],
        "issue_date": date,
        "repository_url": f"https://github.com/{REPO}",
        "repository_path": selected["path"],
        "source_url": pdf["download_url"],
        "source_pdf": str(destination.resolve()),
        "source_bytes": destination.stat().st_size,
    }
    metadata_path = args.output_dir / args.metadata_name
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as exc:
        print(f"GitHub HTTP error {exc.code}: {exc.reason}", file=sys.stderr)
        raise SystemExit(2)
