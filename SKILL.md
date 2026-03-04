---
name: ytinfo-skill
description: "Extract YouTube video metadata and transcript into flat JSON using the `ytinfo` CLI. Use this skill when users want to download video info (URL, channel, title, description, transcript) from YouTube. Triggers on mentions of \"ytinfo\", \"youtube transcript\", \"youtube metadata\", \"video info\", or any task involving extracting structured data from a YouTube video."
---

# ytinfo — YouTube Video Info Extractor

`ytinfo` extracts a YouTube video's URL, channel, title, description, and full transcript into a single flat JSON object.

## Prerequisites

- **Python 3.10+**
- **`yt-dlp`** installed and on PATH (version 2026+)
- No pip dependencies — stdlib only

## Quick Reference

```bash
ytinfo <url>                     # Print JSON to stdout
ytinfo <url> -o                  # Save to auto-named file in cwd
ytinfo <url> -o output.json     # Save to specific path
ytinfo -h                        # Show help
```

## Output Schema

Flat JSON with exactly 5 string fields:

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "channel": "Channel Name",
  "title": "Video Title",
  "description": "Full video description text...",
  "transcript": "Full transcript as a single deduplicated line..."
}
```

- `transcript` is a single string with no timestamps. Empty string `""` if no English captions exist.
- Output to stdout is valid JSON suitable for piping to `jq` or other tools.
- When using `-o`, a `Saved to <path>` message is printed to **stderr** (keeps stdout clean for piping).

## Auto-Named File Format

When using `-o` with no argument:

```
YYYY-MM-DD-<channel-word1>-<channel-word2>-<title-word1>-<title-word2>.json
```

Example: `2026-03-04-ai-news-dario-amodei.json`

## Common Patterns

### Extract and print to stdout
```bash
ytinfo "https://www.youtube.com/watch?v=abc123"
```

### Save with auto-generated filename
```bash
ytinfo "https://www.youtube.com/watch?v=abc123" -o
```

### Save to a specific file
```bash
ytinfo "https://www.youtube.com/watch?v=abc123" -o /tmp/video.json
```

### Pipe to jq for field extraction
```bash
ytinfo "https://www.youtube.com/watch?v=abc123" | jq '.transcript'
ytinfo "https://www.youtube.com/watch?v=abc123" | jq '{title, channel}'
```

### Batch multiple videos
```bash
for url in "https://youtube.com/watch?v=aaa" "https://youtube.com/watch?v=bbb"; do
  ytinfo "$url" -o
done
```

### Feed transcript into NotebookLM via nlm
```bash
ytinfo "https://youtube.com/watch?v=abc123" -o /tmp/vid.json
nlm source add <notebook-id> --text "$(jq -r '.transcript' /tmp/vid.json)" --title "$(jq -r '.title' /tmp/vid.json)"
```

## Notes

- Uses `yt-dlp` under the hood — if `yt-dlp` fails (network, invalid URL), the error propagates naturally.
- All intermediate files (subtitle downloads) use a temp directory and are cleaned up automatically.
- Transcript deduplication handles auto-generated subtitle repetition.
