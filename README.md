# ytinfo

Extract YouTube video metadata and transcript into flat JSON.

## Output

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "channel": "Channel Name",
  "title": "Video Title",
  "description": "Full video description text...",
  "transcript": "Full transcript as a single deduplicated line..."
}
```

## Requirements

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (2026+) on PATH

No pip dependencies — stdlib only.

## Install

```bash
git clone https://github.com/YOUR_USERNAME/ytinfo.git
cd ytinfo
chmod +x ytinfo.py

# Option A: symlink to a directory on your PATH
ln -s "$(pwd)/ytinfo.py" "$HOME/.local/bin/ytinfo"

# Option B: just run directly
python3 ytinfo.py <url>
```

## Usage

```bash
# Print JSON to stdout
ytinfo "https://youtube.com/watch?v=abc123"

# Save to auto-named file in cwd (YYYY-MM-DD-channel-title.json)
ytinfo "https://youtube.com/watch?v=abc123" -o

# Save to a specific file
ytinfo "https://youtube.com/watch?v=abc123" -o output.json
```

### Piping

```bash
# Extract just the transcript
ytinfo "https://youtube.com/watch?v=abc123" | jq -r '.transcript'

# Get title and channel
ytinfo "https://youtube.com/watch?v=abc123" | jq '{title, channel}'
```

### Batch

```bash
for url in "https://youtube.com/watch?v=aaa" "https://youtube.com/watch?v=bbb"; do
  ytinfo "$url" -o
done
```

## Auto-Named File Format

When using `-o` with no argument, the filename is:

```
YYYY-MM-DD-<channel-word1>-<channel-word2>-<title-word1>-<title-word2>.json
```

Example: `2026-03-04-ai-news-dario-amodei.json`

## AI Agent Skill

This repo includes a `SKILL.md` for use with AI coding assistants (Gemini, Claude Code, etc.). To register the skill:

```bash
mkdir -p "$HOME/.gemini/antigravity/skills/ytinfo"
ln -s "$(pwd)/SKILL.md" "$HOME/.gemini/antigravity/skills/ytinfo/SKILL.md"
```

See also `GEMINI.md` for Gemini-specific agent instructions.

## How It Works

1. Resolves the video ID via `yt-dlp --print "%(id)s"`
2. Downloads metadata JSON and auto-generated English subtitles (json3 format) into a temp directory
3. Deduplicates and joins subtitle segments into a single transcript string
4. Outputs flat JSON with the 5 fields above
5. Cleans up all temp files automatically

## License

MIT
