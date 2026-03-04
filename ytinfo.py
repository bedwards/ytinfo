#!/usr/bin/env python3
"""Extract YouTube video metadata and transcript into flat JSON.

Usage:
    python ytinfo.py <url>                  # print JSON to stdout
    python ytinfo.py <url> -o               # save to auto-named file in cwd
    python ytinfo.py <url> -o path.json     # save to specific file

Default filename format: YYYY-MM-DD-channel-word1-word2-title-word1-word2.json
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime


def slugify(text: str, max_words: int = 2) -> str:
    """Convert text to kebab-case, limited to max_words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    words = text.split()[:max_words]
    return "-".join(w for w in words if w)


def get_video_id(url: str) -> str:
    """Extract video ID using yt-dlp."""
    result = subprocess.run(
        ["yt-dlp", "--print", "%(id)s", "--skip-download", url],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def get_metadata(url: str, sub_dir: str, video_id: str) -> dict:
    """Download metadata JSON and subtitle file."""
    out_template = os.path.join(sub_dir, f"yt-{video_id}")
    result = subprocess.run(
        [
            "yt-dlp", "--no-simulate", "--skip-download", "--dump-json",
            "--write-auto-subs", "--sub-lang", "en", "--sub-format", "json3",
            "-o", out_template, url,
        ],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def extract_transcript(sub_dir: str, video_id: str) -> str:
    """Parse json3 subtitle file into a single line of deduplicated text."""
    sub_path = os.path.join(sub_dir, f"yt-{video_id}.en.json3")
    if not os.path.exists(sub_path):
        return ""

    with open(sub_path) as f:
        data = json.load(f)

    seen = set()
    lines = []
    for event in data.get("events", []):
        segs = event.get("segs")
        if not segs:
            continue
        text = "".join(seg.get("utf8", "") for seg in segs).strip()
        if text and text not in seen:
            seen.add(text)
            lines.append(text)

    return " ".join(lines)


def default_filename(channel: str, title: str) -> str:
    """Generate default filename: YYYY-MM-DD-channel-slug-title-slug.json"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    channel_slug = slugify(channel)
    title_slug = slugify(title)
    return f"{date_str}-{channel_slug}-{title_slug}.json"


def main():
    parser = argparse.ArgumentParser(
        description="Extract YouTube video URL, channel, title, description, and transcript into flat JSON.",
        epilog="Examples:\n"
               "  python ytinfo.py https://youtube.com/watch?v=abc123\n"
               "  python ytinfo.py https://youtube.com/watch?v=abc123 -o\n"
               "  python ytinfo.py https://youtube.com/watch?v=abc123 -o output.json\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-o", "--output",
        nargs="?",
        const="AUTO",
        default=None,
        help="Save to file. No arg = auto-named file in cwd. With arg = save to that path.",
    )
    args = parser.parse_args()

    video_id = get_video_id(args.url)

    with tempfile.TemporaryDirectory() as tmp_dir:
        metadata = get_metadata(args.url, tmp_dir, video_id)
        transcript = extract_transcript(tmp_dir, video_id)

    result = {
        "url": metadata.get("webpage_url", ""),
        "channel": metadata.get("channel", ""),
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "transcript": transcript,
    }

    if args.output is None:
        # Default: print to stdout
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        output_path = (
            default_filename(result["channel"], result["title"])
            if args.output == "AUTO"
            else args.output
        )
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
