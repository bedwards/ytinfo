# Gemini Agent Instructions

This project provides `ytinfo`, a CLI tool for extracting YouTube video metadata and transcripts into flat JSON.

## Project Structure

```
ytinfo.py   # Main script (also linked as `ytinfo` on PATH)
SKILL.md    # AI agent skill definition
SPEC.md     # Original build & verification spec
```

## Skill Registration

To make this skill available to Gemini/Antigravity:

```bash
mkdir -p "$HOME/.gemini/antigravity/skills/ytinfo"
ln -s "$(pwd)/SKILL.md" "$HOME/.gemini/antigravity/skills/ytinfo/SKILL.md"
```

## Key Facts

- **No pip dependencies** — uses only Python stdlib + `yt-dlp` on PATH.
- **Output is flat JSON** with 5 string fields: `url`, `channel`, `title`, `description`, `transcript`.
- **Transcript** is deduplicated auto-generated English subtitles joined into one line, no timestamps.
- **`-o` flag** saves to file (auto-named or explicit path); without it, JSON goes to stdout.
- **Temp files** are cleaned up automatically via `tempfile.TemporaryDirectory`.

## Common Agent Tasks

### Extract video info
```bash
ytinfo "https://youtube.com/watch?v=VIDEO_ID" -o /tmp/video.json
```

### Read the output
```bash
cat /tmp/video.json | jq '.title'
```

### Feed into NotebookLM
```bash
ytinfo "https://youtube.com/watch?v=VIDEO_ID" -o /tmp/vid.json
nlm source add <notebook-id> \
  --text "$(jq -r '.transcript' /tmp/vid.json)" \
  --title "$(jq -r '.title' /tmp/vid.json)"
```
